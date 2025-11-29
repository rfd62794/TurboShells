"""
Settings View using SRP-compliant components.

Demonstrates the new architecture by integrating TabManager, UIRenderer, 
EventHandler, and LayoutManager components.
"""

import pygame
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass

from audio.audio_manager import audio_manager
from graphics.graphics_manager import graphics_manager
from core.logging_config import get_logger
from core.config import config_manager

from ui.components.tab_manager import TabManager, SettingsTab, TabConfig
from ui.components.ui_renderer import UIRenderer, UIElement, StyleManager
from ui.components.event_handler import EventHandler
from ui.components.layout_manager import LayoutManager


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
    Settings view using SRP-compliant component architecture.
    
    This class now acts as a coordinator, delegating responsibilities
    to specialized components while maintaining the public interface.
    """
    
    def __init__(self, screen_rect: pygame.Rect):
        """
        Initialize settings view.
        
        Args:
            screen_rect: Screen rectangle for positioning
        """
        self.logger = get_logger(__name__)
        self.screen_rect = screen_rect
        
        # Initialize SRP components
        self.layout_manager = LayoutManager(screen_rect)
        self.tab_manager = TabManager(self.layout_manager.get_tab_bar_rect())
        self.ui_renderer = UIRenderer()
        self.event_handler = EventHandler(self.tab_manager)
        
        # View state
        self.visible: bool = False
        self.needs_redraw: bool = True
        
        # UI elements
        self.tab_content: Dict[SettingsTab, List[UIElement]] = {}
        self.action_buttons: List[UIElement] = []
        
        # Initialize content
        self._initialize_tab_content()
        self._initialize_action_buttons()
        self._setup_event_callbacks()
        
        # Configure event handler
        self.event_handler.set_action_buttons(self.action_buttons)
        for tab_id, elements in self.tab_content.items():
            self.event_handler.set_ui_elements(tab_id, elements)
        
        self.logger.info("Refactored settings view initialized")
    
    def _initialize_tab_content(self) -> None:
        """Initialize content for each tab using layout manager."""
        # Graphics tab content
        self._create_graphics_tab()
        
        # Audio tab content
        self._create_audio_tab()
        
        # Controls tab content
        self._create_controls_tab()
        
        # Gameplay tab content
        self._create_gameplay_tab()
        
        # System tab content
        self._create_system_tab()
        
        # Other tabs (placeholder)
        self.tab_content[SettingsTab.PROFILE] = []
        self.tab_content[SettingsTab.APPEARANCE] = []
    
    def _create_graphics_tab(self) -> None:
        """Create graphics settings tab content."""
        content = []
        content_rect = self.layout_manager.get_content_rect()
        
        # Define elements with layout information
        elements_config = [
            {'element_type': 'dropdown', 'label': 'Resolution:', 'height': 25, 'width': 200},
            {'element_type': 'checkbox', 'label': 'Fullscreen', 'height': 20, 'width': 20},
            {'element_type': 'dropdown', 'label': 'Quality:', 'height': 25, 'width': 150},
            {'element_type': 'checkbox', 'label': 'VSync', 'height': 20, 'width': 20},
        ]
        
        # Calculate positions using layout manager
        positions = self.layout_manager.calculate_element_positions(elements_config, content_rect)
        
        # Create UI elements
        config = config_manager.get_config()
        current_resolution = f"{config.graphics.resolution_width}x{config.graphics.resolution_height}"
        
        for i, (element_config, position) in enumerate(zip(elements_config, positions)):
            element = UIElement(
                rect=position,
                element_type=element_config['element_type'],
                label=element_config['label'],
                value=self._get_graphics_value(element_config['label'], config),
                callback=self._create_graphics_callback(element_config['label']),
                tooltip=f"Configure {element_config['label'].lower()}"
            )
            content.append(element)
        
        self.tab_content[SettingsTab.GRAPHICS] = content
    
    def _create_audio_tab(self) -> None:
        """Create audio settings tab content."""
        content = []
        content_rect = self.layout_manager.get_content_rect()
        
        elements_config = [
            {'element_type': 'slider', 'label': 'Master Volume', 'height': 20, 'width': 200},
            {'element_type': 'slider', 'label': 'Music Volume', 'height': 20, 'width': 200},
            {'element_type': 'slider', 'label': 'SFX Volume', 'height': 20, 'width': 200},
            {'element_type': 'checkbox', 'label': 'Enable Audio', 'height': 20, 'width': 20},
        ]
        
        positions = self.layout_manager.calculate_element_positions(elements_config, content_rect)
        config = config_manager.get_config()
        
        for element_config, position in zip(elements_config, positions):
            element = UIElement(
                rect=position,
                element_type=element_config['element_type'],
                label=element_config['label'],
                value=self._get_audio_value(element_config['label'], config),
                callback=self._create_audio_callback(element_config['label']),
                tooltip=f"Adjust {element_config['label'].lower()}"
            )
            content.append(element)
        
        self.tab_content[SettingsTab.AUDIO] = content
    
    def _create_controls_tab(self) -> None:
        """Create controls settings tab content."""
        content = []
        content_rect = self.layout_manager.get_content_rect()
        
        elements_config = [
            {'element_type': 'slider', 'label': 'Mouse Sensitivity:', 'height': 20, 'width': 200},
            {'element_type': 'checkbox', 'label': 'Invert Mouse Y', 'height': 20, 'width': 20},
        ]
        
        positions = self.layout_manager.calculate_element_positions(elements_config, content_rect)
        config = config_manager.get_config()
        
        for element_config, position in zip(elements_config, positions):
            element = UIElement(
                rect=position,
                element_type=element_config['element_type'],
                label=element_config['label'],
                value=self._get_controls_value(element_config['label'], config),
                callback=self._create_controls_callback(element_config['label']),
                tooltip=f"Configure {element_config['label'].lower()}"
            )
            content.append(element)
        
        # Add key bindings section
        key_bindings_label = UIElement(
            rect=pygame.Rect(content_rect.x + 20, positions[-1].bottom + 20, content_rect.width - 40, 30),
            element_type='label',
            label='Key Bindings:',
            value='',
            tooltip='Configure keyboard controls'
        )
        content.append(key_bindings_label)
        
        self.tab_content[SettingsTab.CONTROLS] = content
    
    def _create_gameplay_tab(self) -> None:
        """Create gameplay settings tab content."""
        content = []
        content_rect = self.layout_manager.get_content_rect()
        
        elements_config = [
            {'element_type': 'dropdown', 'label': 'Difficulty Level:', 'height': 25, 'width': 200},
            {'element_type': 'checkbox', 'label': 'Auto-save', 'height': 20, 'width': 20},
            {'element_type': 'checkbox', 'label': 'Show Tutorials', 'height': 20, 'width': 20},
            {'element_type': 'checkbox', 'label': 'Confirm Actions', 'height': 20, 'width': 20},
        ]
        
        positions = self.layout_manager.calculate_element_positions(elements_config, content_rect)
        config = config_manager.get_config()
        
        for element_config, position in zip(elements_config, positions):
            element = UIElement(
                rect=position,
                element_type=element_config['element_type'],
                label=element_config['label'],
                value=self._get_gameplay_value(element_config['label'], config),
                callback=self._create_gameplay_callback(element_config['label']),
                tooltip=f"Configure {element_config['label'].lower()}"
            )
            content.append(element)
        
        self.tab_content[SettingsTab.GAMEPLAY] = content
    
    def _create_system_tab(self) -> None:
        """Create system settings tab content."""
        content = []
        content_rect = self.layout_manager.get_content_rect()
        
        elements_config = [
            {'element_type': 'list', 'label': 'Save Files:', 'height': 200, 'width': 300},
            {'element_type': 'button', 'label': 'Create Backup', 'height': 30, 'width': 100},
            {'element_type': 'button', 'label': 'Export', 'height': 30, 'width': 100},
            {'element_type': 'button', 'label': 'Import', 'height': 30, 'width': 100},
            {'element_type': 'button', 'label': 'Delete', 'height': 30, 'width': 100},
            {'element_type': 'slider', 'label': 'Auto-save Interval (minutes):', 'height': 20, 'width': 200},
            {'element_type': 'checkbox', 'label': 'Share Analytics', 'height': 20, 'width': 20},
            {'element_type': 'checkbox', 'label': 'Send Crash Reports', 'height': 20, 'width': 20},
            {'element_type': 'checkbox', 'label': 'Performance Data', 'height': 20, 'width': 20},
        ]
        
        # Use horizontal layout for first row of buttons
        button_positions = self.layout_manager.calculate_horizontal_layout(
            elements_config[1:4], content_rect
        )
        
        # Use vertical layout for remaining elements
        remaining_elements = [elements_config[0]] + elements_config[4:]
        remaining_positions = self.layout_manager.calculate_vertical_layout(
            remaining_elements, content_rect
        )
        
        # Combine positions
        all_positions = [remaining_positions[0]] + button_positions + remaining_positions[1:]
        
        config = config_manager.get_config()
        
        for element_config, position in zip(elements_config, all_positions):
            element = UIElement(
                rect=position,
                element_type=element_config['element_type'],
                label=element_config['label'],
                value=self._get_system_value(element_config['label'], config),
                callback=self._create_system_callback(element_config['label']),
                tooltip=f"Configure {element_config['label'].lower()}"
            )
            content.append(element)
        
        self.tab_content[SettingsTab.SYSTEM] = content
    
    def _initialize_action_buttons(self) -> None:
        """Initialize action buttons using layout manager."""
        panel_rect = self.layout_manager.get_panel_rect()
        
        # Calculate button positions
        button_positions = self.layout_manager.calculate_button_positions(
            3, (80, 30), panel_rect, "right"
        )
        
        # Create buttons
        self.action_buttons = [
            UIElement(
                rect=button_positions[0],
                element_type='button',
                label='Apply',
                value='apply',
                callback=self._apply_settings,
                tooltip='Apply all settings changes'
            ),
            UIElement(
                rect=button_positions[1],
                element_type='button',
                label='Reset',
                value='reset',
                callback=self._reset_settings,
                tooltip='Reset all settings to defaults'
            ),
            UIElement(
                rect=button_positions[2],
                element_type='button',
                label='X',
                value='close',
                callback=self._close_settings,
                tooltip='Close settings without applying'
            )
        ]
    
    def _setup_event_callbacks(self) -> None:
        """Setup event handler callbacks."""
        # Tab change callback
        self.event_handler.add_tab_change_callback(self._on_tab_change)
        
        # Escape key callback
        self.event_handler.add_element_callback("escape", self._close_settings)
    
    # Value getter methods
    def _get_graphics_value(self, label: str, config) -> Any:
        """Get graphics setting value."""
        if label == 'Resolution:':
            return f"{config.graphics.resolution_width}x{config.graphics.resolution_height}"
        elif label == 'Fullscreen':
            return config.graphics.fullscreen
        elif label == 'Quality:':
            return config.graphics.quality_level
        elif label == 'VSync':
            return config.graphics.vsync
        return None
    
    def _get_audio_value(self, label: str, config) -> Any:
        """Get audio setting value."""
        if label == 'Master Volume':
            return config.audio.master_volume
        elif label == 'Music Volume':
            return config.audio.music_volume
        elif label == 'SFX Volume':
            return config.audio.sfx_volume
        elif label == 'Enable Audio':
            return config.audio.enabled
        return None
    
    def _get_controls_value(self, label: str, config) -> Any:
        """Get controls setting value."""
        if label == 'Mouse Sensitivity:':
            return config.controls.mouse_sensitivity
        elif label == 'Invert Mouse Y':
            return config.controls.invert_mouse_y
        return None
    
    def _get_gameplay_value(self, label: str, config) -> Any:
        """Get gameplay setting value."""
        if label == 'Difficulty Level:':
            return config.difficulty.difficulty_level
        elif label == 'Auto-save':
            return config.difficulty.auto_save
        elif label == 'Show Tutorials':
            return config.difficulty.show_tutorials
        elif label == 'Confirm Actions':
            return config.difficulty.confirm_actions
        return None
    
    def _get_system_value(self, label: str, config) -> Any:
        """Get system setting value."""
        if label == 'Save Files:':
            return "save_list"
        elif label == 'Auto-save Interval (minutes):':
            return config.controls.auto_save_interval / 60
        elif label == 'Share Analytics':
            return True  # Default value
        elif label == 'Send Crash Reports':
            return True  # Default value
        elif label == 'Performance Data':
            return False  # Default value
        return None
    
    # Callback creation methods
    def _create_graphics_callback(self, label: str) -> Callable:
        """Create graphics setting callback."""
        if label == 'Fullscreen':
            return self._on_fullscreen_toggle
        elif label == 'VSync':
            return self._on_vsync_toggle
        else:
            return lambda: self.logger.debug(f"Graphics setting {label} changed")
    
    def _create_audio_callback(self, label: str) -> Callable:
        """Create audio setting callback."""
        if label == 'Enable Audio':
            return self._on_audio_enabled_toggle
        else:
            return lambda: self.logger.debug(f"Audio setting {label} changed")
    
    def _create_controls_callback(self, label: str) -> Callable:
        """Create controls setting callback."""
        if label == 'Invert Mouse Y':
            return self._on_invert_mouse_y_change
        else:
            return lambda: self.logger.debug(f"Controls setting {label} changed")
    
    def _create_gameplay_callback(self, label: str) -> Callable:
        """Create gameplay setting callback."""
        if label == 'Auto-save':
            return self._on_autosave_toggle
        elif label == 'Show Tutorials':
            return self._on_tutorials_toggle
        elif label == 'Confirm Actions':
            return self._on_confirm_actions_toggle
        else:
            return lambda: self.logger.debug(f"Gameplay setting {label} changed")
    
    def _create_system_callback(self, label: str) -> Callable:
        """Create system setting callback."""
        if label == 'Create Backup':
            return self._on_create_backup
        elif label == 'Export':
            return self._on_export_save
        elif label == 'Import':
            return self._on_import_save
        elif label == 'Delete':
            return self._on_delete_save
        else:
            return lambda: self.logger.debug(f"System setting {label} changed")
    
    # Event handlers
    def _on_tab_change(self, new_tab: SettingsTab) -> None:
        """Handle tab change event."""
        self.needs_redraw = True
        self.logger.debug(f"Tab changed to {new_tab.value}")
    
    def _on_fullscreen_toggle(self) -> None:
        """Handle fullscreen toggle."""
        config = config_manager.get_config()
        config.graphics.fullscreen = not config.graphics.fullscreen
        self.logger.info(f"Fullscreen toggled to {config.graphics.fullscreen}")
    
    def _on_vsync_toggle(self) -> None:
        """Handle VSync toggle."""
        config = config_manager.get_config()
        config.graphics.vsync = not config.graphics.vsync
        self.logger.info(f"VSync toggled to {config.graphics.vsync}")
    
    def _on_audio_enabled_toggle(self) -> None:
        """Handle audio enabled toggle."""
        config = config_manager.get_config()
        config.audio.enabled = not config.audio.enabled
        self.logger.info(f"Audio enabled toggled to {config.audio.enabled}")
    
    def _on_invert_mouse_y_change(self) -> None:
        """Handle invert mouse Y toggle."""
        config = config_manager.get_config()
        config.controls.invert_mouse_y = not config.controls.invert_mouse_y
        self.logger.info(f"Invert mouse Y toggled to {config.controls.invert_mouse_y}")
    
    def _on_autosave_toggle(self) -> None:
        """Handle auto-save toggle."""
        config = config_manager.get_config()
        config.difficulty.auto_save = not config.difficulty.auto_save
        self.logger.info(f"Auto-save toggled to {config.difficulty.auto_save}")
    
    def _on_tutorials_toggle(self) -> None:
        """Handle tutorials toggle."""
        config = config_manager.get_config()
        config.difficulty.show_tutorials = not config.difficulty.show_tutorials
        self.logger.info(f"Show tutorials toggled to {config.difficulty.show_tutorials}")
    
    def _on_confirm_actions_toggle(self) -> None:
        """Handle confirm actions toggle."""
        config = config_manager.get_config()
        config.difficulty.confirm_actions = not config.difficulty.confirm_actions
        self.logger.info(f"Confirm actions toggled to {config.difficulty.confirm_actions}")
    
    def _on_create_backup(self) -> None:
        """Handle backup creation."""
        from core.save_protection import SaveProtectionManager
        save_manager = SaveProtectionManager()
        success = save_manager.create_backup("current_save.json", "manual")
        if success:
            self.logger.info("Backup created successfully")
        else:
            self.logger.error("Failed to create backup")
    
    def _on_export_save(self) -> None:
        """Handle save export."""
        self.logger.debug("Save export requested")
    
    def _on_import_save(self) -> None:
        """Handle save import."""
        self.logger.debug("Save import requested")
    
    def _on_delete_save(self) -> None:
        """Handle save deletion."""
        self.logger.debug("Save deletion requested")
    
    def _apply_settings(self) -> None:
        """Apply all settings changes."""
        config_manager.save_config()
        graphics_manager.initialize_display()
        audio_manager.apply_volume_settings()
        self.logger.info("Settings applied")
        self.hide()
    
    def _reset_settings(self) -> None:
        """Reset all settings to defaults."""
        config_manager.reset_to_defaults()
        graphics_manager.reset_to_defaults()
        audio_manager.reset_to_defaults()
        self._initialize_tab_content()
        self.logger.info("Settings reset to defaults")
        self.needs_redraw = True
    
    def _close_settings(self) -> None:
        """Close settings without applying changes."""
        self.hide()
    
    # Public interface methods
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
        Handle pygame events using event handler.
        
        Args:
            event: Pygame event
            
        Returns:
            True if event was handled, False otherwise
        """
        if not self.visible:
            return False
        
        return self.event_handler.handle_event(event)
    
    def update(self, dt: float) -> None:
        """
        Update the settings view.
        
        Args:
            dt: Time delta since last update
        """
        if not self.visible:
            return
        
        # Update renderer with current mouse position
        mouse_pos = pygame.mouse.get_pos()
        self.ui_renderer.update_mouse_position(mouse_pos)
    
    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the settings view using renderer.
        
        Args:
            screen: Surface to draw on
        """
        if not self.visible:
            return
        
        # Draw main panel
        self.ui_renderer.draw_panel(screen, self.layout_manager.get_panel_rect(), "Settings")
        
        # Draw tabs
        self.ui_renderer.draw_tabs(screen, self.tab_manager)
        
        # Draw tab content
        current_tab = self.tab_manager.get_active_tab()
        content_elements = self.tab_content.get(current_tab, [])
        for element in content_elements:
            self.ui_renderer.draw_ui_element(screen, element)
        
        # Draw action buttons
        for button in self.action_buttons:
            self.ui_renderer.draw_ui_element(screen, button)
        
        # Draw tooltip if needed
        tooltip_text, tooltip_pos = self.event_handler.get_tooltip_info()
        if tooltip_text:
            self.ui_renderer.draw_tooltip(screen, tooltip_text, tooltip_pos)
    
    def update_layout(self, screen_rect: pygame.Rect) -> None:
        """
        Update layout for new screen dimensions.
        
        Args:
            screen_rect: New screen rectangle
        """
        self.screen_rect = screen_rect
        self.layout_manager.update_screen_size(screen_rect)
        
        # Update tab manager with new layout
        self.tab_manager.update_layout(self.layout_manager.get_tab_bar_rect())
        
        # Reinitialize content with new layout
        self._initialize_tab_content()
        self._initialize_action_buttons()
        
        # Update event handler
        self.event_handler.set_action_buttons(self.action_buttons)
        for tab_id, elements in self.tab_content.items():
            self.event_handler.set_ui_elements(tab_id, elements)
        
        self.needs_redraw = True
        self.logger.info(f"Settings layout updated to {screen_rect.width}x{screen_rect.height}")
    
    def get_component_info(self) -> Dict[str, Any]:
        """
        Get information about all components for debugging.
        
        Returns:
            Dictionary with component information
        """
        return {
            "layout_manager": self.layout_manager.get_layout_info(),
            "tab_manager": {
                "active_tab": self.tab_manager.get_active_tab().value,
                "tab_count": self.tab_manager.get_tab_count(),
                "enabled_tabs": self.tab_manager.get_enabled_tab_count()
            },
            "ui_elements": {
                "total_tabs": len(self.tab_content),
                "elements_per_tab": {tab.value: len(elements) for tab, elements in self.tab_content.items()},
                "action_buttons": len(self.action_buttons)
            }
        }
