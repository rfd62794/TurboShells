"""Betting controls component for race wagering."""

import pygame
import pygame_gui
from pygame_gui import UIManager
from typing import Optional, Dict, Any
from ..base_component import BaseComponent


class BettingControls(BaseComponent):
    """Component for betting controls and start race button.
    
    Single Responsibility: Handle betting UI and race start functionality.
    """
    
    def __init__(self, rect: pygame.Rect, manager: Optional[UIManager] = None,
                 game_state=None, container=None):
        super().__init__(rect, manager, container)
        self.game_state = game_state
        
        # UI elements
        self.btn_bet_0 = None
        self.btn_bet_5 = None
        self.btn_bet_10 = None
        self.btn_start_race = None
        self.btn_menu = None  # Add menu button
        self.lbl_money = None  # Add money label
        
        # Create UI elements
        self._create_ui_elements()
        
        # Set initial visibility
        self._update_visibility()
        
    def _create_ui_elements(self) -> None:
        """Create betting control buttons."""
        if not self.manager or not self.container:
            return
            
        # Calculate positions based on container width
        container_width = self.rect.width
        
        # Betting buttons - move further left from current position
        self.btn_bet_0 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((container_width - 335, 0), (100, 30)),  # 30px more left
            text="Bet: $0",
            manager=self.manager,
            container=self.container,
            visible=False
        )
        
        self.btn_bet_5 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((container_width - 235, 0), (100, 30)),  # 30px more left
            text="Bet: $5",
            manager=self.manager,
            container=self.container,
            visible=False
        )
        
        self.btn_bet_10 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((container_width - 135, 0), (100, 30)),  # 30px more left
            text="Bet: $10",
            manager=self.manager,
            container=self.container,
            visible=False
        )
        
        # Start race button - move further left with betting controls
        self.btn_start_race = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((container_width - 435, 0), (100, 30)),  # 30px more left
            text="START RACE",
            manager=self.manager,
            container=self.container,
            visible=False
        )
        
        # Menu button - position on absolute left side
        self.btn_menu = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 0), (80, 30)),  # Absolute left side (x=0)
            text="Menu",
            manager=self.manager,
            container=self.container,
            visible=True  # Always visible
        )
        
        # Money label - next to Menu button with small spacer
        self.lbl_money = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((85, 0), (150, 30)),  # Menu (80) + spacer (5)
            text=f"Funds: ${self.game_state.get('money', 0) if self.game_state else 0}",
            manager=self.manager,
            container=self.container
        )
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for betting controls."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_bet_0:
                print(f"[DEBUG] ✓ MATCHED Bet $0 button")
                self.game_state.set('set_bet', 0)
                return True
            elif event.ui_element == self.btn_bet_5:
                print(f"[DEBUG] ✓ MATCHED Bet $5 button")
                self.game_state.set('set_bet', 5)
                return True
            elif event.ui_element == self.btn_bet_10:
                print(f"[DEBUG] ✓ MATCHED Bet $10 button")
                self.game_state.set('set_bet', 10)
                return True
            elif event.ui_element == self.btn_start_race:
                print(f"[DEBUG] ✓ MATCHED START RACE button!")
                active_racer_idx = self.game_state.get('active_racer_index', -1)
                if active_racer_idx >= 0:
                    self.game_state.set('start_race', active_racer_idx)
                return True
            elif event.ui_element == self.btn_menu:
                print(f"[DEBUG] ✓ MATCHED Menu button!")
                self.game_state.set('select_racer_mode', False)
                # Navigate to menu using the same pattern as other components
                self.game_state.set('state', 'MENU')
                return True
        return False
        
    def update_mode(self, select_mode: bool) -> None:
        """Update visibility based on select mode."""
        if select_mode:
            self.btn_bet_0.show()
            self.btn_bet_5.show()
            self.btn_bet_10.show()
            if self.btn_start_race:
                self.btn_start_race.show()
        else:
            self.btn_bet_0.hide()
            self.btn_bet_5.hide()
            self.btn_bet_10.hide()
            if self.btn_start_race:
                self.btn_start_race.hide()
                
    def update_bet_feedback(self, current_bet: int) -> None:
        """Update betting button visual feedback."""
        if not all([self.btn_bet_0, self.btn_bet_5, self.btn_bet_10]):
            return
            
        # Reset all buttons to normal appearance
        self.btn_bet_0.set_text("Bet: $0")
        self.btn_bet_5.set_text("Bet: $5")
        self.btn_bet_10.set_text("Bet: $10")
        
        # Highlight the active bet button
        if current_bet == 0:
            self.btn_bet_0.set_text("Bet: $0 ✓")
        elif current_bet == 5:
            self.btn_bet_5.set_text("Bet: $5 ✓")
        elif current_bet == 10:
            self.btn_bet_10.set_text("Bet: $10 ✓")
            
    def _update_visibility(self) -> None:
        """Set initial visibility state."""
        select_mode = self.game_state.get('select_racer_mode', False) if self.game_state else False
        self.update_mode(select_mode)
        
    def get_buttons(self) -> Dict[str, Any]:
        """Get button references for debugging."""
        return {
            'btn_bet_0': self.btn_bet_0,
            'btn_bet_5': self.btn_bet_5,
            'btn_bet_10': self.btn_bet_10,
            'btn_start_race': self.btn_start_race,
            'btn_menu': self.btn_menu
        }
        
    def update_money(self, money: int) -> None:
        """Update money display."""
        if self.lbl_money:
            self.lbl_money.set_text(f"Funds: ${money}")
        
    def render(self, surface: pygame.Surface) -> None:
        """Render the component. pygame_gui handles rendering."""
        pass
        
    def destroy(self) -> None:
        """Clean up UI elements."""
        if self.btn_bet_0:
            self.btn_bet_0.kill()
        if self.btn_bet_5:
            self.btn_bet_5.kill()
        if self.btn_bet_10:
            self.btn_bet_10.kill()
        if self.btn_start_race:
            self.btn_start_race.kill()
        if self.btn_menu:
            self.btn_menu.kill()
        if self.lbl_money:
            self.lbl_money.kill()
