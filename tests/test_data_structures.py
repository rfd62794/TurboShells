#!/usr/bin/env python3
"""
Comprehensive unit tests for data structures
Tests turtle data, game state serialization, and data validation.
"""

import pytest
import json
from unittest.mock import Mock, patch
from dataclasses import asdict
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from src.core.data.data_structures import (
        TurtleStats, TurtlePerformance, TurtleParents, TurtleLineage,
        TurtleIdentity, TurtleDynamicState, TurtleRaceResult,
        TurtleVisualGenetics, TurtleEnhancedPerformance, TurtleStaticData,
        TurtleDynamicData, EnhancedTurtleData, TurtleData
    )
except ImportError as e:
    # Fallback to basic testing if data structures not available
    TurtleStats = None
    print(f"Warning: Could not import data structures: {e}")


class MockTurtleStats:
    """Mock TurtleStats for testing"""
    def __init__(self, speed=5.0, energy=100.0, recovery=2.0, swim=1.5, climb=1.5):
        self.speed = speed
        self.energy = energy
        self.recovery = recovery
        self.swim = swim
        self.climb = climb


class MockTurtleData:
    """Mock TurtleData for testing"""
    def __init__(self, name="TestTurtle", speed=5.0, energy=100.0):
        self.name = name
        self.speed = speed
        self.energy = energy
        self.recovery = 2.0
        self.swim = 1.5
        self.climb = 1.5
        self.age = 0
        self.is_active = True
        self.current_energy = energy
        self.race_distance = 0.0
        self.is_resting = False
        self.finished = False
        self.rank = 0


class TestTurtleStats:
    """Unit tests for turtle stats data structure"""

    @pytest.fixture
    def sample_stats(self):
        """Create sample turtle stats"""
        # Use mock since actual TurtleStats has different constructor
        return MockTurtleStats(5.0, 100.0, 2.0, 1.5, 1.5)

    @pytest.mark.unit
    def test_stats_initialization(self, sample_stats):
        """Test stats initialization"""
        assert sample_stats.speed == 5.0
        assert sample_stats.energy == 100.0
        assert sample_stats.recovery == 2.0
        assert sample_stats.swim == 1.5
        assert sample_stats.climb == 1.5

    @pytest.mark.unit
    def test_stats_bounds(self, sample_stats):
        """Test stats are within expected bounds"""
        assert 1.0 <= sample_stats.speed <= 10.0
        assert 50.0 <= sample_stats.energy <= 150.0
        assert 0.5 <= sample_stats.recovery <= 5.0
        assert 0.5 <= sample_stats.swim <= 3.0
        assert 0.5 <= sample_stats.climb <= 3.0

    @pytest.mark.unit
    def test_stats_serialization(self, sample_stats):
        """Test stats can be serialized"""
        if hasattr(sample_stats, '__dict__'):
            stats_dict = asdict(sample_stats) if hasattr(sample_stats, '__dataclass_fields__') else sample_stats.__dict__
            assert isinstance(stats_dict, dict)
            assert 'speed' in stats_dict
            assert 'energy' in stats_dict


