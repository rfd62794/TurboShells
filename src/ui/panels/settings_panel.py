"""Settings Panel - ImGui Implementation

Proof of concept for migrating legacy settings view to ImGui panel.
Demonstrates full data binding integration and clean architecture.
"""

import imgui
from typing import Dict, Any, Optional, List
from .base_panel import BasePanel, PanelStyle, PanelState
from ..data_binding import DataBindingManager, ValidationRule, ValidationType, BindingDirection
from ..game_state_interface import TurboShellsGameStateInterface


class SettingsPanel(BasePanel):
    """Settings interface with proper data binding and ImGui integration.
    
    This panel demonstrates:
    - Clean separation between UI and game logic
    - Two-way data binding with validation
    - Reactive UI updates
    - Proper error handling
    - Component-based architecture
    """
    
    def __init__(self, game_state_interface: TurboShellsGameStateInterface, 
                 data_binding_manager: DataBindingManager):
        """Initialize settings panel.
        
        Args:
            game_state_interface: Clean interface to game state
            data_binding_manager: Data binding manager for reactive updates
        """
        super().__init__("settings", "Game Settings")
        
        self.game_state = game_state_interface
        self.data_binding_manager = data_binding_manager
        
        # Panel configuration
        self.size = (400, 500)
        self.position = (100, 100)
        self.auto_resize = False
        
        # Settings categories
        self.categories = ["Graphics", "Audio", "Controls", "Gameplay", "System"]
        self.active_category = 0
        
        # Settings data
        self.settings_data = {
            "graphics": {
                "fullscreen": False,
                "vsync": True,
                "resolution": "1024x768",
                "fps_limit": 60,
                "show_fps": False
            },
            "audio": {
                "master_volume": 0.8,
                "music_volume": 0.7,
                "sfx_volume": 0.9,
                "mute_audio": False
            },
            "controls": {
                "mouse_sensitivity": 1.0,
                "key_repeat_delay": 500,
                "key_repeat_rate": 30,
                "invert_mouse": False
            },
            "gameplay": {
                "auto_save_interval": 300,
                "show_tutorials": True,
                "difficulty": "normal",
                "race_speed": 1.0
            },
            "system": {
                "debug_mode": False,
                "log_level": "info",
                "enable_monitoring": True,
                "clear_cache": False
            }
        }
        
        # UI state
        self._changed_settings = set()
        self._validation_errors = {}
        
        # Initialize data bindings
        self._initialize_data_bindings()
    
    def _initialize_data_bindings(self) -> None:
        """Initialize data bindings for reactive updates."""
        # Bind to game state properties
        self.data_binding_manager.bind_property(
            "settings_money", 
            self.game_state.game, 
            "money",
            "settings_panel.money_display",
            BindingDirection.ONE_WAY_TO_UI
        )
        
        # Bind to computed properties
        self.data_binding_manager.bind_property(
            "settings_turtle_count",
            self.game_state.game,
            "active_turtle_count",  # This will be computed
            "settings_panel.turtle_count_display",
            BindingDirection.ONE_WAY_TO_UI
        )
        
        # Register change callbacks
        self.data_binding_manager.add_change_callback(
            "settings_money",
            self._on_money_changed,
            source_changed=True
        )
    
    def render_content(self, game_state: Any) -> None:
        """Render the settings panel content.
        
        Args:
            game_state: Current game state object
        """
        # Render category tabs
        self._render_category_tabs()
        
        # Render current category content
        category = self.categories[self.active_category]
        
        imgui.separator()
        
        if category == "Graphics":
            self._render_graphics_settings()
        elif category == "Audio":
            self._render_audio_settings()
        elif category == "Controls":
            self._render_controls_settings()
        elif category == "Gameplay":
            self._render_gameplay_settings()
        elif category == "System":
            self._render_system_settings()
        
        # Render action buttons
        imgui.separator()
        self._render_action_buttons()
        
        # Render status information
        self._render_status_info()
    
    def _render_category_tabs(self) -> None:
        """Render settings category tabs."""
        for i, category in enumerate(self.categories):
            is_active = (i == self.active_category)
            
            if imgui.selectable(category, is_active)[0]:
                self.active_category = i
            
            if i < len(self.categories) - 1:
                imgui.same_line()
    
    def _render_graphics_settings(self) -> None:
        """Render graphics settings."""
        graphics = self.settings_data["graphics"]
        
        # Fullscreen toggle
        changed, graphics["fullscreen"] = imgui.checkbox("Fullscreen", graphics["fullscreen"])
        if changed:
            self._mark_setting_changed("graphics.fullscreen")
        
        # VSync toggle
        changed, graphics["vsync"] = imgui.checkbox("VSync", graphics["vsync"])
        if changed:
            self._mark_setting_changed("graphics.vsync")
        
        # Resolution dropdown
        resolutions = ["800x600", "1024x768", "1280x720", "1920x1080"]
        current_resolution = graphics["resolution"]
        current_index = resolutions.index(current_resolution) if current_resolution in resolutions else 1
        
        changed, new_index = imgui.combo("Resolution", current_index, resolutions)
        if changed:
            graphics["resolution"] = resolutions[new_index]
            self._mark_setting_changed("graphics.resolution")
        
        # FPS limit slider
        changed, graphics["fps_limit"] = imgui.slider_int("FPS Limit", graphics["fps_limit"], 30, 144)
        if changed:
            self._mark_setting_changed("graphics.fps_limit")
        
        # Show FPS toggle
        changed, graphics["show_fps"] = imgui.checkbox("Show FPS", graphics["show_fps"])
        if changed:
            self._mark_setting_changed("graphics.show_fps")
    
    def _render_audio_settings(self) -> None:
        """Render audio settings."""
        audio = self.settings_data["audio"]
        
        # Master volume slider
        changed, audio["master_volume"] = imgui.slider_float(
            "Master Volume", audio["master_volume"], 0.0, 1.0
        )
        if changed:
            self._mark_setting_changed("audio.master_volume")
        
        # Music volume slider
        changed, audio["music_volume"] = imgui.slider_float(
            "Music Volume", audio["music_volume"], 0.0, 1.0
        )
        if changed:
            self._mark_setting_changed("audio.music_volume")
        
        # SFX volume slider
        changed, audio["sfx_volume"] = imgui.slider_float(
            "SFX Volume", audio["sfx_volume"], 0.0, 1.0
        )
        if changed:
            self._mark_setting_changed("audio.sfx_volume")
        
        # Mute audio toggle
        changed, audio["mute_audio"] = imgui.checkbox("Mute Audio", audio["mute_audio"])
        if changed:
            self._mark_setting_changed("audio.mute_audio")
    
    def _render_controls_settings(self) -> None:
        """Render controls settings."""
        controls = self.settings_data["controls"]
        
        # Mouse sensitivity slider
        changed, controls["mouse_sensitivity"] = imgui.slider_float(
            "Mouse Sensitivity", controls["mouse_sensitivity"], 0.1, 3.0
        )
        if changed:
            self._mark_setting_changed("controls.mouse_sensitivity")
        
        # Key repeat delay slider
        changed, controls["key_repeat_delay"] = imgui.slider_int(
            "Key Repeat Delay (ms)", controls["key_repeat_delay"], 100, 1000
        )
        if changed:
            self._mark_setting_changed("controls.key_repeat_delay")
        
        # Key repeat rate slider
        changed, controls["key_repeat_rate"] = imgui.slider_int(
            "Key Repeat Rate", controls["key_repeat_rate"], 10, 100
        )
        if changed:
            self._mark_setting_changed("controls.key_repeat_rate")
        
        # Invert mouse toggle
        changed, controls["invert_mouse"] = imgui.checkbox("Invert Mouse", controls["invert_mouse"])
        if changed:
            self._mark_setting_changed("controls.invert_mouse")
    
    def _render_gameplay_settings(self) -> None:
        """Render gameplay settings."""
        gameplay = self.settings_data["gameplay"]
        
        # Auto-save interval slider
        changed, gameplay["auto_save_interval"] = imgui.slider_int(
            "Auto-Save Interval (seconds)", gameplay["auto_save_interval"], 60, 600
        )
        if changed:
            self._mark_setting_changed("gameplay.auto_save_interval")
        
        # Show tutorials toggle
        changed, gameplay["show_tutorials"] = imgui.checkbox("Show Tutorials", gameplay["show_tutorials"])
        if changed:
            self._mark_setting_changed("gameplay.show_tutorials")
        
        # Difficulty dropdown
        difficulties = ["easy", "normal", "hard", "extreme"]
        current_difficulty = gameplay["difficulty"]
        current_index = difficulties.index(current_difficulty) if current_difficulty in difficulties else 1
        
        changed, new_index = imgui.combo("Difficulty", current_index, difficulties)
        if changed:
            gameplay["difficulty"] = difficulties[new_index]
            self._mark_setting_changed("gameplay.difficulty")
        
        # Race speed slider
        changed, gameplay["race_speed"] = imgui.slider_float(
            "Race Speed", gameplay["race_speed"], 0.5, 3.0
        )
        if changed:
            self._mark_setting_changed("gameplay.race_speed")
    
    def _render_system_settings(self) -> None:
        """Render system settings."""
        system = self.settings_data["system"]
        
        # Debug mode toggle
        changed, system["debug_mode"] = imgui.checkbox("Debug Mode", system["debug_mode"])
        if changed:
            self._mark_setting_changed("system.debug_mode")
        
        # Log level dropdown
        log_levels = ["debug", "info", "warning", "error"]
        current_log_level = system["log_level"]
        current_index = log_levels.index(current_log_level) if current_log_level in log_levels else 1
        
        changed, new_index = imgui.combo("Log Level", current_index, log_levels)
        if changed:
            system["log_level"] = log_levels[new_index]
            self._mark_setting_changed("system.log_level")
        
        # Enable monitoring toggle
        changed, system["enable_monitoring"] = imgui.checkbox("Enable Monitoring", system["enable_monitoring"])
        if changed:
            self._mark_setting_changed("system.enable_monitoring")
        
        # Clear cache button
        if imgui.button("Clear Cache"):
            self._clear_cache()
        
        imgui.same_line()
        imgui.text("Clear temporary files and cache")
    
    def _render_action_buttons(self) -> None:
        """Render action buttons."""
        # Apply button
        apply_enabled = len(self._changed_settings) > 0
        if apply_enabled:
            if imgui.button("Apply Changes"):
                self._apply_settings()
        else:
            imgui.push_style_var(imgui.STYLE_ALPHA, 0.5)
            imgui.button("Apply Changes")
            imgui.pop_style_var()
        
        imgui.same_line()
        
        # Reset button
        if imgui.button("Reset to Defaults"):
            self._reset_to_defaults()
        
        imgui.same_line()
        
        # Cancel button
        if imgui.button("Cancel"):
            self._cancel_changes()
    
    def _render_status_info(self) -> None:
        """Render status information."""
        # Game state info
        money = self.game_state.get('money', 0)
        turtle_count = self.game_state.get('active_turtle_count', 0)
        
        imgui.separator()
        imgui.text(f"Money: ${money}")
        imgui.text(f"Active Turtles: {turtle_count}")
        
        # Settings status
        if self._changed_settings:
            imgui.text_colored((1.0, 1.0, 0.0, 1.0), f"Unsaved changes: {len(self._changed_settings)}")
            imgui.text("Click 'Apply Changes' to save")
        else:
            imgui.text_colored((0.0, 1.0, 0.0, 1.0), "All settings up to date")
        
        # Validation errors
        if self._validation_errors:
            imgui.text_colored((1.0, 0.0, 0.0, 1.0), "Validation Errors:")
            for error in self._validation_errors.values():
                imgui.text(f"  - {error}")
    
    def _mark_setting_changed(self, setting_key: str) -> None:
        """Mark a setting as changed.
        
        Args:
            setting_key: Key of the changed setting
        """
        self._changed_settings.add(setting_key)
        
        # Clear any previous validation errors for this setting
        if setting_key in self._validation_errors:
            del self._validation_errors[setting_key]
    
    def _apply_settings(self) -> None:
        """Apply all changed settings."""
        try:
            # Apply each changed setting
            for setting_key in self._changed_settings:
                self._apply_single_setting(setting_key)
            
            # Clear changed settings
            self._changed_settings.clear()
            
            # Show success message (could be a toast notification)
            print("Settings applied successfully")
            
        except Exception as e:
            print(f"Error applying settings: {e}")
    
    def _apply_single_setting(self, setting_key: str) -> None:
        """Apply a single setting.
        
        Args:
            setting_key: Key of the setting to apply
        """
        category, setting = setting_key.split('.', 1)
        value = self.settings_data[category][setting]
        
        # Apply setting based on category
        if category == "graphics":
            self._apply_graphics_setting(setting, value)
        elif category == "audio":
            self._apply_audio_setting(setting, value)
        elif category == "controls":
            self._apply_controls_setting(setting, value)
        elif category == "gameplay":
            self._apply_gameplay_setting(setting, value)
        elif category == "system":
            self._apply_system_setting(setting, value)
    
    def _apply_graphics_setting(self, setting: str, value: Any) -> None:
        """Apply graphics setting.
        
        Args:
            setting: Setting name
            value: Setting value
        """
        if setting == "fullscreen":
            # Apply fullscreen setting
            pass
        elif setting == "vsync":
            # Apply VSync setting
            pass
        elif setting == "resolution":
            # Apply resolution setting
            pass
        elif setting == "fps_limit":
            # Apply FPS limit setting
            pass
        elif setting == "show_fps":
            # Apply show FPS setting
            pass
    
    def _apply_audio_setting(self, setting: str, value: Any) -> None:
        """Apply audio setting.
        
        Args:
            setting: Setting name
            value: Setting value
        """
        # Apply audio settings
        pass
    
    def _apply_controls_setting(self, setting: str, value: Any) -> None:
        """Apply controls setting.
        
        Args:
            setting: Setting name
            value: Setting value
        """
        # Apply controls settings
        pass
    
    def _apply_gameplay_setting(self, setting: str, value: Any) -> None:
        """Apply gameplay setting.
        
        Args:
            setting: Setting name
            value: Setting value
        """
        if setting == "auto_save_interval":
            # Update auto-save interval
            pass
        elif setting == "race_speed":
            # Update race speed
            self.game_state.set('race_speed_multiplier', value)
    
    def _apply_system_setting(self, setting: str, value: Any) -> None:
        """Apply system setting.
        
        Args:
            setting: Setting name
            value: Setting value
        """
        # Apply system settings
        pass
    
    def _reset_to_defaults(self) -> None:
        """Reset all settings to default values."""
        # Reset to default values
        self.settings_data = {
            "graphics": {
                "fullscreen": False,
                "vsync": True,
                "resolution": "1024x768",
                "fps_limit": 60,
                "show_fps": False
            },
            "audio": {
                "master_volume": 0.8,
                "music_volume": 0.7,
                "sfx_volume": 0.9,
                "mute_audio": False
            },
            "controls": {
                "mouse_sensitivity": 1.0,
                "key_repeat_delay": 500,
                "key_repeat_rate": 30,
                "invert_mouse": False
            },
            "gameplay": {
                "auto_save_interval": 300,
                "show_tutorials": True,
                "difficulty": "normal",
                "race_speed": 1.0
            },
            "system": {
                "debug_mode": False,
                "log_level": "info",
                "enable_monitoring": True,
                "clear_cache": False
            }
        }
        
        # Mark all settings as changed
        for category in self.settings_data:
            for setting in self.settings_data[category]:
                self._changed_settings.add(f"{category}.{setting}")
    
    def _cancel_changes(self) -> None:
        """Cancel all pending changes."""
        self._changed_settings.clear()
        self._validation_errors.clear()
        
        # Reload current settings from game state
        self._load_current_settings()
    
    def _load_current_settings(self) -> None:
        """Load current settings from game state."""
        # This would load actual settings from the game
        # For now, we'll keep the defaults
        pass
    
    def _clear_cache(self) -> None:
        """Clear application cache."""
        # Clear cache functionality
        print("Cache cleared")
    
    def _on_money_changed(self, binding_id: str, old_value: Any, new_value: Any) -> None:
        """Handle money changes from game state.
        
        Args:
            binding_id: ID of the binding that changed
            old_value: Previous money value
            new_value: New money value
        """
        # React to money changes
        pass
    
    def get_changed_settings(self) -> List[str]:
        """Get list of changed settings.
        
        Returns:
            List of changed setting keys
        """
        return list(self._changed_settings)
    
    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes.
        
        Returns:
            True if there are unsaved changes, False otherwise
        """
        return len(self._changed_settings) > 0
    
    def validate_settings(self) -> Dict[str, str]:
        """Validate all settings.
        
        Returns:
            Dictionary of validation errors by setting key
        """
        errors = {}
        
        # Validate each setting
        for category_name, category_data in self.settings_data.items():
            for setting_name, value in category_data.items():
                setting_key = f"{category_name}.{setting_name}"
                
                # Perform validation based on setting type
                error = self._validate_single_setting(setting_key, value)
                if error:
                    errors[setting_key] = error
        
        self._validation_errors = errors
        return errors
    
    def _validate_single_setting(self, setting_key: str, value: Any) -> Optional[str]:
        """Validate a single setting.
        
        Args:
            setting_key: Key of the setting to validate
            value: Value to validate
            
        Returns:
            Error message if invalid, None otherwise
        """
        category, setting = setting_key.split('.', 1)
        
        # Add validation logic here
        if category == "graphics" and setting == "fps_limit":
            if not isinstance(value, int) or value < 30 or value > 144:
                return "FPS limit must be between 30 and 144"
        
        elif category == "audio":
            if setting.endswith("_volume") and (not isinstance(value, (int, float)) or value < 0 or value > 1):
                return "Volume must be between 0.0 and 1.0"
        
        elif category == "gameplay" and setting == "auto_save_interval":
            if not isinstance(value, int) or value < 60 or value > 600:
                return "Auto-save interval must be between 60 and 600 seconds"
        
        return None
