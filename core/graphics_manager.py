"""
Graphics settings manager for TurboShells.

This module handles applying graphics configuration settings to Pygame
and managing display options, quality settings, and performance optimizations.
"""

import pygame
from typing import Tuple, List, Dict, Any
from core.config import config_manager, GraphicsSettings
from core.logging_config import get_logger


class GraphicsManager:
    """
    Manages graphics settings and display configuration.

    Handles resolution changes, fullscreen mode, quality settings,
    and performance optimizations based on user preferences.
    """

    # Available resolutions (width, height)
    AVAILABLE_RESOLUTIONS = [
        (800, 600),
        (1024, 768),
        (1280, 720),
        (1366, 768),
        (1920, 1080),
        (2560, 1440),
        (3840, 2160)
    ]

    # Quality levels with their settings
    QUALITY_PRESETS = {
        "low": {
            "texture_quality": 0.5,
            "particle_count": 0.3,
            "shadow_quality": 0.2,
            "anti_aliasing": 0,
            "anisotropic_filtering": 0
        },
        "medium": {
            "texture_quality": 0.7,
            "particle_count": 0.6,
            "shadow_quality": 0.5,
            "anti_aliasing": 2,
            "anisotropic_filtering": 2
        },
        "high": {
            "texture_quality": 0.9,
            "particle_count": 0.8,
            "shadow_quality": 0.8,
            "anti_aliasing": 4,
            "anisotropic_filtering": 4
        },
        "ultra": {
            "texture_quality": 1.0,
            "particle_count": 1.0,
            "shadow_quality": 1.0,
            "anti_aliasing": 8,
            "anisotropic_filtering": 8
        }
    }

    def __init__(self):
        """Initialize graphics manager."""
        self.logger = get_logger(__name__)
        self.screen: pygame.Surface = None
        self.current_settings: GraphicsSettings = None
        self.quality_settings: Dict[str, float] = {}

        # Load settings
        self.load_settings()

        # Initialize display
        self.initialize_display()

    def load_settings(self) -> None:
        """Load graphics settings from configuration."""
        config = config_manager.get_config()
        self.current_settings = config.graphics
        self.quality_settings = self.QUALITY_PRESETS.get(
            self.current_settings.quality_level,
            self.QUALITY_PRESETS["high"]
        )
        self.logger.info(
            f"Loaded graphics settings: {
                self.current_settings.resolution_width}x{
                self.current_settings.resolution_height}")

    def initialize_display(self) -> pygame.Surface:
        """
        Initialize the Pygame display with current settings.

        Returns:
            The initialized display surface
        """
        try:
            # Set display flags
            flags = pygame.DOUBLEBUF
            if self.current_settings.fullscreen:
                flags |= pygame.FULLSCREEN

            # Create display
            self.screen = pygame.display.set_mode(
                self.current_settings.get_resolution(),
                flags
            )

            # Set frame rate
            pygame.time.Clock()

            # Apply VSync if available
            if self.current_settings.vsync:
                # Note: VSync is set at display creation in modern Pygame
                pass

            self.logger.info(
                f"Display initialized: {
                    self.current_settings.get_resolution()}, Fullscreen: {
                    self.current_settings.fullscreen}")
            return self.screen

        except Exception as e:
            self.logger.error(f"Failed to initialize display: {e}")
            # Fallback to default settings
            self.current_settings.resolution_width = 1024
            self.current_settings.resolution_height = 768
            self.current_settings.fullscreen = False
            self.screen = pygame.display.set_mode((1024, 768))
            return self.screen

    def apply_resolution_change(self, width: int, height: int, fullscreen: bool = None) -> bool:
        """
        Apply a new resolution setting.

        Args:
            width: New screen width
            height: New screen height
            fullscreen: New fullscreen setting (None to keep current)

        Returns:
            True if change successful, False otherwise
        """
        try:
            old_settings = (
                self.current_settings.resolution_width,
                self.current_settings.resolution_height,
                self.current_settings.fullscreen
            )

            # Update settings
            self.current_settings.set_resolution(width, height)
            if fullscreen is not None:
                self.current_settings.fullscreen = fullscreen

            # Reinitialize display
            self.initialize_display()

            # Save configuration
            config_manager.save_config()

            self.logger.info(f"Resolution changed to {width}x{height}, Fullscreen: {self.current_settings.fullscreen}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to change resolution: {e}")
            # Revert to old settings
            self.current_settings.resolution_width, self.current_settings.resolution_height, self.current_settings.fullscreen = old_settings
            return False

    def toggle_fullscreen(self) -> bool:
        """
        Toggle fullscreen mode.

        Returns:
            True if toggle successful, False otherwise
        """
        return self.apply_resolution_change(
            self.current_settings.resolution_width,
            self.current_settings.resolution_height,
            not self.current_settings.fullscreen
        )

    def set_quality_level(self, quality: str) -> bool:
        """
        Set graphics quality level.

        Args:
            quality: Quality level ('low', 'medium', 'high', 'ultra')

        Returns:
            True if set successfully, False otherwise
        """
        if quality not in self.QUALITY_PRESETS:
            self.logger.warning(f"Invalid quality level: {quality}")
            return False

        self.current_settings.quality_level = quality
        self.quality_settings = self.QUALITY_PRESETS[quality]

        # Apply quality settings
        self._apply_quality_settings()

        # Save configuration
        config_manager.save_config()

        self.logger.info(f"Graphics quality set to {quality}")
        return True

    def _apply_quality_settings(self) -> None:
        """Apply current quality settings to rendering."""
        # This would be expanded to actually apply settings to the rendering pipeline
        # For now, we just log what would be applied
        self.logger.debug(f"Applying quality settings: {self.quality_settings}")

    def get_available_resolutions(self) -> List[Tuple[int, int]]:
        """
        Get list of available resolutions.

        Returns:
            List of available (width, height) tuples
        """
        return self.AVAILABLE_RESOLUTIONS.copy()

    def get_current_resolution(self) -> Tuple[int, int]:
        """
        Get current resolution.

        Returns:
            Current (width, height) tuple
        """
        return self.current_settings.get_resolution()

    def is_fullscreen(self) -> bool:
        """
        Check if currently in fullscreen mode.

        Returns:
            True if fullscreen, False otherwise
        """
        return self.current_settings.fullscreen

    def get_quality_level(self) -> str:
        """
        Get current quality level.

        Returns:
            Current quality level string
        """
        return self.current_settings.quality_level

    def get_texture_quality(self) -> float:
        """
        Get texture quality multiplier.

        Returns:
            Texture quality (0.0 to 1.0)
        """
        return self.quality_settings.get("texture_quality", 1.0)

    def get_particle_count(self) -> float:
        """
        Get particle count multiplier.

        Returns:
            Particle count multiplier (0.0 to 1.0)
        """
        return self.quality_settings.get("particle_count", 1.0)

    def get_shadow_quality(self) -> float:
        """
        Get shadow quality multiplier.

        Returns:
            Shadow quality (0.0 to 1.0)
        """
        return self.quality_settings.get("shadow_quality", 1.0)

    def get_anti_aliasing_level(self) -> int:
        """
        Get anti-aliasing level.

        Returns:
            Anti-aliasing level (0, 2, 4, 8)
        """
        return self.quality_settings.get("anti_aliasing", 0)

    def get_anisotropic_filtering(self) -> int:
        """
        Get anisotropic filtering level.

        Returns:
            Anisotropic filtering level (0, 2, 4, 8)
        """
        return self.quality_settings.get("anisotropic_filtering", 0)

    def set_frame_rate_limit(self, limit: int) -> None:
        """
        Set frame rate limit.

        Args:
            limit: Maximum frames per second
        """
        self.current_settings.frame_rate_limit = max(30, min(240, limit))
        config_manager.save_config()
        self.logger.info(f"Frame rate limit set to {self.current_settings.frame_rate_limit}")

    def get_frame_rate_limit(self) -> int:
        """
        Get current frame rate limit.

        Returns:
            Current frame rate limit
        """
        return self.current_settings.frame_rate_limit

    def enable_vsync(self, enabled: bool) -> None:
        """
        Enable or disable VSync.

        Args:
            enabled: Whether to enable VSync
        """
        self.current_settings.vsync = enabled
        # Note: VSync requires display reinitialization in Pygame
        self.initialize_display()
        config_manager.save_config()
        self.logger.info(f"VSync {'enabled' if enabled else 'disabled'}")

    def is_vsync_enabled(self) -> bool:
        """
        Check if VSync is enabled.

        Returns:
            True if VSync enabled, False otherwise
        """
        return self.current_settings.vsync

    def get_display_info(self) -> Dict[str, Any]:
        """
        Get comprehensive display information.

        Returns:
            Dictionary with display information
        """
        info = pygame.display.Info()
        return {
            "current_resolution": self.get_current_resolution(),
            "desktop_resolution": (info.current_w, info.current_h),
            "fullscreen": self.is_fullscreen(),
            "quality_level": self.get_quality_level(),
            "frame_rate_limit": self.get_frame_rate_limit(),
            "vsync": self.is_vsync_enabled(),
            "hardware_accelerated": bool(info.hw),
            "available_resolutions": self.get_available_resolutions()
        }

    def reset_to_defaults(self) -> None:
        """Reset graphics settings to defaults."""
        self.current_settings = GraphicsSettings()
        self.quality_settings = self.QUALITY_PRESETS["high"]
        self.initialize_display()
        config_manager.save_config()
        self.logger.info("Graphics settings reset to defaults")


# Global graphics manager instance
graphics_manager = GraphicsManager()
