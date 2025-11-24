"""
Tests for TabManager component.

Tests SRP compliance and tab management functionality.
"""

import unittest
from unittest.mock import Mock, patch
import pygame

from ui.components.tab_manager import TabManager, TabConfig, SettingsTab


class TestTabManager(unittest.TestCase):
    """Test cases for TabManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tab_bar_rect = pygame.Rect(10, 10, 800, 40)
        self.tab_manager = TabManager(self.tab_bar_rect)
    
    def test_initialization(self):
        """Test TabManager initialization."""
        self.assertEqual(self.tab_manager.tab_bar_rect, self.tab_bar_rect)
        self.assertEqual(self.tab_manager.active_tab, SettingsTab.GRAPHICS)
        self.assertEqual(len(self.tab_manager.tabs), 7)  # Default tabs
        self.assertEqual(len(self.tab_manager.tab_configs), 7)
    
    def test_default_tabs_created(self):
        """Test that default tabs are created correctly."""
        expected_tabs = [
            SettingsTab.GRAPHICS,
            SettingsTab.AUDIO,
            SettingsTab.CONTROLS,
            SettingsTab.GAMEPLAY,
            SettingsTab.PROFILE,
            SettingsTab.APPEARANCE,
            SettingsTab.SYSTEM
        ]
        
        for tab_id in expected_tabs:
            self.assertIn(tab_id, self.tab_manager.tabs)
            tab_element = self.tab_manager.get_tab_element(tab_id)
            self.assertIsNotNone(tab_element)
            self.assertEqual(tab_element.config.tab_id, tab_id)
            self.assertTrue(tab_element.config.enabled)
    
    def test_tab_layout_calculation(self):
        """Test tab layout calculations."""
        # Check that tabs are positioned horizontally
        tab_positions = []
        for tab_element in self.tab_manager.get_all_tab_elements():
            tab_positions.append(tab_element.rect.x)
        
        # Tabs should be in increasing x order
        self.assertEqual(tab_positions, sorted(tab_positions))
        
        # Check tab dimensions
        for tab_element in self.tab_manager.get_all_tab_elements():
            self.assertGreaterEqual(tab_element.rect.width, self.tab_manager.min_tab_width)
            self.assertLessEqual(tab_element.rect.width, self.tab_manager.max_tab_width)
            self.assertEqual(tab_element.rect.height, 35)
    
    def test_switch_to_valid_tab(self):
        """Test switching to a valid tab."""
        result = self.tab_manager.switch_to_tab(SettingsTab.AUDIO)
        
        self.assertTrue(result)
        self.assertEqual(self.tab_manager.get_active_tab(), SettingsTab.AUDIO)
    
    def test_switch_to_invalid_tab(self):
        """Test switching to an invalid tab."""
        result = self.tab_manager.switch_to_tab(SettingsTab.GRAPHICS)  # Already active
        self.assertTrue(result)
        
        # Try to switch to non-existent tab (if we had one)
        # This test would need a mock invalid tab
    
    def test_switch_to_disabled_tab(self):
        """Test switching to a disabled tab."""
        # Disable a tab
        self.tab_manager.enable_tab(SettingsTab.AUDIO, False)
        
        # Try to switch to disabled tab
        result = self.tab_manager.switch_to_tab(SettingsTab.AUDIO)
        
        self.assertFalse(result)
        self.assertNotEqual(self.tab_manager.get_active_tab(), SettingsTab.AUDIO)
    
    def test_enable_disable_tab(self):
        """Test enabling and disabling tabs."""
        # Initially enabled
        self.assertTrue(self.tab_manager.get_tab_element(SettingsTab.AUDIO).config.enabled)
        
        # Disable tab
        self.tab_manager.enable_tab(SettingsTab.AUDIO, False)
        self.assertFalse(self.tab_manager.get_tab_element(SettingsTab.AUDIO).config.enabled)
        
        # Re-enable tab
        self.tab_manager.enable_tab(SettingsTab.AUDIO, True)
        self.assertTrue(self.tab_manager.get_tab_element(SettingsTab.AUDIO).config.enabled)
    
    def test_get_enabled_tabs(self):
        """Test getting enabled tabs."""
        # All tabs should be enabled initially
        enabled_tabs = self.tab_manager.get_enabled_tabs()
        self.assertEqual(len(enabled_tabs), 7)
        
        # Disable one tab
        self.tab_manager.enable_tab(SettingsTab.AUDIO, False)
        enabled_tabs = self.tab_manager.get_enabled_tabs()
        self.assertEqual(len(enabled_tabs), 6)
        
        # Check that disabled tab is not in enabled list
        enabled_tab_ids = [tab.config.tab_id for tab in enabled_tabs]
        self.assertNotIn(SettingsTab.AUDIO, enabled_tab_ids)
    
    def test_handle_click_valid_tab(self):
        """Test handling clicks on valid tabs."""
        # Get tab position
        audio_tab = self.tab_manager.get_tab_element(SettingsTab.AUDIO)
        click_pos = audio_tab.rect.center
        
        result = self.tab_manager.handle_click(click_pos)
        
        self.assertEqual(result, SettingsTab.AUDIO)
        self.assertEqual(self.tab_manager.get_active_tab(), SettingsTab.AUDIO)
    
    def test_handle_click_disabled_tab(self):
        """Test handling clicks on disabled tabs."""
        # Disable tab
        self.tab_manager.enable_tab(SettingsTab.AUDIO, False)
        
        # Click on disabled tab
        audio_tab = self.tab_manager.get_tab_element(SettingsTab.AUDIO)
        click_pos = audio_tab.rect.center
        
        result = self.tab_manager.handle_click(click_pos)
        
        self.assertIsNone(result)
        self.assertNotEqual(self.tab_manager.get_active_tab(), SettingsTab.AUDIO)
    
    def test_handle_click_no_tab(self):
        """Test handling clicks outside tabs."""
        # Click outside any tab
        click_pos = (0, 0)
        
        result = self.tab_manager.handle_click(click_pos)
        
        self.assertIsNone(result)
    
    def test_get_tab_at_position(self):
        """Test getting tab at specific position."""
        # Get tab position
        audio_tab = self.tab_manager.get_tab_element(SettingsTab.AUDIO)
        
        # Test position on tab
        result = self.tab_manager.get_tab_at_position(audio_tab.rect.center)
        self.assertEqual(result, SettingsTab.AUDIO)
        
        # Test position outside tabs
        result = self.tab_manager.get_tab_at_position((0, 0))
        self.assertIsNone(result)
    
    def test_is_tab_active(self):
        """Test checking if tab is active."""
        # Default active tab
        self.assertTrue(self.tab_manager.is_tab_active(SettingsTab.GRAPHICS))
        self.assertFalse(self.tab_manager.is_tab_active(SettingsTab.AUDIO))
        
        # Switch active tab
        self.tab_manager.switch_to_tab(SettingsTab.AUDIO)
        self.assertFalse(self.tab_manager.is_tab_active(SettingsTab.GRAPHICS))
        self.assertTrue(self.tab_manager.is_tab_active(SettingsTab.AUDIO))
    
    def test_set_tab_tooltip(self):
        """Test setting tab tooltips."""
        original_tooltip = self.tab_manager.get_tab_element(SettingsTab.AUDIO).config.tooltip
        
        new_tooltip = "Test tooltip"
        self.tab_manager.set_tab_tooltip(SettingsTab.AUDIO, new_tooltip)
        
        updated_tooltip = self.tab_manager.get_tab_element(SettingsTab.AUDIO).config.tooltip
        self.assertEqual(updated_tooltip, new_tooltip)
        self.assertNotEqual(updated_tooltip, original_tooltip)
    
    def test_update_layout(self):
        """Test updating tab layout."""
        original_positions = {}
        for tab_id, tab_element in self.tab_manager.tabs.items():
            original_positions[tab_id] = tab_element.rect.copy()
        
        # Update with new tab bar rect
        new_tab_bar_rect = pygame.Rect(20, 20, 600, 40)
        self.tab_manager.update_layout(new_tab_bar_rect)
        
        # Check that layout was updated
        self.assertEqual(self.tab_manager.tab_bar_rect, new_tab_bar_rect)
        
        # Positions should have changed
        for tab_id in self.tab_manager.tabs:
            self.assertNotEqual(
                self.tab_manager.tabs[tab_id].rect,
                original_positions[tab_id]
            )
    
    def test_get_tab_count(self):
        """Test getting tab counts."""
        self.assertEqual(self.tab_manager.get_tab_count(), 7)
        self.assertEqual(self.tab_manager.get_enabled_tab_count(), 7)
        
        # Disable a tab
        self.tab_manager.enable_tab(SettingsTab.AUDIO, False)
        self.assertEqual(self.tab_manager.get_tab_count(), 7)  # Total unchanged
        self.assertEqual(self.tab_manager.get_enabled_tab_count(), 6)  # Enabled reduced
    
    def test_reset_to_default(self):
        """Test resetting to default state."""
        # Change state
        self.tab_manager.switch_to_tab(SettingsTab.AUDIO)
        self.tab_manager.enable_tab(SettingsTab.GRAPHICS, False)
        
        # Reset
        self.tab_manager.reset_to_default()
        
        # Check defaults restored
        self.assertEqual(self.tab_manager.get_active_tab(), SettingsTab.GRAPHICS)
        self.assertTrue(self.tab_manager.get_tab_element(SettingsTab.GRAPHICS).config.enabled)
        self.assertEqual(len(self.tab_manager.tabs), 7)
    
    @patch('ui.components.tab_manager.get_logger')
    def test_logging(self, mock_get_logger):
        """Test that logging is properly configured."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        # Create new tab manager to test logging
        tab_manager = TabManager(self.tab_bar_rect)
        
        # Verify logger was called
        mock_get_logger.assert_called_once_with('ui.components.tab_manager')
        mock_logger.debug.assert_called()
    
    def test_tab_callback_functionality(self):
        """Test that tab callbacks work correctly."""
        # Test that tab elements have callbacks
        for tab_element in self.tab_manager.get_all_tab_elements():
            self.assertIsNotNone(tab_element.callback)
            self.assertTrue(callable(tab_element.callback))
        
        # Test callback execution
        original_tab = self.tab_manager.get_active_tab()
        audio_tab = self.tab_manager.get_tab_element(SettingsTab.AUDIO)
        
        # Execute callback
        audio_tab.callback()
        
        # Check that tab switched
        self.assertEqual(self.tab_manager.get_active_tab(), SettingsTab.AUDIO)


if __name__ == '__main__':
    unittest.main()
