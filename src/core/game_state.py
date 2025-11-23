"""
Game State Module for TurboShells
Manages game state and configuration.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum
import random


class GameState(Enum):
    """Game states"""

    MENU = "menu"
    RACING = "racing"
    PAUSED = "paused"
    FINISHED = "finished"
    SETTINGS = "settings"


@dataclass
class GameConfig:
    """Game configuration"""

    track_width: int = 800
    track_height: int = 600
    max_turtles: int = 8
    race_laps: int = 3
    difficulty: str = "normal"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "track_width": self.track_width,
            "track_height": self.track_height,
            "max_turtles": self.max_turtles,
            "race_laps": self.race_laps,
            "difficulty": self.difficulty,
        }


@dataclass
class RaceState:
    """Race state information"""

    current_lap: int = 1
    total_laps: int = 3
    race_time: float = 0.0
    best_lap_time: Optional[float] = None
    checkpoints_passed: int = 0
    total_checkpoints: int = 0

    def next_checkpoint(self):
        """Move to next checkpoint"""
        self.checkpoints_passed += 1

    def next_lap(self):
        """Move to next lap"""
        self.current_lap += 1
        self.checkpoints_passed = 0

    def is_finished(self) -> bool:
        """Check if race is finished"""
        return self.current_lap > self.total_laps


class StateManager:
    """Manages game state transitions"""

    def __init__(self):
        self.current_state = GameState.MENU
        self.config = GameConfig()
        self.race_state = RaceState()
        self.previous_states = []

    def change_state(self, new_state: GameState):
        """Change game state"""
        self.previous_states.append(self.current_state)
        self.current_state = new_state

    def get_state(self) -> GameState:
        """Get current state"""
        return self.current_state

    def reset_race(self):
        """Reset race state"""
        self.race_state = RaceState()
        self.current_state = GameState.RACING

    def get_config(self) -> GameConfig:
        """Get game configuration"""
        return self.config

    def update_config(self, **kwargs):
        """Update game configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)


def generate_random_turtle():
    """Generate a random turtle for compatibility"""
    from .entities import TurtleEntity

    return TurtleEntity(
        x=random.uniform(100, 700),
        y=random.uniform(100, 500),
        angle=random.uniform(0, 360),
        speed=random.uniform(0.5, 2.0),
        color=random.choice(["red", "green", "blue", "yellow", "purple", "orange"]),
    )


def breed_turtles(parent1, parent2):
    """Breed two turtles to create offspring"""
    from .entities import TurtleEntity

    return TurtleEntity(
        x=(parent1.x + parent2.x) / 2,
        y=(parent1.y + parent2.y) / 2,
        angle=random.uniform(parent1.angle, parent2.angle),
        speed=random.uniform(
            min(parent1.speed, parent2.speed), max(parent1.speed, parent2.speed)
        ),
        color=parent1.color if random.random() > 0.5 else parent2.color,
    )


def compute_turtle_cost(turtle):
    """Compute cost/fitness of a turtle"""
    # Simple cost calculation based on speed and position
    base_cost = 100
    speed_cost = turtle.speed * 20
    position_cost = (abs(turtle.x - 400) + abs(turtle.y - 300)) * 0.1
    return base_cost + speed_cost + position_cost


def generate_track(width=800, height=600):
    """Generate a race track"""
    from .entities import RaceTrack

    track = RaceTrack(width=width, height=height)

    # Add some checkpoints
    checkpoints = [
        (200, 150, 30),
        (600, 150, 30),
        (600, 450, 30),
        (200, 450, 30),
        (400, 300, 40),  # Finish line
    ]

    for x, y, radius in checkpoints:
        track.add_checkpoint(x, y, radius)

    return track


def get_terrain_at(x, y):
    """Get terrain type at position"""
    # Simple terrain generation
    if x < 200 or x > 600 or y < 150 or y > 450:
        return "rough"
    elif 350 <= x <= 450 and 250 <= y <= 350:
        return "finish"
    else:
        return "track"


def run_race(turtles, track, max_steps=1000):
    """Run a race simulation"""
    results = []

    for turtle in turtles:
        steps = 0
        checkpoints_passed = 0

        while steps < max_steps and checkpoints_passed < len(track.checkpoints):
            # Simple movement simulation
            turtle.move_forward(turtle.speed)
            turtle.turn(random.uniform(-10, 10))

            # Check checkpoints
            if track.is_checkpoint_reached(turtle, checkpoints_passed):
                checkpoints_passed += 1

            steps += 1

        results.append(
            {
                "turtle": turtle,
                "steps": steps,
                "checkpoints": checkpoints_passed,
                "finished": checkpoints_passed >= len(track.checkpoints),
            }
        )

    # Sort by checkpoints passed, then by steps
    results.sort(key=lambda x: (-x["checkpoints"], x["steps"]))

    return results
