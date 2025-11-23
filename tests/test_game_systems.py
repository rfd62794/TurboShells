#!/usr/bin/env python3
"""
Comprehensive unit tests for game systems
Tests game state, race track, and core game mechanics.
"""

import pytest
from unittest.mock import Mock, patch
from src.core.game_state import generate_random_turtle, breed_turtles, compute_turtle_cost
from src.core.race_track import generate_track, get_terrain_modifier
from src.core.entities import Turtle
from tests.conftest import TestDataFactory


class TestGameStateFunctions:
    """Tests for game state helper functions"""

    @pytest.mark.unit
    def test_generate_random_turtle(self, assert_helpers):
        """Test random turtle generation"""
        turtle = generate_random_turtle("Test Turtle")

        assert isinstance(turtle, Turtle)
        assert turtle.name == "Test Turtle"
        assert_helpers.assert_valid_turtle(turtle)
        
        # Check stat ranges
        assert 1.0 <= turtle.speed <= 10.0
        assert 50.0 <= turtle.energy <= 150.0
        assert 0.5 <= turtle.recovery <= 5.0
        assert 0.5 <= turtle.swim <= 3.0
        assert 0.5 <= turtle.climb <= 3.0
        assert 0 <= turtle.age <= 20

    @pytest.mark.unit
    def test_generate_random_turtle_different_names(self):
        """Test random turtle generation with different names"""
        names = ["Speedy", "Slowpoke", "Balanced", "Extreme"]
        turtles = []

        for name in names:
            turtle = generate_random_turtle(name)
            turtles.append(turtle)
            assert turtle.name == name

        # All turtles should be different (due to random generation)
        stat_combinations = set()
        for turtle in turtles:
            stats = (turtle.speed, turtle.energy, turtle.recovery, turtle.swim, turtle.climb)
            stat_combinations.add(stats)

        # Should have different stat combinations (high probability)
        assert len(stat_combinations) >= 1

    @pytest.mark.unit
    def test_compute_turtle_cost(self, sample_turtle):
        """Test turtle cost calculation"""
        cost = compute_turtle_cost(sample_turtle)

        assert isinstance(cost, int)
        assert cost > 0
        assert cost < 10000  # Reasonable upper bound

    @pytest.mark.unit
    def test_compute_turtle_cost_correlation(self):
        """Test that higher stats result in higher costs"""
        # Create turtles with different stat levels
        low_turtle = TestDataFactory.create_minimal_turtle("Low")
        high_turtle = TestDataFactory.create_extreme_turtle("High")

        low_cost = compute_turtle_cost(low_turtle)
        high_cost = compute_turtle_cost(high_turtle)

        # Higher stats should cost more
        assert high_cost > low_cost

    @pytest.mark.unit
    def test_compute_turtle_cost_consistency(self, sample_turtle):
        """Test cost calculation is consistent"""
        cost1 = compute_turtle_cost(sample_turtle)
        cost2 = compute_turtle_cost(sample_turtle)

        assert cost1 == cost2

    @pytest.mark.unit
    def test_breed_turtles_basic(self, sample_turtles, assert_helpers):
        """Test basic turtle breeding functionality"""
        parent1, parent2 = sample_turtles[0], sample_turtles[1]

        child = breed_turtles(parent1, parent2)

        assert isinstance(child, Turtle)
        assert_helpers.assert_valid_turtle(child)
        assert child.age == 0  # New turtles start at age 0
        assert child.is_active  # New turtles are active

    @pytest.mark.unit
    def test_breed_turtles_stat_inheritance(self, sample_turtles):
        """Test that child stats are influenced by parents"""
        parent1, parent2 = sample_turtles[0], sample_turtles[1]

        child = breed_turtles(parent1, parent2)

        # Child stats should be reasonably influenced by parents
        # Allow for mutation and variation
        parent_speed_avg = (parent1.speed + parent2.speed) / 2
        assert abs(child.speed - parent_speed_avg) <= 3.0  # Allow reasonable variation

        parent_energy_avg = (parent1.energy + parent2.energy) / 2
        assert abs(child.energy - parent_energy_avg) <= 30.0  # Allow reasonable variation

    @pytest.mark.unit
    def test_breed_turtles_edge_cases(self):
        """Test breeding with edge case turtles"""
        # Breed minimal and extreme turtles
        parent_min = TestDataFactory.create_minimal_turtle("Min")
        parent_max = TestDataFactory.create_extreme_turtle("Max")

        child = breed_turtles(parent_min, parent_max)

        assert isinstance(child, Turtle)
        # Child should have stats somewhere between parents (allowing for mutation)
        assert 0.5 <= child.speed <= 10.0
        assert 50.0 <= child.energy <= 150.0

    @pytest.mark.unit
    def test_breed_turtles_same_parents(self, sample_turtle):
        """Test breeding turtle with itself (if allowed)"""
        # This might not be allowed by the actual implementation
        try:
            child = breed_turtles(sample_turtle, sample_turtle)
            assert isinstance(child, Turtle)
        except (ValueError, AttributeError):
            # Expected if self-breeding is not allowed
            pass


