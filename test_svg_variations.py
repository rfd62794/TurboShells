#!/usr/bin/env python3

import pygame
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from core.visual_genetics import VisualGenetics
from core.turtle_svg_generator import TurtleSVGGenerator
from core.svg_pygame_renderer_direct import get_svg_renderer

def main():
    """Test SVG rendering with very different turtle genetics"""
    print("=== Testing SVG Variations ===")
    
    # Initialize PyGame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("SVG Variations Test")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    
    # Initialize systems
    vg = VisualGenetics()
    generator = TurtleSVGGenerator()
    renderer = get_svg_renderer()
    
    # Generate turtles with very different genetics
    turtles = []
    
    # Create 4 very different turtles
    for i in range(4):
        # Force specific genetic values for maximum visual difference
        genetics = vg.generate_random_genetics()
        
        # Override with extreme values for testing
        if i == 0:
            # Red shell, green body
            genetics['shell_base_color'] = (255, 0, 0)
            genetics['body_base_color'] = (0, 255, 0)
            genetics['shell_pattern_type'] = 'stripes'
        elif i == 1:
            # Blue shell, yellow body
            genetics['shell_base_color'] = (0, 0, 255)
            genetics['body_base_color'] = (255, 255, 0)
            genetics['shell_pattern_type'] = 'spots'
        elif i == 2:
            # Green shell, purple body
            genetics['shell_base_color'] = (0, 128, 0)
            genetics['body_base_color'] = (128, 0, 128)
            genetics['shell_pattern_type'] = 'spiral'
        else:
            # Orange shell, cyan body
            genetics['shell_base_color'] = (255, 165, 0)
            genetics['body_base_color'] = (0, 255, 255)
            genetics['shell_pattern_type'] = 'geometric'
        
        # Generate SVG and render
        svg_drawing = generator.generate_turtle_svg(genetics, 150)
        surface = renderer.render_svg_drawing_to_surface(svg_drawing, 150)
        
        if surface:
            turtles.append({
                'genetics': genetics,
                'surface': surface,
                'description': f"Turtle {i+1}: {genetics['shell_pattern_type'].title()} pattern"
            })
        else:
            print(f"Failed to render turtle {i+1}")
    
    print(f"Generated {len(turtles)} test turtles")
    
    # Display loop
    running = True
    selected = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_LEFT:
                    selected = (selected - 1) % len(turtles)
                elif event.key == pygame.K_RIGHT:
                    selected = (selected + 1) % len(turtles)
        
        # Clear screen
        screen.fill((240, 248, 255))
        
        # Draw current turtle
        if turtles and selected < len(turtles):
            turtle = turtles[selected]
            
            # Center the turtle
            x = (800 - turtle['surface'].get_width()) // 2
            y = (600 - turtle['surface'].get_height()) // 2 - 50
            screen.blit(turtle['surface'], (x, y))
            
            # Draw description
            desc_surface = font.render(turtle['description'], True, (0, 0, 0))
            desc_rect = desc_surface.get_rect(center=(400, 500))
            screen.blit(desc_surface, desc_rect)
            
            # Draw genetic info
            genetics = turtle['genetics']
            info_lines = [
                f"Shell: RGB{genetics['shell_base_color']}",
                f"Body: RGB{genetics['body_base_color']}",
                f"Pattern: {genetics['shell_pattern_type']}",
                f"Eye: RGB{genetics['eye_color']}"
            ]
            
            small_font = pygame.font.Font(None, 18)
            for i, line in enumerate(info_lines):
                text_surface = small_font.render(line, True, (100, 100, 100))
                screen.blit(text_surface, (50, 50 + i * 25))
        
        # Draw navigation
        nav_text = f"Turtle {selected + 1}/{len(turtles)} - Use LEFT/RIGHT arrows, ESC to exit"
        nav_surface = font.render(nav_text, True, (0, 0, 0))
        nav_rect = nav_surface.get_rect(center=(400, 550))
        screen.blit(nav_surface, nav_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("Test completed!")

if __name__ == '__main__':
    main()
