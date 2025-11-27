"""Settings Panel - Thorpy Implementation

Migrated from ImGui to Thorpy for simpler, lightweight UI.
Demonstrates data binding integration and clean architecture.
"""

import thorpy
import pygame
from typing import Dict, Any, Optional, List
from .base_panel import BasePanel, PanelStyle, PanelState
from ..data_binding import DataBindingManager, BindingDirection
from game.game_state_interface import TurboShellsGameStateInterface


class SettingsPanel(BasePanel):
    """Settings interface with Thorpy integration.
    
    This panel demonstrates:
    - Simple, non-draggable UI
    - Two-way data binding
    - Reactive UI updates
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
        self.size = (500, 600)
        self.position = (100, 50)
        
        # Settings data (simplified for Thorpy demo)
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
        
        self._changed_settings = set()
        
        # Re-create element with specific content
        self._create_settings_ui()
        
    def _create_element(self) -> None:
        """Override base creation to do nothing initially, we call _create_settings_ui later."""
        pass

    def _create_settings_ui(self) -> None:
        """Create the Thorpy UI elements for settings."""
        
        # Container for all settings
        elements = []
        
        # Title
        title = thorpy.make_text("Game Settings", font_size=20, font_color=(255, 255, 255))
        elements.append(title)
        
        # Graphics Section
        elements.append(thorpy.make_text("Graphics", font_size=16, font_color=(200, 200, 255)))
        
        # Fullscreen
        self.chk_fullscreen = thorpy.Toggler("Fullscreen")
        self.chk_fullscreen.active = self.settings_data["graphics"]["fullscreen"]
        elements.append(self.chk_fullscreen)
        
        # VSync
        self.chk_vsync = thorpy.Toggler("VSync")
        self.chk_vsync.active = self.settings_data["graphics"]["vsync"]
        elements.append(self.chk_vsync)
        
        # FPS Limit
        self.slider_fps = thorpy.SliderX(100, (30, 144), "FPS Limit", type_=int, initial_value=self.settings_data["graphics"]["fps_limit"])
        elements.append(self.slider_fps)
        
        # Audio Section
        elements.append(thorpy.make_text("Audio", font_size=16, font_color=(200, 200, 255)))
        
        # Master Volume
        self.slider_master = thorpy.SliderX(100, (0.0, 1.0), "Master Vol", initial_value=self.settings_data["audio"]["master_volume"])
        elements.append(self.slider_master)
        
        # Gameplay Section
        elements.append(thorpy.make_text("Gameplay", font_size=16, font_color=(200, 200, 255)))
        
        # Race Speed
        self.slider_speed = thorpy.SliderX(100, (0.5, 3.0), "Race Speed", initial_value=self.settings_data["gameplay"]["race_speed"])
        elements.append(self.slider_speed)
        
        # Buttons
        btn_apply = thorpy.make_button("Apply Changes", func=self._apply_settings)
        btn_close = thorpy.make_button("Close", func=self.hide)
        
        button_box = thorpy.Box(children=[btn_apply, btn_close])
        button_box.set_bck_color((0,0,0,0))
        elements.append(button_box)
        
        # Main Box
        self.element = thorpy.Box(children=elements)
        self.element.set_size(self.size)
        self.element.set_topleft(self.position)
        self.element.set_bck_color((40, 40, 50, 230))
        
    def _apply_settings(self) -> None:
        """Apply settings from UI elements."""
        print("Applying settings...")
        
        # Graphics
        self.settings_data["graphics"]["fullscreen"] = self.chk_fullscreen.active
        self.settings_data["graphics"]["vsync"] = self.chk_vsync.active
        self.settings_data["graphics"]["fps_limit"] = self.slider_fps.get_value()
        
        # Audio
        self.settings_data["audio"]["master_volume"] = self.slider_master.get_value()
        
        # Gameplay
        self.settings_data["gameplay"]["race_speed"] = self.slider_speed.get_value()
        
        # Apply to game state
        self.game_state.set('race_speed_multiplier', self.settings_data["gameplay"]["race_speed"])
        
        print("Settings applied!")
        
    def update(self, game_state: Any) -> None:
        """Update panel state."""
        pass
