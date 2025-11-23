"""
Configuration management system for TurboShells.

This module handles loading, saving, and managing game settings
and user preferences with JSON persistence.
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from core.logging_config import get_logger


@dataclass
class GraphicsSettings:
    """Graphics configuration settings."""
    resolution_width: int = 1024
    resolution_height: int = 768
    fullscreen: bool = False
    vsync: bool = True
    frame_rate_limit: int = 60
    quality_level: str = "high"  # low, medium, high, ultra
    
    def get_resolution(self) -> Tuple[int, int]:
        """Get resolution as tuple."""
        return (self.resolution_width, self.resolution_height)
    
    def set_resolution(self, width: int, height: int) -> None:
        """Set resolution from tuple."""
        self.resolution_width = width
        self.resolution_height = height


@dataclass
class AudioSettings:
    """Audio configuration settings."""
    master_volume: float = 1.0
    music_volume: float = 0.8
    sfx_volume: float = 0.9
    voice_volume: float = 1.0
    enabled: bool = True
    mute_when_inactive: bool = False
    
    def get_music_volume(self) -> float:
        """Get effective music volume."""
        return self.master_volume * self.music_volume if self.enabled else 0.0
    
    def get_sfx_volume(self) -> float:
        """Get effective SFX volume."""
        return self.master_volume * self.sfx_volume if self.enabled else 0.0


@dataclass
class ControlSettings:
    """Control and input settings."""
    key_bindings: Dict[str, str] = None
    mouse_sensitivity: float = 1.0
    invert_mouse_y: bool = False
    auto_save_interval: int = 300  # seconds
    
    def __post_init__(self):
        """Initialize default key bindings if not provided."""
        if self.key_bindings is None:
            self.key_bindings = {
                "menu": "m",
                "race": "r",
                "shop": "s",
                "breeding": "b",
                "train_1": "q",
                "train_2": "w",
                "train_3": "e",
                "rest_1": "z",
                "rest_2": "x",
                "rest_3": "c",
                "retire_1": "4",
                "retire_2": "5",
                "retire_3": "6",
                "speed_1x": "1",
                "speed_2x": "2",
                "speed_4x": "3",
                "breed": "return",
                "escape": "escape"
            }


@dataclass
class DifficultySettings:
    """Game difficulty and accessibility settings."""
    difficulty_level: str = "normal"  # easy, normal, hard, expert
    auto_save: bool = True
    show_tutorials: bool = True
    confirm_actions: bool = True
    race_speed_multiplier: float = 1.0
    economy_multiplier: float = 1.0
    
    def get_race_speed(self) -> float:
        """Get race speed based on difficulty."""
        difficulty_multipliers = {
            "easy": 0.8,
            "normal": 1.0,
            "hard": 1.2,
            "expert": 1.5
        }
        return self.race_speed_multiplier * difficulty_multipliers.get(self.difficulty_level, 1.0)


@dataclass
class PlayerProfile:
    """Player profile information."""
    name: str = "Player"
    avatar_index: int = 0
    total_playtime: int = 0  # seconds
    races_completed: int = 0
    turtles_bred: int = 0
    highest_money: int = 0
    achievements_unlocked: list = None
    
    def __post_init__(self):
        """Initialize achievements list if not provided."""
        if self.achievements_unlocked is None:
            self.achievements_unlocked = []


@dataclass
class UITheme:
    """UI theme settings."""
    theme_name: str = "default"
    color_scheme: str = "blue"  # blue, green, red, purple, dark
    font_size: int = 16
    ui_scale: float = 1.0
    show_animations: bool = True
    animation_speed: float = 1.0


@dataclass
class AccessibilitySettings:
    """Accessibility and comfort settings."""
    colorblind_mode: str = "none"  # none, protanopia, deuteranopia, tritanopia
    high_contrast: bool = False
    large_text: bool = False
    screen_reader: bool = False
    reduced_motion: bool = False
    visual_indicators: bool = True


@dataclass
class PrivacySettings:
    """Privacy and data collection settings."""
    analytics_enabled: bool = False
    crash_reporting: bool = True
    usage_statistics: bool = False
    personal_data_sharing: bool = False


@dataclass
class GameConfig:
    """Main game configuration containing all settings."""
    graphics: GraphicsSettings = None
    audio: AudioSettings = None
    controls: ControlSettings = None
    difficulty: DifficultySettings = None
    player_profile: PlayerProfile = None
    ui_theme: UITheme = None
    accessibility: AccessibilitySettings = None
    privacy: PrivacySettings = None
    
    def __post_init__(self):
        """Initialize default settings if not provided."""
        if self.graphics is None:
            self.graphics = GraphicsSettings()
        if self.audio is None:
            self.audio = AudioSettings()
        if self.controls is None:
            self.controls = ControlSettings()
        if self.difficulty is None:
            self.difficulty = DifficultySettings()
        if self.player_profile is None:
            self.player_profile = PlayerProfile()
        if self.ui_theme is None:
            self.ui_theme = UITheme()
        if self.accessibility is None:
            self.accessibility = AccessibilitySettings()
        if self.privacy is None:
            self.privacy = PrivacySettings()


class ConfigManager:
    """Manages loading, saving, and accessing game configuration."""
    
    def __init__(self, config_dir: str = "config", config_file: str = "settings.json"):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory to store configuration files
            config_file: Name of the main configuration file
        """
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / config_file
        self.logger = get_logger(__name__)
        self._config: Optional[GameConfig] = None
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        
        # Load configuration
        self.load_config()
    
    def load_config(self) -> GameConfig:
        """
        Load configuration from file or create defaults.
        
        Returns:
            Loaded or default configuration
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convert JSON to GameConfig
                self._config = self._dict_to_config(data)
                self.logger.info("Configuration loaded successfully")
            else:
                self._config = GameConfig()
                self.save_config()  # Save default config
                self.logger.info("Created default configuration")
                
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            self._config = GameConfig()  # Fallback to defaults
        
        return self._config
    
    def save_config(self) -> bool:
        """
        Save current configuration to file.
        
        Returns:
            True if save successful, False otherwise
        """
        try:
            if self._config is None:
                self.logger.error("No configuration to save")
                return False
            
            # Convert GameConfig to dictionary
            data = asdict(self._config)
            
            # Save to file with backup
            backup_file = self.config_file.with_suffix('.json.bak')
            if self.config_file.exists():
                self.config_file.rename(backup_file)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Configuration saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
    
    def get_config(self) -> GameConfig:
        """
        Get current configuration.
        
        Returns:
            Current game configuration
        """
        if self._config is None:
            self._config = self.load_config()
        return self._config
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self._config = GameConfig()
        self.save_config()
        self.logger.info("Configuration reset to defaults")
    
    def export_config(self, export_path: str) -> bool:
        """
        Export configuration to specified path.
        
        Args:
            export_path: Path to export configuration
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            if self._config is None:
                return False
            
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = asdict(self._config)
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuration exported to {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """
        Import configuration from specified path.
        
        Args:
            import_path: Path to import configuration from
            
        Returns:
            True if import successful, False otherwise
        """
        try:
            import_file = Path(import_path)
            if not import_file.exists():
                self.logger.error(f"Import file not found: {import_path}")
                return False
            
            with open(import_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._config = self._dict_to_config(data)
            self.save_config()
            
            self.logger.info(f"Configuration imported from {import_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import configuration: {e}")
            return False
    
    def _dict_to_config(self, data: Dict[str, Any]) -> GameConfig:
        """
        Convert dictionary to GameConfig object.
        
        Args:
            data: Dictionary data
            
        Returns:
            GameConfig object
        """
        # Extract individual settings
        graphics_data = data.get('graphics', {})
        audio_data = data.get('audio', {})
        controls_data = data.get('controls', {})
        difficulty_data = data.get('difficulty', {})
        profile_data = data.get('player_profile', {})
        theme_data = data.get('ui_theme', {})
        accessibility_data = data.get('accessibility', {})
        privacy_data = data.get('privacy', {})
        
        # Create settings objects
        graphics = GraphicsSettings(**graphics_data)
        audio = AudioSettings(**audio_data)
        controls = ControlSettings(**controls_data)
        difficulty = DifficultySettings(**difficulty_data)
        profile = PlayerProfile(**profile_data)
        theme = UITheme(**theme_data)
        accessibility = AccessibilitySettings(**accessibility_data)
        privacy = PrivacySettings(**privacy_data)
        
        return GameConfig(
            graphics=graphics,
            audio=audio,
            controls=controls,
            difficulty=difficulty,
            player_profile=profile,
            ui_theme=theme,
            accessibility=accessibility,
            privacy=privacy
        )


# Global configuration manager instance
config_manager = ConfigManager()
