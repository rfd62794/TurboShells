#!/usr/bin/env python3
"""
Comprehensive pytest configuration and fixtures for TurboShells
Provides centralized test data management and test utilities.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Generator
from unittest.mock import Mock, MagicMock
import pytest
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Try to import game modules for fixtures, handle gracefully if not found
try:
    from src.core.game.entities import Turtle
    from src.core.game_state import generate_random_turtle, breed_turtles, compute_turtle_cost, generate_track, get_terrain_at
    from tests.mock_data_generator import MockDataGenerator
    GAME_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Game modules not available: {e}")
    GAME_MODULES_AVAILABLE = False
    Turtle = None
    MockDataGenerator = None

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


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Provide test data directory path"""
    return Path(__file__).parent / "test_data"


@pytest.fixture(scope="session")
def mock_generator():
    """Provide mock data generator with fixed seed"""
    if not GAME_MODULES_AVAILABLE or MockDataGenerator is None:
        pytest.skip("Game modules not available")
    return MockDataGenerator(seed=42)


@pytest.fixture
def sample_turtle_data(mock_generator):
    """Provide sample turtle data for testing"""
    if not GAME_MODULES_AVAILABLE:
        pytest.skip("Game modules not available")
    return mock_generator.generate_turtle()


@pytest.fixture
def sample_turtle(sample_turtle_data):
    """Provide a sample Turtle instance"""
    if not GAME_MODULES_AVAILABLE or Turtle is None:
        pytest.skip("Game modules not available")
    return Turtle(
        name=sample_turtle_data.name,
        speed=sample_turtle_data.speed,
        energy=sample_turtle_data.energy,
        recovery=sample_turtle_data.recovery,
        swim=sample_turtle_data.swim,
        climb=sample_turtle_data.climb,
    )


@pytest.fixture
def sample_turtles(mock_generator):
    """Provide multiple sample turtles for testing"""
    if not GAME_MODULES_AVAILABLE:
        pytest.skip("Game modules not available")
    return [mock_generator.generate_turtle() for _ in range(5)]


@pytest.fixture
def mock_game_state():
    """Provide a mock game state"""
    mock_game = Mock()
    mock_game.money = 100
    mock_game.roster = []
    mock_game.retired_roster = []
    mock_game.shop_inventory = []
    mock_game.state = "MENU"
    mock_game.current_race = None
    mock_game.race_history = []
    mock_game.votes = {}
    mock_game.genetics_pool = {}
    return mock_game


