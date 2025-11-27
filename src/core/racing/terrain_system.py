"""
Terrain System for Race Tracks
Provides visual variety and strategic elements to racing
"""

import pygame
import random
from typing import List, Dict, Tuple, Optional
from enum import Enum
from settings import TRACK_LENGTH_LOGIC, TRACK_LENGTH_PIXELS

class TerrainType(Enum):
    """Different terrain types with their properties"""
    NORMAL = "normal"
    WATER = "water"          # Faster for swim stat
    SAND = "sand"            # Slower overall, affects energy
    ROCKS = "rocks"          # Slower, affects climb stat
    GRASS = "grass"          # Normal speed
    MUD = "mud"             # Much slower, high energy drain
    BOOST = "boost"         # Speed boost area

class TerrainSegment:
    """Individual terrain segment with properties"""
    
    def __init__(self, terrain_type: TerrainType, start_pos: float, end_pos: float):
        self.terrain_type = terrain_type
        self.start_pos = start_pos  # Position in logical units
        self.end_pos = end_pos
        self.color = self._get_terrain_color()
        self.speed_modifier = self._get_speed_modifier()
        self.energy_drain = self._get_energy_drain()
        
    def _get_terrain_color(self) -> Tuple[int, int, int]:
        """Get terrain color for rendering"""
        colors = {
            TerrainType.NORMAL: (100, 150, 100),    # Green
            TerrainType.WATER: (100, 150, 255),     # Blue
            TerrainType.SAND: (238, 203, 173),      # Sandy
            TerrainType.ROCKS: (139, 137, 137),     # Gray
            TerrainType.GRASS: (34, 139, 34),       # Dark green
            TerrainType.MUD: (101, 67, 33),         # Brown
            TerrainType.BOOST: (255, 215, 0)        # Gold
        }
        return colors.get(self.terrain_type, (100, 150, 100))
    
    def _get_speed_modifier(self) -> float:
        """Get speed multiplier for this terrain"""
        modifiers = {
            TerrainType.NORMAL: 1.0,
            TerrainType.WATER: 1.2,    # Faster for swimming
            TerrainType.SAND: 0.7,     # Slower
            TerrainType.ROCKS: 0.6,    # Much slower
            TerrainType.GRASS: 1.0,    # Normal
            TerrainType.MUD: 0.4,      # Very slow
            TerrainType.BOOST: 1.5     # Speed boost
        }
        return modifiers.get(self.terrain_type, 1.0)
    
    def _get_energy_drain(self) -> float:
        """Get energy drain multiplier for this terrain"""
        drain = {
            TerrainType.NORMAL: 1.0,
            TerrainType.WATER: 1.1,     # Slightly more energy
            TerrainType.SAND: 1.3,      # More energy
            TerrainType.ROCKS: 1.2,     # More energy
            TerrainType.GRASS: 0.9,     # Less energy
            TerrainType.MUD: 1.8,       # High energy drain
            TerrainType.BOOST: 0.8      # Less energy drain
        }
        return drain.get(self.terrain_type, 1.0)

