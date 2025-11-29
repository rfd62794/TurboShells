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
        self.lbl_money = None
        self.btn_menu = None
        self.top_bar = None
        
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
        
        # Money label
        self.lbl_money = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20, 15), (200, 30)),
            text=f"Funds: ${self.game_state.get('money', 0) if self.game_state else 0}",
            manager=self.manager,
            container=self.top_bar
        )
        
        # Menu button
        self.btn_menu = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.rect.width - 100, 10), (100, 40)),
            text="Menu",
            manager=self.manager,
            container=self.top_bar
        )
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for header component."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_menu:
                print(f"[DEBUG] ✓ MATCHED Menu button")
                if self.game_state:
                    self.game_state.set('select_racer_mode', False)
                    # Navigate to menu - this would need to be handled by parent
                return True
        return False
        
    def update_money(self, money: int) -> None:
        """Update money display."""
        if self.lbl_money:
            self.lbl_money.set_text(f"Funds: ${money}")
            
    def get_elements(self) -> Dict[str, Any]:
        """Get UI element references."""
        return {
            'lbl_money': self.lbl_money,
            'btn_menu': self.btn_menu,
            'top_bar': self.top_bar
        }
        
    def render(self, surface: pygame.Surface) -> None:
        """Render the component. pygame_gui handles rendering."""
        pass
        
    def destroy(self) -> None:
        """Clean up UI elements."""
        if self.top_bar:
            self.top_bar.kill()
        if self.lbl_money:
            self.lbl_money.kill()
        if self.btn_menu:
            self.btn_menu.kill()
