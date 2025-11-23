"""
Save Manager for TurboShells

Handles all save/load operations with compression, validation, and error handling.
Implements the save system design from the technical documentation.
"""

import json
import gzip
import shutil
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime, timezone
import logging

from core.data import (
    GameData, TurtleData, PlayerPreferences,
    DataValidator, DataSerializer,
    create_default_game_data, create_default_turtle_data, create_default_preference_data,
    PerformanceOptimizer, SecurityManager
)


class SaveManager:
    """Centralized save/load operations with compression and validation"""
    
    def __init__(self, save_directory: Optional[str] = None):
        """Initialize save manager with directory setup"""
        self.save_directory = Path(save_directory) if save_directory else self._get_default_save_directory()
        self.save_directory.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.primary_save_path = self.save_directory / "turbo_shells_save.json"
        self.backup_save_path = self.save_directory / "turbo_shells_backup.json"
        self.old_save_path = self.save_directory / "turbo_shells_old.json"
        
        # Validator and serializer
        self.validator = DataValidator()
        self.serializer = DataSerializer()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Compression settings
        self.compression_enabled = True
        self.compression_level = 6
        
        # Auto-save settings
        self.auto_save_enabled = True
        self.last_auto_save = None
        
        self.logger.info(f"SaveManager initialized with directory: {self.save_directory}")
    
    def _get_default_save_directory(self) -> Path:
        """Get default save directory based on OS"""
        import os
        if os.name == 'nt':  # Windows
            base_dir = Path(os.environ.get('APPDATA', '')) / 'TurboShells'
        else:  # Unix-like
            base_dir = Path.home() / '.local' / 'share' / 'TurboShells'
        
        return base_dir
    
    def _compress_data(self, data: str) -> bytes:
        """Compress data using gzip"""
        if not self.compression_enabled:
            return data.encode('utf-8')
        
        return gzip.compress(data.encode('utf-8'), compresslevel=self.compression_level)
    
    def _decompress_data(self, compressed_data: bytes) -> str:
        """Decompress data from gzip"""
        if not self.compression_enabled:
            return compressed_data.decode('utf-8')
        
        try:
            return gzip.decompress(compressed_data).decode('utf-8')
        except gzip.BadGzipFile:
            # Fallback to uncompressed data
            return compressed_data.decode('utf-8')
    
    def _create_backup(self) -> bool:
        """Create backup of existing save file"""
        if not self.primary_save_path.exists():
            return True
        
        try:
            # Move current backup to old
            if self.backup_save_path.exists():
                shutil.move(self.backup_save_path, self.old_save_path)
            
            # Copy primary to backup
            shutil.copy2(self.primary_save_path, self.backup_save_path)
            self.logger.info("Backup created successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return False
    
    def _validate_save_data(self, game_data: Dict[str, Any], 
                          turtles: List[Dict[str, Any]], 
                          preferences: Dict[str, Any]) -> bool:
        """Validate all save data"""
        # Validate game data
        game_valid, game_error = self.validator.validate_game_data(game_data)
        if not game_valid:
            self.logger.error(f"Game data validation failed: {game_error}")
            return False
        
        # Validate turtle data
        for i, turtle in enumerate(turtles):
            turtle_valid, turtle_error = self.validator.validate_turtle_data(turtle)
            if not turtle_valid:
                self.logger.error(f"Turtle {i} validation failed: {turtle_error}")
                return False
        
        # Validate preference data
        pref_valid, pref_error = self.validator.validate_preference_data(preferences)
        if not pref_valid:
            self.logger.error(f"Preference data validation failed: {pref_error}")
            return False
        
        return True
    
    def _convert_to_dict(self, obj) -> Dict[str, Any]:
        """Recursively convert dataclass objects to dictionaries"""
        if hasattr(obj, '__dict__'):
            # It's a dataclass or object with __dict__
            result = {}
            for key, value in obj.__dict__.items():
                if hasattr(value, '__dict__'):
                    # Recursively convert nested dataclass
                    result[key] = self._convert_to_dict(value)
                elif isinstance(value, dict):
                    # Handle nested dictionaries
                    result[key] = {k: self._convert_to_dict(v) if hasattr(v, '__dict__') else v 
                                 for k, v in value.items()}
                elif isinstance(value, list):
                    # Handle lists of objects
                    result[key] = [self._convert_to_dict(item) if hasattr(item, '__dict__') else item 
                                  for item in value]
                else:
                    result[key] = value
            return result
        else:
            # It's already a primitive value
            return obj
    
    def save_game(self, game_data: GameData, turtles: List[TurtleData], 
                  preferences: PlayerPreferences) -> bool:
        """Save complete game state"""
        try:
            # Convert to dictionaries recursively
            game_dict = self._convert_to_dict(game_data)
            turtles_dict = [self._convert_to_dict(turtle) for turtle in turtles]
            preferences_dict = self._convert_to_dict(preferences)
            
            # Validate data
            if not self._validate_save_data(game_dict, turtles_dict, preferences_dict):
                return False
            
            # Create backup
            if not self._create_backup():
                self.logger.warning("Backup failed, proceeding with save")
            
            # Prepare save structure
            save_data = {
                "version": "2.2.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "game_data": game_dict,
                "turtles": turtles_dict,
                "preferences": preferences_dict,
                "checksum": self._calculate_checksum(game_dict, turtles_dict, preferences_dict)
            }
            
            # Serialize and compress
            json_data = json.dumps(save_data, indent=2, default=str)
            compressed_data = self._compress_data(json_data)
            
            # Write to file
            with open(self.primary_save_path, 'wb') as f:
                f.write(compressed_data)
            
            # Update auto-save timestamp
            self.last_auto_save = datetime.now(timezone.utc)
            
            self.logger.info(f"Game saved successfully to {self.primary_save_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Save failed: {e}")
            # Attempt to restore from backup
            if self.backup_save_path.exists():
                shutil.copy2(self.backup_save_path, self.primary_save_path)
                self.logger.info("Restored from backup after save failure")
            return False
    
    def load_game(self) -> Optional[tuple[GameData, List[TurtleData], PlayerPreferences]]:
        """Load complete game state"""
        try:
            if not self.primary_save_path.exists():
                self.logger.info("No save file found, creating new game")
                return self._create_new_game()
            
            # Read and decompress
            with open(self.primary_save_path, 'rb') as f:
                compressed_data = f.read()
            
            json_data = self._decompress_data(compressed_data)
            save_data = json.loads(json_data)
            
            # Extract components
            game_dict = save_data["game_data"]
            turtles_dict = save_data["turtles"]
            preferences_dict = save_data["preferences"]
            
            # Verify checksum
            expected_checksum = save_data.get("checksum")
            actual_checksum = self._calculate_checksum(game_dict, turtles_dict, preferences_dict)
            
            if expected_checksum and expected_checksum != actual_checksum:
                self.logger.error("Save file checksum mismatch, data may be corrupted")
                # Try loading from backup
                return self._load_from_backup()
            
            # Validate data
            if not self._validate_save_data(game_dict, turtles_dict, preferences_dict):
                self.logger.error("Save file validation failed")
                # Try loading from backup
                return self._load_from_backup()
            
            # Convert to data objects
            game_data = GameData(**game_dict)
            turtles = [TurtleData(**turtle_dict) for turtle_dict in turtles_dict]
            preferences = PlayerPreferences(**preferences_dict)
            
            self.logger.info(f"Game loaded successfully from {self.primary_save_path}")
            return game_data, turtles, preferences
            
        except Exception as e:
            self.logger.error(f"Load failed: {e}")
            # Try loading from backup
            return self._load_from_backup()
    
    def _load_from_backup(self) -> Optional[tuple[GameData, List[TurtleData], PlayerPreferences]]:
        """Attempt to load from backup file"""
        if not self.backup_save_path.exists():
            self.logger.warning("No backup file available")
            return self._create_new_game()
        
        try:
            # Temporarily replace primary path with backup
            primary_backup = self.primary_save_path
            self.primary_save_path = self.backup_save_path
            
            # Load from backup
            result = self.load_game()
            
            # Restore primary path
            self.primary_save_path = primary_backup
            
            if result:
                self.logger.info("Successfully loaded from backup")
                # Restore backup as primary
                shutil.copy2(self.backup_save_path, self.primary_save_path)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Backup load failed: {e}")
            return self._create_new_game()
    
    def _create_new_game(self) -> tuple[GameData, List[TurtleData], PlayerPreferences]:
        """Create new game with default data"""
        player_id = f"player_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        game_data = create_default_game_data(player_id)
        preferences = create_default_preference_data(player_id)
        turtles = []  # Start with empty roster
        
        self.logger.info("Created new game with default data")
        return game_data, turtles, preferences
    
    def auto_save(self, game_data: GameData, turtles: List[TurtleData], 
                  preferences: PlayerPreferences) -> bool:
        """Auto-save game state"""
        if not self.auto_save_enabled:
            return True
        
        # Check if enough time has passed since last auto-save (5 minutes)
        if self.last_auto_save:
            time_since_last = datetime.now(timezone.utc) - self.last_auto_save
            if time_since_last.total_seconds() < 300:  # 5 minutes
                return True
        
        return self.save_game(game_data, turtles, preferences)
    
    def _calculate_checksum(self, game_data: Dict[str, Any], 
                           turtles: List[Dict[str, Any]], 
                           preferences: Dict[str, Any]) -> str:
        """Calculate checksum for data integrity"""
        import hashlib
        
        # Create a deterministic string representation
        data_string = json.dumps({
            "game_data": game_data,
            "turtles": turtles,
            "preferences": preferences
        }, sort_keys=True, default=str)
        
        return hashlib.sha256(data_string.encode('utf-8')).hexdigest()
    
    def validate_save_file(self, file_path: Optional[str] = None) -> bool:
        """Validate save file integrity"""
        path = Path(file_path) if file_path else self.primary_save_path
        
        if not path.exists():
            return False
        
        try:
            # Read and decompress
            with open(path, 'rb') as f:
                compressed_data = f.read()
            
            json_data = self._decompress_data(compressed_data)
            save_data = json.loads(json_data)
            
            # Basic structure validation
            required_keys = ["version", "timestamp", "game_data", "turtles", "preferences"]
            if not all(key in save_data for key in required_keys):
                return False
            
            # Validate individual components
            return self._validate_save_data(
                save_data["game_data"],
                save_data["turtles"],
                save_data["preferences"]
            )
            
        except Exception as e:
            self.logger.error(f"Save file validation failed: {e}")
            return False
    
    def cleanup_old_saves(self) -> None:
        """Clean up old save files"""
        try:
            # Remove old save file if it exists
            if self.old_save_path.exists():
                self.old_save_path.unlink()
                self.logger.info("Cleaned up old save file")
            
            # TODO: Implement additional cleanup logic for multiple save slots
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
    
    def get_save_info(self) -> Dict[str, Any]:
        """Get information about save files"""
        info = {
            "save_directory": str(self.save_directory),
            "primary_exists": self.primary_save_path.exists(),
            "backup_exists": self.backup_save_path.exists(),
            "old_exists": self.old_save_path.exists(),
            "compression_enabled": self.compression_enabled,
            "auto_save_enabled": self.auto_save_enabled,
            "last_auto_save": self.last_auto_save.isoformat() if self.last_auto_save else None
        }
        
        if self.primary_save_path.exists():
            stat = self.primary_save_path.stat()
            info.update({
                "primary_size_bytes": stat.st_size,
                "primary_modified": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()
            })
        
        return info
    
    def delete_save(self) -> bool:
        """Delete all save files"""
        try:
            files_deleted = []
            
            for path in [self.primary_save_path, self.backup_save_path, self.old_save_path]:
                if path.exists():
                    path.unlink()
                    files_deleted.append(str(path))
            
            self.logger.info(f"Deleted save files: {files_deleted}")
            return True
            
        except Exception as e:
            self.logger.error(f"Delete save files failed: {e}")
            return False
    
    def export_save(self, export_path: str) -> bool:
        """Export save file to specified path"""
        try:
            if not self.primary_save_path.exists():
                self.logger.error("No save file to export")
                return False
            
            export_path = Path(export_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(self.primary_save_path, export_path)
            self.logger.info(f"Save exported to {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Export failed: {e}")
            return False
    
    def import_save(self, import_path: str) -> bool:
        """Import save file from specified path"""
        try:
            import_path = Path(import_path)
            if not import_path.exists():
                self.logger.error(f"Import file not found: {import_path}")
                return False
            
            # Validate imported file
            temp_primary = self.primary_save_path
            self.primary_save_path = import_path
            
            if not self.validate_save_file():
                self.primary_save_path = temp_primary
                self.logger.error("Imported file validation failed")
                return False
            
            # Create backup of current save
            self._create_backup()
            
            # Copy imported file
            shutil.copy2(import_path, self.primary_save_path)
            
            # Restore path
            self.primary_save_path = temp_primary
            
            self.logger.info(f"Save imported from {import_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Import failed: {e}")
            return False


# ============================================================================
# GLOBAL SAVE MANAGER INSTANCE
# ============================================================================

save_manager = SaveManager()
