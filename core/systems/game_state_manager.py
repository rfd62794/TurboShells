"""
Game State Manager for TurboShells
Handles game state initialization, loading, and saving logic
"""

from typing import Optional, Tuple, Dict, Any, List
from core.game.entities import Turtle
from core.auto_load_system import auto_load_system
from managers.save_manager import SaveManager


class GameStateManager:
    """Manages game state initialization, loading, and persistence"""
    
    def __init__(self):
        self.save_manager = SaveManager()
        self.player_id = None
        self.load_notification = None
    
    def initialize_game_state(self) -> Tuple[bool, List[Turtle], List[Turtle], int, str, Dict[str, Any]]:
        """
        Initialize game state using auto-load system
        
        Returns:
            Tuple of (success, roster, retired_roster, money, state, load_notification)
        """
        try:
            # Perform auto-load
            success, error, loaded_data, notification = auto_load_system.auto_load()
            
            # Store notification for display
            self.load_notification = notification
            
            if success and loaded_data:
                game_data, turtles, preferences = loaded_data
                
                # Convert dataclass to dict if needed
                game_data, turtles = self._convert_loaded_data(game_data, turtles)
                
                # Store player_id for save operations
                self.player_id = game_data.get("player_id", "unknown")
                
                # Restore game state from loaded data
                money = game_data.get("game_state", {}).get("money", 100)
                state = game_data.get("game_state", {}).get("current_phase", "MENU")
                
                # Convert turtle data to game entities
                roster, retired_roster = self._load_turtles_from_data(game_data, turtles)
                
                print(f"Game loaded successfully for player {self.player_id}")
                print(f"Money: ${money}, Active turtles: {len([t for t in roster if t])}")
                
                return True, roster, retired_roster, money, state, notification
                
            else:
                # Keep default state for new game
                print(f"Starting new game: {error or 'No save file found'}")
                
                # Create default roster with starter turtle
                roster = [Turtle("Starter", speed=5, energy=100, recovery=5, swim=5, climb=5), None, None]
                retired_roster = []
                money = 100
                state = "MENU"
                
                return True, roster, retired_roster, money, state, notification
                
        except Exception as e:
            print(f"Error during game state initialization: {e}")
            
            # Fallback state
            self.load_notification = {
                "type": "load_notification",
                "success": False,
                "message": f"Initialization error: {e}",
                "timestamp": "2025-11-22T00:00:00Z"
            }
            
            roster = [Turtle("Starter", speed=5, energy=100, recovery=5, swim=5, climb=5), None, None]
            retired_roster = []
            money = 100
            state = "MENU"
            
            return False, roster, retired_roster, money, state, self.load_notification
    
    def _convert_loaded_data(self, game_data: Any, turtles: Any) -> Tuple[Dict, List[Dict]]:
        """Convert dataclass objects to dictionaries for compatibility"""
        # Convert game data to dict if needed
        if hasattr(game_data, '__dict__'):
            game_data = game_data.__dict__
        
        # Convert turtle dataclasses to dicts if needed
        turtles_dict = []
        for turtle in turtles:
            if hasattr(turtle, '__dict__'):
                turtles_dict.append(turtle.__dict__)
            else:
                turtles_dict.append(turtle)
        
        return game_data, turtles_dict
    
    def _load_turtles_from_data(self, game_data: Dict, turtles: List[Dict]) -> Tuple[List[Optional[Turtle]], List[Turtle]]:
        """Convert turtle data to game entities"""
        roster = [None] * 3  # Initialize empty roster
        retired_roster = []
        
        # Load active turtles
        active_turtle_ids = game_data.get("roster", {}).get("active_turtles", [])
        for i, turtle_id in enumerate(active_turtle_ids[:3]):
            if i < 3:
                # Find corresponding turtle data
                turtle_data = next((t for t in turtles if t.get("turtle_id") == turtle_id), None)
                if turtle_data:
                    turtle_stats = turtle_data.get("stats", {})
                    roster[i] = Turtle(
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
                retired_roster.append(Turtle(
                    turtle_data.get("name", "Unknown"),
                    speed=turtle_stats.get("speed", 5),
                    energy=turtle_stats.get("max_energy", 100),
                    recovery=turtle_stats.get("recovery", 5),
                    swim=turtle_stats.get("swim", 5),
                    climb=turtle_stats.get("climb", 5)
                ))
        
        return roster, retired_roster
    
    def create_save_data(self, roster: List[Optional[Turtle]], retired_roster: List[Turtle], 
                        money: int, state: str, race_results: List) -> Tuple[Dict, List[Dict], Dict]:
        """
        Convert current game state to save data structures
        
        Returns:
            Tuple of (game_data_dict, turtle_data_list, preferences_dict)
        """
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
            "money": money,
            "current_phase": state,
            "unlocked_features": ["roster", "racing", "voting"],
            "tutorial_progress": {
                "roster_intro": True,
                "racing_basics": True,
                "breeding_intro": False,
                "voting_system": True
            },
            "session_stats": {
                "total_playtime_minutes": 0,
                "races_completed": len(race_results),
                "turtles_bred": 0,
                "votes_cast": 0
            }
        }
        
        # Convert turtles to data structures
        turtle_data_list = self._convert_turtles_to_save_data(roster, retired_roster)
        
        # Create game data dictionary
        game_data_dict = {
            "version": "2.2.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "player_id": self.player_id,
            "game_state": game_state_dict,
            "economy": {
                "total_earned": money,
                "total_spent": 0,
                "transaction_history": []
            },
            "roster": {
                "active_slots": 3,
                "active_turtles": [f"turtle_{i:03d}" for i, t in enumerate(roster) if t],
                "retired_turtles": [f"turtle_retired_{i:03d}" for i in range(len(retired_roster))],
                "max_retired": 20
            },
            "last_sessions": []
        }
        
        # Get or create preferences dictionary
        preferences_dict = create_default_preference_data(self.player_id)
        if hasattr(preferences_dict, '__dict__'):
            preferences_dict = preferences_dict.__dict__
        
        return game_data_dict, turtle_data_list, preferences_dict
    
    def _convert_turtles_to_save_data(self, roster: List[Optional[Turtle]], 
                                    retired_roster: List[Turtle]) -> List[Dict]:
        """Convert turtle objects to save data dictionaries"""
        turtle_data_list = []
        
        # Process active roster
        for i, turtle in enumerate(roster):
            if turtle:
                turtle_id = f"turtle_{i:03d}"
                turtle_dict = self._create_turtle_dict(turtle, turtle_id)
                turtle_data_list.append(turtle_dict)
        
        # Process retired roster
        for i, turtle in enumerate(retired_roster):
            turtle_id = f"turtle_retired_{i:03d}"
            turtle_dict = self._create_turtle_dict(turtle, turtle_id)
            turtle_data_list.append(turtle_dict)
        
        return turtle_data_list
    
    def _create_turtle_dict(self, turtle: Turtle, turtle_id: str) -> Dict:
        """Create save data dictionary for a single turtle"""
        return {
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
    
    def auto_save(self, roster: List[Optional[Turtle]], retired_roster: List[Turtle],
                  money: int, state: str, race_results: List, trigger: str = "manual") -> bool:
        """Auto-save game state"""
        try:
            game_data, turtles, preferences = self.create_save_data(
                roster, retired_roster, money, state, race_results
            )
            success = self.save_manager.save_game(game_data, turtles, preferences)
            
            if success:
                print(f"Game auto-saved successfully (trigger: {trigger})")
            else:
                print(f"Auto-save failed (trigger: {trigger})")
                
            return success
            
        except Exception as e:
            print(f"Auto-save error: {e}")
            return False
