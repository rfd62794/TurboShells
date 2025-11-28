"""
UI and pygame fixtures.

This module contains fixtures for UI testing, pygame setup,
and UI component testing.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Generator
from unittest.mock import Mock
import pytest
import sys

# Ensure project root is in path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Import utility classes
from tests.utils import UIAssertHelpers, UITestDataFactory, UIPerformanceTracker

# UI-specific imports
try:
    import pygame
    import pygame_gui
    PYGAME_AVAILABLE = True
except ImportError:
    print("Warning: pygame not available")
    PYGAME_AVAILABLE = False
    pygame = None
    pygame_gui = None


@pytest.fixture
def mock_pygame():
    """Mock pygame for UI testing"""
    pygame_mock = Mock()
    pygame_mock.display.set_mode.return_value = Mock()
    pygame_mock.display.get_surface.return_value = Mock()
    pygame_mock.event.get.return_value = []
    pygame_mock.key.get_pressed.return_value = [False] * 1000
    pygame_mock.mouse.get_pos.return_value = (400, 300)
    pygame_mock.mouse.get_pressed.return_value = (False, False, False)
    pygame_mock.time.Clock.return_value = Mock()
    pygame_mock.time.Clock.return_value.tick.return_value = 60
    return pygame_mock


# UI-Specific Fixtures
@pytest.fixture
def pygame_setup():
    """Setup pygame for UI testing"""
    if not PYGAME_AVAILABLE:
        pytest.skip("pygame not available")
    
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    manager = pygame_gui.UIManager((1024, 768))
    
    yield screen, manager
    
    pygame.quit()


@pytest.fixture  
def ui_manager():
    """Provide UI manager for testing"""
    if not PYGAME_AVAILABLE:
        pytest.skip("pygame not available")
    
    pygame.init()
    manager = pygame_gui.UIManager((800, 600))
    yield manager
    pygame.quit()


@pytest.fixture
def mock_game_state_interface():
    """Provide mock game state interface for UI testing"""
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
    
    # Try to import and wrap with interface
    try:
        from game.game_state_interface import TurboShellsGameStateInterface
        return TurboShellsGameStateInterface(mock_game)
    except ImportError:
        # Return mock game directly if interface not available
        return mock_game


@pytest.fixture
def mock_event_bus():
    """Provide mock event bus for UI testing"""
    return Mock()


@pytest.fixture
def ui_test_data():
    """Provide data for UI testing"""
    return {
        'window_size': (1024, 768),
        'panel_size': (400, 550),
        'button_size': (360, 40),
        'money_display_size': (140, 25),
        'test_positions': [(100, 100), (400, 300), (700, 500)],
        'click_events': [(100, 100, 'left'), (400, 300, 'right')],
        'key_events': [('space', 'down'), ('escape', 'up')],
        'button_texts': ['Roster', 'Shop', 'Breeding', 'Race', 'Voting', 'Settings', 'Quit'],
        'button_actions': ['navigate_roster', 'navigate_shop', 'navigate_breeding', 'navigate_race', 'navigate_voting', 'toggle_settings', 'quit']
    }


@pytest.fixture
def main_menu_components():
    """Provide main menu component configurations for testing"""
    return {
        'window_config': {
            'title': 'Turbo Shells',
            'size': (400, 550),
            'resizable': False
        },
        'button_config': {
            'primary': {'style': 'primary'},
            'danger': {'style': 'danger'},
            'secondary': {'style': 'secondary'}
        },
        'money_display_config': {
            'font_size': 16,
            'text_color': (255, 255, 255),
            'prefix': '$',
            'show_prefix': True
        },
        'layout_config': {
            'button_spacing': 10,
            'button_height': 40,
            'header_height': 40,
            'padding': 10,
            'margin': 10
        }
    }


@pytest.fixture
def ui_assert_helpers():
    """Provide UI assertion helpers"""
    return UIAssertHelpers()


@pytest.fixture
def ui_test_factory():
    """Provide UI test data factory"""
    return UITestDataFactory()


@pytest.fixture
def ui_perf_tracker():
    """Provide UI performance tracker"""
    return UIPerformanceTracker()


@pytest.fixture
def ui_test_data():
    """Provide data for UI testing"""
    return {
        'window_size': (800, 600),
        'test_positions': [(100, 100), (400, 300), (700, 500)],
        'click_events': [(100, 100, 'left'), (400, 300, 'right')],
        'key_events': [('space', 'down'), ('escape', 'up')]
    }
