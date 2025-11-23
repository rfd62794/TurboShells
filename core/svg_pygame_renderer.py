"""
SVG to PyGame Renderer for TurboShells
Complete SVG to PyGame surface conversion system with caching
"""

import os
import tempfile
import io
from typing import Optional, Dict, Any, Tuple
from PIL import Image
import pygame

try:
    import cairosvg
except ImportError:
    cairosvg = None

try:
    import drawsvg as draw
except ImportError:
    draw = None


class SVGToPyGameRenderer:
    """
    Complete SVG to PyGame surface conversion system
    Handles SVG rendering, caching, and PyGame integration
    """
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.cache = {}
        self.max_cache_size = 100
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Check dependencies
        self.cairo_available = cairosvg is not None
        self.drawsvg_available = draw is not None
        
        if not self.cairo_available:
            print("Warning: cairosvg not available. SVG rendering will be limited.")
    
    def render_svg_string_to_surface(self, svg_string: str, size: Optional[int] = None) -> Optional[pygame.Surface]:
        """
        Render SVG string directly to PyGame surface
        """
        if not svg_string:
            return None
            
        # Check cache first
        cache_key = f"string_{hash(svg_string)}_{size}"
        if cache_key in self.cache:
            self.cache_hits += 1
            return self.cache[cache_key]
        
        self.cache_misses += 1
        
        # Convert SVG to PNG using cairosvg
        png_data = self.svg_to_png_data(svg_string, size)
        if png_data is None:
            return None
        
        # Convert PNG data to PyGame surface
        try:
            # Create PIL Image from PNG data
            pil_image = Image.open(io.BytesIO(png_data))
            
            # Convert to PyGame surface
            pygame_surface = pygame.image.fromstring(
                pil_image.tobytes(),
                pil_image.size,
                pil_image.mode
            )
            
            # Cache the result
            self.cache_surface(cache_key, pygame_surface)
            
            return pygame_surface
            
        except Exception as e:
            print(f"Error converting PNG to PyGame surface: {e}")
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
    
    def svg_to_png_data(self, svg_string: str, size: Optional[int] = None) -> Optional[bytes]:
        """
        Convert SVG string to PNG data bytes
        """
        if not self.cairo_available:
            print("Error: cairosvg not available for SVG to PNG conversion")
            return None
        
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
            
            # Convert SVG to PNG
            png_data = cairosvg.svg2png(
                bytestring=svg_string.encode('utf-8'),
                output_width=output_width,
                output_height=output_height
            )
            
            return png_data
            
        except Exception as e:
            print(f"Error converting SVG to PNG: {e}")
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
            return None
        
        # Generate turtle SVG
        generator = TurtleSVGGenerator()
        svg_drawing = generator.generate_turtle_svg(visual_genetics, size)
        
        if svg_drawing is None:
            return None
        
        # Render to PyGame surface
        return self.render_svg_drawing_to_surface(svg_drawing, size)
    
    def create_placeholder_surface(self, size: int, text: str = "Turtle") -> pygame.Surface:
        """
        Create a placeholder surface when SVG rendering fails
        """
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        surface.fill((240, 240, 240))  # Light gray background
        
        # Draw text
        font = pygame.font.Font(None, size // 4)
        text_surface = font.render(text, True, (100, 100, 100))
        text_rect = text_surface.get_rect(center=(size // 2, size // 2))
        surface.blit(text_surface, text_rect)
        
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
    
    def optimize_cache_size(self, target_memory_mb: int = 50) -> None:
        """
        Optimize cache size based on memory usage
        """
        # Estimate average surface size (rough approximation)
        avg_surface_size = 100 * 100 * 4  # 100x100 RGBA surface
        max_surfaces = (target_memory_mb * 1024 * 1024) // avg_surface_size
        
        self.max_cache_size = max(10, min(500, int(max_surfaces)))
        
        # Trim cache if necessary
        while len(self.cache) > self.max_cache_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
    
    def render_batch_turtles(self, genetics_list: list, size: Optional[int] = None) -> list:
        """
        Render multiple turtles efficiently
        """
        surfaces = []
        
        for genetics in genetics_list:
            surface = self.render_turtle_to_surface(genetics, size)
            if surface is None:
                surface = self.create_placeholder_surface(size or 100)
            surfaces.append(surface)
        
        return surfaces
    
    def create_turtle_sprite_sheet(self, genetics_list: list, 
                                 sprite_size: int = 64) -> Optional[pygame.Surface]:
        """
        Create a sprite sheet from multiple turtle genetics
        """
        if not genetics_list:
            return None
        
        # Calculate sprite sheet dimensions
        sprites_per_row = min(8, len(genetics_list))
        rows = (len(genetics_list) + sprites_per_row - 1) // sprites_per_row
        
        sheet_width = sprites_per_row * sprite_size
        sheet_height = rows * sprite_size
        
        # Create sprite sheet surface
        sprite_sheet = pygame.Surface((sheet_width, sheet_height), pygame.SRCALPHA)
        sprite_sheet.fill((0, 0, 0, 0))  # Transparent background
        
        # Render each turtle to sprite sheet
        for i, genetics in enumerate(genetics_list):
            row = i // sprites_per_row
            col = i % sprites_per_row
            
            x = col * sprite_size
            y = row * sprite_size
            
            # Render turtle
            turtle_surface = self.render_turtle_to_surface(genetics, sprite_size)
            if turtle_surface is None:
                turtle_surface = self.create_placeholder_surface(sprite_size)
            
            # Center turtle in sprite cell
            turtle_rect = turtle_surface.get_rect(center=(x + sprite_size // 2, y + sprite_size // 2))
            sprite_sheet.blit(turtle_surface, turtle_rect)
        
        return sprite_sheet
    
    def validate_svg_string(self, svg_string: str) -> Dict[str, bool]:
        """
        Validate SVG string format
        """
        validation = {
            'is_string': isinstance(svg_string, str),
            'has_svg_tag': '<svg' in svg_string and '</svg>' in svg_string,
            'has_xml_declaration': svg_string.strip().startswith('<?xml') or '<svg' in svg_string,
            'not_empty': len(svg_string.strip()) > 0
        }
        
        validation['overall'] = all(validation.values())
        return validation
    
    def get_rendering_capabilities(self) -> Dict[str, Any]:
        """
        Get information about rendering capabilities
        """
        return {
            'cairosvg_available': self.cairo_available,
            'drawsvg_available': self.drawsvg_available,
            'pygame_available': pygame is not None,
            'pil_available': Image is not None,
            'can_render_svg': self.cairo_available and pygame is not None,
            'cache_enabled': True,
            'max_cache_size': self.max_cache_size
        }
    
    def prewarm_cache(self, genetics_list: list, size: Optional[int] = None) -> None:
        """
        Prewarm cache with common turtle variations
        """
        for genetics in genetics_list:
            self.render_turtle_to_surface(genetics, size)
    
    def export_surface_to_file(self, surface: pygame.Surface, 
                              filename: str, file_format: str = 'PNG') -> bool:
        """
        Export PyGame surface to file
        """
        try:
            # Convert PyGame surface to PIL Image
            pil_image = Image.frombytes(
                'RGBA',
                surface.get_size(),
                pygame.image.tostring(surface, 'RGBA', False)
            )
            
            # Save to file
            pil_image.save(filename, file_format)
            return True
            
        except Exception as e:
            print(f"Error exporting surface to file: {e}")
            return False
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """
        Estimate memory usage of cached surfaces
        """
        total_pixels = 0
        for surface in self.cache.values():
            width, height = surface.get_size()
            total_pixels += width * height
        
        # Estimate memory usage (4 bytes per pixel for RGBA)
        estimated_bytes = total_pixels * 4
        estimated_mb = estimated_bytes / (1024 * 1024)
        
        return {
            'cached_surfaces': len(self.cache),
            'total_pixels': total_pixels,
            'estimated_bytes': estimated_bytes,
            'estimated_mb': estimated_mb,
            'cache_limit_mb': (self.max_cache_size * 100 * 100 * 4) / (1024 * 1024)
        }


# Global renderer instance
_renderer_instance = None


def get_svg_renderer() -> SVGToPyGameRenderer:
    """
    Get global SVG renderer instance
    """
    global _renderer_instance
    if _renderer_instance is None:
        _renderer_instance = SVGToPyGameRenderer()
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
