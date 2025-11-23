"""
Core Module for TurboShells
Modular architecture following Single Responsibility Principle
"""

# Import genetics from root level
import genetics

# Import all sub-modules
from . import rendering
from . import voting
from . import game
from . import systems
from . import race_track

# Import new entities
from .entities import TurtleEntity, RaceTrack
from .game_state import GameState, GameConfig, RaceState, StateManager

# Convenience imports for backward compatibility
from genetics import VisualGenetics
from .rendering import DirectTurtleRenderer, get_direct_renderer
from .voting import VotingSystem, DesignPackage
from .game import (
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
TurtleEntity = Turtle

__all__ = [
    # Sub-modules
    "rendering",
    "voting",
    "game",
    "systems",
    "race_track",
    # Main classes
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
    # New entities and state
    "RaceTrack",
    "GameState",
    "GameConfig",
    "RaceState",
    "StateManager",
    # Convenience functions
    "get_direct_renderer",
]
