"""
Core Module for TurboShells
Modular architecture following Single Responsibility Principle
"""

# Import genetics from the correct location
try:
    from genetics import VisualGenetics
except ImportError:
    try:
        from src.genetics import VisualGenetics
    except ImportError:
        VisualGenetics = None

# Import all sub-modules
from . import rendering
from . import voting
from . import systems
from . import race_track

# Import new entities
from .entities import TurtleEntity, RaceTrack
from .game_state import GameState, GameConfig, RaceState, StateManager

# Convenience imports for backward compatibility
if VisualGenetics:
    from .rendering import DirectTurtleRenderer, get_direct_renderer
    from .voting import VotingSystem, DesignPackage
    from game import (
        Turtle,
        KeyboardHandler,
        compute_turtle_cost,
        generate_random_turtle,
        breed_turtles,
        generate_track,
        get_terrain_at,
        run_race,
    )
    from .systems import StateHandler, GeneticPoolManager, PatternGenerators

# Alias for compatibility
if VisualGenetics:
    TurtleEntity = Turtle

__all__ = [
    # Sub-modules
    "rendering",
    "voting",
    "game",
    "systems",
    "race_track",
    # New entities and state
    "RaceTrack",
    "GameState",
    "GameConfig",
    "RaceState",
    "StateManager",
]

# Add genetics-related items only if available
if VisualGenetics:
    __all__.extend([
        "VisualGenetics",
        "DirectTurtleRenderer",
        "VotingSystem",
        "DesignPackage",
        "Turtle",
        "TurtleEntity",
        "KeyboardHandler",
        "compute_turtle_cost",
        "generate_random_turtle",
        "breed_turtles",
        "generate_track",
        "get_terrain_at",
        "run_race",
        "StateHandler",
        "GeneticPoolManager",
        "PatternGenerators",
        "get_direct_renderer",
    ])
