"""
Core Entities Module for TurboShells
Defines basic game entities.
"""

from dataclasses import dataclass
from typing import Optional, List
import random

@dataclass
class TurtleEntity:
    """Basic turtle entity"""
    x: float = 0.0
    y: float = 0.0
    angle: float = 0.0
    speed: float = 1.0
    color: str = "green"
    pen_down: bool = True
    
    def move_forward(self, distance: float):
        """Move turtle forward"""
        import math
        self.x += distance * math.cos(math.radians(self.angle))
        self.y += distance * math.sin(math.radians(self.angle))
    
    def turn(self, angle: float):
        """Turn turtle"""
        self.angle += angle
        
    def __str__(self):
        return f"Turtle(x={self.x:.1f}, y={self.y:.1f}, angle={self.angle:.1f})"

# Alias for compatibility
Turtle = TurtleEntity

@dataclass
class RaceTrack:
    """Race track entity"""
    width: int = 800
    height: int = 600
    checkpoints: list = None
    
    def __post_init__(self):
        if self.checkpoints is None:
            self.checkpoints = []
    
    def add_checkpoint(self, x: float, y: float, radius: float = 20):
        """Add a checkpoint to the track"""
        self.checkpoints.append({"x": x, "y": y, "radius": radius})
    
    def is_checkpoint_reached(self, turtle: TurtleEntity, checkpoint_index: int) -> bool:
        """Check if turtle reached a checkpoint"""
        if checkpoint_index >= len(self.checkpoints):
            return False
        
        checkpoint = self.checkpoints[checkpoint_index]
        distance = ((turtle.x - checkpoint["x"])**2 + (turtle.y - checkpoint["y"])**2)**0.5
        return distance <= checkpoint["radius"]

def generate_random_turtle() -> TurtleEntity:
    """Generate a random turtle"""
    return TurtleEntity(
        x=random.uniform(100, 700),
        y=random.uniform(100, 500),
        angle=random.uniform(0, 360),
        speed=random.uniform(0.5, 2.0),
        color=random.choice(["red", "green", "blue", "yellow", "purple", "orange"])
    )
