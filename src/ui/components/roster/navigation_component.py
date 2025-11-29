"""Navigation component for roster panel."""

import pygame
import pygame_gui
from pygame_gui import UIManager
from typing import Optional, Dict, Any, Callable
from ..base_component import BaseComponent


class NavigationComponent(BaseComponent):
    """Component for navigation buttons (Race).
    
    Single Responsibility: Handle navigation UI elements.
    """
    
    def __init__(self, rect: pygame.Rect, manager: Optional[UIManager] = None,
                 game_state=None, container=None, on_navigate: Optional[Callable] = None):
        super().__init__(rect, manager, container)
        self.game_state = game_state
        self.on_navigate = on_navigate
        
        # UI elements
        # Race button removed - now handled by BettingControls component
        # self.btn_race = None
        
        # Create UI elements
        self._create_ui_elements()
        
    def _create_ui_elements(self) -> None:
        """Create navigation UI elements."""
        if not self.manager or not self.container:
            return
            
        # Race button removed - now handled by BettingControls component
        # self.btn_race = pygame_gui.elements.UIButton(
        #     relative_rect=pygame.Rect((self.rect.width - 440, 0), (100, 30)),
        #     text="Race",
        #     manager=self.manager,
        #     container=self.container
        # )
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for navigation component."""
        # Race button handling removed - now handled by BettingControls component
        return False
        
    def get_elements(self) -> Dict[str, Any]:
        """Get UI element references."""
        return {
            # Race button removed - now handled by BettingControls component
        }
        
    def render(self, surface: pygame.Surface) -> None:
        """Render the component. pygame_gui handles rendering."""
        pass
        
    def destroy(self) -> None:
        """Clean up UI elements."""
        # Race button cleanup removed - now handled by BettingControls component
        pass
