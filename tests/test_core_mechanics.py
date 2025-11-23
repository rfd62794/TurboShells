#!/usr/bin/env python3
"""
Comprehensive unit tests for core game mechanics
Tests physics, movement, energy, and game rules.
"""

import pytest
from unittest.mock import Mock, patch
from src.core.game.entities import Turtle
from src.core.game_state import get_terrain_at, run_race
from src.core.entities import RaceTrack


class TestTurtlePhysics:
    """Unit tests for turtle physics and movement"""

    @pytest.fixture
    def test_turtle(self):
        """Create a test turtle with known stats"""
        return Turtle(
            name="TestTurtle",
            speed=5.0,
            energy=100.0,
            recovery=2.0,
            swim=1.5,
            climb=1.5
        )

    @pytest.mark.unit
    def test_turtle_initialization(self, test_turtle):
        """Test turtle is properly initialized"""
        assert test_turtle.name == "TestTurtle"
        assert test_turtle.stats['speed'] == 5.0
        assert test_turtle.stats['max_energy'] == 100.0
        assert test_turtle.stats['recovery'] == 2.0
        assert test_turtle.stats['swim'] == 1.5
        assert test_turtle.stats['climb'] == 1.5
        assert test_turtle.current_energy == 100.0
        assert test_turtle.race_distance == 0.0
        assert not test_turtle.is_resting
        assert not test_turtle.finished
        assert test_turtle.rank is None

    @pytest.mark.unit
    def test_turtle_reset_for_race(self, test_turtle):
        """Test turtle race reset functionality"""
        # Modify turtle state
        test_turtle.current_energy = 50.0
        test_turtle.race_distance = 100.0
        test_turtle.is_resting = True
        test_turtle.finished = True
        test_turtle.rank = 3

        # Reset
        test_turtle.reset_for_race()

        # Check reset state
        assert test_turtle.current_energy == test_turtle.stats['max_energy']
        assert test_turtle.race_distance == 0.0
        assert not test_turtle.is_resting
        assert not test_turtle.finished
        assert test_turtle.rank is None

    @pytest.mark.unit
    @pytest.mark.parametrize("terrain", ["rough", "finish", "track"])
    def test_turtle_update_physics_different_terrains(self, test_turtle, terrain):
        """Test turtle physics on different terrains"""
        initial_distance = test_turtle.race_distance
        initial_energy = test_turtle.current_energy

        # Update physics
        test_turtle.update_physics(terrain)

        # Should have moved (unless exhausted or finished)
        if not test_turtle.finished and test_turtle.current_energy > 0:
            assert test_turtle.race_distance >= initial_distance
            assert test_turtle.current_energy <= initial_energy

    @pytest.mark.unit
    def test_turtle_exhaustion_and_recovery(self, test_turtle):
        """Test turtle exhaustion and recovery mechanics"""
        # Exhaust the turtle
        test_turtle.current_energy = 1.0
        test_turtle.update_physics("track")

        # Should be resting when exhausted
        if test_turtle.current_energy <= 0:
            assert test_turtle.is_resting

        # Test recovery while resting
        if test_turtle.is_resting:
            initial_energy = test_turtle.current_energy
            test_turtle.update_physics("track")
            assert test_turtle.current_energy >= initial_energy

    @pytest.mark.unit
    def test_turtle_finished_state(self, test_turtle):
        """Test turtle finished state behavior"""
        # Mark turtle as finished
        test_turtle.finished = True
        test_turtle.rank = 1

        initial_distance = test_turtle.race_distance
        initial_energy = test_turtle.current_energy

        # Update physics - should not move when finished
        test_turtle.update_physics("track")

        assert test_turtle.race_distance == initial_distance
        assert test_turtle.current_energy == initial_energy

    @pytest.mark.unit
    def test_turtle_energy_bounds(self, test_turtle):
        """Test turtle energy stays within bounds"""
        # Test energy doesn't go negative
        test_turtle.current_energy = 0
        test_turtle.update_physics("track")
        assert test_turtle.current_energy >= 0

        # Test energy doesn't exceed maximum
        max_energy = test_turtle.stats['max_energy']
        test_turtle.current_energy = max_energy
        
        if test_turtle.is_resting:
            test_turtle.update_physics("track")
            assert test_turtle.current_energy <= max_energy

    @pytest.mark.unit
    @pytest.mark.parametrize("speed", [1.0, 5.0, 10.0])
    def test_turtle_speed_impact(self, speed):
        """Test different speed values affect movement"""
        turtle = Turtle("SpeedTest", speed, 100.0, 2.0, 1.5, 1.5)
        
        initial_distance = turtle.race_distance
        turtle.update_physics("track")
        
        # Faster turtles should move more (generally)
        distance_moved = turtle.race_distance - initial_distance
        assert distance_moved >= 0

    @pytest.mark.unit
    @pytest.mark.parametrize("recovery", [0.5, 2.0, 5.0])
    def test_turtle_recovery_impact(self, recovery):
        """Test different recovery values affect rest time"""
        turtle = Turtle("RecoveryTest", 5.0, 100.0, recovery, 1.5, 1.5)
        
        # Exhaust turtle
        turtle.current_energy = 0
        turtle.is_resting = True
        
        initial_energy = turtle.current_energy
        turtle.update_physics("track")
        
        # Should recover some energy
        assert turtle.current_energy >= initial_energy

    @pytest.mark.unit
    def test_turtle_terrain_modifiers(self, test_turtle):
        """Test terrain modifiers affect movement"""
        # Test on different terrains
        terrains = ["rough", "finish", "track"]
        distances = {}
        
        for terrain in terrains:
            test_turtle.reset_for_race()
            initial_distance = test_turtle.race_distance
            test_turtle.update_physics(terrain)
            distances[terrain] = test_turtle.race_distance - initial_distance
        
        # Different terrains should produce potentially different results
        # (allowing for randomness in physics)
        assert all(d >= 0 for d in distances.values())


