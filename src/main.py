"""Game orchestration: main loop and shared state container.

Defines the `TurboShellsGame` class, which owns global game state,
routes input to managers, and delegates drawing to the UI layer.
"""

import pygame
import sys

# Import settings with fallback
try:
    from settings import *
except ImportError:
    try:
        from src.settings import *
    except ImportError:
        # Define basic settings if import fails
        SCREEN_WIDTH = 1024
        SCREEN_HEIGHT = 768
        FPS = 60
        BLACK = (0, 0, 0)
        STATE_MENU = "menu"
        STATE_ROSTER = "roster"
        STATE_RACE = "race"
        STATE_RACE_RESULT = "race_result"
        STATE_SHOP = "shop"
        STATE_BREEDING = "breeding"
        STATE_PROFILE = "profile"
        STATE_VOTING = "voting"
        AUTO_SAVE_INTERVAL = 300  # 5 minutes in seconds

from game.entities import Turtle
from ui.views.renderer import Renderer
from managers.shop_manager import ShopManager
from managers.race_manager import RaceManager
from managers.breeding_manager import BreedingManager
from managers.roster_manager import RosterManager
from game.game_state import generate_random_turtle
from core.systems.state_handler import StateHandler
from game.keyboard_handler import KeyboardHandler
from core.systems.game_state_manager import GameStateManager
from managers.save_manager import SaveManager
# from managers.settings_manager import SettingsManager # Legacy settings

# UI System imports
from ui.ui_manager import UIManager
from ui.panels.settings_panel import SettingsPanel
from ui.panels.main_menu_panel import MainMenuPanel
from ui.panels.shop_panel import ShopPanel
from ui.panels.roster_panel import RosterPanel
from ui.panels.race_hud_panel import RaceHUDPanel
from ui.panels.race_result_panel import RaceResultPanel
from ui.data_binding import DataBindingManager
from game.game_state_interface import TurboShellsGameStateInterface

# Monitoring system imports
from core.monitoring_system import monitoring_system
from core.monitoring_overlay import monitoring_overlay
from core.profiler import game_loop_profiler
from core.logging_config import GameLogger

# --- MAIN GAME CLASS ---


class TurboShellsGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE
        )
        pygame.display.set_caption("Turbo Shells MVP")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        
        # Initialize monitoring system
        self.game_logger = GameLogger("main")
        self.game_logger.info("Initializing TurboShells game...")
        
        # Start monitoring
        monitoring_system.start()
        self.game_logger.info("Monitoring system started")

        self.state = STATE_MENU

        # --- SHARED STATE ---
        # This object will be passed to renderers and managers
        # Using self as the container for simplicity in MVP
        self.roster = [
            Turtle("Starter", speed=5, energy=100, recovery=5, swim=5, climb=5),
            None,
            None,
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

        # --- UI SYSTEM ---
        self.ui_manager = UIManager(self.screen.get_rect())
        
        # Initialize UI Manager first
        if not self.ui_manager.initialize(self.screen):
            print("Warning: Failed to initialize UI Manager")
            
        # Initialize Game State Interface and Data Binding
        self.game_state_interface = TurboShellsGameStateInterface(self)
        self.data_binding_manager = DataBindingManager()
        
        # Create and Register Panels
        self.settings_panel = SettingsPanel(self.game_state_interface, self.data_binding_manager)
        self.ui_manager.register_panel("settings", self.settings_panel)
        
        self.main_menu_panel = MainMenuPanel(self.game_state_interface)
        self.ui_manager.register_panel("main_menu", self.main_menu_panel)
        
        self.shop_panel = ShopPanel(self.game_state_interface)
        self.ui_manager.register_panel("shop", self.shop_panel)
        
        self.roster_panel = RosterPanel(self.game_state_interface)
        self.ui_manager.register_panel("roster", self.roster_panel)
        
        self.race_hud_panel = RaceHUDPanel(self.game_state_interface)
        self.ui_manager.register_panel("race_hud", self.race_hud_panel)
        
        self.race_result_panel = RaceResultPanel(self.game_state_interface)
        self.ui_manager.register_panel("race_result", self.race_result_panel)
        
        # --- MANAGERS ---
        self.renderer = Renderer(self.screen, self.font)
        self.roster_manager = RosterManager(self)
        self.shop_manager = ShopManager(self)
        self.race_manager = RaceManager(self)
        self.breeding_manager = BreedingManager(self)
        # self.settings_manager = SettingsManager(self.screen.get_rect()) # Legacy

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
            # 1. UI Manager gets first priority (pygame_gui)
            if self.ui_manager.handle_event(event):
                # Even if consumed, we might want to process some global keys like ESC
                # But typically if UI consumes it, we stop.
                # However, for toggling the settings panel itself, we need to check keydown
                pass
            
            # Handle specific panel events if needed (e.g. SettingsPanel custom logic)
            # self.settings_panel.handle_event(event) # pygame_gui handles this internally mostly
            # self.main_menu_panel.handle_event(event) # Main menu custom handling
            
            # Pass events to active panels if they need custom handling
            if self.state == STATE_MENU:
                self.main_menu_panel.handle_event(event)
            elif self.state == STATE_SHOP:
                self.shop_panel.handle_event(event)
            elif self.state == STATE_ROSTER:
                self.roster_panel.handle_event(event)
            elif self.state == STATE_RACE:
                self.race_hud_panel.handle_event(event)
            elif self.state == STATE_RACE_RESULT:
                self.race_result_panel.handle_event(event)
            
            # 2. Handle monitoring overlay input
            monitoring_overlay.handle_key_event(event)
            
            # 3. Core game events
            if event.type == pygame.QUIT:
                self.save_on_exit()
                monitoring_system.stop()
                if self.ui_manager:
                    self.ui_manager.shutdown()
                pygame.quit()
                sys.exit()

            # 4. Window resize handling
            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(
                    (event.w, event.h), pygame.RESIZABLE
                )
                new_screen_rect = pygame.Rect(0, 0, event.w, event.h)
                # self.settings_manager.update_screen_rect(new_screen_rect)
                self.ui_manager.handle_screen_resize(new_screen_rect)
                continue

            # 5. Mouse handling (for legacy systems)
            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Only process game clicks if UI didn't consume event
                # We can check if mouse is over any UI window, but pygame_gui consumes event if so.
                # Since we passed event to ui_manager.handle_event above, we should check return value.
                # But handle_event returns bool.
                # Let's refine step 1.
                pass
                
                if event.button == 1:  # Left Click
                    self.state_handler.handle_click(event.pos)
                elif event.button in [4, 5]:  # Mouse wheel
                    self.state_handler.handle_mouse_wheel(event.button)

            # 6. Keyboard handling (legacy)
            if event.type == pygame.KEYDOWN:
                # Check for settings toggle
                if event.key == pygame.K_ESCAPE:
                    self.ui_manager.toggle_panel("settings")
                    continue
                
                # Handle other keyboard input through keyboard handler
                self.keyboard_handler.handle_keydown(event)

        # Draw settings overlay on top of everything (Legacy)
        # if self.settings_manager.is_visible():
        #     self.settings_manager.draw(self.screen)

    def update(self):
        # Start frame profiling
        game_loop_profiler.start_frame()
        
        try:
            # Calculate time delta
            time_delta = self.clock.get_time() / 1000.0
            
            # Update monitoring overlay
            current_time = pygame.time.get_ticks() / 1000.0
            monitoring_overlay.update(current_time)
            
            # Update UI Manager
            self.ui_manager.update(time_delta)
            
            # Manage Panel Visibility based on State
            if self.state == STATE_MENU:
                if not self.main_menu_panel.visible:
                    self.main_menu_panel.show()
            else:
                if self.main_menu_panel.visible:
                    self.main_menu_panel.hide()
                    
            if self.state == STATE_SHOP:
                if not self.shop_panel.visible:
                    self.shop_panel.show()
            else:
                if self.shop_panel.visible:
                    self.shop_panel.hide()
                    
            if self.state == STATE_ROSTER:
                if not self.roster_panel.visible:
                    self.roster_panel.show()
            else:
                if self.roster_panel.visible:
                    self.roster_panel.hide()
                    
            if self.state == STATE_RACE:
                if not self.race_hud_panel.visible:
                    self.race_hud_panel.show()
            else:
                if self.race_hud_panel.visible:
                    self.race_hud_panel.hide()
                    
            if self.state == STATE_RACE_RESULT:
                if not self.race_result_panel.visible:
                    self.race_result_panel.show()
            else:
                if self.race_result_panel.visible:
                    self.race_result_panel.hide()
            
            # Update settings manager (legacy)
            # self.settings_manager.update(1.0 / FPS)

            if self.state == STATE_SHOP:
                self.shop_manager.update()
            elif self.state == STATE_RACE:
                race_finished = self.race_manager.update()
                if race_finished:
                    self.state = STATE_RACE_RESULT
                
            # Auto-save periodically
            if pygame.time.get_ticks() % (AUTO_SAVE_INTERVAL * 1000) < 16:  # Every AUTO_SAVE_INTERVAL seconds
                self.auto_save("periodic")
                
        except Exception as e:
            # Report error to monitoring system
            monitoring_system.error_monitor.report_error(e, "game_update", {
                "state": self.state,
                "money": self.money,
                "roster_size": len([t for t in self.roster if t is not None])
            })
            self.game_logger.error(f"Error in game update: {e}")
            raise
        finally:
            # End frame profiling
            game_loop_profiler.end_frame()

    def draw(self):
        # 1. Clear screen (PyGame)
        self.screen.fill(BLACK)

        # 2. Render game world (PyGame - sprites, entities)
        # Only draw legacy menu if we are NOT using the new panel (or maybe draw background?)
        # For now, let's disable legacy menu drawing to avoid overlap/confusion
        if self.state == STATE_MENU:
            # self.renderer.draw_main_menu(self) # Replaced by MainMenuPanel
            pass
        elif self.state == STATE_ROSTER:
            # self.renderer.draw_menu(self) # Replaced by RosterPanel
            pass
        elif self.state == STATE_RACE:
            self.renderer.draw_race(self) # Only draws world now
        elif self.state == STATE_RACE_RESULT:
            # self.renderer.draw_race_result(self) # Replaced by RaceResultPanel
            pass
        elif self.state == STATE_SHOP:
            # self.renderer.draw_shop(self) # Replaced by ShopPanel
            pass
        elif self.state == STATE_BREEDING:
            self.renderer.draw_breeding(self)
        elif self.state == STATE_PROFILE:
            self.renderer.draw_profile(self)
        elif self.state == STATE_VOTING:
            self.renderer.draw_voting(self)

        # 3. Render UI overlay (pygame_gui)
        self.ui_manager.draw_ui(self.screen)

        # 4. Draw legacy overlays on top
        # if self.settings_manager.is_visible():
        #     self.settings_manager.draw(self.screen)
            
        # 5. Draw monitoring overlay on top of everything
        monitoring_overlay.render(self.screen)

        # 6. Final PyGame display flip
        pygame.display.flip()

    def _initialize_game_state(self):
        """Initialize game state using GameStateManager"""
        success, roster, retired_roster, money, state, notification = (
            self.game_state_manager.initialize_game_state()
        )

        # Update game state
        self.roster = roster
        self.retired_roster = retired_roster
        self.money = money
        self.state = state
        self.load_notification = notification

    def auto_save(self, trigger="manual"):
        """Auto-save game state using GameStateManager"""
        print(f"[DEBUG] Auto-save triggered: {trigger}")
        print(
            f"[DEBUG] Roster before save: {[t.name if t else None for t in self.roster]}"
        )
        print(f"[DEBUG] Money: ${self.money}")
        result = self.game_state_manager.auto_save(
            self.roster,
            self.retired_roster,
            self.money,
            self.state,
            self.race_results,
            trigger,
        )
        print(f"[DEBUG] Auto-save result: {result}")
        return result

    def save_on_exit(self):
        """Save game when exiting"""
        print("Saving game on exit...")
        self.auto_save("exit")
        
        # Clean up UI system
        if self.ui_manager:
            self.ui_manager.shutdown()


# --- ENTRY POINT ---
if __name__ == "__main__":
    try:
        game = TurboShellsGame()
        
        # Log game start
        game.game_logger.info("Starting TurboShells main game loop")
        
        while True:
            game.handle_input()
            game.update()
            game.draw()
            game.clock.tick(FPS)
            
    except KeyboardInterrupt:
        print("\nGame closed by user.")
        game.save_on_exit()
        monitoring_system.stop()
        pygame.quit()
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        # Report error to monitoring system
        try:
            monitoring_system.error_monitor.report_error(e, "main_loop")
        except:
            pass  # Monitoring system might not be available
        game.save_on_exit()
        monitoring_system.stop()
        pygame.quit()
        sys.exit(1)  # Quality check test