class TerrainGenerator:
    """Generates terrain patterns for race tracks"""
    
    def __init__(self):
        self.min_segment_length = 50   # Minimum segment length in logical units
        self.max_segment_length = 200  # Maximum segment length
        
        # Terrain weights for random generation
        self.terrain_weights = {
            TerrainType.NORMAL: 0.3,
            TerrainType.WATER: 0.15,
            TerrainType.SAND: 0.15,
            TerrainType.ROCKS: 0.1,
            TerrainType.GRASS: 0.15,
            TerrainType.MUD: 0.1,
            TerrainType.BOOST: 0.05
        }
    
    def generate_terrain(self, track_length: float = TRACK_LENGTH_LOGIC, 
                        difficulty: str = "normal") -> List[TerrainSegment]:
        """Generate terrain segments for a track"""
        
        # Adjust weights based on difficulty
        weights = self.terrain_weights.copy()
        if difficulty == "easy":
            weights[TerrainType.BOOST] = 0.1
            weights[TerrainType.MUD] = 0.05
        elif difficulty == "hard":
            weights[TerrainType.MUD] = 0.15
            weights[TerrainType.ROCKS] = 0.15
            weights[TerrainType.BOOST] = 0.03
        
        terrain_types = list(weights.keys())
        weight_values = list(weights.values())
        
        segments = []
        current_pos = 0.0
        
        while current_pos < track_length:
            # Choose terrain type
            terrain_type = random.choices(terrain_types, weights=weight_values)[0]
            
            # Determine segment length
            segment_length = random.uniform(self.min_segment_length, self.max_segment_length)
            
            # Ensure we don't exceed track length
            if current_pos + segment_length > track_length:
                segment_length = track_length - current_pos
            
            # Create segment
            segment = TerrainSegment(terrain_type, current_pos, current_pos + segment_length)
            segments.append(segment)
            
            current_pos += segment_length
        
        print(f"[DEBUG] Generated {len(segments)} terrain segments for {difficulty} track")
        return segments
    
    def generate_pattern_terrain(self, pattern: str = "mixed") -> List[TerrainSegment]:
        """Generate terrain with specific patterns"""
        
        if pattern == "water_heavy":
            return self._generate_water_heavy()
        elif pattern == "mountain":
            return self._generate_mountain()
        elif pattern == "desert":
            return self._generate_desert()
        elif pattern == "balanced":
            return self._generate_balanced()
        else:
            return self.generate_terrain()
    
    def _generate_water_heavy(self) -> List[TerrainSegment]:
        """Generate track with lots of water segments"""
        segments = []
        current_pos = 0.0
        
        while current_pos < TRACK_LENGTH_LOGIC:
            if random.random() < 0.4:  # 40% chance for water
                terrain_type = TerrainType.WATER
                length = random.uniform(80, 150)
            elif random.random() < 0.7:  # 30% chance for grass
                terrain_type = TerrainType.GRASS
                length = random.uniform(50, 100)
            else:  # 30% chance for normal
                terrain_type = TerrainType.NORMAL
                length = random.uniform(40, 80)
            
            if current_pos + length > TRACK_LENGTH_LOGIC:
                length = TRACK_LENGTH_LOGIC - current_pos
            
            segments.append(TerrainSegment(terrain_type, current_pos, current_pos + length))
            current_pos += length
        
        return segments
    
    def _generate_mountain(self) -> List[TerrainSegment]:
        """Generate track with rocks and climbs"""
        segments = []
        current_pos = 0.0
        
        while current_pos < TRACK_LENGTH_LOGIC:
            if random.random() < 0.5:  # 50% chance for rocks
                terrain_type = TerrainType.ROCKS
                length = random.uniform(60, 120)
            elif random.random() < 0.8:  # 30% chance for grass
                terrain_type = TerrainType.GRASS
                length = random.uniform(40, 80)
            else:  # 20% chance for normal
                terrain_type = TerrainType.NORMAL
                length = random.uniform(30, 60)
            
            if current_pos + length > TRACK_LENGTH_LOGIC:
                length = TRACK_LENGTH_LOGIC - current_pos
            
            segments.append(TerrainSegment(terrain_type, current_pos, current_pos + length))
            current_pos += length
        
        return segments
    
    def _generate_desert(self) -> List[TerrainSegment]:
        """Generate track with sand and mud"""
        segments = []
        current_pos = 0.0
        
        while current_pos < TRACK_LENGTH_LOGIC:
            if random.random() < 0.6:  # 60% chance for sand
                terrain_type = TerrainType.SAND
                length = random.uniform(80, 140)
            elif random.random() < 0.85:  # 25% chance for mud
                terrain_type = TerrainType.MUD
                length = random.uniform(40, 80)
            else:  # 15% chance for normal
                terrain_type = TerrainType.NORMAL
                length = random.uniform(30, 60)
            
            if current_pos + length > TRACK_LENGTH_LOGIC:
                length = TRACK_LENGTH_LOGIC - current_pos
            
            segments.append(TerrainSegment(terrain_type, current_pos, current_pos + length))
            current_pos += length
        
        return segments
    
    def _generate_balanced(self) -> List[TerrainSegment]:
        """Generate balanced track with all terrain types"""
        segments = []
        current_pos = 0.0
        terrain_cycle = [
            TerrainType.NORMAL,
            TerrainType.GRASS,
            TerrainType.WATER,
            TerrainType.SAND,
            TerrainType.BOOST,
            TerrainType.ROCKS,
            TerrainType.MUD
        ]
        
        while current_pos < TRACK_LENGTH_LOGIC:
            terrain_type = random.choice(terrain_cycle)
            length = random.uniform(60, 100)
            
            if current_pos + length > TRACK_LENGTH_LOGIC:
                length = TRACK_LENGTH_LOGIC - current_pos
            
            segments.append(TerrainSegment(terrain_type, current_pos, current_pos + length))
            current_pos += length
        
        return segments