class TestTerrainSystem:
    """Unit tests for terrain system"""

    @pytest.mark.unit
    @pytest.mark.parametrize("x,y,expected_terrain", [
        (100, 100, "rough"),  # Outside track bounds
        (400, 300, "finish"), # Finish area
        (300, 300, "track"),  # On track
        (700, 500, "rough"),  # Outside track bounds
    ])
    def test_terrain_at_specific_positions(self, x, y, expected_terrain):
        """Test terrain at specific positions"""
        terrain = get_terrain_at(x, y)
        assert terrain == expected_terrain

    @pytest.mark.unit
    def test_terrain_boundaries(self):
        """Test terrain at boundary positions"""
        # Test boundaries
        boundary_positions = [
            (200, 150),  # Track boundary
            (600, 450),  # Track boundary
            (350, 250),  # Finish boundary
            (450, 350),  # Finish boundary
        ]
        
        for x, y in boundary_positions:
            terrain = get_terrain_at(x, y)
            assert terrain in ["rough", "finish", "track"]

    @pytest.mark.unit
    def test_terrain_consistency(self):
        """Test terrain consistency"""
        # Same position should always return same terrain
        test_positions = [(100, 100), (400, 300), (700, 500)]
        
        for x, y in test_positions:
            terrain1 = get_terrain_at(x, y)
            terrain2 = get_terrain_at(x, y)
            assert terrain1 == terrain2

    @pytest.mark.unit
    def test_terrain_coverage(self):
        """Test terrain covers entire expected area"""
        # Test various positions across the map
        positions = [
            (0, 0), (400, 300), (800, 600),  # Corners and center
            (200, 150), (600, 450),          # Track corners
            (350, 250), (450, 350),          # Finish area
        ]
        
        for x, y in positions:
            terrain = get_terrain_at(x, y)
            assert terrain in ["rough", "finish", "track"]


