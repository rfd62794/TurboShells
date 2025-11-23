"""
Fixed Tkinter SVG Renderer for TurboShells
Uses PIL drawing with proper Tkinter PhotoImage creation
"""

import os
import tempfile
from typing import Optional, Dict, Any, Tuple
import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageDraw, ImageTk

try:
    import drawsvg as draw
except ImportError:
    draw = None


class FixedTkinterSVGRenderer:
    """
    Fixed SVG renderer for Tkinter canvas using PIL drawing
    """
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.cache = {}
        self.max_cache_size = 100
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Check dependencies
        self.drawsvg_available = draw is not None
        
        print(f"Fixed Tkinter SVG Renderer: Using PIL drawing (drawsvg available: {self.drawsvg_available})")
    
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
        
        # Parse SVG and create PIL drawing
        photo_image = self.create_svg_pil_drawing(svg_string, size)
        
        if photo_image:
            # Cache the result
            self.cache_image(cache_key, photo_image)
            return photo_image
        
        # Fallback to generic turtle
        return self.create_fallback_photoimage(size or 200)
    
    def create_svg_pil_drawing(self, svg_string: str, size: Optional[int] = None) -> Optional[ImageTk.PhotoImage]:
        """
        Parse SVG and create PIL drawing
        """
        try:
            # Parse SVG elements
            elements = self.parse_svg_elements(svg_string)
            
            if not elements:
                return None
            
            # Create PIL image
            img_size = size or 200
            pil_image = Image.new('RGBA', (img_size, img_size), (240, 248, 255, 255))
            draw = ImageDraw.Draw(pil_image)
            
            # Scale factor
            scale = img_size / 200.0
            
            # Draw elements
            for element in elements:
                self.draw_svg_element(draw, element, scale)
            
            # Convert to PhotoImage (requires root window)
            try:
                photo_image = ImageTk.PhotoImage(pil_image)
                return photo_image
            except RuntimeError as e:
                if "no default root window" in str(e):
                    # Save to file and return path
                    temp_file = os.path.join(self.temp_dir, f"svg_{id(svg_string)}.png")
                    pil_image.save(temp_file)
                    return temp_file
                else:
                    raise e
                    
        except Exception as e:
            print(f"Error creating SVG PIL drawing: {e}")
            return None
    
    def parse_svg_elements(self, svg_string: str) -> list:
        """
        Parse SVG string into elements
        """
        import re
        
        elements = []
        
        # Parse circles
        circles = re.findall(r'<circle[^>]*cx="([^"]*)"[^>]*cy="([^"]*)"[^>]*r="([^"]*)"[^>]*fill="([^"]*)"[^>]*', svg_string)
        for cx, cy, r, fill in circles:
            elements.append({
                'type': 'circle',
                'cx': float(cx),
                'cy': float(cy),
                'r': float(r),
                'fill': fill
            })
        
        # Parse ellipses
        ellipses = re.findall(r'<ellipse[^>]*cx="([^"]*)"[^>]*cy="([^"]*)"[^>]*rx="([^"]*)"[^>]*ry="([^"]*)"[^>]*fill="([^"]*)"[^>]*', svg_string)
        for cx, cy, rx, ry, fill in ellipses:
            elements.append({
                'type': 'ellipse',
                'cx': float(cx),
                'cy': float(cy),
                'rx': float(rx),
                'ry': float(ry),
                'fill': fill
            })
        
        # Parse paths (simplified - just draw as lines)
        paths = re.findall(r'<path[^>]*d="([^"]*)"[^>]*fill="([^"]*)"[^>]*', svg_string)
        for d, fill in paths:
            elements.append({
                'type': 'path',
                'd': d,
                'fill': fill
            })
        
        return elements
    
    def draw_svg_element(self, draw, element: dict, scale: float):
        """
        Draw a single SVG element on PIL image
        """
        if element['type'] == 'circle':
            cx = int(element['cx'] * scale)
            cy = int(element['cy'] * scale)
            r = int(element['r'] * scale)
            color = self.parse_color(element['fill'])
            
            bbox = [cx - r, cy - r, cx + r, cy + r]
            draw.ellipse(bbox, fill=color, outline=color)
        
        elif element['type'] == 'ellipse':
            cx = int(element['cx'] * scale)
            cy = int(element['cy'] * scale)
            rx = int(element['rx'] * scale)
            ry = int(element['ry'] * scale)
            color = self.parse_color(element['fill'])
            
            bbox = [cx - rx, cy - ry, cx + rx, cy + ry]
            draw.ellipse(bbox, fill=color, outline=color)
        
        elif element['type'] == 'path':
            # Simplified path drawing - just draw as colored background
            color = self.parse_color(element['fill'])
            # For paths, we'll draw a simple rectangle as placeholder
            draw.rectangle([50, 50, 150, 150], fill=color)
    
    def parse_color(self, color_str: str) -> Tuple[int, int, int]:
        """
        Parse color string to RGB tuple
        """
        if color_str.startswith('#'):
            # Remove # and convert hex to RGB
            hex_color = color_str[1:]
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                return (r, g, b)
        elif color_str == 'none':
            return (240, 248, 255)  # Alice blue
        
        # Default color
        return (128, 128, 128)
    
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
        Create a fallback PhotoImage with a colorful turtle
        """
        # Create PIL image with turtle drawing
        pil_image = Image.new('RGBA', (size, size), (240, 248, 255, 255))
        
        # Draw turtle using PIL
        draw = ImageDraw.Draw(pil_image)
        
        center_x = size // 2
        center_y = size // 2
        scale = size / 200.0
        
        # Shell - bright green
        shell_width = int(80 * scale)
        shell_height = int(60 * scale)
        shell_bbox = [
            center_x - shell_width//2, center_y - shell_height//2,
            center_x + shell_width//2, center_y + shell_height//2
        ]
        draw.ellipse(shell_bbox, fill=(34, 139, 34), outline=(0, 100, 0), width=2)
        
        # Head - brown
        head_radius = int(20 * scale)
        head_bbox = [
            center_x - head_radius, center_y - int(40 * scale) - head_radius,
            center_x + head_radius, center_y - int(40 * scale) + head_radius
        ]
        draw.ellipse(head_bbox, fill=(139, 90, 43), outline=(100, 60, 20), width=2)
        
        # Eyes - black
        eye_size = max(2, int(3 * scale))
        draw.ellipse([
            center_x - int(8 * scale) - eye_size, center_y - int(40 * scale) - eye_size,
            center_x - int(8 * scale) + eye_size, center_y - int(40 * scale) + eye_size
        ], fill=(0, 0, 0))
        draw.ellipse([
            center_x + int(8 * scale) - eye_size, center_y - int(40 * scale) - eye_size,
            center_x + int(8 * scale) + eye_size, center_y - int(40 * scale) + eye_size
        ], fill=(0, 0, 0))
        
        # Legs - brown
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
            ], fill=(101, 67, 33), outline=(60, 40, 20))
        
        # Add some pattern to the shell
        pattern_size = int(10 * scale)
        for i in range(3):
            for j in range(2):
                px = center_x - int(20 * scale) + i * int(20 * scale)
                py = center_y - int(10 * scale) + j * int(20 * scale)
                draw.ellipse([
                    px - pattern_size//2, py - pattern_size//2,
                    px + pattern_size//2, py + pattern_size//2
                ], fill=(0, 100, 0), outline=(0, 80, 0))
        
        # Convert to PhotoImage - handle Tkinter root window requirement
        try:
            photo_image = ImageTk.PhotoImage(pil_image)
            return photo_image
        except RuntimeError as e:
            if "no default root window" in str(e):
                # Save to temp file and load later
                temp_file = os.path.join(self.temp_dir, f"fallback_{id(self)}.png")
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
            'drawsvg_available': self.drawsvg_available,
            'tkinter_available': True,
            'can_render_svg': True,
            'cache_enabled': True,
            'max_cache_size': self.max_cache_size,
            'renderer_type': 'tkinter_fixed',
            'svg_parsing': True,
            'pil_drawing': True
        }


# Global renderer instance
_renderer_instance = None


def get_svg_renderer() -> FixedTkinterSVGRenderer:
    """
    Get global SVG renderer instance
    """
    global _renderer_instance
    if _renderer_instance is None:
        _renderer_instance = FixedTkinterSVGRenderer()
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
