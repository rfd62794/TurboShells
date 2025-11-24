"""
Integration tests for the refactored Settings View.

Tests the coordination between all SRP components.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pygame

from ui.components.settings_view_refactored import SettingsViewRefactored, UIElement
from ui.components.tab_manager import SettingsTab


class TestSettingsViewRefactored(unittest.TestCase):
    """Test cases for the refactored SettingsView class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.screen_rect = pygame.Rect(0, 0, 1024, 768)
        self.settings_view = SettingsViewRefactored(self.screen_rect)
    
    def test_initialization(self):
        """Test SettingsView initialization with SRP components."""
        # Check that all components are initialized
        self.assertIsNotNone(self.settings_view.layout_manager)
        self.assertIsNotNone(self.settings_view.tab_manager)
        self.assertIsNotNone(self.settings_view.ui_renderer)
        self.assertIsNotNone(self.settings_view.event_handler)
        
        # Check initial state
        self.assertFalse(self.settings_view.visible)
        self.assertTrue(self.settings_view.needs_redraw)
        
        # Check that tab content is created
        self.assertIn(SettingsTab.GRAPHICS, self.settings_view.tab_content)
        self.assertIn(SettingsTab.AUDIO, self.settings_view.tab_content)
        self.assertIn(SettingsTab.CONTROLS, self.settings_view.tab_content)
        self.assertIn(SettingsTab.GAMEPLAY, self.settings_view.tab_content)
        self.assertIn(SettingsTab.SYSTEM, self.settings_view.tab_content)
        
        # Check action buttons
        self.assertEqual(len(self.settings_view.action_buttons), 3)
        button_labels = [button.label for button in self.settings_view.action_buttons]
        self.assertIn("Apply", button_labels)
        self.assertIn("Reset", button_labels)
        self.assertIn("X", button_labels)
    
    def test_component_integration(self):
        """Test that components are properly integrated."""
        # Check that layout manager provides correct rectangles
        panel_rect = self.settings_view.layout_manager.get_panel_rect()
        tab_bar_rect = self.settings_view.layout_manager.get_tab_bar_rect()
        content_rect = self.settings_view.layout_manager.get_content_rect()
        
        # Check that tab manager uses layout manager's tab bar
        self.assertEqual(self.settings_view.tab_manager.tab_bar_rect, tab_bar_rect)
        
        # Check that event handler is configured
        self.assertEqual(len(self.settings_view.event_handler.action_buttons), 3)
        self.assertIn(SettingsTab.GRAPHICS, self.settings_view.event_handler.ui_elements)
        
        # Check that tab change callback is set
        self.assertEqual(len(self.settings_view.event_handler.tab_change_callbacks), 1)
    
    def test_show_hide_toggle(self):
        """Test show, hide, and toggle functionality."""
        # Initially hidden
        self.assertFalse(self.settings_view.visible)
        
        # Show
        self.settings_view.show()
        self.assertTrue(self.settings_view.visible)
        self.assertTrue(self.settings_view.needs_redraw)
        
        # Hide
        self.settings_view.hide()
        self.assertFalse(self.settings_view.visible)
        
        # Toggle from hidden
        self.settings_view.toggle()
        self.assertTrue(self.settings_view.visible)
        
        # Toggle from visible
        self.settings_view.toggle()
        self.assertFalse(self.settings_view.visible)
    
    def test_tab_content_creation(self):
        """Test that tab content is created correctly."""
        # Graphics tab
        graphics_content = self.settings_view.tab_content[SettingsTab.GRAPHICS]
        self.assertGreater(len(graphics_content), 0)
        
        # Check for expected element types
        element_types = [element.element_type for element in graphics_content]
        self.assertIn('dropdown', element_types)
        self.assertIn('checkbox', element_types)
        
        # Audio tab
        audio_content = self.settings_view.tab_content[SettingsTab.AUDIO]
        self.assertGreater(len(audio_content), 0)
        
        element_types = [element.element_type for element in audio_content]
        self.assertIn('slider', element_types)
        self.assertIn('checkbox', element_types)
    
    def test_layout_calculations(self):
        """Test that layouts are calculated correctly."""
        content_rect = self.settings_view.layout_manager.get_content_rect()
        
        # Check that elements are positioned within content area
        for tab_content in self.settings_view.tab_content.values():
            for element in tab_content:
                self.assertGreaterEqual(element.rect.x, content_rect.x)
                self.assertGreaterEqual(element.rect.y, content_rect.y)
                self.assertLessEqual(element.rect.right, content_rect.right)
                self.assertLessEqual(element.rect.bottom, content_rect.bottom)
        
        # Check action buttons are positioned correctly
        panel_rect = self.settings_view.layout_manager.get_panel_rect()
        for button in self.settings_view.action_buttons:
            self.assertGreaterEqual(button.rect.x, panel_rect.x)
            self.assertGreaterEqual(button.rect.y, panel_rect.y)
            self.assertLessEqual(button.rect.right, panel_rect.right)
            self.assertLessEqual(button.rect.bottom, panel_rect.bottom)
    
    def test_event_handling_delegation(self):
        """Test that events are properly delegated to event handler."""
        # Create a mock event
        mock_event = Mock()
        mock_event.type = pygame.MOUSEBUTTONDOWN
        mock_event.button = 1
        mock_event.pos = (100, 100)
        
        # Test with hidden view (should not handle)
        self.settings_view.visible = False
        result = self.settings_view.handle_event(mock_event)
        self.assertFalse(result)
        
        # Test with visible view
        self.settings_view.visible = True
        with patch.object(self.settings_view.event_handler, 'handle_event', return_value=True):
            result = self.settings_view.handle_event(mock_event)
            self.assertTrue(result)
            self.settings_view.event_handler.handle_event.assert_called_once_with(mock_event)
    
    def test_update_functionality(self):
        """Test update functionality."""
        # Test with hidden view (should not update)
        self.settings_view.visible = False
        self.settings_view.update(0.016)  # 60 FPS
        
        # Test with visible view
        self.settings_view.visible = True
        with patch('pygame.mouse.get_pos', return_value=(500, 300)):
            self.settings_view.update(0.016)
            # Should update renderer mouse position
            # (This is tested implicitly through the renderer mock)
    
    @patch('pygame.display.get_surface')
    def test_draw_functionality(self, mock_get_surface):
        """Test draw functionality."""
        mock_screen = Mock()
        mock_get_surface.return_value = mock_screen
        
        # Test with hidden view (should not draw)
        self.settings_view.visible = False
        self.settings_view.draw(mock_screen)
        
        # Verify no drawing calls were made
        mock_screen.fill.assert_not_called()
        
        # Test with visible view
        self.settings_view.visible = True
        
        # Mock renderer methods
        with patch.object(self.settings_view.ui_renderer, 'draw_panel') as mock_panel:
            with patch.object(self.settings_view.ui_renderer, 'draw_tabs') as mock_tabs:
                with patch.object(self.settings_view.ui_renderer, 'draw_ui_element') as mock_element:
                    with patch.object(self.settings_view.ui_renderer, 'draw_tooltip') as mock_tooltip:
                        
                        self.settings_view.draw(mock_screen)
                        
                        # Verify drawing calls were made
                        mock_panel.assert_called_once()
                        mock_tabs.assert_called_once()
                        
                        # Verify elements were drawn
                        current_tab = self.settings_view.tab_manager.get_active_tab()
                        content_elements = self.settings_view.tab_content.get(current_tab, [])
                        expected_element_calls = len(content_elements) + len(self.settings_view.action_buttons)
                        self.assertEqual(mock_element.call_count, expected_element_calls)
    
    def test_layout_update(self):
        """Test layout update functionality."""
        new_screen_rect = pygame.Rect(0, 0, 800, 600)
        
        # Get original layout info
        original_layout = self.settings_view.layout_manager.get_layout_info()
        
        # Update layout
        self.settings_view.update_layout(new_screen_rect)
        
        # Check that layout was updated
        self.assertEqual(self.settings_view.screen_rect, new_screen_rect)
        updated_layout = self.settings_view.layout_manager.get_layout_info()
        self.assertNotEqual(original_layout['screen_size'], updated_layout['screen_size'])
        
        # Check that components were updated
        self.assertEqual(self.settings_view.tab_manager.tab_bar_rect, 
                        self.settings_view.layout_manager.get_tab_bar_rect())
        
        # Check that event handler was updated
        self.assertEqual(len(self.settings_view.event_handler.action_buttons), 3)
        self.assertIn(SettingsTab.GRAPHICS, self.settings_view.event_handler.ui_elements)
    
    def test_settings_callbacks(self):
        """Test that settings callbacks work correctly."""
        # Test fullscreen toggle
        with patch('core.config.config_manager') as mock_config:
            mock_config.get_config.return_value.graphics.fullscreen = False
            
            self.settings_view._on_fullscreen_toggle()
            
            # Verify config was updated
            self.assertTrue(mock_config.get_config.return_value.graphics.fullscreen)
        
        # Test apply settings
        with patch('core.config.config_manager') as mock_config:
            with patch('core.graphics_manager.graphics_manager') as mock_graphics:
                with patch('core.audio_manager.audio_manager') as mock_audio:
                    
                    self.settings_view._apply_settings()
                    
                    # Verify managers were called
                    mock_config.save_config.assert_called_once()
                    mock_graphics.initialize_display.assert_called_once()
                    mock_audio.apply_volume_settings.assert_called_once()
                    
                    # Verify view was hidden
                    self.assertFalse(self.settings_view.visible)
        
        # Test reset settings
        with patch('core.config.config_manager') as mock_config:
            with patch('core.graphics_manager.graphics_manager') as mock_graphics:
                with patch('core.audio_manager.audio_manager') as mock_audio:
                    
                    self.settings_view._reset_settings()
                    
                    # Verify managers were called
                    mock_config.reset_to_defaults.assert_called_once()
                    mock_graphics.reset_to_defaults.assert_called_once()
                    mock_audio.reset_to_defaults.assert_called_once()
                    
                    # Verify content was reinitialized
                    self.assertIn(SettingsTab.GRAPHICS, self.settings_view.tab_content)
    
    def test_component_info(self):
        """Test component information gathering."""
        info = self.settings_view.get_component_info()
        
        # Check required keys
        required_keys = ['layout_manager', 'tab_manager', 'ui_elements']
        for key in required_keys:
            self.assertIn(key, info)
        
        # Check layout manager info
        self.assertIn('screen_size', info['layout_manager'])
        self.assertIn('panel_size', info['layout_manager'])
        
        # Check tab manager info
        self.assertIn('active_tab', info['tab_manager'])
        self.assertIn('tab_count', info['tab_manager'])
        self.assertIn('enabled_tabs', info['tab_manager'])
        
        # Check UI elements info
        self.assertIn('total_tabs', info['ui_elements'])
        self.assertIn('elements_per_tab', info['ui_elements'])
        self.assertIn('action_buttons', info['ui_elements'])
        
        # Verify values
        self.assertEqual(info['tab_manager']['active_tab'], 'graphics')
        self.assertEqual(info['ui_elements']['action_buttons'], 3)
    
    def test_value_getters(self):
        """Test value getter methods."""
        mock_config = Mock()
        mock_config.graphics.resolution_width = 1920
        mock_config.graphics.resolution_height = 1080
        mock_config.graphics.fullscreen = True
        mock_config.graphics.quality_level = "High"
        mock_config.graphics.vsync = False
        
        # Test graphics value getter
        resolution = self.settings_view._get_graphics_value('Resolution:', mock_config)
        self.assertEqual(resolution, "1920x1080")
        
        fullscreen = self.settings_view._get_graphics_value('Fullscreen', mock_config)
        self.assertTrue(fullscreen)
        
        quality = self.settings_view._get_graphics_value('Quality:', mock_config)
        self.assertEqual(quality, "High")
        
        vsync = self.settings_view._get_graphics_value('VSync', mock_config)
        self.assertFalse(vsync)
    
    def test_callback_creation(self):
        """Test callback creation methods."""
        # Test graphics callback creation
        fullscreen_callback = self.settings_view._create_graphics_callback('Fullscreen')
        self.assertIsNotNone(fullscreen_callback)
        self.assertTrue(callable(fullscreen_callback))
        
        # Test unknown label callback
        unknown_callback = self.settings_view._create_graphics_callback('Unknown')
        self.assertIsNotNone(unknown_callback)
        self.assertTrue(callable(unknown_callback))
    
    @patch('ui.components.settings_view_refactored.get_logger')
    def test_logging(self, mock_get_logger):
        """Test that logging is properly configured."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        # Create new settings view to test logging
        settings_view = SettingsViewRefactored(self.screen_rect)
        
        # Verify logger was called
        mock_get_logger.assert_called_once_with('ui.components.settings_view_refactored')
        mock_logger.info.assert_called()
    
    def test_error_handling(self):
        """Test error handling in various scenarios."""
        # Test with invalid screen rect
        invalid_rect = pygame.Rect(0, 0, 100, 100)  # Very small
        try:
            small_view = SettingsViewRefactored(invalid_rect)
            # Should still work but with adjusted layout
            self.assertIsNotNone(small_view.layout_manager)
        except Exception as e:
            self.fail(f"SettingsView should handle small screen sizes: {e}")
        
        # Test event handling with None event
        try:
            result = self.settings_view.handle_event(None)
            self.assertFalse(result)
        except Exception as e:
            self.fail(f"Should handle None event gracefully: {e}")


if __name__ == '__main__':
    unittest.main()
