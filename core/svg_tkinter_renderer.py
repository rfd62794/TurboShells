"""
Tkinter SVG Renderer for TurboShells
Renders SVG directly in Tkinter canvas using PIL
"""

import os
import tempfile
import io
from typing import Optional, Dict, Any, Tuple
import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk

try:
    import drawsvg as draw
except ImportError:
    draw = None

try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except (ImportError, OSError):
    CAIROSVG_AVAILABLE = False

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


class TkinterSVGRenderer:
    """
    SVG renderer for Tkinter canvas using multiple conversion methods
    """
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.cache = {}
        self.max_cache_size = 100
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Check dependencies
        self.drawsvg_available = draw is not None
        self.cairosvg_available = CAIROSVG_AVAILABLE
        self.wand_available = WAND_AVAILABLE
        self.svg2png_available = SVG2PNG_AVAILABLE
        
        # Determine best available converter
        self.available_converters = []
        if self.cairosvg_available:
            self.available_converters.append('cairosvg')
        if self.wand_available:
            self.available_converters.append('wand')
        if self.svg2png_available:
            self.available_converters.append('svg2png')
        
        self.primary_converter = self.available_converters[0] if self.available_converters else 'fallback'
        
        print(f"Tkinter SVG Renderer: Using {self.primary_converter} (available: {', '.join(self.available_converters) or 'none'})")
    
    def svg_to_photoimage(self, svg_string: str, size: Optional[int] = None) -> Optional[ImageTk.PhotoImage]:
        """
        Convert SVG string to PhotoImage for Tkinter
        """
        if not svg_string:
            return None
            
        # Check cache first
        cache_key = f"string_{hash(svg_string)}_{size}"
        if cache_key in self.cache:
            self.cache_hits += 1
            return self.cache[cache_key]
        
        self.cache_misses += 1
        
        # Try each available converter
        for converter_name in self.available_converters:
            try:
                if converter_name == 'cairosvg':
                    photo_image = self.convert_with_cairosvg(svg_string, size)
                elif converter_name == 'wand':
                    photo_image = self.convert_with_wand(svg_string, size)
                elif converter_name == 'svg2png':
                    photo_image = self.convert_with_svg2png(svg_string, size)
                else:
                    continue
                
                if photo_image:
                    # Cache the result
                    self.cache_image(cache_key, photo_image)
                    return photo_image
                    
            except Exception as e:
                print(f"Converter {converter_name} failed: {e}")
                continue
        
        # All converters failed, create fallback
        return self.create_fallback_photoimage(size or 200)
    
    def convert_with_cairosvg(self, svg_string: str, size: Optional[int] = None) -> Optional[ImageTk.PhotoImage]:
        """Convert using cairosvg"""
        try:
            # Convert SVG to PNG
            png_data = cairosvg.svg2png(svg_string, output_width=size, output_height=size)
            
            # Create PIL Image
            pil_image = Image.open(io.BytesIO(png_data))
            
            # Convert to PhotoImage
            photo_image = ImageTk.PhotoImage(pil_image)
            return photo_image
            
        except Exception as e:
            print(f"CairoSVG conversion failed: {e}")
            return None
    
    def convert_with_wand(self, svg_string: str, size: Optional[int] = None) -> Optional[ImageTk.PhotoImage]:
        """Convert using wand"""
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
                
                # Convert to PIL
                img_bytes = wand_img.make_blob('png')
                pil_image = Image.open(io.BytesIO(img_bytes))
                
                # Convert to PhotoImage
                photo_image = ImageTk.PhotoImage(pil_image)
                return photo_image
                
        except Exception as e:
            print(f"Wand conversion failed: {e}")
            return None
    
    def convert_with_svg2png(self, svg_string: str, size: Optional[int] = None) -> Optional[ImageTk.PhotoImage]:
        """Convert using svg2png"""
        try:
            # Save SVG to temp file
            temp_svg = os.path.join(self.temp_dir, f"temp_{id(svg_string)}.svg")
            with open(temp_svg, 'w', encoding='utf-8') as f:
                f.write(svg_string)
            
            # Convert to PNG
            temp_png = os.path.join(self.temp_dir, f"temp_{id(svg_string)}.png")
            svg2png.svg2png(inputfile=temp_svg, outputfile=temp_png)
            
            # Load with PIL
            if os.path.exists(temp_png):
                pil_image = Image.open(temp_png)
                photo_image = ImageTk.PhotoImage(pil_image)
                
                # Cleanup
                os.unlink(temp_png)
                os.unlink(temp_svg)
                
                return photo_image
            
            # Cleanup
            if os.path.exists(temp_svg):
                os.unlink(temp_svg)
            if os.path.exists(temp_png):
                os.unlink(temp_png)
                
            return None
            
        except Exception as e:
            print(f"svg2png conversion failed: {e}")
            return None
    
    def svg_drawing_to_photoimage(self, svg_drawing: object, size: Optional[int] = None) -> Optional[ImageTk.PhotoImage]:
        """
        Convert drawsvg Drawing object to PhotoImage
        """
        if svg_drawing is None:
            return self.create_fallback_photoimage(size or 200)
            
        # Convert drawing to SVG string
        svg_string = svg_drawing.as_svg()
        return self.svg_to_photoimage(svg_string, size)
    
    def render_turtle_to_photoimage(self, visual_genetics: Dict[str, Any], 
                                  size: Optional[int] = None) -> Optional[ImageTk.PhotoImage]:
        """
        Render turtle from genetics to PhotoImage
        """
        from .turtle_svg_generator import TurtleSVGGenerator
        
        if not self.drawsvg_available:
            print("Error: drawsvg not available for turtle generation")
            return self.create_fallback_photoimage(size or 100)
        
        # Generate turtle SVG
        generator = TurtleSVGGenerator()
        svg_drawing = generator.generate_turtle_svg(visual_genetics, size)
        
        if svg_drawing is None:
            return self.create_fallback_photoimage(size or 100)
        
        # Convert to PhotoImage
        return self.svg_drawing_to_photoimage(svg_drawing, size)
    
    def create_fallback_photoimage(self, size: int, text: str = "Turtle") -> ImageTk.PhotoImage:
        """
        Create a fallback PhotoImage when SVG conversion fails
        """
        # Create PIL image with turtle drawing
        pil_image = Image.new('RGBA', (size, size), (240, 248, 255, 255))
        
        # Draw turtle using PIL
        from PIL import ImageDraw
        draw = ImageDraw.Draw(pil_image)
        
        center_x = size // 2
        center_y = size // 2
        scale = size / 200.0
        
        # Shell
        shell_width = int(80 * scale)
        shell_height = int(60 * scale)
        shell_bbox = [
            center_x - shell_width//2, center_y - shell_height//2,
            center_x + shell_width//2, center_y + shell_height//2
        ]
        draw.ellipse(shell_bbox, fill=(34, 139, 34), outline=(0, 100, 0))
        
        # Head
        head_radius = int(20 * scale)
        head_bbox = [
            center_x - head_radius, center_y - int(40 * scale) - head_radius,
            center_x + head_radius, center_y - int(40 * scale) + head_radius
        ]
        draw.ellipse(head_bbox, fill=(139, 90, 43), outline=(100, 60, 20))
        
        # Eyes
        eye_size = max(2, int(3 * scale))
        draw.ellipse([
            center_x - int(8 * scale) - eye_size, center_y - int(40 * scale) - eye_size,
            center_x - int(8 * scale) + eye_size, center_y - int(40 * scale) + eye_size
        ], fill=(0, 0, 0))
        draw.ellipse([
            center_x + int(8 * scale) - eye_size, center_y - int(40 * scale) - eye_size,
            center_x + int(8 * scale) + eye_size, center_y - int(40 * scale) + eye_size
        ], fill=(0, 0, 0))
        
        # Legs
        leg_width = int(8 * scale)
        leg_length = int(30 * scale)
        leg_positions = [
            (center_x - int(60 * scale), center_y + int(20 * scale)),
            (center_x + int(60 * scale), center_y + int(20 * scale)),
            (center_x - int(40 * scale), center_y + int(40 * scale)),
            (center_x + int(40 * scale), center_y + int(40 * scale))
        ]
        
        for leg_x, leg_y in leg_positions:
            draw.rectangle([
                leg_x - leg_width//2, leg_y,
                leg_x + leg_width//2, leg_y + leg_length
            ], fill=(101, 67, 33))
        
        # Convert to PhotoImage
        photo_image = ImageTk.PhotoImage(pil_image)
        return photo_image
    
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
            'drawsvg_available': self.drawsvg_available,
            'cairosvg_available': self.cairosvg_available,
            'wand_available': self.wand_available,
            'svg2png_available': self.svg2png_available,
            'available_converters': self.available_converters,
            'primary_converter': self.primary_converter,
            'tkinter_available': True,
            'can_render_svg': len(self.available_converters) > 0,
            'cache_enabled': True,
            'max_cache_size': self.max_cache_size,
            'renderer_type': 'tkinter'
        }


# Global renderer instance
_renderer_instance = None


def get_svg_renderer() -> TkinterSVGRenderer:
    """
    Get global SVG renderer instance
    """
    global _renderer_instance
    if _renderer_instance is None:
        _renderer_instance = TkinterSVGRenderer()
    return _renderer_instance


# Utility functions
def render_turtle_to_photoimage(visual_genetics: Dict[str, Any], 
                              size: Optional[int] = None) -> Optional[ImageTk.PhotoImage]:
    """
    Render turtle from genetics to PhotoImage using global renderer
    """
    renderer = get_svg_renderer()
    return renderer.render_turtle_to_photoimage(visual_genetics, size)


def render_svg_to_photoimage(svg_string: str, 
                            size: Optional[int] = None) -> Optional[ImageTk.PhotoImage]:
    """
    Render SVG string to PhotoImage using global renderer
    """
    renderer = get_svg_renderer()
    return renderer.svg_to_photoimage(svg_string, size)


def create_turtle_placeholder_photoimage(size: int, text: str = "Turtle") -> ImageTk.PhotoImage:
    """
    Create turtle placeholder PhotoImage using global renderer
    """
    renderer = get_svg_renderer()
    return renderer.create_fallback_photoimage(size, text)


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
