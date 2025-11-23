"""
SVG to PyGame Renderer using Wand (ImageMagick) for TurboShells
Alternative renderer that uses ImageMagick instead of cairosvg
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
    from wand.image import Image as WandImage
    from wand.api import library
    import ctypes
    WAND_AVAILABLE = True
except ImportError:
    WAND_AVAILABLE = False


class WandSVGToPyGameRenderer:
    """
    SVG to PyGame surface conversion using Wand (ImageMagick)
    Provides high-quality SVG rendering without requiring cairo
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
        self.wand_available = WAND_AVAILABLE
        
        if not self.wand_available:
            print("Warning: Wand (ImageMagick) not available. SVG rendering will be limited.")
        else:
            # Configure ImageMagick settings
            try:
                # Set up ImageMagick to handle SVG properly
                library.MagickSetResourceLimit(library.ResourceType.MEMORY_RESOURCE, 256*1024*1024)  # 256MB
                library.MagickSetResourceLimit(library.ResourceType.DISK_RESOURCE, 1024*1024*1024)  # 1GB
            except:
                pass  # Resource limit setting is optional
    
    def render_svg_string_to_surface(self, svg_string: str, size: Optional[int] = None) -> Optional[pygame.Surface]:
        """
        Render SVG string directly to PyGame surface using Wand
        """
        if not svg_string or not self.wand_available:
            return self.create_enhanced_fallback_surface(size or 200)
            
        # Check cache first
        cache_key = f"string_{hash(svg_string)}_{size}"
        if cache_key in self.cache:
            self.cache_hits += 1
            return self.cache[cache_key]
        
        self.cache_misses += 1
        
        try:
            # Create Wand Image from SVG string
            with WandImage(blob=svg_string.encode('utf-8')) as wand_img:
                # Set resolution for better quality
                wand_img.resolution = (150, 150)
                
                # Resize if size specified
                if size is not None:
                    # Calculate scale to fit within size while maintaining aspect ratio
                    orig_width, orig_height = wand_img.width, wand_img.height
                    if orig_width > size or orig_height > size:
                        scale = min(size / orig_width, size / orig_height)
                        new_width = int(orig_width * scale)
                        new_height = int(orig_height * scale)
                        wand_img.resize(new_width, new_height)
                
                # Convert to PIL Image
                pil_image = self.wand_to_pil(wand_img)
                
                if pil_image:
                    # Convert PIL to PyGame surface
                    surface = self.pil_to_pygame(pil_image)
                    
                    if surface:
                        # Cache the result
                        self.cache_surface(cache_key, surface)
                        return surface
            
        except Exception as e:
            print(f"Error converting SVG to PyGame surface: {e}")
            return self.create_enhanced_fallback_surface(size or 200)
        
        return self.create_enhanced_fallback_surface(size or 200)
    
    def render_svg_drawing_to_surface(self, svg_drawing: object, size: Optional[int] = None) -> Optional[pygame.Surface]:
        """
        Render drawsvg Drawing object to PyGame surface
        """
        if svg_drawing is None:
            return self.create_enhanced_fallback_surface(size or 200)
            
        # Convert drawing to SVG string
        svg_string = svg_drawing.as_svg()
        return self.render_svg_string_to_surface(svg_string, size)
    
    def wand_to_pil(self, wand_img: WandImage) -> Optional[Image.Image]:
        """
        Convert Wand Image to PIL Image
        """
        try:
            # Convert Wand to bytes
            img_bytes = wand_img.make_blob('png')
            
            # Create PIL Image from bytes
            pil_image = Image.open(io.BytesIO(img_bytes))
            return pil_image
            
        except Exception as e:
            print(f"Error converting Wand to PIL: {e}")
            return None
    
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
            'wand_available': self.wand_available,
            'pygame_available': pygame is not None,
            'can_render_svg': self.wand_available and self.pil_available and pygame is not None,
            'cache_enabled': True,
            'max_cache_size': self.max_cache_size,
            'renderer_type': 'wand'
        }


# Global renderer instance
_renderer_instance = None


def get_svg_renderer() -> WandSVGToPyGameRenderer:
    """
    Get global SVG renderer instance
    """
    global _renderer_instance
    if _renderer_instance is None:
        _renderer_instance = WandSVGToPyGameRenderer()
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
