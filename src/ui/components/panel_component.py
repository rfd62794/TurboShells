"""
Panel component following SRP for better UI architecture.
"""

import pygame
import pygame_gui
from typing import Optional, Dict, Any, List
from .base_component import BaseComponent
from .container import ScrollableContainer
from .turtle_display import DesignDisplay
from .rating_component import RatingCategory


class PanelComponent(BaseComponent):
    """Base panel component with proper SRP separation."""
    
    def __init__(self, rect: pygame.Rect, manager=None, title: str = ""):
        """Initialize panel component.
        
        Args:
            rect: Panel position and size
            manager: pygame_gui UIManager
            title: Panel title
        """
        super().__init__(rect, manager)
        self.title = title
        self.window: Optional[pygame_gui.elements.UIWindow] = None
        self.ui_elements: Dict[str, Any] = {}
        self.font = pygame.font.Font(None, 24)
        
    def create_window(self, manager: pygame_gui.UIManager) -> None:
        """Create the pygame_gui window."""
        if self.window:
            return
            
        self.manager = manager
        self.window = pygame_gui.elements.UIWindow(
            rect=self.rect,
            manager=manager,
            window_title=self.title,
            draggable=True,
            resizable=False
        )
        
    def destroy_window(self) -> None:
        """Destroy the pygame_gui window."""
        if self.window:
            self.window.kill()
            self.window = None
            
    def get_container(self):
        """Get the window container for adding UI elements."""
        if self.window:
            return self.window.get_container()
        return None
        
    def render(self, surface: pygame.Surface) -> None:
        """Render panel (handled by pygame_gui window)."""
        # Window is rendered by pygame_gui automatically
        pass
        
    def show(self) -> None:
        """Show the panel."""
        if self.window:
            self.window.show()
        self.visible = True
        
    def hide(self) -> None:
        """Hide the panel."""
        if self.window:
            self.window.hide()
        self.visible = False


