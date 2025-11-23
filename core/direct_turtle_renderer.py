"""
Direct Turtle Renderer for TurboShells
Draws turtles directly using PIL without SVG parsing
"""

import os
import tempfile
from typing import Optional, Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageTk


class DirectTurtleRenderer:
    """
    Direct turtle renderer that draws turtles using PIL primitives
    """
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.cache = {}
        self.max_cache_size = 100
        self.cache_hits = 0
        self.cache_misses = 0
        
        print("Direct Turtle Renderer: Using PIL drawing (no SVG parsing)")
    
    def rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex color"""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def get_darker_color(self, rgb: Tuple[int, int, int], factor: float = 0.7) -> Tuple[int, int, int]:
        """Get a darker version of a color"""
        return tuple(int(c * factor) for c in rgb)
    
    def get_lighter_color(self, rgb: Tuple[int, int, int], factor: float = 1.3) -> Tuple[int, int, int]:
        """Get a lighter version of a color"""
        return tuple(min(255, int(c * factor)) for c in rgb)
    
    def draw_realistic_turtle(self, draw: ImageDraw.Draw, genetics: Dict[str, Any], size: int):
        """
        Draw a realistic turtle using PIL drawing primitives
        """
        center_x = size // 2
        center_y = size // 2
        scale = size / 200.0
        
        # Extract colors
        shell_color = genetics.get('shell_base_color', (139, 69, 19))  # Brown
        head_color = genetics.get('head_color', (34, 139, 34))  # Green
        flipper_color = genetics.get('leg_color', (34, 139, 34))  # Green
        eye_color = genetics.get('eye_color', (0, 0, 0))  # Black
        
        # Get darker colors for outlines
        shell_outline = self.get_darker_color(shell_color)
        head_outline = self.get_darker_color(head_color)
        flipper_outline = self.get_darker_color(flipper_color)
        
        # Draw shadow first
        shadow_ellipse = [
            center_x - int(70 * scale), center_y + int(40 * scale) - int(10 * scale),
            center_x + int(70 * scale), center_y + int(40 * scale) + int(10 * scale)
        ]
        draw.ellipse(shadow_ellipse, fill=(100, 100, 100, 50))
        
        # Draw shell (carapace) - realistic turtle shell shape
        shell_points = []
        shell_width = int(80 * scale)
        shell_height = int(60 * scale)
        
        # Create realistic shell shape using polygon
        for i in range(20):
            angle = (i / 20) * 3.14159  # Half circle
            if i < 10:
                # Top curve
                x = center_x - shell_width//2 + int(shell_width * (i / 10))
                y = center_y - shell_height//2 + int(shell_height//4 * (1 - abs(i - 5) / 5))
            else:
                # Bottom curve
                x = center_x + shell_width//2 - int(shell_width * ((i - 10) / 10))
                y = center_y + shell_height//2 - int(shell_height//4 * (1 - abs(i - 15) / 5))
            shell_points.append((x, y))
        
        # Draw shell
        draw.polygon(shell_points, fill=shell_color, outline=shell_outline, width=2)
        
        # Draw shell pattern (scutes/segments)
        self.draw_shell_pattern(draw, center_x, center_y, shell_width, shell_height, shell_color, scale)
        
        # Draw head - realistic turtle head
        head_width = int(25 * scale)
        head_height = int(20 * scale)
        head_y = center_y - int(45 * scale)
        
        # Head shape (rounded rectangle with curves)
        head_points = [
            (center_x - head_width//2, head_y),
            (center_x - head_width//2 + int(5 * scale), head_y - int(5 * scale)),
            (center_x + head_width//2 - int(5 * scale), head_y - int(5 * scale)),
            (center_x + head_width//2, head_y),
            (center_x + head_width//2, head_y + head_height),
            (center_x - head_width//2, head_y + head_height)
        ]
        draw.polygon(head_points, fill=head_color, outline=head_outline, width=1)
        
        # Draw eyes
        eye_radius = int(3 * scale)
        eye_y = head_y + int(8 * scale)
        
        # Left eye
        draw.ellipse([
            center_x - int(8 * scale) - eye_radius, eye_y - eye_radius,
            center_x - int(8 * scale) + eye_radius, eye_y + eye_radius
        ], fill=eye_color)
        
        # Right eye
        draw.ellipse([
            center_x + int(8 * scale) - eye_radius, eye_y - eye_radius,
            center_x + int(8 * scale) + eye_radius, eye_y + eye_radius
        ], fill=eye_color)
        
        # Draw flippers (more realistic shape)
        flipper_length = int(25 * scale)
        flipper_width = int(12 * scale)
        
        # Front right flipper
        fr_points = [
            (center_x + int(35 * scale), center_y - int(10 * scale)),
            (center_x + int(50 * scale), center_y - int(20 * scale)),
            (center_x + int(55 * scale), center_y),
            (center_x + int(45 * scale), center_y + int(15 * scale)),
            (center_x + int(35 * scale), center_y + int(5 * scale))
        ]
        draw.polygon(fr_points, fill=flipper_color, outline=flipper_outline, width=1)
        
        # Front left flipper
        fl_points = [
            (center_x - int(35 * scale), center_y - int(10 * scale)),
            (center_x - int(50 * scale), center_y - int(20 * scale)),
            (center_x - int(55 * scale), center_y),
            (center_x - int(45 * scale), center_y + int(15 * scale)),
            (center_x - int(35 * scale), center_y + int(5 * scale))
        ]
        draw.polygon(fl_points, fill=flipper_color, outline=flipper_outline, width=1)
        
        # Back right flipper
        br_points = [
            (center_x + int(30 * scale), center_y + int(30 * scale)),
            (center_x + int(45 * scale), center_y + int(35 * scale)),
            (center_x + int(40 * scale), center_y + int(50 * scale)),
            (center_x + int(25 * scale), center_y + int(45 * scale))
        ]
        draw.polygon(br_points, fill=flipper_color, outline=flipper_outline, width=1)
        
        # Back left flipper
        bl_points = [
            (center_x - int(30 * scale), center_y + int(30 * scale)),
            (center_x - int(45 * scale), center_y + int(35 * scale)),
            (center_x - int(40 * scale), center_y + int(50 * scale)),
            (center_x - int(25 * scale), center_y + int(45 * scale))
        ]
        draw.polygon(bl_points, fill=flipper_color, outline=flipper_outline, width=1)
    
    def draw_shell_pattern(self, draw: ImageDraw.Draw, center_x: int, center_y: int, 
                          shell_width: int, shell_height: int, shell_color: Tuple[int, int, int], scale: float):
        """
        Draw shell pattern (scutes/segments) based on genetics
        """
        pattern_type = 'scutes'  # Always draw realistic scutes pattern
        
        # Get pattern color (darker version of shell)
        pattern_color = self.get_darker_color(shell_color, 0.6)
        highlight_color = self.get_lighter_color(shell_color, 1.2)
        
        if pattern_type == 'scutes':
            # Draw turtle shell scutes (segments)
            scute_size = int(8 * scale)
            
            # Central scutes
            for i in range(3):
                for j in range(2):
                    x = center_x - int(15 * scale) + j * int(30 * scale)
                    y = center_y - int(10 * scale) + i * int(20 * scale)
                    
                    # Hexagonal scute shape
                    scute_points = []
                    for k in range(6):
                        angle = k * 3.14159 / 3
                        sx = x + int(scute_size * 0.866 * (1 if k % 2 == 0 else 0.5) * (1 if k < 3 else -1))
                        sy = y + int(scute_size * 0.5 * (1 if k < 2 else -1 if k > 3 else 0))
                        scute_points.append((sx, sy))
                    
                    draw.polygon(scute_points, fill=pattern_color, outline=self.get_darker_color(pattern_color))
            
            # Side scutes
            for side in [-1, 1]:
                for i in range(4):
                    x = center_x + side * int(35 * scale)
                    y = center_y - int(20 * scale) + i * int(20 * scale)
                    
                    # Smaller side scutes
                    scute_points = [
                        (x - int(4 * scale), y - int(3 * scale)),
                        (x + int(4 * scale), y - int(3 * scale)),
                        (x + int(5 * scale), y + int(3 * scale)),
                        (x - int(5 * scale), y + int(3 * scale))
                    ]
                    draw.polygon(scute_points, fill=pattern_color, outline=self.get_darker_color(pattern_color))
    
    def render_turtle_to_photoimage(self, genetics: Dict[str, Any], size: Optional[int] = None) -> Optional[ImageTk.PhotoImage]:
        """
        Render turtle from genetics to PhotoImage
        """
        img_size = size or 200
        
        # Check cache first
        cache_key = f"turtle_{hash(str(genetics))}_{img_size}"
        if cache_key in self.cache:
            self.cache_hits += 1
            return self.cache[cache_key]
        
        self.cache_misses += 1
        
        # Create PIL image
        pil_image = Image.new('RGBA', (img_size, img_size), (240, 248, 255, 255))  # Alice blue background
        draw = ImageDraw.Draw(pil_image)
        
        # Draw realistic turtle
        self.draw_realistic_turtle(draw, genetics, img_size)
        
        # Convert to PhotoImage - handle Tkinter root window requirement
        try:
            photo_image = ImageTk.PhotoImage(pil_image)
            
            # Cache the result
            self.cache_image(cache_key, photo_image)
            return photo_image
            
        except RuntimeError as e:
            if "no default root window" in str(e):
                # Save to temp file and return path
                temp_file = os.path.join(self.temp_dir, f"turtle_{id(genetics)}.png")
                pil_image.save(temp_file)
                return temp_file  # Return file path instead
            else:
                raise e
    
    def cache_image(self, cache_key: str, photo_image: ImageTk.PhotoImage) -> None:
        """
        Cache PhotoImage with size management
        """
        if len(self.cache) >= self.max_cache_size:
            # Remove oldest entry (simple LRU)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[cache_key] = photo_image
    
    def clear_cache(self) -> None:
        """
        Clear the image cache
        """
        self.cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        """
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_cache_size,
            'hits': self.cache_hits,
            'misses': self.cache_misses,
            'hit_rate_percentage': hit_rate,
            'usage_percentage': (len(self.cache) / self.max_cache_size) * 100
        }
    
    def get_rendering_capabilities(self) -> Dict[str, Any]:
        """
        Get information about rendering capabilities
        """
        return {
            'renderer_type': 'direct_pil',
            'pil_drawing': True,
            'realistic_anatomy': True,
            'shell_patterns': True,
            'cache_enabled': True,
            'max_cache_size': self.max_cache_size,
            'can_render_turtle': True,
            'svg_required': False
        }


# Global renderer instance
_renderer_instance = None


def get_direct_renderer() -> DirectTurtleRenderer:
    """
    Get global direct turtle renderer instance
    """
    global _renderer_instance
    if _renderer_instance is None:
        _renderer_instance = DirectTurtleRenderer()
    return _renderer_instance


# Utility functions
def render_turtle_directly(genetics: Dict[str, Any], 
                          size: Optional[int] = None) -> Optional[ImageTk.PhotoImage]:
    """
    Render turtle directly from genetics using PIL
    """
    renderer = get_direct_renderer()
    return renderer.render_turtle_to_photoimage(genetics, size)


def clear_direct_cache() -> None:
    """
    Clear direct renderer cache
    """
    renderer = get_direct_renderer()
    renderer.clear_cache()


def get_direct_cache_stats() -> Dict[str, Any]:
    """
    Get direct renderer cache statistics
    """
    renderer = get_direct_renderer()
    return renderer.get_cache_stats()
