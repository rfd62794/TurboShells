"""TurboShells Headless Engine Package.

Provides decoupled simulation logic for both PyGame desktop and Web UI modes.
Zero PyGame dependencies—pure Python with Pydantic serialization.

Exports:
    RaceEngine: Tick-based deterministic race simulation
    TurtleState: Pydantic model for turtle state snapshots
    RaceSnapshot: Pydantic model for full race state
    GenomeCodec: Encode/decode genetics to compact strings
"""

from src.engine.models import TurtleState, RaceSnapshot
from src.engine.race_engine import RaceEngine
from src.engine.genome_codec import GenomeCodec

__all__ = ["RaceEngine", "TurtleState", "RaceSnapshot", "GenomeCodec"]
