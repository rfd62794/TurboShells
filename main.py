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
from managers.save_manager import SaveManager

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
        self.save_manager = SaveManager()
        self.player_id = None
        self._initialize_game_state()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_on_exit()
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
                
                # Convert dataclass to dict if needed
                if hasattr(game_data, '__dict__'):
                    game_data = game_data.__dict__
                if hasattr(preferences, '__dict__'):
                    preferences = preferences.__dict__
                
                # Convert turtle dataclasses to dicts if needed
                turtles_dict = []
                for turtle in turtles:
                    if hasattr(turtle, '__dict__'):
                        turtles_dict.append(turtle.__dict__)
                    else:
                        turtles_dict.append(turtle)
                turtles = turtles_dict
                
                # Store player_id for save operations
                self.player_id = game_data.get("player_id", "unknown")
                
                # Restore game state from loaded data
                self.money = game_data.get("game_state", {}).get("money", 100)
                self.state = game_data.get("game_state", {}).get("current_phase", STATE_MENU)
                
                # Convert turtle data to game entities
                self.roster = [None] * 3  # Initialize empty roster
                self.retired_roster = []
                
                # Load active turtles
                active_turtle_ids = game_data.get("roster", {}).get("active_turtles", [])
                for i, turtle_id in enumerate(active_turtle_ids[:3]):
                    if i < 3:
                        # Find corresponding turtle data
                        turtle_data = next((t for t in turtles if t.get("turtle_id") == turtle_id), None)
                        if turtle_data:
                            turtle_stats = turtle_data.get("stats", {})
                            self.roster[i] = Turtle(
                                turtle_data.get("name", "Unknown"),
                                speed=turtle_stats.get("speed", 5),
                                energy=turtle_stats.get("max_energy", 100),
                                recovery=turtle_stats.get("recovery", 5),
                                swim=turtle_stats.get("swim", 5),
                                climb=turtle_stats.get("climb", 5)
                            )
                
                # Load retired turtles
                retired_turtle_ids = game_data.get("roster", {}).get("retired_turtles", [])
                for turtle_id in retired_turtle_ids:
                    turtle_data = next((t for t in turtles if t.get("turtle_id") == turtle_id), None)
                    if turtle_data:
                        turtle_stats = turtle_data.get("stats", {})
                        self.retired_roster.append(Turtle(
                            turtle_data.get("name", "Unknown"),
                            speed=turtle_stats.get("speed", 5),
                            energy=turtle_stats.get("max_energy", 100),
                            recovery=turtle_stats.get("recovery", 5),
                            swim=turtle_stats.get("swim", 5),
                            climb=turtle_stats.get("climb", 5)
                        ))
                
                print(f"Game loaded successfully for player {self.player_id}")
                print(f"Money: ${self.money}, Active turtles: {len([t for t in self.roster if t])}")
                
            else:
                # Keep default state for new game
                print(f"Starting new game: {error or 'No save file found'}")
                # Ensure we have a starter turtle
                if not any(self.roster):  # If all slots are empty
                    self.roster[0] = Turtle("Starter", speed=5, energy=100, recovery=5, swim=5, climb=5)
                
        except Exception as e:
            print(f"Error during game state initialization: {e}")
            # Keep default state and ensure starter turtle
            self.load_notification = {
                "type": "load_notification",
                "success": False,
                "message": f"Initialization error: {e}",
                "timestamp": "2025-11-22T00:00:00Z"
            }
            # Ensure we have a starter turtle
            if not any(self.roster):  # If all slots are empty
                self.roster[0] = Turtle("Starter", speed=5, energy=100, recovery=5, swim=5, climb=5)

    def _create_save_data(self):
        """Convert current game state to save data structures"""
        from core.data import (
            GameData, TurtleData, PlayerPreferences, create_default_preference_data,
            GameStateData, EconomicData, SessionStats, RosterData, LastSession,
            TurtleParents, GeneTrait, BaseStats, GeneticModifiers, TurtleStats,
            TerrainPerformance, TurtlePerformance, RaceResult
        )
        from datetime import datetime, timezone
        
        # Ensure we have a player_id
        if not self.player_id:
            self.player_id = f"player_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Convert game state to dictionary
        game_state_dict = {
            "money": self.money,
            "current_phase": self.state,
            "unlocked_features": ["roster", "racing", "voting"],  # TODO: Track actual unlocked features
            "tutorial_progress": {
                "roster_intro": True,
                "racing_basics": True,
                "breeding_intro": False,
                "voting_system": True
            },
            "session_stats": {
                "total_playtime_minutes": 0,  # TODO: Track actual playtime
                "races_completed": len(self.race_results),
                "turtles_bred": 0,  # TODO: Track breeding count
                "votes_cast": 0  # TODO: Track voting count
            }
        }
        
        # Convert turtles to data structures
        active_turtles = []
        retired_turtles = []
        turtle_data_list = []
        
        # Process active roster
        for i, turtle in enumerate(self.roster):
            if turtle:
                turtle_id = f"turtle_{i:03d}"
                active_turtles.append(turtle_id)
                
                turtle_dict = {
                    "turtle_id": turtle_id,
                    "name": turtle.name,
                    "generation": 0,  # TODO: Track actual generation
                    "created_timestamp": "2025-11-22T00:00:00Z",  # TODO: Track actual creation time
                    "parents": None,  # TODO: Track actual parents
                    "genetics": {
                        "shell_pattern": {"value": "hex", "dominance": 1.0, "mutation_source": "random"},
                        "shell_color": {"value": "#4A90E2", "dominance": 1.0, "mutation_source": "random"},
                        "pattern_color": {"value": "#E74C3C", "dominance": 1.0, "mutation_source": "random"},
                        "limb_shape": {"value": "flippers", "dominance": 1.0, "mutation_source": "random"},
                        "limb_length": {"value": 1.0, "dominance": 1.0, "mutation_source": "random"},
                        "head_size": {"value": 1.0, "dominance": 1.0, "mutation_source": "random"},
                        "eye_color": {"value": "#2ECC71", "dominance": 1.0, "mutation_source": "random"},
                        "skin_texture": {"value": "smooth", "dominance": 1.0, "mutation_source": "random"}
                    },
                    "stats": {
                        "speed": turtle.speed,
                        "max_energy": turtle.max_energy,
                        "recovery": turtle.recovery,
                        "swim": turtle.swim,
                        "climb": turtle.climb,
                        "base_stats": {
                            "speed": turtle.speed,
                            "max_energy": turtle.max_energy,
                            "recovery": turtle.recovery,
                            "swim": turtle.swim,
                            "climb": turtle.climb
                        },
                        "genetic_modifiers": {"speed": 0, "max_energy": 0, "recovery": 0, "swim": 0, "climb": 0}
                    },
                    "performance": {
                        "race_history": [],
                        "total_races": 0,
                        "wins": 0,
                        "average_position": 0.0,
                        "total_earnings": 0
                    }
                }
                turtle_data_list.append(turtle_dict)
        
        # Process retired roster
        for i, turtle in enumerate(self.retired_roster):
            turtle_id = f"turtle_retired_{i:03d}"
            retired_turtles.append(turtle_id)
            
            turtle_dict = {
                "turtle_id": turtle_id,
                "name": turtle.name,
                "generation": 0,
                "created_timestamp": "2025-11-22T00:00:00Z",
                "parents": None,
                "genetics": {
                    "shell_pattern": {"value": "hex", "dominance": 1.0, "mutation_source": "random"},
                    "shell_color": {"value": "#4A90E2", "dominance": 1.0, "mutation_source": "random"},
                    "pattern_color": {"value": "#E74C3C", "dominance": 1.0, "mutation_source": "random"},
                    "limb_shape": {"value": "flippers", "dominance": 1.0, "mutation_source": "random"},
                    "limb_length": {"value": 1.0, "dominance": 1.0, "mutation_source": "random"},
                    "head_size": {"value": 1.0, "dominance": 1.0, "mutation_source": "random"},
                    "eye_color": {"value": "#2ECC71", "dominance": 1.0, "mutation_source": "random"},
                    "skin_texture": {"value": "smooth", "dominance": 1.0, "mutation_source": "random"}
                },
                "stats": {
                    "speed": turtle.speed,
                    "max_energy": turtle.max_energy,
                    "recovery": turtle.recovery,
                    "swim": turtle.swim,
                    "climb": turtle.climb,
                    "base_stats": {
                        "speed": turtle.speed,
                        "max_energy": turtle.max_energy,
                        "recovery": turtle.recovery,
                        "swim": turtle.swim,
                        "climb": turtle.climb
                    },
                    "genetic_modifiers": {"speed": 0, "max_energy": 0, "recovery": 0, "swim": 0, "climb": 0}
                },
                "performance": {
                    "race_history": [],
                    "total_races": 0,
                    "wins": 0,
                    "average_position": 0.0,
                    "total_earnings": 0
                }
            }
            turtle_data_list.append(turtle_dict)
        
        # Create game data dictionary
        game_data_dict = {
            "version": "2.2.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "player_id": self.player_id,
            "game_state": game_state_dict,
            "economy": {
                "total_earned": self.money,  # TODO: Track actual earnings
                "total_spent": 0,  # TODO: Track actual spending
                "transaction_history": []
            },
            "roster": {
                "active_slots": 3,
                "active_turtles": active_turtles,
                "retired_turtles": retired_turtles,
                "max_retired": 20
            },
            "last_sessions": []
        }
        
        # Get or create preferences dictionary
        preferences_dict = create_default_preference_data(self.player_id)
        if hasattr(preferences_dict, '__dict__'):
            # Convert dataclass to dict if needed
            preferences_dict = preferences_dict.__dict__
        
        return game_data_dict, turtle_data_list, preferences_dict
    
    def auto_save(self, trigger="manual"):
        """Auto-save game state"""
        try:
            game_data, turtles, preferences = self._create_save_data()
            success = self.save_manager.save_game(game_data, turtles, preferences)
            
            if success:
                print(f"Game auto-saved successfully (trigger: {trigger})")
            else:
                print(f"Auto-save failed (trigger: {trigger})")
                
            return success
            
        except Exception as e:
            print(f"Auto-save error: {e}")
            return False
    
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
        sys.exit(1)