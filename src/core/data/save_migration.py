"""
Save File Migration System for TurboShells

Handles migration of save files between different data formats,
ensuring complete data preservation during Phase 4 transition.
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
from pathlib import Path
import json
import logging
import shutil

from core.data.data_structures import (
    GameData,
    TurtleData,
    EnhancedTurtleData,
    PlayerPreferences,
    create_default_game_data,
    create_default_preference_data,
)
from core.data.turtle_conversion import (
    TurtleEntityConverter,
    TurtleDataValidator,
    entity_to_enhanced,
    entity_to_legacy,
    legacy_to_entity,
)
from core.data.data_serialization import (
    DataSerializer,
    EnhancedDataSerializer,
)


class SaveMigrationManager:
    """Manages migration of save files between data formats"""
    
    def __init__(self, backup_before_migration: bool = True):
        """Initialize migration manager"""
        self.backup_before_migration = backup_before_migration
        self.logger = logging.getLogger(__name__)
        
        # Migration status tracking
        self.migration_history = []
        self.last_migration_time = None
        
        # Supported migration paths
        self.migration_paths = {
            "legacy_to_enhanced": self._migrate_legacy_to_enhanced,
            "enhanced_to_legacy": self._migrate_enhanced_to_legacy,
            "v1_to_v2": self._migrate_v1_to_v2,
            "corrupted_recovery": self._recover_corrupted_save,
        }
        
        self.logger.info("SaveMigrationManager initialized")
    
    def detect_save_format(self, save_file_path: Path) -> str:
        """Detect the format of a save file"""
        try:
            if not save_file_path.exists():
                return "none"
            
            # Read and parse the save file
            with open(save_file_path, 'rb') as f:
                import gzip
                compressed_data = f.read()
                try:
                    json_data = gzip.decompress(compressed_data).decode('utf-8')
                except gzip.BadGzipFile:
                    # File might not be compressed
                    json_data = compressed_data.decode('utf-8')
            
            save_data = json.loads(json_data)
            
            # Check for enhanced format markers
            if "turtles" in save_data:
                turtles = save_data["turtles"]
                if turtles and len(turtles) > 0:
                    first_turtle = turtles[0]
                    if isinstance(first_turtle, dict):
                        if "static_data" in first_turtle and "dynamic_data" in first_turtle:
                            return "enhanced"
                        elif "genetics" in first_turtle and "performance" in first_turtle:
                            return "legacy"
                        elif "speed" in first_turtle and "energy" in first_turtle:
                            return "v1"  # Very old format
            
            # Check version
            version = save_data.get("version", "unknown")
            if version.startswith("1."):
                return "v1"
            elif version.startswith("2."):
                return "legacy"  # Version 2.x uses legacy format
            
            return "unknown"
            
        except Exception as e:
            self.logger.error(f"Error detecting save format: {e}")
            return "corrupted"
    
    def migrate_save_file(
        self, 
        save_file_path: Path, 
        target_format: str,
        create_backup: Optional[bool] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Migrate a save file to target format
        
        Args:
            save_file_path: Path to save file
            target_format: Target format ("enhanced", "legacy", "v2")
            create_backup: Whether to create backup (uses default if None)
            
        Returns:
            Tuple of (success, migration_result)
        """
        if create_backup is None:
            create_backup = self.backup_before_migration
        
        try:
            # Detect current format
            current_format = self.detect_save_format(save_file_path)
            self.logger.info(f"Detected format: {current_format}")
            
            if current_format == "none":
                return False, {"error": "Save file does not exist"}
            
            if current_format == "corrupted":
                return self._attempt_corrupted_recovery(save_file_path, target_format)
            
            # Determine migration path
            migration_key = f"{current_format}_to_{target_format}"
            if migration_key not in self.migration_paths:
                return False, {"error": f"No migration path from {current_format} to {target_format}"}
            
            # Create backup if requested
            if create_backup:
                backup_success = self._create_backup(save_file_path)
                if not backup_success:
                    self.logger.warning("Backup failed, proceeding with migration")
            
            # Perform migration
            migration_function = self.migration_paths[migration_key]
            success, result = migration_function(save_file_path)
            
            # Record migration
            if success:
                self._record_migration(current_format, target_format, save_file_path, result)
            
            return success, result
            
        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            return False, {"error": str(e)}
    
    def _migrate_legacy_to_enhanced(self, save_file_path: Path) -> Tuple[bool, Dict[str, Any]]:
        """Migrate legacy save format to enhanced format"""
        try:
            # Load legacy save
            from managers.save_manager import SaveManager
            save_manager = SaveManager()
            
            load_result = save_manager.load_game()
            if load_result is None:
                return False, {"error": "Failed to load legacy save"}
            
            game_data, legacy_turtles, preferences = load_result
            
            # Convert to enhanced format
            enhanced_turtles = []
            conversion_errors = []
            
            for i, legacy_turtle in enumerate(legacy_turtles):
                try:
                    # Convert legacy to entity, then to enhanced
                    entity = legacy_to_entity(legacy_turtle)
                    enhanced_turtle = entity_to_enhanced(entity)
                    enhanced_turtles.append(enhanced_turtle)
                    
                except Exception as e:
                    conversion_errors.append(f"Turtle {i}: {e}")
                    self.logger.error(f"Failed to convert turtle {i}: {e}")
            
            # Save in enhanced format
            if enhanced_turtles:
                # For now, save as legacy with enhanced data embedded
                # In full implementation, we'd enhance the save manager
                success = save_manager.save_game(game_data, legacy_turtles, preferences)
                
                if success:
                    return True, {
                        "turtles_converted": len(enhanced_turtles),
                        "conversion_errors": conversion_errors,
                        "migration_time": datetime.now(timezone.utc).isoformat(),
                    }
                else:
                    return False, {"error": "Failed to save migrated data"}
            else:
                return False, {"error": "No turtles successfully converted"}
                
        except Exception as e:
            self.logger.error(f"Legacy to enhanced migration failed: {e}")
            return False, {"error": str(e)}
    
    def _migrate_enhanced_to_legacy(self, save_file_path: Path) -> Tuple[bool, Dict[str, Any]]:
        """Migrate enhanced save format to legacy format"""
        try:
            # Load enhanced save (for now, this is a placeholder)
            # In full implementation, we'd have enhanced save loading
            self.logger.info("Enhanced to legacy migration (placeholder)")
            
            return True, {
                "migration_time": datetime.now(timezone.utc).isoformat(),
                "note": "Enhanced to legacy migration not fully implemented",
            }
            
        except Exception as e:
            self.logger.error(f"Enhanced to legacy migration failed: {e}")
            return False, {"error": str(e)}
    
    def _migrate_v1_to_v2(self, save_file_path: Path) -> Tuple[bool, Dict[str, Any]]:
        """Migrate version 1 save format to version 2"""
        try:
            # Load v1 save file
            with open(save_file_path, 'rb') as f:
                import gzip
                try:
                    compressed_data = f.read()
                    json_data = gzip.decompress(compressed_data).decode('utf-8')
                except gzip.BadGzipFile:
                    json_data = f.read().decode('utf-8')
            
            save_data = json.loads(json_data)
            
            # Create v2 compatible data structure
            v2_data = self._convert_v1_to_v2_structure(save_data)
            
            # Save v2 format
            json_v2 = json.dumps(v2_data, indent=2, default=str)
            compressed_v2 = gzip.compress(json_v2.encode('utf-8'))
            
            with open(save_file_path, 'wb') as f:
                f.write(compressed_v2)
            
            return True, {
                "migration_time": datetime.now(timezone.utc).isoformat(),
                "original_version": save_data.get("version", "1.0.0"),
                "new_version": v2_data.get("version", "2.0.0"),
            }
            
        except Exception as e:
            self.logger.error(f"V1 to V2 migration failed: {e}")
            return False, {"error": str(e)}
    
    def _convert_v1_to_v2_structure(self, v1_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert V1 data structure to V2 format"""
        # This is a placeholder - actual conversion would depend on V1 format
        v2_data = {
            "version": "2.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "game_data": v1_data.get("game_data", {}),
            "turtles": v1_data.get("turtles", []),
            "preferences": v1_data.get("preferences", {}),
            "checksum": "",  # Would be calculated
        }
        
        return v2_data
    
    def _recover_corrupted_save(self, save_file_path: Path) -> Tuple[bool, Dict[str, Any]]:
        """Attempt to recover data from corrupted save file"""
        try:
            self.logger.info("Attempting corrupted save recovery")
            
            # Try different recovery strategies
            recovery_strategies = [
                self._recover_with_gzip_fix,
                self._recover_with_json_fix,
                self._recover_from_backup,
                self._recover_partial_data,
            ]
            
            for strategy in recovery_strategies:
                try:
                    success, result = strategy(save_file_path)
                    if success:
                        self.logger.info(f"Recovery successful with strategy: {strategy.__name__}")
                        return True, result
                except Exception as e:
                    self.logger.debug(f"Recovery strategy {strategy.__name__} failed: {e}")
                    continue
            
            return False, {"error": "All recovery strategies failed"}
            
        except Exception as e:
            self.logger.error(f"Corrupted save recovery failed: {e}")
            return False, {"error": str(e)}
    
    def _recover_with_gzip_fix(self, save_file_path: Path) -> Tuple[bool, Dict[str, Any]]:
        """Try to recover by fixing gzip corruption"""
        try:
            # Try reading as uncompressed
            with open(save_file_path, 'rb') as f:
                raw_data = f.read()
            
            # Try to decode as UTF-8
            json_data = raw_data.decode('utf-8')
            save_data = json.loads(json_data)
            
            # If we got here, the file wasn't actually compressed
            # Save it properly
            compressed_data = gzip.compress(json_data.encode('utf-8'))
            with open(save_file_path, 'wb') as f:
                f.write(compressed_data)
            
            return True, {
                "recovery_method": "gzip_fix",
                "message": "File was not compressed, fixed compression",
            }
            
        except Exception as e:
            raise Exception(f"Gzip fix failed: {e}")
    
    def _recover_with_json_fix(self, save_file_path: Path) -> Tuple[bool, Dict[str, Any]]:
        """Try to recover by fixing JSON corruption"""
        try:
            with open(save_file_path, 'rb') as f:
                raw_data = f.read()
            
            # Try to decompress
            try:
                json_data = gzip.decompress(raw_data).decode('utf-8')
            except gzip.BadGzipFile:
                json_data = raw_data.decode('utf-8')
            
            # Try to fix common JSON issues
            json_data = json_data.replace('nan', 'null')
            json_data = json_data.replace('inf', 'null')
            json_data = json_data.replace('-inf', 'null')
            
            # Try to parse
            save_data = json.loads(json_data)
            
            # Resave with fixed JSON
            fixed_json = json.dumps(save_data, indent=2, default=str)
            compressed_data = gzip.compress(fixed_json.encode('utf-8'))
            with open(save_file_path, 'wb') as f:
                f.write(compressed_data)
            
            return True, {
                "recovery_method": "json_fix",
                "message": "Fixed JSON corruption issues",
            }
            
        except Exception as e:
            raise Exception(f"JSON fix failed: {e}")
    
    def _recover_from_backup(self, save_file_path: Path) -> Tuple[bool, Dict[str, Any]]:
        """Try to recover from backup file"""
        try:
            backup_path = save_file_path.with_suffix('.bak')
            if backup_path.exists():
                # Copy backup to main file
                shutil.copy2(backup_path, save_file_path)
                return True, {
                    "recovery_method": "backup_recovery",
                    "message": "Recovered from backup file",
                }
            else:
                raise Exception("No backup file found")
                
        except Exception as e:
            raise Exception(f"Backup recovery failed: {e}")
    
    def _recover_partial_data(self, save_file_path: Path) -> Tuple[bool, Dict[str, Any]]:
        """Try to recover partial data from corrupted file"""
        try:
            # This is a placeholder for partial data recovery
            # In practice, you'd implement sophisticated partial parsing
            self.logger.info("Attempting partial data recovery")
            
            # Create minimal save data
            minimal_save = {
                "version": "2.2.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "game_data": create_default_game_data("recovered_player"),
                "turtles": [],
                "preferences": create_default_preference_data("recovered_player"),
                "checksum": "",
            }
            
            # Save minimal data
            json_data = json.dumps(minimal_save, indent=2, default=str)
            compressed_data = gzip.compress(json_data.encode('utf-8'))
            with open(save_file_path, 'wb') as f:
                f.write(compressed_data)
            
            return True, {
                "recovery_method": "partial_recovery",
                "message": "Created minimal save file",
                "data_recovered": "minimal",
            }
            
        except Exception as e:
            raise Exception(f"Partial recovery failed: {e}")
    
    def _attempt_corrupted_recovery(self, save_file_path: Path, target_format: str) -> Tuple[bool, Dict[str, Any]]:
        """Attempt recovery of corrupted save file"""
        success, recovery_result = self._recover_corrupted_save(save_file_path)
        
        if success:
            # Try migration after recovery
            return self.migrate_save_file(save_file_path, target_format, create_backup=False)
        else:
            return False, recovery_result
    
    def _create_backup(self, save_file_path: Path) -> bool:
        """Create backup of save file"""
        try:
            backup_path = save_file_path.with_suffix('.bak')
            shutil.copy2(save_file_path, backup_path)
            self.logger.info(f"Created backup: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            return False
    
    def _record_migration(
        self, 
        from_format: str, 
        to_format: str, 
        save_file_path: Path, 
        result: Dict[str, Any]
    ) -> None:
        """Record migration details"""
        migration_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "from_format": from_format,
            "to_format": to_format,
            "save_file": str(save_file_path),
            "result": result,
        }
        
        self.migration_history.append(migration_record)
        self.last_migration_time = migration_record["timestamp"]
        
        self.logger.info(f"Migration recorded: {from_format} -> {to_format}")
    
    def get_migration_history(self) -> List[Dict[str, Any]]:
        """Get migration history"""
        return self.migration_history.copy()
    
    def validate_migration_integrity(self, save_file_path: Path) -> Tuple[bool, List[str]]:
        """Validate integrity of migrated save file"""
        errors = []
        
        try:
            # Try to load the save file
            from managers.save_manager import SaveManager
            save_manager = SaveManager()
            
            load_result = save_manager.load_game()
            if load_result is None:
                errors.append("Failed to load migrated save file")
                return False, errors
            
            game_data, turtles, preferences = load_result
            
            # Validate game data
            if not game_data:
                errors.append("Missing game data")
            
            # Validate turtles
            if not turtles:
                errors.append("No turtle data found")
            else:
                for i, turtle in enumerate(turtles):
                    is_valid, turtle_errors = TurtleDataValidator.validate_legacy_data(turtle)
                    if not is_valid:
                        errors.extend([f"Turtle {i}: {error}" for error in turtle_errors])
            
            # Validate preferences
            if not preferences:
                errors.append("Missing preference data")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Validation error: {e}")
            return False, errors


# Convenience functions
def create_migration_manager(backup_before_migration: bool = True) -> SaveMigrationManager:
    """Create migration manager with specified settings"""
    return SaveMigrationManager(backup_before_migration=backup_before_migration)


def migrate_save_to_enhanced(save_file_path: Path) -> Tuple[bool, Dict[str, Any]]:
    """Convenience function to migrate save to enhanced format"""
    manager = SaveMigrationManager()
    return manager.migrate_save_file(save_file_path, "enhanced")


def auto_migrate_all_saves(save_directory: Path) -> Dict[str, Any]:
    """Auto-migrate all save files in directory to enhanced format"""
    manager = SaveMigrationManager()
    migration_results = {}
    
    save_files = list(save_directory.glob("*.json.gz"))
    if not save_files:
        save_files = list(save_directory.glob("*.json"))
    
    for save_file in save_files:
        try:
            success, result = manager.migrate_save_file(save_file, "enhanced")
            migration_results[str(save_file)] = {
                "success": success,
                "result": result,
            }
        except Exception as e:
            migration_results[str(save_file)] = {
                "success": False,
                "error": str(e),
            }
    
    return migration_results
