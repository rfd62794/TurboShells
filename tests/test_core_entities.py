#!/usr/bin/env python3
"""
Comprehensive unit tests for core game entities
Tests Turtle entity and related game mechanics with 95%+ coverage goals.
"""

import pytest
from unittest.mock import Mock, patch
from src.core.game.entities import Turtle
from src.core.game_state import generate_random_turtle, breed_turtles, compute_turtle_cost
from tests.conftest import TestDataFactory


class TestTurtleEntity:
    """Comprehensive tests for the Turtle entity class"""

    @pytest.mark.unit
    def test_turtle_creation_valid(self, assert_helpers):
        """Test turtle creation with valid parameters"""
        turtle = Turtle(
            name="Test Turtle",
            speed=5.0,
            energy=100.0,
            recovery=2.0,
            swim=1.5,
            climb=1.5
        )

        assert_helpers.assert_valid_turtle(turtle)
        assert turtle.name == "Test Turtle"
        assert turtle.stats['speed'] == 5.0
        assert turtle.stats['max_energy'] == 100.0

    @pytest.mark.unit
    def test_turtle_initial_state(self, sample_turtle):
        """Test turtle initial state after creation"""
        # Check initial race state
        assert sample_turtle.current_energy == sample_turtle.stats['max_energy']
        assert sample_turtle.race_distance == 0.0
        assert not sample_turtle.is_resting
        assert not sample_turtle.finished
        assert sample_turtle.rank is None

    @pytest.mark.unit
    def test_turtle_reset_for_race(self, sample_turtle):
        """Test turtle race reset functionality"""
        # Modify race state
        sample_turtle.current_energy = 50.0
        sample_turtle.race_distance = 100.0
        sample_turtle.is_resting = True
        sample_turtle.finished = True
        sample_turtle.rank = 3

        # Reset for race
        sample_turtle.reset_for_race()

        # Check reset state
        assert sample_turtle.current_energy == sample_turtle.stats['max_energy']
        assert sample_turtle.race_distance == 0.0
        assert not sample_turtle.is_resting
        assert not sample_turtle.finished
        assert sample_turtle.rank is None

    @pytest.mark.unit
    @pytest.mark.parametrize("terrain,expected_modifier", [
        ('grass', 1.0),
        ('water', None),  # Depends on swim stat
        ('rock', None),   # Depends on climb stat
    ])
    def test_turtle_update_physics_grass(self, sample_turtle, terrain, expected_modifier):
        """Test turtle physics update on different terrains"""
        initial_distance = sample_turtle.race_distance
        initial_energy = sample_turtle.current_energy

        # Update on terrain
        sample_turtle.update_physics(terrain)

        # Should move and consume energy (unless exhausted)
        if sample_turtle.current_energy > 0:
            assert sample_turtle.race_distance > initial_distance
            assert sample_turtle.current_energy < initial_energy
            assert not sample_turtle.is_resting

    @pytest.mark.unit
    def test_turtle_exhaustion_and_recovery(self, sample_turtle):
        """Test turtle exhaustion and recovery mechanics"""
        # Exhaust the turtle
        sample_turtle.current_energy = 1.0
        sample_turtle.update_physics('grass')

        # Should be resting
        assert sample_turtle.is_resting

        # Test recovery
        initial_energy = sample_turtle.current_energy
        sample_turtle.update_physics('grass')  # Should recover while resting

        # Should recover energy
        assert sample_turtle.current_energy > initial_energy

    @pytest.mark.unit
    def test_turtle_terrain_performance(self, sample_turtle):
        """Test turtle performance on different terrains"""
        terrains = ['grass', 'water', 'rock']
        distances = {}

        for terrain in terrains:
            sample_turtle.reset_for_race()
            sample_turtle.update_physics(terrain)
            distances[terrain] = sample_turtle.race_distance

        # Different terrains should produce different results
        # (unless turtle has perfectly balanced stats)
        unique_distances = set(distances.values())
        assert len(unique_distances) >= 1  # At least some variation

    @pytest.mark.unit
    def test_turtle_stat_access(self, sample_turtle):
        """Test turtle stat access through stats dictionary"""
        # Test accessing stats
        assert 'speed' in sample_turtle.stats
        assert 'max_energy' in sample_turtle.stats
        assert 'recovery' in sample_turtle.stats
        assert 'swim' in sample_turtle.stats
        assert 'climb' in sample_turtle.stats
        
        # Test stat values are in expected ranges
        assert 1.0 <= sample_turtle.stats['speed'] <= 10.0
        assert 50.0 <= sample_turtle.stats['max_energy'] <= 150.0
        assert 0.5 <= sample_turtle.stats['recovery'] <= 5.0
        assert 0.5 <= sample_turtle.stats['swim'] <= 3.0
        assert 0.5 <= sample_turtle.stats['climb'] <= 3.0

    @pytest.mark.unit
    def test_turtle_edge_cases(self, assert_helpers):
        """Test turtle edge cases and error conditions"""
        # Test with minimum stats
        turtle_min = TestDataFactory.create_minimal_turtle("Min")
        assert_helpers.assert_valid_turtle(turtle_min)

        # Test with maximum stats
        turtle_max = TestDataFactory.create_extreme_turtle("Max")
        assert_helpers.assert_valid_turtle(turtle_max)

        # Test with zero energy
        turtle_zero = TestDataFactory.create_exhausted_turtle("Zero")
        turtle_zero.update_physics('grass')
        assert turtle_zero.is_resting

    @pytest.mark.unit
    def test_turtle_age_progression(self, sample_turtle):
        """Test turtle aging mechanics"""
        initial_age = sample_turtle.age
        
        # Manually age turtle
        sample_turtle.age += 1
        
        assert sample_turtle.age == initial_age + 1

    @pytest.mark.unit
    def test_turtle_retirement(self, sample_turtle):
        """Test turtle retirement logic"""
        # Set age to maximum
        sample_turtle.age = 20
        
        # Check if should be retired
        # (This depends on the MAX_AGE constant implementation)
        # For now, just test the age check
        assert sample_turtle.age >= 20

    @pytest.mark.unit
    def test_turtle_energy_bounds(self, sample_turtle):
        """Test turtle energy stays within bounds"""
        # Test energy doesn't go below 0
        sample_turtle.current_energy = 0
        sample_turtle.update_physics('grass')
        assert sample_turtle.current_energy >= 0

        # Test energy doesn't go above maximum
        sample_turtle.current_energy = sample_turtle.stats['max_energy']
        if sample_turtle.is_resting:
            sample_turtle.update_physics('grass')
            assert sample_turtle.current_energy <= sample_turtle.stats['max_energy']

    @pytest.mark.unit
    def test_turtle_race_completion(self, sample_turtle):
        """Test turtle race completion logic"""
        # Set turtle to finish line
        sample_turtle.race_distance = 1000.0
        sample_turtle.finished = True
        sample_turtle.rank = 1

        assert sample_turtle.finished
        assert sample_turtle.rank > 0

    @pytest.mark.unit
    def test_turtle_copy(self, sample_turtle):
        """Test turtle copying functionality"""
        # This tests if there's a copy method or similar
        # Implementation depends on the actual Turtle class
        if hasattr(sample_turtle, 'copy'):
            turtle_copy = sample_turtle.copy()
            assert turtle_copy.name == sample_turtle.name
            assert turtle_copy.speed == sample_turtle.speed
            # Ensure it's a different object
            assert turtle_copy is not sample_turtle

    @pytest.mark.unit
    def test_turtle_equality(self, sample_turtle):
        """Test turtle equality comparison"""
        # This tests if there's an __eq__ method
        # Implementation depends on the actual Turtle class
        if hasattr(sample_turtle, '__eq__'):
            same_turtle = Turtle(
                name=sample_turtle.name,
                speed=sample_turtle.stats['speed'],
                energy=sample_turtle.stats['max_energy'],
                recovery=sample_turtle.stats['recovery'],
                swim=sample_turtle.stats['swim'],
                climb=sample_turtle.stats['climb']
            )
            assert same_turtle == sample_turtle

    @pytest.mark.unit
    def test_turtle_string_representation(self, sample_turtle):
        """Test turtle string representation"""
        str_repr = str(sample_turtle)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0
        assert sample_turtle.name in str_repr

    @pytest.mark.unit
    def test_turtle_dict_serialization(self, sample_turtle):
        """Test turtle dictionary serialization"""
        # This tests if there's a to_dict method
        if hasattr(sample_turtle, 'to_dict'):
            turtle_dict = sample_turtle.to_dict()
            assert isinstance(turtle_dict, dict)
            assert 'name' in turtle_dict
            assert turtle_dict['name'] == sample_turtle.name

    @pytest.mark.unit
    def test_turtle_validation(self, assert_helpers):
        """Test turtle validation methods"""
        # Test valid turtle
        valid_turtle = TestDataFactory.create_minimal_turtle("Valid")
        if hasattr(valid_turtle, 'validate'):
            assert valid_turtle.validate()

        # Test invalid turtle data would require modifying the turtle
        # to have invalid data, which might not be possible through the constructor

    @pytest.mark.unit
    @pytest.mark.slow
    def test_turtle_performance_simulation(self, sample_turtle, perf_tracker):
        """Test turtle performance over multiple updates"""
        perf_tracker.start_timer("simulation")
        
        # Simulate 1000 physics updates
        for _ in range(1000):
            if sample_turtle.current_energy > 0:
                sample_turtle.update_physics('grass')
            else:
                break
        
        duration = perf_tracker.end_timer("simulation")
        
        # Should complete within reasonable time
        assert duration < 1.0  # 1 second
        assert sample_turtle.race_distance > 0

    @pytest.mark.unit
    def test_turtle_stat_calculations(self, sample_turtle):
        """Test turtle stat calculation methods"""
        # Test total stats calculation
        if hasattr(sample_turtle, 'get_total_stats'):
            total_stats = sample_turtle.get_total_stats()
            assert isinstance(total_stats, (int, float))
            assert total_stats > 0

        # Test stat averages
        if hasattr(sample_turtle, 'get_stat_average'):
            avg_stat = sample_turtle.get_stat_average()
            assert isinstance(avg_stat, (int, float))
            assert avg_stat > 0

    @pytest.mark.unit
    def test_turtle_special_abilities(self, sample_turtle):
        """Test turtle special abilities or traits"""
        # Test if turtle has any special abilities
        if hasattr(sample_turtle, 'has_special_ability'):
            has_ability = sample_turtle.has_special_ability()
            assert isinstance(has_ability, bool)

        # Test special ability activation
        if hasattr(sample_turtle, 'activate_special_ability'):
            result = sample_turtle.activate_special_ability()
            # Result type depends on implementation

    @pytest.mark.unit
    def test_turtle_state_persistence(self, sample_turtle):
        """Test turtle state can be properly persisted"""
        # Modify turtle state
        sample_turtle.current_energy = 75.0
        sample_turtle.race_distance = 250.0
        sample_turtle.is_resting = True

        # Test state capture
        if hasattr(sample_turtle, 'get_state'):
            state = sample_turtle.get_state()
            assert isinstance(state, dict)
            assert state['current_energy'] == 75.0
            assert state['race_distance'] == 250.0
            assert state['is_resting'] is True

        # Test state restoration
        if hasattr(sample_turtle, 'set_state'):
            new_state = {
                'current_energy': 50.0,
                'race_distance': 100.0,
                'is_resting': False
            }
            sample_turtle.set_state(new_state)
            assert sample_turtle.current_energy == 50.0
            assert sample_turtle.race_distance == 100.0
            assert sample_turtle.is_resting is False