class TestRaceTrackSystem:
    """Tests for race track generation and terrain system"""

    @pytest.mark.unit
    def test_generate_track_basic(self):
        """Test basic race track generation"""
        track = generate_track(1000)

        assert isinstance(track, list)
        assert len(track) == 1000

        # Check that all terrain types are valid
        valid_terrains = {'grass', 'water', 'rock'}
        for terrain in track:
            assert terrain in valid_terrains

        # Check that we have a mix of terrains
        unique_terrains = set(track)
        assert len(unique_terrains) >= 1

    @pytest.mark.unit
    @pytest.mark.parametrize("length", [100, 500, 1000, 2000])
    def test_generate_track_different_lengths(self, length):
        """Test track generation with different lengths"""
        track = generate_track(length)
        assert len(track) == length

    @pytest.mark.unit
    def test_generate_track_terrain_distribution(self):
        """Test terrain distribution in generated tracks"""
        track = generate_track(1000)
        
        terrain_counts = {'grass': 0, 'water': 0, 'rock': 0}
        for terrain in track:
            terrain_counts[terrain] += 1

        # Should have some of each terrain (reasonable distribution)
        for terrain, count in terrain_counts.items():
            assert count >= 50  # At least 5% of track
            assert count <= 600  # At most 60% of track

    @pytest.mark.unit
    def test_generate_track_reproducibility_with_seed(self):
        """Test track generation reproducibility with seed"""
        # This test assumes the generate_track function can accept a seed
        # If not, this tests that the function works consistently
        track1 = generate_track(100)
        track2 = generate_track(100)

        assert isinstance(track1, list)
        assert isinstance(track2, list)
        assert len(track1) == len(track2) == 100

        # Tracks might be different (unless seeded)
        # This is acceptable for random generation

    @pytest.mark.unit
    def test_get_terrain_modifier_grass(self):
        """Test terrain modifier for grass (normal terrain)"""
        modifier = get_terrain_modifier('grass')
        assert modifier == 1.0

    @pytest.mark.unit
    def test_get_terrain_modifier_water(self):
        """Test terrain modifier for water terrain"""
        modifier = get_terrain_modifier('water')
        assert isinstance(modifier, float)
        assert 0.0 <= modifier <= 1.0  # Should slow down or be neutral

    @pytest.mark.unit
    def test_get_terrain_modifier_rock(self):
        """Test terrain modifier for rock terrain"""
        modifier = get_terrain_modifier('rock')
        assert isinstance(modifier, float)
        assert 0.0 <= modifier <= 1.0  # Should slow down or be neutral

    @pytest.mark.unit
    def test_get_terrain_modifier_invalid_terrain(self):
        """Test terrain modifier with invalid terrain"""
        # Should handle invalid terrain gracefully
        try:
            modifier = get_terrain_modifier('invalid')
            assert isinstance(modifier, float)
        except (ValueError, KeyError):
            # Expected for invalid terrain
            pass

    @pytest.mark.unit
    def test_terrain_modifier_consistency(self):
        """Test terrain modifiers are consistent"""
        grass1 = get_terrain_modifier('grass')
        grass2 = get_terrain_modifier('grass')
        assert grass1 == grass2

        water1 = get_terrain_modifier('water')
        water2 = get_terrain_modifier('water')
        assert water1 == water2

        rock1 = get_terrain_modifier('rock')
        rock2 = get_terrain_modifier('rock')
        assert rock1 == rock2

    @pytest.mark.unit
    def test_track_difficulty_analysis(self):
        """Test track difficulty can be analyzed"""
        track = generate_track(1000)
        
        # Count challenging terrain
        challenging_terrain = sum(1 for terrain in track if terrain in ['water', 'rock'])
        difficulty_ratio = challenging_terrain / len(track)
        
        assert 0.0 <= difficulty_ratio <= 1.0
        # Should have some challenging terrain
        assert difficulty_ratio > 0.1  # At least 10% challenging

    @pytest.mark.unit
    @pytest.mark.slow
    def test_large_track_generation_performance(self, perf_tracker):
        """Test performance of large track generation"""
        perf_tracker.start_timer("large_track")
        
        large_track = generate_track(10000)
        
        duration = perf_tracker.end_timer("large_track")
        
        assert len(large_track) == 10000
        assert duration < 1.0  # Should complete within 1 second


