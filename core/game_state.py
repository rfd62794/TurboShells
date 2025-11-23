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
            "difficulty": self.difficulty
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
        color=random.choice(["red", "green", "blue", "yellow", "purple", "orange"])
    )
