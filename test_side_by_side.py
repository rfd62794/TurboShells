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
    """Side-by-side comparison of different turtle colors"""
    print("=== Side-by-Side Color Test ===")
    
    # Initialize PyGame
    pygame.init()
    screen = pygame.display.set_mode((1000, 400))
    pygame.display.set_caption("Side-by-Side Color Test")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    
    # Initialize systems
    vg = VisualGenetics()
    generator = TurtleSVGGenerator()
    renderer = get_svg_renderer()
    
    # Create turtles with very different colors
    color_tests = [
        ((255, 0, 0), "Red Shell"),
        ((0, 255, 0), "Green Shell"), 
        ((0, 0, 255), "Blue Shell"),
        ((255, 255, 0), "Yellow Shell"),
        ((255, 0, 255), "Magenta Shell")
    ]
    
    turtles = []
    
    for i, (shell_color, description) in enumerate(color_tests):
        # Create genetics with specific shell color
        genetics = vg.generate_random_genetics()
        genetics['shell_base_color'] = shell_color
        genetics['body_base_color'] = (128, 128, 128)  # Gray body for contrast
        
        # Generate SVG and render
        svg_drawing = generator.generate_turtle_svg(genetics, 150)
        surface = renderer.render_svg_drawing_to_surface(svg_drawing, 150)
        
        if surface:
            turtles.append({
                'surface': surface,
                'description': description,
                'color': shell_color
            })
            print(f"Generated {description} turtle: RGB{shell_color}")
        else:
            print(f"Failed to render {description} turtle")
    
    # Display loop
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Clear screen
        screen.fill((240, 248, 255))
        
        # Draw turtles side by side
        x_offset = 50
        y_offset = 100
        
        for i, turtle in enumerate(turtles):
            x = x_offset + i * 180
            y = y_offset
            
            # Draw turtle
            screen.blit(turtle['surface'], (x, y))
            
            # Draw label
            label_surface = font.render(turtle['description'], True, (0, 0, 0))
            label_rect = label_surface.get_rect(center=(x + 75, y - 20))
            screen.blit(label_surface, label_rect)
            
            # Draw color info
            color_text = f"RGB{turtle['color']}"
            color_surface = font.render(color_text, True, (100, 100, 100))
            color_rect = color_surface.get_rect(center=(x + 75, y + 170))
            screen.blit(color_surface, color_rect)
        
        # Draw title
        title_surface = font.render("SVG Color Rendering Test - Different Shell Colors", True, (0, 0, 0))
        title_rect = title_surface.get_rect(center=(500, 30))
        screen.blit(title_surface, title_rect)
        
        # Draw instructions
        inst_surface = font.render("Press ESC to exit", True, (100, 100, 100))
        inst_rect = inst_surface.get_rect(center=(500, 370))
        screen.blit(inst_surface, inst_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("Side-by-side test completed!")

if __name__ == '__main__':
    main()
