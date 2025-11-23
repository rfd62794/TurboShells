"""
Visual Genetics System Demo
Complete demonstration of the SVG generation and voting system
"""

import pygame
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from core.visual_genetics import VisualGenetics
from core.genetic_svg_mapper import GeneticToSVGMapper
from core.turtle_svg_generator import TurtleSVGGenerator
from core.svg_pygame_renderer_hybrid import get_svg_renderer
from core.voting_system import VotingSystem
from core.genetic_pool_manager import GeneticPoolManager


def main():
    """Run the visual genetics demonstration"""
    print("=== TurboShells Visual Genetics System Demo ===")
    print()
    
    # Initialize PyGame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("TurboShells - Visual Genetics Demo")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    
    # Initialize systems
    vg = VisualGenetics()
    generator = TurtleSVGGenerator()
    voting_system = VotingSystem()
    pool_manager = GeneticPoolManager()
    svg_renderer = get_svg_renderer()
    
    # Connect systems
    voting_system.set_genetic_pool_manager(pool_manager)
    
    # Generate daily designs
    designs = voting_system.generate_daily_designs()
    current_design_index = 0
    
    print(f"Generated {len(designs)} daily designs for voting")
    print("Use LEFT/RIGHT arrows to navigate, SPACE to vote, ESC to exit")
    print()
    
    running = True
    demo_complete = False
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_LEFT:
                    if current_design_index > 0:
                        current_design_index -= 1
                        print(f"Design {current_design_index + 1}/{len(designs)}")
                elif event.key == pygame.K_RIGHT:
                    if current_design_index < len(designs) - 1:
                        current_design_index += 1
                        print(f"Design {current_design_index + 1}/{len(designs)}")
                elif event.key == pygame.K_SPACE:
                    # Vote for current design
                    if not demo_complete:
                        design = designs[current_design_index]
                        if design.voting_status == 'pending':
                            # Auto-generate ratings for demo
                            ratings = {
                                'overall': 3.0 + (current_design_index * 0.5),
                                'shell_appearance': 3.5,
                                'color_harmony': 4.0,
                                'pattern_quality': 3.0,
                                'proportions': 4.0
                            }
                            
                            result = voting_system.submit_ratings(design.id, ratings)
                            if result['success']:
                                print(f"* Voted on design {current_design_index + 1} - Earned ${result['reward_earned']}")
                                print(f"  Your ratings influenced future turtle genetics!")
                                
                                # Check if all designs are voted
                                status = voting_system.get_daily_status()
                                if status['completed_votes'] == status['total_designs']:
                                    demo_complete = True
                                    print(f"\n*** Demo Complete! You earned ${status['potential_earnings']} ***")
                                    print(f"Your votes have influenced the genetic pool!")
        
        # Clear screen
        screen.fill((240, 248, 255))  # Alice blue
        
        # Draw current design
        if designs and current_design_index < len(designs):
            design = designs[current_design_index]
            
            # Render turtle
            turtle_surface = svg_renderer.render_svg_string_to_surface(design.svg_content, 200)
            if turtle_surface:
                x = 100
                y = 200
                screen.blit(turtle_surface, (x, y))
            else:
                # Draw placeholder
                pygame.draw.circle(screen, (34, 139, 34), (200, 300), 50)
                text = font.render("Turtle", True, (255, 255, 255))
                screen.blit(text, (170, 290))
            
            # Draw design info
            y_offset = 100
            
            # Title
            title = font.render(f"Design {current_design_index + 1}/{len(designs)}", True, (0, 0, 0))
            screen.blit(title, (400, y_offset))
            y_offset += 40
            
            # Status
            if design.voting_status == 'completed':
                status_text = "* VOTED"
                status_color = (34, 139, 34)
            else:
                status_text = "PENDING VOTE"
                status_color = (70, 130, 180)
            
            status = font.render(status_text, True, status_color)
            screen.blit(status, (400, y_offset))
            y_offset += 40
            
            # Feature breakdown
            features_text = font.render("Features:", True, (0, 0, 0))
            screen.blit(features_text, (400, y_offset))
            y_offset += 30
            
            small_font = pygame.font.Font(None, 18)
            for feature_name, feature_data in design.feature_breakdown.items():
                feature_text = f"{feature_data['display_name']}: "
                
                if feature_data['type'] == 'color':
                    rgb = feature_data['value']
                    pygame.draw.rect(screen, rgb, (400, y_offset, 20, 15))
                    feature_text += f"RGB({rgb[0]},{rgb[1]},{rgb[2]})"
                elif feature_data['type'] == 'pattern':
                    feature_text += feature_data['value'].title()
                elif feature_data['type'] == 'proportions':
                    prop_data = feature_data['value']
                    feature_text += f"S:{prop_data['shell_size']:.1f} H:{prop_data['head_size']:.1f}"
                
                text = small_font.render(feature_text, True, (0, 0, 0))
                screen.blit(text, (400, y_offset))
                y_offset += 20
        
        # Draw instructions
        instructions = [
            "← → Navigate designs",
            "SPACE Vote for design",
            "ESC Exit demo"
        ]
        
        y_offset = 450
        for instruction in instructions:
            text = small_font.render(instruction, True, (100, 100, 100))
            screen.blit(text, (400, y_offset))
            y_offset += 25
        
        # Draw voting progress
        status = voting_system.get_daily_status()
        progress_text = f"Progress: {status['completed_votes']}/{status['total_designs']} voted"
        progress = font.render(progress_text, True, (0, 0, 0))
        screen.blit(progress, (400, 550))
        
        # Draw rewards
        rewards_text = f"Potential earnings: ${status['potential_earnings']}"
        rewards = font.render(rewards_text, True, (34, 139, 34))
        screen.blit(rewards, (400, 575))
        
        # Draw demo complete message
        if demo_complete:
            complete_text = "Demo Complete! Check console for summary."
            complete = font.render(complete_text, True, (34, 139, 34))
            complete_rect = complete.get_rect(center=(400, 50))
            screen.blit(complete, complete_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    # Print final statistics
    print(f"\n=== Demo Statistics ===")
    final_status = voting_system.get_daily_status()
    final_stats = voting_system.get_statistics()
    pool_status = pool_manager.get_genetic_pool_status()
    
    print(f"Votes cast: {final_status['completed_votes']}/{final_status['total_designs']}")
    print(f"Total earned: ${final_status['potential_earnings']}")
    print(f"Genetic pool influence: {pool_status['average_weight']:.2f} average weight")
    print(f"Most influenced traits: {[trait[0] for trait in pool_status['most_influenced_traits'][:3]]}")
    
    pygame.quit()


if __name__ == "__main__":
    main()
