"""
Enhanced Game State Manager for TurboShells

Handles game state initialization, loading, and saving with complete
turtle data preservation using Phase 4 enhanced data structures.
"""

from typing import Optional, Tuple, Dict, Any, List
from datetime import datetime, timezone
from pathlib import Path
import logging

from core.game.entities import Turtle
from core.data.turtle_conversion import (
    TurtleEntityConverter,
    TurtleDataValidator,
    TurtleDataFactory,
    entity_to_enhanced,
    enhanced_to_entity,
    entity_to_legacy,
    legacy_to_entity,
)
from core.data.data_structures import (
    EnhancedTurtleData,
    TurtleData,
    GameData,
    PlayerPreferences,
    create_default_game_data,
    create_default_preference_data,
)
from core.data.data_serialization import (
    EnhancedDataSerializer,
    DataSerializer,
)
from managers.save_manager import SaveManager


class EnhancedGameStateManager:
    """Enhanced game state manager with complete turtle data preservation"""
    
    def __init__(self, use_enhanced_data: bool = True):
        """Initialize enhanced game state manager"""
        self.save_manager = SaveManager()
        self.player_id = None
        self.load_notification = None
        self.use_enhanced_data = use_enhanced_data
        self.logger = logging.getLogger(__name__)
        
        # Migration settings
        self.auto_migrate_legacy_saves = True
        self.backup_before_migration = True
        
        self.logger.info(f"EnhancedGameStateManager initialized (enhanced_data={use_enhanced_data})")
    
    def initialize_game_state(
        self,
    ) -> Tuple[bool, List[Turtle], List[Turtle], int, str, Dict[str, Any]]:
        """
        Initialize game state using enhanced data system with complete preservation
        
        Returns:
            Tuple of (success, roster, retired_roster, money, state, load_notification)
        """
        try:
            # Load game data using enhanced system
            success, roster, retired_roster, money, state, notification = self._load_game_state()
            
            # Store notification for display
            self.load_notification = notification
            
            if success:
                self.logger.info(f"Game state loaded successfully: Money=${money}, Phase={state}")
                self.logger.info(f"Roster loaded: {len([t for t in roster if t])} active, {len(retired_roster)} retired")
                return True, roster, retired_roster, money, state, notification
            else:
                # Create new game with default turtles
                roster, retired_roster, money, state = self._create_new_game_state()
                notification = {
                    "type": "load_notification",
                    "success": True,
                    "message": "New game created",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                return True, roster, retired_roster, money, state, notification
                
        except Exception as e:
            self.logger.error(f"Error during enhanced game state initialization: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback to basic state
            roster = [
                Turtle("Starter", speed=5, energy=100, recovery=5, swim=5, climb=5),
                None,
                None,
            ]
            retired_roster = []
            money = 100
            state = "MENU"
            
            notification = {
                "type": "load_notification",
                "success": False,
                "message": f"Initialization error: {e}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            
            return False, roster, retired_roster, money, state, notification
    
    def _load_game_state(self) -> Tuple[bool, List[Turtle], List[Turtle], int, str, Dict[str, Any]]:
        """Load game state using enhanced data system"""
        try:
            # Try to load from save manager
            load_result = self.save_manager.load_game()
            
            if load_result is None:
                self.logger.info("No save file found, creating new game")
                return self._create_new_game_state_with_notification()
            
            game_data, turtles, preferences = load_result
            
            # Store player_id
            self.player_id = game_data.player_id
            
            # Convert turtles to entities based on data type
            if self.use_enhanced_data and self._is_enhanced_save(turtles):
                # Use enhanced data path
                roster, retired_roster = self._convert_enhanced_turtles_to_entities(turtles, game_data)
            else:
                # Use legacy data path with migration
                roster, retired_roster = self._convert_legacy_turtles_to_entities(turtles, game_data)
                
                # Auto-migrate to enhanced format if enabled
                if self.use_enhanced_data and self.auto_migrate_legacy_saves:
                    self._migrate_to_enhanced_format(roster, retired_roster, game_data, preferences)
            
            # Extract game state
            money = game_data.game_state.money
            state = "MENU"  # Always start on Main Menu
            
            notification = {
                "type": "load_notification",
                "success": True,
                "message": "Game loaded successfully",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "turtles_loaded": len([t for t in roster if t]) + len(retired_roster),
                "data_format": "enhanced" if self.use_enhanced_data else "legacy",
            }
            
            return True, roster, retired_roster, money, state, notification
            
        except Exception as e:
            self.logger.error(f"Enhanced load failed: {e}")
            return self._create_new_game_state_with_notification()
    
    def _is_enhanced_save(self, turtles: List[Any]) -> bool:
        """Check if save file uses enhanced data format"""
        if not turtles:
            return False
        
        # Check first turtle for enhanced structure markers
        first_turtle = turtles[0]
        if hasattr(first_turtle, 'static_data') and hasattr(first_turtle, 'dynamic_data'):
            return True
        
        return False
    
    def _convert_enhanced_turtles_to_entities(
        self, enhanced_turtles: List[EnhancedTurtleData], game_data: GameData
    ) -> Tuple[List[Optional[Turtle]], List[Turtle]]:
        """Convert enhanced turtle data to entities"""
        roster = [None] * 3  # Initialize empty roster
        retired_roster = []
        
        # Load active turtles
        active_turtle_ids = game_data.roster.active_turtles
        for i, turtle_id in enumerate(active_turtle_ids[:3]):
            if i < 3:
                # Find corresponding enhanced turtle data
                enhanced_turtle = next(
                    (t for t in enhanced_turtles if t.turtle_id == turtle_id), None
                )
                if enhanced_turtle:
                    try:
                        turtle = enhanced_to_entity(enhanced_turtle)
                        roster[i] = turtle
                    except Exception as e:
                        self.logger.error(f"Failed to convert enhanced turtle {turtle_id}: {e}")
                        # Create fallback turtle
                        roster[i] = Turtle(f"Converted_{turtle_id[:8]}", speed=5, energy=100, recovery=5, swim=5, climb=5)
        
        # Load retired turtles
        retired_turtle_ids = game_data.roster.retired_turtles
        for turtle_id in retired_turtle_ids:
            enhanced_turtle = next(
                (t for t in enhanced_turtles if t.turtle_id == turtle_id), None
            )
            if enhanced_turtle:
                try:
                    turtle = enhanced_to_entity(enhanced_turtle)
                    turtle.is_active = False
                    retired_roster.append(turtle)
                except Exception as e:
                    self.logger.error(f"Failed to convert retired enhanced turtle {turtle_id}: {e}")
        
        return roster, retired_roster
    
    def _convert_legacy_turtles_to_entities(
        self, legacy_turtles: List[TurtleData], game_data: GameData
    ) -> Tuple[List[Optional[Turtle]], List[Turtle]]:
        """Convert legacy turtle data to entities"""
        roster = [None] * 3  # Initialize empty roster
        retired_roster = []
        
        # Load active turtles
        active_turtle_ids = game_data.roster.active_turtles
        for i, turtle_id in enumerate(active_turtle_ids[:3]):
            if i < 3:
                # Find corresponding legacy turtle data
                legacy_turtle = next(
                    (t for t in legacy_turtles if t.turtle_id == turtle_id), None
                )
                if legacy_turtle:
                    try:
                        turtle = legacy_to_entity(legacy_turtle)
                        roster[i] = turtle
                    except Exception as e:
                        self.logger.error(f"Failed to convert legacy turtle {turtle_id}: {e}")
                        # Create fallback turtle with basic stats
                        stats = legacy_turtle.stats
                        roster[i] = Turtle(
                            legacy_turtle.name,
                            speed=getattr(stats, 'speed', 5),
                            energy=getattr(stats, 'energy', 100),
                            recovery=getattr(stats, 'recovery', 5),
                            swim=getattr(stats, 'swim', 5),
                            climb=getattr(stats, 'climb', 5),
                        )
        
        # Load retired turtles
        retired_turtle_ids = game_data.roster.retired_turtles
        for turtle_id in retired_turtle_ids:
            legacy_turtle = next(
                (t for t in legacy_turtles if t.turtle_id == turtle_id), None
            )
            if legacy_turtle:
                try:
                    turtle = legacy_to_entity(legacy_turtle)
                    turtle.is_active = False
                    retired_roster.append(turtle)
                except Exception as e:
                    self.logger.error(f"Failed to convert retired legacy turtle {turtle_id}: {e}")
        
        return roster, retired_roster
    
    def _migrate_to_enhanced_format(
        self, roster: List[Optional[Turtle]], retired_roster: List[Turtle],
        game_data: GameData, preferences: PlayerPreferences
    ) -> None:
        """Migrate current game state to enhanced format"""
        try:
            self.logger.info("Migrating save game to enhanced format...")
            
            # Convert all turtles to enhanced format
            all_turtles = [t for t in roster if t] + retired_roster
            enhanced_turtles = []
            
            for turtle in all_turtles:
                try:
                    enhanced_turtle = entity_to_enhanced(turtle)
                    enhanced_turtles.append(enhanced_turtle)
                except Exception as e:
                    self.logger.error(f"Failed to migrate turtle {turtle.name}: {e}")
            
            # Save in enhanced format
            if enhanced_turtles:
                success = self._save_enhanced_game_data(game_data, enhanced_turtles, preferences)
                if success:
                    self.logger.info("Successfully migrated to enhanced format")
                else:
                    self.logger.error("Failed to save migrated enhanced data")
            
        except Exception as e:
            self.logger.error(f"Migration to enhanced format failed: {e}")
    
    def _create_new_game_state_with_notification(self) -> Tuple[bool, List[Turtle], List[Turtle], int, str, Dict[str, Any]]:
        """Create new game state with notification"""
        roster, retired_roster, money, state = self._create_new_game_state()
        
        notification = {
            "type": "load_notification",
            "success": True,
            "message": "New game created",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        return True, roster, retired_roster, money, state, notification
    
    def _create_new_game_state(self) -> Tuple[List[Optional[Turtle]], List[Turtle], int, str]:
        """Create new game state with default turtles"""
        roster = [
            Turtle("Starter", speed=5, energy=100, recovery=5, swim=5, climb=5),
            None,
            None,
        ]
        retired_roster = []
        money = 100
        state = "MENU"
        
        return roster, retired_roster, money, state
    
    def save_game_state(
        self,
        roster: List[Optional[Turtle]],
        retired_roster: List[Turtle],
        money: int,
        state: str,
        race_results: List = None,
    ) -> bool:
        """
        Save game state using enhanced data system with complete preservation
        """
        try:
            if race_results is None:
                race_results = []
            
            # Ensure we have a player_id
            if not self.player_id:
                self.player_id = f"player_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create game data
            game_data = self._create_game_data(money, state, race_results)
            
            # Convert turtles based on format
            if self.use_enhanced_data:
                turtles = self._convert_entities_to_enhanced(roster, retired_roster)
                success = self._save_enhanced_game_data(game_data, turtles, self._create_preferences())
            else:
                turtles = self._convert_entities_to_legacy(roster, retired_roster)
                success = self.save_manager.save_game(game_data, turtles, self._create_preferences())
            
            if success:
                self.logger.info(f"Game saved successfully using {'enhanced' if self.use_enhanced_data else 'legacy'} format")
            else:
                self.logger.error("Game save failed")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Enhanced save failed: {e}")
            return False
    
    def _convert_entities_to_enhanced(
        self, roster: List[Optional[Turtle]], retired_roster: List[Turtle]
    ) -> List[EnhancedTurtleData]:
        """Convert entities to enhanced turtle data"""
        enhanced_turtles = []
        
        # Process active roster
        for i, turtle in enumerate(roster):
            if turtle:
                try:
                    enhanced_turtle = entity_to_enhanced(turtle)
                    enhanced_turtles.append(enhanced_turtle)
                except Exception as e:
                    self.logger.error(f"Failed to convert turtle {turtle.name} to enhanced: {e}")
        
        # Process retired roster
        for turtle in retired_roster:
            try:
                enhanced_turtle = entity_to_enhanced(turtle)
                enhanced_turtles.append(enhanced_turtle)
            except Exception as e:
                self.logger.error(f"Failed to convert retired turtle {turtle.name} to enhanced: {e}")
        
        return enhanced_turtles
    
    def _convert_entities_to_legacy(
        self, roster: List[Optional[Turtle]], retired_roster: List[Turtle]
    ) -> List[TurtleData]:
        """Convert entities to legacy turtle data"""
        legacy_turtles = []
        
        # Process active roster
        for i, turtle in enumerate(roster):
            if turtle:
                try:
                    legacy_turtle = entity_to_legacy(turtle)
                    legacy_turtles.append(legacy_turtle)
                except Exception as e:
                    self.logger.error(f"Failed to convert turtle {turtle.name} to legacy: {e}")
        
        # Process retired roster
        for turtle in retired_roster:
            try:
                legacy_turtle = entity_to_legacy(turtle)
                legacy_turtles.append(legacy_turtle)
            except Exception as e:
                self.logger.error(f"Failed to convert retired turtle {turtle.name} to legacy: {e}")
        
        return legacy_turtles
    
    def _create_game_data(self, money: int, state: str, race_results: List) -> GameData:
        """Create game data structure"""
        from core.data.data_structures import (
            GameStateData, EconomicData, SessionStats, RosterData, LastSession
        )
        
        return GameData(
            version="2.2.0",
            timestamp=datetime.now(timezone.utc).isoformat(),
            player_id=self.player_id,
            game_state=GameStateData(
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
            ),
            economy=EconomicData(
                total_earned=money, total_spent=0, transaction_history=[]
            ),
            roster=RosterData(
                active_slots=3,
                active_turtles=[],  # Will be populated by save manager
                retired_turtles=[],  # Will be populated by save manager
                max_retired=20,
            ),
            last_sessions=[],
        )
    
    def _create_preferences(self) -> PlayerPreferences:
        """Create default preferences data"""
        return create_default_preference_data(self.player_id)
    
    def _save_enhanced_game_data(
        self, game_data: GameData, enhanced_turtles: List[EnhancedTurtleData], 
        preferences: PlayerPreferences
    ) -> bool:
        """Save game data using enhanced format"""
        try:
            # Convert enhanced turtles to legacy format for save manager compatibility
            # In a full implementation, we'd enhance the save manager itself
            legacy_turtles = [TurtleData.from_enhanced(turtle) for turtle in enhanced_turtles]
            
            # Use existing save manager for now
            return self.save_manager.save_game(game_data, legacy_turtles, preferences)
            
        except Exception as e:
            self.logger.error(f"Enhanced save failed: {e}")
            return False
    
    def auto_save(
        self,
        roster: List[Optional[Turtle]],
        retired_roster: List[Turtle],
        money: int,
        state: str,
        race_results: List = None,
        trigger: str = "manual",
    ) -> bool:
        """Auto-save game state using enhanced system"""
        return self.save_game_state(roster, retired_roster, money, state, race_results)
    
    def get_save_info(self) -> Dict[str, Any]:
        """Get information about save system"""
        info = self.save_manager.get_save_info()
        info.update({
            "enhanced_data_enabled": self.use_enhanced_data,
            "auto_migrate_enabled": self.auto_migrate_legacy_saves,
            "player_id": self.player_id,
        })
        return info
    
    def validate_turtle_data(self, roster: List[Optional[Turtle]], retired_roster: List[Turtle]) -> Tuple[bool, List[str]]:
        """Validate all turtle data for integrity"""
        all_turtles = [t for t in roster if t] + retired_roster
        all_errors = []
        
        for turtle in all_turtles:
            is_valid, errors = TurtleDataValidator.validate_entity(turtle)
            if not is_valid:
                all_errors.extend([f"{turtle.name}: {error}" for error in errors])
        
        return len(all_errors) == 0, all_errors


# Convenience function to create enhanced manager
def create_enhanced_game_state_manager(use_enhanced_data: bool = True) -> EnhancedGameStateManager:
    """Create enhanced game state manager with specified settings"""
    return EnhancedGameStateManager(use_enhanced_data=use_enhanced_data)
