"""
Pygame Turtle Renderer Port for TurboShells
Converts existing PIL renderer output to pygame surfaces
"""

import pygame
import io
from typing import Dict, Any, Optional
from PIL import Image

# Import the existing renderer
from .direct_turtle_renderer import DirectTurtleRenderer


class PygameTurtleRenderer:
    """Pygame adapter for the existing DirectTurtleRenderer"""
    
    def __init__(self):
        self.direct_renderer = DirectTurtleRenderer()
    
    def render_turtle(self, turtle, size: int = 120) -> pygame.Surface:
        """
        Render a turtle using the existing PIL renderer and convert to pygame surface
        This preserves all customizations from the original renderer
        """
        try:
            # Get genetics data from turtle
            genetics = getattr(turtle, 'visual_genetics', {})
            
            # Use the existing renderer to create PIL Image
            pil_image = self._render_to_pil(genetics, size)
            
            # Convert PIL Image to pygame surface
            return self._pil_to_pygame(pil_image)
            
        except Exception as e:
            print(f"Error rendering turtle with PIL converter: {e}")
            # Fallback to simple pygame rendering
            return self._render_fallback(turtle, size)
    
    def _render_to_pil(self, genetics: Dict[str, Any], size: int) -> Image.Image:
        """Use existing renderer to create PIL Image"""
        # Create PIL Image using the existing renderer's internal method
        pil_image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        
        # Import the drawing method from the existing renderer
        from .direct_turtle_renderer import ImageDraw
        draw = ImageDraw.Draw(pil_image)
        
        # Use the existing renderer's draw method
        self.direct_renderer.draw_realistic_turtle(draw, genetics, size)
        
        return pil_image
    
    def _pil_to_pygame(self, pil_image: Image.Image) -> pygame.Surface:
        """Convert PIL Image to pygame surface"""
        # Convert PIL Image to bytes
        img_bytes = io.BytesIO()
        pil_image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Create pygame surface from bytes
        pygame_surface = pygame.image.load(img_bytes)
        
        return pygame_surface
    
    def _render_fallback(self, turtle, size: int) -> pygame.Surface:
        """Simple fallback renderer if PIL conversion fails"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Get genetics data if available
        genetics = getattr(turtle, 'visual_genetics', {})
        
        # Extract colors from genetics or use defaults
        shell_color = self._get_color_from_genetics(genetics, 'shell_color', (74, 144, 226))
        pattern_color = self._get_color_from_genetics(genetics, 'pattern_color', (231, 76, 60))
        
        # Simple turtle shape
        center_x = size // 2
        center_y = size // 2
        
        # Draw shell (ellipse)
        shell_rect = pygame.Rect(center_x - size//3, center_y - size//4, size*2//3, size//2)
        pygame.draw.ellipse(surface, shell_color, shell_rect)
        pygame.draw.ellipse(surface, (0, 0, 0), shell_rect, 2)
        
        # Draw simple pattern
        pygame.draw.circle(surface, pattern_color, (center_x, center_y), size//8)
        
        # Draw head
        pygame.draw.circle(surface, (100, 150, 200), (center_x + size//3, center_y), size//6)
        pygame.draw.circle(surface, (0, 0, 0), (center_x + size//3, center_y), size//6, 2)
        
        return surface
    
    def _get_color_from_genetics(self, genetics: Dict, key: str, default: tuple) -> tuple:
        """Extract color from genetics data or return default"""
        color_data = genetics.get(key, {})
        if isinstance(color_data, dict) and 'value' in color_data:
            color_str = color_data['value']
            if isinstance(color_str, str) and color_str.startswith('#'):
                # Convert hex to RGB
                hex_color = color_str.lstrip('#')
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return default


# Global renderer instance
_renderer = None

def get_pygame_renderer() -> PygameTurtleRenderer:
    """Get or create the global pygame renderer instance"""
    global _renderer
    if _renderer is None:
        _renderer = PygameTurtleRenderer()
    return _renderer

def render_turtle_pygame(turtle, size: int = 120) -> pygame.Surface:
    """Convenience function to render a turtle using existing PIL renderer"""
    renderer = get_pygame_renderer()
    return renderer.render_turtle(turtle, size)