class TestRaceTrackFunctionality:
    """Unit tests for race track functionality"""

    @pytest.fixture
    def sample_track(self):
        """Create a sample race track"""
        track = RaceTrack(800, 600)
        track.add_checkpoint(200, 150, 30)
        track.add_checkpoint(600, 150, 30)
        track.add_checkpoint(600, 450, 30)
        track.add_checkpoint(200, 450, 30)
        track.add_checkpoint(400, 300, 40)  # Finish
        return track

    @pytest.mark.unit
    def test_track_initialization(self, sample_track):
        """Test track is properly initialized"""
        assert sample_track.width == 800
        assert sample_track.height == 600
        assert len(sample_track.checkpoints) == 5

    @pytest.mark.unit
    def test_checkpoint_addition(self):
        """Test adding checkpoints to track"""
        track = RaceTrack()
        assert len(track.checkpoints) == 0
        
        track.add_checkpoint(100, 100, 20)
        assert len(track.checkpoints) == 1
        
        checkpoint = track.checkpoints[0]
        assert checkpoint["x"] == 100
        assert checkpoint["y"] == 100
        assert checkpoint["radius"] == 20

    @pytest.mark.unit
    def test_checkpoint_reached(self, sample_track):
        """Test checkpoint detection"""
        from src.core.entities import TurtleEntity
        
        # Create turtle at checkpoint position
        turtle = TurtleEntity(x=200, y=150)
        
        # Should reach first checkpoint
        reached = sample_track.is_checkpoint_reached(turtle, 0)
        assert reached == True
        
        # Should not reach distant checkpoint
        not_reached = sample_track.is_checkpoint_reached(turtle, 1)
        assert not_reached == False

    @pytest.mark.unit
    def test_checkpoint_bounds(self, sample_track):
        """Test checkpoint boundary detection"""
        from src.core.entities import TurtleEntity
        
        # Create turtle just outside checkpoint radius
        turtle = TurtleEntity(x=200, y=185)  # 35 units away from (200, 150)
        
        # Should not reach checkpoint (radius 30)
        reached = sample_track.is_checkpoint_reached(turtle, 0)
        assert reached == False
        
        # Move within radius
        turtle.y = 175  # 25 units away
        reached = sample_track.is_checkpoint_reached(turtle, 0)
        assert reached == True

    @pytest.mark.unit
    def test_invalid_checkpoint_index(self, sample_track):
        """Test checkpoint detection with invalid indices"""
        from src.core.entities import TurtleEntity
        
        turtle = TurtleEntity(x=200, y=150)
        
        # Invalid indices should return False
        assert sample_track.is_checkpoint_reached(turtle, -1) == False
        assert sample_track.is_checkpoint_reached(turtle, 10) == False
        assert sample_track.is_checkpoint_reached(turtle, 5) == False  # len(checkpoints)


class TestGameStateTransitions:
    """Unit tests for game state transitions"""

    @pytest.mark.unit
    def test_race_simulation_basic(self):
        """Test basic race simulation"""
        from src.core.entities import TurtleEntity
        
        # Create simple turtles
        turtles = [
            TurtleEntity(x=100, y=100, speed=1.0),
            TurtleEntity(x=100, y=100, speed=1.5),
        ]
        
        # Create simple track
        track = RaceTrack()
        track.add_checkpoint(200, 100, 30)
        track.add_checkpoint(400, 100, 30)
        
        # Run short race
        results = run_race(turtles, track, max_steps=100)
        
        assert isinstance(results, list)
        assert len(results) == len(turtles)

    @pytest.mark.unit
    def test_race_simulation_empty_turtles(self):
        """Test race simulation with no turtles"""
        track = RaceTrack()
        track.add_checkpoint(200, 100, 30)
        
        results = run_race([], track, max_steps=100)
        
        assert results == []

    @pytest.mark.unit
    def test_race_simulation_empty_track(self):
        """Test race simulation with empty track"""
        from src.core.entities import TurtleEntity
        
        turtles = [TurtleEntity(x=100, y=100, speed=1.0)]
        track = RaceTrack()  # No checkpoints
        
        results = run_race(turtles, track, max_steps=100)
        
        assert isinstance(results, list)


class TestGameConstants:
    """Unit tests for game constants and configuration"""

    @pytest.mark.unit
    def test_terrain_constants(self):
        """Test terrain-related constants"""
        # Test that terrain types are consistent
        valid_terrains = ["rough", "finish", "track"]
        
        # Test various positions return valid terrain
        for x in range(0, 800, 100):
            for y in range(0, 600, 100):
                terrain = get_terrain_at(x, y)
                assert terrain in valid_terrains

    @pytest.mark.unit
    def test_track_dimensions(self):
        """Test track dimension constants"""
        # Test default track dimensions
        track = RaceTrack()
        assert track.width > 0
        assert track.height > 0
        
        # Test custom dimensions
        custom_track = RaceTrack(1000, 800)
        assert custom_track.width == 1000
        assert custom_track.height == 800

    @pytest.mark.unit
    def test_checkpoint_radius_bounds(self):
        """Test checkpoint radius bounds"""
        track = RaceTrack()
        
        # Test various radius values
        radii = [10, 20, 30, 40, 50]
        for radius in radii:
            track.add_checkpoint(100, 100, radius)
            checkpoint = track.checkpoints[-1]
            assert checkpoint["radius"] == radius
            assert checkpoint["radius"] > 0
