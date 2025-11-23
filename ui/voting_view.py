"""
Voting View for TurboShells
Complete voting interface for design evaluation with PyGame integration
"""

import pygame
import math
import io
from typing import Dict, Any, Optional, List, Tuple
from PIL import Image
from core.voting.voting_system import VotingSystem, DesignPackage
from core.rendering.direct_turtle_renderer import get_direct_renderer


class VotingView:
    """
    Complete voting interface for design evaluation
    Handles all UI components, user interactions, and feedback display
    """
    
    def __init__(self, screen: pygame.Surface, game_state):
        self.screen = screen
        self.game_state = game_state
        self.voting_system = VotingSystem()
        self.turtle_renderer = get_direct_renderer()
        
        # Helper method to convert PIL to PyGame
        self._pil_to_pygame = lambda pil_image: pygame.image.fromstring(
            pil_image.tobytes(), pil_image.size, pil_image.mode
        ) if pil_image else None
        
        # UI state
        self.current_design_index = 0
        self.selected_ratings = {}
        self.show_feedback = False
        self.current_feedback = None
        self.feedback_timer = 0
        
        # UI layout
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.design_size = min(200, self.width // 3)  # Larger design size for left column
        
        # Layout dimensions
        self.left_panel_width = self.width // 2
        self.right_panel_width = self.width - self.left_panel_width
        self.image_x = (self.left_panel_width - self.design_size) // 2
        self.image_y = 150
        
        # Colors
        self.bg_color = (240, 248, 255)  # Alice blue
        self.card_color = (255, 255, 255)
        self.text_color = (0, 0, 0)
        self.accent_color = (70, 130, 180)  # Steel blue
        self.star_color = (255, 215, 0)  # Gold
        self.star_empty_color = (200, 200, 200)  # Light gray
        self.star_hover_color = (255, 255, 100)  # Light yellow
        self.success_color = (34, 139, 34)  # Forest green
        self.button_color = (100, 150, 200)
        self.button_hover_color = (120, 170, 220)
        
        # Fonts
        try:
            self.title_font = pygame.font.Font(None, 36)
            self.header_font = pygame.font.Font(None, 24)
            self.normal_font = pygame.font.Font(None, 18)
            self.small_font = pygame.font.Font(None, 14)
        except:
            # Fallback to default font
            self.title_font = pygame.font.SysFont('Arial', 36)
            self.header_font = pygame.font.SysFont('Arial', 24)
            self.normal_font = pygame.font.SysFont('Arial', 18)
            self.small_font = pygame.font.SysFont('Arial', 14)
        
        # Initialize daily designs
        self.voting_system.generate_daily_designs()
        
        # Mouse state
        self.mouse_pos = (0, 0)
        self.mouse_clicked = False
        
        # Animation state
        self.animation_timer = 0
        self.pulse_phase = 0
    
    def draw(self):
        """Draw the complete voting interface with left-right layout"""
        # Update animations
        self._update_animations()
        
        # Draw background
        self.screen.fill(self.bg_color)
        
        # Draw left panel (turtle image)
        self._draw_left_panel()
        
        # Draw right panel (voting controls)
        self._draw_right_panel()
        
        # Draw feedback if active
        if self.show_feedback and self.current_feedback:
            self._draw_feedback()
    
    def _draw_left_panel(self):
        """Draw left panel with turtle image and navigation"""
        designs = self.voting_system.daily_designs
        
        if not designs or self.current_design_index >= len(designs):
            return
        
        current_design = designs[self.current_design_index]
        
        # Draw panel background
        panel_rect = pygame.Rect(0, 0, self.left_panel_width, self.height)
        pygame.draw.rect(self.screen, (250, 250, 250), panel_rect)
        
        # Draw separator
        pygame.draw.line(self.screen, self.accent_color, 
                        (self.left_panel_width - 2, 0), 
                        (self.left_panel_width - 2, self.height), 3)
        
        # Draw title
        title_text = "Daily Design Voting"
        title_surface = self.title_font.render(title_text, True, self.text_color)
        title_rect = title_surface.get_rect(centerx=self.left_panel_width // 2, y=20)
        self.screen.blit(title_surface, title_rect)
        
        # Draw design info
        design_name = f"Design #{current_design.id}"
        name_surface = self.header_font.render(design_name, True, self.text_color)
        name_rect = name_surface.get_rect(centerx=self.left_panel_width // 2, y=70)
        self.screen.blit(name_surface, name_rect)
        
        # Draw turtle image
        self._draw_turtle_image(current_design, self.image_x, self.image_y)
        
        # Draw navigation controls
        self._draw_navigation_controls()
    
    def _draw_turtle_image(self, current_design, x, y):
        """Draw turtle image in the left panel"""
        # Draw card background
        card_width = self.design_size + 40
        card_height = self.design_size + 40
        card_x = x - 20
        card_y = y - 20
        
        pygame.draw.rect(self.screen, self.card_color, (card_x, card_y, card_width, card_height), border_radius=15)
        pygame.draw.rect(self.screen, self.accent_color, (card_x, card_y, card_width, card_height), 3, border_radius=15)
        
        # Draw turtle using the same rendering system as the main game
        try:
            genetics = current_design.genetics
            if genetics:
                # Use the same direct renderer as the main game
                pil_image = self.turtle_renderer.render_turtle_to_photoimage(
                    genetics, self.design_size
                )
                
                if pil_image and isinstance(pil_image, str):
                    # If it's a file path, load it
                    try:
                        turtle_surface = pygame.image.load(pil_image)
                        self.screen.blit(turtle_surface, (x, y))
                    except:
                        self._draw_placeholder_turtle(x + self.design_size // 2, y + self.design_size // 2)
                elif pil_image:
                    # Convert PIL to PyGame surface
                    try:
                        turtle_surface = self._pil_to_pygame(pil_image)
                        if turtle_surface:
                            self.screen.blit(turtle_surface, (x, y))
                        else:
                            self._draw_placeholder_turtle(x + self.design_size // 2, y + self.design_size // 2)
                    except:
                        self._draw_placeholder_turtle(x + self.design_size // 2, y + self.design_size // 2)
                else:
                    self._draw_placeholder_turtle(x + self.design_size // 2, y + self.design_size // 2)
            else:
                self._draw_placeholder_turtle(x + self.design_size // 2, y + self.design_size // 2)
                
        except Exception as e:
            print(f"Error rendering turtle: {e}")
            self._draw_placeholder_turtle(x + self.design_size // 2, y + self.design_size // 2)
    
    def _draw_navigation_controls(self):
        """Draw navigation controls in left panel"""
        designs = self.voting_system.daily_designs
        
        # Navigation buttons
        nav_y = self.image_y + self.design_size + 80
        
        # Previous button
        if self.current_design_index > 0:
            self._draw_nav_button("<", self.left_panel_width // 2 - 80, nav_y, "previous")
        
        # Next button
        if self.current_design_index < len(designs) - 1:
            self._draw_nav_button(">", self.left_panel_width // 2 + 40, nav_y, "next")
        
        # Design counter
        counter_text = f"Design {self.current_design_index + 1} of {len(designs)}"
        text_surface = self.normal_font.render(counter_text, True, self.text_color)
        text_rect = text_surface.get_rect(centerx=self.left_panel_width // 2, y=nav_y + 10)
        self.screen.blit(text_surface, text_rect)
        
        # Progress bar
        progress = (self.current_design_index + 1) / len(designs)
        bar_width = 200
        bar_height = 8
        bar_x = (self.left_panel_width - bar_width) // 2
        bar_y = nav_y + 50
        
        # Background
        pygame.draw.rect(self.screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), border_radius=4)
        # Progress
        pygame.draw.rect(self.screen, self.accent_color, (bar_x, bar_y, int(bar_width * progress), bar_height), border_radius=4)
    
    def _update_animations(self):
        """Update animation states"""
        self.animation_timer += 1
        self.pulse_phase = (self.animation_timer * 0.05) % (2 * math.pi)
        
        # Update feedback timer
        if self.show_feedback and self.feedback_timer > 0:
            self.feedback_timer -= 1
            if self.feedback_timer <= 0:
                self.show_feedback = False
                self.current_feedback = None
    
    def _draw_right_panel(self):
        """Draw right panel with voting controls"""
        designs = self.voting_system.daily_designs
        
        if not designs or self.current_design_index >= len(designs):
            return
        
        current_design = designs[self.current_design_index]
        
        # Draw panel background
        panel_rect = pygame.Rect(self.left_panel_width, 0, self.right_panel_width, self.height)
        pygame.draw.rect(self.screen, self.bg_color, panel_rect)
        
        # Draw voting title
        voting_title = "Rate This Design"
        title_surface = self.header_font.render(voting_title, True, self.text_color)
        title_rect = title_surface.get_rect(centerx=self.left_panel_width + self.right_panel_width // 2, y=20)
        self.screen.blit(title_surface, title_rect)
        
        # Draw subtitle
        subtitle_text = "Rate each category to earn $1 and influence genetics!"
        subtitle_surface = self.normal_font.render(subtitle_text, True, (100, 100, 100))
        subtitle_rect = subtitle_surface.get_rect(centerx=self.left_panel_width + self.right_panel_width // 2, y=55)
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Draw voting controls
        if current_design.voting_status == 'completed':
            self._draw_completed_ratings(current_design)
        else:
            self._draw_rating_controls()
        
        # Draw submit button if ratings are complete
        if self._can_submit_ratings():
            self._draw_submit_button()
    
    def _draw_rating_controls(self):
        """Draw rating controls in right panel"""
        designs = self.voting_system.daily_designs
        
        if not designs or self.current_design_index >= len(designs):
            return
        
        current_design = designs[self.current_design_index]
        
        if current_design.voting_status == 'completed':
            self._draw_completed_ratings(current_design)
            return
        
        categories = current_design.rating_categories
        
        # Rating controls area (right panel)
        controls_x = self.left_panel_width + 30
        controls_y = 120
        controls_width = self.right_panel_width - 60
        
        # Draw category names and star ratings
        y_offset = 0
        for category_name, category_data in categories.items():
            # Category name
            category_text = category_data['display_name']
            text_surface = self.normal_font.render(category_text, True, self.text_color)
            self.screen.blit(text_surface, (controls_x, controls_y + y_offset))
            
            # Draw description
            desc_text = category_data['description']
            desc_surface = self.small_font.render(desc_text, True, (100, 100, 100))
            self.screen.blit(desc_surface, (controls_x, controls_y + y_offset + 25))
            
            # Draw stars (more space in right panel)
            star_rating = self.selected_ratings.get(category_name, 0)
            self._draw_star_rating(controls_x, controls_y + y_offset + 55, 
                                  star_rating, category_name, controls_width)
            
            y_offset += 120
        
        # Draw submit button if ratings are complete
        if self._can_submit_ratings():
            self._draw_submit_button()
    
    def _draw_header(self):
        """Draw voting interface header"""
        # Title
        title_text = "Daily Design Voting"
        title_surface = self.title_font.render(title_text, True, self.text_color)
        title_rect = title_surface.get_rect(centerx=self.width // 2, y=20)
        self.screen.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle_text = "Rate designs to earn $1 and influence future turtle genetics!"
        subtitle_surface = self.normal_font.render(subtitle_text, True, self.text_color)
        subtitle_rect = subtitle_surface.get_rect(centerx=self.width // 2, y=60)
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Draw separator line
        pygame.draw.line(self.screen, self.accent_color, 
                        (50, 90), (self.width - 50, 90), 2)
    
    def _draw_current_design(self):
        """Draw the current design for voting"""
        designs = self.voting_system.daily_designs
        
        if not designs or self.current_design_index >= len(designs):
            return
        
        current_design = designs[self.current_design_index]
        
        # Design card background
        card_x = (self.width - self.design_size * 2.2) // 2
        card_y = 110
        card_width = self.design_size * 2.2
        card_height = self.design_size * 2.8
        
        # Draw card shadow
        shadow_rect = pygame.Rect(card_x + 5, card_y + 5, card_width, card_height)
        pygame.draw.rect(self.screen, (200, 200, 200), shadow_rect, border_radius=10)
        
        # Draw card background
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        pygame.draw.rect(self.screen, self.card_color, card_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.accent_color, card_rect, 3, border_radius=10)
        
        # Draw turtle using the same rendering system as the main game
        try:
            genetics = current_design.genetics
            if genetics:
                # Use the same direct renderer as the main game
                pil_image = self.turtle_renderer.render_turtle_to_photoimage(
                    genetics, self.design_size
                )
                
                if pil_image and isinstance(pil_image, str):
                    # If it's a file path, load it
                    try:
                        turtle_surface = pygame.image.load(pil_image)
                        # Center the turtle in the card
                        turtle_x = card_x + (card_width - self.design_size) // 2
                        turtle_y = card_y + 30
                        self.screen.blit(turtle_surface, (turtle_x, turtle_y))
                    except:
                        self._draw_placeholder_turtle(card_x + card_width // 2, card_y + 80)
                elif pil_image:
                    # Convert PIL to PyGame surface
                    try:
                        turtle_surface = self._pil_to_pygame(pil_image)
                        if turtle_surface:
                            # Center the turtle in the card
                            turtle_x = card_x + (card_width - self.design_size) // 2
                            turtle_y = card_y + 30
                            self.screen.blit(turtle_surface, (turtle_x, turtle_y))
                        else:
                            self._draw_placeholder_turtle(card_x + card_width // 2, card_y + 80)
                    except:
                        self._draw_placeholder_turtle(card_x + card_width // 2, card_y + 80)
                else:
                    self._draw_placeholder_turtle(card_x + card_width // 2, card_y + 80)
            else:
                self._draw_placeholder_turtle(card_x + card_width // 2, card_y + 80)
                
        except Exception as e:
            print(f"Error rendering turtle: {e}")
            self._draw_placeholder_turtle(card_x + card_width // 2, card_y + 80)
        
        # Draw feature breakdown
        self._draw_feature_breakdown(current_design, card_x + 20, card_y + self.design_size + 50)
        
        # Draw design status
        if current_design.voting_status == 'completed':
            status_text = "✓ VOTED"
            status_color = self.success_color
        else:
            status_text = "PENDING VOTE"
            status_color = self.accent_color
        
        status_surface = self.normal_font.render(status_text, True, status_color)
        status_rect = status_surface.get_rect(right=card_x + card_width - 20, top=card_y + 10)
        self.screen.blit(status_surface, status_rect)
    
    def _draw_placeholder_turtle(self, x: int, y: int):
        """Draw placeholder turtle when SVG fails"""
        # Draw simple turtle shape
        # Shell
        pygame.draw.ellipse(self.screen, (34, 139, 34), 
                           (x - 40, y - 30, 80, 60))
        pygame.draw.ellipse(self.screen, (0, 100, 0), 
                           (x - 40, y - 30, 80, 60), 2)
        
        # Head
        pygame.draw.circle(self.screen, (139, 90, 43), (x, y - 50), 15)
        pygame.draw.circle(self.screen, (100, 60, 20), (x, y - 50), 15, 2)
        
        # Legs
        leg_positions = [(-25, 10), (25, 10), (-20, 25), (20, 25)]
        for leg_x, leg_y in leg_positions:
            pygame.draw.line(self.screen, (101, 67, 33), 
                           (x + leg_x, y + leg_y), 
                           (x + leg_x, y + leg_y + 20), 3)
        
        # Eyes
        pygame.draw.circle(self.screen, (0, 0, 0), (x - 5, y - 50), 2)
        pygame.draw.circle(self.screen, (0, 0, 0), (x + 5, y - 50), 2)
    
    def _draw_feature_breakdown(self, design: DesignPackage, x: int, y: int):
        """Draw feature breakdown for the design"""
        features = design.feature_breakdown
        
        y_offset = 0
        for feature_name, feature_data in features.items():
            # Feature name
            feature_text = f"{feature_data['display_name']}:"
            text_surface = self.small_font.render(feature_text, True, self.text_color)
            self.screen.blit(text_surface, (x, y + y_offset))
            
            # Feature value
            if feature_data['type'] == 'color':
                # Draw color swatch
                rgb = feature_data['value']
                pygame.draw.rect(self.screen, rgb, (x + 120, y + y_offset, 25, 15))
                pygame.draw.rect(self.screen, self.text_color, (x + 120, y + y_offset, 25, 15), 1)
                
                # Draw RGB values
                rgb_text = f"RGB({rgb[0]},{rgb[1]},{rgb[2]})"
                rgb_surface = self.small_font.render(rgb_text, True, self.text_color)
                self.screen.blit(rgb_surface, (x + 150, y + y_offset))
                
            elif feature_data['type'] == 'pattern':
                pattern_text = feature_data['value'].title()
                text_surface = self.small_font.render(pattern_text, True, self.text_color)
                self.screen.blit(text_surface, (x + 120, y + y_offset))
                
            elif feature_data['type'] == 'proportions':
                prop_data = feature_data['value']
                prop_text = f"S:{prop_data['shell_size']:.1f} H:{prop_data['head_size']:.1f} L:{prop_data['leg_length']:.1f}"
                text_surface = self.small_font.render(prop_text, True, self.text_color)
                self.screen.blit(text_surface, (x + 120, y + y_offset))
            
            y_offset += 22
    
    def _draw_rating_controls(self):
        """Draw rating controls for current design"""
        designs = self.voting_system.daily_designs
        
        if not designs or self.current_design_index >= len(designs):
            return
        
        current_design = designs[self.current_design_index]
        
        if current_design.voting_status == 'completed':
            self._draw_completed_ratings(current_design)
            return
        
        categories = current_design.rating_categories
        
        # Rating controls area
        controls_x = 50
        controls_y = 420
        controls_width = self.width - 100
        
        # Draw category names and star ratings
        y_offset = 0
        for category_name, category_data in categories.items():
            # Category name
            category_text = category_data['display_name']
            text_surface = self.normal_font.render(category_text, True, self.text_color)
            self.screen.blit(text_surface, (controls_x, controls_y + y_offset))
            
            # Draw description
            desc_text = category_data['description']
            desc_surface = self.small_font.render(desc_text, True, (100, 100, 100))
            self.screen.blit(desc_surface, (controls_x, controls_y + y_offset + 20))
            
            # Draw stars
            star_rating = self.selected_ratings.get(category_name, 0)
            self._draw_star_rating(controls_x + 200, controls_y + y_offset, 
                                  star_rating, category_name)
            
            y_offset += 55
        
        # Draw submit button if ratings are complete
        if self._can_submit_ratings():
            self._draw_submit_button()
    
    def _draw_completed_ratings(self, design: DesignPackage):
        """Draw completed ratings display"""
        if not design.ratings:
            return
        
        controls_x = 50
        controls_y = 420
        
        # Title
        title_text = "Your Ratings:"
        title_surface = self.header_font.render(title_text, True, self.success_color)
        self.screen.blit(title_surface, (controls_x, controls_y))
        
        # Display ratings
        y_offset = 40
        for category_name, rating in design.ratings.items():
            category_data = design.rating_categories.get(category_name, {})
            category_text = category_data.get('display_name', category_name)
            
            # Category name
            text_surface = self.normal_font.render(category_text, True, self.text_color)
            self.screen.blit(text_surface, (controls_x, controls_y + y_offset))
            
            # Stars
            self._draw_star_rating(controls_x + 200, controls_y + y_offset, rating, category_name, interactive=False)
            
            # Rating value
            rating_text = f"{rating:.1f}/5.0"
            rating_surface = self.normal_font.render(rating_text, True, self.text_color)
            self.screen.blit(rating_surface, (controls_x + 350, controls_y + y_offset))
            
            y_offset += 30
    
    def _draw_star_rating(self, x: int, y: int, rating: float, category_name: str, interactive: bool = True):
        """Draw interactive star rating"""
        star_size = 20
        star_spacing = 25
        
        for i in range(5):
            star_x = x + i * star_spacing
            star_y = y
            
            # Check if mouse is over this star
            is_hovered = False
            if interactive:
                is_hovered = (star_x <= self.mouse_pos[0] <= star_x + star_size and 
                             star_y <= self.mouse_pos[1] <= star_y + star_size)
            
            # Determine star color
            if i < rating:
                star_color = self.star_color
            elif is_hovered and interactive:
                star_color = self.star_hover_color
            else:
                star_color = self.star_empty_color
            
            # Draw star
            self._draw_star(star_x, star_y, star_size, star_color)
    
    def _draw_star(self, x: int, y: int, size: int, color: Tuple[int, int, int]):
        """Draw a star shape"""
        points = []
        for i in range(10):
            angle = math.pi * i / 5
            if i % 2 == 0:
                radius = size
            else:
                radius = size * 0.5
            
            point_x = x + radius * math.cos(angle - math.pi / 2)
            point_y = y + radius * math.sin(angle - math.pi / 2)
            points.append((point_x, point_y))
        
        pygame.draw.polygon(self.screen, color, points)
    
    def _draw_submit_button(self):
        """Draw submit ratings button in right panel"""
        button_x = self.left_panel_width + (self.right_panel_width - 200) // 2
        button_y = self.height - 80
        button_width = 200
        button_height = 50
        
        # Check if mouse is over button
        is_hovered = (button_x <= self.mouse_pos[0] <= button_x + button_width and
                     button_y <= self.mouse_pos[1] <= button_y + button_height)
        
        # Button color with pulse effect
        pulse_factor = 0.1 * math.sin(self.pulse_phase)
        base_color = self.button_color if not is_hovered else self.button_hover_color
        button_color = tuple(min(255, int(c + c * pulse_factor)) for c in base_color)
        
        # Draw button
        pygame.draw.rect(self.screen, button_color, 
                        (button_x, button_y, button_width, button_height), border_radius=8)
        pygame.draw.rect(self.screen, self.text_color, 
                        (button_x, button_y, button_width, button_height), 2, border_radius=8)
        
        # Button text
        button_text = "Submit & Earn $1"
        text_surface = self.normal_font.render(button_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(centerx=button_x + button_width // 2, 
                                         centery=button_y + button_height // 2)
        self.screen.blit(text_surface, text_rect)
    
    def _draw_navigation(self):
        """Draw navigation controls"""
        designs = self.voting_system.daily_designs
        
        # Previous button
        if self.current_design_index > 0:
            self._draw_nav_button("<", 50, 350, "previous")
        
        # Next button
        if self.current_design_index < len(designs) - 1:
            self._draw_nav_button(">", self.width - 90, 350, "next")
        
        # Design counter
        counter_text = f"Design {self.current_design_index + 1} of {len(designs)}"
        text_surface = self.normal_font.render(counter_text, True, self.text_color)
        text_rect = text_surface.get_rect(centerx=self.width // 2, y=350)
        self.screen.blit(text_surface, text_rect)
        
        # Progress bar
        progress = (self.current_design_index + 1) / len(designs)
        bar_width = 200
        bar_height = 8
        bar_x = (self.width - bar_width) // 2
        bar_y = 375
        
        # Background
        pygame.draw.rect(self.screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), border_radius=4)
        # Progress
        pygame.draw.rect(self.screen, self.accent_color, (bar_x, bar_y, int(bar_width * progress), bar_height), border_radius=4)
    
    def _draw_nav_button(self, text: str, x: int, y: int, action: str):
        """Draw navigation button"""
        button_width = 40
        button_height = 30
        
        # Check if mouse is over button
        is_hovered = (x <= self.mouse_pos[0] <= x + button_width and
                     y <= self.mouse_pos[1] <= y + button_height)
        
        # Button color
        button_color = (150, 150, 150) if is_hovered else (100, 100, 100)
        
        # Draw button
        pygame.draw.rect(self.screen, button_color, (x, y, button_width, button_height), border_radius=5)
        pygame.draw.rect(self.screen, self.text_color, (x, y, button_width, button_height), 1, border_radius=5)
        
        # Button text
        text_surface = self.normal_font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(centerx=x + button_width // 2,
                                         centery=y + button_height // 2)
        self.screen.blit(text_surface, text_rect)
    
    def _draw_status(self):
        """Draw voting status information"""
        status = self.voting_system.get_daily_status()
        
        # Status panel
        panel_x = 50
        panel_y = self.height - 80
        panel_width = self.width - 100
        panel_height = 60
        
        # Draw panel background
        pygame.draw.rect(self.screen, self.card_color, (panel_x, panel_y, panel_width, panel_height), border_radius=5)
        pygame.draw.rect(self.screen, self.accent_color, (panel_x, panel_y, panel_width, panel_height), 2, border_radius=5)
        
        # Status text
        status_text = f"Completed: {status['completed_votes']}/{status['total_designs']} | " \
                     f"Available Rewards: ${status['potential_earnings']}"
        text_surface = self.normal_font.render(status_text, True, self.text_color)
        text_rect = text_surface.get_rect(centerx=self.width // 2, y=panel_y + 10)
        self.screen.blit(text_surface, text_rect)
        
        # Progress text
        progress_text = f"Progress: {status['completion_percentage']:.1f}%"
        progress_surface = self.small_font.render(progress_text, True, self.text_color)
        progress_rect = progress_surface.get_rect(centerx=self.width // 2, y=panel_y + 35)
        self.screen.blit(progress_surface, progress_rect)
    
    def _draw_feedback(self):
        """Draw feedback popup"""
        if not self.current_feedback:
            return
        
        # Popup background with fade effect
        popup_alpha = min(255, self.feedback_timer * 10)
        popup_x = (self.width - 400) // 2
        popup_y = (self.height - 200) // 2
        popup_width = 400
        popup_height = 200
        
        # Create semi-transparent surface
        popup_surface = pygame.Surface((popup_width, popup_height))
        popup_surface.set_alpha(popup_alpha)
        popup_surface.fill(self.card_color)
        
        # Draw popup
        self.screen.blit(popup_surface, (popup_x, popup_y))
        pygame.draw.rect(self.screen, self.accent_color, 
                        (popup_x, popup_y, popup_width, popup_height), 3, border_radius=10)
        
        # Feedback title
        title_text = "Rating Submitted!"
        title_surface = self.header_font.render(title_text, True, self.success_color)
        title_rect = title_surface.get_rect(centerx=popup_x + popup_width // 2, y=popup_y + 20)
        self.screen.blit(title_surface, title_rect)
        
        # Reward message
        reward_text = f"You earned ${self.current_feedback['reward_earned']}!"
        reward_surface = self.normal_font.render(reward_text, True, self.text_color)
        reward_rect = reward_surface.get_rect(centerx=popup_x + popup_width // 2, y=popup_y + 60)
        self.screen.blit(reward_surface, reward_rect)
        
        # Impact message
        impact_text = "Your ratings will influence future turtle genetics!"
        impact_surface = self.normal_font.render(impact_text, True, self.text_color)
        impact_rect = impact_surface.get_rect(centerx=popup_x + popup_width // 2, y=popup_y + 90)
        self.screen.blit(impact_surface, impact_rect)
        
        # Close instruction
        close_text = "Click to continue"
        close_surface = self.small_font.render(close_text, True, self.accent_color)
        close_rect = close_surface.get_rect(centerx=popup_x + popup_width // 2, y=popup_y + 150)
        self.screen.blit(close_surface, close_rect)
    
    def handle_event(self, event: pygame.event.Event) -> str:
        """Handle pygame events"""
        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.mouse_clicked = True
                self._handle_click(event.pos)
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.mouse_clicked = False
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "menu"
            elif event.key == pygame.K_LEFT:
                self._navigate_previous()
            elif event.key == pygame.K_RIGHT:
                self._navigate_next()
        
        return "voting"
    
    def _handle_click(self, pos: Tuple[int, int]):
        """Handle mouse click"""
        x, y = pos
        
        # Check feedback popup
        if self.show_feedback:
            self.show_feedback = False
            self.current_feedback = None
            self.feedback_timer = 0
            return
        
        designs = self.voting_system.daily_designs
        
        if not designs or self.current_design_index >= len(designs):
            return
        
        current_design = designs[self.current_design_index]
        
        # Check star ratings
        if current_design.voting_status == 'pending':
            categories = current_design.rating_categories
            controls_x = 50
            controls_y = 420
            
            y_offset = 0
            for category_name in categories:
                star_y = controls_y + y_offset
                
                for i in range(5):
                    star_x = controls_x + 200 + i * 25
                    
                    if (star_x <= x <= star_x + 20 and star_y <= y <= star_y + 20):
                        # Set rating for this category
                        self.selected_ratings[category_name] = i + 1
                        return
                
                y_offset += 55
        
        # Check submit button
        if self._can_submit_ratings():
            button_x = (self.width - 180) // 2
            button_y = 580
            button_width = 180
            button_height = 40
            
            if (button_x <= x <= button_x + button_width and
                button_y <= y <= button_y + button_height):
                self._submit_ratings()
                return
        
        # Check navigation
        if x >= 50 and x <= 90 and y >= 350 and y <= 380:
            # Previous button
            self._navigate_previous()
        
        if x >= self.width - 90 and x <= self.width - 50 and y >= 350 and y <= 380:
            # Next button
            self._navigate_next()
    
    def _navigate_previous(self):
        """Navigate to previous design"""
        if self.current_design_index > 0:
            self.current_design_index -= 1
            self.selected_ratings = {}
    
    def _navigate_next(self):
        """Navigate to next design"""
        designs = self.voting_system.daily_designs
        if self.current_design_index < len(designs) - 1:
            self.current_design_index += 1
            self.selected_ratings = {}
    
    def _can_submit_ratings(self) -> bool:
        """Check if ratings can be submitted"""
        designs = self.voting_system.daily_designs
        
        if not designs or self.current_design_index >= len(designs):
            return False
        
        current_design = designs[self.current_design_index]
        return current_design.voting_status == 'pending' and len(self.selected_ratings) > 0
    
    def _submit_ratings(self):
        """Submit current ratings"""
        designs = self.voting_system.daily_designs
        
        if not designs or self.current_design_index >= len(designs):
            return
        
        current_design = designs[self.current_design_index]
        
        # Submit ratings
        result = self.voting_system.submit_ratings(current_design.id, self.selected_ratings)
        
        if result['success']:
            self.current_feedback = result
            self.show_feedback = True
            self.feedback_timer = 180  # 3 seconds at 60 FPS
            self.selected_ratings = {}
            
            # Auto-advance to next design
            designs = self.voting_system.daily_designs
            if self.current_design_index < len(designs) - 1:
                self.current_design_index += 1
    
    def update(self):
        """Update voting view state"""
        # Generate daily designs if needed
        self.voting_system.generate_daily_designs()
        
        # Validate current design index
        designs = self.voting_system.daily_designs
        if self.current_design_index >= len(designs):
            self.current_design_index = max(0, len(designs) - 1)
    
    def get_voting_data(self) -> Dict[str, Any]:
        """Get current voting data for external use"""
        return {
            'current_design_index': self.current_design_index,
            'selected_ratings': self.selected_ratings.copy(),
            'daily_status': self.voting_system.get_daily_status(),
            'can_submit': self._can_submit_ratings()
        }
    
    def handle_click(self, pos):
        """Handle mouse clicks in the voting interface"""
        x, y = pos
        
        # Check submit button (matching new right panel position)
        if self._can_submit_ratings():
            button_x = self.left_panel_width + (self.right_panel_width - 200) // 2
            button_y = self.height - 80
            submit_rect = pygame.Rect(button_x, button_y, 200, 50)
            if submit_rect.collidepoint(pos):
                result = self._submit_ratings()
                if result:
                    return "vote_completed"
        
        # Check navigation buttons (matching new left panel positions)
        if self.current_design_index > 0:
            nav_y = self.image_y + self.design_size + 80
            prev_rect = pygame.Rect(self.left_panel_width // 2 - 80, nav_y, 40, 40)
            if prev_rect.collidepoint(pos):
                self.current_design_index -= 1
                return None
        
        designs = self.voting_system.daily_designs
        if self.current_design_index < len(designs) - 1:
            nav_y = self.image_y + self.design_size + 80
            next_rect = pygame.Rect(self.left_panel_width // 2 + 40, nav_y, 40, 40)
            if next_rect.collidepoint(pos):
                self.current_design_index += 1
                return None
        
        # Check rating stars (matching new right panel positions)
        current_design = designs[self.current_design_index]
        if current_design.voting_status != 'completed':
            controls_x = self.left_panel_width + 30
            controls_y = 120
            y_offset = 0
            categories = current_design.rating_categories
            for category_name, category_data in categories.items():
                star_x = controls_x
                star_y = controls_y + y_offset + 55
                for star in range(1, 6):
                    star_rect = pygame.Rect(star_x + (star - 1) * 45, star_y, 35, 35)  # Larger spacing
                    if star_rect.collidepoint(pos):
                        self.selected_ratings[category_name] = star
                        return None
                y_offset += 120
        
        return None
