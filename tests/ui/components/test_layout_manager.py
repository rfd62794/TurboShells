"""
Tests for LayoutManager component.

Tests SRP compliance and layout management functionality.
"""

import unittest
from unittest.mock import Mock, patch
import pygame

from ui.components.layout_manager import LayoutManager, LayoutConstraints


class TestLayoutManager(unittest.TestCase):
    """Test cases for LayoutManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.screen_rect = pygame.Rect(0, 0, 1024, 768)
        self.layout_manager = LayoutManager(self.screen_rect)
    
    def test_initialization(self):
        """Test LayoutManager initialization."""
        self.assertEqual(self.layout_manager.screen_rect, self.screen_rect)
        self.assertIsNotNone(self.layout_manager.panel_rect)
        self.assertIsNotNone(self.layout_manager.tab_bar_rect)
        self.assertIsNotNone(self.layout_manager.content_rect)
        
        # Check that panel is within screen bounds
        self.assertGreaterEqual(self.layout_manager.panel_rect.x, 0)
        self.assertGreaterEqual(self.layout_manager.panel_rect.y, 0)
        self.assertLessEqual(self.layout_manager.panel_rect.right, self.screen_rect.width)
        self.assertLessEqual(self.layout_manager.panel_rect.bottom, self.screen_rect.height)
    
    def test_panel_constraints(self):
        """Test that panel respects constraints."""
        panel_rect = self.layout_manager.get_panel_rect()
        
        # Check minimum constraints
        self.assertGreaterEqual(panel_rect.width, self.layout_manager.panel_constraints.min_width)
        self.assertGreaterEqual(panel_rect.height, self.layout_manager.panel_constraints.min_height)
        
        # Check maximum constraints
        self.assertLessEqual(panel_rect.width, self.layout_manager.panel_constraints.max_width)
        self.assertLessEqual(panel_rect.height, self.layout_manager.panel_constraints.max_height)
        
        # Check that panel uses percentage of screen
        expected_max_width = self.screen_rect.width * 0.95
        expected_max_height = self.screen_rect.height * 0.9
        
        self.assertLessEqual(panel_rect.width, expected_max_width)
        self.assertLessEqual(panel_rect.height, expected_max_height)
    
    def test_tab_bar_positioning(self):
        """Test tab bar positioning within panel."""
        panel_rect = self.layout_manager.get_panel_rect()
        tab_bar_rect = self.layout_manager.get_tab_bar_rect()
        
        # Tab bar should be at top of panel with padding
        self.assertGreater(tab_bar_rect.x, panel_rect.x)
        self.assertEqual(tab_bar_rect.y, panel_rect.y + 10)  # padding
        self.assertLess(tab_bar_rect.right, panel_rect.right)
        self.assertLess(tab_bar_rect.bottom, panel_rect.bottom)
    
    def test_content_area_positioning(self):
        """Test content area positioning."""
        panel_rect = self.layout_manager.get_panel_rect()
        tab_bar_rect = self.layout_manager.get_tab_bar_rect()
        content_rect = self.layout_manager.get_content_rect()
        
        # Content should be below tab bar
        self.assertGreater(content_rect.y, tab_bar_rect.bottom)
        self.assertEqual(content_rect.x, panel_rect.x + 10)  # padding
        self.assertLess(content_rect.right, panel_rect.right)
        self.assertLess(content_rect.bottom, panel_rect.bottom)
    
    def test_update_screen_size(self):
        """Test updating layout for new screen size."""
        new_screen_rect = pygame.Rect(0, 0, 800, 600)
        old_panel_rect = self.layout_manager.panel_rect.copy()
        
        self.layout_manager.update_screen_size(new_screen_rect)
        
        # Check that screen rect was updated
        self.assertEqual(self.layout_manager.screen_rect, new_screen_rect)
        
        # Check that panel was recalculated
        self.assertNotEqual(self.layout_manager.panel_rect.size, old_panel_rect.size)
        
        # Check that new panel fits in new screen
        self.assertLessEqual(self.layout_manager.panel_rect.right, new_screen_rect.width)
        self.assertLessEqual(self.layout_manager.panel_rect.bottom, new_screen_rect.height)
    
    def test_calculate_element_positions(self):
        """Test calculating positions for UI elements."""
        area_rect = pygame.Rect(100, 100, 400, 300)
        
        elements = [
            {'height': 25, 'width': 200},
            {'height': 30, 'width': 150},
            {'height': 25, 'width': 180}
        ]
        
        positions = self.layout_manager.calculate_element_positions(elements, area_rect)
        
        self.assertEqual(len(positions), 3)
        
        # Check vertical arrangement
        for i in range(1, len(positions)):
            self.assertGreater(positions[i].y, positions[i-1].y)
            self.assertEqual(positions[i].x, positions[0].x)  # Same x position
        
        # Check that elements fit in area
        for pos in positions:
            self.assertGreaterEqual(pos.x, area_rect.x)
            self.assertGreaterEqual(pos.y, area_rect.y)
            self.assertLessEqual(pos.right, area_rect.right)
            self.assertLessEqual(pos.bottom, area_rect.bottom)
    
    def test_calculate_button_positions_right_alignment(self):
        """Test button position calculation with right alignment."""
        area_rect = pygame.Rect(100, 100, 400, 300)
        button_size = (80, 30)
        button_count = 3
        
        positions = self.layout_manager.calculate_button_positions(
            button_count, button_size, area_rect, "right"
        )
        
        self.assertEqual(len(positions), 3)
        
        # Check right alignment (buttons should be from right edge)
        expected_x = area_rect.right - button_size[0] - 10
        self.assertEqual(positions[0].x, expected_x)
        
        # Check vertical position
        for pos in positions:
            self.assertEqual(pos.y, area_rect.bottom - button_size[1] - 10)
        
        # Check horizontal spacing
        for i in range(1, len(positions)):
            expected_x = positions[i-1].x - button_size[0] - 10
            self.assertEqual(positions[i].x, expected_x)
    
    def test_calculate_button_positions_center_alignment(self):
        """Test button position calculation with center alignment."""
        area_rect = pygame.Rect(100, 100, 400, 300)
        button_size = (80, 30)
        button_count = 3
        
        positions = self.layout_manager.calculate_button_positions(
            button_count, button_size, area_rect, "center"
        )
        
        self.assertEqual(len(positions), 3)
        
        # Check that buttons are centered
        total_width = button_count * button_size[0] + (button_count - 1) * 10
        expected_start_x = area_rect.centerx - (total_width // 2)
        self.assertEqual(positions[0].x, expected_start_x)
    
    def test_calculate_grid_layout(self):
        """Test grid layout calculation."""
        area_rect = pygame.Rect(100, 100, 400, 300)
        items = [{'id': i} for i in range(5)]
        
        positions = self.layout_manager.calculate_grid_layout(items, area_rect, 2)
        
        self.assertEqual(len(positions), 5)
        
        # Check grid arrangement
        # Row 0: items 0, 1
        # Row 1: items 2, 3  
        # Row 2: item 4
        self.assertEqual(positions[0].y, positions[1].y)  # Same row
        self.assertLess(positions[0].x, positions[1].x)   # Left to right
        
        self.assertEqual(positions[2].y, positions[3].y)  # Same row
        self.assertLess(positions[2].x, positions[3].x)   # Left to right
        
        self.assertGreater(positions[2].y, positions[1].y)  # Next row
        self.assertGreater(positions[4].y, positions[3].y)  # Next row
    
    def test_calculate_vertical_layout(self):
        """Test vertical layout calculation."""
        area_rect = pygame.Rect(100, 100, 400, 300)
        
        elements = [
            {'height': 25, 'width': 200},
            {'height': 30, 'width': 150},
            {'height': 25, 'width': 180}
        ]
        
        positions = self.layout_manager.calculate_vertical_layout(elements, area_rect)
        
        self.assertEqual(len(positions), 3)
        
        # Check vertical arrangement
        for i in range(1, len(positions)):
            self.assertGreater(positions[i].y, positions[i-1].y)
            self.assertEqual(positions[i].x, positions[0].x)  # Same x position
        
        # Check spacing
        for i in range(1, len(positions)):
            expected_spacing = elements[i-1]['height'] + self.layout_manager.content_constraints.spacing
            self.assertEqual(positions[i].y, positions[i-1].y + expected_spacing)
    
    def test_calculate_horizontal_layout(self):
        """Test horizontal layout calculation."""
        area_rect = pygame.Rect(100, 100, 400, 300)
        
        elements = [
            {'height': 25, 'width': 100},
            {'height': 25, 'width': 80},
            {'height': 25, 'width': 120}
        ]
        
        positions = self.layout_manager.calculate_horizontal_layout(elements, area_rect)
        
        self.assertEqual(len(positions), 3)
        
        # Check horizontal arrangement
        for i in range(1, len(positions)):
            self.assertGreater(positions[i].x, positions[i-1].x)
            self.assertEqual(positions[i].y, positions[0].y)  # Same y position
        
        # Check that elements fit in area
        for pos in positions:
            self.assertGreaterEqual(pos.x, area_rect.x)
            self.assertLessEqual(pos.right, area_rect.right)
    
    def test_get_layout_info(self):
        """Test getting layout information."""
        info = self.layout_manager.get_layout_info()
        
        # Check required keys
        required_keys = ['screen_size', 'panel_size', 'tab_bar_size', 'content_size', 'panel_position', 'utilization']
        for key in required_keys:
            self.assertIn(key, info)
        
        # Check data types
        self.assertIsInstance(info['screen_size'], tuple)
        self.assertIsInstance(info['panel_size'], tuple)
        self.assertIsInstance(info['tab_bar_size'], tuple)
        self.assertIsInstance(info['content_size'], tuple)
        self.assertIsInstance(info['panel_position'], tuple)
        self.assertIsInstance(info['utilization'], dict)
        
        # Check utilization percentages
        self.assertGreater(info['utilization']['width_percent'], 0)
        self.assertLess(info['utilization']['width_percent'], 100)
        self.assertGreater(info['utilization']['height_percent'], 0)
        self.assertLess(info['utilization']['height_percent'], 100)
    
    def test_validate_layout_valid(self):
        """Test layout validation with valid layout."""
        issues = self.layout_manager.validate_layout()
        
        # Should have no issues with default valid layout
        self.assertEqual(len(issues), 0)
    
    def test_validate_layout_invalid(self):
        """Test layout validation with invalid layout."""
        # Create invalid layout by setting panel too large
        self.layout_manager.panel_rect = pygame.Rect(0, 0, 2000, 2000)
        
        issues = self.layout_manager.validate_layout()
        
        # Should detect issues
        self.assertGreater(len(issues), 0)
        
        # Check for specific issues
        issue_text = ' '.join(issues)
        self.assertIn("extends beyond", issue_text)
    
    def test_reset_to_defaults(self):
        """Test resetting layout to defaults."""
        # Modify layout
        new_screen_rect = pygame.Rect(0, 0, 800, 600)
        self.layout_manager.update_screen_size(new_screen_rect)
        
        # Reset
        self.layout_manager.reset_to_defaults()
        
        # Should be back to original screen size
        self.assertEqual(self.layout_manager.screen_rect, new_screen_rect)
        
        # Layout should be recalculated
        self.assertIsNotNone(self.layout_manager.panel_rect)
        self.assertIsNotNone(self.layout_manager.tab_bar_rect)
        self.assertIsNotNone(self.layout_manager.content_rect)
    
    def test_minimum_screen_size_handling(self):
        """Test handling of very small screen sizes."""
        small_screen = pygame.Rect(0, 0, 400, 300)
        layout_manager = LayoutManager(small_screen)
        
        # Should still create valid layout
        self.assertIsNotNone(layout_manager.panel_rect)
        self.assertGreaterEqual(layout_manager.panel_rect.width, layout_manager.panel_constraints.min_width)
        self.assertGreaterEqual(layout_manager.panel_rect.height, layout_manager.panel_constraints.min_height)
    
    def test_large_screen_size_handling(self):
        """Test handling of very large screen sizes."""
        large_screen = pygame.Rect(0, 0, 3840, 2160)  # 4K
        layout_manager = LayoutManager(large_screen)
        
        # Should respect maximum constraints
        self.assertLessEqual(layout_manager.panel_rect.width, layout_manager.panel_constraints.max_width)
        self.assertLessEqual(layout_manager.panel_rect.height, layout_manager.panel_constraints.max_height)
        
        # Should still be centered/positioned correctly
        self.assertLessEqual(layout_manager.panel_rect.right, large_screen.width)
        self.assertLessEqual(layout_manager.panel_rect.bottom, large_screen.height)
    
    @patch('ui.components.layout_manager.get_logger')
    def test_logging(self, mock_get_logger):
        """Test that logging is properly configured."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        # Create new layout manager to test logging
        layout_manager = LayoutManager(self.screen_rect)
        
        # Verify logger was called
        mock_get_logger.assert_called_once_with('ui.components.layout_manager')
        mock_logger.debug.assert_called()


if __name__ == '__main__':
    unittest.main()
