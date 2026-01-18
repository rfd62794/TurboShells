"""Pydantic v2 models for type-safe race state serialization.

These models define the contract between the Python engine and any consumer
(PyGame adapter, FastAPI WebSocket, CLI tools). All models use Pydantic v2
for high-performance JSON serialization via model_dump_json().

ADR-002 Compliance:
    - JSON for debugging/initial migration
    - Structure supports future MessagePack pivot without logic changes
"""

from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


class TurtleState(BaseModel):
    """Serializable snapshot of a turtle's race state.
    
    This is the "View Model" sent to renderers. It contains only the data
    needed for display—no physics internals or mutable game state.
    """
    
    model_config = ConfigDict(frozen=True)
    
    id: str = Field(description="Unique turtle identifier")
    name: str = Field(description="Display name")
    x: float = Field(description="Track position (logical units)")
    y: float = Field(default=0.0, description="Lane offset for visual separation")
    angle: float = Field(default=0.0, description="Heading in degrees")
    current_energy: float = Field(ge=0, description="Current energy level")
    max_energy: float = Field(gt=0, description="Maximum energy capacity")
    is_resting: bool = Field(default=False, description="True if recovering energy")
    finished: bool = Field(default=False, description="True if crossed finish line")
    rank: int | None = Field(default=None, description="Finishing position (1-indexed)")
    genome: str = Field(description="Compact genome encoding for Paper Doll: B1-S3-P2-CFF00FF")


class TerrainSegment(BaseModel):
    """A segment of terrain on the track."""
    
    model_config = ConfigDict(frozen=True)
    
    start_distance: float = Field(ge=0, description="Start position on track")
    end_distance: float = Field(gt=0, description="End position on track")
    terrain_type: Literal["grass", "water", "rock", "sand", "mud", "boost"] = Field(
        default="grass", description="Terrain type affecting physics"
    )


class RaceSnapshot(BaseModel):
    """Complete race state at a single tick.
    
    This is the primary payload broadcast via WebSocket. Frontend clients
    use this to render the current race state and interpolate movement.
    """
    
    model_config = ConfigDict(frozen=True)
    
    tick: int = Field(ge=0, description="Current simulation tick (monotonic)")
    elapsed_ms: float = Field(ge=0, description="Total elapsed race time in milliseconds")
    course_id: str = Field(default="default", description="Identifier for the current course/track")
    track_length: float = Field(gt=0, description="Total track length (logical units)")
    turtles: list[TurtleState] = Field(description="All turtle states")
    terrain_ahead: list[TerrainSegment] = Field(
        default_factory=list, 
        description="Upcoming terrain for visual rendering"
    )
    finished: bool = Field(default=False, description="True if race is complete")
    winner_id: str | None = Field(default=None, description="ID of winning turtle")
    
    def to_broadcast_json(self) -> str:
        """Optimized JSON serialization for WebSocket broadcast."""
        return self.model_dump_json(exclude_none=True)


class RaceConfig(BaseModel):
    """Configuration for a race instance."""
    
    track_length: float = Field(default=1500.0, gt=0, description="Track length in logical units")
    tick_rate: int = Field(default=30, ge=1, le=120, description="Target ticks per second")
    max_ticks: int = Field(default=5000, gt=0, description="Maximum ticks before draw")