class TerrainRenderer:
    """Renders terrain on the race track"""
    
    def __init__(self):
        self.terrain_segments: List[TerrainSegment] = []
        self.track_height = 400  # Height of terrain display area
        self.track_y_start = 100  # Y position where terrain starts
        
    def set_terrain(self, segments: List[TerrainSegment]):
        """Set the terrain segments to render"""
        self.terrain_segments = segments
    
    def render_terrain(self, screen: pygame.Surface, track_length_pixels: int = TRACK_LENGTH_PIXELS):
        """Render terrain segments on the screen"""
        
        # Draw background track
        track_rect = pygame.Rect(40, self.track_y_start, track_length_pixels, self.track_height)
        pygame.draw.rect(screen, (50, 50, 50), track_rect)  # Dark background
        
        # Draw each terrain segment
        for segment in self.terrain_segments:
            # Convert logical positions to pixel positions
            start_x = 40 + (segment.start_pos / TRACK_LENGTH_LOGIC) * track_length_pixels
            end_x = 40 + (segment.end_pos / TRACK_LENGTH_LOGIC) * track_length_pixels
            width = end_x - start_x
            
            if width > 0:  # Only draw if segment is visible
                # Draw terrain rectangle
                terrain_rect = pygame.Rect(start_x, self.track_y_start, width, self.track_height)
                pygame.draw.rect(screen, segment.color, terrain_rect)
                
                # Add texture/pattern for different terrains
                self._add_terrain_texture(screen, terrain_rect, segment.terrain_type)
                
                # Draw border
                pygame.draw.rect(screen, (0, 0, 0), terrain_rect, 1)
        
        # Draw lane lines
        for i in range(4):  # 3 lanes = 4 lines
            lane_y = self.track_y_start + (i + 1) * 100
            pygame.draw.line(screen, (255, 255, 255), (40, lane_y), (40 + track_length_pixels, lane_y), 1)
    
    def _add_terrain_texture(self, screen: pygame.Surface, rect: pygame.Rect, terrain_type: TerrainType):
        """Add visual texture to terrain segments"""
        
        if terrain_type == TerrainType.WATER:
            # Draw wave patterns
            for y in range(rect.y, rect.y + rect.height, 20):
                for x in range(rect.x, rect.x + rect.width, 30):
                    pygame.draw.arc(screen, (150, 200, 255), 
                                   pygame.Rect(x, y, 20, 10), 0, 3.14, 2)
        
        elif terrain_type == TerrainType.SAND:
            # Draw dots for sand texture
            for y in range(rect.y + 5, rect.y + rect.height, 15):
                for x in range(rect.x + 5, rect.x + rect.width, 15):
                    pygame.draw.circle(screen, (220, 190, 160), (x, y), 2)
        
        elif terrain_type == TerrainType.ROCKS:
            # Draw rock shapes
            for y in range(rect.y + 10, rect.y + rect.height, 25):
                for x in range(rect.x + 10, rect.x + rect.width, 25):
                    pygame.draw.polygon(screen, (100, 100, 100), 
                                      [(x, y+5), (x+5, y), (x+10, y+5), (x+5, y+10)])
        
        elif terrain_type == TerrainType.MUD:
            # Draw mud splatters
            for y in range(rect.y + 10, rect.y + rect.height, 20):
                for x in range(rect.x + 10, rect.x + rect.width, 20):
                    pygame.draw.ellipse(screen, (80, 50, 20), 
                                      pygame.Rect(x-3, y-3, 6, 6))
        
        elif terrain_type == TerrainType.BOOST:
            # Draw boost arrows
            for x in range(rect.x + 10, rect.x + rect.width, 40):
                for y in range(rect.y + 20, rect.y + rect.height - 20, 60):
                    # Draw arrow pointing right
                    pygame.draw.polygon(screen, (255, 255, 100), 
                                      [(x, y), (x+15, y+5), (x, y+10)])
    
    def get_terrain_at_position(self, position: float) -> Optional[TerrainSegment]:
        """Get terrain segment at specific logical position"""
        for segment in self.terrain_segments:
            if segment.start_pos <= position < segment.end_pos:
                return segment
        return None

# Global instances for easy access
terrain_generator = TerrainGenerator()
terrain_renderer = TerrainRenderer()