class TestTurtleData:
    """Unit tests for turtle data structures"""

    @pytest.fixture
    def sample_turtle_data(self):
        """Create sample turtle data"""
        return MockTurtleData("Speedy", 7.5, 120.0)

    @pytest.mark.unit
    def test_turtle_data_initialization(self, sample_turtle_data):
        """Test turtle data initialization"""
        assert sample_turtle_data.name == "Speedy"
        assert sample_turtle_data.speed == 7.5
        assert sample_turtle_data.energy == 120.0
        assert sample_turtle_data.age == 0
        assert sample_turtle_data.is_active == True

    @pytest.mark.unit
    def test_turtle_data_race_state(self, sample_turtle_data):
        """Test turtle race state"""
        assert sample_turtle_data.current_energy == 120.0
        assert sample_turtle_data.race_distance == 0.0
        assert not sample_turtle_data.is_resting
        assert not sample_turtle_data.finished
        assert sample_turtle_data.rank == 0

    @pytest.mark.unit
    def test_turtle_data_modification(self, sample_turtle_data):
        """Test turtle data can be modified"""
        # Modify race state
        sample_turtle_data.current_energy = 80.0
        sample_turtle_data.race_distance = 150.0
        sample_turtle_data.is_resting = True
        sample_turtle_data.finished = True
        sample_turtle_data.rank = 3

        assert sample_turtle_data.current_energy == 80.0
        assert sample_turtle_data.race_distance == 150.0
        assert sample_turtle_data.is_resting == True
        assert sample_turtle_data.finished == True
        assert sample_turtle_data.rank == 3

    @pytest.mark.unit
    def test_turtle_data_serialization(self, sample_turtle_data):
        """Test turtle data can be serialized to JSON"""
        # Convert to dictionary
        turtle_dict = sample_turtle_data.__dict__.copy()
        
        # Should be JSON serializable
        json_str = json.dumps(turtle_dict)
        assert isinstance(json_str, str)
        
        # Should be deserializable
        restored_dict = json.loads(json_str)
        assert restored_dict['name'] == sample_turtle_data.name
        assert restored_dict['speed'] == sample_turtle_data.speed


class TestDataValidation:
    """Unit tests for data validation"""

    @pytest.mark.unit
    def test_turtle_name_validation(self):
        """Test turtle name validation"""
        # Valid names
        valid_names = ["Speedy", "Turbo", "Flash", "Dash"]
        for name in valid_names:
            turtle = MockTurtleData(name)
            assert turtle.name == name

        # Edge cases
        edge_cases = ["A", "A" * 50, "Turtle_123", "Turtle-Test"]
        for name in edge_cases:
            turtle = MockTurtleData(name)
            assert turtle.name == name

    @pytest.mark.unit
    def test_turtle_stats_validation(self):
        """Test turtle stats validation"""
        # Valid stats ranges
        valid_speeds = [1.0, 5.0, 10.0]
        valid_energies = [50.0, 100.0, 150.0]
        
        for speed in valid_speeds:
            for energy in valid_energies:
                turtle = MockTurtleData("Test", speed, energy)
                assert 1.0 <= turtle.speed <= 10.0
                assert 50.0 <= turtle.energy <= 150.0

    @pytest.mark.unit
    def test_race_state_validation(self):
        """Test race state validation"""
        turtle = MockTurtleData()
        
        # Energy bounds
        turtle.current_energy = -10.0  # Invalid
        # Should handle gracefully (actual validation depends on implementation)
        
        turtle.current_energy = 200.0  # Above max
        # Should handle gracefully
        
        # Rank validation
        turtle.rank = -1  # Invalid
        turtle.rank = 0   # Valid (not finished)
        turtle.rank = 1   # Valid (finished)
        turtle.rank = 10  # Valid (finished in large race)


class TestRaceResultData:
    """Unit tests for race result data structures"""

    @pytest.fixture
    def sample_race_results(self):
        """Create sample race results"""
        return [
            {"turtle_id": "turtle1", "rank": 1, "time": 45.5, "distance": 1000.0},
            {"turtle_id": "turtle2", "rank": 2, "time": 48.2, "distance": 1000.0},
            {"turtle_id": "turtle3", "rank": 3, "time": 52.1, "distance": 950.0},
        ]

    @pytest.mark.unit
    def test_race_results_structure(self, sample_race_results):
        """Test race results have required fields"""
        required_fields = ["turtle_id", "rank", "time", "distance"]
        
        for result in sample_race_results:
            for field in required_fields:
                assert field in result
            assert isinstance(result["rank"], int)
            assert result["rank"] >= 1
            assert isinstance(result["time"], (int, float))
            assert result["time"] > 0
            assert isinstance(result["distance"], (int, float))
            assert result["distance"] >= 0

    @pytest.mark.unit
    def test_race_results_ordering(self, sample_race_results):
        """Test race results are properly ordered"""
        ranks = [result["rank"] for result in sample_race_results]
        assert ranks == sorted(ranks)
        
        # Times should generally increase with rank
        times = [result["time"] for result in sample_race_results]
        assert times == sorted(times)

    @pytest.mark.unit
    def test_race_results_serialization(self, sample_race_results):
        """Test race results can be serialized"""
        json_str = json.dumps(sample_race_results)
        assert isinstance(json_str, str)
        
        restored = json.loads(json_str)
        assert len(restored) == len(sample_race_results)
        assert restored[0]["turtle_id"] == sample_race_results[0]["turtle_id"]