class VotingPanelComponent(PanelComponent):
    """Voting panel component using component-based architecture."""
    
    def __init__(self, rect: pygame.Rect, manager=None, game_state=None):
        """Initialize voting panel component.
        
        Args:
            rect: Panel position and size
            manager: pygame_gui UIManager
            game_state: Game state interface
        """
        super().__init__(rect, manager, "Daily Design Voting")
        self.game_state = game_state
        self.designs: List[Dict] = []
        self.current_design_index = 0
        self.selected_ratings: Dict[str, int] = {}
        self.rating_mode = 'stars'  # 'stars' or 'dropdown'
        
        # Sub-components
        self.design_display: Optional[DesignDisplay] = None
        self.rating_container: Optional[ScrollableContainer] = None
        self.rating_categories: List[RatingCategory] = []
        
        # UI elements
        self.btn_back: Optional[pygame_gui.elements.UIButton] = None
        self.btn_previous: Optional[pygame_gui.elements.UIButton] = None
        self.btn_next: Optional[pygame_gui.elements.UIButton] = None
        self.btn_submit: Optional[pygame_gui.elements.UIButton] = None
        self.btn_toggle_mode: Optional[pygame_gui.elements.UIButton] = None
        self.progress_label: Optional[pygame_gui.elements.UILabel] = None
        
        # Initialize with mock data
        self._generate_mock_designs()
        
    def create_window(self, manager: pygame_gui.UIManager) -> None:
        """Create the voting panel window and components."""
        super().create_window(manager)
        
        if not self.window:
            return
            
        container = self.window.get_container()
        width = self.rect.width - 40
        y_pos = 10
        
        # Header
        self._create_header(container, width, y_pos)
        y_pos += 40
        
        # Subtitle
        self._create_subtitle(container, width, y_pos)
        y_pos += 35
        
        # Navigation
        self._create_navigation(container, width, y_pos)
        y_pos += 70
        
        # Main content area
        self._create_main_content(container, width, y_pos)
        
        # Submit button
        self._create_submit_button(container, width, y_pos)
        
        # Initialize components
        self._initialize_components()
        self._update_display()
        
    def _create_header(self, container, width: int, y_pos: int) -> None:
        """Create header section."""
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_pos), (width, 30)),
            text="Daily Design Voting",
            manager=self.manager,
            container=container
        )
        
        self.btn_back = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width - 80, y_pos), (70, 30)),
            text="BACK",
            manager=self.manager,
            container=container
        )
        
        self.btn_toggle_mode = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width - 160, y_pos), (70, 30)),
            text="Stars",
            manager=self.manager,
            container=container
        )
        
    def _create_subtitle(self, container, width: int, y_pos: int) -> None:
        """Create subtitle section."""
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_pos), (width, 25)),
            text="Rate each category to earn $1 and influence genetics!",
            manager=self.manager,
            container=container
        )
        
    def _create_navigation(self, container, width: int, y_pos: int) -> None:
        """Create navigation controls."""
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
        
        self.progress_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((nav_center_x - 50, y_pos + 35), (100, 25)),
            text="",
            manager=self.manager,
            container=container
        )
        
    def _create_main_content(self, container, width: int, y_pos: int) -> None:
        """Create main content area with design display and ratings."""
        # Left panel - Design display
        design_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((5, y_pos), (width // 2 - 5, 350)),
            manager=self.manager,
            container=container
        )
        
        # Right panel - Rating controls
        rating_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((width // 2, y_pos), (width // 2 - 5, 350)),
            manager=self.manager,
            container=container
        )
        
        # Store panels for component creation
        self.ui_elements['design_panel'] = design_panel
        self.ui_elements['rating_panel'] = rating_panel
        
    def _create_submit_button(self, container, width: int, y_pos: int) -> None:
        """Create submit button."""
        self.btn_submit = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width // 2 + 30, y_pos + 370), (150, 40)),
            text="Submit & Earn $1",
            manager=self.manager,
            container=container
        )
        self.btn_submit.disable()
        
    def _initialize_components(self) -> None:
        """Initialize sub-components."""
        # Design display component
        design_rect = pygame.Rect(10, 10, 250, 330)
        self.design_display = DesignDisplay(design_rect, self.manager)
        
        # Rating container (scrollable)
        rating_rect = pygame.Rect(10, 10, 250, 330)
        self.rating_container = ScrollableContainer(rating_rect, self.manager)
        
        # Create rating categories
        self._create_rating_categories()
        
    def _create_rating_categories(self) -> None:
        """Create rating category components."""
        if not self.designs or self.current_design_index >= len(self.designs):
            return
            
        current_design = self.designs[self.current_design_index]
        categories = current_design.get('rating_categories', {})
        
        self.rating_categories.clear()
        
        y_pos = 10
        for category_name, category_data in categories.items():
            category_rect = pygame.Rect(10, y_pos, 230, 80)
            rating_category = RatingCategory(
                category_rect,
                category_data['display_name'],
                category_data['description'],
                self.rating_mode,
                self.manager
            )
            
            # Set rating change callback
            rating_category.set_rating_changed_callback(
                lambda rating, cat=category_name: self._on_rating_changed(cat, rating)
            )
            
            self.rating_categories.append(rating_category)
            self.rating_container.add_child(rating_category)
            y_pos += 90
            
        # Update container layout
        self.rating_container._update_layout()
        
    def _on_rating_changed(self, category: str, rating: int) -> None:
        """Handle rating change."""
        if rating == 0:
            self.selected_ratings.pop(category, None)
        else:
            self.selected_ratings[category] = rating
            
        self._update_submit_button()
        
    def _generate_mock_designs(self) -> None:
        """Generate mock design data."""
        self.designs = []
        for i in range(5):
            design = {
                'id': i + 1,
                'name': f'Design #{i + 1}',
                'voting_status': 'pending',
                'rating_categories': {
                    'shell_appearance': {
                        'display_name': 'Shell Appearance',
                        'description': 'Color, pattern, and visual appeal'
                    },
                    'body_design': {
                        'display_name': 'Body Design',
                        'description': 'Body color, pattern, and aesthetics'
                    },
                    'head_features': {
                        'display_name': 'Head Features',
                        'description': 'Head size, color, and characteristics'
                    },
                    'limb_structure': {
                        'display_name': 'Limb Structure',
                        'description': 'Leg length, thickness, and design'
                    },
                    'eye_quality': {
                        'display_name': 'Eye Quality',
                        'description': 'Eye size, color, and expression'
                    },
                    'overall_balance': {
                        'display_name': 'Overall Balance',
                        'description': 'Harmony between all elements'
                    }
                }
            }
            self.designs.append(design)
            
    def _update_display(self) -> None:
        """Update the display with current design."""
        if not self.designs or self.current_design_index >= len(self.designs):
            return
            
        current_design = self.designs[self.current_design_index]
        
        # Update design display
        if self.design_display:
            self.design_display.set_design(current_design)
            
        # Update progress
        if self.progress_label:
            progress_text = f"Design {self.current_design_index + 1} of {len(self.designs)}"
            self.progress_label.set_text(progress_text)
            
        # Update navigation buttons
        if self.btn_previous:
            self.btn_previous.enable() if self.current_design_index > 0 else self.btn_previous.disable()
            
        if self.btn_next:
            self.btn_next.enable() if self.current_design_index < len(self.designs) - 1 else self.btn_next.disable()
            
        # Update submit button
        self._update_submit_button()
        
    def _update_submit_button(self) -> None:
        """Update submit button state."""
        if not self.btn_submit or not self.designs:
            return
            
        current_design = self.designs[self.current_design_index]
        
        # Check if all categories are rated
        all_rated = True
        for category_name in current_design.get('rating_categories', {}):
            if category_name not in self.selected_ratings:
                all_rated = False
                break
                
        # Enable submit if all categories are rated and design is pending
        if all_rated and current_design.get('voting_status') == 'pending':
            self.btn_submit.enable()
        else:
            self.btn_submit.disable()
            
    def _handle_component_event(self, event: pygame.event.Event) -> bool:
        """Handle panel-specific events."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_back:
                self._emit_event('back')
                return True
                
            elif event.ui_element == self.btn_toggle_mode:
                self._toggle_rating_mode()
                return True
                
            elif event.ui_element == self.btn_previous:
                self._navigate_previous()
                return True
                
            elif event.ui_element == self.btn_next:
                self._navigate_next()
                return True
                
            elif event.ui_element == self.btn_submit:
                self._submit_ratings()
                return True
                
        return False
        
    def _toggle_rating_mode(self) -> None:
        """Toggle between rating modes."""
        if self.rating_mode == 'stars':
            self.rating_mode = 'dropdown'
            self.btn_toggle_mode.set_text('Dropdown')
        else:
            self.rating_mode = 'stars'
            self.btn_toggle_mode.set_text('Stars')
            
        # Recreate rating categories
        self._create_rating_categories()
        
    def _navigate_previous(self) -> None:
        """Navigate to previous design."""
        if self.current_design_index > 0:
            self.current_design_index -= 1
            self.selected_ratings.clear()
            self._create_rating_categories()
            self._update_display()
            
    def _navigate_next(self) -> None:
        """Navigate to next design."""
        if self.current_design_index < len(self.designs) - 1:
            self.current_design_index += 1
            self.selected_ratings.clear()
            self._create_rating_categories()
            self._update_display()
            
    def _submit_ratings(self) -> None:
        """Submit current ratings."""
        if not self.designs or self.current_design_index >= len(self.designs):
            return
            
        current_design = self.designs[self.current_design_index]
        
        # Save ratings
        current_design['ratings'] = self.selected_ratings.copy()
        current_design['voting_status'] = 'completed'
        
        # Award money
        current_money = self.game_state.get('money', 0) if self.game_state else 0
        if self.game_state:
            self.game_state.set('money', current_money + 1)
            
        # Clear ratings and navigate
        self.selected_ratings.clear()
        
        if self.current_design_index < len(self.designs) - 1:
            self._navigate_next()
        else:
            self._emit_event('back')  # All done, go back
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events with component delegation."""
        # Let sub-components handle events first
        if self.design_display and self.design_display.handle_event(event):
            return True
            
        if self.rating_container and self.rating_container.handle_event(event):
            return True
            
        # Handle panel events
        return super().handle_event(event)
        
    def update(self, dt: float) -> None:
        """Update panel and components."""
        super().update(dt)
        
        # Update sub-components
        if self.design_display:
            self.design_display.update(dt)
            
        if self.rating_container:
            self.rating_container.update(dt)
