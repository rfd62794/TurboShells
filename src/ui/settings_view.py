"""
Settings menu view for TurboShells.

This module provides a comprehensive settings interface with tabbed navigation
for managing all game configuration options.
"""

import pygame
from typing import Dict, List, Tuple, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass

from core.config import config_manager
from core.graphics_manager import graphics_manager
from core.audio_manager import audio_manager
from core.logging_config import get_logger


class SettingsTab(Enum):
    """Settings tabs enumeration."""

    GRAPHICS = "graphics"
    AUDIO = "audio"
    CONTROLS = "controls"
    GAMEPLAY = "gameplay"  # Combined Difficulty + Accessibility
    PROFILE = "profile"
    APPEARANCE = "appearance"
    SYSTEM = "system"  # Combined Saves + Privacy


@dataclass
class UIElement:
    """Base UI element for settings interface."""

    rect: pygame.Rect
    element_type: str
    label: str
    value: Any
    callback: Callable = None
    tooltip: str = ""
    enabled: bool = True


class SettingsView:
    """
    Main settings view with tabbed navigation.

    Provides a comprehensive interface for managing all game settings
    with organized tabs and intuitive controls.
    """

    # UI Colors (can be themed)
    COLORS = {
        "background": (40, 40, 40),
        "panel": (60, 60, 60),
        "border": (100, 100, 100),
        "text": (255, 255, 255),
        "text_disabled": (150, 150, 150),
        "button": (80, 80, 80),
        "button_hover": (100, 100, 100),
        "button_active": (120, 120, 120),
        "tab": (70, 70, 70),
        "tab_active": (90, 90, 90),
        "accent": (100, 150, 200),
        "slider_track": (50, 50, 50),
        "slider_handle": (120, 120, 120),
        "checkbox": (80, 80, 80),
        "checkbox_checked": (100, 150, 200),
    }

    # Fonts
    FONT_SIZES = {"title": 24, "tab": 16, "label": 14, "value": 14, "tooltip": 12}

    def __init__(self, screen_rect: pygame.Rect):
        """
        Initialize settings view.

        Args:
            screen_rect: Screen rectangle for positioning
        """
        self.screen_rect = screen_rect
        self.logger = get_logger(__name__)

        # Initialize fonts
        self.fonts = self._initialize_fonts()

        # Current state
        self.active_tab: SettingsTab = SettingsTab.GRAPHICS
        self.visible: bool = False
        self.needs_redraw: bool = True

        # UI elements
        self.tabs: Dict[SettingsTab, UIElement] = {}
        self.tab_content: Dict[SettingsTab, List[UIElement]] = {}
        self.buttons: List[UIElement] = []

        # Layout dimensions - Upper-left corner positioning for better tab fit
        panel_width = min(
            screen_rect.width * 0.95, 950
        )  # 95% of screen width, max 950px for maximum space
        panel_height = min(
            screen_rect.height * 0.9, 700
        )  # 90% of screen height, max 700px for more space

        self.panel_rect = pygame.Rect(
            30,  # Even closer to upper-left corner
            30,  # Even closer to upper-left corner  
            panel_width,
            panel_height,
        )

        self.tab_bar_rect = pygame.Rect(
            self.panel_rect.x + 10,
            self.panel_rect.y + 10,
            self.panel_rect.width - 20,
            40,
        )

        self.content_rect = pygame.Rect(
            self.panel_rect.x + 10,
            self.tab_bar_rect.bottom + 10,
            self.panel_rect.width - 20,
            self.panel_rect.height - self.tab_bar_rect.height - 60,
        )

        # Initialize UI elements
        self._initialize_tabs()
        self._initialize_buttons()
        self._initialize_tab_content()

        self.logger.info("Settings view initialized")

    def update_layout(self, screen_rect: pygame.Rect) -> None:
        """Update layout to match new screen dimensions."""
        self.screen_rect = screen_rect

        # Recalculate panel dimensions
        panel_width = min(
            screen_rect.width * 0.95, 950
        )  # 95% of screen width, max 950px for maximum space
        panel_height = min(
            screen_rect.height * 0.9, 700
        )  # 90% of screen height, max 700px for more space

        self.panel_rect = pygame.Rect(
            30,  # Even closer to upper-left corner
            30,  # Even closer to upper-left corner
            panel_width,
            panel_height,
        )

        # Update child rectangles
        self.tab_bar_rect = pygame.Rect(
            self.panel_rect.x + 10,
            self.panel_rect.y + 10,
            self.panel_rect.width - 20,
            40,
        )

        self.content_rect = pygame.Rect(
            self.panel_rect.x + 10,
            self.tab_bar_rect.bottom + 10,
            self.panel_rect.width - 20,
            self.panel_rect.height - self.tab_bar_rect.height - 60,
        )

        # Reinitialize UI elements with new layout
        self._initialize_tabs()
        self._initialize_buttons()
        self._initialize_tab_content()

        self.needs_redraw = True
        self.logger.info(
            f"Settings layout updated to {screen_rect.width}x{screen_rect.height}"
        )

    def _initialize_fonts(self) -> Dict[str, pygame.font.Font]:
        """Initialize fonts for the settings interface."""
        fonts = {}
        try:
            for name, size in self.FONT_SIZES.items():
                fonts[name] = pygame.font.Font(None, size)
        except Exception as e:
            self.logger.error(f"Failed to initialize fonts: {e}")
            # Fallback to default font
            for name, size in self.FONT_SIZES.items():
                fonts[name] = pygame.font.SysFont("Arial", size)
        return fonts

    def _initialize_tabs(self) -> None:
        """Initialize tab navigation elements."""
        tab_configs = [
            (SettingsTab.GRAPHICS, "Graphics"),
            (SettingsTab.AUDIO, "Audio"),
            (SettingsTab.CONTROLS, "Controls"),
            (SettingsTab.GAMEPLAY, "Gameplay"),
            (SettingsTab.PROFILE, "Profile"),
            (SettingsTab.APPEARANCE, "Appearance"),
            (SettingsTab.SYSTEM, "System"),
        ]

        # Calculate tab layout with better spacing
        num_tabs = len(tab_configs)
        available_width = self.tab_bar_rect.width - 20  # Leave some padding
        tab_spacing = 5  # Normal spacing now that we have fewer tabs
        
        # Calculate optimal tab width
        tab_width = (available_width - (num_tabs - 1) * tab_spacing) // num_tabs
        tab_width = max(100, min(tab_width, 120))  # Ensure reasonable min/max width
        tab_height = 35

        for i, (tab, label) in enumerate(tab_configs):
            x = self.tab_bar_rect.x + 10 + i * (tab_width + tab_spacing)
            y = self.tab_bar_rect.y

            rect = pygame.Rect(x, y, tab_width, tab_height)

            self.tabs[tab] = UIElement(
                rect=rect,
                element_type="tab",
                label=label,
                value=tab,
                callback=lambda t=tab: self._switch_tab(t),
            )

    def _initialize_buttons(self) -> None:
        """Initialize action buttons."""
        button_width = 80
        button_height = 30
        button_spacing = 10

        # Apply button
        apply_rect = pygame.Rect(
            self.panel_rect.right - button_width * 2 - button_spacing * 2,
            self.panel_rect.bottom - button_height - 10,
            button_width,
            button_height,
        )

        self.buttons.append(
            UIElement(
                rect=apply_rect,
                element_type="button",
                label="Apply",
                value="apply",
                callback=self._apply_settings,
            )
        )

        # Reset button
        reset_rect = pygame.Rect(
            self.panel_rect.right - button_width - button_spacing,
            self.panel_rect.bottom - button_height - 10,
            button_width,
            button_height,
        )

        self.buttons.append(
            UIElement(
                rect=reset_rect,
                element_type="button",
                label="Reset",
                value="reset",
                callback=self._reset_settings,
            )
        )

        # Close button
        close_rect = pygame.Rect(
            self.panel_rect.right - button_width,
            self.panel_rect.top + 5,
            button_width,
            25,
        )

        self.buttons.append(
            UIElement(
                rect=close_rect,
                element_type="button",
                label="X",
                value="close",
                callback=self._close_settings,
            )
        )

    def _initialize_tab_content(self) -> None:
        """Initialize content for each tab."""
        # Graphics tab content
        self._initialize_graphics_tab()

        # Audio tab content
        self._initialize_audio_tab()

        # Controls tab content
        self._initialize_controls_tab()

        # Gameplay tab content (combined Difficulty + Accessibility)
        self._initialize_gameplay_tab()

        # System tab content (combined Saves + Privacy)
        self._initialize_system_tab()

        # Other tabs will be initialized as needed
        self.tab_content[SettingsTab.PROFILE] = []
        self.tab_content[SettingsTab.APPEARANCE] = []

    def _initialize_gameplay_tab(self) -> None:
        """Initialize gameplay settings tab content (combined Difficulty + Accessibility)."""
        content = []
        y_offset = self.content_rect.y + 20
        line_height = 40

        config = config_manager.get_config()

        # Difficulty section header
        difficulty_header_rect = pygame.Rect(
            self.content_rect.x + 20, y_offset, self.content_rect.width - 40, 30
        )

        content.append(
            UIElement(
                rect=difficulty_header_rect,
                element_type="label",
                label="Difficulty Settings:",
                value="",
                callback=None,
                tooltip="Configure game difficulty",
            )
        )

        y_offset += 40

        # Difficulty level dropdown
        difficulty_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 200, 25)

        content.append(
            UIElement(
                rect=difficulty_rect,
                element_type="dropdown",
                label="Difficulty Level:",
                value=config.difficulty.difficulty_level,
                callback=self._on_difficulty_change,
                tooltip="Select game difficulty level",
            )
        )

        y_offset += line_height

        # Auto-save checkbox
        autosave_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 20, 20)

        content.append(
            UIElement(
                rect=autosave_rect,
                element_type="checkbox",
                label="Auto-save",
                value=config.difficulty.auto_save,
                callback=self._on_autosave_toggle,
                tooltip="Automatically save game progress",
            )
        )

        y_offset += line_height

        # Show tutorials checkbox
        tutorials_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 20, 20)

        content.append(
            UIElement(
                rect=tutorials_rect,
                element_type="checkbox",
                label="Show Tutorials",
                value=config.difficulty.show_tutorials,
                callback=self._on_tutorials_toggle,
                tooltip="Display tutorial hints and tips",
            )
        )

        y_offset += line_height

        # Confirm actions checkbox
        confirm_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 20, 20)

        content.append(
            UIElement(
                rect=confirm_rect,
                element_type="checkbox",
                label="Confirm Actions",
                value=config.difficulty.confirm_actions,
                callback=self._on_confirm_actions_toggle,
                tooltip="Require confirmation for important actions",
            )
        )

        y_offset += line_height + 20

        # Accessibility section header
        accessibility_header_rect = pygame.Rect(
            self.content_rect.x + 20, y_offset, self.content_rect.width - 40, 30
        )

        content.append(
            UIElement(
                rect=accessibility_header_rect,
                element_type="label",
                label="Accessibility Options:",
                value="",
                callback=None,
                tooltip="Configure accessibility features",
            )
        )

        y_offset += 40

        # Colorblind mode dropdown
        colorblind_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 200, 25)

        content.append(
            UIElement(
                rect=colorblind_rect,
                element_type="dropdown",
                label="Colorblind Mode:",
                value=config.accessibility.colorblind_mode,
                callback=self._on_colorblind_mode_change,
                tooltip="Select colorblind assistance mode",
            )
        )

        y_offset += line_height

        # High contrast checkbox
        high_contrast_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 20, 20)

        content.append(
            UIElement(
                rect=high_contrast_rect,
                element_type="checkbox",
                label="High Contrast",
                value=config.accessibility.high_contrast,
                callback=self._on_high_contrast_toggle,
                tooltip="Increase visual contrast for better visibility",
            )
        )

        y_offset += line_height

        # Large text checkbox
        large_text_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 20, 20)

        content.append(
            UIElement(
                rect=large_text_rect,
                element_type="checkbox",
                label="Large Text",
                value=config.accessibility.large_text,
                callback=self._on_large_text_toggle,
                tooltip="Use larger text for better readability",
            )
        )

        y_offset += line_height

        # Reduced motion checkbox
        reduced_motion_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 20, 20)

        content.append(
            UIElement(
                rect=reduced_motion_rect,
                element_type="checkbox",
                label="Reduced Motion",
                value=config.accessibility.reduced_motion,
                callback=self._on_reduced_motion_toggle,
                tooltip="Reduce animations and motion effects",
            )
        )

        self.tab_content[SettingsTab.GAMEPLAY] = content

    def _initialize_system_tab(self) -> None:
        """Initialize system settings tab content (combined Saves + Privacy)."""
        content = []
        y_offset = self.content_rect.y + 20
        line_height = 40

        # Save management section header
        saves_header_rect = pygame.Rect(
            self.content_rect.x + 20, y_offset, self.content_rect.width - 40, 30
        )

        content.append(
            UIElement(
                rect=saves_header_rect,
                element_type="label",
                label="Save Management:",
                value="",
                callback=None,
                tooltip="Manage game saves and backups",
            )
        )

        y_offset += 40

        # Save file list
        save_list_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 300, 200)

        content.append(
            UIElement(
                rect=save_list_rect,
                element_type="list",
                label="Save Files:",
                value="save_list",
                callback=self._on_save_file_select,
                tooltip="Select a save file to manage",
            )
        )

        y_offset += 220

        # Backup button
        backup_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 100, 30)

        content.append(
            UIElement(
                rect=backup_rect,
                element_type="button",
                label="Create Backup",
                value="backup",
                callback=self._on_create_backup,
                tooltip="Create a backup of the selected save file",
            )
        )

        # Export button
        export_rect = pygame.Rect(self.content_rect.x + 130, y_offset, 100, 30)

        content.append(
            UIElement(
                rect=export_rect,
                element_type="button",
                label="Export",
                value="export",
                callback=self._on_export_save,
                tooltip="Export save file to external location",
            )
        )

        y_offset += 40

        # Import button
        import_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 100, 30)

        content.append(
            UIElement(
                rect=import_rect,
                element_type="button",
                label="Import",
                value="import",
                callback=self._on_import_save,
                tooltip="Import save file from external location",
            )
        )

        # Delete button
        delete_rect = pygame.Rect(self.content_rect.x + 130, y_offset, 100, 30)

        content.append(
            UIElement(
                rect=delete_rect,
                element_type="button",
                label="Delete",
                value="delete",
                callback=self._on_delete_save,
                tooltip="Delete selected save file",
            )
        )

        y_offset += 40

        # Auto-save interval slider
        autosave_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 200, 20)

        config = config_manager.get_config()
        content.append(
            UIElement(
                rect=autosave_rect,
                element_type="slider",
                label="Auto-save Interval (minutes):",
                value=config.controls.auto_save_interval / 60,  # Convert to minutes
                callback=self._on_autosave_change,
                tooltip="Set automatic save interval",
            )
        )

        y_offset += line_height + 20

        # Privacy section header
        privacy_header_rect = pygame.Rect(
            self.content_rect.x + 20, y_offset, self.content_rect.width - 40, 30
        )

        content.append(
            UIElement(
                rect=privacy_header_rect,
                element_type="label",
                label="Privacy Settings:",
                value="",
                callback=None,
                tooltip="Configure data collection and privacy",
            )
        )

        y_offset += 40

        # Analytics checkbox
        analytics_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 20, 20)

        content.append(
            UIElement(
                rect=analytics_rect,
                element_type="checkbox",
                label="Share Analytics",
                value=True,  # Default value
                callback=self._on_analytics_toggle,
                tooltip="Share anonymous usage data to improve the game",
            )
        )

        y_offset += line_height

        # Crash reports checkbox
        crash_reports_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 20, 20)

        content.append(
            UIElement(
                rect=crash_reports_rect,
                element_type="checkbox",
                label="Send Crash Reports",
                value=True,  # Default value
                callback=self._on_crash_reports_toggle,
                tooltip="Automatically send crash reports to help fix bugs",
            )
        )

        y_offset += line_height

        # Data collection checkbox
        data_collection_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 20, 20)

        content.append(
            UIElement(
                rect=data_collection_rect,
                element_type="checkbox",
                label="Performance Data",
                value=False,  # Default value
                callback=self._on_performance_data_toggle,
                tooltip="Share performance data for optimization",
            )
        )

        self.tab_content[SettingsTab.SYSTEM] = content

    def _initialize_controls_tab(self) -> None:
        """Initialize controls settings tab content."""
        content = []
        y_offset = self.content_rect.y + 20
        line_height = 40

        config = config_manager.get_config()

        # Mouse sensitivity slider
        mouse_sensitivity_rect = pygame.Rect(
            self.content_rect.x + 20, y_offset, 200, 20
        )

        content.append(
            UIElement(
                rect=mouse_sensitivity_rect,
                element_type="slider",
                label="Mouse Sensitivity:",
                value=config.controls.mouse_sensitivity,
                callback=self._on_mouse_sensitivity_change,
                tooltip="Adjust mouse sensitivity for camera control",
            )
        )

        y_offset += line_height

        # Invert mouse Y checkbox
        invert_mouse_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 20, 20)

        content.append(
            UIElement(
                rect=invert_mouse_rect,
                element_type="checkbox",
                label="Invert Mouse Y",
                value=config.controls.invert_mouse_y,
                callback=self._on_invert_mouse_y_change,
                tooltip="Invert vertical mouse movement",
            )
        )

        y_offset += line_height

        # Key bindings section
        key_bindings_label_rect = pygame.Rect(
            self.content_rect.x + 20, y_offset, self.content_rect.width - 40, 30
        )

        content.append(
            UIElement(
                rect=key_bindings_label_rect,
                element_type="label",
                label="Key Bindings:",
                value="",
                callback=None,
                tooltip="Configure keyboard controls",
            )
        )

        y_offset += 40

        # Sample key bindings (placeholder)
        key_bindings = [
            ("Move Forward", "W"),
            ("Move Backward", "S"),
            ("Move Left", "A"),
            ("Move Right", "D"),
            ("Jump", "Space"),
            ("Sprint", "Shift"),
            ("Interact", "E"),
            ("Menu", "ESC"),
        ]

        for i, (action, key) in enumerate(key_bindings):
            if i >= 8:  # Limit to 8 bindings
                break

            # Action label
            action_rect = pygame.Rect(
                self.content_rect.x + 20, y_offset + i * 30, 150, 25
            )

            content.append(
                UIElement(
                    rect=action_rect,
                    element_type="label",
                    label=action,
                    value=key,
                    callback=None,
                    tooltip=f"Current key: {key}",
                )
            )

            # Key binding button
            key_rect = pygame.Rect(self.content_rect.x + 180, y_offset + i * 30, 80, 25)

            content.append(
                UIElement(
                    rect=key_rect,
                    element_type="button",
                    label=key,
                    value=f"key_{action.lower().replace(' ', '_')}",
                    callback=self._on_key_binding_change,
                    tooltip=f"Click to change {action} key",
                )
            )

        self.tab_content[SettingsTab.CONTROLS] = content

    def _initialize_graphics_tab(self) -> None:
        """Initialize graphics settings tab content."""
        content = []
        y_offset = self.content_rect.y + 20
        line_height = 35

        config = config_manager.get_config()

        # Resolution dropdown
        resolution_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 200, 25)

        current_resolution = (
            f"{config.graphics.resolution_width}x{config.graphics.resolution_height}"
        )
        content.append(
            UIElement(
                rect=resolution_rect,
                element_type="dropdown",
                label="Resolution:",
                value=current_resolution,
                callback=self._on_resolution_change,
                tooltip="Select screen resolution",
            )
        )

        y_offset += line_height

        # Fullscreen checkbox
        fullscreen_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 20, 20)

        content.append(
            UIElement(
                rect=fullscreen_rect,
                element_type="checkbox",
                label="Fullscreen",
                value=config.graphics.fullscreen,
                callback=self._on_fullscreen_toggle,
                tooltip="Toggle fullscreen mode",
            )
        )

        y_offset += line_height

        # Quality dropdown
        quality_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 150, 25)

        content.append(
            UIElement(
                rect=quality_rect,
                element_type="dropdown",
                label="Quality:",
                value=config.graphics.quality_level,
                callback=self._on_quality_change,
                tooltip="Select graphics quality",
            )
        )

        y_offset += line_height

        # VSync checkbox
        vsync_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 20, 20)

        content.append(
            UIElement(
                rect=vsync_rect,
                element_type="checkbox",
                label="VSync",
                value=config.graphics.vsync,
                callback=self._on_vsync_toggle,
                tooltip="Enable vertical sync",
            )
        )

        self.tab_content[SettingsTab.GRAPHICS] = content

    def _initialize_audio_tab(self) -> None:
        """Initialize audio settings tab content."""
        content = []
        y_offset = self.content_rect.y + 20
        line_height = 40

        config = config_manager.get_config()

        # Master volume slider
        master_volume_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 200, 20)

        content.append(
            UIElement(
                rect=master_volume_rect,
                element_type="slider",
                label="Master Volume",
                value=config.audio.master_volume,
                callback=self._on_master_volume_change,
                tooltip="Adjust master volume",
            )
        )

        y_offset += line_height

        # Music volume slider
        music_volume_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 200, 20)

        content.append(
            UIElement(
                rect=music_volume_rect,
                element_type="slider",
                label="Music Volume",
                value=config.audio.music_volume,
                callback=self._on_music_volume_change,
                tooltip="Adjust music volume",
            )
        )

        y_offset += line_height

        # SFX volume slider
        sfx_volume_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 200, 20)

        content.append(
            UIElement(
                rect=sfx_volume_rect,
                element_type="slider",
                label="SFX Volume",
                value=config.audio.sfx_volume,
                callback=self._on_sfx_volume_change,
                tooltip="Adjust sound effects volume",
            )
        )

        y_offset += line_height

        # Audio enabled checkbox
        audio_enabled_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 20, 20)

        content.append(
            UIElement(
                rect=audio_enabled_rect,
                element_type="checkbox",
                label="Enable Audio",
                value=config.audio.enabled,
                callback=self._on_audio_enabled_toggle,
                tooltip="Enable/disable all audio",
            )
        )

        self.tab_content[SettingsTab.AUDIO] = content

    def _switch_tab(self, tab: SettingsTab) -> None:
        """Switch to a different settings tab."""
        self.active_tab = tab
        self.needs_redraw = True
        self.logger.debug(f"Switched to {tab.value} tab")

    def show(self) -> None:
        """Show the settings view."""
        self.visible = True
        self.needs_redraw = True
        self.logger.info("Settings view shown")

    def hide(self) -> None:
        """Hide the settings view."""
        self.visible = False
        self.logger.info("Settings view hidden")

    def toggle(self) -> None:
        """Toggle settings view visibility."""
        if self.visible:
            self.hide()
        else:
            self.show()

    # Callback methods for the new combined tabs
    def _on_analytics_toggle(self) -> None:
        """Handle analytics toggle."""
        self.logger.info("Analytics setting toggled")

    def _on_crash_reports_toggle(self) -> None:
        """Handle crash reports toggle."""
        self.logger.info("Crash reports setting toggled")

    def _on_performance_data_toggle(self) -> None:
        """Handle performance data toggle."""
        self.logger.info("Performance data setting toggled")

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events for the settings view.

        Args:
            event: Pygame event

        Returns:
            True if event was handled, False otherwise
        """
        if not self.visible:
            return False

        # Handle tab clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # Check tab clicks
            for tab, element in self.tabs.items():
                if element.rect.collidepoint(mouse_pos):
                    element.callback()
                    return True

            # Check button clicks
            for button in self.buttons:
                if button.rect.collidepoint(mouse_pos):
                    button.callback()
                    return True

            # Check content element clicks
            content_elements = self.tab_content.get(self.active_tab, [])
            for element in content_elements:
                if element.rect.collidepoint(mouse_pos):
                    if element.callback:
                        element.callback()
                    return True

        return False

    def update(self, dt: float) -> None:
        """
        Update the settings view.

        Args:
            dt: Time delta since last update
        """
        if not self.visible:
            return

        # Update animations, tooltips, etc.
        pass

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the settings view.

        Args:
            screen: Surface to draw on
        """
        if not self.visible:
            return

        # Draw main panel
        pygame.draw.rect(screen, self.COLORS["panel"], self.panel_rect)
        pygame.draw.rect(screen, self.COLORS["border"], self.panel_rect, 2)

        # Draw title
        title_text = self.fonts["title"].render("Settings", True, self.COLORS["text"])
        title_rect = title_text.get_rect(
            centerx=self.panel_rect.centerx, y=self.panel_rect.y + 5
        )
        screen.blit(title_text, title_rect)

        # Draw tab bar
        self._draw_tabs(screen)

        # Draw tab content
        self._draw_tab_content(screen)

        # Draw buttons
        self._draw_buttons(screen)

    def _draw_tabs(self, screen: pygame.Surface) -> None:
        """Draw tab navigation."""
        for tab, element in self.tabs.items():
            # Determine tab color
            if tab == self.active_tab:
                color = self.COLORS["tab_active"]
            else:
                color = self.COLORS["tab"]

            # Draw tab background
            pygame.draw.rect(screen, color, element.rect)
            pygame.draw.rect(screen, self.COLORS["border"], element.rect, 1)

            # Draw tab label with appropriate font size
            label_color = (
                self.COLORS["text"] if tab == self.active_tab else self.COLORS["text"]
            )
            
            # Use appropriate font size based on tab width
            if element.rect.width < 95:
                font_size = 11
            elif element.rect.width < 105:
                font_size = 12
            else:
                font_size = 13
            
            tab_font = pygame.font.Font(None, font_size)
            label_text = tab_font.render(element.label, True, label_color)
            label_rect = label_text.get_rect(center=element.rect.center)
            
            # Smart text truncation if needed
            max_width = element.rect.width - 6
            if label_rect.width > max_width:
                # Calculate how many characters can fit
                avg_char_width = label_rect.width // len(element.label)
                max_chars = max_width // avg_char_width
                
                if max_chars >= 3:
                    truncated_label = element.label[:max_chars-1] + "…" if len(element.label) > max_chars else element.label
                else:
                    # For very narrow tabs, use first letter only
                    truncated_label = element.label[0].upper()
                
                label_text = tab_font.render(truncated_label, True, label_color)
                label_rect = label_text.get_rect(center=element.rect.center)
            
            screen.blit(label_text, label_rect)

    def _draw_tab_content(self, screen: pygame.Surface) -> None:
        """Draw content for the active tab."""
        content_elements = self.tab_content.get(self.active_tab, [])

        for element in content_elements:
            self._draw_ui_element(screen, element)

    def _draw_ui_element(self, screen: pygame.Surface, element: UIElement) -> None:
        """Draw a single UI element."""
        if element.element_type == "dropdown":
            self._draw_dropdown(screen, element)
        elif element.element_type == "checkbox":
            self._draw_checkbox(screen, element)
        elif element.element_type == "slider":
            self._draw_slider(screen, element)
        elif element.element_type == "button":
            self._draw_button(screen, element)
        elif element.element_type == "list":
            self._draw_list(screen, element)
        elif element.element_type == "label":
            self._draw_label(screen, element)

    def _draw_buttons(self, screen: pygame.Surface) -> None:
        """Draw action buttons."""
        for button in self.buttons:
            self._draw_button(screen, button)

    # Placeholder drawing methods (can be implemented as needed)
    def _draw_dropdown(self, screen: pygame.Surface, element: UIElement) -> None:
        """Draw a dropdown element."""
        pygame.draw.rect(screen, self.COLORS["button"], element.rect)
        pygame.draw.rect(screen, self.COLORS["border"], element.rect, 1)
        
        label_text = self.fonts["label"].render(element.label, True, self.COLORS["text"])
        screen.blit(label_text, (element.rect.x + 5, element.rect.y + 5))

    def _draw_checkbox(self, screen: pygame.Surface, element: UIElement) -> None:
        """Draw a checkbox element."""
        pygame.draw.rect(screen, self.COLORS["checkbox"], element.rect)
        pygame.draw.rect(screen, self.COLORS["border"], element.rect, 1)
        
        if element.value:
            # Draw checkmark
            pygame.draw.line(screen, self.COLORS["checkbox_checked"], 
                           (element.rect.x + 3, element.rect.y + 10),
                           (element.rect.x + 8, element.rect.y + 15), 2)
            pygame.draw.line(screen, self.COLORS["checkbox_checked"],
                           (element.rect.x + 8, element.rect.y + 15),
                           (element.rect.x + 17, element.rect.y + 5), 2)
        
        label_text = self.fonts["label"].render(element.label, True, self.COLORS["text"])
        screen.blit(label_text, (element.rect.x + 25, element.rect.y))

    def _draw_slider(self, screen: pygame.Surface, element: UIElement) -> None:
        """Draw a slider element."""
        # Draw track
        pygame.draw.rect(screen, self.COLORS["slider_track"], element.rect)
        
        # Draw handle
        handle_x = element.rect.x + int(element.value * element.rect.width)
        handle_rect = pygame.Rect(handle_x - 5, element.rect.y - 2, 10, element.rect.height + 4)
        pygame.draw.rect(screen, self.COLORS["slider_handle"], handle_rect)
        
        label_text = self.fonts["label"].render(element.label, True, self.COLORS["text"])
        screen.blit(label_text, (element.rect.x, element.rect.y - 20))

    def _draw_button(self, screen: pygame.Surface, element: UIElement) -> None:
        """Draw a button element."""
        pygame.draw.rect(screen, self.COLORS["button"], element.rect)
        pygame.draw.rect(screen, self.COLORS["border"], element.rect, 1)
        
        label_text = self.fonts["label"].render(element.label, True, self.COLORS["text"])
        label_rect = label_text.get_rect(center=element.rect.center)
        screen.blit(label_text, label_rect)

    def _draw_list(self, screen: pygame.Surface, element: UIElement) -> None:
        """Draw a list element."""
        pygame.draw.rect(screen, self.COLORS["button"], element.rect)
        pygame.draw.rect(screen, self.COLORS["border"], element.rect, 1)
        
        label_text = self.fonts["label"].render(element.label, True, self.COLORS["text"])
        screen.blit(label_text, (element.rect.x + 5, element.rect.y + 5))

    def _draw_label(self, screen: pygame.Surface, element: UIElement) -> None:
        """Draw a label element."""
        label_text = self.fonts["label"].render(element.label, True, self.COLORS["text"])
        screen.blit(label_text, (element.rect.x, element.rect.y))
        colorblind_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 200, 25)

        content.append(
            UIElement(
                rect=colorblind_rect,
                element_type="dropdown",
                label="Colorblind Mode:",
                value=config.accessibility.colorblind_mode,
                callback=self._on_colorblind_mode_change,
                tooltip="Select colorblind assistance mode",
            )
        )

        y_offset += line_height

        # High contrast checkbox
        high_contrast_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 20, 20)

        content.append(
            UIElement(
                rect=high_contrast_rect,
                element_type="checkbox",
                label="High Contrast",
                value=config.accessibility.high_contrast,
                callback=self._on_high_contrast_toggle,
                tooltip="Increase visual contrast for better visibility",
            )
        )

        y_offset += line_height

        # Large text checkbox
        large_text_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 20, 20)

        content.append(
            UIElement(
                rect=large_text_rect,
                element_type="checkbox",
                label="Large Text",
                value=config.accessibility.large_text,
                callback=self._on_large_text_toggle,
                tooltip="Use larger text for better readability",
            )
        )

        y_offset += line_height

        # Reduced motion checkbox
        reduced_motion_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 20, 20)

        content.append(
            UIElement(
                rect=reduced_motion_rect,
                element_type="checkbox",
                label="Reduced Motion",
                value=config.accessibility.reduced_motion,
                callback=self._on_reduced_motion_toggle,
                tooltip="Reduce animations and motion effects",
            )
        )

        self.tab_content[SettingsTab.DIFFICULTY] = content

    def _initialize_graphics_tab(self) -> None:
        """Initialize graphics settings tab content."""
        content = []
        y_offset = self.content_rect.y + 20
        line_height = 35

        config = config_manager.get_config()

        # Resolution dropdown
        resolution_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 200, 25)

        current_resolution = (
            f"{config.graphics.resolution_width}x{config.graphics.resolution_height}"
        )
        content.append(
            UIElement(
                rect=resolution_rect,
                element_type="dropdown",
                label="Resolution:",
                value=current_resolution,
                callback=self._on_resolution_change,
                tooltip="Select screen resolution",
            )
        )

        y_offset += line_height

        # Fullscreen checkbox
        fullscreen_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 20, 20)

        content.append(
            UIElement(
                rect=fullscreen_rect,
                element_type="checkbox",
                label="Fullscreen",
                value=config.graphics.fullscreen,
                callback=self._on_fullscreen_toggle,
                tooltip="Toggle fullscreen mode",
            )
        )

        y_offset += line_height

        # Quality dropdown
        quality_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 150, 25)

        content.append(
            UIElement(
                rect=quality_rect,
                element_type="dropdown",
                label="Quality:",
                value=config.graphics.quality_level,
                callback=self._on_quality_change,
                tooltip="Select graphics quality",
            )
        )

        y_offset += line_height

        # VSync checkbox
        vsync_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 20, 20)

        content.append(
            UIElement(
                rect=vsync_rect,
                element_type="checkbox",
                label="VSync",
                value=config.graphics.vsync,
                callback=self._on_vsync_toggle,
                tooltip="Enable vertical sync",
            )
        )

        self.tab_content[SettingsTab.GRAPHICS] = content

    def _initialize_audio_tab(self) -> None:
        """Initialize audio settings tab content."""
        content = []
        y_offset = self.content_rect.y + 20
        line_height = 40

        config = config_manager.get_config()

        # Master volume slider
        master_volume_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 200, 20)

        content.append(
            UIElement(
                rect=master_volume_rect,
                element_type="slider",
                label="Master Volume",
                value=config.audio.master_volume,
                callback=self._on_master_volume_change,
                tooltip="Adjust master volume",
            )
        )

        y_offset += line_height

        # Music volume slider
        music_volume_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 200, 20)

        content.append(
            UIElement(
                rect=music_volume_rect,
                element_type="slider",
                label="Music Volume",
                value=config.audio.music_volume,
                callback=self._on_music_volume_change,
                tooltip="Adjust music volume",
            )
        )

        y_offset += line_height

        # SFX volume slider
        sfx_volume_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 200, 20)

        content.append(
            UIElement(
                rect=sfx_volume_rect,
                element_type="slider",
                label="SFX Volume",
                value=config.audio.sfx_volume,
                callback=self._on_sfx_volume_change,
                tooltip="Adjust sound effects volume",
            )
        )

        y_offset += line_height

        # Audio enabled checkbox
        audio_enabled_rect = pygame.Rect(self.content_rect.x + 20, y_offset, 20, 20)

        content.append(
            UIElement(
                rect=audio_enabled_rect,
                element_type="checkbox",
                label="Enable Audio",
                value=config.audio.enabled,
                callback=self._on_audio_enabled_toggle,
                tooltip="Enable/disable all audio",
            )
        )

        self.tab_content[SettingsTab.AUDIO] = content

    def _switch_tab(self, tab: SettingsTab) -> None:
        """Switch to a different settings tab."""
        self.active_tab = tab
        self.needs_redraw = True
        self.logger.debug(f"Switched to {tab.value} tab")

    def show(self) -> None:
        """Show the settings view."""
        self.visible = True
        self.needs_redraw = True
        self.logger.info("Settings view shown")

    def hide(self) -> None:
        """Hide the settings view."""
        self.visible = False
        self.logger.info("Settings view hidden")

    def toggle(self) -> None:
        """Toggle settings view visibility."""
        if self.visible:
            self.hide()
        else:
            self.show()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events for the settings view.

        Args:
            event: Pygame event

        Returns:
            True if event was handled, False otherwise
        """
        if not self.visible:
            return False

        # Handle tab clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # Check tab clicks
            for tab, element in self.tabs.items():
                if element.rect.collidepoint(mouse_pos):
                    element.callback()
                    return True

            # Check button clicks
            for button in self.buttons:
                if button.rect.collidepoint(mouse_pos):
                    button.callback()
                    return True

            # Check content element clicks
            content_elements = self.tab_content.get(self.active_tab, [])
            for element in content_elements:
                if element.rect.collidepoint(mouse_pos):
                    if element.callback:
                        element.callback()
                    return True

        return False

    def update(self, dt: float) -> None:
        """
        Update the settings view.

        Args:
            dt: Time delta since last update
        """
        if not self.visible:
            return

        # Update animations, tooltips, etc.
        pass

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the settings view.

        Args:
            screen: Surface to draw on
        """
        if not self.visible:
            return

        # Draw main panel
        pygame.draw.rect(screen, self.COLORS["panel"], self.panel_rect)
        pygame.draw.rect(screen, self.COLORS["border"], self.panel_rect, 2)

        # Draw title
        title_text = self.fonts["title"].render("Settings", True, self.COLORS["text"])
        title_rect = title_text.get_rect(
            centerx=self.panel_rect.centerx, y=self.panel_rect.y + 5
        )
        screen.blit(title_text, title_rect)

        # Draw tab bar
        self._draw_tabs(screen)

        # Draw tab content
        self._draw_tab_content(screen)

        # Draw buttons
        self._draw_buttons(screen)

    def _draw_tabs(self, screen: pygame.Surface) -> None:
        """Draw tab navigation."""
        for tab, element in self.tabs.items():
            # Determine tab color
            if tab == self.active_tab:
                color = self.COLORS["tab_active"]
            else:
                color = self.COLORS["tab"]

            # Draw tab background
            pygame.draw.rect(screen, color, element.rect)
            pygame.draw.rect(screen, self.COLORS["border"], element.rect, 1)

            # Draw tab label with appropriate font size
            label_color = (
                self.COLORS["text"] if tab == self.active_tab else self.COLORS["text"]
            )
            
            # Use appropriate font size based on tab width
            if element.rect.width < 95:
                font_size = 11
            elif element.rect.width < 105:
                font_size = 12
            else:
                font_size = 13
            
            tab_font = pygame.font.Font(None, font_size)
            label_text = tab_font.render(element.label, True, label_color)
            label_rect = label_text.get_rect(center=element.rect.center)
            
            # Smart text truncation if needed
            max_width = element.rect.width - 6
            if label_rect.width > max_width:
                # Calculate how many characters can fit
                avg_char_width = label_rect.width // len(element.label)
                max_chars = max_width // avg_char_width
                
                if max_chars >= 3:
                    truncated_label = element.label[:max_chars-1] + "…" if len(element.label) > max_chars else element.label
                else:
                    # For very narrow tabs, use first letter only
                    truncated_label = element.label[0].upper()
                
                label_text = tab_font.render(truncated_label, True, label_color)
                label_rect = label_text.get_rect(center=element.rect.center)
            
            screen.blit(label_text, label_rect)

    def _draw_tab_content(self, screen: pygame.Surface) -> None:
        """Draw content for the active tab."""
        content_elements = self.tab_content.get(self.active_tab, [])

        for element in content_elements:
            self._draw_ui_element(screen, element)

    def _draw_ui_element(self, screen: pygame.Surface, element: UIElement) -> None:
        """Draw a single UI element."""
        if element.element_type == "dropdown":
            self._draw_dropdown(screen, element)
        elif element.element_type == "checkbox":
            self._draw_checkbox(screen, element)
        elif element.element_type == "slider":
            self._draw_slider(screen, element)
        elif element.element_type == "button":
            self._draw_button(screen, element)
        elif element.element_type == "list":
            self._draw_list(screen, element)
        elif element.element_type == "label":
            self._draw_label(screen, element)

    def _draw_dropdown(self, screen: pygame.Surface, element: UIElement) -> None:
        """Draw a dropdown element."""
        # Draw dropdown background
        pygame.draw.rect(screen, self.COLORS["button"], element.rect)
        pygame.draw.rect(screen, self.COLORS["border"], element.rect, 1)

        # Draw label
        label_text = self.fonts["label"].render(
            element.label, True, self.COLORS["text"]
        )
        label_rect = label_text.get_rect(
            right=element.rect.left - 10, centery=element.rect.centery
        )
        screen.blit(label_text, label_rect)

        # Draw value
        value_text = self.fonts["value"].render(
            str(element.value), True, self.COLORS["text"]
        )
        value_rect = value_text.get_rect(
            left=element.rect.left + 5, centery=element.rect.centery
        )
        screen.blit(value_text, value_rect)

        # Draw dropdown arrow
        arrow_points = [
            (element.rect.right - 15, element.rect.centery - 5),
            (element.rect.right - 5, element.rect.centery - 5),
            (element.rect.right - 10, element.rect.centery + 5),
        ]
        pygame.draw.polygon(screen, self.COLORS["text"], arrow_points)

    def _draw_checkbox(self, screen: pygame.Surface, element: UIElement) -> None:
        """Draw a checkbox element."""
        # Draw checkbox
        color = (
            self.COLORS["checkbox_checked"]
            if element.value
            else self.COLORS["checkbox"]
        )
        pygame.draw.rect(screen, color, element.rect)
        pygame.draw.rect(screen, self.COLORS["border"], element.rect, 2)

        # Draw checkmark if checked
        if element.value:
            check_points = [
                (element.rect.left + 3, element.rect.centery),
                (element.rect.left + 8, element.rect.bottom - 3),
                (element.rect.right - 3, element.rect.top + 3),
            ]
            pygame.draw.lines(screen, self.COLORS["text"], False, check_points, 2)

        # Draw label
        label_text = self.fonts["label"].render(
            element.label, True, self.COLORS["text"]
        )
        label_rect = label_text.get_rect(
            left=element.rect.right + 10, centery=element.rect.centery
        )
        screen.blit(label_text, label_rect)

    def _draw_slider(self, screen: pygame.Surface, element: UIElement) -> None:
        """Draw a slider element."""
        # Draw label
        label_text = self.fonts["label"].render(
            element.label, True, self.COLORS["text"]
        )
        label_rect = label_text.get_rect(
            left=element.rect.left, top=element.rect.top - 20
        )
        screen.blit(label_text, label_rect)

        # Draw track
        track_rect = pygame.Rect(
            element.rect.x, element.rect.centery - 2, element.rect.width, 4
        )
        pygame.draw.rect(screen, self.COLORS["slider_track"], track_rect)

        # Draw handle
        handle_x = element.rect.x + int(element.value * element.rect.width)
        handle_rect = pygame.Rect(handle_x - 8, element.rect.centery - 8, 16, 16)
        pygame.draw.rect(screen, self.COLORS["slider_handle"], handle_rect)
        pygame.draw.rect(screen, self.COLORS["border"], handle_rect, 1)

        # Draw value
        value_text = self.fonts["value"].render(
            f"{int(element.value * 100)}%", True, self.COLORS["text"]
        )
        value_rect = value_text.get_rect(
            left=element.rect.right + 10, centery=element.rect.centery
        )
        screen.blit(value_text, value_rect)

    def _draw_button(self, screen: pygame.Surface, element: UIElement) -> None:
        """Draw a button element."""
        # Determine button color based on hover state
        mouse_pos = pygame.mouse.get_pos()
        if element.rect.collidepoint(mouse_pos):
            color = self.COLORS["button_hover"]
        else:
            color = self.COLORS["button"]

        # Draw button background
        pygame.draw.rect(screen, color, element.rect)
        pygame.draw.rect(screen, self.COLORS["border"], element.rect, 1)

        # Draw button label
        label_text = self.fonts["label"].render(
            element.label, True, self.COLORS["text"]
        )
        label_rect = label_text.get_rect(center=element.rect.center)
        screen.blit(label_text, label_rect)

    def _draw_list(self, screen: pygame.Surface, element: UIElement) -> None:
        """Draw a list element."""
        # Draw list background
        pygame.draw.rect(screen, self.COLORS["button"], element.rect)
        pygame.draw.rect(screen, self.COLORS["border"], element.rect, 1)

        # Draw label
        label_text = self.fonts["label"].render(
            element.label, True, self.COLORS["text"]
        )
        label_rect = label_text.get_rect(
            left=element.rect.left, top=element.rect.top - 20
        )
        screen.blit(label_text, label_rect)

        # Draw sample save files (placeholder)
        sample_saves = [
            "Save 1 - 2025-11-23",
            "Save 2 - 2025-11-22",
            "Save 3 - 2025-11-21",
        ]
        for i, save_name in enumerate(sample_saves[:5]):  # Show max 5 saves
            item_y = element.rect.y + 5 + i * 25
            if item_y + 20 < element.rect.bottom:
                save_text = self.fonts["value"].render(
                    save_name, True, self.COLORS["text"]
                )
                screen.blit(save_text, (element.rect.x + 5, item_y))

    def _draw_label(self, screen: pygame.Surface, element: UIElement) -> None:
        """Draw a label element."""
        # Draw label text
        label_text = self.fonts["label"].render(
            element.label, True, self.COLORS["text"]
        )

        if element.value:  # If there's a value, draw it next to the label
            value_text = self.fonts["value"].render(
                str(element.value), True, self.COLORS["text"]
            )

            # Draw label
            label_rect = label_text.get_rect(
                left=element.rect.left, centery=element.rect.centery
            )
            screen.blit(label_text, label_rect)

            # Draw value
            value_rect = value_text.get_rect(
                left=label_rect.right + 10, centery=element.rect.centery
            )
            screen.blit(value_text, value_rect)
        else:
            # Draw centered label
            label_rect = label_text.get_rect(center=element.rect.center)
            screen.blit(label_text, label_rect)

    def _draw_buttons(self, screen: pygame.Surface) -> None:
        """Draw all action buttons."""
        for button in self.buttons:
            self._draw_button(screen, button)

    # Callback methods for UI elements
    def _on_resolution_change(self) -> None:
        """Handle resolution change."""
        self.logger.debug("Resolution change requested")
        # Implementation would show resolution selection dialog

    def _on_fullscreen_toggle(self) -> None:
        """Handle fullscreen toggle."""
        config = config_manager.get_config()
        config.graphics.fullscreen = not config.graphics.fullscreen
        self.logger.info(f"Fullscreen toggled to {config.graphics.fullscreen}")

    def _on_quality_change(self) -> None:
        """Handle quality change."""
        self.logger.debug("Quality change requested")
        # Implementation would show quality selection dialog

    def _on_vsync_toggle(self) -> None:
        """Handle VSync toggle."""
        config = config_manager.get_config()
        config.graphics.vsync = not config.graphics.vsync
        self.logger.info(f"VSync toggled to {config.graphics.vsync}")

    def _on_master_volume_change(self) -> None:
        """Handle master volume change."""
        self.logger.debug("Master volume change requested")
        # Implementation would handle slider interaction

    def _on_music_volume_change(self) -> None:
        """Handle music volume change."""
        self.logger.debug("Music volume change requested")
        # Implementation would handle slider interaction

    def _on_sfx_volume_change(self) -> None:
        """Handle SFX volume change."""
        self.logger.debug("SFX volume change requested")
        # Implementation would handle slider interaction

    def _on_audio_enabled_toggle(self) -> None:
        """Handle audio enabled toggle."""
        config = config_manager.get_config()
        config.audio.enabled = not config.audio.enabled
        self.logger.info(f"Audio enabled toggled to {config.audio.enabled}")

    def _apply_settings(self) -> None:
        """Apply all settings changes."""
        # Save configuration
        config_manager.save_config()

        # Apply graphics settings
        graphics_manager.initialize_display()

        # Apply audio settings
        audio_manager.apply_volume_settings()

        self.logger.info("Settings applied")
        self.hide()

    def _reset_settings(self) -> None:
        """Reset all settings to defaults."""
        config_manager.reset_to_defaults()
        graphics_manager.reset_to_defaults()
        audio_manager.reset_to_defaults()

        # Reinitialize tab content with new defaults
        self._initialize_tab_content()

        self.logger.info("Settings reset to defaults")
        self.needs_redraw = True

    def _close_settings(self) -> None:
        """Close settings without applying changes."""
        self.hide()

    # Save management callbacks
    def _on_save_file_select(self) -> None:
        """Handle save file selection."""
        self.logger.debug("Save file selection requested")
        # Implementation would show file selection dialog

    def _on_create_backup(self) -> None:
        """Handle backup creation."""
        from core.save_protection import SaveProtectionManager

        save_manager = SaveProtectionManager()

        # Create backup of current save
        success = save_manager.create_backup("current_save.json", "manual")
        if success:
            self.logger.info("Backup created successfully")
        else:
            self.logger.error("Failed to create backup")

    def _on_export_save(self) -> None:
        """Handle save export."""
        self.logger.debug("Save export requested")
        # Implementation would show file dialog for export location

    def _on_import_save(self) -> None:
        """Handle save import."""
        self.logger.debug("Save import requested")
        # Implementation would show file dialog for import selection

    def _on_delete_save(self) -> None:
        """Handle save deletion."""
        self.logger.debug("Save deletion requested")
        # Implementation would show confirmation dialog

    def _on_autosave_change(self) -> None:
        """Handle auto-save interval change."""
        self.logger.debug("Auto-save interval change requested")
        # Implementation would handle slider interaction

    # Controls callbacks
    def _on_mouse_sensitivity_change(self) -> None:
        """Handle mouse sensitivity change."""
        self.logger.debug("Mouse sensitivity change requested")
        # Implementation would handle slider interaction

    def _on_invert_mouse_y_change(self) -> None:
        """Handle invert mouse Y toggle."""
        config = config_manager.get_config()
        config.controls.invert_mouse_y = not config.controls.invert_mouse_y
        self.logger.info(f"Invert mouse Y toggled to {config.controls.invert_mouse_y}")

    def _on_key_binding_change(self) -> None:
        """Handle key binding change."""
        self.logger.debug("Key binding change requested")
        # Implementation would show key capture dialog

    # Difficulty callbacks
    def _on_difficulty_change(self) -> None:
        """Handle difficulty level change."""
        self.logger.debug("Difficulty level change requested")
        # Implementation would show difficulty selection dialog

    def _on_autosave_toggle(self) -> None:
        """Handle auto-save toggle."""
        config = config_manager.get_config()
        config.difficulty.auto_save = not config.difficulty.auto_save
        self.logger.info(f"Auto-save toggled to {config.difficulty.auto_save}")

    def _on_tutorials_toggle(self) -> None:
        """Handle tutorials toggle."""
        config = config_manager.get_config()
        config.difficulty.show_tutorials = not config.difficulty.show_tutorials
        self.logger.info(
            f"Show tutorials toggled to {config.difficulty.show_tutorials}"
        )

    def _on_confirm_actions_toggle(self) -> None:
        """Handle confirm actions toggle."""
        config = config_manager.get_config()
        config.difficulty.confirm_actions = not config.difficulty.confirm_actions
        self.logger.info(
            f"Confirm actions toggled to {config.difficulty.confirm_actions}"
        )

    # Accessibility callbacks
    def _on_colorblind_mode_change(self) -> None:
        """Handle colorblind mode change."""
        self.logger.debug("Colorblind mode change requested")
        # Implementation would show colorblind mode selection dialog

    def _on_high_contrast_toggle(self) -> None:
        """Handle high contrast toggle."""
        config = config_manager.get_config()
        config.accessibility.high_contrast = not config.accessibility.high_contrast
        self.logger.info(
            f"High contrast toggled to {config.accessibility.high_contrast}"
        )

    def _on_large_text_toggle(self) -> None:
        """Handle large text toggle."""
        config = config_manager.get_config()
        config.accessibility.large_text = not config.accessibility.large_text
        self.logger.info(f"Large text toggled to {config.accessibility.large_text}")

    def _on_reduced_motion_toggle(self) -> None:
        """Handle reduced motion toggle."""
        config = config_manager.get_config()
        config.accessibility.reduced_motion = not config.accessibility.reduced_motion
        self.logger.info(
            f"Reduced motion toggled to {config.accessibility.reduced_motion}"
        )