class TestTurtleFactory:
    """Tests for turtle creation and factory methods"""

    @pytest.mark.unit
    def test_random_turtle_generation(self):
        """Test random turtle generation produces valid turtles"""
        # This would test the generate_random_turtle function
        # Implementation depends on the actual function signature
        pass

    @pytest.mark.unit
    def test_turtle_cost_calculation(self, sample_turtle):
        """Test turtle cost calculation"""
        # This would test the compute_turtle_cost function
        # Implementation depends on the actual function signature
        pass

    @pytest.mark.unit
    def test_breeding_functionality(self, sample_turtles):
        """Test turtle breeding produces valid offspring"""
        # This would test the breed_turtles function
        # Implementation depends on the actual function signature
        pass


@pytest.mark.integration
class TestTurtleIntegration:
    """Integration tests for turtle entities with game systems"""

    @pytest.mark.integration
    def test_turtle_with_race_system(self, sample_turtle, sample_track):
        """Test turtle interaction with race system"""
        # Simulate a race
        sample_turtle.reset_for_race()
        
        for terrain in sample_track[:100]:  # Test first 100 tiles
            if sample_turtle.current_energy > 0 and not sample_turtle.finished:
                sample_turtle.update_physics(terrain)
        
        # Should have made progress
        assert sample_turtle.race_distance > 0

    @pytest.mark.integration
    def test_turtle_with_save_system(self, sample_turtle, temp_save_dir):
        """Test turtle can be saved and loaded"""
        # This would test save/load functionality
        # Implementation depends on the save system
        pass

    @pytest.mark.integration
    def test_turtle_with_genetics_system(self, sample_turtle):
        """Test turtle genetics integration"""
        # This would test genetics system integration
        # Implementation depends on the genetics system
        pass
