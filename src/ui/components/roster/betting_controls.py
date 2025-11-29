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
        
        # Betting buttons - move slightly left from original position
        self.btn_bet_0 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((container_width - 360, 0), (100, 30)),  # 20px left
            text="Bet: $0",
            manager=self.manager,
            container=self.container,
            visible=False
        )
        
        self.btn_bet_5 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((container_width - 250, 0), (100, 30)),  # 20px left
            text="Bet: $5",
            manager=self.manager,
            container=self.container,
            visible=False
        )
        
        self.btn_bet_10 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((container_width - 140, 0), (100, 30)),  # 20px left
            text="Bet: $10",
            manager=self.manager,
            container=self.container,
            visible=False
        )
        
        # Start race button - move slightly left with betting controls
        self.btn_start_race = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((container_width - 460, 0), (100, 30)),  # 20px left
            text="START RACE",
            manager=self.manager,
            container=self.container,
            visible=False
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
            'btn_start_race': self.btn_start_race
        }
        
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
