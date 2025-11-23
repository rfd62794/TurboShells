#!/usr/bin/env python3

"""
Working Visual Genetics Demo for TurboShells
Uses PyGame with the direct SVG renderer that we know works
"""

import pygame
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from core.visual_genetics import VisualGenetics
from core.genetic_svg_mapper import GeneticToSVGMapper
from core.turtle_svg_generator import TurtleSVGGenerator
from core.svg_pygame_renderer_direct import get_svg_renderer
from core.voting_system import VotingSystem
from core.genetic_pool_manager import GeneticPoolManager


class WorkingVisualGeneticsDemo:
    """Working visual genetics demonstration using PyGame"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 700))
        pygame.display.set_caption("TurboShells Visual Genetics System - Working Demo")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Initialize systems
        self.vg = VisualGenetics()
        self.mapper = GeneticToSVGMapper()
        self.generator = TurtleSVGGenerator()
        self.renderer = get_svg_renderer()
        self.voting_system = VotingSystem()
        self.pool_manager = GeneticPoolManager()
        
        self.voting_system.set_genetic_pool_manager(self.pool_manager)
        
        # Demo state
        self.designs = []
        self.current_design_index = 0
        self.demo_complete = False
        
        # Generate designs
        self.generate_designs()
        
        # Display first design
        self.display_current_design()
    
    def generate_designs(self):
        """Generate daily designs for voting"""
        print("Generating daily designs...")
        self.designs = self.voting_system.generate_daily_designs()
        print(f"Generated {len(self.designs)} designs for voting")
    
    def display_current_design(self):
        """Display the current turtle design"""
        if not self.designs or self.current_design_index >= len(self.designs):
            return
        
        design = self.designs[self.current_design_index]
        
        # Clear screen
        self.screen.fill((240, 248, 255))  # Alice blue
        
        # Render turtle
        surface = self.renderer.render_turtle_to_surface(design.genetics, 300)
        
        if surface:
            # Center the turtle
            x = (1000 - surface.get_width()) // 2 - 200
            y = (700 - surface.get_height()) // 2 - 50
            self.screen.blit(surface, (x, y))
        else:
            # Show error
            error_text = self.font.render("Failed to render turtle", True, (255, 0, 0))
            error_rect = error_text.get_rect(center=(500, 350))
            self.screen.blit(error_text, error_rect)
        
        # Draw design info
        self.draw_design_info(design)
        
        # Draw navigation
        self.draw_navigation()
        
        # Draw status
        self.draw_status()
        
        # Draw statistics
        self.draw_statistics()
    
    def draw_design_info(self, design):
        """Draw design information panel"""
        # Create info panel background
        panel_rect = pygame.Rect(750, 50, 230, 400)
        pygame.draw.rect(self.screen, (255, 255, 255), panel_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), panel_rect, 2)
        
        # Title
        title_text = self.font.render("Design Information", True, (0, 0, 0))
        self.screen.blit(title_text, (760, 60))
        
        genetics = design.genetics
        y_offset = 90
        
        # Key visual traits
        info_lines = [
            f"Design: {design.id}",
            f"Status: {design.voting_status.title()}",
            "",
            "=== Genetic Traits ===",
            f"Shell: RGB{genetics['shell_base_color']}",
            f"Body: RGB{genetics['body_base_color']}",
            f"Shell Pattern: {genetics['shell_pattern_type'].title()}",
            f"Body Pattern: {genetics['body_pattern_type'].title()}",
            f"Eyes: RGB{genetics['eye_color']}",
            f"Head: RGB{genetics['head_color']}",
            f"Legs: RGB{genetics['leg_color']}",
            "",
            "=== Size Modifiers ===",
            f"Shell: {genetics['shell_size_modifier']:.2f}",
            f"Head: {genetics['head_size_modifier']:.2f}",
            f"Eyes: {genetics['eye_size_modifier']:.2f}",
            f"Leg Length: {genetics['leg_length_modifier']:.2f}",
            f"Leg Thickness: {genetics['leg_thickness_modifier']:.2f}"
        ]
        
        for line in info_lines:
            if line.startswith("==="):
                text = self.font.render(line, True, (0, 0, 0))
            else:
                text = self.small_font.render(line, True, (50, 50, 50))
            self.screen.blit(text, (760, y_offset))
            y_offset += 20 if line.startswith("===") else 18
    
    def draw_navigation(self):
        """Draw navigation controls"""
        # Navigation background
        nav_rect = pygame.Rect(750, 470, 230, 80)
        pygame.draw.rect(self.screen, (255, 255, 255), nav_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), nav_rect, 2)
        
        # Title
        title_text = self.font.render("Controls", True, (0, 0, 0))
        self.screen.blit(title_text, (760, 480))
        
        # Navigation info
        nav_text = self.small_font.render("LEFT/RIGHT: Navigate", True, (50, 50, 50))
        self.screen.blit(nav_text, (760, 510))
        
        space_text = self.small_font.render("SPACE: Vote for Design", True, (50, 50, 50))
        self.screen.blit(space_text, (760, 530))
        
        esc_text = self.small_font.render("ESC: Exit Demo", True, (50, 50, 50))
        self.screen.blit(esc_text, (760, 550))
    
    def draw_status(self):
        """Draw status panel"""
        # Status background
        status_rect = pygame.Rect(20, 20, 200, 60)
        pygame.draw.rect(self.screen, (255, 255, 255), status_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), status_rect, 2)
        
        # Current design
        design_text = self.font.render(f"Design {self.current_design_index + 1}/{len(self.designs)}", True, (0, 0, 0))
        self.screen.blit(design_text, (30, 30))
        
        # Vote status
        if self.designs and self.current_design_index < len(self.designs):
            design = self.designs[self.current_design_index]
            status = "Already Voted" if design.voting_status == 'completed' else "Ready to Vote"
            color = (100, 100, 100) if design.voting_status == 'completed' else (0, 128, 0)
            status_text = self.small_font.render(status, True, color)
            self.screen.blit(status_text, (30, 55))
    
    def draw_statistics(self):
        """Draw statistics panel"""
        # Statistics background
        stats_rect = pygame.Rect(20, 620, 960, 60)
        pygame.draw.rect(self.screen, (255, 255, 255), stats_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), stats_rect, 2)
        
        # Get statistics
        status = self.voting_system.get_daily_status()
        pool_stats = self.pool_manager.get_genetic_pool_status()
        
        # Create stats text
        stats_text = f"Votes: {status['completed_votes']}/{status['total_designs']} | "
        stats_text += f"Potential Earnings: ${status['potential_earnings']} | "
        stats_text += f"Pool Influence: {pool_stats['average_weight']:.2f}"
        
        if pool_stats['most_influenced_traits']:
            traits = pool_stats['most_influenced_traits']
            if traits and isinstance(traits[0], tuple):
                trait_names = [trait[0] for trait in traits[:3]]
            else:
                trait_names = traits[:3]
            stats_text += f" | Top Traits: {', '.join(trait_names)}"
        
        # Render stats
        text_surface = self.small_font.render(stats_text, True, (0, 0, 0))
        self.screen.blit(text_surface, (30, 640))
    
    def vote_for_design(self):
        """Vote for the current design"""
        if not self.designs or self.current_design_index >= len(self.designs):
            return
        
        design = self.designs[self.current_design_index]
        
        if design.voting_status == 'completed':
            print(f"Already voted for Design {self.current_design_index + 1}")
            return
        
        # Generate automatic ratings for demo
        ratings = {
            'overall': 3.0 + (self.current_design_index * 0.5),
            'shell_appearance': 3.5,
            'color_harmony': 4.0,
            'pattern_quality': 3.0,
            'proportions': 4.0
        }
        
        # Submit vote
        result = self.voting_system.submit_ratings(design.id, ratings)
        
        if result['success']:
            print(f"Successfully voted for Design {self.current_design_index + 1}!")
            print(f"Earned ${result['reward_earned']}")
            print("Your ratings influenced future turtle genetics!")
            
            # Update display
            design.voting_status = 'completed'
            self.display_current_design()
            
            # Check if all designs are voted
            status = self.voting_system.get_daily_status()
            if status['completed_votes'] == status['total_designs']:
                self.demo_complete = True
                print(f"Demo Complete! Total earned: ${status['potential_earnings']}")
        else:
            print(f"Failed to submit vote: {result.get('error', 'Unknown error')}")
    
    def prev_design(self):
        """Navigate to previous design"""
        if self.designs:
            self.current_design_index = (self.current_design_index - 1) % len(self.designs)
            self.display_current_design()
    
    def next_design(self):
        """Navigate to next design"""
        if self.designs:
            self.current_design_index = (self.current_design_index + 1) % len(self.designs)
            self.display_current_design()
    
    def run(self):
        """Start the demo"""
        print("=== TurboShells Visual Genetics System Demo (Working) ===")
        print()
        print("Use LEFT/RIGHT arrows to navigate, SPACE to vote, ESC to exit")
        print()
        
        # Show renderer capabilities
        capabilities = self.renderer.get_rendering_capabilities()
        print(f"Renderer: {capabilities['renderer_type']}")
        print(f"Can render SVG: {capabilities['can_render_svg']}")
        print(f"Direct SVG parsing: {'Yes' if capabilities['renderer_type'] == 'direct' else 'No'}")
        print()
        
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_LEFT:
                        self.prev_design()
                    elif event.key == pygame.K_RIGHT:
                        self.next_design()
                    elif event.key == pygame.K_SPACE:
                        self.vote_for_design()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        print("Demo completed!")


def main():
    """Run the working visual genetics demonstration"""
    try:
        demo = WorkingVisualGeneticsDemo()
        demo.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
