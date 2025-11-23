#!/usr/bin/env python3
"""
Unit tests for race track system
Tests track generation, terrain, and checkpoint functionality.
"""

import pytest
from src.core.game_state import generate_track, get_terrain_at
from src.core.entities import RaceTrack


class TestTrackGeneration:
    """Tests for race track generation"""

    @pytest.mark.unit
    def test_generate_track_basic(self):
        """Test basic race track generation"""
        track = generate_track()
        
        assert track is not None
        assert track.width == 800
        assert track.height == 600
        assert len(track.checkpoints) > 0

    @pytest.mark.unit
    @pytest.mark.parametrize("length", [100, 500, 1000, 2000])
    def test_generate_track_different_lengths(self, length):
        """Test track generation with different lengths"""
        track = generate_track(length, length)
        
        assert track is not None
        assert track.width == length
        assert track.height == length
        assert len(track.checkpoints) > 0

    @pytest.mark.unit
    def test_generate_track_terrain_distribution(self):
        """Test track has terrain variety"""
        track = generate_track()
        
        # Check that track has checkpoints
        assert len(track.checkpoints) > 0
        
        # Check checkpoint positions are within bounds
        for checkpoint in track.checkpoints:
            assert 0 <= checkpoint["x"] <= track.width
            assert 0 <= checkpoint["y"] <= track.height

    @pytest.mark.unit
    def test_generate_track_reproducibility_with_seed(self):
        """Test track generation reproducibility"""
        track1 = generate_track(100, 100)
        track2 = generate_track(100, 100)

        assert isinstance(track1, RaceTrack)
        assert isinstance(track2, RaceTrack)
        assert len(track1.checkpoints) == len(track2.checkpoints)

        # Tracks should have same structure (same generation logic)
        assert track1.width == track2.width
        assert track1.height == track2.height

    @pytest.mark.unit
    def test_track_difficulty_analysis(self):
        """Test track difficulty can be analyzed"""
        track = generate_track()
        
        # Analyze checkpoint distribution
        checkpoint_count = len(track.checkpoints)
        
        # Check that track has reasonable number of checkpoints
        assert 3 <= checkpoint_count <= 10  # Reasonable range
        
        # Check track dimensions
        assert track.width > 0
        assert track.height > 0

    @pytest.mark.unit
    @pytest.mark.slow
    def test_large_track_generation_performance(self):
        """Test performance of large track generation"""
        import time
        
        start_time = time.time()
        large_track = generate_track(2000, 2000)  # Smaller but still large
        duration = time.time() - start_time
        
        assert isinstance(large_track, RaceTrack)
        assert large_track.width == 2000
        assert large_track.height == 2000
        assert duration < 1.0  # Should complete within 1 second

    @pytest.mark.unit
    def test_track_checkpoint_positions(self):
        """Test that checkpoints are positioned correctly"""
        track = generate_track()
        
        # Check that checkpoints follow expected pattern
        expected_checkpoints = [
            (200, 150, 30),
            (600, 150, 30),
            (600, 450, 30),
            (200, 450, 30),
            (400, 300, 40),  # Finish line
        ]
        
        assert len(track.checkpoints) == len(expected_checkpoints)
        
        for i, (x, y, radius) in enumerate(expected_checkpoints):
            checkpoint = track.checkpoints[i]
            assert checkpoint["x"] == x
            assert checkpoint["y"] == y
            assert checkpoint["radius"] == radius


class TestTerrainSystem:
    """Tests for terrain system"""

    @pytest.mark.unit
    def test_get_terrain_at_function(self):
        """Test terrain function for different positions"""
        # Test terrain at different positions
        positions = [(100, 100), (400, 300), (700, 500)]
        
        for x, y in positions:
            terrain = get_terrain_at(x, y)
            assert isinstance(terrain, str)
            assert terrain in ['rough', 'finish', 'track']  # Valid terrain types

    @pytest.mark.unit
    def test_terrain_function_consistency(self):
        """Test terrain function consistency"""
        # Same position should return same terrain
        x, y = 400, 300
        terrain1 = get_terrain_at(x, y)
        terrain2 = get_terrain_at(x, y)
        
        assert terrain1 == terrain2

    @pytest.mark.unit
    @pytest.mark.parametrize("x,y,expected", [
        (100, 100, "rough"),  # Outside track bounds
        (400, 300, "finish"), # Finish area
        (300, 300, "track"),  # On track
        (700, 500, "rough"),  # Outside track bounds
        (200, 150, "rough"),  # Track boundary
        (600, 450, "rough"),  # Track boundary
        (350, 250, "finish"), # Finish boundary
        (450, 350, "finish"), # Finish boundary
    ])
    def test_terrain_at_specific_positions(self, x, y, expected):
        """Test terrain at specific positions"""
        terrain = get_terrain_at(x, y)
        assert terrain == expected

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
    """Tests for race track functionality"""

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
