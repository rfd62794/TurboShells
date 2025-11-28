#!/usr/bin/env python3
"""
Simple test to verify pygame_gui panel testing works with actual panel interfaces.
"""

import sys
import os
import pytest
import pygame
import pygame_gui
from unittest.mock import Mock

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from ui.panels.settings_panel import SettingsPanel
from ui.data_binding import DataBindingManager
from game.game_state_interface import TurboShellsGameStateInterface


class TestActualPanels:
    """Test suite for existing pygame_gui panels."""
    
    @pytest.fixture
    def pygame_setup(self):
        """Setup pygame for testing."""
        pygame.init()
        screen = pygame.display.set_mode((1024, 768))
        manager = pygame_gui.UIManager((1024, 768))
        yield screen, manager
        pygame.quit()
    
    @pytest.fixture
    def mock_game_state(self):
        """Create mock game state for testing."""
        class MockGame:
            def __init__(self):
                self.money = 1000
                self.resolution = (1024, 768)
                self.quality = "High"
                self.vsync = True
                self.master_volume = 0.8
                self.mouse_sensitivity = 0.5
                
            def get(self, key, default=None):
                return getattr(self, key, default)
                
            def set(self, key, value):
                setattr(self, key, value)
        
        return MockGame()
    
    def test_settings_panel_creation(self, pygame_setup, mock_game_state):
        """Test settings panel can be created and setup."""
        screen, manager = pygame_setup
        game_state_interface = TurboShellsGameStateInterface(mock_game_state)
        data_binding_manager = DataBindingManager()
        
        # Create panel
        panel = SettingsPanel(game_state_interface, data_binding_manager)
        
        # Verify panel creation
        assert panel is not None
        assert panel.panel_id == "settings"
        assert panel.title == "Game Settings"
        assert not panel.visible  # Initially hidden
        
        # Setup UI
        panel.setup_ui(manager)
        
        # Verify UI setup
        assert panel.manager == manager
        assert panel.window is None  # Window created on show
        
        # Show panel
        panel.show()
        
        # Verify panel shown
        assert panel.visible
        assert panel.window is not None
        assert panel.window.visible
        
        # Hide panel
        panel.hide()
        
        # Verify panel hidden
        assert not panel.visible
        assert not panel.window.visible
    
    def test_basic_event_handling(self, pygame_setup, mock_game_state):
        """Test basic event handling works."""
        screen, manager = pygame_setup
        game_state_interface = TurboShellsGameStateInterface(mock_game_state)
        data_binding_manager = DataBindingManager()
        
        panel = SettingsPanel(game_state_interface, data_binding_manager)
        panel.setup_ui(manager)
        panel.show()
        
        # Test event handling
        mouse_event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {'pos': (100, 100), 'button': 1}
        )
        
        result = panel.handle_event(mouse_event)
        assert isinstance(result, bool)
        
        # Test window close event
        close_event = pygame.event.Event(
            pygame_gui.UI_WINDOW_CLOSE,
            {'ui_element': panel.window}
        )
        
        result = panel.handle_event(close_event)
        assert isinstance(result, bool)
        # Panel might not hide immediately due to event processing


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
