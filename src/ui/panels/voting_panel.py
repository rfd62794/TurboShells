"""
Voting Panel for TurboShells

Modern pygame_gui implementation of the voting interface.
"""

import pygame
import pygame_gui
import math
from typing import Dict, Any, Optional, List, Tuple
from ui.panels.base_panel import BasePanel
from core.rendering.turtle_render_engine import TurtleRenderEngine
from core.ui.window_manager import window_manager


class VotingPanel(BasePanel):
    """Voting interface panel using pygame_gui components."""
    
    def __init__(self, game_state_interface):
        super().__init__("voting", "Daily Design Voting", use_window_manager=True)
        
        self.game_state = game_state_interface
        
        # Voting state
        self.current_design_index = 0
        self.selected_ratings = {}
        self.show_feedback = False
        self.feedback_timer = 0
        
        # Turtle rendering engine
        self.turtle_render_engine = TurtleRenderEngine()
        
        # Rating display mode: 'stars' or 'dropdown'
        self.rating_mode = 'stars'  # Can be toggled
        
        # Scrolling state
        self.scroll_offset = 0
        self.max_scroll = 0
        self.scrollbar_visible = False
        self.scroll_step = 30
        
        # Mock voting system data with more realistic categories
        self.daily_designs = self._generate_mock_designs()
        
        # UI elements
        self.btn_back = None
        self.btn_previous = None
        self.btn_next = None
        self.btn_submit = None
        self.btn_toggle_rating = None
        self.rating_buttons = {}
        self.rating_dropdowns = {}
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
                    'shell_appearance': {
                        'display_name': 'Shell Appearance',
                        'description': 'Color, pattern, and visual appeal of shell'
                    },
                    'body_design': {
                        'display_name': 'Body Design',
                        'description': 'Body color, pattern, and overall aesthetics'
                    },
                    'head_features': {
                        'display_name': 'Head Features',
                        'description': 'Head size, color, and facial characteristics'
                    },
                    'limb_structure': {
                        'display_name': 'Limb Structure',
                        'description': 'Leg length, thickness, and fin/feet design'
                    },
                    'eye_quality': {
                        'display_name': 'Eye Quality',
                        'description': 'Eye size, color, and visual expression'
                    },
                    'overall_balance': {
                        'display_name': 'Overall Balance',
                        'description': 'Harmony between all design elements'
                    }
                }
            }
            designs.append(design)
        return designs
        
    def _create_window(self) -> None:
        """Create the voting window with enhanced layout."""
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
        
        # Rating mode toggle button
        self.btn_toggle_rating = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width - 160, y_pos), (70, 30)),
            text="Stars",
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
        
        # Left panel - Turtle image display (adjusted for more content)
        self.design_container = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((5, y_pos), (width // 2 - 5, 350)),
            manager=self.manager,
            container=container
        )
        
        # Create turtle display area
        self._create_turtle_display()
        
        # Right panel - Voting controls with scrolling support
        self.voting_container = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((width // 2, y_pos), (width // 2 - 5, 350)),
            manager=self.manager,
            container=container
        )
        
        # Create scrollable area for voting controls
        self.scroll_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect((10, 10), (width // 2 - 25, 330)),
            manager=self.manager,
            container=self.voting_container
        )
        
        # Create voting controls in scrollable container
        self._create_voting_controls()
        
        # Update scroll limits
        self._update_scroll_limits()
        
        # Submit button (adjusted position)
        self.btn_submit = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width // 2 + 30, y_pos + 370), (150, 40)),
            text="Submit & Earn $1",
            manager=self.manager,
            container=container
        )
        self.btn_submit.disable()
        
        # Update display
        self._update_design_display()
        
    def _create_turtle_display(self) -> None:
        """Create turtle image display area with proper rendering."""
        if not self.design_container:
            return
            
        # Design name label
        self.design_info_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 10), (300, 25)),
            text="",
            manager=self.manager,
            container=self.design_container
        )
        
        # Turtle image placeholder (larger for better detail)
        self.turtle_image = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect((20, 40), (200, 200)),
            image_surface=pygame.Surface((200, 200)),
            manager=self.manager,
            container=self.design_container
        )
        
        # Design stats/info area
        self.design_stats_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 250), (300, 80)),
            text="Design preview and stats\nwill appear here",
            manager=self.manager,
            container=self.design_container
        )
        
    def _create_voting_controls(self) -> None:
        """Create rating controls for each category (stars or dropdown) in scrollable container."""
        if not self.scroll_container or not self.daily_designs:
            return
            
        current_design = self.daily_designs[self.current_design_index]
        categories = current_design['rating_categories']
        
        # Clear existing controls
        self.rating_buttons = {}
        self.rating_dropdowns = {}
        
        # Calculate total content height
        content_height = len(categories) * 90 + 50  # 90px per category + submit button space
        
        # Set scroll container content size
        self.scroll_container.set_scrollable_area_dimensions((self.scroll_container.container_rect.width, content_height))
        
        y_pos = 10
        
        for category_name, category_data in categories.items():
            # Category label
            category_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((10, y_pos), (250, 25)),
                text=category_data['display_name'],
                manager=self.manager,
                container=self.scroll_container
            )
            
            # Description
            desc_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((10, y_pos + 25), (250, 20)),
                text=category_data['description'],
                manager=self.manager,
                container=self.scroll_container
            )
            
            if self.rating_mode == 'stars':
                # Star rating buttons
                star_buttons = []
                for i in range(5):
                    star_btn = pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((10 + i * 32, y_pos + 50), (28, 28)),
                        text="★",
                        manager=self.manager,
                        container=self.scroll_container,
                        object_id=f"#star_{category_name}_{i}"
                    )
                    star_btn.category = category_name
                    star_btn.rating = i + 1
                    star_buttons.append(star_btn)
                    
                self.rating_buttons[category_name] = star_buttons
            else:
                # Dropdown rating selector
                rating_options = ['No Rating'] + [f'{i} Stars' for i in range(1, 6)]
                dropdown = pygame_gui.elements.UIDropDownMenu(
                    options_list=rating_options,
                    starting_option='No Rating',
                    relative_rect=pygame.Rect((10, y_pos + 50), (150, 30)),
                    manager=self.manager,
                    container=self.scroll_container
                )
                dropdown.category = category_name
                self.rating_dropdowns[category_name] = dropdown
                
            y_pos += 90  # Adjusted for larger labels
            
    def _update_scroll_limits(self) -> None:
        """Update scroll limits based on content height."""
        if not self.scroll_container or not self.daily_designs:
            return
            
        current_design = self.daily_designs[self.current_design_index]
        categories = current_design['rating_categories']
        
        # Calculate total content height
        content_height = len(categories) * 90 + 50  # 90px per category + submit button space
        available_height = self.scroll_container.rect.height
        
        # Set scrollable area dimensions
        if content_height > available_height:
            self.scroll_container.set_scrollable_area_dimensions((self.scroll_container.rect.width, content_height))
            self.scrollbar_visible = True
        else:
            self.scroll_container.set_scrollable_area_dimensions((self.scroll_container.rect.width, available_height))
            self.scrollbar_visible = False
            
    def _update_design_display(self) -> None:
        """Update the design information display with proper turtle rendering."""
        if not self.daily_designs or self.current_design_index >= len(self.daily_designs):
            return
            
        current_design = self.daily_designs[self.current_design_index]
        
        # Update design info
        design_text = f"{current_design['name']} - Status: {current_design['voting_status'].upper()}"
        if self.design_info_label:
            self.design_info_label.set_text(design_text)
            
        # Update turtle image using proper TurtleRenderEngine
        if hasattr(self, 'turtle_image') and self.turtle_image:
            try:
                # Create a mock turtle with realistic genetics for demonstration
                class MockTurtle:
                    def __init__(self, design_id):
                        self.name = f"Design #{design_id}"
                        self.id = design_id
                        # Generate realistic genetics based on design ID
                        seed = design_id * 12345
                        import random
                        random.seed(seed)
                        
                        # Realistic turtle genetics
                        self.shell_base_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
                        self.shell_pattern_type = random.choice(['solid', 'stripes', 'spots', 'marbled'])
                        self.shell_pattern_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
                        self.pattern_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
                        self.shell_pattern_density = random.uniform(0.1, 0.9)
                        self.shell_pattern_opacity = random.uniform(0.3, 0.8)
                        self.shell_size_modifier = random.uniform(0.8, 1.3)
                        
                        self.body_base_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
                        self.body_pattern_type = random.choice(['solid', 'mottled', 'gradient'])
                        self.body_pattern_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
                        self.body_pattern_density = random.uniform(0.1, 0.7)
                        
                        self.head_size_modifier = random.uniform(0.9, 1.2)
                        self.head_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
                        
                        self.leg_length = random.uniform(0.3, 1.2)
                        self.limb_shape = random.choice(['feet', 'fins', 'claws'])
                        self.leg_thickness_modifier = random.uniform(0.7, 1.4)
                        self.leg_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
                        
                        self.eye_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
                        self.eye_size_modifier = random.uniform(0.8, 1.3)
                        
                        # Additional attributes for rendering
                        self.speed = random.randint(15, 25)
                        self.energy = random.randint(200, 300)
                        
                mock_turtle = MockTurtle(current_design['id'])
                turtle_surface = self.turtle_render_engine.get_turtle_sprite_surface(mock_turtle, (190, 190))
                if turtle_surface:
                    self.turtle_image.set_image(turtle_surface)
            except Exception as e:
                print(f"Error rendering design turtle: {e}")
                
        # Update design stats with more detailed information
        if self.design_stats_label:
            stats_text = (
                f"Design ID: {current_design['id']}\n"
                f"Status: {current_design['voting_status'].upper()}\n"
                f"Categories: {len(current_design['rating_categories'])}\n"
                f"Rating Mode: {self.rating_mode.capitalize()}\n\n"
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
            
        # Update rating display based on mode
        if self.rating_mode == 'stars':
            self._update_star_display()
        else:
            self._update_dropdown_display()
        
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
                    
    def _update_dropdown_display(self) -> None:
        """Update dropdown selections based on ratings."""
        current_design = self.daily_designs[self.current_design_index]
        
        for category_name, dropdown in self.rating_dropdowns.items():
            current_rating = self.selected_ratings.get(category_name, 0)
            if current_rating > 0:
                dropdown.selected_option = f'{current_rating} Stars'
            else:
                dropdown.selected_option = 'No Rating'
                    
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
        """Handle voting panel events with scrolling support."""
        # Handle mouse wheel scrolling first
        if event.type == pygame.MOUSEWHEEL:
            if self.scroll_container and self.scrollbar_visible:
                # Scroll up or down based on wheel direction
                if event.y > 0:  # Scroll up
                    self.scroll_container.scroll_up()
                elif event.y < 0:  # Scroll down
                    self.scroll_container.scroll_down()
                return True
                
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Back button
            if event.ui_element == self.btn_back:
                self.game_state.set('goto_menu', True)
                return True
                
            # Rating mode toggle button
            elif event.ui_element == self.btn_toggle_rating:
                self._toggle_rating_mode()
                return True
                
            # Navigation buttons
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
                
            # Submit button
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
                
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            # Handle dropdown rating changes
            if hasattr(event.ui_element, 'category'):
                category_name = event.ui_element.category
                selected_text = event.text
                
                # Parse rating from dropdown selection
                if selected_text == 'No Rating':
                    self.selected_ratings.pop(category_name, None)
                else:
                    # Extract number from "X Stars"
                    rating = int(selected_text.split(' ')[0])
                    self.selected_ratings[category_name] = rating
                    
                self._update_submit_button()
                return True
                
        return False
        
    def _toggle_rating_mode(self) -> None:
        """Toggle between star and dropdown rating modes."""
        if self.rating_mode == 'stars':
            self.rating_mode = 'dropdown'
            self.btn_toggle_rating.set_text('Dropdown')
        else:
            self.rating_mode = 'stars'
            self.btn_toggle_rating.set_text('Stars')
            
        # Recreate voting controls with new mode
        self._create_voting_controls()
        self._update_scroll_limits()
        self._update_design_display()
        
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
        
    def _on_window_resize(self, new_size: Tuple[int, int]) -> None:
        """Called after window resize. Update display if UI elements are ready."""
        # Update display only if UI elements are properly initialized
        if hasattr(self, 'design_stats_label') and self.design_stats_label:
            self._update_design_display()
