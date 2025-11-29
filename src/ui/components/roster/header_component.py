"""Header component for roster panel."""

import pygame
import pygame_gui
from pygame_gui import UIManager
from typing import Optional, Dict, Any
from ..base_component import BaseComponent


class HeaderComponent(BaseComponent):
    """Component for header with money display and menu button.
    
    Single Responsibility: Handle header UI elements.
    """
    
    def __init__(self, rect: pygame.Rect, manager: Optional[UIManager] = None,
                 game_state=None, container=None):
        super().__init__(rect, manager, container)
        self.game_state = game_state
        
        # UI elements
        self.lbl_money = None  # Money label removed - moved to betting controls
        self.top_bar = None
        # Menu button removed - now in betting controls
        
        # Create UI elements
        self._create_ui_elements()
        
    def _create_ui_elements(self) -> None:
        """Create header UI elements."""
        if not self.manager or not self.container:
            return
            
        # Header panel
        self.top_bar = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 0), (self.rect.width, 60)),
            manager=self.manager,
            container=self.container,
            object_id="#roster_header"
        )
        
        # Money label removed - moved to betting controls
        # self.lbl_money = pygame_gui.elements.UILabel(
        #     relative_rect=pygame.Rect((20, 15), (200, 30)),
        #     text=f"Funds: ${self.game_state.get('money', 0) if self.game_state else 0}",
        #     manager=self.manager,
        #     container=self.top_bar
        # )
        
        # Menu button removed - now in betting controls
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for header component."""
        # Menu button handling removed - now in betting controls
        return False
        
    def update_money(self, money: int) -> None:
        """Update money display - no longer needed, moved to betting controls."""
        pass
            
    def get_elements(self) -> Dict[str, Any]:
        """Get UI element references."""
        return {
            'top_bar': self.top_bar
            # Money label and Menu button removed - now in betting controls
        }
        
    def render(self, surface: pygame.Surface) -> None:
        """Render the component. pygame_gui handles rendering."""
        pass
        
    def destroy(self) -> None:
        """Clean up UI elements."""
        if self.top_bar:
            self.top_bar.kill()
        # Money label cleanup removed - now in betting controls
