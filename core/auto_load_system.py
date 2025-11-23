"""
Auto-Load System for TurboShells

Handles automatic loading of save files on game startup with validation,
fallback handling, and user notification.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timezone

from core.data import (
    GameData, TurtleData, PlayerPreferences,
    DataValidator, DataMigrator
)
from managers.save_manager import SaveManager


class AutoLoadSystem:
    """Handles automatic loading of save files on startup"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validator = DataValidator()
        self.migrator = DataMigrator()
        self.save_manager = SaveManager()
        
        # Load states
        self.load_successful = False
        self.load_error = None
        self.loaded_data = None
        self.save_file_info = None
    
    def check_for_save_file(self) -> bool:
        """Check if save file exists on game launch"""
        try:
            save_path = self.save_manager.primary_save_path
            
            if save_path.exists():
                self.logger.info(f"Save file found at {save_path}")
                return True
            else:
                self.logger.info("No save file found - starting new game")
                return False
                
        except Exception as e:
            self.logger.error(f"Error checking for save file: {e}")
            return False
    
    def validate_save_file(self, save_path: Optional[Path] = None) -> Tuple[bool, Optional[str]]:
        """Verify save file integrity and compatibility"""
        try:
            path = save_path or self.save_manager.primary_save_path
            
            if not path.exists():
                return False, "Save file not found"
            
            # Use save manager's validation
            is_valid = self.save_manager.validate_save_file(str(path))
            
            if not is_valid:
                return False, "Save file validation failed"
            
            # Try to read and validate the data structure
            try:
                # Use SaveManager's built-in validation and loading
                result = self.save_manager.load_game()
                if result is None:
                    return False, "Failed to load save file data"
                
                game_data, turtles, preferences = result
                
                # SaveManager already validates the data, so if we got here it's valid
                return True, None
                
            except Exception as e:
                return False, f"Save file structure validation failed: {e}"
                
        except Exception as e:
            self.logger.error(f"Save file validation error: {e}")
            return False, f"Validation error: {e}"
    
    def restore_game_state(self) -> Tuple[bool, Optional[str], Optional[Tuple[GameData, list[TurtleData], PlayerPreferences]]]:
        """Restore complete game state from save"""
        try:
            self.logger.info("Attempting to restore game state from save file")
            
            # Load the game data
            result = self.save_manager.load_game()
            
            if result is None:
                return False, "Failed to load save file", None
            
            game_data, turtles, preferences = result
            
            # Validate loaded data (they should be dataclass objects)
            game_valid, game_error = self.validator.validate_game_data(game_data.__dict__)
            if not game_valid:
                return False, f"Invalid game data: {game_error}", None
            
            for i, turtle in enumerate(turtles):
                turtle_valid, turtle_error = self.validator.validate_turtle_data(turtle.__dict__)
                if not turtle_valid:
                    return False, f"Invalid turtle data for turtle {i+1}: {turtle_error}", None
            
            pref_valid, pref_error = self.validator.validate_preference_data(preferences.__dict__)
            if not pref_valid:
                return False, f"Invalid preference data: {pref_error}", None
            
            # Store as loaded data
            self.loaded_data = (game_data, turtles, preferences)
            self.load_successful = True
            self.load_error = None
            self.save_file_info = {
                "file_path": str(self.save_manager.primary_save_path),
                "file_size": self.save_manager.primary_save_path.stat().st_size,
                "last_modified": datetime.fromtimestamp(self.save_manager.primary_save_path.stat().st_mtime, timezone.utc).isoformat()
            }
            
            self.logger.info(f"Successfully restored game state for player {game_data.player_id}")
            return True, None, (game_data, turtles, preferences)
            
        except Exception as e:
            self.logger.error(f"Failed to restore game state: {e}")
            return False, f"Failed to restore game state: {e}", None
    
    def handle_corrupted_save(self) -> Tuple[bool, Optional[str], Optional[Tuple[GameData, list[TurtleData], PlayerPreferences]]]:
        """Handle corrupted or missing save files"""
        try:
            self.logger.warning("Handling corrupted save file")
            
            # Try to load from backup
            if self.save_manager.backup_save_path.exists():
                self.logger.info("Attempting to load from backup file")
                
                # Temporarily switch to backup
                original_primary = self.save_manager.primary_save_path
                self.save_manager.primary_save_path = self.save_manager.backup_save_path
                
                try:
                    result = self.restore_game_state()
                    if result[0]:  # If successful
                        # Restore backup as primary
                        self.save_manager.primary_save_path = original_primary
                        self.save_manager._create_backup()
                        import shutil
                        shutil.copy2(self.save_manager.backup_save_path, self.save_manager.primary_save_path)
                        
                        self.logger.info("Successfully restored from backup")
                        return result
                        
                finally:
                    # Always restore original path
                    self.save_manager.primary_save_path = original_primary
            
            # If backup also fails, create new game
            self.logger.info("Creating new game due to corrupted save")
            return self.create_new_game()
            
        except Exception as e:
            error_msg = f"Failed to handle corrupted save: {e}"
            self.logger.error(error_msg)
            return False, error_msg, None
    
    def create_new_game(self) -> Tuple[bool, Optional[str], Optional[Tuple[GameData, list[TurtleData], PlayerPreferences]]]:
        """Create new game when no save is available"""
        try:
            from core.data import create_default_game_data, create_default_turtle_data, create_default_preference_data
            
            self.logger.info("Creating new game")
            
            # Generate unique player ID
            player_id = f"player_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create default data
            game_data = create_default_game_data(player_id)
            preferences = create_default_preference_data(player_id)
            turtles = []  # Start with empty roster
            
            # Store as loaded data
            self.loaded_data = (game_data, turtles, preferences)
            self.load_successful = True
            self.load_error = None
            self.save_file_info = None
            
            self.logger.info(f"Created new game for player {player_id}")
            return True, None, (game_data, turtles, preferences)
            
        except Exception as e:
            error_msg = f"Failed to create new game: {e}"
            self.logger.error(error_msg)
            return False, error_msg, None
    
    def notify_user(self, success: bool, message: Optional[str] = None) -> Dict[str, Any]:
        """Inform user about load status"""
        notification = {
            "type": "load_notification",
            "success": success,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": message
        }
        
        if success and self.loaded_data:
            game_data, turtles, preferences = self.loaded_data
            
            # Handle both dataclass and dict formats
            if hasattr(game_data, 'game_state'):
                if hasattr(game_data.game_state, 'money'):
                    money = game_data.game_state.money
                else:
                    money = game_data.game_state.get('money', 0)
            else:
                money = game_data.get('game_state', {}).get('money', 0)
            
            # Simple notification without complex attribute access
            notification.update({
                "player_id": getattr(game_data, 'player_id', 'unknown'),
                "game_version": getattr(game_data, 'version', 'unknown'),
                "save_timestamp": getattr(game_data, 'timestamp', 'unknown'),
                "money": money,
                "active_turtles": len(turtles) if turtles else 0,
                "retired_turtles": 0,
                "total_races": 0,
                "total_votes_cast": 0
            })
            
            if self.save_file_info:
                notification["save_file_info"] = self.save_file_info
        
        elif not success:
            notification["error"] = self.load_error
        
        return notification
    
    def auto_load(self) -> Tuple[bool, Optional[str], Optional[Tuple[GameData, list[TurtleData], PlayerPreferences]], Dict[str, Any]]:
        """Complete auto-load process with all steps"""
        try:
            # Step 1: Check for save file
            has_save = self.check_for_save_file()
            
            if not has_save:
                # No save file - create new game
                success, error, data = self.create_new_game()
                notification = self.notify_user(success, "New game created")
                return success, error, data, notification
            
            # Step 2: Try to load directly (skip validation since SaveManager validates internally)
            try:
                success, error, data = self.restore_game_state()
                if success:
                    notification = self.notify_user(success, "Game loaded successfully")
                    return success, error, data, notification
            except Exception as e:
                self.logger.warning(f"Game state restoration failed: {e}")
            
            # Step 3: If restore failed, create new game
            self.logger.info("Creating new game due to load failure")
            success, error, data = self.create_new_game()
            notification = self.notify_user(success, "New game created (load failed)")
            return success, error, data, notification
            
        except Exception as e:
            error_msg = f"Auto-load process failed: {e}"
            self.logger.error(error_msg)
            
            # Ultimate fallback - create new game
            success, error, data = self.create_new_game()
            notification = self.notify_user(success, f"Auto-load failed, new game created: {error_msg}")
            return success, error, data, notification
    
    def get_load_status(self) -> Dict[str, Any]:
        """Get current load status information"""
        return {
            "load_successful": self.load_successful,
            "load_error": self.load_error,
            "has_loaded_data": self.loaded_data is not None,
            "save_file_info": self.save_file_info,
            "save_file_exists": self.save_manager.primary_save_path.exists(),
            "backup_file_exists": self.save_manager.backup_save_path.exists()
        }


# ============================================================================
# GLOBAL AUTO-LOAD SYSTEM INSTANCE
# ============================================================================

auto_load_system = AutoLoadSystem()
