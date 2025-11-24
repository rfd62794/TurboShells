"""Keyboard input handling system for TurboShells game.

Centralizes all keyboard input logic and makes it easily maintainable.
"""

import pygame

# Import settings with fallback
try:
    from settings import *
except ImportError:
    try:
        from src.settings import *
    except ImportError:
        # Define basic settings if import fails
        SCREEN_WIDTH = 800
        SCREEN_HEIGHT = 600
        FPS = 60


class KeyboardHandler:
    """Handles all keyboard input for the game."""

    def __init__(self, game):
        self.game = game
        self.global_keys = {
            pygame.K_m: self._global_menu_key,
        }
        self.state_handlers = {
            STATE_MENU: self._handle_menu_keys,
            STATE_ROSTER: self._handle_roster_keys,
            STATE_SHOP: self._handle_shop_keys,
            STATE_RACE: self._handle_race_keys,
            STATE_RACE_RESULT: self._handle_race_result_keys,
            STATE_BREEDING: self._handle_breeding_keys,
        }

    def handle_keydown(self, event):
        """Handle keyboard key down events."""
        # Check global keys first
        if event.key in self.global_keys:
            self.global_keys[event.key]()
            return

        # Then check state-specific keys
        handler = self.state_handlers.get(self.game.state)
        if handler:
            handler(event)

    def _global_menu_key(self):
        """Global menu key - always returns to main menu."""
        self.game.state = STATE_MENU
        # Clear temporary opponents when returning to menu
        self._clear_temporary_opponents()

    def _clear_temporary_opponents(self):
        """Clear temporary opponents from roster."""
        if self.game.roster[1] and getattr(self.game.roster[1], "is_temp", False):
            self.game.roster[1] = None
        if self.game.roster[2] and getattr(self.game.roster[2], "is_temp", False):
            self.game.roster[2] = None

    def _handle_menu_keys(self, event):
        """Handle keys in main menu state."""
        key_actions = {
            pygame.K_r: lambda: self.game.state_handler.transition_to_roster(),
            pygame.K_s: lambda: self.game.state_handler.transition_to_shop(),
            pygame.K_b: lambda: self.game.state_handler.transition_to_breeding(),
        }

        if event.key in key_actions:
            key_actions[event.key]()

    def _handle_roster_keys(self, event):
        """Handle keys in roster state."""
        # Navigation keys
        nav_actions = {
            pygame.K_r: lambda: self.game.state_handler.transition_to_race(),
            pygame.K_s: lambda: self.game.state_handler.transition_to_shop(),
            pygame.K_b: lambda: self.game.state_handler.transition_to_breeding(),
        }

        # Turtle management keys
        turtle_actions = {
            pygame.K_4: lambda: self.game.roster_manager.retire_turtle(0),
            pygame.K_5: lambda: self.game.roster_manager.retire_turtle(1),
            pygame.K_6: lambda: self.game.roster_manager.retire_turtle(2),
            pygame.K_q: lambda: self.game.roster_manager.train_turtle(0),
            pygame.K_w: lambda: self.game.roster_manager.train_turtle(1),
            pygame.K_e: lambda: self.game.roster_manager.train_turtle(2),
            pygame.K_z: lambda: self.game.roster_manager.rest_turtle(0),
            pygame.K_x: lambda: self.game.roster_manager.rest_turtle(1),
            pygame.K_c: lambda: self.game.roster_manager.rest_turtle(2),
        }

        if event.key in nav_actions:
            nav_actions[event.key]()
        elif event.key in turtle_actions:
            turtle_actions[event.key]()

    def _handle_shop_keys(self, event):
        """Handle keys in shop state."""
        shop_actions = {
            pygame.K_r: lambda: self.game.shop_manager.refresh_stock(),
            pygame.K_1: lambda: self.game.shop_manager.buy_turtle(0),
            pygame.K_2: lambda: self.game.shop_manager.buy_turtle(1),
            pygame.K_3: lambda: self.game.shop_manager.buy_turtle(2),
        }

        if event.key in shop_actions:
            shop_actions[event.key]()

    def _handle_race_keys(self, event):
        """Handle keys during race."""
        speed_actions = {
            pygame.K_1: lambda: setattr(self.game, "race_speed_multiplier", 1),
            pygame.K_2: lambda: setattr(self.game, "race_speed_multiplier", 2),
            pygame.K_3: lambda: setattr(self.game, "race_speed_multiplier", 4),
        }

        if event.key in speed_actions:
            speed_actions[event.key]()

    def _handle_race_result_keys(self, event):
        """Handle keys in race result state."""
        if event.key == pygame.K_m:
            self.game.state = STATE_MENU
            self._clear_temporary_opponents()

    def _handle_breeding_keys(self, event):
        """Handle keys in breeding state."""
        breeding_actions = {
            pygame.K_1: lambda: self._toggle_breeding_parent(0),
            pygame.K_2: lambda: self._toggle_breeding_parent(1),
            pygame.K_3: lambda: self._toggle_breeding_parent(2),
            pygame.K_4: lambda: self._toggle_breeding_parent(3),
            pygame.K_5: lambda: self._toggle_breeding_parent(4),
            pygame.K_6: lambda: self._toggle_breeding_parent(5),
            pygame.K_RETURN: lambda: self._attempt_breeding(),
        }

        if event.key in breeding_actions:
            breeding_actions[event.key]()

    def _toggle_breeding_parent(self, index):
        """Toggle parent selection by index from breeding candidates."""
        candidates = self.game.breeding_manager._get_breeding_candidates()
        if index < len(candidates):
            turtle = candidates[index]
            self.game.breeding_manager._toggle_parent_by_turtle(turtle)

    def _attempt_breeding(self):
        """Attempt breeding and return to menu if successful."""
        if self.game.breeding_manager.breed():
            self.game.state = STATE_MENU
