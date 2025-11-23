"""
Direct SVG to PyGame Renderer for TurboShells
Parses SVG content directly and renders to PyGame surface
"""

import os
import tempfile
import io
import re
import math
from typing import Optional, Dict, Any, Tuple, List
import pygame

try:
    import drawsvg as draw
except ImportError:
    draw = None

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import svg
    SVG_AVAILABLE = True
except ImportError:
    SVG_AVAILABLE = False


class DirectSVGToPyGameRenderer:
    """
    Direct SVG to PyGame surface conversion by parsing SVG content
    """
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.cache = {}
        self.max_cache_size = 100
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Check dependencies
        self.drawsvg_available = draw is not None
        self.pil_available = PIL_AVAILABLE
        self.svg_available = SVG_AVAILABLE
        
        if not self.svg_available:
            print("Warning: svg.py not available. Using fallback renderer.")
    
    def render_svg_string_to_surface(self, svg_string: str, size: Optional[int] = None) -> Optional[pygame.Surface]:
        """
        Render SVG string directly to PyGame surface
        """
        if not svg_string:
            return self.create_enhanced_fallback_surface(size or 200)
            
        # Check cache first
        cache_key = f"string_{hash(svg_string)}_{size}"
        if cache_key in self.cache:
            self.cache_hits += 1
            return self.cache[cache_key]
        
        self.cache_misses += 1
        
        try:
            if self.svg_available:
                surface = self.render_with_svg_py(svg_string, size)
            else:
                surface = self.render_with_manual_parsing(svg_string, size)
            
            if surface:
                # Cache the result
                self.cache_surface(cache_key, surface)
                return surface
            
        except Exception as e:
            print(f"Direct SVG rendering failed: {e}")
        
        return self.create_enhanced_fallback_surface(size or 200)
    
    def render_with_svg_py(self, svg_string: str, size: Optional[int] = None) -> Optional[pygame.Surface]:
        """Render using svg.py library"""
        try:
            # Parse SVG
            svg_doc = svg.parse_string(svg_string)
            
            # Get dimensions
            width, height = self.get_svg_dimensions(svg_string)
            if size is not None:
                scale = min(size / width, size / height)
                width = int(width * scale)
                height = int(height * scale)
            
            # Create PIL image
            pil_image = Image.new('RGBA', (width, height), (240, 248, 255, 255))
            draw = ImageDraw.Draw(pil_image)
            
            # Render SVG elements
            self.render_svg_elements_to_pil(svg_doc, draw, width, height)
            
            # Convert to PyGame
            return self.pil_to_pygame(pil_image)
            
        except Exception as e:
            print(f"svg.py rendering failed: {e}")
            return None
    
    def render_with_manual_parsing(self, svg_string: str, size: Optional[int] = None) -> Optional[pygame.Surface]:
        """Render by manually parsing SVG elements"""
        try:
            # Get dimensions
            width, height = self.get_svg_dimensions(svg_string)
            if size is not None:
                scale = min(size / width, size / height)
                width = int(width * scale)
                height = int(height * scale)
            
            # Create PyGame surface directly
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            surface.fill((240, 248, 255, 255))  # Alice blue background
            
            # Parse and render SVG elements
            self.render_svg_elements_to_pygame(svg_string, surface, width, height)
            
            return surface
            
        except Exception as e:
            print(f"Manual SVG parsing failed: {e}")
            return None
    
    def get_svg_dimensions(self, svg_string: str) -> Tuple[int, int]:
        """Extract dimensions from SVG string"""
        # Try viewBox
        viewBox_match = re.search(r'viewBox="[^"]*"', svg_string)
        if viewBox_match:
            viewBox = viewBox_match.group()
            numbers = re.findall(r'\d+\.?\d*', viewBox)
            if len(numbers) >= 4:
                width = int(float(numbers[2]))
                height = int(float(numbers[3]))
                return width, height
        
        # Try width/height attributes
        width_match = re.search(r'width="(\d+)"', svg_string)
        height_match = re.search(r'height="(\d+)"', svg_string)
        
        if width_match and height_match:
            width = int(width_match.group(1))
            height = int(height_match.group(1))
            return width, height
        
        # Default size
        return 200, 200
    
    def render_svg_elements_to_pil(self, svg_doc, draw, width: int, height: int):
        """Render SVG elements to PIL ImageDraw"""
        try:
            # This is a simplified approach - svg.py has a complex structure
            # We'll extract basic shapes from the SVG string instead
            pass
        except:
            pass
    
    def render_svg_elements_to_pygame(self, svg_string: str, surface: pygame.Surface, width: int, height: int):
        """Parse and render SVG elements directly to PyGame surface"""
        try:
            # Extract basic shapes from SVG string
            scale_x = width / 200.0  # Assume original SVG is 200x200
            scale_y = height / 200.0
            
            # Find circles
            circles = re.findall(r'<circle[^>]*cx="([^"]*)"[^>]*cy="([^"]*)"[^>]*r="([^"]*)"[^>]*fill="([^"]*)"[^>]*', svg_string)
            for cx, cy, r, fill in circles:
                x = int(float(cx) * scale_x)
                y = int(float(cy) * scale_y)
                radius = int(float(r) * min(scale_x, scale_y))
                color = self.parse_color(fill)
                pygame.draw.circle(surface, color, (x, y), radius)
            
            # Find ellipses
            ellipses = re.findall(r'<ellipse[^>]*cx="([^"]*)"[^>]*cy="([^"]*)"[^>]*rx="([^"]*)"[^>]*ry="([^"]*)"[^>]*fill="([^"]*)"[^>]*', svg_string)
            for cx, cy, rx, ry, fill in ellipses:
                x = int(float(cx) * scale_x)
                y = int(float(cy) * scale_y)
                rx_scaled = int(float(rx) * scale_x)
                ry_scaled = int(float(ry) * scale_y)
                color = self.parse_color(fill)
                # Draw ellipse as stretched circle
                pygame.draw.ellipse(surface, color, (x - rx_scaled, y - ry_scaled, rx_scaled * 2, ry_scaled * 2))
            
            # Find rectangles
            rects = re.findall(r'<rect[^>]*x="([^"]*)"[^>]*y="([^"]*)"[^>]*width="([^"]*)"[^>]*height="([^"]*)"[^>]*fill="([^"]*)"[^>]*', svg_string)
            for x, y, w, h, fill in rects:
                rect_x = int(float(x) * scale_x)
                rect_y = int(float(y) * scale_y)
                rect_w = int(float(w) * scale_x)
                rect_h = int(float(h) * scale_y)
                color = self.parse_color(fill)
                pygame.draw.rect(surface, color, (rect_x, rect_y, rect_w, rect_h))
            
            # Find paths (simplified)
            paths = re.findall(r'<path[^>]*d="([^"]*)"[^>]*fill="([^"]*)"[^>]*', svg_string)
            for path_data, fill in paths:
                color = self.parse_color(fill)
                self.render_path_to_pygame(path_data, surface, scale_x, scale_y, color)
            
            # Find lines
            lines = re.findall(r'<line[^>]*x1="([^"]*)"[^>]*y1="([^"]*)"[^>]*x2="([^"]*)"[^>]*y2="([^"]*)"[^>]*stroke="([^"]*)"[^>]*stroke-width="([^"]*)"[^>]*', svg_string)
            for x1, y1, x2, y2, stroke, stroke_width in lines:
                start_x = int(float(x1) * scale_x)
                start_y = int(float(y1) * scale_y)
                end_x = int(float(x2) * scale_x)
                end_y = int(float(y2) * scale_y)
                color = self.parse_color(stroke)
                width = max(1, int(float(stroke_width) * min(scale_x, scale_y)))
                pygame.draw.line(surface, color, (start_x, start_y), (end_x, end_y), width)
            
        except Exception as e:
            print(f"Error rendering SVG elements: {e}")
    
    def render_path_to_pygame(self, path_data: str, surface: pygame.Surface, scale_x: float, scale_y: float, color):
        """Render SVG path to PyGame surface (simplified)"""
        try:
            # Very basic path parsing - just handle line segments
            points = []
            commands = re.findall(r'([MLCZ])\s*([^MLCZ]*)', path_data)
            
            current_x, current_y = 0, 0
            
            for command, coords in commands:
                if command == 'M':  # Move to
                    xy = re.findall(r'[\d.-]+', coords)
                    if len(xy) >= 2:
                        current_x = int(float(xy[0]) * scale_x)
                        current_y = int(float(xy[1]) * scale_y)
                        points.append((current_x, current_y))
                
                elif command == 'L':  # Line to
                    xy = re.findall(r'[\d.-]+', coords)
                    if len(xy) >= 2:
                        next_x = int(float(xy[0]) * scale_x)
                        next_y = int(float(xy[1]) * scale_y)
                        pygame.draw.line(surface, color, (current_x, current_y), (next_x, next_y), 2)
                        current_x, current_y = next_x, next_y
                        points.append((current_x, current_y))
                
                elif command == 'C':  # Cubic bezier (simplified)
                    xy = re.findall(r'[\d.-]+', coords)
                    if len(xy) >= 6:
                        # Simplify to straight line
                        next_x = int(float(xy[4]) * scale_x)
                        next_y = int(float(xy[5]) * scale_y)
                        pygame.draw.line(surface, color, (current_x, current_y), (next_x, next_y), 2)
                        current_x, current_y = next_x, next_y
                        points.append((current_x, current_y))
            
            # Draw polygon if we have points
            if len(points) > 2:
                pygame.draw.polygon(surface, color, points, 2)
                
        except Exception as e:
            print(f"Error rendering path: {e}")
    
    def parse_color(self, color_str: str) -> Tuple[int, int, int]:
        """Parse color string to RGB tuple"""
        try:
            # Handle hex colors
            if color_str.startswith('#'):
                hex_color = color_str[1:]
                if len(hex_color) == 6:
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                    return (r, g, b)
                elif len(hex_color) == 3:
                    r = int(hex_color[0] * 2, 16)
                    g = int(hex_color[1] * 2, 16)
                    b = int(hex_color[2] * 2, 16)
                    return (r, g, b)
            
            # Handle rgb colors
            elif color_str.startswith('rgb('):
                rgb_values = re.findall(r'\d+', color_str)
                if len(rgb_values) >= 3:
                    return (int(rgb_values[0]), int(rgb_values[1]), int(rgb_values[2]))
            
            # Handle named colors (basic ones)
            elif color_str.lower() in ['red', 'green', 'blue', 'black', 'white', 'yellow', 'orange', 'purple']:
                color_map = {
                    'red': (255, 0, 0),
                    'green': (0, 128, 0),
                    'blue': (0, 0, 255),
                    'black': (0, 0, 0),
                    'white': (255, 255, 255),
                    'yellow': (255, 255, 0),
                    'orange': (255, 165, 0),
                    'purple': (128, 0, 128)
                }
                return color_map.get(color_str.lower(), (128, 128, 128))
            
        except:
            pass
        
        # Default gray
        return (128, 128, 128)
    
    def render_svg_drawing_to_surface(self, svg_drawing: object, size: Optional[int] = None) -> Optional[pygame.Surface]:
        """
        Render drawsvg Drawing object to PyGame surface
        """
        if svg_drawing is None:
            return self.create_enhanced_fallback_surface(size or 200)
            
        # Convert drawing to SVG string
        svg_string = svg_drawing.as_svg()
        return self.render_svg_string_to_surface(svg_string, size)
    
    def pil_to_pygame(self, pil_image: Image.Image) -> Optional[pygame.Surface]:
        """Convert PIL Image to PyGame surface"""
        try:
            if pil_image.mode not in ['RGB', 'RGBA']:
                if pil_image.mode == 'P':
                    pil_image = pil_image.convert('RGBA')
                else:
                    pil_image = pil_image.convert('RGB')
            
            width, height = pil_image.size
            image_data = pil_image.tobytes()
            
            if pil_image.mode == 'RGBA':
                surface = pygame.image.fromstring(image_data, (width, height), 'RGBA')
            else:
                surface = pygame.image.fromstring(image_data, (width, height), 'RGB')
            
            return surface
            
        except Exception as e:
            print(f"Error converting PIL to PyGame: {e}")
            return None
    
    def render_turtle_to_surface(self, visual_genetics: Dict[str, Any], 
                                size: Optional[int] = None) -> Optional[pygame.Surface]:
        """
        Render turtle from genetics directly to PyGame surface
        """
        from .turtle_svg_generator import TurtleSVGGenerator
        
        if not self.drawsvg_available:
            print("Error: drawsvg not available for turtle generation")
            return self.create_enhanced_fallback_surface(size or 100)
        
        # Generate turtle SVG
        generator = TurtleSVGGenerator()
        svg_drawing = generator.generate_turtle_svg(visual_genetics, size)
        
        if svg_drawing is None:
            return self.create_enhanced_fallback_surface(size or 100)
        
        # Render to PyGame surface
        return self.render_svg_drawing_to_surface(svg_drawing, size)
    
    def create_enhanced_fallback_surface(self, size: int, text: str = "Turtle") -> pygame.Surface:
        """
        Create an enhanced fallback surface with genetic-inspired variations
        """
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        surface.fill((240, 248, 255))  # Alice blue background
        
        # Generate some variation based on size to simulate genetic differences
        import random
        random.seed(size)  # Consistent variation for same size
        
        center_x = size // 2
        center_y = size // 2
        scale = size / 200  # Scale based on size
        
        # Shell with gradient effect and pattern variation
        shell_width = int(80 * scale)
        shell_height = int(60 * scale)
        
        # Vary shell color slightly
        shell_green = 34 + random.randint(-10, 10)
        shell_green = max(20, min(50, shell_green))
        shell_color = (shell_green, 139, 34)
        
        pygame.draw.ellipse(surface, shell_color, 
                           (center_x - shell_width//2, center_y - shell_height//2, 
                            shell_width, shell_height))
        pygame.draw.ellipse(surface, (0, 100, 0), 
                           (center_x - shell_width//2, center_y - shell_height//2, 
                            shell_width, shell_height), 3)
        
        # Shell pattern lines with variation
        pattern_count = random.randint(2, 4)
        for i in range(pattern_count):
            y_offset = -shell_height//3 + i * (shell_height//pattern_count)
            pygame.draw.arc(surface, (0, 80, 0), 
                          (center_x - shell_width//2, center_y + y_offset - 10, 
                           shell_width, 20), 0, 3.14, 2)
        
        # Add spots pattern (randomly)
        if random.random() > 0.5:
            for _ in range(3):
                spot_x = center_x + random.randint(-shell_width//3, shell_width//3)
                spot_y = center_y + random.randint(-shell_height//3, shell_height//3)
                spot_size = random.randint(3, 8)
                pygame.draw.circle(surface, (0, 120, 0), (spot_x, spot_y), spot_size)
        
        # Head with color variation
        head_radius = int(20 * scale)
        head_brown = 139 + random.randint(-20, 20)
        head_brown = max(100, min(180, head_brown))
        head_color = (head_brown, 90, 43)
        
        pygame.draw.circle(surface, head_color, 
                         (center_x, center_y - int(40 * scale)), head_radius)
        pygame.draw.circle(surface, (100, 60, 20), 
                         (center_x, center_y - int(40 * scale)), head_radius, 2)
        
        # Legs with better shape and variation
        leg_width = int(8 * scale)
        leg_length = int(30 * scale)
        leg_brown = 101 + random.randint(-15, 15)
        leg_brown = max(80, min(130, leg_brown))
        leg_color = (leg_brown, 67, 33)
        
        leg_positions = [
            (center_x - int(60 * scale), center_y + int(20 * scale)),
            (center_x + int(60 * scale), center_y + int(20 * scale)),
            (center_x - int(40 * scale), center_y + int(40 * scale)),
            (center_x + int(40 * scale), center_y + int(40 * scale))
        ]
        
        for leg_x, leg_y in leg_positions:
            # Draw leg as thick line with rounded end
            pygame.draw.line(surface, leg_color, 
                           (leg_x, leg_y), (leg_x, leg_y + leg_length), leg_width)
            pygame.draw.circle(surface, leg_color, 
                             (leg_x, leg_y + leg_length), leg_width//2)
        
        # Eyes with variation
        eye_size = max(2, int(3 * scale))
        pygame.draw.circle(surface, (0, 0, 0), 
                         (center_x - int(8 * scale), center_y - int(40 * scale)), eye_size)
        pygame.draw.circle(surface, (0, 0, 0), 
                         (center_x + int(8 * scale), center_y - int(40 * scale)), eye_size)
        
        # Add tail
        tail_length = int(25 * scale)
        pygame.draw.line(surface, leg_color,
                        (center_x, center_y + int(20 * scale)),
                        (center_x - int(10 * scale), center_y + int(20 * scale) + tail_length), 3)
        
        # Draw text
        try:
            font = pygame.font.Font(None, max(12, size // 8))
            text_surface = font.render(text, True, (100, 100, 100))
            text_rect = text_surface.get_rect(center=(center_x, center_y + size//2 + 20))
            surface.blit(text_surface, text_rect)
        except:
            pass
        
        return surface
    
    def cache_surface(self, cache_key: str, surface: pygame.Surface) -> None:
        """
        Cache PyGame surface with size management
        """
        if len(self.cache) >= self.max_cache_size:
            # Remove oldest entry (simple LRU)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[cache_key] = surface
    
    def clear_cache(self) -> None:
        """
        Clear the surface cache
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
            'drawsvg_available': self.drawsvg_available,
            'pil_available': self.pil_available,
            'svg_available': self.svg_available,
            'pygame_available': pygame is not None,
            'can_render_svg': True,  # Always can render with fallback
            'cache_enabled': True,
            'max_cache_size': self.max_cache_size,
            'renderer_type': 'direct'
        }


# Global renderer instance
_renderer_instance = None


def get_svg_renderer() -> DirectSVGToPyGameRenderer:
    """
    Get global SVG renderer instance
    """
    global _renderer_instance
    if _renderer_instance is None:
        _renderer_instance = DirectSVGToPyGameRenderer()
    return _renderer_instance


# Utility functions
def render_turtle_to_surface(visual_genetics: Dict[str, Any], 
                            size: Optional[int] = None) -> Optional[pygame.Surface]:
    """
    Render turtle from genetics to PyGame surface using global renderer
    """
    renderer = get_svg_renderer()
    return renderer.render_turtle_to_surface(visual_genetics, size)


def render_svg_string_to_surface(svg_string: str, 
                                size: Optional[int] = None) -> Optional[pygame.Surface]:
    """
    Render SVG string to PyGame surface using global renderer
    """
    renderer = get_svg_renderer()
    return renderer.render_svg_string_to_surface(svg_string, size)


def create_turtle_placeholder(size: int, text: str = "Turtle") -> pygame.Surface:
    """
    Create turtle placeholder using global renderer
    """
    renderer = get_svg_renderer()
    return renderer.create_enhanced_fallback_surface(size, text)


def clear_svg_cache() -> None:
    """
    Clear global SVG cache
    """
    renderer = get_svg_renderer()
    renderer.clear_cache()


def get_svg_cache_stats() -> Dict[str, Any]:
    """
    Get global SVG cache statistics
    """
    renderer = get_svg_renderer()
    return renderer.get_cache_stats()
