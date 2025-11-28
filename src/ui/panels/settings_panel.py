"""Settings Panel - Pygame GUI Implementation

Migrated to pygame_gui for robust UI management.
"""

import pygame
import pygame_gui
from typing import Dict, Any, Optional, List
from .base_panel import BasePanel
from ..data_binding import DataBindingManager, BindingDirection
from game.game_state_interface import TurboShellsGameStateInterface


class SettingsPanel(BasePanel):
    """Settings interface with pygame_gui integration."""
    
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
        self.size = (500, 600)
        self.position = (100, 50)
        
        # UI Elements
        self.chk_fullscreen = None
        self.chk_vsync = None
        self.slider_fps = None
        self.slider_master = None
        self.slider_speed = None
        
        # Settings data
        self.settings_data = {
            "graphics": {
                "fullscreen": False,
                "vsync": True,
                "fps_limit": 60
            },
            "audio": {
                "master_volume": 0.8,
                "music_volume": 0.7,
                "sfx_volume": 0.9
            },
            "gameplay": {
                "race_speed": 1.0,
                "difficulty": "normal"
            }
        }
        
    def _create_window(self) -> None:
        """Create the settings window and elements."""
        super()._create_window()
        
        if not self.window:
            return
            
        container = self.window.get_container()
        width = self.size[0] - 40
        y_pos = 10
        
        # Graphics Section
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_pos), (width, 30)),
            text="Graphics",
            manager=self.manager,
            container=container
        )
        y_pos += 35
        
        # Fullscreen Toggle
        self.btn_fullscreen = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, y_pos), (150, 30)),
            text=f"Fullscreen: {'On' if self.settings_data['graphics']['fullscreen'] else 'Off'}",
            manager=self.manager,
            container=container
        )
        y_pos += 40
        
        # FPS Limit
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_pos), (100, 25)),
            text="FPS Limit:",
            manager=self.manager,
            container=container
        )
        self.slider_fps = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((120, y_pos), (200, 25)),
            start_value=self.settings_data['graphics']['fps_limit'],
            value_range=(30, 144),
            manager=self.manager,
            container=container
        )
        y_pos += 40
        
        # --- Audio ---
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_pos), (width, 25)),
            text="Audio",
            manager=self.manager,
            container=container
        )
        y_pos += 30
        
        # Master Volume
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_pos), (100, 25)),
            text="Master Vol:",
            manager=self.manager,
            container=container
        )
        self.slider_master = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((120, y_pos), (200, 25)),
            start_value=self.settings_data['audio']['master_volume'],
            value_range=(0.0, 1.0),
            manager=self.manager,
            container=container
        )
        y_pos += 40
        
        # --- Gameplay ---
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_pos), (width, 25)),
            text="Gameplay",
            manager=self.manager,
            container=container
        )
        y_pos += 30
        
        # Race Speed
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_pos), (100, 25)),
            text="Race Speed:",
            manager=self.manager,
            container=container
        )
        self.slider_speed = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((120, y_pos), (200, 25)),
            start_value=self.settings_data['gameplay']['race_speed'],
            value_range=(0.5, 3.0),
            manager=self.manager,
            container=container
        )
        y_pos += 50
        
        # Buttons
        self.btn_apply = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, y_pos), (120, 30)),
            text="Apply",
            manager=self.manager,
            container=container
        )
        
        self.btn_close = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((140, y_pos), (120, 30)),
            text="Close",
            manager=self.manager,
            container=container
        )

    def show(self) -> None:
        """Show the settings panel and hide main menu."""
        # Hide main menu first
        if hasattr(self.game_state.game, 'ui_manager'):
            ui_manager = self.game_state.game.ui_manager
            if hasattr(ui_manager, 'hide_panel'):
                ui_manager.hide_panel('main_menu')
        
        # Show settings panel
        super().show()

    def hide(self) -> None:
        """Hide the settings panel and restore main menu."""
        # Hide settings panel
        super().hide()
        
        # Show main menu again
        if hasattr(self.game_state.game, 'ui_manager'):
            ui_manager = self.game_state.game.ui_manager
            if hasattr(ui_manager, 'show_panel'):
                ui_manager.show_panel('main_menu')

    def update(self, time_delta: float) -> None:
        """Update panel logic."""
        super().update(time_delta)
        
        # Update fullscreen button text if setting changed
        if hasattr(self, 'btn_fullscreen') and self.btn_fullscreen:
            current_text = self.btn_fullscreen.text
            expected_text = f"Fullscreen: {'On' if self.settings_data['graphics']['fullscreen'] else 'Off'}"
            if current_text != expected_text:
                self.btn_fullscreen.set_text(expected_text)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle specific events."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_apply:
                self._apply_settings()
                return True
            elif event.ui_element == self.btn_close:
                self.hide()
                return True
            elif event.ui_element == getattr(self, 'btn_fullscreen', None):
                self.settings_data['graphics']['fullscreen'] = not self.settings_data['graphics']['fullscreen']
                self.btn_fullscreen.set_text(f"Fullscreen: {'On' if self.settings_data['graphics']['fullscreen'] else 'Off'}")
                return True
                
        return False

    def _apply_settings(self) -> None:
        """Apply settings from UI elements."""
        print("Applying settings...")
        
        # Update data from sliders
        if self.slider_fps:
            self.settings_data["graphics"]["fps_limit"] = int(self.slider_fps.get_current_value())
        if self.slider_master:
            self.settings_data["audio"]["master_volume"] = self.slider_master.get_current_value()
        if self.slider_speed:
            self.settings_data["gameplay"]["race_speed"] = self.slider_speed.get_current_value()
            
        # Apply to game state
        self.game_state.set('race_speed_multiplier', self.settings_data["gameplay"]["race_speed"])
        
        print("Settings applied!")

