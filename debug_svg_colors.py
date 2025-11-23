#!/usr/bin/env python3

from core.visual_genetics import VisualGenetics
from core.turtle_svg_generator import TurtleSVGGenerator
import re

def main():
    """Debug if colors are actually being applied in SVG"""
    print("=== Debug SVG Color Application ===")
    
    # Initialize systems
    vg = VisualGenetics()
    generator = TurtleSVGGenerator()
    
    # Generate a turtle with specific colors
    genetics = vg.generate_random_genetics()
    genetics['shell_base_color'] = (255, 0, 0)  # Bright red
    genetics['body_base_color'] = (0, 255, 0)  # Bright green
    
    print(f"Input genetics:")
    print(f"  Shell color: RGB{genetics['shell_base_color']}")
    print(f"  Body color: RGB{genetics['body_base_color']}")
    
    # Generate SVG
    svg_drawing = generator.generate_turtle_svg(genetics, 200)
    svg_string = svg_drawing.as_svg()
    
    # Extract colors from SVG
    hex_colors = re.findall(r'fill="#([^"]*)"', svg_string)
    stroke_colors = re.findall(r'stroke="#([^"]*)"', svg_string)
    
    print(f"\nColors found in SVG:")
    print(f"  Fill colors: {set(hex_colors)}")
    print(f"  Stroke colors: {set(stroke_colors)}")
    
    # Check for expected colors
    red_hex = '#ff0000'
    green_hex = '#00ff00'
    
    print(f"\nColor check:")
    print(f"  Red #{red_hex} found: {'Yes' if red_hex in hex_colors else 'No'}")
    print(f"  Green #{green_hex} found: {'Yes' if green_hex in hex_colors else 'No'}")
    
    # Show a sample of the SVG content
    print(f"\nSVG content sample (first 1000 chars):")
    print(svg_string[:1000])
    print("...")

if __name__ == '__main__':
    main()
