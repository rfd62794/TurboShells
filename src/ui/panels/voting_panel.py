"""
Voting Panel for TurboShells

Modern pygame_gui implementation of the voting interface.
"""

import pygame
import pygame_gui
import math
from typing import Dict, Any, Optional, List, Tuple
from ui.panels.base_panel import BasePanel
from core.rendering.pygame_turtle_renderer import render_turtle_pygame


class VotingPanel(BasePanel):
    """Voting interface panel using pygame_gui components."""
    
    def __init__(self, game_state_interface):
        super().__init__("voting", "Daily Design Voting")
        
        self.game_state = game_state_interface
        
        # Set default size and position to fit within game window
        self.size = (800, 550)
        self.position = (100, 75)
        
        # Voting state
        self.current_design_index = 0
        self.selected_ratings = {}
        self.show_feedback = False
        self.feedback_timer = 0
        
        # Mock voting system data (simplified)
        self.daily_designs = self._generate_mock_designs()
        
        # UI elements
        self.btn_back = None
        self.btn_previous = None
        self.btn_next = None
        self.btn_submit = None
        self.rating_buttons = {}
        self.design_info_label = None
        self.progress_label = None
        self.design_container = None
        self.voting_container = None
        
    def _generate_mock_designs(self) -> List[Dict]:
        """Generate mock design data for testing."""
        designs = []
        for i in range(5):
            design = {
                'id': i + 1,
                'name': f'Design #{i + 1}',
                'voting_status': 'pending' if i > 0 else 'pending',
                'ratings': {},
                'rating_categories': {
                    'appearance': {
                        'display_name': 'Appearance',
                        'description': 'Visual appeal and aesthetics'
                    },
                    'functionality': {
                        'display_name': 'Functionality',
                        'description': 'Practical design and usability'
                    },
                    'creativity': {
                        'display_name': 'Creativity',
                        'description': 'Originality and innovation'
                    },
                    'balance': {
                        'display_name': 'Balance',
                        'description': 'Overall proportion and harmony'
                    }
                }
            }
            designs.append(design)
        return designs
        
    def _create_window(self) -> None:
        """Create the voting window with left-right layout matching original."""
        super()._create_window()
        
        if not self.window:
            return
            
        container = self.window.get_container()
        width = self.size[0] - 40
        y_pos = 10
        
        # Header
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_pos), (width, 30)),
            text="Daily Design Voting",
            manager=self.manager,
            container=container
        )
        
        # Back button
        self.btn_back = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width - 80, y_pos), (70, 30)),
            text="BACK",
            manager=self.manager,
            container=container
        )
        y_pos += 40
        
        # Subtitle
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_pos), (width, 25)),
            text="Rate each category to earn $1 and influence genetics!",
            manager=self.manager,
            container=container
        )
        y_pos += 35
        
        # Navigation controls
        nav_center_x = width // 2
        
        self.btn_previous = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((nav_center_x - 100, y_pos), (40, 30)),
            text="<",
            manager=self.manager,
            container=container
        )
        
        self.btn_next = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((nav_center_x + 60, y_pos), (40, 30)),
            text=">",
            manager=self.manager,
            container=container
        )
        
        # Design counter and progress
        self.progress_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((nav_center_x - 50, y_pos + 35), (100, 25)),
            text="",
            manager=self.manager,
            container=container
        )
        y_pos += 70
        
        # Left panel - Turtle image display (adjusted for smaller window)
        self.design_container = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((10, y_pos), (width // 2 - 20, 300)),
            manager=self.manager,
            container=container
        )
        
        # Create turtle display area
        self._create_turtle_display()
        
        # Right panel - Voting controls (adjusted for smaller window)
        self.voting_container = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((width // 2, y_pos), (width // 2 - 10, 300)),
            manager=self.manager,
            container=container
        )
        
        # Create voting controls
        self._create_voting_controls()
        
        # Submit button (adjusted position)
        self.btn_submit = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width // 2 + 50, y_pos + 320), (150, 40)),
            text="Submit & Earn $1",
            manager=self.manager,
            container=container
        )
        self.btn_submit.disable()
        
        # Update display
        self._update_design_display()
        
    def _create_turtle_display(self) -> None:
        """Create turtle image display area like the original voting view."""
        if not self.design_container:
            return
            
        # Design name label
        self.design_info_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 10), (300, 25)),
            text="",
            manager=self.manager,
            container=self.design_container
        )
        
        # Turtle image placeholder (adjusted for smaller panel)
        self.turtle_image = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect((25, 40), (150, 150)),
            image_surface=pygame.Surface((150, 150)),
            manager=self.manager,
            container=self.design_container
        )
        
        # Design stats/info area (adjusted)
        self.design_stats_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 200), (300, 90)),
            text="Design preview and stats\nwill appear here",
            manager=self.manager,
            container=self.design_container
        )
        
    def _create_voting_controls(self) -> None:
        """Create star rating controls for each category."""
        if not self.voting_container or not self.daily_designs:
            return
            
        current_design = self.daily_designs[self.current_design_index]
        categories = current_design['rating_categories']
        
        y_pos = 10
        self.rating_buttons = {}
        
        for category_name, category_data in categories.items():
            # Category label
            category_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((10, y_pos), (300, 25)),
                text=category_data['display_name'],
                manager=self.manager,
                container=self.voting_container
            )
            
            # Description
            desc_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((10, y_pos + 25), (300, 20)),
                text=category_data['description'],
                manager=self.manager,
                container=self.voting_container
            )
            
            # Star rating buttons
            star_buttons = []
            for i in range(5):
                star_btn = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect((10 + i * 35, y_pos + 50), (30, 30)),
                    text="★",
                    manager=self.manager,
                    container=self.voting_container,
                    object_id=f"#star_{category_name}_{i}"
                )
                star_btn.category = category_name
                star_btn.rating = i + 1
                star_buttons.append(star_btn)
                
            self.rating_buttons[category_name] = star_buttons
            y_pos += 100
            
    def _update_design_display(self) -> None:
        """Update the design information display with turtle image."""
        if not self.daily_designs or self.current_design_index >= len(self.daily_designs):
            return
            
        current_design = self.daily_designs[self.current_design_index]
        
        # Update design info
        design_text = f"{current_design['name']} - Status: {current_design['voting_status'].upper()}"
        if self.design_info_label:
            self.design_info_label.set_text(design_text)
            
        # Update turtle image (mock turtle for now)
        if hasattr(self, 'turtle_image') and self.turtle_image:
            try:
                # Create a mock turtle for demonstration
                class MockTurtle:
                    def __init__(self, design_id):
                        self.name = f"Design #{design_id}"
                        self.id = design_id
                        self.color_scheme = (design_id * 50 % 255, 100, 150)
                        
                mock_turtle = MockTurtle(current_design['id'])
                turtle_surface = render_turtle_pygame(mock_turtle, 140)  # Smaller for adjusted panel
                if turtle_surface:
                    self.turtle_image.set_image(turtle_surface)
            except Exception as e:
                print(f"Error rendering design turtle: {e}")
                
        # Update design stats
        if self.design_stats_label:
            stats_text = (
                f"Design ID: {current_design['id']}\n"
                f"Status: {current_design['voting_status'].upper()}\n"
                f"Categories: {len(current_design['rating_categories'])}\n\n"
                f"Rate each category to\n"
                f"influence future genetics!"
            )
            self.design_stats_label.set_text(stats_text)
            
        # Update progress
        progress_text = f"Design {self.current_design_index + 1} of {len(self.daily_designs)}"
        if self.progress_label:
            self.progress_label.set_text(progress_text)
            
        # Update navigation buttons
        if self.btn_previous:
            self.btn_previous.enable() if self.current_design_index > 0 else self.btn_previous.disable()
            
        if self.btn_next:
            self.btn_next.enable() if self.current_design_index < len(self.daily_designs) - 1 else self.btn_next.disable()
            
        # Update star ratings display
        self._update_star_display()
        
        # Update submit button
        self._update_submit_button()
        
    def _update_star_display(self) -> None:
        """Update star button appearances based on ratings."""
        current_design = self.daily_designs[self.current_design_index]
        
        for category_name, star_buttons in self.rating_buttons.items():
            current_rating = self.selected_ratings.get(category_name, 0)
            
            for i, star_btn in enumerate(star_buttons):
                if i < current_rating:
                    star_btn.enable()
                else:
                    star_btn.disable()
                    
    def _update_submit_button(self) -> None:
        """Update submit button state based on rating completion."""
        if not self.btn_submit:
            return
            
        current_design = self.daily_designs[self.current_design_index]
        
        # Check if all categories are rated
        all_rated = True
        for category_name in current_design['rating_categories']:
            if category_name not in self.selected_ratings:
                all_rated = False
                break
                
        # Enable submit if all categories are rated and design is pending
        if all_rated and current_design['voting_status'] == 'pending':
            self.btn_submit.enable()
        else:
            self.btn_submit.disable()
            
    def update(self, time_delta: float) -> None:
        """Update panel state."""
        super().update(time_delta)
        
        # Update feedback timer
        if self.show_feedback and self.feedback_timer > 0:
            self.feedback_timer -= time_delta
            if self.feedback_timer <= 0:
                self.show_feedback = False
                
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle voting panel events."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Navigation buttons
            if event.ui_element == self.btn_back:
                self.game_state.set('goto_menu', True)
                return True
                
            elif event.ui_element == self.btn_previous:
                if self.current_design_index > 0:
                    self.current_design_index -= 1
                    self._update_design_display()
                return True
                
            elif event.ui_element == self.btn_next:
                if self.current_design_index < len(self.daily_designs) - 1:
                    self.current_design_index += 1
                    self._update_design_display()
                return True
                
            elif event.ui_element == self.btn_submit:
                self._submit_ratings()
                return True
                
            # Star rating buttons
            elif hasattr(event.ui_element, 'category') and hasattr(event.ui_element, 'rating'):
                category_name = event.ui_element.category
                rating = event.ui_element.rating
                
                # Toggle rating (click same star to unrate)
                if self.selected_ratings.get(category_name) == rating:
                    self.selected_ratings.pop(category_name, None)
                else:
                    self.selected_ratings[category_name] = rating
                    
                self._update_star_display()
                self._update_submit_button()
                return True
                
        return False
        
    def _submit_ratings(self) -> None:
        """Submit the current ratings."""
        if not self.daily_designs or self.current_design_index >= len(self.daily_designs):
            return
            
        current_design = self.daily_designs[self.current_design_index]
        
        # Save ratings
        current_design['ratings'] = self.selected_ratings.copy()
        current_design['voting_status'] = 'completed'
        
        # Award money (via game state)
        current_money = self.game_state.get('money', 0)
        self.game_state.set('money', current_money + 1)
        
        # Show feedback
        self.show_feedback = True
        self.feedback_timer = 2.0  # Show for 2 seconds
        
        # Clear ratings for next design
        self.selected_ratings = {}
        
        # Auto-advance to next design if available
        if self.current_design_index < len(self.daily_designs) - 1:
            self.current_design_index += 1
            self._update_design_display()
        else:
            # All designs voted, return to menu
            self.game_state.set('goto_menu', True)
            
    def reset_voting_session(self) -> None:
        """Reset the voting session for a new day."""
        self.current_design_index = 0
        self.selected_ratings = {}
        self.daily_designs = self._generate_mock_designs()
        self._update_design_display()
