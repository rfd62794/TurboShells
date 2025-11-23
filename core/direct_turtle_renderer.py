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
        self.current_genetics = {} 
        print("Direct Turtle Renderer: Initialized Procedural Engine")
    
    # --- Color Utilities ---
    def rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex color"""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def get_variant_color(self, rgb: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
        """Adjust brightness safely"""
        return tuple(max(0, min(255, int(c * factor))) for c in rgb)

    # --- TEXTURE ENGINES ---
    
    def _draw_triangle_texture(self, draw, points, color, density=0.4):
        """
        Draws scales strictly inside a triangle using Barycentric coordinates.
        This prevents dots from floating in the empty space outside the flipper.
        """
        p1, p2, p3 = points
        
        # Calculate area to determine how many dots to draw
        area = 0.5 * abs((p1[0]*(p2[1]-p3[1]) + p2[0]*(p3[1]-p1[1]) + p3[0]*(p1[1]-p2[1])))
        num_dots = int(area * 0.005 * density)
        
        scale_color = self.get_variant_color(color, 1.1)
        
        for _ in range(num_dots):
            # Barycentric coordinate generation (guarantees point is inside triangle)
            r1 = random.random()
            r2 = random.random()
            sqrt_r1 = math.sqrt(r1)
            
            x = (1 - sqrt_r1) * p1[0] + (sqrt_r1 * (1 - r2)) * p2[0] + (sqrt_r1 * r2) * p3[0]
            y = (1 - sqrt_r1) * p1[1] + (sqrt_r1 * (1 - r2)) * p2[1] + (sqrt_r1 * r2) * p3[1]
            
            size = random.randint(1, 2)
            draw.ellipse([x, y, x+size, y+size], fill=scale_color)

    def _draw_ellipse_texture(self, draw, bbox, color, density=0.6):
        """Draws scales inside an ellipse using rejection sampling"""
        x1, y1, x2, y2 = bbox
        w, h = x2 - x1, y2 - y1
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        
        num_dots = int((w * h) * 0.005 * density)
        scale_color = self.get_variant_color(color, 1.1)
        
        count = 0
        attempts = 0
        while count < num_dots and attempts < num_dots * 3:
            attempts += 1
            # Pick random point in box
            rx = random.randint(int(x1), int(x2))
            ry = random.randint(int(y1), int(y2))
            
            # Check if inside ellipse equation
            if ((rx - cx) / (w/2))**2 + ((ry - cy) / (h/2))**2 <= 0.8:
                size = random.randint(1, 2)
                draw.ellipse([rx, ry, rx+size, ry+size], fill=scale_color)
                count += 1

    # --- Main Rendering Logic ---
    def draw_realistic_turtle(self, draw: ImageDraw.Draw, genetics: Dict[str, Any], size: int):
        center_x = size // 2
        center_y = size // 2
        scale = size / 200.0
        
        self.current_genetics = genetics
        gene_seed = hash(str(genetics)) 
        random.seed(gene_seed)

        # --- Extract Genes ---
        shell_base = genetics.get('shell_base_color', (34, 139, 34))
        skin_base = genetics.get('head_color', (46, 125, 50))
        pattern_color = genetics.get('pattern_color', self.get_variant_color(shell_base, 0.6))
        
        skin_shadow = self.get_variant_color(skin_base, 0.7)
        shell_shadow = self.get_variant_color(shell_base, 0.6)
        
        # --- 1. Drop Shadow ---
        shadow_y_offset = int(10 * scale)
        draw.ellipse([
            center_x - int(60 * scale), center_y - int(40 * scale) + shadow_y_offset,
            center_x + int(60 * scale), center_y + int(50 * scale) + shadow_y_offset
        ], fill=(0, 0, 0, 60))

        # --- 2. Limbs & Tail (Textured) ---
        self._draw_limbs(draw, center_x, center_y, scale, skin_base, skin_shadow)
        self._draw_tail(draw, center_x, center_y, scale, skin_base, skin_shadow)
        
        # --- 3. Head (Textured) ---
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

        # --- 5. Shell Pattern ---
        self._draw_shell_pattern(draw, center_x, center_y, shell_w, shell_h, scale, shell_base, pattern_color)

    def _draw_limbs(self, draw, cx, cy, scale, color, outline):
        """Draws flippers with strict internal texture"""
        offsets = [
            (45, -35, 85, -55, 75, -5),    # Front Right
            (-45, -35, -85, -55, -75, -5), # Front Left
            (35, 35, 60, 55, 40, 65),      # Back Right
            (-35, 35, -60, 55, -40, 65)    # Back Left
        ]

        for p1x, p1y, p2x, p2y, p3x, p3y in offsets:
            points = [
                (cx + int(p1x * scale), cy + int(p1y * scale)),
                (cx + int(p2x * scale), cy + int(p2y * scale)),
                (cx + int(p3x * scale), cy + int(p3y * scale))
            ]
            draw.polygon(points, fill=color, outline=outline)
            
            # Triangle Texture Logic
            self._draw_triangle_texture(draw, points, color)

    def _draw_tail(self, draw, cx, cy, scale, color, outline):
        tail_len = int(25 * scale)
        points = [
            (cx - int(5 * scale), cy + int(50 * scale)),
            (cx + int(5 * scale), cy + int(50 * scale)),
            (cx, cy + int(50 * scale) + tail_len)
        ]
        draw.polygon(points, fill=color, outline=outline)
        self._draw_triangle_texture(draw, points, color)

    def _draw_head(self, draw, cx, cy, scale, color, outline, genetics):
        head_w = int(32 * scale)
        head_h = int(35 * scale)
        head_y = cy - int(75 * scale) 
        
        # Neck
        draw.rectangle([
            cx - int(12 * scale), head_y + int(15 * scale),
            cx + int(12 * scale), cy - int(20 * scale)
        ], fill=color)

        # Head Shape
        bbox = [cx - head_w//2, head_y, cx + head_w//2, head_y + head_h]
        draw.ellipse(bbox, fill=color, outline=outline)
        
        # Ellipse Texture Logic
        self._draw_ellipse_texture(draw, bbox, color)

        # Eyes
        eye_color = genetics.get('eye_color', (0, 0, 0))
        eye_size = int(5 * scale)
        eye_y = head_y + int(8 * scale)
        
        for offset in [-11, 11]: 
            ex = cx + int(offset * scale)
            draw.ellipse([ex - eye_size, eye_y - eye_size, ex + eye_size, eye_y + eye_size], fill=(240, 240, 200))
            pupil_s = int(2.5 * scale)
            draw.ellipse([ex - pupil_s, eye_y - pupil_s, ex + pupil_s, eye_y + pupil_s], fill=eye_color)

    def _draw_shell_pattern(self, draw, cx, cy, w, h, scale, base_color, pat_color):
        styles = ['hex', 'spots', 'stripes', 'rings']
        
        # --- FIXED LOGIC: CHECK MULTIPLE KEYS ---
        keys_to_check = ['shell_pattern', 'shell_pattern_type', 'pattern_type', 'pattern']
        raw_pattern = None
        
        # Look for the first matching key in genetics
        for k in keys_to_check:
            if k in self.current_genetics:
                raw_pattern = self.current_genetics[k]
                break
        
        style = 'hex'
        if raw_pattern:
            if isinstance(raw_pattern, dict):
                style = raw_pattern.get('type', 'hex')
            else:
                style = str(raw_pattern).lower()
        
        # If style is not recognized, fallback to hash
        if style not in styles:
            style_idx = hash(str(self.current_genetics)) % len(styles)
            style = styles[style_idx]

        # Draw specific style
        if style == 'spots':
            self._draw_pattern_spots(draw, cx, cy, w, h, scale, pat_color)
        elif style == 'stripes':
            self._draw_pattern_stripes(draw, cx, cy, w, h, scale, pat_color)
        elif style == 'rings':
            self._draw_pattern_rings(draw, cx, cy, w, h, scale, pat_color)
        else:
            self._draw_pattern_hex(draw, cx, cy, w, h, scale, base_color, pat_color)

    # --- Pattern Drawers ---
    def _draw_pattern_spots(self, draw, cx, cy, w, h, scale, color):
        num_spots = 12
        for _ in range(num_spots):
            sx = cx + int(random.randint(int(-w*0.6), int(w*0.6)))
            sy = cy + int(random.randint(int(-h*0.6), int(h*0.6)))
            r = int(random.randint(4, 9) * scale)
            draw.ellipse([sx-r, sy-r, sx+r, sy+r], fill=color)

    def _draw_pattern_stripes(self, draw, cx, cy, w, h, scale, color):
        num_stripes = 5
        for i in range(num_stripes):
            y = cy - int(h*0.6) + (i * int(h*0.3))
            stripe_w = int(w * (0.9 - abs(i-2)*0.2)) 
            thick = int(6 * scale)
            draw.line([cx - stripe_w, y, cx + stripe_w, y], fill=color, width=thick)

    def _draw_pattern_rings(self, draw, cx, cy, w, h, scale, color):
        draw.ellipse([cx - int(w*0.7), cy - int(h*0.7), cx + int(w*0.7), cy + int(h*0.7)], outline=color, width=int(3*scale))
        draw.ellipse([cx - int(w*0.4), cy - int(h*0.4), cx + int(w*0.4), cy + int(h*0.4)], outline=color, width=int(3*scale))
        r = int(5*scale)
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=color)

    def _draw_pattern_hex(self, draw, cx, cy, w, h, scale, base_color, pat_color):
        scute_size = int(20 * scale)
        for i in range(3):
            y_pos = cy - int(25 * scale) + (i * int(22 * scale))
            poly = [
                (cx, y_pos - scute_size + 5), (cx + scute_size - 5, y_pos),
                (cx + scute_size - 5, y_pos + scute_size - 5), (cx, y_pos + scute_size),
                (cx - scute_size + 5, y_pos + scute_size - 5), (cx - scute_size + 5, y_pos)
            ]
            draw.polygon(poly, fill=self.get_variant_color(base_color, 1.05), outline=pat_color)
            smaller_poly = [(x + (cx-x)*0.3, y + (y_pos+10-y)*0.3) for x, y in poly] 
            draw.line(poly + [poly[0]], fill=pat_color, width=int(2*scale))

        sides = [-1, 1]
        for side in sides:
            for i in range(2):
                sx = cx + (int(35 * scale) * side)
                sy = cy - int(15 * scale) + (i * int(30 * scale))
                bbox = [sx - int(15 * scale), sy - int(15 * scale), sx + int(15 * scale), sy + int(15 * scale)]
                draw.chord(bbox, 0, 360, fill=self.get_variant_color(base_color, 0.95), outline=pat_color, width=int(2*scale))

    # --- Cache System ---
    def render_turtle_to_photoimage(self, genetics: Dict[str, Any], size: Optional[int] = None) -> Optional[ImageTk.PhotoImage]:
        img_size = size or 200
        cache_key = f"turtle_{hash(str(genetics))}_{img_size}"
        
        if cache_key in self.cache:
            self.cache_hits += 1
            return self.cache[cache_key]
        
        self.cache_misses += 1
        
        pil_image = Image.new('RGBA', (img_size, img_size), (0, 0, 0, 0)) 
        draw = ImageDraw.Draw(pil_image)
        self.draw_realistic_turtle(draw, genetics, img_size)
        
        try:
            photo_image = ImageTk.PhotoImage(pil_image)
            self.cache_image(cache_key, photo_image)
            return photo_image
        except RuntimeError as e:
            if "no default root window" in str(e):
                temp_file = os.path.join(self.temp_dir, f"turtle_{id(genetics)}.png")
                pil_image.save(temp_file)
                return temp_file 
            else:
                raise e
    
    def cache_image(self, cache_key: str, photo_image: ImageTk.PhotoImage) -> None:
        if len(self.cache) >= self.max_cache_size:
            del self.cache[next(iter(self.cache))]
        self.cache[cache_key] = photo_image
    
    def clear_cache(self) -> None:
        self.cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0

    def get_rendering_capabilities(self) -> Dict[str, Any]:
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

_renderer_instance = None

def get_direct_renderer() -> DirectTurtleRenderer:
    global _renderer_instance
    if _renderer_instance is None:
        _renderer_instance = DirectTurtleRenderer()
    return _renderer_instance

def render_turtle_directly(genetics: Dict[str, Any], size: Optional[int] = None) -> Optional[ImageTk.PhotoImage]:
    renderer = get_direct_renderer()
    return renderer.render_turtle_to_photoimage(genetics, size)

def clear_direct_cache() -> None:
    renderer = get_direct_renderer()
    renderer.clear_cache()

def get_direct_cache_stats() -> Dict[str, Any]:
    renderer = get_direct_renderer()
    return renderer.get_cache_stats()