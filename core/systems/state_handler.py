"""State management system for TurboShells game.

Handles all game state transitions and logic in a centralized way.
"""

import pygame
from settings import *
import ui.layouts.positions as layout


class StateHandler:
    """Manages game state transitions and click handling."""
    
    def __init__(self, game):
        self.game = game
        self.state_transitions = {
            STATE_MENU: self._handle_menu_clicks,
            STATE_ROSTER: self._handle_roster_clicks,
            STATE_SHOP: self._handle_shop_clicks,
            STATE_BREEDING: self._handle_breeding_clicks,
            STATE_TRAINING: self._handle_training_clicks,
            STATE_RACE: self._handle_race_clicks,
            STATE_RACE_RESULT: self._handle_race_result_clicks,
            STATE_PROFILE: self._handle_profile_clicks,
            STATE_VOTING: self._handle_voting_clicks,
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
            (layout.MENU_ROSTER_RECT, STATE_ROSTER),  # ROSTER
            (layout.MENU_SHOP_RECT, STATE_SHOP),  # SHOP
            (layout.MENU_BREEDING_RECT, STATE_BREEDING),  # BREEDING
            (layout.MENU_RACE_RECT, STATE_RACE),  # RACE
            (layout.MENU_VOTING_RECT, STATE_VOTING),  # VOTING
        ]
        
        for rect, new_state in menu_rects:
            if rect.collidepoint(pos):
                if new_state == STATE_RACE:
                    # Go to roster with select racer mode
                    self.game.state = STATE_ROSTER
                    self.game.select_racer_mode = True
                else:
                    self.game.state = new_state
                break
    
    def _handle_roster_clicks(self, pos):
        """Handle clicks in roster state."""
        # Check for Menu button in header
        menu_rect = pygame.Rect(700, 5, 80, 30)
        if menu_rect.collidepoint(pos):
            self.game.state = STATE_MENU
            # Reset select racer mode when leaving
            self.game.select_racer_mode = False
            return
        
        # Check if we're in select racer mode
        select_racer_mode = getattr(self.game, "select_racer_mode", False)
        if select_racer_mode:
            # Check for bet button clicks
            if layout.BET_BTN_NONE_RECT.collidepoint(pos):
                self.game.current_bet = 0
                return
            elif layout.BET_BTN_5_RECT.collidepoint(pos):
                self.game.current_bet = 5
                return
            elif layout.BET_BTN_10_RECT.collidepoint(pos):
                self.game.current_bet = 10
                return
            
            # Check for turtle slot clicks to select racer
            for i, slot_rect in enumerate(layout.SLOT_RECTS):
                if slot_rect.collidepoint(pos):
                    turtle = self.game.roster[i]
                    if turtle:  # Only select if there's a turtle
                        # Set this turtle as the active racer
                        self.game.active_racer_index = i
                        # Start the race immediately
                        self.game.race_manager.start_race()
                        self.game.state = STATE_RACE
                        # Reset select racer mode
                        self.game.select_racer_mode = False
                    return
        
        # Normal roster handling
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
        elif action == "TRAINING":
            # Transition to training view
            self.game.state = STATE_TRAINING
        elif action == "PROFILE":
            # Transition to profile view
            self.game.state = STATE_PROFILE
            # Set profile turtle index based on clicked turtle
            self._set_profile_turtle_index(pos)
    
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
    
    def _set_profile_turtle_index(self, pos):
        """Set the profile turtle index based on click position."""
        from ui.views.profile_view import get_all_turtles
        
        all_turtles = get_all_turtles(self.game)
        if not all_turtles:
            return
        
        # Check which turtle was clicked
        show_retired = getattr(self.game, "show_retired_view", False)
        
        if not show_retired:
            # Active roster view
            for i, slot_rect in enumerate(layout.SLOT_RECTS):
                if slot_rect.collidepoint(pos) and i < len(self.game.roster) and self.game.roster[i]:
                    # Find this turtle in the all_turtles list
                    for j, turtle in enumerate(all_turtles):
                        if turtle == self.game.roster[i]:
                            self.game.profile_turtle_index = j
                            return
        else:
            # Retired view
            for i, slot_rect in enumerate(layout.SLOT_RECTS):
                if slot_rect.collidepoint(pos) and i < len(self.game.retired_roster):
                    # Find this turtle in the all_turtles list
                    for j, turtle in enumerate(all_turtles):
                        if turtle == self.game.retired_roster[i]:
                            self.game.profile_turtle_index = j
                            return
    
    def _handle_training_clicks(self, pos):
        """Handle clicks in training state."""
        # Check for Menu button in header
        menu_rect = pygame.Rect(700, 5, 80, 30)
        if menu_rect.collidepoint(pos):
            self.game.state = STATE_ROSTER
            return
        
        # Get the selected turtle
        active_racer_index = getattr(self.game, "active_racer_index", 0)
        turtle = self.game.roster[active_racer_index]
        
        if not turtle:
            return
        
        # Training buttons
        button_y = 250  # Starting y position for training buttons
        training_buttons = [
            ("speed", 50, button_y),
            ("energy", 300, button_y),
            ("recovery", 50, button_y + 60),
            ("swim", 300, button_y + 60),
            ("climb", 50, button_y + 120)
        ]
        
        for stat, x, y in training_buttons:
            button_rect = pygame.Rect(x, y, 200, 40)
            if button_rect.collidepoint(pos):
                # Perform training
                if turtle.train(stat):
                    print(f"Trained {turtle.name}! {stat.capitalize()} is now {turtle.stats[stat]}")
                    # Auto-retire turtles that reach age 100 via training
                    if turtle.age >= 100:
                        self.game.roster_manager.retire_turtle(active_racer_index)
                        print(f"{turtle.name} retired due to age!")
                    # Auto-save after training
                    self.game.auto_save("training")
                else:
                    print(f"{turtle.name} is too tired to train!")
                return
    
    def _handle_profile_clicks(self, pos):
        """Handle clicks in profile state."""
        from ui.views.profile_view import handle_profile_click
        result = handle_profile_click(self.game, pos, None, None, None)
        
        if result == "back":
            self.game.state = STATE_ROSTER
        elif result == "navigate_prev":
            # Navigate to previous turtle
            from ui.views.profile_view import get_all_turtles
            all_turtles = get_all_turtles(self.game)
            if all_turtles:
                current_index = getattr(self.game, 'profile_turtle_index', 0)
                self.game.profile_turtle_index = (current_index - 1) % len(all_turtles)
        elif result == "navigate_next":
            # Navigate to next turtle
            from ui.views.profile_view import get_all_turtles
            all_turtles = get_all_turtles(self.game)
            if all_turtles:
                current_index = getattr(self.game, 'profile_turtle_index', 0)
                self.game.profile_turtle_index = (current_index + 1) % len(all_turtles)
    
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
    
    def _handle_voting_clicks(self, pos):
        """Handle clicks in voting state."""
        from ui.voting_interface import handle_voting_click
        result = handle_voting_click(self.game, pos)
        
        if result == "back_to_menu":
            self.game.state = STATE_MENU
        elif result == "vote_completed":
            # Award $1 for completed vote
            self.game.money += 1
            # Auto-save after vote
            if hasattr(self.game, 'save_manager'):
                self.game.save_manager.auto_save()
        elif result == "back":
            self.game.state = STATE_MENU
    
    def handle_mouse_wheel(self, button):
        """Handle mouse wheel events."""
        if self.game.state == STATE_VOTING:
            if hasattr(self.game, 'voting_view'):
                self.game.voting_view.handle_event(pygame.event.Event(
                    pygame.MOUSEBUTTONDOWN, {'button': button}
                ))