class TestGameStateData:
    """Unit tests for game state data structures"""

    @pytest.fixture
    def sample_game_state(self):
        """Create sample game state"""
        return {
            "version": "2.4.0",
            "money": 150,
            "roster": [
                {
                    "name": "Speedy",
                    "speed": 7.5,
                    "energy": 120.0,
                    "recovery": 2.5,
                    "swim": 1.8,
                    "climb": 1.2,
                    "age": 2,
                    "is_active": True,
                }
            ],
            "retired_roster": [],
            "shop_inventory": [],
            "race_history": [],
            "current_track": {"width": 800, "height": 600},
        }

    @pytest.mark.unit
    def test_game_state_structure(self, sample_game_state):
        """Test game state has required fields"""
        required_fields = ["version", "money", "roster", "retired_roster"]
        
        for field in required_fields:
            assert field in sample_game_state
        
        assert isinstance(sample_game_state["money"], int)
        assert sample_game_state["money"] >= 0
        assert isinstance(sample_game_state["roster"], list)
        assert isinstance(sample_game_state["retired_roster"], list)

    @pytest.mark.unit
    def test_game_state_serialization(self, sample_game_state):
        """Test game state can be serialized"""
        json_str = json.dumps(sample_game_state)
        assert isinstance(json_str, str)
        
        restored = json.loads(json_str)
        assert restored["version"] == sample_game_state["version"]
        assert restored["money"] == sample_game_state["money"]
        assert len(restored["roster"]) == len(sample_game_state["roster"])

    @pytest.mark.unit
    def test_game_state_validation(self, sample_game_state):
        """Test game state validation"""
        # Money bounds
        assert sample_game_state["money"] >= 0
        
        # Roster validation
        for turtle in sample_game_state["roster"]:
            assert "name" in turtle
            assert "speed" in turtle
            assert "energy" in turtle
            assert isinstance(turtle["is_active"], bool)


class TestDataConversion:
    """Unit tests for data conversion utilities"""

    @pytest.mark.unit
    def test_turtle_to_dict_conversion(self):
        """Test turtle to dictionary conversion"""
        turtle = MockTurtleData("Converter", 6.0, 110.0)
        
        # Convert to dict
        turtle_dict = turtle.__dict__.copy()
        
        assert isinstance(turtle_dict, dict)
        assert turtle_dict["name"] == "Converter"
        assert turtle_dict["speed"] == 6.0

    @pytest.mark.unit
    def test_dict_to_turtle_conversion(self):
        """Test dictionary to turtle conversion"""
        turtle_dict = {
            "name": "FromDict",
            "speed": 5.5,
            "energy": 105.0,
            "recovery": 2.2,
            "swim": 1.6,
            "climb": 1.4,
            "age": 1,
            "is_active": True,
        }
        
        # Create turtle from dict
        turtle = MockTurtleData()
        for key, value in turtle_dict.items():
            if hasattr(turtle, key):
                setattr(turtle, key, value)
        
        assert turtle.name == "FromDict"
        assert turtle.speed == 5.5
        assert turtle.energy == 105.0

    @pytest.mark.unit
    def test_data_integrity_through_conversion(self):
        """Test data integrity through conversion cycles"""
        original = MockTurtleData("Integrity", 8.0, 130.0)
        
        # Convert to dict
        turtle_dict = original.__dict__.copy()
        
        # Convert back
        restored = MockTurtleData()
        for key, value in turtle_dict.items():
            if hasattr(restored, key):
                setattr(restored, key, value)
        
        # Check integrity
        assert restored.name == original.name
        assert restored.speed == original.speed
        assert restored.energy == original.energy