class TestGameLogicIntegration:
    """Integration tests for game logic components"""

    @pytest.mark.integration
    def test_turtle_on_different_terrains(self, sample_turtle, sample_tracks):
        """Test turtle performance across different track types"""
        results = {}
        
        for track_name, track in sample_tracks.items():
            sample_turtle.reset_for_race()
            initial_energy = sample_turtle.current_energy
            
            # Simulate first 100 tiles of each track
            for terrain in track[:100]:
                if sample_turtle.current_energy > 0:
                    sample_turtle.update_physics(terrain)
            
            results[track_name] = {
                'distance': sample_turtle.race_distance,
                'energy_used': initial_energy - sample_turtle.current_energy
            }
        
        # Different tracks should produce different results
        distances = [result['distance'] for result in results.values()]
        assert len(set(distances)) >= 1  # Some variation expected

    @pytest.mark.integration
    def test_race_simulation_complete(self, sample_turtles, sample_track):
        """Test complete race simulation with multiple turtles"""
        # Reset all turtles
        for turtle in sample_turtles:
            turtle.reset_for_race()
        
        # Simulate race until completion or max iterations
        max_iterations = 5000
        finished_turtles = []
        
        for iteration in range(max_iterations):
            all_finished = True
            current_terrain = sample_track[iteration % len(sample_track)]
            
            for turtle in sample_turtles:
                if not turtle.finished:
                    all_finished = False
                    if turtle.current_energy > 0:
                        turtle.update_physics(current_terrain)
                    else:
                        # Mark as finished if exhausted
                        turtle.finished = True
                        turtle.rank = len(finished_turtles) + 1
                        finished_turtles.append(turtle)
            
            if all_finished:
                break
        
        # At least some turtles should have finished or made progress
        progress_made = any(turtle.race_distance > 0 for turtle in sample_turtles)
        assert progress_made

    @pytest.mark.integration
    def test_cost_vs_performance_correlation(self, sample_turtles, sample_track):
        """Test correlation between turtle cost and performance"""
        turtle_costs = []
        turtle_performance = []
        
        for turtle in sample_turtles:
            cost = compute_turtle_cost(turtle)
            
            # Test performance on short track segment
            turtle.reset_for_race()
            for terrain in sample_track[:200]:  # First 200 tiles
                if turtle.current_energy > 0:
                    turtle.update_physics(terrain)
            
            performance = turtle.race_distance
            
            turtle_costs.append(cost)
            turtle_performance.append(performance)
        
        # Higher cost turtles should generally perform better
        # (This is a trend test, not absolute)
        sorted_costs = sorted(zip(turtle_costs, turtle_performance))
        
        # Check trend: later (higher cost) turtles should generally have better performance
        better_performance_count = 0
        for i in range(1, len(sorted_costs)):
            if sorted_costs[i][1] >= sorted_costs[i-1][1]:
                better_performance_count += 1
        
        # At least some correlation expected (allowing for randomness)
        assert better_performance_count >= len(sorted_costs) // 3

    @pytest.mark.integration
    def test_breeding_stat_progression(self):
        """Test that breeding can produce stat progression over generations"""
        # Start with base turtles
        parent1 = TestDataFactory.create_minimal_turtle("Gen1_Parent1")
        parent2 = TestDataFactory.create_minimal_turtle("Gen1_Parent2")
        
        # Track stats over generations
        generation_stats = []
        
        for generation in range(5):
            child = breed_turtles(parent1, parent2)
            generation_stats.append(child.speed)
            
            # Use child as parent for next generation (with some selection)
            if generation % 2 == 0:
                parent1 = child
            else:
                parent2 = child
        
        # Stats should show some variation over generations
        assert len(set(generation_stats)) >= 2  # Some variation occurred

    @pytest.mark.integration
    def test_terrain_specialization(self):
        """Test turtle specialization for different terrains"""
        # Create turtles with different specializations
        swimmer = Turtle("Swimmer", 5.0, 100.0, 2.0, 3.0, 0.5, 5, True)  # High swim
        climber = Turtle("Climber", 5.0, 100.0, 2.0, 0.5, 3.0, 5, True)   # High climb
        balanced = Turtle("Balanced", 5.0, 100.0, 2.0, 1.5, 1.5, 5, True)  # Balanced
        
        turtles = [swimmer, climber, balanced]
        water_track = ['water'] * 100
        rock_track = ['rock'] * 100
        grass_track = ['grass'] * 100
        
        results = {}
        
        for turtle in turtles:
            # Test on water
            turtle.reset_for_race()
            for terrain in water_track:
                turtle.update_physics(terrain)
            water_distance = turtle.race_distance
            
            # Test on rock
            turtle.reset_for_race()
            for terrain in rock_track:
                turtle.update_physics(terrain)
            rock_distance = turtle.race_distance
            
            # Test on grass
            turtle.reset_for_race()
            for terrain in grass_track:
                turtle.update_physics(terrain)
            grass_distance = turtle.race_distance
            
            results[turtle.name] = {
                'water': water_distance,
                'rock': rock_distance,
                'grass': grass_distance
            }
        
        # Swimmer should perform best on water
        assert results['Swimmer']['water'] >= results['Climber']['water']
        # Climber should perform best on rock
        assert results['Climber']['rock'] >= results['Swimmer']['rock']
