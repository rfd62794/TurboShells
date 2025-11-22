"""State management system for TurboShells game.

Handles all game state transitions and logic in a centralized way.
"""

from settings import *


class StateHandler:
    """Manages game state transitions and click handling."""
    
    def __init__(self, game):
        self.game = game
        self.state_transitions = {
            STATE_MENU: self._handle_menu_clicks,
            STATE_ROSTER: self._handle_roster_clicks,
            STATE_SHOP: self._handle_shop_clicks,
            STATE_BREEDING: self._handle_breeding_clicks,
            STATE_RACE: self._handle_race_clicks,
            STATE_RACE_RESULT: self._handle_race_result_clicks,
        }
    
    def handle_click(self, pos):
        """Route click handling to appropriate state method."""
        handler = self.state_transitions.get(self.game.state)
        if handler:
            return handler(pos)
        return None
    
    def _handle_menu_clicks(self, pos):
        """Handle clicks in main menu state."""
        # Check main menu button clicks
        menu_rects = [
            (pygame.Rect(200, 150, 400, 80), STATE_ROSTER),  # ROSTER
            (pygame.Rect(200, 250, 400, 80), STATE_SHOP),  # SHOP
            (pygame.Rect(200, 350, 400, 80), STATE_BREEDING),  # BREEDING
        ]
        
        for rect, new_state in menu_rects:
            if rect.collidepoint(pos):
                if new_state == STATE_SHOP:
                    self.game.shop_manager.refresh_stock()
                self.game.state = new_state
                break
    
    def _handle_roster_clicks(self, pos):
        """Handle clicks in roster state."""
        action = self.game.roster_manager.handle_click(pos)
        if action == "GOTO_RACE":
            # Check if we have a selected racer and bet
            active_racer = self.game.roster[getattr(self.game, "active_racer_index", 0)]
            if active_racer:
                self.game.race_manager.start_race()
                self.game.state = STATE_RACE
        elif action == "GOTO_MENU":
            self.game.state = STATE_MENU
        elif action == "GOTO_SHOP":
            self.game.state = STATE_SHOP
        elif action == "GOTO_BREEDING":
            self.game.state = STATE_BREEDING
    
    def _handle_shop_clicks(self, pos):
        """Handle clicks in shop state."""
        action = self.game.shop_manager.handle_click(pos)
        if action == "GOTO_MENU":
            self.game.state = STATE_MENU
    
    def _handle_breeding_clicks(self, pos):
        """Handle clicks in breeding state."""
        action = self.game.breeding_manager.handle_click(pos)
        if action == "GOTO_MENU":
            self.game.state = STATE_MENU
    
    def _handle_race_clicks(self, pos):
        """Handle clicks during race."""
        self.game.race_manager.handle_click(pos)
    
    def _handle_race_result_clicks(self, pos):
        """Handle clicks in race result state."""
        action = self.game.race_manager.handle_result_click(pos)
        if action == "GOTO_MENU":
            self.game.state = STATE_MENU
            # Clear temporary opponents when returning to menu
            if self.game.roster[1] and getattr(self.game.roster[1], 'is_temp', False):
                self.game.roster[1] = None
            if self.game.roster[2] and getattr(self.game.roster[2], 'is_temp', False):
                self.game.roster[2] = None
        elif action == "RERUN":
            self.game.state = STATE_RACE
    
    def transition_to_menu(self):
        """Transition to main menu state."""
        self.game.state = STATE_MENU
    
    def transition_to_roster(self):
        """Transition to roster state."""
        self.game.state = STATE_ROSTER
    
    def transition_to_shop(self):
        """Transition to shop state."""
        self.game.state = STATE_SHOP
        self.game.shop_manager.refresh_stock()
    
    def transition_to_breeding(self):
        """Transition to breeding state."""
        self.game.state = STATE_BREEDING
    
    def transition_to_race(self):
        """Transition to race state if conditions are met."""
        active_racer = self.game.roster[getattr(self.game, "active_racer_index", 0)]
        if active_racer:
            self.game.race_manager.start_race()
            self.game.state = STATE_RACE
            return True
        return False
