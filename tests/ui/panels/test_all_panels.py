#!/usr/bin/env python3
"""
Comprehensive test for all existing pygame_gui panels to verify they work correctly.
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
from ui.panels.shop_panel import ShopPanel
from ui.panels.breeding_panel import BreedingPanel
from ui.panels.voting_panel import VotingPanel
from ui.panels.main_menu_panel_refactored import MainMenuPanelRefactored
from ui.data_binding import DataBindingManager
from game.game_state_interface import TurboShellsGameStateInterface


class TestAllPanels:
    """Test suite for all existing pygame_gui panels."""
    
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
                # Basic state
                self.money = 2000
                self.state = "main_menu"
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
                self.roster = [None, None, None]
                self.retired_roster = []
                
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
    
    def test_settings_panel_functionality(self, pygame_setup, mock_game_state):
        """Test SettingsPanel basic functionality."""
        screen, manager = pygame_setup
        game_state_interface = TurboShellsGameStateInterface(mock_game_state)
        data_binding_manager = DataBindingManager()
        
        panel = SettingsPanel(game_state_interface, data_binding_manager)
        panel.setup_ui(manager)
        panel.show()
        
        # Verify panel setup
        assert panel.visible
        assert panel.window is not None
        assert "Settings" in panel.window.window_title
        
        # Test event handling
        mouse_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (100, 100)})
        result = panel.handle_event(mouse_event)
        assert isinstance(result, bool)
        
        panel.hide()
        assert not panel.visible
    
    def test_shop_panel_functionality(self, pygame_setup, mock_game_state):
        """Test ShopPanel basic functionality."""
        screen, manager = pygame_setup
        game_state_interface = TurboShellsGameStateInterface(mock_game_state)
        
        panel = ShopPanel(game_state_interface)
        panel.setup_ui(manager)
        panel.show()
        
        # Verify panel setup
        assert panel.visible
        assert panel.window is not None
        assert "Shop" in panel.window.window_title
        
        # Test event handling
        mouse_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (100, 100)})
        result = panel.handle_event(mouse_event)
        assert isinstance(result, bool)
        
        panel.hide()
        assert not panel.visible
    
    def test_breeding_panel_functionality(self, pygame_setup, mock_game_state):
        """Test BreedingPanel basic functionality."""
        screen, manager = pygame_setup
        game_state_interface = TurboShellsGameStateInterface(mock_game_state)
        
        panel = BreedingPanel(game_state_interface)
        panel.setup_ui(manager)
        panel.show()
        
        # Verify panel setup
        assert panel.visible
        assert panel.window is not None
        assert "Breeding" in panel.window.window_title
        
        # Test event handling
        mouse_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (100, 100)})
        result = panel.handle_event(mouse_event)
        assert isinstance(result, bool)
        
        panel.hide()
        assert not panel.visible
    
    def test_voting_panel_functionality(self, pygame_setup, mock_game_state):
        """Test VotingPanel basic functionality."""
        screen, manager = pygame_setup
        game_state_interface = TurboShellsGameStateInterface(mock_game_state)
        
        panel = VotingPanel(game_state_interface)
        panel.setup_ui(manager)
        panel.show()
        
        # Verify panel setup
        assert panel.visible
        assert panel.window is not None
        assert "Voting" in panel.window.window_title
        
        # Test event handling
        mouse_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (100, 100)})
        result = panel.handle_event(mouse_event)
        assert isinstance(result, bool)
        
        panel.hide()
        assert not panel.visible
    
    def test_main_menu_panel_functionality(self, pygame_setup, mock_game_state):
        """Test MainMenuPanelRefactored basic functionality."""
        screen, manager = pygame_setup
        game_state_interface = TurboShellsGameStateInterface(mock_game_state)
        
        panel = MainMenuPanelRefactored(game_state_interface)
        panel.setup_ui(manager)
        panel.show()
        
        # Verify panel setup
        assert panel.visible
        assert panel.window is not None
        assert "Main Menu" in panel.window.window_title
        
        # Test event handling
        mouse_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (100, 100)})
        result = panel.handle_event(mouse_event)
        assert isinstance(result, bool)
        
        panel.hide()
        assert not panel.visible
    
    def test_panel_visibility_management(self, pygame_setup, mock_game_state):
        """Test that panels can be shown and hidden properly."""
        screen, manager = pygame_setup
        game_state_interface = TurboShellsGameStateInterface(mock_game_state)
        
        panels = [
            SettingsPanel(game_state_interface, DataBindingManager()),
            ShopPanel(game_state_interface),
            BreedingPanel(game_state_interface),
            VotingPanel(game_state_interface),
            MainMenuPanelRefactored(game_state_interface)
        ]
        
        # Setup all panels
        for panel in panels:
            panel.setup_ui(manager)
        
        # Test showing panels one at a time
        for i, panel in enumerate(panels):
            # Show current panel
            panel.show()
            assert panel.visible
            assert panel.window.visible
            
            # Hide other panels
            for j, other_panel in enumerate(panels):
                if i != j:
                    other_panel.hide()
                    assert not other_panel.visible
                    assert not other_panel.window.visible
        
        # Hide all panels
        for panel in panels:
            panel.hide()
            assert not panel.visible
    
    def test_panel_event_processing(self, pygame_setup, mock_game_state):
        """Test that panels process events without errors."""
        screen, manager = pygame_setup
        game_state_interface = TurboShellsGameStateInterface(mock_game_state)
        
        panels = [
            SettingsPanel(game_state_interface, DataBindingManager()),
            ShopPanel(game_state_interface),
            BreedingPanel(game_state_interface),
            VotingPanel(game_state_interface),
            MainMenuPanelRefactored(game_state_interface)
        ]
        
        # Setup and show all panels
        for panel in panels:
            panel.setup_ui(manager)
            panel.show()
        
        # Test various events
        events = [
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (100, 100), 'button': 1}),
            pygame.event.Event(pygame.MOUSEBUTTONUP, {'pos': (100, 100), 'button': 1}),
            pygame.event.Event(pygame.MOUSEMOTION, {'pos': (200, 200)}),
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE}),
            pygame.event.Event(pygame.KEYUP, {'key': pygame.K_ESCAPE}),
        ]
        
        # Test each panel with each event
        for panel in panels:
            for event in events:
                try:
                    result = panel.handle_event(event)
                    assert isinstance(result, bool)
                except Exception as e:
                    pytest.fail(f"Panel {panel.__class__.__name__} failed to handle event {event}: {e}")
        
        # Hide all panels
        for panel in panels:
            panel.hide()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
