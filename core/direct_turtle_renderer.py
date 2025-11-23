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