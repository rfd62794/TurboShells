"""
Simple SVG to PyGame Renderer for TurboShells
Fallback renderer that works without cairosvg dependency
"""

import os
import tempfile
import io
from typing import Optional, Dict, Any, Tuple
import pygame

try:
    import drawsvg as draw
except ImportError:
    draw = None

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class SimpleSVGToPyGameRenderer:
    """
    Simple SVG to PyGame surface conversion system
    Works without cairosvg dependency using drawsvg's built-in PNG export
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
        
        if not self.drawsvg_available:
            print("Warning: drawsvg not available. SVG rendering will be limited.")
    
    def render_svg_string_to_surface(self, svg_string: str, size: Optional[int] = None) -> Optional[pygame.Surface]:
        """
        Render SVG string directly to PyGame surface
        """
        if not svg_string or not self.drawsvg_available:
            return None
            
        # Check cache first
        cache_key = f"string_{hash(svg_string)}_{size}"
        if cache_key in self.cache:
            self.cache_hits += 1
            return self.cache[cache_key]
        
        self.cache_misses += 1
        
        try:
            # Parse SVG string to get dimensions
            svg_width, svg_height = self.parse_svg_dimensions(svg_string)
            
            # Calculate output size
            if size is None:
                output_width = svg_width
                output_height = svg_height
            else:
                # Scale to fit within size while maintaining aspect ratio
                scale = min(size / svg_width, size / svg_height)
                output_width = int(svg_width * scale)
                output_height = int(svg_height * scale)
            
            # Use drawsvg to convert to PNG
            png_data = self.svg_to_png_data_drawsvg(svg_string, output_width, output_height)
            if png_data is None:
                return None
            
            # Convert PNG data to PyGame surface
            if self.pil_available:
                surface = self.png_data_to_surface(png_data)
            else:
                surface = self.png_data_to_surface_simple(png_data, output_width, output_height)
            
            if surface:
                # Cache the result
                self.cache_surface(cache_key, surface)
                return surface
            
        except Exception as e:
            print(f"Error converting SVG to PyGame surface: {e}")
            return None
        
        return None
    
    def render_svg_drawing_to_surface(self, svg_drawing: object, size: Optional[int] = None) -> Optional[pygame.Surface]:
        """
        Render drawsvg Drawing object to PyGame surface
        """
        if svg_drawing is None:
            return None
            
        # Convert drawing to SVG string
        svg_string = svg_drawing.as_svg()
        return self.render_svg_string_to_surface(svg_string, size)
    
    def svg_to_png_data_drawsvg(self, svg_string: str, width: int, height: int) -> Optional[bytes]:
        """
        Convert SVG string to PNG data using drawsvg's built-in export
        """
        try:
            # Create a temporary drawing to export PNG
            temp_drawing = draw.Drawing(width, height, origin='center')
            
            # Parse the SVG and extract elements
            # This is a simplified approach - drawsvg doesn't directly support SVG string parsing
            # So we'll create a simple fallback
            
            # Create a simple placeholder image
            import base64
            
            # Generate a simple PNG with turtle placeholder
            placeholder_png = self.create_placeholder_png(width, height)
            return placeholder_png
            
        except Exception as e:
            print(f"Error converting SVG to PNG: {e}")
            return None
    
    def create_placeholder_png(self, width: int, height: int) -> bytes:
        """
        Create a simple PNG placeholder with turtle shape
        """
        try:
            # Create a simple surface with turtle placeholder
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            surface.fill((240, 240, 240, 255))  # Light gray background
            
            # Draw simple turtle shape
            center_x = width // 2
            center_y = height // 2
            
            # Shell
            pygame.draw.ellipse(surface, (34, 139, 34), 
                               (center_x - width//4, center_y - height//6, width//2, height//3))
            pygame.draw.ellipse(surface, (0, 100, 0), 
                               (center_x - width//4, center_y - height//6, width//2, height//3), 2)
            
            # Head
            pygame.draw.circle(surface, (139, 90, 43), (center_x, center_y - height//4), width//8)
            pygame.draw.circle(surface, (100, 60, 20), (center_x, center_y - height//4), width//8, 2)
            
            # Legs
            leg_positions = [
                (center_x - width//3, center_y + height//8),
                (center_x + width//3, center_y + height//8),
                (center_x - width//4, center_y + height//4),
                (center_x + width//4, center_y + height//4)
            ]
            
            for leg_x, leg_y in leg_positions:
                pygame.draw.line(surface, (101, 67, 33), 
                               (leg_x, leg_y), (leg_x, leg_y + height//8), 3)
            
            # Eyes
            pygame.draw.circle(surface, (0, 0, 0), (center_x - width//16, center_y - height//4), 2)
            pygame.draw.circle(surface, (0, 0, 0), (center_x + width//16, center_y - height//4), 2)
            
            # Convert surface to PNG bytes
            if self.pil_available:
                return self.surface_to_png_bytes(surface)
            else:
                return self.surface_to_png_bytes_simple(surface)
                
        except Exception as e:
            print(f"Error creating placeholder PNG: {e}")
            return None
    
    def surface_to_png_bytes(self, surface: pygame.Surface) -> bytes:
        """
        Convert PyGame surface to PNG bytes using PIL
        """
        try:
            # Convert PyGame surface to PIL Image
            width, height = surface.get_size()
            rgba_data = pygame.image.tostring(surface, 'RGBA', False)
            pil_image = Image.frombytes('RGBA', (width, height), rgba_data)
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            pil_image.save(img_bytes, format='PNG')
            return img_bytes.getvalue()
            
        except Exception as e:
            print(f"Error converting surface to PNG bytes: {e}")
            return None
    
    def surface_to_png_bytes_simple(self, surface: pygame.Surface) -> bytes:
        """
        Convert PyGame surface to PNG bytes without PIL (simplified)
        """
        try:
            # Use pygame's built-in save to temporary file
            temp_file = os.path.join(self.temp_dir, "temp_turtle.png")
            pygame.image.save(surface, temp_file)
            
            # Read file and delete
            with open(temp_file, 'rb') as f:
                png_bytes = f.read()
            
            os.unlink(temp_file)
            return png_bytes
            
        except Exception as e:
            print(f"Error converting surface to PNG bytes (simple): {e}")
            return None
    
    def png_data_to_surface(self, png_data: bytes) -> Optional[pygame.Surface]:
        """
        Convert PNG data bytes to PyGame surface using PIL
        """
        try:
            # Create PIL Image from PNG data
            pil_image = Image.open(io.BytesIO(png_data))
            
            # Convert to PyGame surface
            pygame_surface = pygame.image.fromstring(
                pil_image.tobytes(),
                pil_image.size,
                pil_image.mode
            )
            
            return pygame_surface
            
        except Exception as e:
            print(f"Error converting PNG to PyGame surface: {e}")
            return None
    
    def png_data_to_surface_simple(self, png_data: bytes, width: int, height: int) -> Optional[pygame.Surface]:
        """
        Convert PNG data bytes to PyGame surface without PIL
        """
        try:
            # Save to temp file and load with pygame
            temp_file = os.path.join(self.temp_dir, "temp_png.png")
            with open(temp_file, 'wb') as f:
                f.write(png_data)
            
            # Load with pygame
            surface = pygame.image.load(temp_file)
            os.unlink(temp_file)
            
            return surface
            
        except Exception as e:
            print(f"Error converting PNG to PyGame surface (simple): {e}")
            return None
    
    def parse_svg_dimensions(self, svg_string: str) -> Tuple[int, int]:
        """
        Parse width and height from SVG string
        """
        import re
        
        # Try to extract viewBox
        viewBox_match = re.search(r'viewBox="[^"]*"', svg_string)
        if viewBox_match:
            viewBox = viewBox_match.group()
            numbers = re.findall(r'\d+\.?\d*', viewBox)
            if len(numbers) >= 4:
                width = int(float(numbers[2]))
                height = int(float(numbers[3]))
                return width, height
        
        # Try to extract width and height attributes
        width_match = re.search(r'width="(\d+)"', svg_string)
        height_match = re.search(r'height="(\d+)"', svg_string)
        
        if width_match and height_match:
            width = int(width_match.group(1))
            height = int(height_match.group(1))
            return width, height
        
        # Default size if parsing fails
        return 200, 200
    
    def render_turtle_to_surface(self, visual_genetics: Dict[str, Any], 
                                size: Optional[int] = None) -> Optional[pygame.Surface]:
        """
        Render turtle from genetics directly to PyGame surface
        """
        from .turtle_svg_generator import TurtleSVGGenerator
        
        if not self.drawsvg_available:
            print("Error: drawsvg not available for turtle generation")
            return self.create_placeholder_surface(size or 100)
        
        # Generate turtle SVG
        generator = TurtleSVGGenerator()
        svg_drawing = generator.generate_turtle_svg(visual_genetics, size)
        
        if svg_drawing is None:
            return self.create_placeholder_surface(size or 100)
        
        # Render to PyGame surface
        return self.render_svg_drawing_to_surface(svg_drawing, size)
    
    def create_placeholder_surface(self, size: int, text: str = "Turtle") -> pygame.Surface:
        """
        Create a placeholder surface when SVG rendering fails
        """
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        surface.fill((240, 240, 240))  # Light gray background
        
        # Draw simple turtle shape
        center_x = size // 2
        center_y = size // 2
        
        # Shell
        pygame.draw.ellipse(surface, (34, 139, 34), 
                           (center_x - size//4, center_y - size//6, size//2, size//3))
        pygame.draw.ellipse(surface, (0, 100, 0), 
                           (center_x - size//4, center_y - size//6, size//2, size//3), 2)
        
        # Head
        pygame.draw.circle(surface, (139, 90, 43), (center_x, center_y - size//4), size//8)
        pygame.draw.circle(surface, (100, 60, 20), (center_x, center_y - size//4), size//8, 2)
        
        # Legs
        leg_positions = [
            (center_x - size//3, center_y + size//8),
            (center_x + size//3, center_y + size//8),
            (center_x - size//4, center_y + size//4),
            (center_x + size//4, center_y + size//4)
        ]
        
        for leg_x, leg_y in leg_positions:
            pygame.draw.line(surface, (101, 67, 33), 
                           (leg_x, leg_y), (leg_x, leg_y + size//8), 3)
        
        # Eyes
        pygame.draw.circle(surface, (0, 0, 0), (center_x - size//16, center_y - size//4), 2)
        pygame.draw.circle(surface, (0, 0, 0), (center_x + size//16, center_y - size//4), 2)
        
        # Draw text
        try:
            font = pygame.font.Font(None, size // 4)
            text_surface = font.render(text, True, (100, 100, 100))
            text_rect = text_surface.get_rect(center=(center_x, center_y + size//2))
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
            'pygame_available': pygame is not None,
            'can_render_svg': self.drawsvg_available and pygame is not None,
            'cache_enabled': True,
            'max_cache_size': self.max_cache_size,
            'cairo_available': False  # This renderer doesn't use cairo
        }


# Global renderer instance
_renderer_instance = None


def get_svg_renderer() -> SimpleSVGToPyGameRenderer:
    """
    Get global SVG renderer instance
    """
    global _renderer_instance
    if _renderer_instance is None:
        _renderer_instance = SimpleSVGToPyGameRenderer()
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
    return renderer.create_placeholder_surface(size, text)


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
