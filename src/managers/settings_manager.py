"""
Settings manager for TurboShells.

This module manages the integration of the settings interface with the main game,
handling settings display, input processing, and application of changes.
"""

import pygame
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

from ui.settings_view import SettingsView, SettingsTab
from ui.ui_components import Button, Checkbox, Slider, Dropdown, Panel, ComponentStyle
from core.config import config_manager
from core.graphics_manager import graphics_manager
from core.audio_manager import audio_manager
from core.logging_config import get_logger


@dataclass
class SettingsState:
    """Current state of the settings interface."""
    visible: bool = False
    active_tab: SettingsTab = SettingsTab.GRAPHICS
    pending_changes: Dict[str, Any] = None
    requires_restart: bool = False


class SettingsManager:
    """
    Manages the settings interface and integration.

    Handles displaying settings, processing user input,
    and applying configuration changes to the game.
    """

    def __init__(self, screen_rect: pygame.Rect):
        """
        Initialize settings manager.

        Args:
            screen_rect: Screen rectangle for positioning
        """
        self.screen_rect = screen_rect
        self.logger = get_logger(__name__)

        # Settings state
        self.state = SettingsState()
        self.pending_changes = {}

        # Initialize settings view
        self.settings_view = SettingsView(screen_rect)

        self.logger.info("Settings manager initialized")

    def update_screen_rect(self, screen_rect: pygame.Rect) -> None:
        """Update screen rectangle and adjust layout."""
        self.screen_rect = screen_rect
        self.settings_view.update_layout(screen_rect)
        self.logger.info(f"Settings manager updated for screen size {screen_rect.width}x{screen_rect.height}")

    def _initialize_components(self) -> None:
        """Initialize UI components for settings."""
        # Define common styles
        button_style = ComponentStyle(
            background_color=(80, 80, 80),
            border_color=(120, 120, 120),
            text_color=(255, 255, 255),
            hover_color=(100, 100, 100),
            pressed_color=(120, 120, 120),
            disabled_color=(60, 60, 60),
            corner_radius=4
        )

        checkbox_style = ComponentStyle(
            background_color=(60, 60, 60),
            border_color=(100, 100, 100),
            text_color=(255, 255, 255),
            hover_color=(80, 80, 80),
            pressed_color=(100, 100, 100),
            disabled_color=(40, 40, 40)
        )

        slider_style = ComponentStyle(
            background_color=(50, 50, 50),
            border_color=(100, 100, 100),
            text_color=(255, 255, 255),
            hover_color=(70, 70, 70),
            pressed_color=(90, 90, 90),
            disabled_color=(30, 30, 30)
        )

        # Store styles for later use
        self.styles = {
            'button': button_style,
            'checkbox': checkbox_style,
            'slider': slider_style
        }

    def show_settings(self, tab: SettingsTab = SettingsTab.GRAPHICS) -> None:
        """
        Show the settings interface.

        Args:
            tab: Initial tab to display
        """
        self.state.visible = True
        self.state.active_tab = tab
        self.settings_view.show()
        self.settings_view.active_tab = tab

        # Load current settings
        self._load_current_settings()

        self.logger.info(f"Settings shown, tab: {tab.value}")

    def hide_settings(self) -> None:
        """Hide the settings interface."""
        self.state.visible = False
        self.settings_view.hide()
        self.logger.info("Settings hidden")

    def toggle_settings(self) -> None:
        """Toggle settings interface visibility."""
        if self.state.visible:
            self.hide_settings()
        else:
            self.show_settings()

    def is_visible(self) -> bool:
        """Check if settings interface is visible."""
        return self.state.visible

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events for the settings interface.

        Args:
            event: Pygame event

        Returns:
            True if event was handled, False otherwise
        """
        if not self.state.visible:
            return False

        # Handle settings view events
        handled = self.settings_view.handle_event(event)

        # Handle keyboard shortcuts
        if not handled and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.hide_settings()
                return True

        return handled

    def update(self, dt: float) -> None:
        """
        Update the settings interface.

        Args:
            dt: Time delta since last update
        """
        if not self.state.visible:
            return

        self.settings_view.update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the settings interface.

        Args:
            screen: Surface to draw on
        """
        if not self.state.visible:
            return

        self.settings_view.draw(screen)

    def _load_current_settings(self) -> None:
        """Load current settings into the interface."""
        config = config_manager.get_config()

        # Clear pending changes
        self.pending_changes.clear()

        # Graphics settings
        self.pending_changes.update({
            'resolution': f"{config.graphics.resolution_width}x{config.graphics.resolution_height}",
            'fullscreen': config.graphics.fullscreen,
            'quality': config.graphics.quality_level,
            'vsync': config.graphics.vsync,
            'frame_rate_limit': config.graphics.frame_rate_limit
        })

        # Audio settings
        self.pending_changes.update({
            'master_volume': config.audio.master_volume,
            'music_volume': config.audio.music_volume,
            'sfx_volume': config.audio.sfx_volume,
            'voice_volume': config.audio.voice_volume,
            'audio_enabled': config.audio.enabled,
            'mute_when_inactive': config.audio.mute_when_inactive
        })

        # Control settings
        self.pending_changes.update({
            'mouse_sensitivity': config.controls.mouse_sensitivity,
            'invert_mouse_y': config.controls.invert_mouse_y,
            'auto_save_interval': config.controls.auto_save_interval
        })

        # Difficulty settings
        self.pending_changes.update({
            'difficulty_level': config.difficulty.difficulty_level,
            'auto_save': config.difficulty.auto_save,
            'show_tutorials': config.difficulty.show_tutorials,
            'confirm_actions': config.difficulty.confirm_actions
        })

        # Player profile
        self.pending_changes.update({
            'player_name': config.player_profile.name,
            'avatar_index': config.player_profile.avatar_index
        })

        # UI theme
        self.pending_changes.update({
            'theme_name': config.ui_theme.theme_name,
            'color_scheme': config.ui_theme.color_scheme,
            'font_size': config.ui_theme.font_size,
            'ui_scale': config.ui_theme.ui_scale
        })

        # Accessibility
        self.pending_changes.update({
            'colorblind_mode': config.accessibility.colorblind_mode,
            'high_contrast': config.accessibility.high_contrast,
            'large_text': config.accessibility.large_text,
            'reduced_motion': config.accessibility.reduced_motion
        })

        # Privacy
        self.pending_changes.update({
            'analytics_enabled': config.privacy.analytics_enabled,
            'crash_reporting': config.privacy.crash_reporting,
            'usage_statistics': config.privacy.usage_statistics,
            'personal_data_sharing': config.privacy.personal_data_sharing
        })

    def apply_settings(self) -> bool:
        """
        Apply all pending settings changes.

        Returns:
            True if application successful, False otherwise
        """
        try:
            config = config_manager.get_config()
            requires_restart = False

            # Apply graphics settings
            if 'resolution' in self.pending_changes:
                resolution_str = self.pending_changes['resolution']
                width, height = map(int, resolution_str.split('x'))

                if (config.graphics.resolution_width != width or
                        config.graphics.resolution_height != height):
                    config.graphics.set_resolution(width, height)
                    graphics_manager.apply_resolution_change(width, height)

            if 'fullscreen' in self.pending_changes:
                config.graphics.fullscreen = self.pending_changes['fullscreen']
                if config.graphics.fullscreen != graphics_manager.is_fullscreen():
                    graphics_manager.toggle_fullscreen()

            if 'quality' in self.pending_changes:
                config.graphics.quality_level = self.pending_changes['quality']
                graphics_manager.set_quality_level(config.graphics.quality_level)

            if 'vsync' in self.pending_changes:
                config.graphics.vsync = self.pending_changes['vsync']
                graphics_manager.enable_vsync(config.graphics.vsync)

            if 'frame_rate_limit' in self.pending_changes:
                config.graphics.frame_rate_limit = self.pending_changes['frame_rate_limit']
                graphics_manager.set_frame_rate_limit(config.graphics.frame_rate_limit)

            # Apply audio settings
            if 'master_volume' in self.pending_changes:
                config.audio.master_volume = self.pending_changes['master_volume']
                audio_manager.set_master_volume(config.audio.master_volume)

            if 'music_volume' in self.pending_changes:
                config.audio.music_volume = self.pending_changes['music_volume']
                audio_manager.set_music_volume(config.audio.music_volume)

            if 'sfx_volume' in self.pending_changes:
                config.audio.sfx_volume = self.pending_changes['sfx_volume']
                audio_manager.set_sfx_volume(config.audio.sfx_volume)

            if 'voice_volume' in self.pending_changes:
                config.audio.voice_volume = self.pending_changes['voice_volume']
                audio_manager.set_voice_volume(config.audio.voice_volume)

            if 'audio_enabled' in self.pending_changes:
                config.audio.enabled = self.pending_changes['audio_enabled']
                audio_manager.toggle_audio(config.audio.enabled)

            if 'mute_when_inactive' in self.pending_changes:
                config.audio.mute_when_inactive = self.pending_changes['mute_when_inactive']
                audio_manager.toggle_mute_when_inactive(config.audio.mute_when_inactive)

            # Apply control settings
            if 'mouse_sensitivity' in self.pending_changes:
                config.controls.mouse_sensitivity = self.pending_changes['mouse_sensitivity']

            if 'invert_mouse_y' in self.pending_changes:
                config.controls.invert_mouse_y = self.pending_changes['invert_mouse_y']

            if 'auto_save_interval' in self.pending_changes:
                config.controls.auto_save_interval = self.pending_changes['auto_save_interval']

            # Apply difficulty settings
            if 'difficulty_level' in self.pending_changes:
                config.difficulty.difficulty_level = self.pending_changes['difficulty_level']

            if 'auto_save' in self.pending_changes:
                config.difficulty.auto_save = self.pending_changes['auto_save']

            if 'show_tutorials' in self.pending_changes:
                config.difficulty.show_tutorials = self.pending_changes['show_tutorials']

            if 'confirm_actions' in self.pending_changes:
                config.difficulty.confirm_actions = self.pending_changes['confirm_actions']

            # Apply player profile settings
            if 'player_name' in self.pending_changes:
                config.player_profile.name = self.pending_changes['player_name']

            if 'avatar_index' in self.pending_changes:
                config.player_profile.avatar_index = self.pending_changes['avatar_index']

            # Apply UI theme settings
            if 'theme_name' in self.pending_changes:
                config.ui_theme.theme_name = self.pending_changes['theme_name']

            if 'color_scheme' in self.pending_changes:
                config.ui_theme.color_scheme = self.pending_changes['color_scheme']

            if 'font_size' in self.pending_changes:
                config.ui_theme.font_size = self.pending_changes['font_size']

            if 'ui_scale' in self.pending_changes:
                config.ui_theme.ui_scale = self.pending_changes['ui_scale']

            # Apply accessibility settings
            if 'colorblind_mode' in self.pending_changes:
                config.accessibility.colorblind_mode = self.pending_changes['colorblind_mode']

            if 'high_contrast' in self.pending_changes:
                config.accessibility.high_contrast = self.pending_changes['high_contrast']

            if 'large_text' in self.pending_changes:
                config.accessibility.large_text = self.pending_changes['large_text']

            if 'reduced_motion' in self.pending_changes:
                config.accessibility.reduced_motion = self.pending_changes['reduced_motion']

            # Apply privacy settings
            if 'analytics_enabled' in self.pending_changes:
                config.privacy.analytics_enabled = self.pending_changes['analytics_enabled']

            if 'crash_reporting' in self.pending_changes:
                config.privacy.crash_reporting = self.pending_changes['crash_reporting']

            if 'usage_statistics' in self.pending_changes:
                config.privacy.usage_statistics = self.pending_changes['usage_statistics']

            if 'personal_data_sharing' in self.pending_changes:
                config.privacy.personal_data_sharing = self.pending_changes['personal_data_sharing']

            # Save configuration
            config_manager.save_config()

            self.logger.info("Settings applied successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to apply settings: {e}")
            return False

    def reset_settings(self) -> bool:
        """
        Reset all settings to defaults.

        Returns:
            True if reset successful, False otherwise
        """
        try:
            # Reset configuration
            config_manager.reset_to_defaults()

            # Reset managers
            graphics_manager.reset_to_defaults()
            audio_manager.reset_to_defaults()

            # Reload current settings
            self._load_current_settings()

            self.logger.info("Settings reset to defaults")
            return True

        except Exception as e:
            self.logger.error(f"Failed to reset settings: {e}")
            return False

    def update_pending_setting(self, key: str, value: Any) -> None:
        """
        Update a pending setting value.

        Args:
            key: Setting key
            value: New setting value
        """
        self.pending_changes[key] = value
        self.logger.debug(f"Updated pending setting: {key} = {value}")

    def get_pending_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a pending setting value.

        Args:
            key: Setting key
            default: Default value if key not found

        Returns:
            Setting value or default
        """
        return self.pending_changes.get(key, default)

    def has_pending_changes(self) -> bool:
        """Check if there are pending changes that haven't been applied."""
        config = config_manager.get_config()

        # Check if any pending values differ from current config
        for key, value in self.pending_changes.items():
            if key == 'resolution':
                current_value = f"{config.graphics.resolution_width}x{config.graphics.resolution_height}"
            elif key in ['fullscreen', 'quality', 'vsync']:
                current_value = getattr(config.graphics, key)
            elif key in ['master_volume', 'music_volume', 'sfx_volume', 'voice_volume', 'audio_enabled', 'mute_when_inactive']:
                current_value = getattr(config.audio, key)
            elif key in ['mouse_sensitivity', 'invert_mouse_y', 'auto_save_interval']:
                current_value = getattr(config.controls, key)
            elif key in ['difficulty_level', 'auto_save', 'show_tutorials', 'confirm_actions']:
                current_value = getattr(config.difficulty, key)
            elif key in ['player_name', 'avatar_index']:
                current_value = getattr(config.player_profile, key)
            elif key in ['theme_name', 'color_scheme', 'font_size', 'ui_scale']:
                current_value = getattr(config.ui_theme, key)
            elif key in ['colorblind_mode', 'high_contrast', 'large_text', 'reduced_motion']:
                current_value = getattr(config.accessibility, key)
            elif key in ['analytics_enabled', 'crash_reporting', 'usage_statistics', 'personal_data_sharing']:
                current_value = getattr(config.privacy, key)
            else:
                current_value = None

            if current_value != value:
                return True

        return False

    def get_settings_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current settings.

        Returns:
            Dictionary with settings summary
        """
        config = config_manager.get_config()

        return {
            'graphics': {
                'resolution': f"{config.graphics.resolution_width}x{config.graphics.resolution_height}",
                'fullscreen': config.graphics.fullscreen,
                'quality': config.graphics.quality_level,
                'vsync': config.graphics.vsync
            },
            'audio': {
                'master_volume': config.audio.master_volume,
                'music_volume': config.audio.music_volume,
                'sfx_volume': config.audio.sfx_volume,
                'enabled': config.audio.enabled
            },
            'controls': {
                'mouse_sensitivity': config.controls.mouse_sensitivity,
                'auto_save_interval': config.controls.auto_save_interval
            },
            'difficulty': {
                'level': config.difficulty.difficulty_level,
                'auto_save': config.difficulty.auto_save
            },
            'profile': {
                'name': config.player_profile.name,
                'races_completed': config.player_profile.races_completed
            }
        }

    def export_settings(self, file_path: str) -> bool:
        """
        Export current settings to a file.

        Args:
            file_path: Path to export settings

        Returns:
            True if export successful, False otherwise
        """
        try:
            return config_manager.export_config(file_path)
        except Exception as e:
            self.logger.error(f"Failed to export settings: {e}")
            return False

    def import_settings(self, file_path: str) -> bool:
        """
        Import settings from a file.

        Args:
            file_path: Path to import settings from

        Returns:
            True if import successful, False otherwise
        """
        try:
            success = config_manager.import_config(file_path)
            if success:
                self._load_current_settings()
                # Apply imported settings
                self.apply_settings()
            return success
        except Exception as e:
            self.logger.error(f"Failed to import settings: {e}")
            return False
