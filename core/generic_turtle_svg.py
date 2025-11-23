"""
Generic Turtle SVG Template for TurboShells
Uses a predefined turtle SVG shape with customizable colors
"""

import re
from typing import Dict, Any, Tuple


class GenericTurtleSVG:
    """
    Generic turtle SVG template with customizable colors and patterns
    """
    
    def __init__(self):
        # Base turtle SVG template - simple but recognizable turtle shape
        self.turtle_template = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
  <!-- Shadow -->
  <ellipse cx="100" cy="180" rx="60" ry="15" fill="#000000" opacity="0.2" />
  
  <!-- Shell -->
  <ellipse cx="100" cy="100" rx="70" ry="50" fill="{shell_color}" stroke="{shell_outline}" stroke-width="2" />
  
  <!-- Shell pattern -->
  {shell_pattern}
  
  <!-- Head -->
  <ellipse cx="100" cy="50" rx="25" ry="20" fill="{head_color}" stroke="{head_outline}" stroke-width="2" />
  
  <!-- Eyes -->
  <circle cx="90" cy="45" r="5" fill="{eye_color}" />
  <circle cx="110" cy="45" r="5" fill="{eye_color}" />
  <circle cx="90" cy="45" r="2" fill="black" />
  <circle cx="110" cy="45" r="2" fill="black" />
  
  <!-- Legs -->
  <rect x="50" y="120" width="12" height="30" rx="6" fill="{leg_color}" stroke="{leg_outline}" stroke-width="1" />
  <rect x="138" y="120" width="12" height="30" rx="6" fill="{leg_color}" stroke="{leg_outline}" stroke-width="1" />
  <rect x="70" y="140" width="12" height="25" rx="6" fill="{leg_color}" stroke="{leg_outline}" stroke-width="1" />
  <rect x="118" y="140" width="12" height="25" rx="6" fill="{leg_color}" stroke="{leg_outline}" stroke-width="1" />
  
  <!-- Tail -->
  <path d="M 100 150 Q 80 170 60 160" fill="none" stroke="{tail_color}" stroke-width="8" stroke-linecap="round" />
</svg>'''
        
        # Pattern templates
        self.patterns = {
            'stripes': '''<rect x="60" y="85" width="80" height="5" fill="{pattern_color}" opacity="0.6" />
<rect x="60" y="95" width="80" height="5" fill="{pattern_color}" opacity="0.6" />
<rect x="60" y="105" width="80" height="5" fill="{pattern_color}" opacity="0.6" />
<rect x="60" y="115" width="80" height="5" fill="{pattern_color}" opacity="0.6" />''',
            
            'spots': '''<circle cx="75" cy="90" r="8" fill="{pattern_color}" opacity="0.6" />
<circle cx="125" cy="90" r="8" fill="{pattern_color}" opacity="0.6" />
<circle cx="100" cy="110" r="8" fill="{pattern_color}" opacity="0.6" />
<circle cx="85" cy="115" r="6" fill="{pattern_color}" opacity="0.6" />
<circle cx="115" cy="115" r="6" fill="{pattern_color}" opacity="0.6" />''',
            
            'spiral': '''<path d="M 100 100 Q 110 90 120 100 T 100 120 Q 90 110 80 100 T 100 80" 
               fill="none" stroke="{pattern_color}" stroke-width="3" opacity="0.6" />''',
            
            'geometric': '''<polygon points="100,70 120,90 120,110 100,130 80,110 80,90" 
               fill="{pattern_color}" opacity="0.6" />
<circle cx="100" cy="100" r="15" fill="{pattern_color}" opacity="0.4" />''',
            
            'complex': '''<path d="M 70 85 Q 100 75 130 85 L 130 115 Q 100 125 70 115 Z" 
               fill="{pattern_color}" opacity="0.3" />
