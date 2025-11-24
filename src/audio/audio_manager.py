"""
Audio settings manager for TurboShells.

This module handles audio configuration, volume controls,
and sound management based on user preferences.
"""

import pygame
from typing import Dict, Optional
from core.config import config_manager, AudioSettings
from core.logging_config import get_logger


class AudioManager:
    """
    Manages audio settings and sound playback.

    Handles volume controls, sound toggles, and audio configuration
    based on user preferences.
    """

    def __init__(self):
        """Initialize audio manager."""
        self.logger = get_logger(__name__)
        self.current_settings: AudioSettings = None
        self.initialized: bool = False

        # Load settings
        self.load_settings()

        # Initialize audio system
        self.initialize_audio()

    def load_settings(self) -> None:
        """Load audio settings from configuration."""
        config = config_manager.get_config()
        self.current_settings = config.audio
        self.logger.info(
            f"Loaded audio settings: Master Volume {
                self.current_settings.master_volume}, Enabled {
                self.current_settings.enabled}"
        )

    def initialize_audio(self) -> bool:
        """
        Initialize the Pygame audio system.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            if not self.initialized:
                # Check if mixer is already initialized
                if not pygame.mixer.get_init():
                    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self.initialized = True
                self.logger.info("Audio system initialized successfully")

            # Apply initial settings
            self.apply_volume_settings()

            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize audio system: {e}")
            return False

    def apply_volume_settings(self) -> None:
        """Apply current volume settings to the audio system."""
        if not self.initialized:
            return

        try:
            # Set master volume
            master_volume = self.current_settings.get_music_volume()
            pygame.mixer.music.set_volume(master_volume)

            # Set SFX volume (will be applied to individual channels)
            self.logger.debug(
                f"Applied volume settings - Music: {master_volume:.2f}, SFX: {self.current_settings.get_sfx_volume():.2f}"
            )

        except Exception as e:
            self.logger.error(f"Failed to apply volume settings: {e}")

    def set_master_volume(self, volume: float) -> bool:
        """
        Set master volume level.

        Args:
            volume: Volume level (0.0 to 1.0)

        Returns:
            True if set successfully, False otherwise
        """
        volume = max(0.0, min(1.0, volume))
        self.current_settings.master_volume = volume

        # Apply to audio system
        self.apply_volume_settings()

        # Save configuration
        config_manager.save_config()

        self.logger.info(f"Master volume set to {volume:.2f}")
        return True

    def set_music_volume(self, volume: float) -> bool:
        """
        Set music volume level.

        Args:
            volume: Volume level (0.0 to 1.0)

        Returns:
            True if set successfully, False otherwise
        """
        volume = max(0.0, min(1.0, volume))
        self.current_settings.music_volume = volume

        # Apply to audio system
        if self.initialized:
            pygame.mixer.music.set_volume(self.current_settings.get_music_volume())

        # Save configuration
        config_manager.save_config()

        self.logger.info(f"Music volume set to {volume:.2f}")
        return True

    def set_sfx_volume(self, volume: float) -> bool:
        """
        Set sound effects volume level.

        Args:
            volume: Volume level (0.0 to 1.0)

        Returns:
            True if set successfully, False otherwise
        """
        volume = max(0.0, min(1.0, volume))
        self.current_settings.sfx_volume = volume

        # Note: SFX volume is applied per-channel when sounds are played

        # Save configuration
        config_manager.save_config()

        self.logger.info(f"SFX volume set to {volume:.2f}")
        return True

    def set_voice_volume(self, volume: float) -> bool:
        """
        Set voice volume level.

        Args:
            volume: Volume level (0.0 to 1.0)

        Returns:
            True if set successfully, False otherwise
        """
        volume = max(0.0, min(1.0, volume))
        self.current_settings.voice_volume = volume

        # Save configuration
        config_manager.save_config()

        self.logger.info(f"Voice volume set to {volume:.2f}")
        return True

    def toggle_audio(self, enabled: bool) -> bool:
        """
        Enable or disable audio.

        Args:
            enabled: Whether to enable audio

        Returns:
            True if toggle successful, False otherwise
        """
        self.current_settings.enabled = enabled

        if enabled:
            self.apply_volume_settings()
        else:
            # Mute everything
            if self.initialized:
                pygame.mixer.music.set_volume(0.0)

        # Save configuration
        config_manager.save_config()

        self.logger.info(f"Audio {'enabled' if enabled else 'disabled'}")
        return True

    def toggle_mute_when_inactive(self, enabled: bool) -> bool:
        """
        Enable or disable muting when window is inactive.

        Args:
            enabled: Whether to mute when inactive

        Returns:
            True if toggle successful, False otherwise
        """
        self.current_settings.mute_when_inactive = enabled

        # Save configuration
        config_manager.save_config()

        self.logger.info(f"Mute when inactive {'enabled' if enabled else 'disabled'}")
        return True

    def get_master_volume(self) -> float:
        """
        Get current master volume.

        Returns:
            Master volume (0.0 to 1.0)
        """
        return self.current_settings.master_volume

    def get_music_volume(self) -> float:
        """
        Get current music volume.

        Returns:
            Music volume (0.0 to 1.0)
        """
        return self.current_settings.music_volume

    def get_sfx_volume(self) -> float:
        """
        Get current SFX volume.

        Returns:
            SFX volume (0.0 to 1.0)
        """
        return self.current_settings.sfx_volume

    def get_voice_volume(self) -> float:
        """
        Get current voice volume.

        Returns:
            Voice volume (0.0 to 1.0)
        """
        return self.current_settings.voice_volume

    def is_audio_enabled(self) -> bool:
        """
        Check if audio is enabled.

        Returns:
            True if audio enabled, False otherwise
        """
        return self.current_settings.enabled

    def is_mute_when_inactive(self) -> bool:
        """
        Check if mute when inactive is enabled.

        Returns:
            True if mute when inactive enabled, False otherwise
        """
        return self.current_settings.mute_when_inactive

    def get_effective_music_volume(self) -> float:
        """
        Get effective music volume (considering master volume and enabled state).

        Returns:
            Effective music volume (0.0 to 1.0)
        """
        return self.current_settings.get_music_volume()

    def get_effective_sfx_volume(self) -> float:
        """
        Get effective SFX volume (considering master volume and enabled state).

        Returns:
            Effective SFX volume (0.0 to 1.0)
        """
        return self.current_settings.get_sfx_volume()

    def play_sound(
        self, sound_file: str, volume_override: float = None
    ) -> Optional[pygame.mixer.Sound]:
        """
        Play a sound effect with current volume settings.

        Args:
            sound_file: Path to sound file
            volume_override: Optional volume override (0.0 to 1.0)

        Returns:
            Sound object if successful, None otherwise
        """
        if not self.initialized or not self.current_settings.enabled:
            return None

        try:
            sound = pygame.mixer.Sound(sound_file)

            # Apply volume
            if volume_override is not None:
                volume = max(0.0, min(1.0, volume_override))
            else:
                volume = self.current_settings.get_sfx_volume()

            sound.set_volume(volume)
            sound.play()

            return sound

        except Exception as e:
            self.logger.error(f"Failed to play sound {sound_file}: {e}")
            return None

    def play_music(self, music_file: str, loops: int = -1) -> bool:
        """
        Play background music with current volume settings.

        Args:
            music_file: Path to music file
            loops: Number of times to loop (-1 for infinite)

        Returns:
            True if playback started successfully, False otherwise
        """
        if not self.initialized or not self.current_settings.enabled:
            return False

        try:
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.set_volume(self.current_settings.get_music_volume())
            pygame.mixer.music.play(loops)

            self.logger.info(f"Playing music: {music_file}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to play music {music_file}: {e}")
            return False

    def stop_music(self) -> None:
        """Stop currently playing music."""
        if self.initialized:
            pygame.mixer.music.stop()
            self.logger.info("Music stopped")

    def pause_music(self) -> None:
        """Pause currently playing music."""
        if self.initialized:
            pygame.mixer.music.pause()
            self.logger.info("Music paused")

    def resume_music(self) -> None:
        """Resume paused music."""
        if self.initialized:
            pygame.mixer.music.unpause()
            self.logger.info("Music resumed")

    def is_music_playing(self) -> bool:
        """
        Check if music is currently playing.

        Returns:
            True if music playing, False otherwise
        """
        if not self.initialized:
            return False
        return pygame.mixer.music.get_busy()

    def handle_window_focus(self, focused: bool) -> None:
        """
        Handle window focus changes for mute when inactive setting.

        Args:
            focused: Whether window is focused
        """
        if self.current_settings.mute_when_inactive:
            if not focused:
                # Window lost focus, mute audio
                if self.initialized:
                    pygame.mixer.music.set_volume(0.0)
                self.logger.debug("Window unfocused, audio muted")
            else:
                # Window gained focus, restore volume
                if self.initialized:
                    pygame.mixer.music.set_volume(
                        self.current_settings.get_music_volume()
                    )
                self.logger.debug("Window focused, audio restored")

    def get_audio_info(self) -> Dict[str, any]:
        """
        Get comprehensive audio information.

        Returns:
            Dictionary with audio information
        """
        info = {
            "initialized": self.initialized,
            "enabled": self.is_audio_enabled(),
            "master_volume": self.get_master_volume(),
            "music_volume": self.get_music_volume(),
            "sfx_volume": self.get_sfx_volume(),
            "voice_volume": self.get_voice_volume(),
            "effective_music_volume": self.get_effective_music_volume(),
            "effective_sfx_volume": self.get_effective_sfx_volume(),
            "mute_when_inactive": self.is_mute_when_inactive(),
            "music_playing": self.is_music_playing(),
        }

        if self.initialized:
            mixer_info = pygame.mixer.get_init()
            if mixer_info and len(mixer_info) >= 4:
                info.update(
                    {
                        "frequency": mixer_info[0],
                        "size": mixer_info[1],
                        "channels": mixer_info[2],
                        "buffer": mixer_info[3],
                    }
                )
            elif mixer_info:
                # Handle case where tuple has fewer elements
                info.update(
                    {
                        "frequency": mixer_info[0] if len(mixer_info) > 0 else 0,
                        "size": mixer_info[1] if len(mixer_info) > 1 else 0,
                        "channels": mixer_info[2] if len(mixer_info) > 2 else 0,
                        "buffer": mixer_info[3] if len(mixer_info) > 3 else 0,
                    }
                )

        return info

    def reset_to_defaults(self) -> None:
        """Reset audio settings to defaults."""
        self.current_settings = AudioSettings()
        self.apply_volume_settings()
        config_manager.save_config()
        self.logger.info("Audio settings reset to defaults")


# Global audio manager instance
audio_manager = AudioManager()
