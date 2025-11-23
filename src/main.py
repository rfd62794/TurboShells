"""Game orchestration: main loop and shared state container.

Defines the `TurboShellsGame` class, which owns global game state,
routes input to managers, and delegates drawing to the UI layer.
"""

import pygame
import sys
from settings import *
from core.game.entities import Turtle
from ui.renderer import Renderer
from managers.shop_manager import ShopManager
from managers.race_manager import RaceManager
from managers.breeding_manager import BreedingManager
from managers.roster_manager import RosterManager
from core.game.game_state import generate_random_turtle
from core.systems.state_handler import StateHandler
from core.game.keyboard_handler import KeyboardHandler
from core.systems.game_state_manager import GameStateManager
from managers.save_manager import SaveManager
from managers.settings_manager import SettingsManager

# --- MAIN GAME CLASS ---


class TurboShellsGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Turbo Shells MVP")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)

        self.state = STATE_MENU

        # --- SHARED STATE ---
        # This object will be passed to renderers and managers
        # Using self as the container for simplicity in MVP
        self.roster = [
            Turtle("Starter", speed=5, energy=100, recovery=5, swim=5, climb=5),
            None,
            None
        ]
        self.retired_roster = []
        self.money = 200

        # State-specific data containers
        self.shop_inventory = []
        self.shop_message = ""

        self.race_results = []
        self.race_speed_multiplier = 1
        self.active_racer_index = 0

        self.breeding_parents = []
        self.current_bet = 0
        self.select_racer_mode = False

        # Stable view mode: False = Active roster, True = Retired view
        self.show_retired_view = False

        self.mouse_pos = (0, 0)

        # --- MANAGERS ---
        self.renderer = Renderer(self.screen, self.font)
        self.roster_manager = RosterManager(self)
        self.shop_manager = ShopManager(self)
        self.race_manager = RaceManager(self)
        self.breeding_manager = BreedingManager(self)
        self.settings_manager = SettingsManager(self.screen.get_rect())

        # Initialize shop with stock
        self.shop_manager.refresh_stock(free=True)

        # --- HANDLERS ---
        self.state_handler = StateHandler(self)
        self.keyboard_handler = KeyboardHandler(self)

        # --- GAME STATE MANAGER ---
        self.game_state_manager = GameStateManager()
        self.load_notification = None
        self._initialize_game_state()

    def handle_input(self):
        for event in pygame.event.get():
            # Handle settings input first (it overlays everything)
            if self.settings_manager.is_visible():
                if self.settings_manager.handle_event(event):
                    continue  # Event was handled by settings

            if event.type == pygame.QUIT:
                self.save_on_exit()
                pygame.quit()
                sys.exit()

            # Handle window resize
            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                new_screen_rect = pygame.Rect(0, 0, event.w, event.h)
                self.settings_manager.update_screen_rect(new_screen_rect)
                continue

            # Mouse Handling
            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left Click
                    self.state_handler.handle_click(event.pos)
                elif event.button in [4, 5]:  # Mouse wheel
                    self.state_handler.handle_mouse_wheel(event.button)

            if event.type == pygame.KEYDOWN:
                # Check for settings toggle
                if event.key == pygame.K_ESCAPE:
                    self.settings_manager.toggle_settings()
                    continue

            # Handle other input based on game state
            # StateHandler handles clicks through handle_click() method above
            # No need for separate input handlers for each state

        # Draw settings overlay on top of everything
        if self.settings_manager.is_visible():
            self.settings_manager.draw(self.screen)

    def update(self):
        # Update settings manager (always active)
        self.settings_manager.update(1.0 / FPS)

        if self.state == STATE_SHOP:
            self.shop_manager.update()

        if self.state == STATE_RACE:
            if self.race_manager.update():
                self.state = STATE_RACE_RESULT

    def draw(self):
        self.screen.fill(BLACK)

        # Draw game content based on state
        if self.state == STATE_MENU:
            self.renderer.draw_main_menu(self)
        elif self.state == STATE_ROSTER:
            self.renderer.draw_menu(self)
        elif self.state == STATE_RACE:
            self.renderer.draw_race(self)
        elif self.state == STATE_RACE_RESULT:
            self.renderer.draw_race_result(self)
        elif self.state == STATE_SHOP:
            self.renderer.draw_shop(self)
        elif self.state == STATE_BREEDING:
            self.renderer.draw_breeding(self)
        elif self.state == STATE_PROFILE:
            self.renderer.draw_profile(self)
        elif self.state == STATE_VOTING:
            self.renderer.draw_voting(self)

        # Draw settings overlay on top of everything
        if self.settings_manager.is_visible():
            self.settings_manager.draw(self.screen)

        pygame.display.flip()  # Make sure we update the display

    def _initialize_game_state(self):
        """Initialize game state using GameStateManager"""
        success, roster, retired_roster, money, state, notification = self.game_state_manager.initialize_game_state()

        # Update game state
        self.roster = roster
        self.retired_roster = retired_roster
        self.money = money
        self.state = state
        self.load_notification = notification

    def auto_save(self, trigger="manual"):
        """Auto-save game state using GameStateManager"""
        print(f"[DEBUG] Auto-save triggered: {trigger}")
        print(f"[DEBUG] Roster before save: {[t.name if t else None for t in self.roster]}")
        print(f"[DEBUG] Money: ${self.money}")
        result = self.game_state_manager.auto_save(
            self.roster, self.retired_roster, self.money, self.state,
            self.race_results, trigger
        )
        print(f"[DEBUG] Auto-save result: {result}")
        return result

    def save_on_exit(self):
        """Save game when exiting"""
        print("Saving game on exit...")
        self.auto_save("exit")


# --- ENTRY POINT ---
if __name__ == "__main__":
    try:
        game = TurboShellsGame()
        while True:
            game.handle_input()
            game.update()
            game.draw()
            game.clock.tick(FPS)
    except KeyboardInterrupt:
        print("\nGame closed by user.")
        game.save_on_exit()
        pygame.quit()
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        game.save_on_exit()
        pygame.quit()
        sys.exit(1)  # Quality check test