@pytest.fixture
def temp_save_dir() -> Generator[Path, None, None]:
    """Provide temporary directory for save file testing"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_track():
    """Provide sample race track for testing"""
    return generate_track(1000)


@pytest.fixture
def sample_tracks():
    """Provide multiple sample tracks with different lengths"""
    return {
        'short': generate_track(500),
        'medium': generate_track(1000),
        'long': generate_track(1500)
    }


@pytest.fixture
def terrain_functions():
    """Provide terrain function test data"""
    return {
        'get_terrain_at': get_terrain_at,
        'test_positions': [(100, 100), (400, 300), (700, 500)]
    }


@pytest.fixture
def breeding_scenarios(mock_generator):
    """Provide breeding scenario test data"""
    parent1 = mock_generator.generate_turtle()
    parent2 = mock_generator.generate_turtle()
    
    return {
        'parents': (parent1, parent2),
        'high_stats_parents': (
            mock_generator.generate_turtle(high_stats=True),
            mock_generator.generate_turtle(high_stats=True)
        ),
        'low_stats_parents': (
            mock_generator.generate_turtle(low_stats=True),
            mock_generator.generate_turtle(low_stats=True)
        )
    }


@pytest.fixture
def performance_test_data():
    """Provide data for performance testing"""
    return {
        'large_roster_size': 50,
        'race_iterations': 100,
        'memory_test_iterations': 1000,
        'timeout_seconds': 30
    }


@pytest.fixture
def ui_test_data():
    """Provide data for UI testing"""
    return {
        'window_size': (800, 600),
        'test_positions': [(100, 100), (400, 300), (700, 500)],
        'click_events': [(100, 100, 'left'), (400, 300, 'right')],
        'key_events': [('space', 'down'), ('escape', 'up')]
    }


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
def performance_test_data():
    """Provide data for performance testing"""
    return {
        'large_roster_size': 50,
        'race_iterations': 100,
        'memory_test_iterations': 1000,
        'timeout_seconds': 30,
        'ui_performance': {
            'creation_threshold': 0.1,  # 100ms
            'update_threshold': 0.001,   # 1ms  
            'render_threshold': 0.01     # 10ms
        }
    }


@pytest.fixture
def save_file_data():
    """Provide sample save file data"""
    return {
        'version': '2.4.0',
        'money': 150,
        'roster': [
            {
                'name': 'Test Turtle',
                'speed': 5.0,
                'energy': 100.0,
                'recovery': 2.0,
                'swim': 1.5,
                'climb': 1.5,
                'age': 3,
                'is_active': True,
                'current_energy': 100.0,
                'race_distance': 0.0,
                'is_resting': False,
                'finished': False,
                'rank': 0
            }
        ],
        'retired_roster': [],
        'shop_inventory': [],
        'race_history': [],
        'votes': {},
        'genetics_pool': {}
    }


@pytest.fixture
def error_scenarios():
    """Provide error scenario test data"""
    return {
        'invalid_turtle_data': {
            'name': '',
            'speed': -1.0,
            'energy': 0.0,
            'recovery': -1.0,
            'swim': -1.0,
            'climb': -1.0,
            'age': -1,
            'is_active': True
        },
        'corrupted_save_file': '{"invalid": json}',
        'empty_track': [],
        'negative_money': -100,
        'invalid_race_state': 'INVALID_STATE'
    }


# Test markers for categorization
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "unit: Mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: Mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: Mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "ui: Mark test as UI test"
    )
    config.addinivalue_line(
        "markers", "ui_components: Mark test as UI component test"
    )
    config.addinivalue_line(
        "markers", "ui_panels: Mark test as UI panel test"
    )
    config.addinivalue_line(
        "markers", "ui_integration: Mark test as UI integration test"
    )
    config.addinivalue_line(
        "markers", "slow: Mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "genetics: Mark test as genetics-related"
    )
    config.addinivalue_line(
        "markers", "save_load: Mark test as save/load related"
    )


# Custom assertion helpers
class AssertHelpers:
    """Custom assertion helpers for game testing"""
    
    @staticmethod
    def assert_valid_turtle(turtle):
        """Assert turtle has valid attributes"""
        if not GAME_MODULES_AVAILABLE or Turtle is None:
            pytest.skip("Game modules not available")
            
        assert isinstance(turtle.name, str) and len(turtle.name) > 0
        assert hasattr(turtle, 'stats')
        assert 1.0 <= turtle.stats['speed'] <= 10.0
        assert 50.0 <= turtle.stats['max_energy'] <= 150.0
        assert 0.5 <= turtle.stats['recovery'] <= 5.0
        assert 0.5 <= turtle.stats['swim'] <= 3.0
        assert 0.5 <= turtle.stats['climb'] <= 3.0
        assert 0 <= turtle.age <= 20
        assert isinstance(turtle.is_active, bool)
        assert turtle.current_energy >= 0
        assert turtle.race_distance >= 0
        assert isinstance(turtle.is_resting, bool)
        assert isinstance(turtle.finished, bool)
        assert turtle.rank is None or turtle.rank >= 0
    
    @staticmethod
    def assert_valid_race_result(results):
        """Assert race results are valid"""
        assert isinstance(results, list)
        for result in results:
            assert 'turtle' in result
            assert 'rank' in result
            assert 'time' in result
            assert 1 <= result['rank'] <= len(results)
    
    @staticmethod
    def assert_valid_save_data(data):
        """Assert save data structure is valid"""
        required_keys = ['version', 'money', 'roster', 'retired_roster', 'shop_inventory']
        for key in required_keys:
            assert key in data
        assert isinstance(data['money'], int) and data['money'] >= 0
        assert isinstance(data['roster'], list)
        assert isinstance(data['retired_roster'], list)


class UIAssertHelpers:
    """Custom assertion helpers for UI testing"""
    
    @staticmethod
    def assert_valid_button(button):
        """Assert button has valid attributes"""
        assert hasattr(button, 'text')
        assert hasattr(button, 'action')
        assert hasattr(button, 'rect')
        assert hasattr(button, 'config')
        assert hasattr(button, 'button')  # pygame_gui element
        assert isinstance(button.text, str) and len(button.text) > 0
        assert isinstance(button.action, str) and len(button.action) > 0
        assert isinstance(button.rect, tuple) or hasattr(button.rect, 'x')
        assert isinstance(button.config, dict)
    
    @staticmethod
    def assert_valid_money_display(money_display):
        """Assert money display has valid attributes"""
        assert hasattr(money_display, 'amount')
        assert hasattr(money_display, 'rect')
        assert hasattr(money_display, 'config')
        assert hasattr(money_display, 'label')  # pygame_gui element
        assert isinstance(money_display.amount, (int, float))
        assert money_display.amount >= 0
        assert isinstance(money_display.config, dict)
    
    @staticmethod
    def assert_valid_panel(panel):
        """Assert panel has valid attributes"""
        assert hasattr(panel, 'panel_id')
        assert hasattr(panel, 'title')
        assert hasattr(panel, 'size')
        assert hasattr(panel, 'position')
        assert isinstance(panel.panel_id, str)
        assert isinstance(panel.title, str)
        assert isinstance(panel.size, (tuple, list)) and len(panel.size) == 2
        assert isinstance(panel.position, (tuple, list)) and len(panel.position) == 2
    
    @staticmethod
    def assert_button_layout(buttons, expected_count=None, spacing=None):
        """Assert buttons are laid out correctly"""
        if expected_count is not None:
            assert len(buttons) == expected_count
        
        # Check no overlapping
        for i in range(len(buttons) - 1):
            current = buttons[i]
            next_btn = buttons[i + 1]
            
            if hasattr(current, 'button') and hasattr(next_btn, 'button'):
                current_rect = current.button.rect
                next_rect = next_btn.button.rect
                
                # No vertical overlap
                assert current_rect.bottom <= next_rect.top, f"Buttons {i} and {i+1} overlap"
                
                # Check spacing if specified
                if spacing is not None:
                    actual_spacing = next_rect.top - current_rect.bottom
                    assert abs(actual_spacing - spacing) <= 1, f"Button spacing incorrect: expected {spacing}, got {actual_spacing}"
    
    @staticmethod
    def assert_component_positioning(component, expected_x=None, expected_y=None, expected_size=None):
        """Assert component is positioned correctly"""
        if hasattr(component, 'button'):  # Button component
            rect = component.button.rect
        elif hasattr(component, 'label'):  # MoneyDisplay component
            rect = component.label.rect
        elif hasattr(component, 'window'):  # Panel component
            rect = component.window.rect
        else:
            rect = component.rect
        
        if expected_x is not None:
            assert rect.x == expected_x, f"X position incorrect: expected {expected_x}, got {rect.x}"
        
        if expected_y is not None:
            assert rect.y == expected_y, f"Y position incorrect: expected {expected_y}, got {rect.y}"
        
        if expected_size is not None:
            assert rect.width == expected_size[0], f"Width incorrect: expected {expected_size[0]}, got {rect.width}"
            assert rect.height == expected_size[1], f"Height incorrect: expected {expected_size[1]}, got {rect.height}"
    
    @staticmethod
    def assert_ui_component_visible(component):
        """Assert UI component is visible"""
        if hasattr(component, 'button'):
            assert component.button.visible, "Button not visible"
        elif hasattr(component, 'label'):
            assert component.label.visible, "Label not visible"
        elif hasattr(component, 'window'):
            assert component.window.visible, "Window not visible"


@pytest.fixture
def assert_helpers():
    """Provide assertion helpers"""
    return AssertHelpers()


@pytest.fixture
def ui_assert_helpers():
    """Provide UI assertion helpers"""
    return UIAssertHelpers()


# Performance measurement utilities
class PerformanceTracker:
    """Track performance metrics during tests"""
    
    def __init__(self):
        self.metrics = {}
    
    def start_timer(self, name: str):
        """Start timing an operation"""
        import time
        self.metrics[f"{name}_start"] = time.time()
    
    def end_timer(self, name: str):
        """End timing an operation"""
        import time
        if f"{name}_start" in self.metrics:
            duration = time.time() - self.metrics[f"{name}_start"]
            self.metrics[f"{name}_duration"] = duration
            return duration
        return None
    
    def track_memory(self, name: str):
        """Track memory usage"""
        try:
            import psutil
            process = psutil.Process()
            self.metrics[f"{name}_memory"] = process.memory_info().rss
        except ImportError:
            pass
    
    def get_metric(self, name: str):
        """Get a specific metric"""
        return self.metrics.get(name)
    
    def all_metrics(self) -> Dict:
        """Get all metrics"""
        return self.metrics.copy()


class UIPerformanceTracker(PerformanceTracker):
    """Track UI-specific performance metrics"""
    
    def track_creation_time(self, component_name: str, create_func):
        """Track UI component creation time"""
        self.start_timer(f"{component_name}_creation")
        component = create_func()
        duration = self.end_timer(f"{component_name}_creation")
        return component, duration
    
    def track_render_time(self, component_name: str, render_func):
        """Track UI component render time"""
        self.start_timer(f"{component_name}_render")
        result = render_func()
        duration = self.end_timer(f"{component_name}_render")
        return result, duration
    
    def track_event_handling_time(self, component_name: str, event_func):
        """Track UI component event handling time"""
        self.start_timer(f"{component_name}_events")
        result = event_func()
        duration = self.end_timer(f"{component_name}_events")
        return result, duration


@pytest.fixture
def perf_tracker():
    """Provide performance tracker"""
    return PerformanceTracker()


@pytest.fixture
def ui_perf_tracker():
    """Provide UI performance tracker"""
    return UIPerformanceTracker()


# Mock data factories
class TestDataFactory:
    """Factory for creating test data"""
    
    @staticmethod
    def create_minimal_turtle(name: str = "Minimal"):
        """Create turtle with minimal stats for edge case testing"""
        if not GAME_MODULES_AVAILABLE or Turtle is None:
            pytest.skip("Game modules not available")
        return Turtle(
            name=name,
            speed=1.0,  # Minimum
            energy=50.0,  # Minimum
            recovery=0.5,  # Minimum
            swim=0.5,  # Minimum
            climb=0.5,  # Minimum
        )

    @staticmethod
    def create_extreme_turtle(name: str = "Extreme"):
        """Create turtle with maximum stats for testing"""
        if not GAME_MODULES_AVAILABLE or Turtle is None:
            pytest.skip("Game modules not available")
        return Turtle(
            name=name,
            speed=10.0,  # Maximum
            energy=150.0,  # Maximum
            recovery=5.0,  # Maximum
            swim=3.0,  # Maximum
            climb=3.0,  # Maximum
        )

    @staticmethod
    def create_exhausted_turtle(name: str = "Exhausted"):
        """Create turtle with zero energy for testing recovery"""
        if not GAME_MODULES_AVAILABLE or Turtle is None:
            pytest.skip("Game modules not available")
        turtle = TestDataFactory.create_minimal_turtle(name)
        turtle.current_energy = 0.0
        turtle.is_resting = True
        return turtle


class UITestDataFactory:
    """Factory for creating UI test data"""
    
    @staticmethod
    def create_mock_button(text="Test Button", action="test_action", rect=None):
        """Create mock button for testing"""
        if rect is None:
            rect = pygame.Rect(10, 10, 100, 30) if PYGAME_AVAILABLE else (10, 10, 100, 30)
        
        button = Mock()
        button.text = text
        button.action = action
        button.rect = rect
        button.config = {'style': 'primary'}
        button.button = Mock()
        button.button.visible = True
        button.button.rect = rect
        button.enabled = True
        return button
    
    @staticmethod
    def create_mock_money_display(amount=1000, rect=None):
        """Create mock money display for testing"""
        if rect is None:
            rect = pygame.Rect(10, 10, 150, 25) if PYGAME_AVAILABLE else (10, 10, 150, 25)
        
        display = Mock()
        display.amount = amount
        display.rect = rect
        display.config = {'font_size': 16, 'prefix': '$'}
        display.label = Mock()
        display.label.visible = True
        display.label.rect = rect
        return display
    
    @staticmethod
    def create_mock_panel(panel_id="test_panel", title="Test Panel", size=(400, 300)):
        """Create mock panel for testing"""
        panel = Mock()
        panel.panel_id = panel_id
        panel.title = title
        panel.size = size
        panel.position = (100, 100)
        panel.window = Mock()
        panel.window.visible = True
        panel.window.rect = pygame.Rect(100, 100, size[0], size[1]) if PYGAME_AVAILABLE else Mock()
        return panel
    
    @staticmethod
    def create_mock_event(event_type, **kwargs):
        """Create mock pygame event for testing"""
        event = Mock()
        event.type = event_type
        for key, value in kwargs.items():
            setattr(event, key, value)
        return event


@pytest.fixture
def test_factory():
    """Provide test data factory"""
    return TestDataFactory()


@pytest.fixture
def ui_test_factory():
    """Provide UI test data factory"""
    return UITestDataFactory()
