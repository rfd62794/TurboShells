"""
Game logic and systems for TurboShells.

This module contains core game mechanics, race systems, breeding systems,
and other game-specific logic.
"""

# Import game entities and systems
from .entities import Turtle
from .keyboard_handler import KeyboardHandler
from .game_state import generate_random_turtle, compute_turtle_cost, breed_turtles
from .race_track import generate_track, get_terrain_at
from .simulation import run_race

__all__ = [
    'Turtle',
    'KeyboardHandler', 
    'generate_random_turtle',
    'compute_turtle_cost',
    'breed_turtles',
    'generate_track',
    'get_terrain_at',
    'run_race'
]
