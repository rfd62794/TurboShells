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
        # Improved turtle SVG template with realistic anatomy
        self.turtle_template = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="200" height="200" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    {pattern_defs}
  </defs>
  
  <g id="turtle-base" fill="#8B4513" stroke="black" stroke-width="0.5">
    <!-- Carapace (Shell) -->
    <path
      id="carapace"
      d="M 20,40 C 5,50 5,80 20,90 L 80,90 C 95,80 95,50 80,40 Z"
      fill="{shell_fill}"
      stroke-width="2"
    />

    <!-- Head -->
    <path
      id="head"
      d="M 40,30 C 45,15 55,15 60,30 C 55,35 45,35 40,30 Z"
      fill="{head_color}"
    />

    <!-- Front Right Flipper -->
    <path
      id="front-right-flipper"
      d="M 75,45 C 85,35 90,50 85,60 Z"
      fill="{flipper_color}"
    />

    <!-- Front Left Flipper -->
    <path
      id="front-left-flipper"
      d="M 25,45 C 15,35 10,50 15,60 Z"
      fill="{flipper_color}"
    />

    <!-- Back Right Flipper -->
    <path
      id="back-right-flipper"
      d="M 70,85 C 80,90 75,100 65,95 Z"
      fill="{flipper_color}"
    />

    <!-- Back Left Flipper -->
    <path
      id="back-left-flipper"
      d="M 30,85 C 20,90 25,100 35,95 Z"
      fill="{flipper_color}"
    />

    <!-- Eyes -->
    <circle cx="45" cy="25" r="2" fill="{eye_color}" />
    <circle cx="55" cy="25" r="2" fill="{eye_color}" />
    
    <!-- Eye pupils -->
    <circle cx="45" cy="25" r="1" fill="black" />
    <circle cx="55" cy="25" r="1" fill="black" />
  </g>
</svg>'''
        
        # Pattern templates for the carapace
        self.patterns = {
            'stripes': '''<pattern id="stripes" x="0" y="0" width="10" height="10" patternUnits="userSpaceOnUse">
    <rect x="0" y="0" width="5" height="10" fill="{pattern_color}" opacity="0.7" />
    <rect x="5" y="0" width="5" height="10" fill="{pattern_color}" opacity="0.3" />
</pattern>''',
            
            'spots': '''<pattern id="spots" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
    <circle cx="5" cy="5" r="3" fill="{pattern_color}" opacity="0.6" />
    <circle cx="15" cy="15" r="3" fill="{pattern_color}" opacity="0.6" />
    <circle cx="15" cy="5" r="2" fill="{pattern_color}" opacity="0.4" />
    <circle cx="5" cy="15" r="2" fill="{pattern_color}" opacity="0.4" />
</pattern>''',
            
            'spiral': '''<pattern id="spiral" x="0" y="0" width="30" height="30" patternUnits="userSpaceOnUse">
    <path d="M 15,15 Q 20,10 25,15 T 15,25 Q 10,20 5,15 T 15,5" 
          fill="none" stroke="{pattern_color}" stroke-width="2" opacity="0.6" />
</pattern>''',
            
            'geometric': '''<pattern id="geometric" x="0" y="0" width="15" height="15" patternUnits="userSpaceOnUse">
    <polygon points="7.5,2 12,7 12,12 7.5,17 3,12 3,7" 
             fill="{pattern_color}" opacity="0.5" />
    <circle cx="7.5" cy="9.5" r="3" fill="{pattern_color}" opacity="0.3" />
</pattern>''',
            
            'complex': '''<pattern id="complex" x="0" y="0" width="25" height="25" patternUnits="userSpaceOnUse">
    <path d="M 5,5 Q 12.5,2 20,5 L 20,20 Q 12.5,23 5,20 Z" 
          fill="{pattern_color}" opacity="0.3" />
    <circle cx="8" cy="8" r="2" fill="{pattern_color}" opacity="0.6" />
    <circle cx="17" cy="8" r="2" fill="{pattern_color}" opacity="0.6" />
    <circle cx="12.5" cy="17" r="2" fill="{pattern_color}" opacity="0.6" />
</pattern>''',
            
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
        Generate a turtle SVG using the improved template with genetic colors
        """
        # Extract colors from genetics
        shell_color = self.rgb_to_hex(genetics.get('shell_base_color', (160, 82, 45)))  # Brown
        head_color = self.rgb_to_hex(genetics.get('head_color', (60, 179, 113)))  # Green
        flipper_color = self.rgb_to_hex(genetics.get('leg_color', (60, 179, 113)))  # Green for flippers
        eye_color = self.rgb_to_hex(genetics.get('eye_color', (0, 0, 0)))  # Black
        
        # Get pattern
        shell_pattern_type = genetics.get('shell_pattern_type', 'solid')
        pattern_template = self.patterns.get(shell_pattern_type, self.patterns['solid'])
        
        # Determine shell fill
        if shell_pattern_type == 'solid':
            # Solid color shell
            shell_fill = shell_color
            pattern_defs = ''
        else:
            # Patterned shell
            # Get pattern color
            shell_rgb = genetics.get('shell_base_color', (160, 82, 45))
            pattern_color = self.get_pattern_color(shell_rgb)
            
            # Fill pattern template
            pattern_defs = pattern_template.format(pattern_color=pattern_color)
            shell_fill = f"url(#{shell_pattern_type})"
        
        # Fill the main template
        svg_content = self.turtle_template.format(
            shell_fill=shell_fill,
            head_color=head_color,
            flipper_color=flipper_color,
            eye_color=eye_color,
            pattern_defs=pattern_defs
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
