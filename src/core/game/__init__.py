"""
Game Logic for TurboShells
Modular game system following Single Responsibility Principle
"""

from .entities import Turtle
from .keyboard_handler import KeyboardHandler

# Import functions from game_state
from .game_state import compute_turtle_cost, generate_random_turtle, breed_turtles

# Import functions from race_track
from .race_track import generate_track, get_terrain_at

# Import functions from simulation
from .simulation import run_race

__all__ = [
    "Turtle",
    "KeyboardHandler",
    "compute_turtle_cost",
    "generate_random_turtle",
    "breed_turtles",
    "generate_track",
    "get_terrain_at",
    "run_race",
]
