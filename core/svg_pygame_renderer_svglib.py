"""
SVG to PyGame Renderer using svglib for TurboShells
Alternative renderer that uses svglib + reportlab instead of cairosvg
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

try:
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
    SVGLIB_AVAILABLE = True
except ImportError:
    SVGLIB_AVAILABLE = False


class SvglibSVGToPyGameRenderer:
    """
    SVG to PyGame surface conversion using svglib and reportlab
    Provides better SVG rendering without requiring cairo
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
        self.svglib_available = SVGLIB_AVAILABLE
        
        if not self.svglib_available:
            print("Warning: svglib not available. SVG rendering will be limited.")
    
    def render_svg_string_to_surface(self, svg_string: str, size: Optional[int] = None) -> Optional[pygame.Surface]:
        """
        Render SVG string directly to PyGame surface using svglib
        """
        if not svg_string or not self.svglib_available:
            return self.create_fallback_surface(size or 200)
            
        # Check cache first
        cache_key = f"string_{hash(svg_string)}_{size}"
        if cache_key in self.cache:
            self.cache_hits += 1
            return self.cache[cache_key]
        
        self.cache_misses += 1
        
        try:
            # Parse SVG and convert to reportlab drawing
            drawing = svg2rlg(io.StringIO(svg_string))
            if drawing is None:
                return self.create_fallback_surface(size or 200)
            
            # Get original dimensions
            orig_width, orig_height = drawing.width, drawing.height
            
            # Calculate output size
            if size is None:
                output_width = int(orig_width)
                output_height = int(orig_height)
            else:
                # Scale to fit within size while maintaining aspect ratio
                scale = min(size / orig_width, size / orig_height)
                output_width = int(orig_width * scale)
                output_height = int(orig_height * scale)
            
            # Render to PIL Image
            pil_image = renderPM.drawToPIL(drawing, dpi=72, 
                                          width=output_width, height=output_height)
            
            if pil_image:
                # Convert PIL to PyGame surface
                if self.pil_available:
                    surface = self.pil_to_pygame(pil_image)
                else:
                    surface = self.pil_to_pygame_simple(pil_image)
                
                if surface:
                    # Cache the result
                    self.cache_surface(cache_key, surface)
                    return surface
            
        except Exception as e:
            print(f"Error converting SVG to PyGame surface: {e}")
            return self.create_fallback_surface(size or 200)
        
        return self.create_fallback_surface(size or 200)
    
    def render_svg_drawing_to_surface(self, svg_drawing: object, size: Optional[int] = None) -> Optional[pygame.Surface]:
        """
        Render drawsvg Drawing object to PyGame surface
        """
        if svg_drawing is None:
            return self.create_fallback_surface(size or 200)
            
        # Convert drawing to SVG string
        svg_string = svg_drawing.as_svg()
        return self.render_svg_string_to_surface(svg_string, size)
    
    def pil_to_pygame(self, pil_image: Image.Image) -> Optional[pygame.Surface]:
        """
        Convert PIL Image to PyGame surface with proper format handling
        """
        try:
            # Ensure image is in RGB or RGBA format
            if pil_image.mode not in ['RGB', 'RGBA']:
                if pil_image.mode == 'P':
                    pil_image = pil_image.convert('RGBA')
                else:
                    pil_image = pil_image.convert('RGB')
            
            # Convert to PyGame surface
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
    
    def pil_to_pygame_simple(self, pil_image: Image.Image) -> Optional[pygame.Surface]:
        """
        Convert PIL Image to PyGame surface without advanced features
        """
        try:
            # Save to temp file and load with pygame
            temp_file = os.path.join(self.temp_dir, "temp_pil.png")
            pil_image.save(temp_file, 'PNG')
            
            surface = pygame.image.load(temp_file)
            os.unlink(temp_file)
            
            return surface
            
        except Exception as e:
            print(f"Error converting PIL to PyGame (simple): {e}")
            return None
    
    def render_turtle_to_surface(self, visual_genetics: Dict[str, Any], 
                                size: Optional[int] = None) -> Optional[pygame.Surface]:
        """
        Render turtle from genetics directly to PyGame surface
        """
        from .turtle_svg_generator import TurtleSVGGenerator
        
        if not self.drawsvg_available:
            print("Error: drawsvg not available for turtle generation")
            return self.create_fallback_surface(size or 100)
        
        # Generate turtle SVG
        generator = TurtleSVGGenerator()
        svg_drawing = generator.generate_turtle_svg(visual_genetics, size)
        
        if svg_drawing is None:
            return self.create_fallback_surface(size or 100)
        
        # Render to PyGame surface
        return self.render_svg_drawing_to_surface(svg_drawing, size)
    
    def create_fallback_surface(self, size: int, text: str = "Turtle") -> pygame.Surface:
        """
        Create a better fallback surface when SVG rendering fails
        """
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        surface.fill((240, 248, 255))  # Alice blue background
        
        # Draw more detailed turtle shape
        center_x = size // 2
        center_y = size // 2
        scale = size / 200  # Scale based on size
        
        # Shell with gradient effect
        shell_width = int(80 * scale)
        shell_height = int(60 * scale)
        pygame.draw.ellipse(surface, (34, 139, 34), 
                           (center_x - shell_width//2, center_y - shell_height//2, 
                            shell_width, shell_height))
        pygame.draw.ellipse(surface, (0, 100, 0), 
                           (center_x - shell_width//2, center_y - shell_height//2, 
                            shell_width, shell_height), 3)
        
        # Shell pattern lines
        for i in range(3):
            y_offset = -shell_height//4 + i * (shell_height//4)
            pygame.draw.arc(surface, (0, 80, 0), 
                          (center_x - shell_width//2, center_y + y_offset - 10, 
                           shell_width, 20), 0, 3.14, 2)
        
        # Head
        head_radius = int(20 * scale)
        pygame.draw.circle(surface, (139, 90, 43), 
                         (center_x, center_y - int(40 * scale)), head_radius)
        pygame.draw.circle(surface, (100, 60, 20), 
                         (center_x, center_y - int(40 * scale)), head_radius, 2)
        
        # Legs with better shape
        leg_width = int(8 * scale)
        leg_length = int(30 * scale)
        leg_positions = [
            (center_x - int(60 * scale), center_y + int(20 * scale)),
            (center_x + int(60 * scale), center_y + int(20 * scale)),
            (center_x - int(40 * scale), center_y + int(40 * scale)),
            (center_x + int(40 * scale), center_y + int(40 * scale))
        ]
        
        for leg_x, leg_y in leg_positions:
            # Draw leg as thick line with rounded end
            pygame.draw.line(surface, (101, 67, 33), 
                           (leg_x, leg_y), (leg_x, leg_y + leg_length), leg_width)
            pygame.draw.circle(surface, (101, 67, 33), 
                             (leg_x, leg_y + leg_length), leg_width//2)
        
        # Eyes
        eye_size = max(2, int(3 * scale))
        pygame.draw.circle(surface, (0, 0, 0), 
                         (center_x - int(8 * scale), center_y - int(40 * scale)), eye_size)
        pygame.draw.circle(surface, (0, 0, 0), 
                         (center_x + int(8 * scale), center_y - int(40 * scale)), eye_size)
        
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
            'svglib_available': self.svglib_available,
            'pygame_available': pygame is not None,
            'can_render_svg': self.svglib_available and self.pil_available and pygame is not None,
            'cache_enabled': True,
            'max_cache_size': self.max_cache_size,
            'renderer_type': 'svglib'
        }


# Global renderer instance
_renderer_instance = None


def get_svg_renderer() -> SvglibSVGToPyGameRenderer:
    """
    Get global SVG renderer instance
    """
    global _renderer_instance
    if _renderer_instance is None:
        _renderer_instance = SvglibSVGToPyGameRenderer()
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
    return renderer.create_fallback_surface(size, text)


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
