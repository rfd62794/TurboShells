"""
Direct Turtle Renderer for TurboShells
Draws stylized, textured turtles directly using PIL without SVG parsing
"""

import os
import tempfile
import random
import math
from typing import Optional, Dict, Any, Tuple, List
from PIL import Image, ImageDraw, ImageTk


class DirectTurtleRenderer:
    """
    Advanced Procedural Renderer: Draws stylized, textured turtles 
    using PIL primitives with pseudo-3D shading and genetic variation.
    """
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.cache = {}
        self.max_cache_size = 100
        self.cache_hits = 0
        self.cache_misses = 0
        print("Direct Turtle Renderer: Initialized Procedural Engine")
    
    # --- Color Utilities ---
    def rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex color"""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def get_variant_color(self, rgb: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
        """Adjust brightness safely"""
        return tuple(max(0, min(255, int(c * factor))) for c in rgb)

    def generate_noise_color(self, base_rgb: Tuple[int, int, int], variance: int = 20) -> Tuple[int, int, int]:
        """Adds slight randomness to color for organic texture"""
        r, g, b = base_rgb
        var = random.randint(-variance, variance)
        return (max(0, min(255, r + var)), 
                max(0, min(255, g + var)), 
                max(0, min(255, b + var)))

    # --- Drawing Primitives ---
    def draw_organic_scales(self, draw: ImageDraw.Draw, bbox: List[int], color: Tuple[int, int, int], density: float = 0.4):
        """Draws small random scales inside a bounding box area to simulate skin texture"""
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1
        num_scales = int((width * height) * 0.005 * density)
        
        scale_color = self.get_variant_color(color, 1.1) # Lighter scales
        
        for _ in range(num_scales):
            sx = random.randint(x1 + 2, x2 - 2)
            sy = random.randint(y1 + 2, y2 - 2)
            # Simple distance check to keep scales roughly inside an ellipse
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            if ((sx - cx) / (width/2))**2 + ((sy - cy) / (height/2))**2 <= 0.8:
                size = random.randint(1, 3)
                draw.ellipse([sx, sy, sx+size, sy+size], fill=scale_color)

    # --- Main Rendering Logic ---
    def draw_realistic_turtle(self, draw: ImageDraw.Draw, genetics: Dict[str, Any], size: int):
        center_x = size // 2
        center_y = size // 2
        scale = size / 200.0
        
        # Seed random generator with genetics hash
        gene_seed = hash(str(genetics)) 
        random.seed(gene_seed)

        # --- Extract Genes ---
        shell_base = genetics.get('shell_base_color', (34, 139, 34))
        skin_base = genetics.get('head_color', (46, 125, 50))
        pattern_color = genetics.get('pattern_color', self.get_variant_color(shell_base, 0.6))
        
        # Colors
        skin_shadow = self.get_variant_color(skin_base, 0.7)
        shell_shadow = self.get_variant_color(shell_base, 0.6)
        
        # --- 1. Drop Shadow ---
        shadow_y_offset = int(10 * scale)
        draw.ellipse([
            center_x - int(60 * scale), center_y - int(40 * scale) + shadow_y_offset,
            center_x + int(60 * scale), center_y + int(50 * scale) + shadow_y_offset
        ], fill=(0, 0, 0, 60))

        # --- 2. Limbs & Tail ---
        self._draw_limbs(draw, center_x, center_y, scale, skin_base, skin_shadow, genetics)
        self._draw_tail(draw, center_x, center_y, scale, skin_base, skin_shadow)
        
        # --- 3. Head ---
        self._draw_head(draw, center_x, center_y, scale, skin_base, skin_shadow, genetics)

        # --- 4. Shell Body ---
        shell_w = int(65 * scale) 
        shell_h = int(55 * scale)
        
        # Shell Rim 
        draw.ellipse([
            center_x - shell_w, center_y - shell_h,
            center_x + shell_w, center_y + shell_h
        ], fill=shell_shadow)

        # Main Shell Dome
        dome_offset = int(5 * scale)
        draw.ellipse([
            center_x - shell_w + 3, center_y - shell_h,
            center_x + shell_w - 3, center_y + shell_h - dome_offset
        ], fill=shell_base)

        # --- 5. Shell Scutes ---
        self._draw_shell_pattern(draw, center_x, center_y, shell_w, shell_h, scale, shell_base, pattern_color)

    def _draw_limbs(self, draw, cx, cy, scale, color, outline, genetics):
        """Draws textured flippers extended for visibility"""
        # Pushed coordinates outward (larger offsets)
        offsets = [
            # Front Right (Extended out to x+55)
            (45, -35, 85, -55, 75, -5),   
            # Front Left
            (-45, -35, -85, -55, -75, -5), 
            # Back Right
            (35, 35, 60, 55, 40, 65),     
            # Back Left
            (-35, 35, -60, 55, -40, 65)   
        ]

        for p1x, p1y, p2x, p2y, p3x, p3y in offsets:
            points = [
                (cx + int(p1x * scale), cy + int(p1y * scale)),
                (cx + int(p2x * scale), cy + int(p2y * scale)),
                (cx + int(p3x * scale), cy + int(p3y * scale))
            ]
            # Draw Limb
            draw.polygon(points, fill=color, outline=outline)
            
            # Draw Texture (Scales)
            min_x = min(p[0] for p in points)
            max_x = max(p[0] for p in points)
            min_y = min(p[1] for p in points)
            max_y = max(p[1] for p in points)
            self.draw_organic_scales(draw, [min_x, min_y, max_x, max_y], color)

    def _draw_tail(self, draw, cx, cy, scale, color, outline):
        tail_len = int(25 * scale)
        points = [
            (cx - int(5 * scale), cy + int(55 * scale)),
            (cx + int(5 * scale), cy + int(55 * scale)),
            (cx, cy + int(55 * scale) + tail_len)
        ]
        draw.polygon(points, fill=color, outline=outline)

    def _draw_head(self, draw, cx, cy, scale, color, outline, genetics):
        head_w = int(32 * scale)
        head_h = int(35 * scale)
        
        # Pushed head UP (more negative Y) so it clears the shell
        # Old was cy - 55 (hidden), New is cy - 75 (visible)
        head_y = cy - int(75 * scale) 
        
        # Neck connection (Thicker and longer)
        draw.rectangle([
            cx - int(12 * scale), head_y + int(15 * scale),
            cx + int(12 * scale), cy - int(20 * scale)
        ], fill=color)

        # Head Shape
        bbox = [cx - head_w//2, head_y, cx + head_w//2, head_y + head_h]
        draw.ellipse(bbox, fill=color, outline=outline)
        
        # Skin Texture on Head
        self.draw_organic_scales(draw, bbox, color, density=0.6)

        # Eyes (More distinct)
        eye_color = genetics.get('eye_color', (0, 0, 0))
        eye_size = int(5 * scale) # Bigger eyes
        eye_y = head_y + int(8 * scale)
        
        for offset in [-11, 11]: # Wider set eyes
            ex = cx + int(offset * scale)
            # Eye White
            draw.ellipse([ex - eye_size, eye_y - eye_size, ex + eye_size, eye_y + eye_size], fill=(240, 240, 200))
            # Pupil
            pupil_s = int(2.5 * scale)
            draw.ellipse([ex - pupil_s, eye_y - pupil_s, ex + pupil_s, eye_y + pupil_s], fill=eye_color)

    def _draw_shell_pattern(self, draw, cx, cy, w, h, scale, base_color, pat_color):
        """Draws a hex/scute pattern based on geometry"""
        
        # 1. Central Ridge (The Vertebral Scutes)
        scute_size = int(20 * scale)
        for i in range(3):
            y_pos = cy - int(25 * scale) + (i * int(22 * scale))
            
            # Draw a Hexagon-ish shape for central scutes
            poly = [
                (cx, y_pos - scute_size + 5),
                (cx + scute_size - 5, y_pos),
                (cx + scute_size - 5, y_pos + scute_size - 5),
                (cx, y_pos + scute_size),
                (cx - scute_size + 5, y_pos + scute_size - 5),
                (cx - scute_size + 5, y_pos)
            ]
            
            # Gradient fill for scute (Darker center, lighter edge)
            draw.polygon(poly, fill=self.get_variant_color(base_color, 1.05), outline=pat_color)
            
            # Inner "growth ring" details
            smaller_poly = [(x + (cx-x)*0.3, y + (y_pos+10-y)*0.3) for x, y in poly] # simple shrink
            draw.line(poly + [poly[0]], fill=pat_color, width=int(2*scale))

        # 2. Side Scutes (Costal Scutes)
        sides = [-1, 1]
        for side in sides:
            for i in range(2):
                sx = cx + (int(35 * scale) * side)
                sy = cy - int(15 * scale) + (i * int(30 * scale))
                
                # Draw curved scute representation
                bbox = [
                    sx - int(15 * scale), sy - int(15 * scale),
                    sx + int(15 * scale), sy + int(15 * scale)
                ]
                draw.chord(bbox, 0, 360, fill=self.get_variant_color(base_color, 0.95), outline=pat_color, width=int(2*scale))

    # --- Cache System ---
    def render_turtle_to_photoimage(self, genetics: Dict[str, Any], size: Optional[int] = None) -> Optional[ImageTk.PhotoImage]:
        img_size = size or 200
        
        # Check cache first
        cache_key = f"turtle_{hash(str(genetics))}_{img_size}"
        if cache_key in self.cache:
            self.cache_hits += 1
            return self.cache[cache_key]
        
        self.cache_misses += 1
        
        # Create PIL image (Transparent background)
        pil_image = Image.new('RGBA', (img_size, img_size), (0, 0, 0, 0)) 
        draw = ImageDraw.Draw(pil_image)
        
        # Draw procedural turtle
        self.draw_realistic_turtle(draw, genetics, img_size)
        
        # Convert to PhotoImage
        try:
            photo_image = ImageTk.PhotoImage(pil_image)
            self.cache_image(cache_key, photo_image)
            return photo_image
            
        except RuntimeError as e:
            if "no default root window" in str(e):
                # Save to temp file and return path
                temp_file = os.path.join(self.temp_dir, f"turtle_{id(genetics)}.png")
                pil_image.save(temp_file)
                return temp_file 
            else:
                raise e
    
    def cache_image(self, cache_key: str, photo_image: ImageTk.PhotoImage) -> None:
        if len(self.cache) >= self.max_cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[cache_key] = photo_image
    
    def clear_cache(self) -> None:
        self.cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0

    def get_rendering_capabilities(self) -> Dict[str, Any]:
        """
        Get information about rendering capabilities
        """
        return {
            'renderer_type': 'procedural_pil',
            'pil_drawing': True,
            'realistic_anatomy': True,
            'shell_patterns': True,
            'cache_enabled': True,
            'max_cache_size': self.max_cache_size,
            'can_render_turtle': True,
            'svg_required': False
        }

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


# ==========================================
# GLOBAL HELPER FUNCTIONS
# ==========================================

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