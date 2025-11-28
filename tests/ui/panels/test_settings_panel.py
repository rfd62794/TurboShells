#!/usr/bin/env python3
"""
Comprehensive test suite for Settings Panel (pygame_gui version).

This test suite verifies:
1. Settings panel initialization and setup
2. Tab navigation and switching
3. Settings controls functionality (sliders, dropdowns, checkboxes)
4. Event handling and callbacks
5. Game state integration
6. UI Manager integration
"""

import sys
import os
import pytest
import pygame
import pygame_gui
from unittest.mock import Mock, patch, MagicMock

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from ui.panels.settings_panel import SettingsPanel
from game.game_state_interface import TurboShellsGameStateInterface
from ui.data_binding import DataBindingManager


class TestSettingsPanel:
    """Test suite for Settings Panel with pygame_gui."""
    
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
                # Graphics settings
                self.resolution = (1024, 768)
                self.quality = "High"
                self.vsync = True
                self.fullscreen = False
                
                # Audio settings
                self.master_volume = 0.8
                self.music_volume = 0.7
                self.sfx_volume = 0.9
                self.audio_enabled = True
                
                # Control settings
                self.mouse_sensitivity = 0.5
                self.invert_mouse_y = False
                
                # Gameplay settings
                self.difficulty = "Normal"
                self.auto_save = True
                self.show_tutorial = True
                
            def get(self, key, default=None):
                return getattr(self, key, default)
                
            def set(self, key, value):
                setattr(self, key, value)
                
            def get_settings_dict(self):
                return {
                    'resolution': self.resolution,
                    'quality': self.quality,
                    'vsync': self.vsync,
                    'fullscreen': self.fullscreen,
                    'master_volume': self.master_volume,
                    'music_volume': self.music_volume,
                    'sfx_volume': self.sfx_volume,
                    'audio_enabled': self.audio_enabled,
                    'mouse_sensitivity': self.mouse_sensitivity,
                    'invert_mouse_y': self.invert_mouse_y,
                    'difficulty': self.difficulty,
                    'auto_save': self.auto_save,
                    'show_tutorial': self.show_tutorial,
                }
        
        return MockGame()
    
    @pytest.fixture
    def settings_panel(self, pygame_setup, mock_game_state):
        """Create settings panel for testing."""
        screen, manager = pygame_setup
        game_state_interface = TurboShellsGameStateInterface(mock_game_state)
        data_binding = DataBindingManager()
        
        panel = SettingsPanel(game_state_interface, data_binding)
        panel.initialize(manager)
        
        return panel, manager, mock_game_state
    
    def test_settings_panel_initialization(self, settings_panel):
        """Test settings panel initialization."""
        panel, manager, game_state = settings_panel
        
        # Verify panel creation
        assert panel is not None
        assert hasattr(panel, 'window')
        assert hasattr(panel, 'tab_container')
        assert hasattr(panel, 'content_panels')
        
        # Verify game state integration
        assert panel.game_state_interface is not None
        assert panel.data_binding_manager is not None
        
        # Verify UI manager integration
        assert panel.ui_manager == manager
    
    def test_tab_navigation(self, settings_panel):
        """Test tab navigation functionality."""
        panel, manager, game_state = settings_panel
        
        # Get initial active tab
        initial_tab = panel.tab_container.get_active_tab()
        
        # Test switching to each tab
        tabs = ['Graphics', 'Audio', 'Controls', 'Gameplay', 'System']
        for i, tab_name in enumerate(tabs):
            panel.tab_container.set_current_tab(i)
            assert panel.tab_container.get_active_tab() == i
            
            # Verify content panel visibility
            for j, content_panel in enumerate(panel.content_panels):
                if j == i:
                    assert content_panel.visible
                else:
                    assert not content_panel.visible
    
    def test_graphics_settings_controls(self, settings_panel):
        """Test graphics settings controls."""
        panel, manager, game_state = settings_panel
        
        # Switch to graphics tab
        panel.tab_container.set_current_tab(0)
        graphics_panel = panel.content_panels[0]
        
        # Test resolution dropdown
        resolution_dropdown = graphics_panel.resolution_dropdown
        assert resolution_dropdown is not None
        assert resolution_dropdown.selected_option == str(game_state.resolution)
        
        # Test quality dropdown
        quality_dropdown = graphics_panel.quality_dropdown
        assert quality_dropdown is not None
        assert quality_dropdown.selected_option == game_state.quality
        
        # Test VSync checkbox
        vsync_checkbox = graphics_panel.vsync_checkbox
        assert vsync_checkbox is not None
        assert vsync_checkbox.is_selected == game_state.vsync
        
        # Test fullscreen checkbox
        fullscreen_checkbox = graphics_panel.fullscreen_checkbox
        assert fullscreen_checkbox is not None
        assert fullscreen_checkbox.is_selected == game_state.fullscreen
    
    def test_audio_settings_controls(self, settings_panel):
        """Test audio settings controls."""
        panel, manager, game_state = settings_panel
        
        # Switch to audio tab
        panel.tab_container.set_current_tab(1)
        audio_panel = panel.content_panels[1]
        
        # Test volume sliders
        master_slider = audio_panel.master_volume_slider
        assert master_slider is not None
        assert abs(master_slider.get_current_value() - game_state.master_volume) < 0.01
        
        music_slider = audio_panel.music_volume_slider
        assert music_slider is not None
        assert abs(music_slider.get_current_value() - game_state.music_volume) < 0.01
        
        sfx_slider = audio_panel.sfx_volume_slider
        assert sfx_slider is not None
        assert abs(sfx_slider.get_current_value() - game_state.sfx_volume) < 0.01
        
        # Test audio enabled checkbox
        audio_checkbox = audio_panel.audio_enabled_checkbox
        assert audio_checkbox is not None
        assert audio_checkbox.is_selected == game_state.audio_enabled
    
    def test_controls_settings(self, settings_panel):
        """Test controls settings."""
        panel, manager, game_state = settings_panel
        
        # Switch to controls tab
        panel.tab_container.set_current_tab(2)
        controls_panel = panel.content_panels[2]
        
        # Test mouse sensitivity slider
        sensitivity_slider = controls_panel.mouse_sensitivity_slider
        assert sensitivity_slider is not None
        assert abs(sensitivity_slider.get_current_value() - game_state.mouse_sensitivity) < 0.01
        
        # Test invert mouse Y checkbox
        invert_checkbox = controls_panel.invert_mouse_y_checkbox
        assert invert_checkbox is not None
        assert invert_checkbox.is_selected == game_state.invert_mouse_y
    
    def test_gameplay_settings(self, settings_panel):
        """Test gameplay settings."""
        panel, manager, game_state = settings_panel
        
        # Switch to gameplay tab
        panel.tab_container.set_current_tab(3)
        gameplay_panel = panel.content_panels[3]
        
        # Test difficulty dropdown
        difficulty_dropdown = gameplay_panel.difficulty_dropdown
        assert difficulty_dropdown is not None
        assert difficulty_dropdown.selected_option == game_state.difficulty
        
        # Test auto-save checkbox
        autosave_checkbox = gameplay_panel.auto_save_checkbox
        assert autosave_checkbox is not None
        assert autosave_checkbox.is_selected == game_state.auto_save
        
        # Test tutorial checkbox
        tutorial_checkbox = gameplay_panel.show_tutorial_checkbox
        assert tutorial_checkbox is not None
        assert tutorial_checkbox.is_selected == game_state.show_tutorial
    
    def test_settings_persistence(self, settings_panel):
        """Test that settings persist to game state."""
        panel, manager, game_state = settings_panel
        
        # Modify graphics settings
        panel.tab_container.set_current_tab(0)
        graphics_panel = panel.content_panels[0]
        
        # Change resolution
        graphics_panel.resolution_dropdown.selected_option = "1920x1080"
        graphics_panel.resolution_dropdown.on_changed()
        
        # Change quality
        graphics_panel.quality_dropdown.selected_option = "Ultra"
        graphics_panel.quality_dropdown.on_changed()
        
        # Toggle VSync
        graphics_panel.vsync_checkbox.selected = not graphics_panel.vsync_checkbox.is_selected
        graphics_panel.vsync_checkbox.on_changed()
        
        # Verify changes persisted to game state
        assert game_state.resolution == (1920, 1080)
        assert game_state.quality == "Ultra"
        assert game_state.vsync != True  # Should be toggled
    
    def test_data_binding_integration(self, settings_panel):
        """Test data binding manager integration."""
        panel, manager, game_state = settings_panel
        
        # Test data binding setup
        assert panel.data_binding_manager is not None
        
        # Verify bindings are created
        bindings = panel.data_binding_manager.get_bindings()
        assert len(bindings) > 0
        
        # Test two-way binding
        # Change UI value
        panel.tab_container.set_current_tab(1)
        audio_panel = panel.content_panels[1]
        audio_panel.master_volume_slider.set_current_value(0.95)
        
        # Verify game state updated
        assert abs(game_state.master_volume - 0.95) < 0.01
    
    def test_panel_visibility(self, settings_panel):
        """Test panel show/hide functionality."""
        panel, manager, game_state = settings_panel
        
        # Initially visible
        assert panel.visible
        
        # Hide panel
        panel.hide()
        assert not panel.visible
        assert not panel.window.visible
        
        # Show panel
        panel.show()
        assert panel.visible
        assert panel.window.visible
    
    def test_window_resize_handling(self, settings_panel):
        """Test window resize handling."""
        panel, manager, game_state = settings_panel
        
        # Simulate window resize
        new_size = (1280, 720)
        
        # Handle resize
        panel.handle_window_resize(new_size)
        
        # Verify UI manager updated
        assert manager.window_resolution == new_size
        
        # Verify panel adjusted
        assert panel.window.rect.width <= new_size[0]
        assert panel.window.rect.height <= new_size[1]
    
    def test_event_handling(self, settings_panel):
        """Test event handling integration."""
        panel, manager, game_state = settings_panel
        
        # Create test events
        mouse_click_event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {'pos': (100, 100), 'button': 1}
        )
        
        key_press_event = pygame.event.Event(
            pygame.KEYDOWN,
            {'key': pygame.K_ESCAPE, 'mod': 0}
        )
        
        # Test event handling
        result1 = panel.handle_event(mouse_click_event)
        result2 = panel.handle_event(key_press_event)
        
        # Events should be processed
        assert isinstance(result1, bool)
        assert isinstance(result2, bool)
    
    def test_settings_reset(self, settings_panel):
        """Test settings reset functionality."""
        panel, manager, game_state = settings_panel
        
        # Modify some settings
        game_state.master_volume = 0.2
        game_state.quality = "Low"
        game_state.difficulty = "Hard"
        
        # Reset settings
        panel.reset_to_defaults()
        
        # Verify settings reset to defaults
        assert game_state.master_volume == 0.8  # Default value
        assert game_state.quality == "High"     # Default value
        assert game_state.difficulty == "Normal"  # Default value
    
    def test_error_handling(self, settings_panel):
        """Test error handling in settings panel."""
        panel, manager, game_state = settings_panel
        
        # Test invalid setting value
        try:
            # This should handle gracefully
            game_state.set('invalid_setting', 'value')
            panel.update_from_game_state()
        except Exception as e:
            pytest.fail(f"Error handling failed: {e}")
        
        # Test missing game state
        try:
            panel.game_state_interface = None
            panel.update_from_game_state()
        except Exception as e:
            # Should handle gracefully
            assert isinstance(e, (AttributeError, ValueError))
    
    def test_performance_with_large_settings(self, settings_panel):
        """Test performance with many settings operations."""
        panel, manager, game_state = settings_panel
        
        import time
        
        # Test many rapid updates
        start_time = time.time()
        
        for i in range(100):
            game_state.master_volume = i / 100.0
            panel.update_from_game_state()
        
        end_time = time.time()
        
        # Should complete quickly (under 1 second)
        assert (end_time - start_time) < 1.0
    
    @pytest.mark.parametrize("tab_index", [0, 1, 2, 3, 4])
    def test_each_tab_initialization(self, settings_panel, tab_index):
        """Test that each tab initializes correctly."""
        panel, manager, game_state = settings_panel
        
        # Switch to specific tab
        panel.tab_container.set_current_tab(tab_index)
        content_panel = panel.content_panels[tab_index]
        
        # Verify panel is properly initialized
        assert content_panel is not None
        assert hasattr(content_panel, 'controls')
        assert content_panel.visible
        
        # Verify controls exist
        controls = content_panel.controls
        assert len(controls) > 0
        
        # Verify each control is properly configured
        for control in controls.values():
            assert control is not None
            assert hasattr(control, 'rect')
            assert control.rect.width > 0
            assert control.rect.height > 0
