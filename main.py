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
from core.auto_load_system import auto_load_system

# --- MAIN GAME CLASS ---
class TurboShellsGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
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
        self.money = 100
        
        # State-specific data containers
        self.shop_inventory = []
        self.shop_message = ""
        
        self.race_results = []
        self.race_speed_multiplier = 1
        self.active_racer_index = 0
        
        self.breeding_parents = []
        self.current_bet = 0

        # Stable view mode: False = Active roster, True = Retired view
        self.show_retired_view = False

        self.mouse_pos = (0, 0)

        # --- MANAGERS ---
        self.renderer = Renderer(self.screen, self.font)
        self.roster_manager = RosterManager(self)
        self.shop_manager = ShopManager(self)
        self.race_manager = RaceManager(self)
        self.breeding_manager = BreedingManager(self)
        
        # Initialize shop with stock
        self.shop_manager.refresh_stock(free=True)
        
        # --- HANDLERS ---
        self.state_handler = StateHandler(self)
        self.keyboard_handler = KeyboardHandler(self)
        
        # --- AUTO-LOAD SYSTEM ---
        self.load_notification = None
        self._initialize_game_state()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Mouse Handling
            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left Click
                    self.state_handler.handle_click(event.pos)
                elif event.button in [4, 5]: # Mouse wheel
                    self.state_handler.handle_mouse_wheel(event.button)

            if event.type == pygame.KEYDOWN:
                self.keyboard_handler.handle_keydown(event)

    def update(self):
        if self.state == STATE_SHOP:
            self.shop_manager.update()

        if self.state == STATE_RACE:
            if self.race_manager.update():
                self.state = STATE_RACE_RESULT

    def draw(self):
        self.screen.fill(BLACK)
        
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
        
        pygame.display.flip()  # Make sure we update the display
    
    def _initialize_game_state(self):
        """Initialize game state using auto-load system"""
        try:
            # Perform auto-load
            success, error, loaded_data, notification = auto_load_system.auto_load()
            
            # Store notification for display
            self.load_notification = notification
            
            if success and loaded_data:
                game_data, turtles, preferences = loaded_data
                
                # Restore game state from loaded data
                self.money = game_data.game_state.money
                self.state = game_data.game_state.current_phase
                
                # Convert turtle data to game entities
                self.roster = [None] * 3  # Initialize empty roster
                self.retired_roster = []
                
                # Load active turtles
                for i, turtle_id in enumerate(game_data.roster.active_turtles[:3]):
                    if i < 3:
                        # Find corresponding turtle data
                        turtle_data = next((t for t in turtles if t.turtle_id == turtle_id), None)
                        if turtle_data:
                            self.roster[i] = Turtle(
                                turtle_data.name,
                                speed=turtle_data.stats.speed,
                                energy=turtle_data.stats.energy,
                                recovery=turtle_data.stats.recovery,
                                swim=turtle_data.stats.swim,
                                climb=turtle_data.stats.climb
                            )
                
                # Load retired turtles
                for turtle_id in game_data.roster.retired_turtles:
                    turtle_data = next((t for t in turtles if t.turtle_id == turtle_id), None)
                    if turtle_data:
                        self.retired_roster.append(Turtle(
                            turtle_data.name,
                            speed=turtle_data.stats.speed,
                            energy=turtle_data.stats.energy,
                            recovery=turtle_data.stats.recovery,
                            swim=turtle_data.stats.swim,
                            climb=turtle_data.stats.climb
                        ))
                
                print(f"Game loaded successfully for player {game_data.player_id}")
                print(f"Money: ${self.money}, Active turtles: {len([t for t in self.roster if t])}")
                
            else:
                # Keep default state for new game
                print(f"Starting new game: {error or 'No save file found'}")
                
        except Exception as e:
            print(f"Error during game state initialization: {e}")
            # Keep default state
            self.load_notification = {
                "type": "load_notification",
                "success": False,
                "message": f"Initialization error: {e}",
                "timestamp": "2025-11-22T00:00:00Z"
            }

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
        pygame.quit()
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        pygame.quit()
        sys.exit(1)