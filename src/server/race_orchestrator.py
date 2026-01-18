"""Race Orchestrator: Manages race execution and broadcasting.

The orchestrator decouples the physics tick rate from the broadcast rate:
- Physics: Runs at 60Hz for accurate simulation
- Broadcast: Sends snapshots at 30Hz to save bandwidth

This allows smooth client-side interpolation while maintaining physics accuracy.
"""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, Callable, Awaitable

from src.engine.race_engine import RaceEngine
from src.engine.models import RaceConfig, RaceSnapshot
from src.engine.logging_config import get_logger
from src.engine.persistence import save_race_result

if TYPE_CHECKING:
    from src.game.entities import Turtle
    from src.server.websocket_manager import ConnectionManager

logger = get_logger(__name__)


class RaceOrchestrator:
    """Orchestrates race execution with decoupled tick/broadcast rates.
    
    The orchestrator runs the RaceEngine at a high tick rate for physics
    accuracy, but only broadcasts snapshots at a lower rate to save bandwidth.
    
    Attributes:
        engine: The RaceEngine instance
        manager: ConnectionManager for broadcasting
        physics_hz: Physics tick rate (default: 60)
        broadcast_hz: Broadcast rate (default: 30)
    """
    
    def __init__(
        self,
        turtles: list[Turtle],
        manager: ConnectionManager,
        physics_hz: int = 60,
        broadcast_hz: int = 30,
        track_length: float = 1500.0,
    ):
        """Initialize the race orchestrator.
        
        Args:
            turtles: List of Turtle entities to race
            manager: ConnectionManager for broadcasting
            physics_hz: Physics simulation rate (default: 60Hz)
            broadcast_hz: WebSocket broadcast rate (default: 30Hz)
            track_length: Track length in logical units
        """
        self.manager = manager
        self.physics_hz = physics_hz
        self.broadcast_hz = broadcast_hz
        
        config = RaceConfig(
            track_length=track_length,
            tick_rate=physics_hz,
        )
        self.engine = RaceEngine(turtles=turtles, config=config)
        
        self._running = False
        self._task: asyncio.Task | None = None
        self._latest_snapshot: RaceSnapshot | None = None
        self._race_id: str = str(int(time.time() * 1000))  # Unique race ID
        self._speed_multiplier: int = 1  # 1x, 2x, or 4x
        
        self._broadcast_interval = 1.0 / broadcast_hz
        self._physics_interval = 1.0 / physics_hz
        
        if logger:
            logger.info(
                "RaceOrchestrator initialized",
                physics_hz=physics_hz,
                broadcast_hz=broadcast_hz,
                track_length=track_length,
            )
    
    @property
    def latest_snapshot(self) -> RaceSnapshot | None:
        """Get the most recent race snapshot for late-joining clients."""
        return self._latest_snapshot
    
    @property
    def is_running(self) -> bool:
        """Check if the race is currently running."""
        return self._running
    
    @property
    def speed_multiplier(self) -> int:
        """Get current speed multiplier (1, 2, or 4)."""
        return self._speed_multiplier
    
    def set_speed(self, multiplier: int) -> None:
        """Set the race speed multiplier.
        
        Args:
            multiplier: Speed multiplier (1, 2, or 4)
        """
        if multiplier in (1, 2, 4):
            self._speed_multiplier = multiplier
            if logger:
                logger.info("Speed changed", multiplier=multiplier)
    
    async def start(self) -> None:
        """Start the race simulation and broadcasting."""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        
        if logger:
            logger.info("Race started")
    
    async def stop(self) -> None:
        """Stop the race simulation."""
        self._running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        
        if logger:
            logger.info(
                "Race stopped",
                final_tick=self.engine.current_tick if self.engine else 0,
            )
    
    async def _run_loop(self) -> None:
        """Main simulation loop with decoupled tick/broadcast rates."""
        last_broadcast_time = 0.0
        physics_accumulator = 0.0
        last_frame_time = time.perf_counter()
        
        while self._running and not self.engine.is_finished():
            current_time = time.perf_counter()
            frame_delta = current_time - last_frame_time
            last_frame_time = current_time
            
            physics_accumulator += frame_delta
            
            # Run physics ticks (speed_multiplier affects how many ticks per accumulator drain)
            ticks_to_run = self._speed_multiplier
            while physics_accumulator >= self._physics_interval and ticks_to_run > 0:
                for _ in range(self._speed_multiplier):
                    if not self.engine.is_finished():
                        self._latest_snapshot = self.engine.tick(dt=self._physics_interval)
                physics_accumulator -= self._physics_interval
                ticks_to_run -= 1
            
            time_since_broadcast = current_time - last_broadcast_time
            if time_since_broadcast >= self._broadcast_interval:
                if self._latest_snapshot:
                    await self.manager.broadcast_snapshot(self._latest_snapshot)
                last_broadcast_time = current_time
            
            await asyncio.sleep(0.001)
        
        if self._latest_snapshot:
            await self.manager.broadcast_snapshot(self._latest_snapshot)
        
        self._running = False
        
        if logger:
            winner = self.engine.get_winner()
            logger.info(
                "Race completed",
                winner_id=winner.id if winner else None,
                winner_name=winner.name if winner else "DRAW",
                total_ticks=self.engine.current_tick,
            )
        
        # Save race results to database
        await self._save_race_results()
    
    def get_sync_data(self) -> dict:
        """Get data for syncing a late-joining client.
        
        Returns:
            Dict with current snapshot and track info for immediate sync
        """
        return {
            "type": "sync",
            "track_length": self.engine.config.track_length,
            "physics_hz": self.physics_hz,
            "broadcast_hz": self.broadcast_hz,
            "current_tick": self.engine.current_tick,
            "snapshot": self._latest_snapshot.model_dump() if self._latest_snapshot else None,
        }
    
    async def _save_race_results(self) -> None:
        """Save race results to the database.
        
        Called at the end of a race to persist all turtle results.
        """
        if not self._latest_snapshot:
            return
        
        elapsed_ms = self._latest_snapshot.elapsed_ms
        
        # Get finish order from engine
        standings = self.engine.get_standings()
        
        for rank, turtle in enumerate(standings, start=1):
            if hasattr(turtle, 'is_npc') and turtle.is_npc:
                continue
                
            try:
                save_race_result(
                    race_id=self._race_id,
                    turtle=turtle,
                    rank=rank,
                    final_distance=turtle.race_distance,
                    final_time_ms=elapsed_ms if turtle.finished else 0,
                    finished=turtle.finished,
                )
            except Exception as e:
                if logger:
                    logger.error(
                        f"Failed to save race result for {turtle.name}: {repr(e)}",
                        turtle_name=turtle.name,
                    )
