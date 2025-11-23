"""
Save file protection system for TurboShells.

This module provides backup, corruption detection, and recovery
functionality for game save files.
"""

import json
import hashlib
import shutil
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from core.logging_config import get_logger


@dataclass
class SaveFileInfo:
    """Information about a save file."""
    file_path: str
    checksum: str
    timestamp: datetime
    file_size: int
    is_valid: bool
    backup_count: int


@dataclass
class BackupInfo:
    """Information about a backup file."""
    backup_path: str
    original_checksum: str
    backup_timestamp: datetime
    backup_type: str  # 'auto', 'manual', 'corruption_recovery'


class SaveProtectionManager:
    """
    Manages save file protection, backup, and recovery.
    
    Provides automated backup creation, corruption detection,
    and recovery options for game save files.
    """
    
    def __init__(self, save_dir: str = "saves", backup_dir: str = "backups", max_backups: int = 10):
        """
        Initialize save protection manager.
        
        Args:
            save_dir: Directory containing save files
            backup_dir: Directory for backup files
            max_backups: Maximum number of backups to keep
        """
        self.save_dir = Path(save_dir)
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.logger = get_logger(__name__)
        self.corruption_threshold = 3  # Number of failed loads before considering corrupted
        
        # Ensure directories exist
        self.save_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Load backup registry
        self.backup_registry_file = self.backup_dir / "backup_registry.json"
        self.backup_registry: Dict[str, List[BackupInfo]] = {}
        self.load_backup_registry()
    
    def load_backup_registry(self) -> None:
        """Load backup registry from file."""
        try:
            if self.backup_registry_file.exists():
                with open(self.backup_registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convert JSON data to BackupInfo objects
                for save_file, backups in data.items():
                    backup_list = []
                    for backup_data in backups:
                        backup_data['backup_timestamp'] = datetime.fromisoformat(backup_data['backup_timestamp'])
                        backup_list.append(BackupInfo(**backup_data))
                    self.backup_registry[save_file] = backup_list
                
                self.logger.info("Backup registry loaded successfully")
            else:
                self.backup_registry = {}
                self.save_backup_registry()
                
        except Exception as e:
            self.logger.error(f"Failed to load backup registry: {e}")
            self.backup_registry = {}
    
    def save_backup_registry(self) -> bool:
        """
        Save backup registry to file.
        
        Returns:
            True if save successful, False otherwise
        """
        try:
            # Convert BackupInfo objects to JSON-serializable format
            registry_data = {}
            for save_file, backups in self.backup_registry.items():
                backup_list = []
                for backup in backups:
                    backup_dict = asdict(backup)
                    backup_dict['backup_timestamp'] = backup.backup_timestamp.isoformat()
                    backup_list.append(backup_dict)
                registry_data[save_file] = backup_list
            
            with open(self.backup_registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save backup registry: {e}")
            return False
    
    def calculate_checksum(self, file_path: Path) -> str:
        """
        Calculate SHA-256 checksum of a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hexadecimal checksum string
        """
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            self.logger.error(f"Failed to calculate checksum for {file_path}: {e}")
            return ""
    
    def create_backup(self, save_file: str, backup_type: str = "auto") -> bool:
        """
        Create a backup of a save file.
        
        Args:
            save_file: Name of save file to backup
            backup_type: Type of backup ('auto', 'manual', 'corruption_recovery')
            
        Returns:
            True if backup successful, False otherwise
        """
        try:
            source_path = self.save_dir / save_file
            if not source_path.exists():
                self.logger.warning(f"Save file not found: {save_file}")
                return False
            
            # Calculate checksum
            checksum = self.calculate_checksum(source_path)
            if not checksum:
                return False
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{save_file.replace('.json', '')}_{timestamp}_{backup_type}.json"
            backup_path = self.backup_dir / backup_filename
            
            # Copy file
            shutil.copy2(source_path, backup_path)
            
            # Add to registry
            backup_info = BackupInfo(
                backup_path=str(backup_path),
                original_checksum=checksum,
                backup_timestamp=datetime.now(),
                backup_type=backup_type
            )
            
            if save_file not in self.backup_registry:
                self.backup_registry[save_file] = []
            
            self.backup_registry[save_file].append(backup_info)
            
            # Limit number of backups
            self._cleanup_old_backups(save_file)
            
            # Save registry
            self.save_backup_registry()
            
            self.logger.info(f"Backup created: {backup_filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create backup for {save_file}: {e}")
            return False
    
    def _cleanup_old_backups(self, save_file: str) -> None:
        """
        Remove old backups to maintain maximum backup count.
        
        Args:
            save_file: Save file name
        """
        if save_file not in self.backup_registry:
            return
        
        backups = self.backup_registry[save_file]
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda b: b.backup_timestamp, reverse=True)
        
        # Keep only the most recent backups
        if len(backups) > self.max_backups:
            old_backups = backups[self.max_backups:]
            
            for backup in old_backups:
                try:
                    backup_path = Path(backup.backup_path)
                    if backup_path.exists():
                        backup_path.unlink()
                    self.logger.debug(f"Removed old backup: {backup.backup_path}")
                except Exception as e:
                    self.logger.error(f"Failed to remove old backup {backup.backup_path}: {e}")
            
            # Update registry
            self.backup_registry[save_file] = backups[:self.max_backups]
    
    def validate_save_file(self, save_file: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a save file for corruption.
        
        Args:
            save_file: Name of save file to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            save_path = self.save_dir / save_file
            
            if not save_path.exists():
                return False, "Save file does not exist"
            
            # Check file size
            file_size = save_path.stat().st_size
            if file_size == 0:
                return False, "Save file is empty"
            
            # Try to parse JSON
            try:
                with open(save_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                return False, f"Invalid JSON format: {e}"
            
            # Validate required fields (basic validation)
            required_fields = ['game_data', 'turtles', 'preferences']
            for field in required_fields:
                if field not in data:
                    return False, f"Missing required field: {field}"
            
            # Calculate and verify checksum if we have a record
            current_checksum = self.calculate_checksum(save_path)
            if save_file in self.backup_registry and self.backup_registry[save_file]:
                # Check against most recent backup's checksum
                latest_backup = self.backup_registry[save_file][0]
                if current_checksum != latest_backup.original_checksum:
                    # Checksum changed, but this could be normal (save was updated)
                    # We'll log this but not consider it corruption
                    self.logger.debug(f"Save file checksum changed for {save_file}")
            
            return True, None
            
        except Exception as e:
            return False, f"Validation error: {e}"
    
    def detect_corruption(self, save_file: str, load_error: str) -> bool:
        """
        Detect if a save file is corrupted based on load errors.
        
        Args:
            save_file: Name of save file
            load_error: Error message from load attempt
            
        Returns:
            True if corruption detected, False otherwise
        """
        # Check for common corruption indicators
        corruption_indicators = [
            "JSONDecodeError",
            "json.decoder",
            "Expecting value",
            "Unterminated string",
            "Invalid control character",
            "Extra data",
            "UnicodeDecodeError",
            "FileNotFoundError",
            "Permission denied"
        ]
        
        for indicator in corruption_indicators:
            if indicator in load_error:
                self.logger.warning(f"Corruption detected in {save_file}: {load_error}")
                return True
        
        return False
    
    def recover_from_corruption(self, save_file: str) -> Tuple[bool, Optional[str]]:
        """
        Attempt to recover a corrupted save file from backups.
        
        Args:
            save_file: Name of corrupted save file
            
        Returns:
            Tuple of (recovery_successful, backup_used_path)
        """
        try:
            if save_file not in self.backup_registry or not self.backup_registry[save_file]:
                self.logger.error(f"No backups available for {save_file}")
                return False, None
            
            # Get backups sorted by timestamp (newest first)
            backups = sorted(self.backup_registry[save_file], 
                           key=lambda b: b.backup_timestamp, reverse=True)
            
            # Try each backup until we find a valid one
            for backup in backups:
                backup_path = Path(backup.backup_path)
                
                if not backup_path.exists():
                    self.logger.warning(f"Backup file missing: {backup.backup_path}")
                    continue
                
                # Validate backup
                is_valid, error = self.validate_save_file(str(backup_path))
                if is_valid:
                    # Restore from backup
                    save_path = self.save_dir / save_file
                    shutil.copy2(backup_path, save_path)
                    
                    # Create a corruption recovery backup
                    self.create_backup(save_file, "corruption_recovery")
                    
                    self.logger.info(f"Successfully recovered {save_file} from backup: {backup.backup_path}")
                    return True, backup.backup_path
                else:
                    self.logger.warning(f"Backup {backup.backup_path} is also invalid: {error}")
            
            self.logger.error(f"No valid backups found for {save_file}")
            return False, None
            
        except Exception as e:
            self.logger.error(f"Failed to recover {save_file}: {e}")
            return False, None
    
    def get_save_file_info(self, save_file: str) -> Optional[SaveFileInfo]:
        """
        Get information about a save file.
        
        Args:
            save_file: Name of save file
            
        Returns:
            SaveFileInfo object or None if file doesn't exist
        """
        try:
            save_path = self.save_dir / save_file
            
            if not save_path.exists():
                return None
            
            # Get file info
            stat = save_path.stat()
            checksum = self.calculate_checksum(save_path)
            is_valid, _ = self.validate_save_file(save_file)
            backup_count = len(self.backup_registry.get(save_file, []))
            
            return SaveFileInfo(
                file_path=str(save_path),
                checksum=checksum,
                timestamp=datetime.fromtimestamp(stat.st_mtime),
                file_size=stat.st_size,
                is_valid=is_valid,
                backup_count=backup_count
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get save file info for {save_file}: {e}")
            return None
    
    def list_save_files(self) -> List[str]:
        """
        List all save files in the save directory.
        
        Returns:
            List of save file names
        """
        try:
            save_files = []
            for file_path in self.save_dir.glob("*.json"):
                save_files.append(file_path.name)
            return sorted(save_files)
        except Exception as e:
            self.logger.error(f"Failed to list save files: {e}")
            return []
    
    def get_backup_list(self, save_file: str) -> List[BackupInfo]:
        """
        Get list of backups for a save file.
        
        Args:
            save_file: Name of save file
            
        Returns:
            List of backup information
        """
        return self.backup_registry.get(save_file, [])
    
    def manual_backup(self, save_file: str) -> bool:
        """
        Create a manual backup of a save file.
        
        Args:
            save_file: Name of save file to backup
            
        Returns:
            True if backup successful, False otherwise
        """
        return self.create_backup(save_file, "manual")
    
    def export_save_file(self, save_file: str, export_path: str) -> bool:
        """
        Export a save file to a specified path.
        
        Args:
            save_file: Name of save file to export
            export_path: Path to export to
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            source_path = self.save_dir / save_file
            export_path = Path(export_path)
            
            if not source_path.exists():
                self.logger.error(f"Save file not found: {save_file}")
                return False
            
            # Create export directory if needed
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_path, export_path)
            
            self.logger.info(f"Save file exported: {save_file} -> {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export save file {save_file}: {e}")
            return False
    
    def import_save_file(self, import_path: str, save_file: str = None) -> bool:
        """
        Import a save file from a specified path.
        
        Args:
            import_path: Path to import from
            save_file: Name to save as (defaults to original filename)
            
        Returns:
            True if import successful, False otherwise
        """
        try:
            import_path = Path(import_path)
            
            if not import_path.exists():
                self.logger.error(f"Import file not found: {import_path}")
                return False
            
            # Determine save file name
            if save_file is None:
                save_file = import_path.name
            
            save_path = self.save_dir / save_file
            
            # Create backup of existing file if it exists
            if save_path.exists():
                self.create_backup(save_file, "manual")
            
            # Copy file
            shutil.copy2(import_path, save_path)
            
            # Validate imported file
            is_valid, error = self.validate_save_file(save_file)
            if not is_valid:
                self.logger.error(f"Imported save file is invalid: {error}")
                return False
            
            self.logger.info(f"Save file imported: {import_path} -> {save_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import save file: {e}")
            return False
    
    def cleanup_old_backups(self, days_old: int = 30) -> int:
        """
        Clean up old backup files.
        
        Args:
            days_old: Remove backups older than this many days
            
        Returns:
            Number of files removed
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            removed_count = 0
            
            for save_file, backups in self.backup_registry.items():
                backups_to_remove = []
                
                for backup in backups:
                    if backup.backup_timestamp < cutoff_date and backup.backup_type == "auto":
                        # Remove old auto-backups
                        try:
                            backup_path = Path(backup.backup_path)
                            if backup_path.exists():
                                backup_path.unlink()
                            backups_to_remove.append(backup)
                            removed_count += 1
                        except Exception as e:
                            self.logger.error(f"Failed to remove old backup {backup.backup_path}: {e}")
                
                # Update registry
                for backup in backups_to_remove:
                    self.backup_registry[save_file].remove(backup)
            
            # Save updated registry
            self.save_backup_registry()
            
            if removed_count > 0:
                self.logger.info(f"Cleaned up {removed_count} old backup files")
            
            return removed_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old backups: {e}")
            return 0
    
    def get_protection_status(self) -> Dict[str, Any]:
        """
        Get comprehensive protection system status.
        
        Returns:
            Dictionary with protection system information
        """
        total_backups = sum(len(backups) for backups in self.backup_registry.values())
        save_files = self.list_save_files()
        valid_saves = 0
        corrupted_saves = 0
        
        for save_file in save_files:
            info = self.get_save_file_info(save_file)
            if info:
                if info.is_valid:
                    valid_saves += 1
                else:
                    corrupted_saves += 1
        
        return {
            "save_directory": str(self.save_dir),
            "backup_directory": str(self.backup_dir),
            "total_save_files": len(save_files),
            "valid_save_files": valid_saves,
            "corrupted_save_files": corrupted_saves,
            "total_backups": total_backups,
            "max_backups_per_file": self.max_backups,
            "backup_registry_size": len(self.backup_registry)
        }


# Global save protection manager instance
save_protection_manager = SaveProtectionManager()
