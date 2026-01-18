"""Async WebSocket Connection Manager.

Handles connection lifecycle, broadcasting, and zombie connection cleanup.
Designed for long-running "slow grind" sessions where clients may stay
connected for hours.

Key Features:
    - Async broadcast pattern for high concurrency
    - Automatic zombie detection and cleanup
    - Client ID telemetry via Loguru
    - Mid-race sync for late joiners
"""

from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Awaitable

from fastapi import WebSocket, WebSocketDisconnect

from src.engine.logging_config import get_logger

if TYPE_CHECKING:
    from src.engine.models import RaceSnapshot

logger = get_logger(__name__)


@dataclass
class ClientConnection:
    """Represents a connected WebSocket client.
    
    Tracks connection metadata for telemetry and zombie detection.
    """
    websocket: WebSocket
    client_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    connected_at: float = field(default_factory=time.time)
    last_ping: float = field(default_factory=time.time)
    messages_sent: int = 0
    
    def age_seconds(self) -> float:
        """Get connection age in seconds."""
        return time.time() - self.connected_at
    
    def seconds_since_ping(self) -> float:
        """Get seconds since last ping/activity."""
        return time.time() - self.last_ping


class ConnectionManager:
    """Manages WebSocket connections with async broadcast and zombie cleanup.
    
    Single Responsibility: Connection lifecycle and message distribution.
    
    Attributes:
        connections: Active client connections keyed by client_id
        zombie_timeout_seconds: Seconds of inactivity before zombie cleanup
    """
    
    def __init__(self, zombie_timeout_seconds: float = 300.0):
        """Initialize the connection manager.
        
        Args:
            zombie_timeout_seconds: Inactivity timeout for zombie detection (default: 5 minutes)
        """
        self._connections: dict[str, ClientConnection] = {}
        self.zombie_timeout_seconds = zombie_timeout_seconds
        self._broadcast_lock = asyncio.Lock()
        self._cleanup_task: asyncio.Task | None = None
    
    @property
    def connection_count(self) -> int:
        """Get current number of active connections."""
        return len(self._connections)
    
    async def connect(self, websocket: WebSocket) -> ClientConnection:
        """Accept a new WebSocket connection.
        
        Args:
            websocket: FastAPI WebSocket instance
            
        Returns:
            ClientConnection with assigned client_id
        """
        await websocket.accept()
        
        client = ClientConnection(websocket=websocket)
        self._connections[client.client_id] = client
        
        if logger:
            logger.info(
                "Client connected",
                client_id=client.client_id,
                total_connections=self.connection_count,
            )
        
        return client
    
    async def disconnect(self, client: ClientConnection) -> None:
        """Remove a client connection.
        
        Args:
            client: ClientConnection to remove
        """
        if client.client_id in self._connections:
            del self._connections[client.client_id]
        
        if logger:
            logger.info(
                "Client disconnected",
                client_id=client.client_id,
                session_duration_seconds=client.age_seconds(),
                messages_sent=client.messages_sent,
                total_connections=self.connection_count,
            )
    
    async def send_to_client(self, client: ClientConnection, message: str) -> bool:
        """Send a message to a specific client.
        
        Args:
            client: Target client connection
            message: JSON string to send
            
        Returns:
            True if sent successfully, False if client disconnected
        """
        try:
            await client.websocket.send_text(message)
            client.messages_sent += 1
            client.last_ping = time.time()
            return True
        except Exception as e:
            if logger:
                logger.warning(
                    "Failed to send to client",
                    client_id=client.client_id,
                    error=str(e),
                )
            return False
    
    async def broadcast(self, message: str) -> int:
        """Broadcast a message to all connected clients.
        
        Uses async gather for concurrent sends. Disconnects failed clients.
        
        Args:
            message: JSON string to broadcast
            
        Returns:
            Number of clients successfully sent to
        """
        if not self._connections:
            return 0
        
        async with self._broadcast_lock:
            failed_clients: list[ClientConnection] = []
            
            async def send_with_tracking(client: ClientConnection) -> bool:
                success = await self.send_to_client(client, message)
                if not success:
                    failed_clients.append(client)
                return success
            
            results = await asyncio.gather(
                *[send_with_tracking(c) for c in self._connections.values()],
                return_exceptions=True,
            )
            
            for client in failed_clients:
                await self.disconnect(client)
            
            successful = sum(1 for r in results if r is True)
            return successful
    
    async def broadcast_snapshot(self, snapshot: RaceSnapshot) -> int:
        """Broadcast a RaceSnapshot to all clients.
        
        Convenience method that serializes the snapshot.
        
        Args:
            snapshot: RaceSnapshot to broadcast
            
        Returns:
            Number of clients successfully sent to
        """
        return await self.broadcast(snapshot.to_broadcast_json())
    
    async def broadcast_json(self, data: dict) -> int:
        """Broadcast a JSON-serializable dict to all clients.
        
        Args:
            data: Dictionary to serialize and broadcast
            
        Returns:
            Number of clients successfully sent to
        """
        import json
        return await self.broadcast(json.dumps(data))
    
    async def cleanup_zombies(self) -> int:
        """Remove zombie connections that have been inactive.
        
        Returns:
            Number of zombies removed
        """
        now = time.time()
        zombies: list[ClientConnection] = []
        
        for client in self._connections.values():
            if client.seconds_since_ping() > self.zombie_timeout_seconds:
                zombies.append(client)
        
        for zombie in zombies:
            if logger:
                logger.warning(
                    "Removing zombie connection",
                    client_id=zombie.client_id,
                    inactive_seconds=zombie.seconds_since_ping(),
                )
            try:
                await zombie.websocket.close()
            except Exception:
                pass
            await self.disconnect(zombie)
        
        return len(zombies)
    
    async def start_zombie_cleanup_loop(self, interval_seconds: float = 60.0) -> None:
        """Start background task for periodic zombie cleanup.
        
        Args:
            interval_seconds: Seconds between cleanup checks
        """
        async def cleanup_loop():
            while True:
                await asyncio.sleep(interval_seconds)
                removed = await self.cleanup_zombies()
                if removed > 0 and logger:
                    logger.info(
                        "Zombie cleanup completed",
                        removed_count=removed,
                        remaining_connections=self.connection_count,
                    )
        
        self._cleanup_task = asyncio.create_task(cleanup_loop())
    
    async def stop_zombie_cleanup_loop(self) -> None:
        """Stop the background zombie cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
    
    async def close_all(self) -> None:
        """Close all connections gracefully."""
        for client in list(self._connections.values()):
            try:
                await client.websocket.close()
            except Exception:
                pass
            await self.disconnect(client)
