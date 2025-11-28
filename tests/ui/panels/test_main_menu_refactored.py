"""
Comprehensive test suite for the refactored Main Menu Panel.

This test suite verifies:
1. Component architecture and SRP compliance
2. Basic functionality and feature parity
3. Event handling and navigation
4. Visual layout and positioning
5. Integration with game systems
"""

import sys
import os
import pytest
import pygame
import pygame_gui
from unittest.mock import Mock, patch

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from ui.panels.main_menu_panel_refactored import MainMenuPanelRefactored
from game.game_state_interface import TurboShellsGameStateInterface
from ui.components.reusable import Button, MoneyDisplay


class TestMainMenuRefactored:
    """Test suite for the refactored Main Menu Panel."""
    
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
                self.money = 2741
                self.state = "main_menu"
                
            def get(self, key, default=None):
                return getattr(self, key, default)
                
            def set(self, key, value):
                setattr(self, key, value)
                
            class MockUIManager:
                def toggle_panel(self, panel_id):
                    pass
                    
            ui_manager = MockUIManager()
        
        mock_game = MockGame()
        return TurboShellsGameStateInterface(mock_game)
    
    @pytest.fixture
    def main_menu(self, pygame_setup, mock_game_state):
        """Create Main Menu instance for testing."""
        screen, manager = pygame_setup
        main_menu = MainMenuPanelRefactored(mock_game_state)
        main_menu.manager = manager
        main_menu._create_window()
        return main_menu
    
    def test_initialization(self, mock_game_state):
        """Test Main Menu initialization."""
        main_menu = MainMenuPanelRefactored(mock_game_state)
        
        assert main_menu.panel_id == "main_menu"
        assert main_menu.title == "Turbo Shells"
        assert main_menu.size == (400, 550)
        assert len(main_menu.menu_buttons) == 0  # Buttons created in _create_window
        assert main_menu.game_state is not None
    
    def test_window_creation(self, main_menu):
        """Test window creation and positioning."""
        assert main_menu.window is not None
        assert main_menu.container is not None
        
        # Check window is centered
        screen_w, screen_h = main_menu.manager.window_resolution
        expected_x = (screen_w - main_menu.size[0]) // 2
        expected_y = (screen_h - main_menu.size[1]) // 2
        
        assert main_menu.position[0] == expected_x
        assert main_menu.position[1] == expected_y
    
    def test_component_creation(self, main_menu):
        """Test that all components are created correctly."""
        # Money display
        assert main_menu.money_display is not None
        assert isinstance(main_menu.money_display, MoneyDisplay)
        assert main_menu.money_display.get_amount() == 2741
        
        # Buttons
        assert len(main_menu.menu_buttons) == 7
        expected_buttons = ["Roster", "Shop", "Breeding", "Race", "Voting", "Settings", "Quit"]
        actual_buttons = [button.text for button in main_menu.menu_buttons]
        
        assert actual_buttons == expected_buttons
        
        # All buttons should be Button instances
        for button in main_menu.menu_buttons:
            assert isinstance(button, Button)
            assert button.button is not None  # pygame_gui element created
    
    def test_button_positioning(self, main_menu):
        """Test that buttons are positioned correctly."""
        expected_y_positions = [40, 90, 140, 190, 240, 290, 340]  # y_pos + i * (40 + 10)
        
        for i, button in enumerate(main_menu.menu_buttons):
            assert button.rect.x == 10  # Left margin
            assert button.rect.y == expected_y_positions[i]
            assert button.rect.width == 360  # width - 40px margin
            assert button.rect.height == 40
    
    def test_money_display_positioning(self, main_menu):
        """Test money display positioning."""
        money_display = main_menu.money_display
        expected_x = main_menu.size[0] - 40 - 140  # width - margin - display_width
        expected_y = 5
        
        assert money_display.rect.x == expected_x
        assert money_display.rect.y == expected_y
        assert money_display.rect.width == 140
        assert money_display.rect.height == 25
    
    def test_button_actions(self, main_menu):
        """Test that buttons have correct actions."""
        expected_actions = {
            "Roster": "navigate_roster",
            "Shop": "navigate_shop", 
            "Breeding": "navigate_breeding",
            "Race": "navigate_race",
            "Voting": "navigate_voting",
            "Settings": "toggle_settings",
            "Quit": "quit"
        }
        
        for button in main_menu.menu_buttons:
            assert button.action == expected_actions[button.text]
    
    def test_button_styles(self, main_menu):
        """Test that buttons have correct styles."""
        for button in main_menu.menu_buttons:
            if button.text == "Quit":
                assert button.config['style'] == 'danger'
            elif button.text == "Settings":
                assert button.config['style'] == 'secondary'
            else:
                assert button.config['style'] == 'primary'
    
    def test_event_handling(self, main_menu):
        """Test event handling through components."""
        # Test that events are properly delegated
        mock_event = Mock()
        
        # Should handle quit dialog events first
        if main_menu.quit_dialog:
            main_menu.quit_dialog.handle_event = Mock(return_value=False)
        
        # Should handle money display events
        main_menu.money_display.handle_event = Mock(return_value=False)
        
        # Should handle button events
        for button in main_menu.menu_buttons:
            button.handle_event = Mock(return_value=False)
        
        # Should call super().handle_event if no component handles it
        with patch.object(main_menu.__class__.__bases__[0], 'handle_event', return_value=False):
            result = main_menu.handle_event(mock_event)
            assert result is False
    
    def test_navigation_actions(self, main_menu, mock_game_state):
        """Test navigation button actions."""
        # Test navigate actions
        main_menu._on_button_action("navigate_roster")
        assert mock_game_state.get('select_racer_mode') is True
        
        main_menu._on_button_action("navigate_shop")
        # Should emit event or set state
        
        # Test settings toggle
        with patch.object(mock_game_state.game.ui_manager, 'toggle_panel') as mock_toggle:
            main_menu._on_button_action("toggle_settings")
            mock_toggle.assert_called_once_with('settings')
        
        # Test quit action
        with patch.object(main_menu, '_show_quit_confirmation') as mock_quit:
            main_menu._on_button_action("quit")
            mock_quit.assert_called_once()
    
    def test_money_display_update(self, main_menu, mock_game_state):
        """Test money display updates with game state."""
        # Change money amount
        mock_game_state.set('money', 5000)
        
        # Update main menu
        main_menu.update(0.016)
        
        # Check money display updated
        assert main_menu.money_display.get_amount() == 5000
    
    def test_button_utilities(self, main_menu):
        """Test button utility methods."""
        # Test get_button
        roster_button = main_menu.get_button("Roster")
        assert roster_button is not None
        assert roster_button.text == "Roster"
        
        non_existent = main_menu.get_button("NonExistent")
        assert non_existent is None
        
        # Test set_button_enabled
        main_menu.set_button_enabled("Roster", False)
        assert roster_button.enabled is False
        
        main_menu.set_button_enabled("Roster", True)
        assert roster_button.enabled is True
    
    def test_component_isolation(self, main_menu):
        """Test that components are properly isolated (SRP)."""
        # Each component should be independently testable
        assert main_menu.money_display is not None
        assert isinstance(main_menu.money_display, MoneyDisplay)
        
        # Each button should be independent
        for button in main_menu.menu_buttons:
            assert isinstance(button, Button)
            assert button.action is not None
            assert button.text is not None
        
        # Components should be configurable
        for button in main_menu.menu_buttons:
            assert button.config is not None
            assert 'style' in button.config
    
    def test_visual_layout(self, main_menu):
        """Test visual layout and spacing."""
        window_rect = main_menu.window.rect
        container_rect = main_menu.container.rect
        
        # Window should be properly sized
        assert window_rect.width == 430  # size + borders
        assert window_rect.height == 580  # size + borders
        
        # Container should be within window
        assert container_rect.x > window_rect.x
        assert container_rect.y > window_rect.y
        assert container_rect.width < window_rect.width
        assert container_rect.height < window_rect.height
        
        # Buttons should not overlap
        button_rects = [button.button.rect for button in main_menu.menu_buttons]
        for i in range(len(button_rects) - 1):
            current = button_rects[i]
            next_rect = button_rects[i + 1]
            assert current.bottom <= next_rect.top  # No overlap
    
    def test_integration_compatibility(self, main_menu, mock_game_state):
        """Test integration with existing game systems."""
        # Should work with game state interface
        assert main_menu.game_state == mock_game_state
        
        # Should have quit dialog
        assert main_menu.quit_dialog is not None
        
        # Should support callbacks
        callback_called = False
        def test_callback(state):
            nonlocal callback_called
            callback_called = True
        
        main_menu.set_navigation_callback(test_callback)
        main_menu._navigate("ROSTER")
        assert callback_called


class TestMainMenuIntegration:
    """Integration tests for Main Menu with full game systems."""
    
    def test_full_game_integration(self):
        """Test integration with actual game systems."""
        # This would test with real game state and UI manager
        # For now, just verify the import works
        from ui.panels.main_menu_panel_refactored import MainMenuPanelRefactored
        assert MainMenuPanelRefactored is not None


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
