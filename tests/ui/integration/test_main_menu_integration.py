"""
Integration tests for Main Menu with game systems.

This test suite verifies:
1. Main Menu integration with game state
2. Main Menu integration with UI manager
3. Main Menu integration with event bus
4. Main Menu integration with navigation system
5. Main Menu integration with save/load system
"""

import sys
import os
import pytest
import pygame
import pygame_gui
from unittest.mock import Mock, patch, MagicMock

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from ui.panels.main_menu_panel_refactored import MainMenuPanelRefactored
from game.game_state_interface import TurboShellsGameStateInterface


class TestMainMenuGameIntegration:
    """Integration tests for Main Menu with game systems."""
    
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
        """Create mock game state with full interface."""
        class MockGame:
            def __init__(self):
                self.money = 2741
                self.state = "main_menu"
                self.turtles = []
                self.race_history = []
                self.voting_records = []
                
            def get(self, key, default=None):
                return getattr(self, key, default)
                
            def set(self, key, value):
                setattr(self, key, value)
                
            class MockUIManager:
                def __init__(self):
                    self.panels = {}
                    self.active_panels = []
                    
                def toggle_panel(self, panel_id):
                    if panel_id in self.active_panels:
                        self.active_panels.remove(panel_id)
                    else:
                        self.active_panels.append(panel_id)
                        
                def show_panel(self, panel_id):
                    if panel_id not in self.active_panels:
                        self.active_panels.append(panel_id)
                        
                def hide_panel(self, panel_id):
                    if panel_id in self.active_panels:
                        self.active_panels.remove(panel_id)
                    
            ui_manager = MockUIManager()
        
        mock_game = MockGame()
        return TurboShellsGameStateInterface(mock_game)
    
    @pytest.fixture
    def mock_event_bus(self):
        """Create mock event bus."""
        return Mock()
    
    @pytest.fixture
    def main_menu(self, pygame_setup, mock_game_state, mock_event_bus):
        """Create Main Menu with full integration."""
        screen, manager = pygame_setup
        main_menu = MainMenuPanelRefactored(mock_game_state, mock_event_bus)
        main_menu.manager = manager
        main_menu._create_window()
        return main_menu
    
    def test_game_state_integration(self, main_menu, mock_game_state):
        """Test integration with game state interface."""
        # Should have access to game state
        assert main_menu.game_state == mock_game_state
        
        # Should read money from game state
        assert main_menu.money_display.get_amount() == mock_game_state.get('money')
        
        # Should update when game state changes
        mock_game_state.set('money', 5000)
        main_menu.update(0.016)
        assert main_menu.money_display.get_amount() == 5000
    
    def test_ui_manager_integration(self, main_menu):
        """Test integration with UI manager."""
        # Should have UI manager reference
        assert main_menu.manager is not None
        
        # Should create pygame_gui elements through manager
        assert main_menu.window is not None
        assert main_menu.money_display.label is not None
        for button in main_menu.menu_buttons:
            assert button.button is not None
    
    def test_event_bus_integration(self, main_menu, mock_event_bus):
        """Test integration with event bus."""
        # Should have event bus reference
        assert main_menu.event_bus == mock_event_bus
        
        # Should emit navigation events through event bus
        main_menu._navigate("ROSTER")
        
        # Check if event was emitted
        mock_event_bus.emit.assert_called_with("ui:navigate", {"state": "ROSTER"})
    
    def test_navigation_integration(self, main_menu, mock_game_state):
        """Test navigation system integration."""
        # Test roster navigation with special handling
        main_menu._navigate("ROSTER")
        assert mock_game_state.get('select_racer_mode') is True
        
        # Test other navigation
        main_menu._navigate("SHOP")
        # Should emit event or set state
        
        # Test race navigation
        main_menu._navigate("RACE")
        # Should emit race navigation event
    
    def test_ui_panel_integration(self, main_menu, mock_game_state):
        """Test integration with UI panel system."""
        # Test settings panel toggle
        with patch.object(mock_game_state.game.ui_manager, 'toggle_panel') as mock_toggle:
            main_menu._toggle_settings()
            mock_toggle.assert_called_once_with('settings')
    
    def test_quit_dialog_integration(self, main_menu):
        """Test quit dialog integration."""
        # Should have quit dialog
        assert main_menu.quit_dialog is not None
        
        # Should show quit dialog on quit action
        with patch.object(main_menu.quit_dialog, 'show') as mock_show:
            main_menu._show_quit_confirmation()
            mock_show.assert_called_once()
        
        # Should handle quit confirmation
        with patch('pygame.event.post') as mock_post:
            main_menu._on_quit_confirmed()
            mock_post.assert_called_once()
            # Check that QUIT event was posted
    
    def test_callback_integration(self, main_menu):
        """Test callback system integration."""
        # Test navigation callback
        nav_callback_called = False
        nav_callback_state = None
        
        def nav_callback(state):
            nonlocal nav_callback_called, nav_callback_state
            nav_callback_called = True
            nav_callback_state = state
        
        main_menu.set_navigation_callback(nav_callback)
        main_menu._navigate("TEST")
        
        assert nav_callback_called
        assert nav_callback_state == "TEST"
        
        # Test quit callback
        quit_callback_called = False
        
        def quit_callback():
            nonlocal quit_callback_called
            quit_callback_called = True
        
        main_menu.set_quit_callback(quit_callback)
        main_menu._on_quit_confirmed()
        
        assert quit_callback_called
    
    def test_save_load_integration(self, main_menu, mock_game_state):
        """Test integration with save/load system."""
        # Should work with game state that can be saved/loaded
        mock_game_state.set('money', 3000)
        mock_game_state.set('state', 'ROSTER')
        
        # Main menu should reflect current game state
        main_menu.update(0.016)
        assert main_menu.money_display.get_amount() == 3000
        
        # Should handle game state changes from load
        mock_game_state.set('money', 1500)
        main_menu.update(0.016)
        assert main_menu.money_display.get_amount() == 1500
    
    def test_full_game_loop_integration(self, pygame_setup, mock_game_state):
        """Test integration in full game loop simulation."""
        screen, manager = pygame_setup
        
        # Create main menu
        main_menu = MainMenuPanelRefactored(mock_game_state)
        main_menu.manager = manager
        main_menu._create_window()
        
        # Simulate game loop
        clock = pygame.time.Clock()
        running = True
        frame_count = 0
        
        while running and frame_count < 10:  # Run for 10 frames
            time_delta = clock.tick(60) / 1000.0
            frame_count += 1
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                main_menu.handle_event(event)
                manager.process_events(event)
            
            # Update
            manager.update(time_delta)
            main_menu.update(time_delta)
            
            # Render
            screen.fill((50, 50, 50))
            main_menu.render(screen)
            manager.draw_ui(screen)
            pygame.display.flip()
        
        # Should complete without errors
        assert frame_count == 10
    
    def test_error_handling_integration(self, main_menu, mock_game_state):
        """Test error handling in integration scenarios."""
        # Test with missing game state
        main_menu.game_state = None
        try:
            main_menu.update(0.016)
            # Should not crash
        except Exception as e:
            pytest.fail(f"Update with None game state crashed: {e}")
        
        # Test with missing manager
        main_menu.manager = None
        try:
            main_menu.handle_event(Mock())
            # Should not crash
        except Exception as e:
            pytest.fail(f"Event handling with None manager crashed: {e}")
    
    def test_memory_integration(self, main_menu):
        """Test memory usage and cleanup."""
        # Should not leak memory
        initial_button_count = len(main_menu.menu_buttons)
        
        # Recreate window
        main_menu._create_window()
        
        # Should have same number of buttons
        assert len(main_menu.menu_buttons) == initial_button_count
        
        # All components should be properly created
        assert main_menu.window is not None
        assert main_menu.money_display is not None
        assert main_menu.quit_dialog is not None


