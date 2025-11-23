#!/usr/bin/env python3

from core.visual_genetics import VisualGenetics
from core.turtle_svg_generator import TurtleSVGGenerator
from core.svg_pygame_renderer_direct import DirectSVGToPyGameRenderer
import re

def main():
    # Generate a turtle SVG
    vg = VisualGenetics()
    genetics = vg.generate_random_genetics()
    generator = TurtleSVGGenerator()
    svg_drawing = generator.generate_turtle_svg(genetics, 100)

    # Get the SVG string
    svg_string = svg_drawing.as_svg()
    print('Testing SVG element extraction:')
    print(f'SVG length: {len(svg_string)}')

    # Test the exact regex patterns used in the renderer
    circles = re.findall(r'<circle[^>]*cx="([^"]*)"[^>]*cy="([^"]*)"[^>]*r="([^"]*)"[^>]*fill="([^"]*)"[^>]*', svg_string)
    ellipses = re.findall(r'<ellipse[^>]*cx="([^"]*)"[^>]*cy="([^"]*)"[^>]*rx="([^"]*)"[^>]*ry="([^"]*)"[^>]*fill="([^"]*)"[^>]*', svg_string)
    paths = re.findall(r'<path[^>]*d="([^"]*)"[^>]*fill="([^"]*)"[^>]*', svg_string)

    print(f'Circles found with full pattern: {len(circles)}')
    print(f'Ellipses found with full pattern: {len(ellipses)}')
    print(f'Paths found with full pattern: {len(paths)}')

    if ellipses:
        print(f'First ellipse details: {ellipses[0]}')
        
    # Test color parsing
    renderer = DirectSVGToPyGameRenderer()
    if ellipses:
        color_str = ellipses[0][4]  # fill color
        parsed_color = renderer.parse_color(color_str)
        print(f'Color {color_str} parsed to: {parsed_color}')

    # Test actual rendering
    print('\nTesting actual rendering...')
    surface = renderer.render_svg_string_to_surface(svg_string, 100)
    if surface:
        print(f'Successfully rendered surface: {surface.get_size()}')
    else:
        print('Failed to render surface')

if __name__ == '__main__':
    main()
