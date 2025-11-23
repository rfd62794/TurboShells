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
    DIFFICULTY = "difficulty"
    PROFILE = "profile"
    APPEARANCE = "appearance"
    ACCESSIBILITY = "accessibility"
    SAVES = "saves"
    PRIVACY = "privacy"


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
        'background': (40, 40, 40),
        'panel': (60, 60, 60),
        'border': (100, 100, 100),
        'text': (255, 255, 255),
        'text_disabled': (150, 150, 150),
        'button': (80, 80, 80),
        'button_hover': (100, 100, 100),
        'button_active': (120, 120, 120),
        'tab': (70, 70, 70),
        'tab_active': (90, 90, 90),
        'accent': (100, 150, 200),
        'slider_track': (50, 50, 50),
        'slider_handle': (120, 120, 120),
        'checkbox': (80, 80, 80),
        'checkbox_checked': (100, 150, 200)
    }
    
    # Fonts
    FONT_SIZES = {
        'title': 24,
        'tab': 16,
        'label': 14,
        'value': 14,
        'tooltip': 12
    }
    
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
        
        # Layout dimensions
        self.panel_rect = pygame.Rect(
            screen_rect.width // 4,
            screen_rect.height // 8,
            screen_rect.width // 2,
            screen_rect.height * 3 // 4
        )
        
        self.tab_bar_rect = pygame.Rect(
            self.panel_rect.x + 10,
            self.panel_rect.y + 10,
            self.panel_rect.width - 20,
            40
        )
        
        self.content_rect = pygame.Rect(
            self.panel_rect.x + 10,
            self.tab_bar_rect.bottom + 10,
            self.panel_rect.width - 20,
            self.panel_rect.height - self.tab_bar_rect.height - 60
        )
        
        # Initialize UI elements
        self._initialize_tabs()
        self._initialize_buttons()
        self._initialize_tab_content()
        
        self.logger.info("Settings view initialized")
    
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
        tab_width = 100
        tab_height = 35
        tab_spacing = 5
        
        tab_configs = [
            (SettingsTab.GRAPHICS, "Graphics"),
            (SettingsTab.AUDIO, "Audio"),
            (SettingsTab.CONTROLS, "Controls"),
            (SettingsTab.DIFFICULTY, "Difficulty"),
            (SettingsTab.PROFILE, "Profile"),
            (SettingsTab.APPEARANCE, "Appearance"),
            (SettingsTab.ACCESSIBILITY, "Accessibility"),
            (SettingsTab.SAVES, "Saves"),
            (SettingsTab.PRIVACY, "Privacy")
        ]
        
        for i, (tab, label) in enumerate(tab_configs):
            x = self.tab_bar_rect.x + i * (tab_width + tab_spacing)
            y = self.tab_bar_rect.y
            
            rect = pygame.Rect(x, y, tab_width, tab_height)
            
            self.tabs[tab] = UIElement(
                rect=rect,
                element_type="tab",
                label=label,
                value=tab,
                callback=lambda t=tab: self._switch_tab(t)
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
            button_height
        )
        
        self.buttons.append(UIElement(
            rect=apply_rect,
            element_type="button",
            label="Apply",
            value="apply",
            callback=self._apply_settings
        ))
        
        # Reset button
        reset_rect = pygame.Rect(
            self.panel_rect.right - button_width - button_spacing,
            self.panel_rect.bottom - button_height - 10,
            button_width,
            button_height
        )
        
        self.buttons.append(UIElement(
            rect=reset_rect,
            element_type="button",
            label="Reset",
            value="reset",
            callback=self._reset_settings
        ))
        
        # Close button
        close_rect = pygame.Rect(
            self.panel_rect.right - button_width,
            self.panel_rect.top + 5,
            button_width,
            25
        )
        
        self.buttons.append(UIElement(
            rect=close_rect,
            element_type="button",
            label="X",
            value="close",
            callback=self._close_settings
        ))
    
    def _initialize_tab_content(self) -> None:
        """Initialize content for each tab."""
        # Graphics tab content
        self._initialize_graphics_tab()
        
        # Audio tab content
        self._initialize_audio_tab()
        
        # Other tabs will be initialized as needed
        self.tab_content[SettingsTab.CONTROLS] = []
        self.tab_content[SettingsTab.DIFFICULTY] = []
        self.tab_content[SettingsTab.PROFILE] = []
        self.tab_content[SettingsTab.APPEARANCE] = []
        self.tab_content[SettingsTab.ACCESSIBILITY] = []
        self.tab_content[SettingsTab.SAVES] = []
        self.tab_content[SettingsTab.PRIVACY] = []
    
    def _initialize_graphics_tab(self) -> None:
        """Initialize graphics settings tab content."""
        content = []
        y_offset = self.content_rect.y + 20
        line_height = 35
        
        config = config_manager.get_config()
        
        # Resolution dropdown
        resolution_rect = pygame.Rect(
            self.content_rect.x + 20,
            y_offset,
            200,
            25
        )
        
        current_resolution = f"{config.graphics.resolution_width}x{config.graphics.resolution_height}"
        content.append(UIElement(
            rect=resolution_rect,
            element_type="dropdown",
            label="Resolution:",
            value=current_resolution,
            callback=self._on_resolution_change,
            tooltip="Select screen resolution"
        ))
        
        y_offset += line_height
        
        # Fullscreen checkbox
        fullscreen_rect = pygame.Rect(
            self.content_rect.x + 20,
            y_offset,
            20,
            20
        )
        
        content.append(UIElement(
            rect=fullscreen_rect,
            element_type="checkbox",
            label="Fullscreen",
            value=config.graphics.fullscreen,
            callback=self._on_fullscreen_toggle,
            tooltip="Toggle fullscreen mode"
        ))
        
        y_offset += line_height
        
        # Quality dropdown
        quality_rect = pygame.Rect(
            self.content_rect.x + 20,
            y_offset,
            150,
            25
        )
        
        content.append(UIElement(
            rect=quality_rect,
            element_type="dropdown",
            label="Quality:",
            value=config.graphics.quality_level,
            callback=self._on_quality_change,
            tooltip="Select graphics quality"
        ))
        
        y_offset += line_height
        
        # VSync checkbox
        vsync_rect = pygame.Rect(
            self.content_rect.x + 20,
            y_offset,
            20,
            20
        )
        
        content.append(UIElement(
            rect=vsync_rect,
            element_type="checkbox",
            label="VSync",
            value=config.graphics.vsync,
            callback=self._on_vsync_toggle,
            tooltip="Enable vertical sync"
        ))
        
        self.tab_content[SettingsTab.GRAPHICS] = content
    
    def _initialize_audio_tab(self) -> None:
        """Initialize audio settings tab content."""
        content = []
        y_offset = self.content_rect.y + 20
        line_height = 40
        
        config = config_manager.get_config()
        
        # Master volume slider
        master_volume_rect = pygame.Rect(
            self.content_rect.x + 20,
            y_offset,
            200,
            20
        )
        
        content.append(UIElement(
            rect=master_volume_rect,
            element_type="slider",
            label="Master Volume",
            value=config.audio.master_volume,
            callback=self._on_master_volume_change,
            tooltip="Adjust master volume"
        ))
        
        y_offset += line_height
        
        # Music volume slider
        music_volume_rect = pygame.Rect(
            self.content_rect.x + 20,
            y_offset,
            200,
            20
        )
        
        content.append(UIElement(
            rect=music_volume_rect,
            element_type="slider",
            label="Music Volume",
            value=config.audio.music_volume,
            callback=self._on_music_volume_change,
            tooltip="Adjust music volume"
        ))
        
        y_offset += line_height
        
        # SFX volume slider
        sfx_volume_rect = pygame.Rect(
            self.content_rect.x + 20,
            y_offset,
            200,
            20
        )
        
        content.append(UIElement(
            rect=sfx_volume_rect,
            element_type="slider",
            label="SFX Volume",
            value=config.audio.sfx_volume,
            callback=self._on_sfx_volume_change,
            tooltip="Adjust sound effects volume"
        ))
        
        y_offset += line_height
        
        # Audio enabled checkbox
        audio_enabled_rect = pygame.Rect(
            self.content_rect.x + 20,
            y_offset,
            20,
            20
        )
        
        content.append(UIElement(
            rect=audio_enabled_rect,
            element_type="checkbox",
            label="Enable Audio",
            value=config.audio.enabled,
            callback=self._on_audio_enabled_toggle,
            tooltip="Enable/disable all audio"
        ))
        
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
        pygame.draw.rect(screen, self.COLORS['panel'], self.panel_rect)
        pygame.draw.rect(screen, self.COLORS['border'], self.panel_rect, 2)
        
        # Draw title
        title_text = self.fonts['title'].render("Settings", True, self.COLORS['text'])
        title_rect = title_text.get_rect(
            centerx=self.panel_rect.centerx,
            y=self.panel_rect.y + 5
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
                color = self.COLORS['tab_active']
            else:
                color = self.COLORS['tab']
            
            # Draw tab background
            pygame.draw.rect(screen, color, element.rect)
            pygame.draw.rect(screen, self.COLORS['border'], element.rect, 1)
            
            # Draw tab label
            label_color = self.COLORS['text'] if tab == self.active_tab else self.COLORS['text']
            label_text = self.fonts['tab'].render(element.label, True, label_color)
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
    
    def _draw_dropdown(self, screen: pygame.Surface, element: UIElement) -> None:
        """Draw a dropdown element."""
        # Draw dropdown background
        pygame.draw.rect(screen, self.COLORS['button'], element.rect)
        pygame.draw.rect(screen, self.COLORS['border'], element.rect, 1)
        
        # Draw label
        label_text = self.fonts['label'].render(element.label, True, self.COLORS['text'])
        label_rect = label_text.get_rect(
            right=element.rect.left - 10,
            centery=element.rect.centery
        )
        screen.blit(label_text, label_rect)
        
        # Draw value
        value_text = self.fonts['value'].render(str(element.value), True, self.COLORS['text'])
        value_rect = value_text.get_rect(
            left=element.rect.left + 5,
            centery=element.rect.centery
        )
        screen.blit(value_text, value_rect)
        
        # Draw dropdown arrow
        arrow_points = [
            (element.rect.right - 15, element.rect.centery - 5),
            (element.rect.right - 5, element.rect.centery - 5),
            (element.rect.right - 10, element.rect.centery + 5)
        ]
        pygame.draw.polygon(screen, self.COLORS['text'], arrow_points)
    
    def _draw_checkbox(self, screen: pygame.Surface, element: UIElement) -> None:
        """Draw a checkbox element."""
        # Draw checkbox
        color = self.COLORS['checkbox_checked'] if element.value else self.COLORS['checkbox']
        pygame.draw.rect(screen, color, element.rect)
        pygame.draw.rect(screen, self.COLORS['border'], element.rect, 2)
        
        # Draw checkmark if checked
        if element.value:
            check_points = [
                (element.rect.left + 3, element.rect.centery),
                (element.rect.left + 8, element.rect.bottom - 3),
                (element.rect.right - 3, element.rect.top + 3)
            ]
            pygame.draw.lines(screen, self.COLORS['text'], False, check_points, 2)
        
        # Draw label
        label_text = self.fonts['label'].render(element.label, True, self.COLORS['text'])
        label_rect = label_text.get_rect(
            left=element.rect.right + 10,
            centery=element.rect.centery
        )
        screen.blit(label_text, label_rect)
    
    def _draw_slider(self, screen: pygame.Surface, element: UIElement) -> None:
        """Draw a slider element."""
        # Draw label
        label_text = self.fonts['label'].render(element.label, True, self.COLORS['text'])
        label_rect = label_text.get_rect(
            left=element.rect.left,
            top=element.rect.top - 20
        )
        screen.blit(label_text, label_rect)
        
        # Draw track
        track_rect = pygame.Rect(element.rect.x, element.rect.centery - 2, element.rect.width, 4)
        pygame.draw.rect(screen, self.COLORS['slider_track'], track_rect)
        
        # Draw handle
        handle_x = element.rect.x + int(element.value * element.rect.width)
        handle_rect = pygame.Rect(handle_x - 8, element.rect.centery - 8, 16, 16)
        pygame.draw.rect(screen, self.COLORS['slider_handle'], handle_rect)
        pygame.draw.rect(screen, self.COLORS['border'], handle_rect, 1)
        
        # Draw value
        value_text = self.fonts['value'].render(f"{int(element.value * 100)}%", True, self.COLORS['text'])
        value_rect = value_text.get_rect(
            left=element.rect.right + 10,
            centery=element.rect.centery
        )
        screen.blit(value_text, value_rect)
    
    def _draw_button(self, screen: pygame.Surface, element: UIElement) -> None:
        """Draw a button element."""
        # Determine button color based on hover state
        mouse_pos = pygame.mouse.get_pos()
        if element.rect.collidepoint(mouse_pos):
            color = self.COLORS['button_hover']
        else:
            color = self.COLORS['button']
        
        # Draw button background
        pygame.draw.rect(screen, color, element.rect)
        pygame.draw.rect(screen, self.COLORS['border'], element.rect, 1)
        
        # Draw button label
        label_text = self.fonts['label'].render(element.label, True, self.COLORS['text'])
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
