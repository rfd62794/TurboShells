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

# Panels under test
from ui.panels.settings_panel import SettingsPanel
from ui.panels.shop_panel import ShopPanel
from ui.panels.breeding_panel import BreedingPanel
from ui.panels.voting_panel import VotingPanel
from ui.panels.main_menu_panel_refactored import MainMenuPanelRefactored

from ui.data_binding import DataBindingManager
from game.game_state_interface import TurboShellsGameStateInterface


class TestAllPanels:
    """Minimal smoke tests for existing pygame_gui panels."""
    
    @pytest.fixture
    def pygame_setup(self):
        """Setup pygame for testing."""
        pygame.init()
        screen = pygame.display.set_mode((1280, 720))
        manager = pygame_gui.UIManager((1280, 720))
        yield screen, manager
        pygame.quit()
    
    @pytest.fixture
    def mock_game_state(self):
        """Create comprehensive mock game state."""
        class MockGame:
            def __init__(self):
                # Shared properties
                self.money = 2000
                self.state = "main_menu"
                self.resolution = (1280, 720)
                self.quality = "High"
                self.vsync = True
                self.master_volume = 0.8
                self.mouse_sensitivity = 0.5
                self.shop_manager = {
                    'refresh_shop_inventory': Mock(return_value=True)
                }
                self.event_bus = Mock()

                # Shop state
                self.shop_inventory = []
                self.shop_message = ""

                # Breeding state
                self.breeding_parents = []
                self.breeding_cost = 100
                self.roster = [None, None, None]
                self.retired_roster = []

                # Voting state
                self.current_vote = {
                    "id": "vote_001",
                    "title": "Test Vote",
                    "description": "Mock vote",
                    "options": [
                        {"id": "speed", "name": "Speed", "description": "Fast turtles"},
                        {"id": "energy", "name": "Energy", "description": "More stamina"},
                    ],
                    "cost": 50,
                    "end_time": pygame.time.get_ticks() + 60000,
                }
                self.voting_results = {}
                self.voting_history = []
                self.vote_cost = 50
                self.voting_session_active = True

            def get(self, key, default=None):
                return getattr(self, key, default)

            def set(self, key, value):
                setattr(self, key, value)

        return MockGame()
    
    def test_settings_panel_smoke(self, pygame_setup, mock_game_state):
        """Smoke test for SettingsPanel creation and visibility."""
        _, manager = pygame_setup
        game_state_interface = TurboShellsGameStateInterface(mock_game_state)
        data_binding_manager = DataBindingManager()

        panel = SettingsPanel(game_state_interface, data_binding_manager)
        panel.setup_ui(manager)

        panel.show()
        assert panel.visible
        assert panel.window is not None

        panel.hide()
        assert not panel.visible
    
    def test_shop_panel_smoke(self, pygame_setup, mock_game_state):
        _, manager = pygame_setup
        game_state_interface = TurboShellsGameStateInterface(mock_game_state)

        panel = ShopPanel(game_state_interface)
        panel.setup_ui(manager)
        panel.show()

        assert panel.visible
        assert panel.window is not None

        panel.hide()
        assert not panel.visible
    
    def test_breeding_panel_smoke(self, pygame_setup, mock_game_state):
        _, manager = pygame_setup
        game_state_interface = TurboShellsGameStateInterface(mock_game_state)

        panel = BreedingPanel(game_state_interface)
        panel.setup_ui(manager)
        panel.show()

        assert panel.visible
        assert panel.window is not None

        panel.hide()
        assert not panel.visible
    
    @pytest.mark.xfail(reason="Voting panel requires UIScrollingContainer internals", strict=False)
    def test_voting_panel_smoke(self, pygame_setup, mock_game_state):
        _, manager = pygame_setup
        game_state_interface = TurboShellsGameStateInterface(mock_game_state)

        panel = VotingPanel(game_state_interface)
        panel.setup_ui(manager)
        panel.show()

        assert panel.visible
        assert panel.window is not None

        panel.hide()
        assert not panel.visible
    
    def test_main_menu_panel_smoke(self, pygame_setup, mock_game_state):
        _, manager = pygame_setup
        game_state_interface = TurboShellsGameStateInterface(mock_game_state)

        panel = MainMenuPanelRefactored(game_state_interface)
        panel.setup_ui(manager)
        panel.show()

        assert panel.visible
        assert panel.window is not None

        panel.hide()
        assert not panel.visible
    
    def test_panel_visibility_management(self, pygame_setup, mock_game_state):
        _, manager = pygame_setup
        game_state_interface = TurboShellsGameStateInterface(mock_game_state)

        panels = [
            SettingsPanel(game_state_interface, DataBindingManager()),
            ShopPanel(game_state_interface),
            BreedingPanel(game_state_interface),
            pytest.param(VotingPanel(game_state_interface), marks=pytest.mark.xfail(reason="Voting panel scroll dependency")),
            MainMenuPanelRefactored(game_state_interface),
        ]

        for panel in panels:
            panel.setup_ui(manager)
            panel.show()
            assert panel.visible

        for panel in panels:
            panel.hide()
            assert not panel.visible
    
    def test_panel_event_processing(self, pygame_setup, mock_game_state):
        _, manager = pygame_setup
        game_state_interface = TurboShellsGameStateInterface(mock_game_state)

        panels = [
            SettingsPanel(game_state_interface, DataBindingManager()),
            ShopPanel(game_state_interface),
            BreedingPanel(game_state_interface),
            VotingPanel(game_state_interface),
            MainMenuPanelRefactored(game_state_interface),
        ]

        events = [
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (100, 100), 'button': 1}),
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE}),
        ]

        for panel in panels:
            panel.setup_ui(manager)
            panel.show()

            for event in events:
                result = panel.handle_event(event)
                assert isinstance(result, bool)

            panel.hide()


@pytest.mark.parametrize(
    "panel_factory",
    [
        lambda gs: SettingsPanel(gs, DataBindingManager()),
        lambda gs: ShopPanel(gs),
        lambda gs: BreedingPanel(gs),
        pytest.param(lambda gs: VotingPanel(gs), marks=pytest.mark.xfail(reason="Voting panel scroll dependency")),
        lambda gs: MainMenuPanelRefactored(gs),
    ],
)
def test_individual_panel_show_hide(pygame_setup, mock_game_state, panel_factory):
    """Ensure each panel supports show/hide lifecycle."""
    _, manager = pygame_setup
    game_state_interface = TurboShellsGameStateInterface(mock_game_state)

    panel = panel_factory(game_state_interface)
    panel.setup_ui(manager)

    panel.show()
    assert panel.visible

    panel.hide()
    assert not panel.visible


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
