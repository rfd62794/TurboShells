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
        Draw a highly realistic turtle using PIL drawing primitives
        """
        center_x = size // 2
        center_y = size // 2
        scale = size / 200.0
        
        # Extract colors
        shell_color = genetics.get('shell_base_color', (34, 139, 34))  # Sea turtle green
        head_color = genetics.get('head_color', (46, 125, 50))  # Darker green
        flipper_color = genetics.get('leg_color', (46, 125, 50))  # Darker green
        eye_color = genetics.get('eye_color', (0, 0, 0))  # Black
        
        # Get color variations
        shell_outline = self.get_darker_color(shell_color, 0.6)
        shell_highlight = self.get_lighter_color(shell_color, 1.2)
        head_outline = self.get_darker_color(head_color, 0.7)
        flipper_outline = self.get_darker_color(flipper_color, 0.7)
        
        # Draw shadow first (more realistic)
        shadow_ellipse = [
            center_x - int(75 * scale), center_y + int(45 * scale) - int(12 * scale),
            center_x + int(75 * scale), center_y + int(45 * scale) + int(12 * scale)
        ]
        draw.ellipse(shadow_ellipse, fill=(80, 80, 80, 60))
        
        # Draw shell (carapace) - more realistic sea turtle shell
        shell_width = int(85 * scale)
        shell_height = int(65 * scale)
        
        # Create more realistic shell shape using bezier-like curves
        shell_points = []
        
        # Top curve of shell (more pronounced)
        for i in range(21):
            t = i / 20
            if i <= 10:
                # Top curve - more rounded
                x = center_x - shell_width//2 + int(shell_width * t)
                # Use a parabolic curve for the top
                curve_height = int(15 * scale * (1 - 4 * (t - 0.5) ** 2))
                y = center_y - shell_height//2 + curve_height
            else:
                # Bottom curve - flatter
                x = center_x + shell_width//2 - int(shell_width * (t - 0.5) * 2)
                curve_height = int(8 * scale * (1 - 4 * ((t - 0.5) - 0.5) ** 2))
                y = center_y + shell_height//2 - curve_height
            shell_points.append((x, y))
        
        # Draw main shell
        draw.polygon(shell_points, fill=shell_color, outline=shell_outline, width=3)
        
        # Draw detailed shell pattern (more realistic scutes)
        self.draw_detailed_shell_pattern(draw, center_x, center_y, shell_width, shell_height, 
                                        shell_color, shell_outline, shell_highlight, scale)
        
        # Draw head - more realistic sea turtle head
        head_width = int(28 * scale)
        head_height = int(22 * scale)
        head_y = center_y - int(48 * scale)
        
        # Create more realistic head shape
        head_points = []
        
        # Head outline (more rounded)
        for i in range(16):
            angle = (i / 16) * 2 * 3.14159
            if i < 8:
                # Top half of head
                x = center_x + int(head_width * 0.5 * (1 - i/8) * (-1 if i < 4 else 1))
                y = head_y + int(head_height * 0.3 * (1 - i/8))
            else:
                # Bottom half of head (more rounded)
                x = center_x + int(head_width * 0.5 * (1 - (i-8)/8) * (-1 if i < 12 else 1))
                y = head_y + int(head_height * 0.7 * ((i-8)/8))
            head_points.append((x, y))
        
        draw.polygon(head_points, fill=head_color, outline=head_outline, width=2)
        
        # Draw eyes with more detail
        eye_radius = int(4 * scale)
        pupil_radius = int(2 * scale)
        eye_y = head_y + int(8 * scale)
        
        # Left eye with white sclera
        draw.ellipse([
            center_x - int(10 * scale) - eye_radius, eye_y - eye_radius,
            center_x - int(10 * scale) + eye_radius, eye_y + eye_radius
        ], fill=(255, 255, 255), outline=head_outline, width=1)
        
        # Left pupil
        draw.ellipse([
            center_x - int(10 * scale) - pupil_radius, eye_y - pupil_radius,
            center_x - int(10 * scale) + pupil_radius, eye_y + pupil_radius
        ], fill=eye_color)
        
        # Right eye with white sclera
        draw.ellipse([
            center_x + int(10 * scale) - eye_radius, eye_y - eye_radius,
            center_x + int(10 * scale) + eye_radius, eye_y + eye_radius
        ], fill=(255, 255, 255), outline=head_outline, width=1)
        
        # Right pupil
        draw.ellipse([
            center_x + int(10 * scale) - pupil_radius, eye_y - pupil_radius,
            center_x + int(10 * scale) + pupil_radius, eye_y + pupil_radius
        ], fill=eye_color)
        
        # Draw more realistic flippers
        self.draw_realistic_flippers(draw, center_x, center_y, flipper_color, flipper_outline, scale)
    
    def draw_detailed_shell_pattern(self, draw: ImageDraw.Draw, center_x: int, center_y: int, 
                                  shell_width: int, shell_height: int, shell_color: Tuple[int, int, int], 
                                  shell_outline: Tuple[int, int, int], shell_highlight: Tuple[int, int, int], 
                                  scale: float):
        """
        Draw detailed and realistic turtle shell scutes pattern
        """
        # Central vertebral scutes (along the spine)
        vertebral_scute_width = int(12 * scale)
        vertebral_scute_height = int(8 * scale)
        
        for i in range(5):
            x = center_x
            y = center_y - int(20 * scale) + i * int(10 * scale)
            
            # Create hexagonal vertebral scute
            scute_points = []
            for j in range(6):
                angle = j * 3.14159 / 3
                if j % 2 == 0:
                    px = x + int(vertebral_scute_width * 0.6)
                else:
                    px = x + int(vertebral_scute_width * 0.3)
                py = y + int(vertebral_scute_height * 0.5 * (1 if j < 3 else -1))
                scute_points.append((px, py))
            
            # Alternate colors for vertebral scutes
            fill_color = shell_outline if i % 2 == 0 else self.get_darker_color(shell_color, 0.8)
            draw.polygon(scute_points, fill=fill_color, outline=self.get_darker_color(shell_outline, 0.8))
        
        # Costal scutes (side scutes)
        costal_scute_size = int(10 * scale)
        
        # Left costal scutes
        for row in range(4):
            for col in range(2):
                x = center_x - int(25 * scale) + col * int(15 * scale)
                y = center_y - int(15 * scale) + row * int(12 * scale)
                
                # Create irregular costal scute shape
                scute_points = [
                    (x - costal_scute_size//2, y - costal_scute_size//3),
                    (x + costal_scute_size//2, y - costal_scute_size//3),
                    (x + costal_scute_size//2 + int(2 * scale), y + costal_scute_size//3),
                    (x, y + costal_scute_size//2),
                    (x - costal_scute_size//2 - int(2 * scale), y + costal_scute_size//3)
                ]
                
                fill_color = shell_highlight if (row + col) % 2 == 0 else shell_outline
                draw.polygon(scute_points, fill=fill_color, outline=self.get_darker_color(shell_outline, 0.8))
        
        # Right costal scutes (mirror of left)
        for row in range(4):
            for col in range(2):
                x = center_x + int(25 * scale) - col * int(15 * scale)
                y = center_y - int(15 * scale) + row * int(12 * scale)
                
                # Create irregular costal scute shape
                scute_points = [
                    (x - costal_scute_size//2, y - costal_scute_size//3),
                    (x + costal_scute_size//2, y - costal_scute_size//3),
                    (x + costal_scute_size//2 + int(2 * scale), y + costal_scute_size//3),
                    (x, y + costal_scute_size//2),
                    (x - costal_scute_size//2 - int(2 * scale), y + costal_scute_size//3)
                ]
                
                fill_color = shell_highlight if (row + col) % 2 == 0 else shell_outline
                draw.polygon(scute_points, fill=fill_color, outline=self.get_darker_color(shell_outline, 0.8))
        
        # Marginal scutes (edge scutes)
        marginal_size = int(6 * scale)
        
        # Top marginal scutes
        for i in range(6):
            x = center_x - int(35 * scale) + i * int(14 * scale)
            y = center_y - int(25 * scale)
            
            draw.polygon([
                (x - marginal_size//2, y),
                (x + marginal_size//2, y),
                (x + marginal_size//3, y + marginal_size),
                (x - marginal_size//3, y + marginal_size)
            ], fill=shell_outline, outline=self.get_darker_color(shell_outline, 0.8))
        
        # Bottom marginal scutes
        for i in range(4):
            x = center_x - int(20 * scale) + i * int(13 * scale)
            y = center_y + int(20 * scale)
            
            draw.polygon([
                (x - marginal_size//2, y),
                (x + marginal_size//2, y),
                (x + marginal_size//3, y - marginal_size),
                (x - marginal_size//3, y - marginal_size)
            ], fill=shell_outline, outline=self.get_darker_color(shell_outline, 0.8))
    
    def draw_realistic_flippers(self, draw: ImageDraw.Draw, center_x: int, center_y: int, 
                              flipper_color: Tuple[int, int, int], flipper_outline: Tuple[int, int, int], 
                              scale: float):
        """
        Draw realistic sea turtle flippers with proper anatomy
        """
        # Front right flipper - more realistic shape
        fr_points = [
            (center_x + int(40 * scale), center_y - int(5 * scale)),  # Attachment point
            (center_x + int(55 * scale), center_y - int(15 * scale)),  # Upper curve
            (center_x + int(65 * scale), center_y - int(10 * scale)),  # Tip
            (center_x + int(60 * scale), center_y + int(5 * scale)),   # Lower curve
            (center_x + int(45 * scale), center_y + int(10 * scale)),  # Return curve
            (center_x + int(40 * scale), center_y)                     # Back to attachment
        ]
        draw.polygon(fr_points, fill=flipper_color, outline=flipper_outline, width=2)
        
        # Front left flipper - mirror of right
        fl_points = [
            (center_x - int(40 * scale), center_y - int(5 * scale)),
            (center_x - int(55 * scale), center_y - int(15 * scale)),
            (center_x - int(65 * scale), center_y - int(10 * scale)),
            (center_x - int(60 * scale), center_y + int(5 * scale)),
            (center_x - int(45 * scale), center_y + int(10 * scale)),
            (center_x - int(40 * scale), center_y)
        ]
        draw.polygon(fl_points, fill=flipper_color, outline=flipper_outline, width=2)
        
        # Back right flipper - smaller and more rounded
        br_points = [
            (center_x + int(30 * scale), center_y + int(25 * scale)),
            (center_x + int(40 * scale), center_y + int(30 * scale)),
            (center_x + int(38 * scale), center_y + int(45 * scale)),
            (center_x + int(25 * scale), center_y + int(40 * scale))
        ]
        draw.polygon(br_points, fill=flipper_color, outline=flipper_outline, width=2)
        
        # Back left flipper - mirror of right
        bl_points = [
            (center_x - int(30 * scale), center_y + int(25 * scale)),
            (center_x - int(40 * scale), center_y + int(30 * scale)),
            (center_x - int(38 * scale), center_y + int(45 * scale)),
            (center_x - int(25 * scale), center_y + int(40 * scale))
        ]
        draw.polygon(bl_points, fill=flipper_color, outline=flipper_outline, width=2)
    
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
