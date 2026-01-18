"""Tick-based deterministic Race Engine.

The RaceEngine is the "Source of Truth" for race simulation. It is completely
headless—no PyGame, no UI, no rendering. It takes a list of Turtles and a
track, then produces RaceSnapshot models on each tick.

Design Principles:
    - Deterministic: Same inputs → same outputs (for replays/testing)
    - Tick-based: Fixed time-step simulation, not frame-bound
    - Serializable: All state can be exported via Pydantic models
    - Single Responsibility: Only simulation logic, no rendering

Usage:
    engine = RaceEngine(turtles=[t1, t2], track_length=1500)
    while not engine.is_finished():
        snapshot = engine.tick(dt=1/30)  # 30 TPS
        broadcast(snapshot.to_broadcast_json())
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from src.engine.models import TurtleState, RaceSnapshot, TerrainSegment, RaceConfig
from src.engine.genome_codec import GenomeCodec
from src.engine.logging_config import get_logger

if TYPE_CHECKING:
    from src.game.entities import Turtle

logger = get_logger(__name__)


class RaceEngine:
    """Deterministic tick-based race simulation engine.
    
    This is the "Brain" that calculates positions and determines winners.
    Renderers (PyGame, PixiJS) are "Eyes" that only display the state.
    
    Attributes:
        turtles: List of Turtle entities participating in the race
        config: Race configuration (track length, tick rate, etc.)
        current_tick: Current simulation tick (monotonic counter)
        start_time: Timestamp when race started
    """
    
    def __init__(
        self,
        turtles: list[Turtle],
        config: RaceConfig | None = None,
        track: list[str] | None = None,
        course_id: str = "default",
    ):
        """Initialize the race engine.
        
        Args:
            turtles: List of Turtle entities to race
            config: Optional race configuration
            track: Optional pre-generated track (list of terrain types)
            course_id: Unique identifier for the track/course
        """
        self.turtles = turtles
        self.config = config or RaceConfig()
        self.course_id = course_id
        self.current_tick = 0
        self.start_time: float | None = None
        self._finished = False
        self._winner: Turtle | None = None
        self._finish_order: list[Turtle] = []
        
        self._track = track or self._generate_default_track()
        
        self._reset_turtles()
        
        if logger:
            logger.info(
                "RaceEngine initialized",
                turtle_count=len(turtles),
                track_length=self.config.track_length,
            )
    
    def _generate_default_track(self) -> list[str]:
        """Generate default terrain track using game logic."""
        try:
            from src.game.race_track import generate_track
            return generate_track(int(self.config.track_length))
        except ImportError:
            segment_count = int(self.config.track_length / 10) + 100
            return ["grass"] * segment_count
    
    def _reset_turtles(self) -> None:
        """Reset all turtles for a fresh race."""
        for turtle in self.turtles:
            turtle.reset_for_race()
    
    def _get_terrain_at(self, distance: float) -> dict[str, any]:
        """Get terrain dict at a given distance."""
        try:
            from src.game.race_track import get_terrain_at
            terrain_type = get_terrain_at(self._track, distance)
        except ImportError:
            idx = int(distance / 10)
            idx = max(0, min(idx, len(self._track) - 1))
            terrain_type = self._track[idx] if self._track else "grass"
        
        return {"type": terrain_type, "speed_modifier": 1.0, "energy_drain": 1.0}
    
    def tick(self, dt: float = None) -> RaceSnapshot:
        """Advance simulation by one tick and return state snapshot.
        
        Args:
            dt: Delta time in seconds. If None, calculated from tick rate.
            
        Returns:
            RaceSnapshot containing complete race state at this tick.
        """
        if dt is None:
            dt = 1.0 / self.config.tick_rate
        
        if self.start_time is None:
            self.start_time = time.perf_counter()
        
        self.current_tick += 1
        
        if not self._finished:
            self._update_turtles(dt)
            self._check_finish_conditions()
        
        return self._create_snapshot()
    
    def _update_turtles(self, dt: float) -> None:
        """Update all turtle positions based on physics."""
        for turtle in self.turtles:
            if turtle.finished:
                continue
            
            terrain = self._get_terrain_at(turtle.race_distance)
            distance_moved = turtle.update_physics(terrain)
            turtle.race_distance += distance_moved * dt * self.config.tick_rate
            
            if turtle.race_distance >= self.config.track_length:
                turtle.race_distance = self.config.track_length
                turtle.finished = True
                self._finish_order.append(turtle)
                turtle.rank = len(self._finish_order)
                
                if logger:
                    logger.info(
                        "Turtle finished",
                        turtle_id=turtle.id,
                        turtle_name=turtle.name,
                        rank=turtle.rank,
                        tick=self.current_tick,
                    )
    
    def _check_finish_conditions(self) -> None:
        """Check if race should end."""
        all_finished = all(t.finished for t in self.turtles)
        max_ticks_reached = self.current_tick >= self.config.max_ticks
        
        if all_finished or max_ticks_reached:
            self._finished = True
            if self._finish_order:
                self._winner = self._finish_order[0]
            
            if logger:
                logger.info(
                    "Race finished",
                    winner_id=self._winner.id if self._winner else None,
                    winner_name=self._winner.name if self._winner else "DRAW",
                    total_ticks=self.current_tick,
                )
    
    def _create_snapshot(self) -> RaceSnapshot:
        """Create a serializable snapshot of current race state."""
        elapsed_ms = 0.0
        if self.start_time is not None:
            elapsed_ms = (time.perf_counter() - self.start_time) * 1000
        
        turtle_states = []
        for i, turtle in enumerate(self.turtles):
            lane_offset = i * 40
            
            genome = GenomeCodec.encode(turtle.visual_genetics)
            
            state = TurtleState(
                id=turtle.id,
                name=turtle.name,
                x=turtle.race_distance,
                y=float(lane_offset),
                angle=0.0,
                current_energy=turtle.current_energy,
                max_energy=turtle.stats["max_energy"],
                is_resting=turtle.is_resting,
                finished=turtle.finished,
                rank=turtle.rank,
                genome=genome,
            )
            turtle_states.append(state)
        
        terrain_ahead = self._get_terrain_segments()
        
        return RaceSnapshot(
            tick=self.current_tick,
            elapsed_ms=elapsed_ms,
            course_id=self.course_id,
            track_length=self.config.track_length,
            turtles=turtle_states,
            terrain_ahead=terrain_ahead,
            finished=self._finished,
            winner_id=self._winner.id if self._winner else None,
        )
    
    def _get_terrain_segments(self, lookahead: int = 5) -> list[TerrainSegment]:
        """Get upcoming terrain segments for visual rendering."""
        segments = []
        if not self.turtles:
            return segments
        
        # Handle case where all turtles finished (no unfinished turtles to track)
        unfinished = [t for t in self.turtles if not t.finished]
        if not unfinished:
            return segments  # Race complete, no terrain needed
        
        min_distance = min(t.race_distance for t in unfinished)
        segment_length = 100.0
        
        for i in range(lookahead):
            start = min_distance + (i * segment_length)
            end = start + segment_length
            
            if start >= self.config.track_length:
                break
            
            terrain = self._get_terrain_at(start)
            segments.append(TerrainSegment(
                start_distance=start,
                end_distance=min(end, self.config.track_length),
                terrain_type=terrain.get("type", "grass"),
            ))
        
        return segments
    
    def is_finished(self) -> bool:
        """Check if race is complete."""
        return self._finished
    
    def get_winner(self) -> Turtle | None:
        """Get winning turtle, or None if race not finished or draw."""
        return self._winner
    
    def get_standings(self) -> list[Turtle]:
        """Get turtles ordered by current position/rank."""
        return sorted(
            self.turtles,
            key=lambda t: (-t.race_distance, t.rank or float("inf")),
            reverse=False,
        )


if __name__ == "__main__":
    from src.engine.logging_config import configure_logging
    configure_logging(level="DEBUG")
    
    try:
        from src.game.entities import Turtle
    except ImportError:
        print("ERROR: Cannot import Turtle. Run from project root.")
        raise SystemExit(1)
    
    t1 = Turtle("Speedster", speed=12, energy=60, recovery=2, swim=5, climb=5)
    t2 = Turtle("Tank", speed=8, energy=100, recovery=8, swim=5, climb=5)
    
    engine = RaceEngine(turtles=[t1, t2])
    
    print("Running headless race simulation...")
    print("=" * 60)
    
    while not engine.is_finished():
        snapshot = engine.tick()
        
        if snapshot.tick % 100 == 0 or snapshot.finished:
            print(f"Tick {snapshot.tick:4d} | ", end="")
            for ts in snapshot.turtles:
                status = "🏁" if ts.finished else ("💤" if ts.is_resting else "🏃")
                print(f"{ts.name}: {ts.x:.0f}m {status} | ", end="")
            print()
    
    print("=" * 60)
    print(f"Winner: {engine.get_winner().name if engine.get_winner() else 'DRAW'}")
    print(f"Final JSON snapshot:")
    print(snapshot.to_broadcast_json())
