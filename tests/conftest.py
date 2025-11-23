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

# Import game modules for fixtures
from src.core.entities import Turtle
from src.core.game_state import generate_random_turtle, breed_turtles, compute_turtle_cost, generate_track, get_terrain_at
from tests.mock_data_generator import MockDataGenerator


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Provide test data directory path"""
    return Path(__file__).parent / "test_data"


@pytest.fixture(scope="session")
def mock_generator():
    """Provide mock data generator with fixed seed"""
    return MockDataGenerator(seed=42)


@pytest.fixture
def sample_turtle_data(mock_generator):
    """Provide sample turtle data for testing"""
    return mock_generator.generate_turtle()


@pytest.fixture
def sample_turtle(sample_turtle_data):
    """Provide a sample Turtle instance"""
    return Turtle(
        name=sample_turtle_data.name,
        speed=sample_turtle_data.speed,
        energy=sample_turtle_data.energy,
        recovery=sample_turtle_data.recovery,
        swim=sample_turtle_data.swim,
        climb=sample_turtle_data.climb,
        age=sample_turtle_data.age,
        is_active=sample_turtle_data.is_active
    )


@pytest.fixture
def sample_turtles(mock_generator):
    """Provide multiple sample turtles for testing"""
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
    def assert_valid_turtle(turtle: Turtle):
        """Assert turtle has valid attributes"""
        assert isinstance(turtle.name, str) and len(turtle.name) > 0
        assert 1.0 <= turtle.speed <= 10.0
        assert 50.0 <= turtle.energy <= 150.0
        assert 0.5 <= turtle.recovery <= 5.0
        assert 0.5 <= turtle.swim <= 3.0
        assert 0.5 <= turtle.climb <= 3.0
        assert 0 <= turtle.age <= 20
        assert isinstance(turtle.is_active, bool)
        assert turtle.current_energy >= 0
        assert turtle.race_distance >= 0
        assert isinstance(turtle.is_resting, bool)
        assert isinstance(turtle.finished, bool)
        assert turtle.rank >= 0
    
    @staticmethod
    def assert_valid_race_result(results: List[Dict]):
        """Assert race results are valid"""
        assert isinstance(results, list)
        for result in results:
            assert 'turtle' in result
            assert 'rank' in result
            assert 'time' in result
            assert 1 <= result['rank'] <= len(results)
    
    @staticmethod
    def assert_valid_save_data(data: Dict):
        """Assert save data structure is valid"""
        required_keys = ['version', 'money', 'roster', 'retired_roster', 'shop_inventory']
        for key in required_keys:
            assert key in data
        assert isinstance(data['money'], int) and data['money'] >= 0
        assert isinstance(data['roster'], list)
        assert isinstance(data['retired_roster'], list)


@pytest.fixture
def assert_helpers():
    """Provide assertion helpers"""
    return AssertHelpers()


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


@pytest.fixture
def perf_tracker():
    """Provide performance tracker"""
    return PerformanceTracker()


# Mock data factories
class TestDataFactory:
    """Factory for creating test data"""
    
    @staticmethod
    def create_extreme_turtle(name: str = "Extreme") -> Turtle:
        """Create turtle with extreme stats for edge case testing"""
        return Turtle(
            name=name,
            speed=10.0,  # Maximum
            energy=150.0,  # Maximum
            recovery=5.0,  # Maximum
            swim=3.0,  # Maximum
            climb=3.0,  # Maximum
            age=20,  # Maximum
            is_active=True
        )
    
    @staticmethod
    def create_minimal_turtle(name: str = "Minimal") -> Turtle:
        """Create turtle with minimal stats for edge case testing"""
        return Turtle(
            name=name,
            speed=1.0,  # Minimum
            energy=50.0,  # Minimum
            recovery=0.5,  # Minimum
            swim=0.5,  # Minimum
            climb=0.5,  # Minimum
            age=0,  # Minimum
            is_active=True
        )
    
    @staticmethod
    def create_exhausted_turtle(name: str = "Exhausted") -> Turtle:
        """Create exhausted turtle for testing recovery mechanics"""
        turtle = TestDataFactory.create_minimal_turtle(name)
        turtle.current_energy = 1.0
        turtle.is_resting = True
        return turtle


@pytest.fixture
def test_factory():
    """Provide test data factory"""
    return TestDataFactory()
