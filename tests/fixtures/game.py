"""
Game logic and data fixtures.

This module contains fixtures related to game entities, state,
and core game mechanics.
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
from tests.utils import TestDataFactory, AssertHelpers

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
def sample_track():
    """Provide sample race track for testing"""
    if not GAME_MODULES_AVAILABLE:
        pytest.skip("Game modules not available")
    return generate_track(1000)


@pytest.fixture
def sample_tracks():
    """Provide multiple sample tracks with different lengths"""
    if not GAME_MODULES_AVAILABLE:
        pytest.skip("Game modules not available")
    return {
        'short': generate_track(500),
        'medium': generate_track(1000),
        'long': generate_track(1500)
    }


@pytest.fixture
def terrain_functions():
    """Provide terrain function test data"""
    if not GAME_MODULES_AVAILABLE:
        pytest.skip("Game modules not available")
    return {
        'get_terrain_at': get_terrain_at,
        'test_positions': [(100, 100), (400, 300), (700, 500)]
    }


@pytest.fixture
def breeding_scenarios(mock_generator):
    """Provide breeding scenario test data"""
    if not GAME_MODULES_AVAILABLE:
        pytest.skip("Game modules not available")
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
def assert_helpers():
    """Provide assertion helpers"""
    return AssertHelpers()


@pytest.fixture
def test_factory():
    """Provide test data factory"""
    return TestDataFactory()
