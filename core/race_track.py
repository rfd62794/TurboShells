"""
Race Track Module for TurboShells
Defines race track functionality.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import random

@dataclass
class Checkpoint:
    """Checkpoint on a race track"""
    x: float
    y: float
    radius: float
    index: int
    
    def is_reached(self, turtle_x: float, turtle_y: float) -> bool:
        """Check if turtle reached this checkpoint"""
        distance = ((turtle_x - self.x)**2 + (turtle_y - self.y)**2)**0.5
        return distance <= self.radius

@dataclass
class RaceTrack:
    """Race track with checkpoints and terrain"""
    width: int = 800
    height: int = 600
    checkpoints: List[Checkpoint] = None
    terrain_map: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.checkpoints is None:
            self.checkpoints = []
        if self.terrain_map is None:
            self.terrain_map = {}
    
    def add_checkpoint(self, x: float, y: float, radius: float = 20):
        """Add a checkpoint to the track"""
        index = len(self.checkpoints)
        checkpoint = Checkpoint(x=x, y=y, radius=radius, index=index)
        self.checkpoints.append(checkpoint)
    
    def is_checkpoint_reached(self, turtle_x: float, turtle_y: float, checkpoint_index: int) -> bool:
        """Check if turtle reached a specific checkpoint"""
        if checkpoint_index >= len(self.checkpoints):
            return False
        
        checkpoint = self.checkpoints[checkpoint_index]
        return checkpoint.is_reached(turtle_x, turtle_y)
    
    def get_terrain_at(self, x: float, y: float) -> str:
        """Get terrain type at position"""
        # Simple terrain generation
        if x < 200 or x > 600 or y < 150 or y > 450:
            return "rough"
        elif 350 <= x <= 450 and 250 <= y <= 350:
            return "finish"
        else:
            return "track"
    
    def generate_default_track(self):
        """Generate a default oval track"""
        # Clear existing checkpoints
        self.checkpoints = []
        
        # Add oval track checkpoints
        checkpoints = [
            (200, 150, 30),  # Top left
            (400, 100, 30),  # Top center
            (600, 150, 30),  # Top right
            (700, 300, 30),  # Right center
            (600, 450, 30),  # Bottom right
            (400, 500, 30),  # Bottom center
            (200, 450, 30),  # Bottom left
            (100, 300, 30),  # Left center
            (400, 300, 40),  # Center/Finish
        ]
        
        for x, y, radius in checkpoints:
            self.add_checkpoint(x, y, radius)
    
    def get_track_bounds(self) -> tuple:
        """Get track boundaries"""
        if not self.checkpoints:
            return (0, 0, self.width, self.height)
        
        x_coords = [cp.x for cp in self.checkpoints]
        y_coords = [cp.y for cp in self.checkpoints]
        
        min_x = min(x_coords) - 50
        max_x = max(x_coords) + 50
        min_y = min(y_coords) - 50
        max_y = max(y_coords) + 50
        
        return (min_x, min_y, max_x, max_y)
    
    def get_total_checkpoints(self) -> int:
        """Get total number of checkpoints"""
        return len(self.checkpoints)
    
    def get_checkpoint_position(self, index: int) -> tuple:
        """Get position of a specific checkpoint"""
        if index >= len(self.checkpoints):
            return (0, 0)
        
        cp = self.checkpoints[index]
        return (cp.x, cp.y)

# Factory function
def create_oval_track(width=800, height=600) -> RaceTrack:
    """Create an oval race track"""
    track = RaceTrack(width=width, height=height)
    track.generate_default_track()
    return track

def create_custom_track(checkpoints: List[tuple], width=800, height=600) -> RaceTrack:
    """Create a custom track with specified checkpoints"""
    track = RaceTrack(width=width, height=height)
    
    for x, y, radius in checkpoints:
        track.add_checkpoint(x, y, radius)
    
    return track
