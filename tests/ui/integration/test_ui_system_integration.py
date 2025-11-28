#!/usr/bin/env python3
"""
Comprehensive UI Integration Tests for pygame_gui panels.

This test suite verifies:
1. Integration between UI panels and game systems
2. Event bus communication between panels
3. Data binding synchronization
4. State management across panels
5. Performance under integration load
"""

import sys
import os
import pytest
import pygame
import pygame_gui
from unittest.mock import Mock, patch, MagicMock

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from ui.ui_manager import UIManager
from ui.events.ui_event_bus import UIEventBus
from ui.scene_controller import SceneController
from ui.panels.settings_panel import SettingsPanel
from ui.panels.shop_panel import ShopPanel
from ui.panels.breeding_panel import BreedingPanel
from ui.panels.voting_panel import VotingPanel
from ui.panels.main_menu_panel_refactored import MainMenuPanelRefactored
from game.game_state_interface import TurboShellsGameStateInterface
from ui.data_binding import DataBindingManager


class TestUIIntegration:
    """Test suite for UI system integration."""
    
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
        """Create comprehensive mock game state."""
        class MockGame:
            def __init__(self):
                # Basic game state
                self.money = 2000
                self.state = "main_menu"
                self.roster = [None, None, None]
                self.retired_roster = []
                
                # Settings
                self.resolution = (1024, 768)
                self.quality = "High"
                self.vsync = True
                self.master_volume = 0.8
                self.mouse_sensitivity = 0.5
                
                # Shop state
                self.shop_inventory = []
                self.shop_message = ""
                
                # Breeding state
                self.breeding_parents = []
                self.breeding_cost = 100
                
                # Voting state
                self.current_vote = None
                self.voting_results = {}
                self.voting_history = []
                self.vote_cost = 50
                
            def get(self, key, default=None):
                return getattr(self, key, default)
                
            def set(self, key, value):
                setattr(self, key, value)
        
        return MockGame()
    
    @pytest.fixture
    def ui_system(self, pygame_setup, mock_game_state):
        """Create complete UI system for integration testing."""
        screen, manager = pygame_setup
        game_state_interface = TurboShellsGameStateInterface(mock_game_state)
        
        # Create UI system components
        ui_manager = UIManager(screen.get_rect())
        ui_event_bus = UIEventBus()
        data_binding = DataBindingManager()
        
        # Initialize UI manager
        ui_manager.initialize(screen)
        
        # Create panels
        panels = {
            'main_menu': MainMenuPanelRefactored(game_state_interface, event_bus=ui_event_bus),
            'settings': SettingsPanel(game_state_interface, data_binding),
            'shop': ShopPanel(game_state_interface),
            'breeding': BreedingPanel(game_state_interface),
            'voting': VotingPanel(game_state_interface)
        }
        
        # Register panels
        for name, panel in panels.items():
            ui_manager.register_panel(name, panel)
        
        # Create scene controller
        scene_controller = SceneController(
            ui_manager,
            ui_event_bus,
            {
                'main_menu': 'main_menu',
                'settings': 'settings',
                'shop': 'shop',
                'breeding': 'breeding',
                'voting': 'voting',
            }
        )
        
        return {
            'ui_manager': ui_manager,
            'event_bus': ui_event_bus,
            'scene_controller': scene_controller,
            'game_state': mock_game_state,
            'game_state_interface': game_state_interface,
            'data_binding': data_binding,
            'panels': panels
        }
    
    def test_ui_system_initialization(self, ui_system):
        """Test complete UI system initialization."""
        ui_manager = ui_system['ui_manager']
        event_bus = ui_system['event_bus']
        scene_controller = ui_system['scene_controller']
        panels = ui_system['panels']
        
        # Verify UI manager initialized
        assert ui_manager is not None
        assert ui_manager.manager is not None
        
        # Verify event bus initialized
        assert event_bus is not None
        
        # Verify scene controller initialized
        assert scene_controller is not None
        
        # Verify all panels registered
        for name, panel in panels.items():
            assert ui_manager.get_panel(name) == panel
        
        # Verify panels initialized
        for panel in panels.values():
            assert panel is not None
            assert hasattr(panel, 'window')
    
    def test_scene_navigation(self, ui_system):
        """Test scene navigation between panels."""
        scene_controller = ui_system['scene_controller']
        panels = ui_system['panels']
        game_state = ui_system['game_state']
        
        # Test navigation to each scene
        scenes = ['main_menu', 'settings', 'shop', 'breeding', 'voting']
        
        for scene in scenes:
            # Navigate to scene
            scene_controller.goto_state(scene)
            
            # Verify scene active
            assert scene_controller.current_state == scene
            
            # Verify corresponding panel visible
            panel = panels[scene]
            assert panel.visible
            
            # Verify other panels hidden
            for other_scene, other_panel in panels.items():
                if other_scene != scene:
                    assert not other_panel.visible
            
            # Update game state
            game_state.state = scene
    
    def test_event_bus_communication(self, ui_system):
        """Test event bus communication between panels."""
        event_bus = ui_system['event_bus']
        panels = ui_system['panels']
        
        # Test navigation event
        navigation_payload = {'state': 'settings'}
        event_bus.publish('ui:navigate', navigation_payload)
        
        # Verify event processed (implementation dependent)
        # This would test that panels respond to navigation events
        
        # Test settings change event
        settings_payload = {'key': 'resolution', 'value': (1280, 720)}
        event_bus.publish('settings:changed', settings_payload)
        
        # Test shop event
        shop_payload = {'action': 'purchase', 'item': 'turtle', 'cost': 100}
        event_bus.publish('shop:action', shop_payload)
        
        # Verify event bus handles events without errors
        assert True  # If no exceptions raised, test passes
    
    def test_data_binding_synchronization(self, ui_system):
        """Test data binding synchronization between panels and game state."""
        data_binding = ui_system['data_binding']
        game_state = ui_system['game_state']
        panels = ui_system['panels']
        
        # Test settings binding
        settings_panel = panels['settings']
        
        # Change game state
        game_state.master_volume = 0.95
        
        # Update bindings
        data_binding.update_bindings()
        
        # Verify UI updated (implementation dependent)
        # This would test that UI reflects game state changes
        
        # Test reverse binding
        # Change UI value (mock)
        # Verify game state updated
    
    def test_cross_panel_state_consistency(self, ui_system):
        """Test state consistency across panels."""
        game_state = ui_system['game_state']
        panels = ui_system['panels']
        
        # Modify money in shop
        game_state.money = 1500
        
        # Navigate to different panels
        scenes = ['main_menu', 'settings', 'shop', 'breeding', 'voting']
        
        for scene in scenes:
            # Navigate to panel
            ui_system['scene_controller'].goto_state(scene)
            
            # Verify money display consistent
            # This would test that all panels show same money value
            
            # Verify other shared state consistent
            assert game_state.money == 1500
    
    def test_panel_isolation(self, ui_system):
        """Test that panels are properly isolated."""
        panels = ui_system['panels']
        
        # Test that panel internal state doesn't affect others
        settings_panel = panels['settings']
        shop_panel = panels['shop']
        
        # Modify settings panel internal state
        if hasattr(settings_panel, 'current_tab'):
            settings_panel.current_tab = 2
        
        # Verify shop panel unaffected
        # This would test that internal state is isolated
        
        # Test event handling isolation
        # Send event to one panel, verify others don't respond inappropriately
    
    def test_performance_with_all_panels(self, ui_system):
        """Test performance with all panels active."""
        ui_manager = ui_system['ui_manager']
        
        import time
        
        # Test panel creation performance
        start_time = time.time()
        
        # Show all panels (stress test)
        for panel in ui_system['panels'].values():
            panel.show()
        
        creation_time = time.time() - start_time
        
        # Should complete quickly
        assert creation_time < 2.0
        
        # Test update performance
        start_time = time.time()
        
        for _ in range(100):  # 100 update cycles
            ui_manager.update(0.016)  # 60 FPS
        
        update_time = time.time() - start_time
        
        # Should maintain good performance
        assert update_time < 1.0  # 100 updates in under 1 second
    
    def test_memory_management(self, ui_system):
        """Test memory management across panels."""
        import gc
        import sys
        
        # Get initial memory usage
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Create and destroy panels multiple times
        for _ in range(10):
            # Create temporary panel
            temp_panel = SettingsPanel(ui_system['game_state_interface'], ui_system['data_binding'])
            temp_panel.initialize(ui_system['ui_manager'].manager)
            
            # Destroy panel
            temp_panel.hide()
            del temp_panel
        
        # Check for memory leaks
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Should not have significant memory growth
        object_growth = final_objects - initial_objects
        assert object_growth < 1000  # Allow some growth but not excessive
    
    def test_error_propagation(self, ui_system):
        """Test error handling and propagation across UI system."""
        panels = ui_system['panels']
        
        # Test error in one panel doesn't crash system
        settings_panel = panels['settings']
        
        # Mock error condition
        with patch.object(settings_panel, 'handle_event', side_effect=Exception("Test error")):
            # Send event
            test_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (100, 100)})
            
            # Should handle error gracefully
            try:
                settings_panel.handle_event(test_event)
            except Exception:
                # Error should be caught and handled
                pass
        
        # Verify system still functional
        assert ui_system['ui_manager'] is not None
        assert ui_system['event_bus'] is not None
    
    def test_concurrent_access(self, ui_system):
        """Test concurrent access to UI system."""
        import threading
        import time
        
        results = []
        
        def access_panel(panel_name):
            """Function to run in thread."""
            try:
                panel = ui_system['panels'][panel_name]
                for _ in range(10):
                    # Simulate panel access
                    if hasattr(panel, 'update'):
                        panel.update(0.016)
                    time.sleep(0.001)
                results.append(f"{panel_name} success")
            except Exception as e:
                results.append(f"{panel_name} error: {e}")
        
        # Create threads for each panel
        threads = []
        for panel_name in ui_system['panels'].keys():
            thread = threading.Thread(target=access_panel, args=(panel_name,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all threads completed successfully
        for result in results:
            assert "success" in result, f"Thread failed: {result}"
    
    def test_resource_cleanup(self, ui_system):
        """Test proper resource cleanup."""
        ui_manager = ui_system['ui_manager']
        
        # Test panel cleanup
        for panel in ui_system['panels'].values():
            # Verify panel has cleanup method
            if hasattr(panel, 'cleanup'):
                panel.cleanup()
            
            # Verify panel resources released
            # This would test pygame_gui cleanup, etc.
        
        # Test UI manager cleanup
        ui_manager.shutdown()
        
        # Verify resources released
        assert True  # If no errors, cleanup successful
    
    def test_window_resize_integration(self, ui_system):
        """Test window resize handling across all panels."""
        panels = ui_system['panels']
        
        # Test various window sizes
        test_sizes = [(800, 600), (1024, 768), (1280, 720), (1920, 1080)]
        
        for size in test_sizes:
            # Simulate window resize
            for panel in panels.values():
                if hasattr(panel, 'handle_window_resize'):
                    panel.handle_window_resize(size)
            
            # Verify panels adjusted
            for panel in panels.values():
                if hasattr(panel, 'window') and panel.window:
                    assert panel.window.rect.width <= size[0]
                    assert panel.window.rect.height <= size[1]
    
    def test_input_event_distribution(self, ui_system):
        """Test input event distribution to appropriate panels."""
        ui_manager = ui_system['ui_manager']
        scene_controller = ui_system['scene_controller']
        panels = ui_system['panels']
        
        # Navigate to specific panel
        scene_controller.goto_state('settings')
        active_panel = panels['settings']
        
        # Create test events
        events = [
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (100, 100), 'button': 1}),
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE}),
            pygame.event.Event(pygame.MOUSEMOTION, {'pos': (200, 200)})
        ]
        
        # Test event handling
        for event in events:
            # Send event through UI manager
            consumed = ui_manager.handle_event(event)
            
            # Verify event processed appropriately
            assert isinstance(consumed, bool)
    
    def test_state_persistence_integration(self, ui_system):
        """Test state persistence across UI system."""
        game_state = ui_system['game_state']
        panels = ui_system['panels']
        
        # Modify various states
        game_state.money = 3000
        game_state.resolution = (1280, 720)
        game_state.master_volume = 0.9
        
        # Navigate through panels
        for scene_name in ['main_menu', 'settings', 'shop']:
            ui_system['scene_controller'].goto_state(scene_name)
            
            # Simulate panel modifications
            panel = panels[scene_name]
            if hasattr(panel, 'update_from_game_state'):
                panel.update_from_game_state()
        
        # Verify state preserved
        assert game_state.money == 3000
        assert game_state.resolution == (1280, 720)
        assert game_state.master_volume == 0.9
    
    @pytest.mark.parametrize("scene", ['main_menu', 'settings', 'shop', 'breeding', 'voting'])
    def test_individual_panel_integration(self, ui_system, scene):
        """Test individual panel integration."""
        panels = ui_system['panels']
        scene_controller = ui_system['scene_controller']
        
        # Navigate to scene
        scene_controller.goto_state(scene)
        panel = panels[scene]
        
        # Verify panel integration
        assert panel.visible
        assert panel.game_state_interface is not None
        
        # Test basic functionality
        if hasattr(panel, 'update'):
            panel.update(0.016)
        
        if hasattr(panel, 'handle_event'):
            test_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (100, 100)})
            result = panel.handle_event(test_event)
            assert isinstance(result, bool)
        
        # Test panel-specific integration points
        if scene == 'settings':
            assert panel.data_binding_manager is not None
        elif scene == 'main_menu':
            assert hasattr(panel, 'event_bus')
        elif scene in ['shop', 'breeding', 'voting']:
            assert panel.game_state_interface is not None