class TestMainMenuPerformanceIntegration:
    """Performance integration tests."""
    
    @pytest.fixture
    def pygame_setup(self):
        """Setup pygame for testing."""
        pygame.init()
        screen = pygame.display.set_mode((1024, 768))
        manager = pygame_gui.UIManager((1024, 768))
        yield screen, manager
        pygame.quit()
    
    @pytest.fixture
    def main_menu(self, pygame_setup):
        """Create Main Menu for performance testing."""
        screen, manager = pygame_setup
        mock_game_state = Mock()
        mock_game_state.get = Mock(return_value=2741)
        
        main_menu = MainMenuPanelRefactored(mock_game_state)
        main_menu.manager = manager
        main_menu._create_window()
        return main_menu
    
    def test_creation_performance(self, pygame_setup):
        """Test Main Menu creation performance."""
        import time
        
        screen, manager = pygame_setup
        mock_game_state = Mock()
        mock_game_state.get = Mock(return_value=2741)
        
        # Measure creation time
        start_time = time.time()
        
        for _ in range(10):
            main_menu = MainMenuPanelRefactored(mock_game_state)
            main_menu.manager = manager
            main_menu._create_window()
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Should create 10 menus in reasonable time (less than 1 second)
        assert creation_time < 1.0, f"Creation too slow: {creation_time:.3f}s"
    
    def test_update_performance(self, main_menu):
        """Test update performance."""
        import time
        
        # Measure update time
        start_time = time.time()
        
        for _ in range(1000):
            main_menu.update(0.016)
        
        end_time = time.time()
        update_time = end_time - start_time
        
        # Should update 1000 times in reasonable time (less than 0.1 seconds)
        assert update_time < 0.1, f"Update too slow: {update_time:.3f}s"
    
    def test_render_performance(self, main_menu):
        """Test render performance."""
        import time
        screen = pygame.display.set_mode((1024, 768))
        
        # Measure render time
        start_time = time.time()
        
        for _ in range(100):
            main_menu.render(screen)
        
        end_time = time.time()
        render_time = end_time - start_time
        
        # Should render 100 times in reasonable time (less than 0.1 seconds)
        assert render_time < 0.1, f"Render too slow: {render_time:.3f}s"


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
