"""
Game State Manager for TurboShells
Handles game state initialization, loading, and saving logic
"""

from typing import Optional, Tuple, Dict, Any, List
from datetime import datetime, timezone
from game.entities import Turtle
from core.auto_load_system import auto_load_system
from managers.save_manager import SaveManager


class GameStateManager:
    """Manages game state initialization, loading, and persistence"""

    def __init__(self):
        self.save_manager = SaveManager()
        self.player_id = None
        self.load_notification = None

    def initialize_game_state(
        self,
    ) -> Tuple[bool, List[Turtle], List[Turtle], int, str, Dict[str, Any]]:
        """
        Initialize game state using auto-load system with separate roster loading

        Returns:
            Tuple of (success, roster, retired_roster, money, state, load_notification)
        """
        try:
            # Load roster separately first (this always works)
            roster, retired_roster = self.load_roster_separately()

            # Perform auto-load for game state (money, etc.)
            success, error, loaded_data, notification = auto_load_system.auto_load()

            # Store notification for display
            self.load_notification = notification

            if success and loaded_data:
                game_data, turtles, preferences = loaded_data

                # Convert dataclass objects to dictionaries for compatibility
                game_data_dict, turtles_dict = self._convert_loaded_data(
                    game_data, turtles
                )

                # Store player_id for save operations
                self.player_id = game_data_dict.get("player_id", "unknown")

                # Extract game state values
                game_state = game_data_dict.get("game_state", {})
                if hasattr(game_state, "__dict__"):
                    game_state = game_state.__dict__

                money = game_state.get("money", 100)
                state = "MENU"  # Always start on Main Menu, not saved state

                print(f"Game state loaded: Money=${money}, Phase={state}")
                print(
                    f"Roster loaded separately: {len([t for t in roster if t])} turtles"
                )

                return True, roster, retired_roster, money, state, notification

            else:
                # Keep default state for new game
                print(f"Starting new game: {error or 'No save file found'}")

                # If no roster loaded, create default
                if not any(roster):
                    roster = [
                        Turtle(
                            "Starter", speed=5, energy=100, recovery=5, swim=5, climb=5
                        ),
                        None,
                        None,
                    ]

                money = 100
                state = "MENU"

                return True, roster, retired_roster, money, state, notification

        except Exception as e:
            print(f"Error during game state initialization: {e}")
            import traceback

            traceback.print_exc()

            # Fallback state
            self.load_notification = {
                "type": "load_notification",
                "success": False,
                "message": f"Initialization error: {e}",
                "timestamp": "2025-11-22T00:00:00Z",
            }

            # Try to load roster separately at minimum
            try:
                roster, retired_roster = self.load_roster_separately()
                if not any(roster):
                    roster = [
                        Turtle(
                            "Starter", speed=5, energy=100, recovery=5, swim=5, climb=5
                        ),
                        None,
                        None,
                    ]
            except BaseException:
                roster = [
                    Turtle("Starter", speed=5, energy=100, recovery=5, swim=5, climb=5),
                    None,
                    None,
                ]
                retired_roster = []

            money = 100
            state = "MENU"

            return False, roster, retired_roster, money, state, self.load_notification

    def _convert_loaded_data(
        self, game_data: Any, turtles: Any
    ) -> Tuple[Dict, List[Dict]]:
        """Convert dataclass objects to dictionaries for compatibility"""
        # Convert game data to dict if needed
        if hasattr(game_data, "__dict__"):
            game_data_dict = game_data.__dict__
            # Convert nested dataclass objects
            if "game_state" in game_data_dict and hasattr(
                game_data_dict["game_state"], "__dict__"
            ):
                game_data_dict["game_state"] = game_data_dict["game_state"].__dict__
            if "roster" in game_data_dict and hasattr(
                game_data_dict["roster"], "__dict__"
            ):
                game_data_dict["roster"] = game_data_dict["roster"].__dict__
            if "economy" in game_data_dict and hasattr(
                game_data_dict["economy"], "__dict__"
            ):
                game_data_dict["economy"] = game_data_dict["economy"].__dict__
        else:
            game_data_dict = game_data

        # Convert turtle dataclasses to dicts if needed
        turtles_dict = []
        for turtle in turtles:
            if hasattr(turtle, "__dict__"):
                turtle_dict = turtle.__dict__
                # Convert nested dataclass objects to dicts
                if hasattr(turtle, "game_state") and hasattr(
                    turtle.game_state, "__dict__"
                ):
                    turtle_dict["game_state"] = turtle.game_state.__dict__
                if hasattr(turtle, "stats") and hasattr(turtle.stats, "__dict__"):
                    turtle_dict["stats"] = turtle.stats.__dict__
                    # Convert nested BaseStats and GeneticModifiers
                    if "base_stats" in turtle_dict["stats"] and hasattr(
                        turtle_dict["stats"]["base_stats"], "__dict__"
                    ):
                        turtle_dict["stats"]["base_stats"] = turtle_dict["stats"][
                            "base_stats"
                        ].__dict__
                    if "genetic_modifiers" in turtle_dict["stats"] and hasattr(
                        turtle_dict["stats"]["genetic_modifiers"], "__dict__"
                    ):
                        turtle_dict["stats"]["genetic_modifiers"] = turtle_dict[
                            "stats"
                        ]["genetic_modifiers"].__dict__
                turtles_dict.append(turtle_dict)
            else:
                turtles_dict.append(turtle)

        return game_data_dict, turtles_dict

    def _load_turtles_from_data(
        self, game_data: Dict, turtles: List[Dict]
    ) -> Tuple[List[Optional[Turtle]], List[Turtle]]:
        """Convert turtle data to game entities"""
        roster = [None] * 3  # Initialize empty roster
        retired_roster = []

        # Load active turtles
        active_turtle_ids = game_data.get("roster", {}).get("active_turtles", [])
        for i, turtle_id in enumerate(active_turtle_ids[:3]):
            if i < 3:
                # Find corresponding turtle data
                turtle_data = next(
                    (t for t in turtles if t.get("turtle_id") == turtle_id), None
                )
                if turtle_data:
                    # Handle both dict and dataclass turtle stats
                    turtle_stats = turtle_data.get("stats", {})
                    if hasattr(turtle_stats, "__dict__"):
                        # Convert dataclass to dict
                        turtle_stats = {
                            "speed": (
                                getattr(turtle_stats, "speed", {}).value
                                if hasattr(
                                    getattr(turtle_stats, "speed", None), "value"
                                )
                                else getattr(turtle_stats, "speed", 5)
                            ),
                            "max_energy": (
                                getattr(turtle_stats, "max_energy", {}).value
                                if hasattr(
                                    getattr(turtle_stats, "max_energy", None), "value"
                                )
                                else getattr(turtle_stats, "max_energy", 100)
                            ),
                            "recovery": (
                                getattr(turtle_stats, "recovery", {}).value
                                if hasattr(
                                    getattr(turtle_stats, "recovery", None), "value"
                                )
                                else getattr(turtle_stats, "recovery", 5)
                            ),
                            "swim": (
                                getattr(turtle_stats, "swim", {}).value
                                if hasattr(getattr(turtle_stats, "swim", None), "value")
                                else getattr(turtle_stats, "swim", 5)
                            ),
                            "climb": (
                                getattr(turtle_stats, "climb", {}).value
                                if hasattr(
                                    getattr(turtle_stats, "climb", None), "value"
                                )
                                else getattr(turtle_stats, "climb", 5)
                            ),
                            "age": getattr(turtle_stats, "age", 0),  # Load turtle age
                        }

                    roster[i] = Turtle(
                        turtle_data.get("name", "Unknown"),
                        speed=turtle_stats.get("speed", 5),
                        energy=turtle_stats.get("max_energy", 100),
                        recovery=turtle_stats.get("recovery", 5),
                        swim=turtle_stats.get("swim", 5),
                        climb=turtle_stats.get("climb", 5),
                    )
                    # Restore turtle age
                    roster[i].age = turtle_stats.get("age", 0)

        # Load retired turtles
        retired_turtle_ids = game_data.get("roster", {}).get("retired_turtles", [])
        for turtle_id in retired_turtle_ids:
            turtle_data = next(
                (t for t in turtles if t.get("turtle_id") == turtle_id), None
            )
            if turtle_data:
                # Handle both dict and dataclass turtle stats
                turtle_stats = turtle_data.get("stats", {})
                if hasattr(turtle_stats, "__dict__"):
                    # Convert dataclass to dict
                    turtle_stats = {
                        "speed": (
                            getattr(turtle_stats, "speed", {}).value
                            if hasattr(getattr(turtle_stats, "speed", None), "value")
                            else getattr(turtle_stats, "speed", 5)
                        ),
                        "max_energy": (
                            getattr(turtle_stats, "max_energy", {}).value
                            if hasattr(
                                getattr(turtle_stats, "max_energy", None), "value"
                            )
                            else getattr(turtle_stats, "max_energy", 100)
                        ),
                        "recovery": (
                            getattr(turtle_stats, "recovery", {}).value
                            if hasattr(getattr(turtle_stats, "recovery", None), "value")
                            else getattr(turtle_stats, "recovery", 5)
                        ),
                        "swim": (
                            getattr(turtle_stats, "swim", {}).value
                            if hasattr(getattr(turtle_stats, "swim", None), "value")
                            else getattr(turtle_stats, "swim", 5)
                        ),
                        "climb": (
                            getattr(turtle_stats, "climb", {}).value
                            if hasattr(getattr(turtle_stats, "climb", None), "value")
                            else getattr(turtle_stats, "climb", 5)
                        ),
                        "age": getattr(turtle_stats, "age", 0),  # Load turtle age
                    }

                retired_turtle = Turtle(
                    turtle_data.get("name", "Unknown"),
                    speed=turtle_stats.get("speed", 5),
                    energy=turtle_stats.get("max_energy", 100),
                    recovery=turtle_stats.get("recovery", 5),
                    swim=turtle_stats.get("swim", 5),
                    climb=turtle_stats.get("climb", 5),
                )
                # Restore turtle age and mark as retired
                retired_turtle.age = turtle_stats.get("age", 0)
                retired_turtle.is_active = False
                retired_roster.append(retired_turtle)

        return roster, retired_roster

    def create_save_data(
        self,
        roster: List[Optional[Turtle]],
        retired_roster: List[Turtle],
        money: int,
        state: str,
        race_results: List,
    ) -> Tuple[Any, List[Any], Any]:
        """
        Convert current game state to save data structures

        Returns:
            Tuple of (GameData, List[TurtleData], PlayerPreferences)
        """
        from core.data import (
            GameData,
            TurtleData,
            PlayerPreferences,
            create_default_preference_data,
            GameStateData,
            EconomicData,
            SessionStats,
            RosterData,
            LastSession,
            TurtleParents,
            GeneTrait,
            BaseStats,
            GeneticModifiers,
            TurtleStats,
            TerrainPerformance,
            TurtlePerformance,
            RaceResult,
        )
        from datetime import datetime, timezone

        # Ensure we have a player_id
        if not self.player_id:
            self.player_id = f"player_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create game state data
        game_state = GameStateData(
            money=money,
            current_phase=state,
            unlocked_features=["roster", "racing", "voting"],
            tutorial_progress={
                "roster_intro": True,
                "racing_basics": True,
                "breeding_intro": False,
                "voting_system": True,
            },
            session_stats=SessionStats(
                total_playtime_minutes=0,
                races_completed=len(race_results),
                turtles_bred=0,
                votes_cast=0,
            ),
        )

        # Convert turtles to data structures
        turtle_data_list = self._convert_turtles_to_save_data(roster, retired_roster)

        # Create game data object
        game_data = GameData(
            version="2.2.0",
            timestamp=datetime.now(timezone.utc).isoformat(),
            player_id=self.player_id,
            game_state=game_state,
            economy=EconomicData(
                total_earned=money, total_spent=0, transaction_history=[]
            ),
            roster=RosterData(
                active_slots=3,
                active_turtles=[f"turtle_{i:03d}" for i, t in enumerate(roster) if t],
                retired_turtles=[
                    f"turtle_retired_{i:03d}" for i in range(len(retired_roster))
                ],
                max_retired=20,
            ),
            last_sessions=[],
        )

        # Get or create preferences object
        preferences = create_default_preference_data(self.player_id)

        return game_data, turtle_data_list, preferences

    def _convert_turtles_to_save_data(
        self, roster: List[Optional[Turtle]], retired_roster: List[Turtle]
    ) -> List[Any]:
        """Convert turtle objects to TurtleData objects"""
        from core.data import (
            TurtleData,
            TurtleParents,
            GeneTrait,
            BaseStats,
            GeneticModifiers,
            TurtleStats,
            TerrainPerformance,
            TurtlePerformance,
        )

        turtle_data_list = []

        # Process active roster
        for i, turtle in enumerate(roster):
            if turtle:
                turtle_id = f"turtle_{i:03d}"
                turtle_data = self._create_turtle_data(turtle, turtle_id)
                turtle_data_list.append(turtle_data)

        # Process retired roster
        for i, turtle in enumerate(retired_roster):
            turtle_id = f"turtle_retired_{i:03d}"
            turtle_data = self._create_turtle_data(turtle, turtle_id)
            turtle_data_list.append(turtle_data)

        return turtle_data_list

    def _create_turtle_data(self, turtle: Turtle, turtle_id: str) -> Any:
        """Create TurtleData object for a single turtle"""
        from core.data import (
            TurtleData,
            TurtleParents,
            GeneTrait,
            BaseStats,
            GeneticModifiers,
            TurtleStats,
            TerrainPerformance,
            TurtlePerformance,
        )

        return TurtleData(
            turtle_id=turtle_id,
            name=turtle.name,
            generation=0,
            created_timestamp="2025-11-22T00:00:00Z",
            parents=TurtleParents(mother_id=None, father_id=None),
            genetics={
                "shell_pattern": GeneTrait(
                    value="hex", dominance=1.0, mutation_source="random"
                ),
                "shell_color": GeneTrait(
                    value="#4A90E2", dominance=1.0, mutation_source="random"
                ),
                "pattern_color": GeneTrait(
                    value="#E74C3C", dominance=1.0, mutation_source="random"
                ),
                "limb_shape": GeneTrait(
                    value="flippers", dominance=1.0, mutation_source="random"
                ),
                "limb_length": GeneTrait(
                    value=1.0, dominance=1.0, mutation_source="random"
                ),
                "head_size": GeneTrait(
                    value=1.0, dominance=1.0, mutation_source="random"
                ),
                "eye_color": GeneTrait(
                    value="#2ECC71", dominance=1.0, mutation_source="random"
                ),
                "skin_texture": GeneTrait(
                    value="smooth", dominance=1.0, mutation_source="random"
                ),
            },
            stats=TurtleStats(
                speed=turtle.speed,
                energy=turtle.max_energy,
                recovery=turtle.recovery,
                swim=turtle.swim,
                climb=turtle.climb,
                base_stats=BaseStats(
                    speed=turtle.speed,
                    energy=turtle.max_energy,
                    recovery=turtle.recovery,
                    swim=turtle.swim,
                    climb=turtle.climb,
                ),
                genetic_modifiers=GeneticModifiers(
                    speed=0, energy=0, recovery=0, swim=0, climb=0
                ),
                age=getattr(turtle, 'age', 0),  # Preserve turtle age
            ),
            performance=TurtlePerformance(
                race_history=[],
                total_races=0,
                wins=0,
                average_position=0.0,
                total_earnings=0,
            ),
        )

    def save_roster_separately(
        self, roster: List[Optional[Turtle]], retired_roster: List[Turtle]
    ) -> bool:
        """Save roster data separately to ensure persistence"""
        try:
            import json
            from pathlib import Path

            # Create simple roster data structure
            roster_data = {
                "active_roster": [
                    (
                        {
                            "name": turtle.name,
                            "speed": turtle.speed,
                            "max_energy": turtle.max_energy,
                            "recovery": turtle.recovery,
                            "swim": turtle.swim,
                            "climb": turtle.climb,
                            "age": getattr(turtle, 'age', 0),  # Include turtle age
                        }
                        if turtle
                        else None
                    )
                    for turtle in roster
                ],
                "retired_roster": [
                    {
                        "name": turtle.name,
                        "speed": turtle.speed,
                        "max_energy": turtle.max_energy,
                        "recovery": turtle.recovery,
                        "swim": turtle.swim,
                        "climb": turtle.climb,
                        "age": getattr(turtle, 'age', 0),  # Include turtle age
                    }
                    for turtle in retired_roster
                ],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            # Save to separate file
            save_dir = Path(self.save_manager._get_default_save_directory())
            save_dir.mkdir(parents=True, exist_ok=True)
            roster_file = save_dir / "roster_data.json"

            with open(roster_file, "w") as f:
                json.dump(roster_data, f, indent=2)

            print(f"Roster saved separately to {roster_file}")
            return True

        except Exception as e:
            print(f"Failed to save roster separately: {e}")
            return False

    def load_roster_separately(self) -> Tuple[List[Optional[Turtle]], List[Turtle]]:
        """Load roster data from separate file"""
        try:
            import json
            from pathlib import Path

            save_dir = Path(self.save_manager._get_default_save_directory())
            roster_file = save_dir / "roster_data.json"

            if not roster_file.exists():
                print("No separate roster file found")
                return [None, None, None], []

            with open(roster_file, "r") as f:
                roster_data = json.load(f)

            # Reconstruct turtles
            active_roster = []
            for turtle_data in roster_data.get("active_roster", []):
                if turtle_data:
                    turtle = Turtle(
                        name=turtle_data["name"],
                        speed=turtle_data["speed"],
                        energy=turtle_data["max_energy"],
                        recovery=turtle_data["recovery"],
                        swim=turtle_data["swim"],
                        climb=turtle_data["climb"],
                    )
                    # Restore turtle age
                    turtle.age = turtle_data.get("age", 0)
                    active_roster.append(turtle)
                else:
                    active_roster.append(None)

            retired_roster = []
            for turtle_data in roster_data.get("retired_roster", []):
                turtle = Turtle(
                    name=turtle_data["name"],
                    speed=turtle_data["speed"],
                    energy=turtle_data["max_energy"],
                    recovery=turtle_data["recovery"],
                    swim=turtle_data["swim"],
                    climb=turtle_data["climb"],
                )
                # Restore turtle age and mark as retired
                turtle.age = turtle_data.get("age", 0)
                turtle.is_active = False
                retired_roster.append(turtle)

            print(
                f"Loaded {len([t for t in active_roster if t])} active turtles and {len(retired_roster)} retired turtles"
            )
            return active_roster, retired_roster

        except Exception as e:
            print(f"Failed to load roster separately: {e}")
            return [None, None, None], []

    def auto_save(
        self,
        roster: List[Optional[Turtle]],
        retired_roster: List[Turtle],
        money: int,
        state: str,
        race_results: List,
        trigger: str = "manual",
    ) -> bool:
        """Auto-save game state"""
        try:
            # Save roster separately first
            self.save_roster_separately(roster, retired_roster)

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