<circle cx="85" cy="95" r="5" fill="{pattern_color}" opacity="0.5" />
<circle cx="115" cy="95" r="5" fill="{pattern_color}" opacity="0.5" />
<circle cx="100" cy="110" r="5" fill="{pattern_color}" opacity="0.5" />''',
            
            'solid': '''<!-- No pattern for solid shell -->'''
        }
    
    def rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex color"""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def get_darker_color(self, rgb: Tuple[int, int, int], factor: float = 0.8) -> str:
        """Get a darker version of a color for outlines"""
        darker_rgb = tuple(int(c * factor) for c in rgb)
        return self.rgb_to_hex(darker_rgb)
    
    def get_pattern_color(self, shell_color: Tuple[int, int, int]) -> str:
        """Get a contrasting color for shell patterns"""
        # Create a contrasting color by inverting some channels
        r, g, b = shell_color
        pattern_rgb = (
            max(0, min(255, 255 - r // 2)),
            max(0, min(255, 255 - g // 2)),
            max(0, min(255, 255 - b // 2))
        )
        return self.rgb_to_hex(pattern_rgb)
    
    def generate_turtle_svg(self, genetics: Dict[str, Any]) -> str:
        """
        Generate a turtle SVG using the template with genetic colors
        """
        # Extract colors from genetics
        shell_color = self.rgb_to_hex(genetics.get('shell_base_color', (34, 139, 34)))
        body_color = self.rgb_to_hex(genetics.get('body_base_color', (139, 90, 43)))
        eye_color = self.rgb_to_hex(genetics.get('eye_color', (0, 0, 0)))
        head_color = self.rgb_to_hex(genetics.get('head_color', (139, 90, 43)))
        leg_color = self.rgb_to_hex(genetics.get('leg_color', (101, 67, 33)))
        
        # Get pattern
        shell_pattern_type = genetics.get('shell_pattern_type', 'solid')
        pattern_template = self.patterns.get(shell_pattern_type, self.patterns['solid'])
        
        # Get pattern color
        shell_rgb = genetics.get('shell_base_color', (34, 139, 34))
        pattern_color = self.get_pattern_color(shell_rgb)
        
        # Fill pattern template
        shell_pattern_svg = pattern_template.format(pattern_color=pattern_color)
        
        # Get outline colors
        shell_outline = self.get_darker_color(genetics.get('shell_base_color', (34, 139, 34)))
        head_outline = self.get_darker_color(genetics.get('head_color', (139, 90, 43)))
        leg_outline = self.get_darker_color(genetics.get('leg_color', (101, 67, 33)))
        tail_color = leg_color  # Use leg color for tail
        
        # Fill the main template
        svg_content = self.turtle_template.format(
            shell_color=shell_color,
            shell_outline=shell_outline,
            shell_pattern=shell_pattern_svg,
            head_color=head_color,
            head_outline=head_outline,
            eye_color=eye_color,
            leg_color=leg_color,
            leg_outline=leg_outline,
            tail_color=tail_color
        )
        
        return svg_content
    
    def create_turtle_with_variations(self, base_genetics: Dict[str, Any], variations: int = 5) -> list:
        """
        Create multiple turtle variations with slight genetic differences
        """
        from core.visual_genetics import VisualGenetics
        
        vg = VisualGenetics()
        turtles = []
        
        for i in range(variations):
            # Create a copy of base genetics
            genetics = base_genetics.copy()
            
            # Add some variation
            if i > 0:
                # Vary shell color slightly
                shell_rgb = genetics['shell_base_color']
                variation = 20 * i  # Increase variation with each turtle
                genetics['shell_base_color'] = (
                    max(0, min(255, shell_rgb[0] + variation)),
                    max(0, min(255, shell_rgb[1] - variation)),
                    max(0, min(255, shell_rgb[2] + variation // 2))
                )
                
                # Vary pattern
                patterns = ['stripes', 'spots', 'spiral', 'geometric', 'complex']
                genetics['shell_pattern_type'] = patterns[i % len(patterns)]
            
            # Generate SVG
            svg_content = self.generate_turtle_svg(genetics)
            turtles.append({
                'genetics': genetics,
                'svg': svg_content,
                'name': f"Turtle {i+1}"
            })
        
        return turtles


# Utility functions
def create_generic_turtle_svg(genetics: Dict[str, Any]) -> str:
    """
    Create a generic turtle SVG from genetics
    """
    turtle_svg = GenericTurtleSVG()
    return turtle_svg.generate_turtle_svg(genetics)


def create_turtle_variations(base_genetics: Dict[str, Any], count: int = 5) -> list:
    """
    Create multiple turtle variations
    """
    turtle_svg = GenericTurtleSVG()
    return turtle_svg.create_turtle_with_variations(base_genetics, count)
