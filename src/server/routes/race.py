"""WebSocket race endpoint.

Provides the /ws/race endpoint that bridges the RaceEngine to web clients.
Handles:
    - WebSocket connection lifecycle
    - Mid-race sync for late joiners
    - Client command processing (start race, etc.)
"""

from __future__ import annotations

import json
import asyncio
from typing import TYPE_CHECKING

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from src.server.websocket_manager import ConnectionManager
from src.server.race_orchestrator import RaceOrchestrator
from src.engine.logging_config import get_logger

if TYPE_CHECKING:
    from src.game.entities import Turtle

logger = get_logger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])

manager = ConnectionManager(zombie_timeout_seconds=300.0)

_current_orchestrator: RaceOrchestrator | None = None


def get_manager() -> ConnectionManager:
    """Dependency to get the global connection manager."""
    return manager


def get_orchestrator() -> RaceOrchestrator | None:
    """Dependency to get the current race orchestrator."""
    return _current_orchestrator


async def create_demo_race() -> RaceOrchestrator:
    """Create a demo race with sample turtles.
    
    This is a temporary helper for testing. In production,
    races would be created via REST API or game state.
    """
    global _current_orchestrator
    
    try:
        from src.game.entities import Turtle
    except ImportError:
        if logger:
            logger.error("Cannot import Turtle - game entities not available")
        raise ImportError("Game entities not available")
    
    turtles = [
        Turtle("Speedster", speed=12, energy=60, recovery=2, swim=5, climb=5),
        Turtle("Tank", speed=8, energy=100, recovery=8, swim=5, climb=5),
        Turtle("Balanced", speed=10, energy=80, recovery=5, swim=5, climb=5),
    ]
    
    _current_orchestrator = RaceOrchestrator(
        turtles=turtles,
        manager=manager,
        physics_hz=60,
        broadcast_hz=30,
        track_length=1500.0,
    )
    
    return _current_orchestrator


@router.websocket("/race")
async def race_websocket(websocket: WebSocket):
    """WebSocket endpoint for race state streaming.
    
    Protocol:
        1. Client connects → Server sends sync data (if race in progress)
        2. Server broadcasts RaceSnapshot at 30Hz
        3. Client can send commands: {"action": "start"}, {"action": "stop"}
        4. Connection closes when race ends or client disconnects
    """
    client = await manager.connect(websocket)
    
    try:
        if _current_orchestrator and _current_orchestrator.is_running:
            sync_data = _current_orchestrator.get_sync_data()
            await manager.send_to_client(client, json.dumps(sync_data))
            if logger:
                logger.info(
                    "Sent sync data to late joiner",
                    client_id=client.client_id,
                    current_tick=sync_data.get("current_tick"),
                )
        
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=1.0,
                )
                
                try:
                    message = json.loads(data)
                    await handle_client_command(client, message)
                except json.JSONDecodeError:
                    if logger:
                        logger.warning(
                            "Invalid JSON from client",
                            client_id=client.client_id,
                            data=data[:100],
                        )
            
            except asyncio.TimeoutError:
                pass
    
    except WebSocketDisconnect:
        if logger:
            logger.info("WebSocket disconnected", client_id=client.client_id)
    
    except Exception as e:
        if logger:
            logger.error(
                "WebSocket error",
                client_id=client.client_id,
                error=str(e),
            )
    
    finally:
        await manager.disconnect(client)


async def handle_client_command(client, message: dict) -> None:
    """Process commands from connected clients.
    
    Commands:
        {"action": "start"} - Start a new demo race
        {"action": "stop"} - Stop the current race
        {"action": "ping"} - Keep-alive ping
    """
    global _current_orchestrator
    
    action = message.get("action")
    
    if action == "start":
        if _current_orchestrator and _current_orchestrator.is_running:
            await manager.send_to_client(
                client,
                json.dumps({"type": "error", "message": "Race already in progress"}),
            )
            return
        
        orchestrator = await create_demo_race()
        await orchestrator.start()
        
        if logger:
            logger.info(
                "Race started by client",
                client_id=client.client_id,
            )
    
    elif action == "stop":
        if _current_orchestrator:
            await _current_orchestrator.stop()
            _current_orchestrator = None
    
    elif action == "ping":
        await manager.send_to_client(
            client,
            json.dumps({"type": "pong", "timestamp": asyncio.get_event_loop().time()}),
        )
    
    else:
        if logger:
            logger.warning(
                "Unknown action from client",
                client_id=client.client_id,
                action=action,
            )
