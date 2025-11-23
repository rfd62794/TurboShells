"""
Hybrid SVG to PyGame Renderer for TurboShells
Tries multiple rendering approaches and uses the best available one
"""

import os
import tempfile
import io
import subprocess
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
    import cairosvg
    CAIROSVG_AVAILABLE = True
except (ImportError, OSError):
    CAIROSVG_AVAILABLE = False

try:
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
    SVGLIB_AVAILABLE = True
except (ImportError, OSError):
    SVGLIB_AVAILABLE = False

try:
    from wand.image import Image as WandImage
    WAND_AVAILABLE = True
except (ImportError, OSError):
    WAND_AVAILABLE = False

try:
    import svg2png
    SVG2PNG_AVAILABLE = True
except ImportError:
    SVG2PNG_AVAILABLE = False


class HybridSVGToPyGameRenderer:
    """
    Hybrid SVG to PyGame surface conversion that tries multiple approaches
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
        self.cairosvg_available = CAIROSVG_AVAILABLE
        self.svglib_available = SVGLIB_AVAILABLE
        self.wand_available = WAND_AVAILABLE
        self.svg2png_available = SVG2PNG_AVAILABLE
        
        # Determine best available renderer
        self.available_renderers = []
        if self.cairosvg_available:
            self.available_renderers.append('cairosvg')
        if self.svg2png_available:
            self.available_renderers.append('svg2png')
        if self.wand_available:
            self.available_renderers.append('wand')
        if self.svglib_available:
            self.available_renderers.append('svglib')
        
        self.primary_renderer = self.available_renderers[0] if self.available_renderers else 'fallback'
        
        print(f"SVG Renderer: Using {self.primary_renderer} (available: {', '.join(self.available_renderers) or 'none'})")
    
    def render_svg_string_to_surface(self, svg_string: str, size: Optional[int] = None) -> Optional[pygame.Surface]:
        """
        Render SVG string directly to PyGame surface using best available method
        """
        if not svg_string:
            return self.create_enhanced_fallback_surface(size or 200)
            
        # Check cache first
        cache_key = f"string_{hash(svg_string)}_{size}"
        if cache_key in self.cache:
            self.cache_hits += 1
            return self.cache[cache_key]
        
        self.cache_misses += 1
        
        # Try each available renderer in order
        for renderer_name in self.available_renderers:
            try:
                if renderer_name == 'cairosvg':
                    surface = self.render_with_cairosvg(svg_string, size)
                elif renderer_name == 'svg2png':
                    surface = self.render_with_svg2png(svg_string, size)
                elif renderer_name == 'wand':
                    surface = self.render_with_wand(svg_string, size)
                elif renderer_name == 'svglib':
                    surface = self.render_with_svglib(svg_string, size)
                else:
                    continue
                
                if surface:
                    # Cache the result
                    self.cache_surface(cache_key, surface)
                    return surface
                    
            except Exception as e:
                print(f"Renderer {renderer_name} failed: {e}")
                continue
        
        # All renderers failed, use fallback
        return self.create_enhanced_fallback_surface(size or 200)
    
    def render_with_cairosvg(self, svg_string: str, size: Optional[int] = None) -> Optional[pygame.Surface]:
        """Render using cairosvg"""
        if not self.cairosvg_available or not self.pil_available:
            return None
            
        try:
            # Convert SVG to PNG using cairosvg
            png_data = cairosvg.svg2png(svg_string, output_width=size, output_height=size)
            
            # Convert PNG to PIL Image
            pil_image = Image.open(io.BytesIO(png_data))
            
            # Convert PIL to PyGame
            return self.pil_to_pygame(pil_image)
            
        except Exception as e:
            print(f"CairoSVG rendering failed: {e}")
            return None
    
    def render_with_svg2png(self, svg_string: str, size: Optional[int] = None) -> Optional[pygame.Surface]:
        """Render using svg2png"""
        if not self.svg2png_available:
            return None
            
        try:
            # Save SVG to temp file
            temp_svg = os.path.join(self.temp_dir, f"temp_{id(svg_string)}.svg")
            with open(temp_svg, 'w', encoding='utf-8') as f:
                f.write(svg_string)
            
            # Convert to PNG
            temp_png = os.path.join(self.temp_dir, f"temp_{id(svg_string)}.png")
            svg2png.svg2png(url=temp_svg, write_to=temp_png, output_width=size, output_height=size)
            
            # Load with pygame
            if os.path.exists(temp_png):
                surface = pygame.image.load(temp_png)
                os.unlink(temp_png)
                os.unlink(temp_svg)
                return surface
            
            # Cleanup
            if os.path.exists(temp_svg):
                os.unlink(temp_svg)
            if os.path.exists(temp_png):
                os.unlink(temp_png)
                
            return None
            
        except Exception as e:
            print(f"svg2png rendering failed: {e}")
            return None
    
    def render_with_wand(self, svg_string: str, size: Optional[int] = None) -> Optional[pygame.Surface]:
        """Render using wand"""
        if not self.wand_available or not self.pil_available:
            return None
            
        try:
            with WandImage(blob=svg_string.encode('utf-8')) as wand_img:
                wand_img.resolution = (150, 150)
                
                if size is not None:
                    orig_width, orig_height = wand_img.width, wand_img.height
                    if orig_width > size or orig_height > size:
                        scale = min(size / orig_width, size / orig_height)
                        new_width = int(orig_width * scale)
                        new_height = int(orig_height * scale)
                        wand_img.resize(new_width, new_height)
                
                pil_image = self.wand_to_pil(wand_img)
                if pil_image:
                    return self.pil_to_pygame(pil_image)
                    
        except Exception as e:
            print(f"Wand rendering failed: {e}")
            return None
    
    def render_with_svglib(self, svg_string: str, size: Optional[int] = None) -> Optional[pygame.Surface]:
        """Render using svglib"""
        if not self.svglib_available or not self.pil_available:
            return None
            
        try:
            drawing = svg2rlg(io.StringIO(svg_string))
            if drawing is None:
                return None
            
            orig_width, orig_height = drawing.width, drawing.height
            
            if size is None:
                output_width = int(orig_width)
                output_height = int(orig_height)
            else:
                scale = min(size / orig_width, size / orig_height)
                output_width = int(orig_width * scale)
                output_height = int(orig_height * scale)
            
            pil_image = renderPM.drawToPIL(drawing, dpi=72, 
                                          width=output_width, height=output_height)
            
            if pil_image:
                return self.pil_to_pygame(pil_image)
                
        except Exception as e:
            print(f"svglib rendering failed: {e}")
            return None
    
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
        """Convert Wand Image to PIL Image"""
        try:
            img_bytes = wand_img.make_blob('png')
            pil_image = Image.open(io.BytesIO(img_bytes))
            return pil_image
        except Exception as e:
            print(f"Error converting Wand to PIL: {e}")
            return None
    
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
            'cairosvg_available': self.cairosvg_available,
            'svglib_available': self.svglib_available,
            'wand_available': self.wand_available,
            'svg2png_available': self.svg2png_available,
            'available_renderers': self.available_renderers,
            'primary_renderer': self.primary_renderer,
            'pygame_available': pygame is not None,
            'can_render_svg': len(self.available_renderers) > 0,
            'cache_enabled': True,
            'max_cache_size': self.max_cache_size,
            'renderer_type': 'hybrid'
        }


# Global renderer instance
_renderer_instance = None


def get_svg_renderer() -> HybridSVGToPyGameRenderer:
    """
    Get global SVG renderer instance
    """
    global _renderer_instance
    if _renderer_instance is None:
        _renderer_instance = HybridSVGToPyGameRenderer()
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
