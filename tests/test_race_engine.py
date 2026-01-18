"""Unit tests for the headless RaceEngine.

Tests cover:
- RaceEngine initialization and configuration
- Tick-based simulation determinism
- TurtleState serialization/deserialization
- GenomeCodec round-trip encoding
- Race completion detection and winner determination
"""

import pytest
from unittest.mock import Mock, patch

from src.engine.models import TurtleState, RaceSnapshot, RaceConfig, TerrainSegment
from src.engine.genome_codec import GenomeCodec


class TestTurtleState:
    """Tests for TurtleState Pydantic model."""

    @pytest.mark.unit
    def test_turtle_state_creation(self):
        """Test basic TurtleState creation."""
        state = TurtleState(
            id="abc123",
            name="Test Turtle",
            x=150.5,
            y=40.0,
            angle=0.0,
            current_energy=80.0,
            max_energy=100.0,
            is_resting=False,
            finished=False,
            rank=None,
            genome="B0-S0-P0-C228B22",
        )
        
        assert state.id == "abc123"
        assert state.name == "Test Turtle"
        assert state.x == 150.5
        assert state.current_energy == 80.0
        assert not state.finished
    
    @pytest.mark.unit
    def test_turtle_state_json_serialization(self):
        """Test TurtleState JSON serialization."""
        state = TurtleState(
            id="test",
            name="Speedy",
            x=100.0,
            current_energy=50.0,
            max_energy=100.0,
            genome="B1-S2-P0-CFF0000",
        )
        
        json_str = state.model_dump_json()
        
        assert '"id":"test"' in json_str
        assert '"name":"Speedy"' in json_str
        assert '"x":100.0' in json_str
    
    @pytest.mark.unit
    def test_turtle_state_frozen(self):
        """Test TurtleState is immutable (frozen)."""
        state = TurtleState(
            id="test",
            name="Test",
            x=0.0,
            current_energy=100.0,
            max_energy=100.0,
            genome="B0-S0-P0-C228B22",
        )
        
        with pytest.raises(Exception):
            state.x = 50.0


class TestRaceSnapshot:
    """Tests for RaceSnapshot Pydantic model."""
    
    @pytest.mark.unit
    def test_race_snapshot_creation(self):
        """Test basic RaceSnapshot creation."""
        turtle_state = TurtleState(
            id="t1",
            name="Turtle 1",
            x=250.0,
            current_energy=75.0,
            max_energy=100.0,
            genome="B0-S0-P0-C228B22",
        )
        
        snapshot = RaceSnapshot(
            tick=100,
            elapsed_ms=3333.33,
            track_length=1500.0,
            turtles=[turtle_state],
            finished=False,
            winner_id=None,
        )
        
        assert snapshot.tick == 100
        assert len(snapshot.turtles) == 1
        assert not snapshot.finished
    
    @pytest.mark.unit
    def test_race_snapshot_broadcast_json(self):
        """Test optimized broadcast JSON serialization."""
        snapshot = RaceSnapshot(
            tick=50,
            elapsed_ms=1666.66,
            track_length=1500.0,
            turtles=[],
            finished=False,
        )
        
        json_str = snapshot.to_broadcast_json()
        
        assert '"tick":50' in json_str
        assert '"finished":false' in json_str
        assert '"winner_id"' not in json_str


class TestGenomeCodec:
    """Tests for genome encoding/decoding."""
    
    @pytest.mark.unit
    def test_encode_default_genetics(self):
        """Test encoding default genetics."""
        genetics = {
            "body_pattern_type": "solid",
            "shell_pattern_type": "hex",
            "limb_shape": "flippers",
            "shell_base_color": (34, 139, 34),
        }
        
        genome = GenomeCodec.encode(genetics)
        
        assert genome == "B0-S0-P0-C228B22"
    
    @pytest.mark.unit
    def test_encode_varied_genetics(self):
        """Test encoding varied genetics."""
        genetics = {
            "body_pattern_type": "mottled",
            "shell_pattern_type": "spots",
            "limb_shape": "fins",
            "shell_base_color": (255, 0, 255),
        }
        
        genome = GenomeCodec.encode(genetics)
        
        assert genome == "B1-S1-P2-CFF00FF"
    
    @pytest.mark.unit
    def test_decode_genome(self):
        """Test decoding genome string."""
        genome = "B2-S3-P1-C00FF00"
        
        genetics = GenomeCodec.decode(genome)
        
        assert genetics["body_pattern_type"] == "speckled"
        assert genetics["shell_pattern_type"] == "rings"
        assert genetics["limb_shape"] == "feet"
        assert genetics["shell_base_color"] == (0, 255, 0)
    
    @pytest.mark.unit
    def test_roundtrip_encoding(self):
        """Test genome encoding/decoding round-trip."""
        original = {
            "body_pattern_type": "marbled",
            "shell_pattern_type": "stripes",
            "limb_shape": "feet",
            "shell_base_color": (100, 150, 200),
        }
        
        genome = GenomeCodec.encode(original)
        decoded = GenomeCodec.decode(genome)
        
        assert decoded["body_pattern_type"] == original["body_pattern_type"]
        assert decoded["shell_pattern_type"] == original["shell_pattern_type"]
        assert decoded["limb_shape"] == original["limb_shape"]
        assert decoded["shell_base_color"] == original["shell_base_color"]
    
    @pytest.mark.unit
    def test_encode_missing_keys(self):
        """Test encoding with missing genetics keys uses defaults."""
        genetics = {}
        
        genome = GenomeCodec.encode(genetics)
        
        assert genome.startswith("B0-S0-P0-C")
    
    @pytest.mark.unit
    def test_decode_malformed_genome(self):
        """Test decoding handles malformed input gracefully."""
        malformed = "INVALID-GENOME-STRING"
        
        genetics = GenomeCodec.decode(malformed)
        
        assert isinstance(genetics, dict)


class TestRaceConfig:
    """Tests for RaceConfig model."""
    
    @pytest.mark.unit
    def test_default_config(self):
        """Test default race configuration."""
        config = RaceConfig()
        
        assert config.track_length == 1500.0
        assert config.tick_rate == 30
        assert config.max_ticks == 5000
    
    @pytest.mark.unit
    def test_custom_config(self):
        """Test custom race configuration."""
        config = RaceConfig(
            track_length=2000.0,
            tick_rate=60,
            max_ticks=10000,
        )
        
        assert config.track_length == 2000.0
        assert config.tick_rate == 60
    
    @pytest.mark.unit
    def test_config_validation(self):
        """Test config validation constraints."""
        with pytest.raises(Exception):
            RaceConfig(track_length=-100)
        
        with pytest.raises(Exception):
            RaceConfig(tick_rate=0)


class TestTerrainSegment:
    """Tests for TerrainSegment model."""
    
    @pytest.mark.unit
    def test_terrain_segment_creation(self):
        """Test terrain segment creation."""
        segment = TerrainSegment(
            start_distance=100.0,
            end_distance=200.0,
            terrain_type="water",
        )
        
        assert segment.start_distance == 100.0
        assert segment.terrain_type == "water"
    
    @pytest.mark.unit
    def test_terrain_type_validation(self):
        """Test terrain type literal validation."""
        with pytest.raises(Exception):
            TerrainSegment(
                start_distance=0.0,
                end_distance=100.0,
                terrain_type="invalid_terrain",
            )


class TestRaceEngine:
    """Integration tests for RaceEngine."""
    
    @pytest.fixture
    def mock_turtles(self):
        """Create mock Turtle objects for testing."""
        turtle1 = Mock()
        turtle1.id = "t1"
        turtle1.name = "Turtle 1"
        turtle1.race_distance = 0.0
        turtle1.current_energy = 100.0
        turtle1.is_resting = False
        turtle1.finished = False
        turtle1.rank = None
        turtle1.stats = {"max_energy": 100.0}
        turtle1.visual_genetics = {
            "body_pattern_type": "solid",
            "shell_pattern_type": "hex",
            "limb_shape": "flippers",
            "shell_base_color": (34, 139, 34),
        }
        turtle1.reset_for_race = Mock()
        turtle1.update_physics = Mock(return_value=10.0)
        
        turtle2 = Mock()
        turtle2.id = "t2"
        turtle2.name = "Turtle 2"
        turtle2.race_distance = 0.0
        turtle2.current_energy = 100.0
        turtle2.is_resting = False
        turtle2.finished = False
        turtle2.rank = None
        turtle2.stats = {"max_energy": 100.0}
        turtle2.visual_genetics = {
            "body_pattern_type": "mottled",
            "shell_pattern_type": "spots",
            "limb_shape": "feet",
            "shell_base_color": (255, 0, 0),
        }
        turtle2.reset_for_race = Mock()
        turtle2.update_physics = Mock(return_value=8.0)
        
        return [turtle1, turtle2]
    
    @pytest.mark.unit
    def test_engine_initialization(self, mock_turtles):
        """Test RaceEngine initialization."""
        from src.engine.race_engine import RaceEngine
        
        engine = RaceEngine(turtles=mock_turtles)
        
        assert len(engine.turtles) == 2
        assert engine.current_tick == 0
        assert not engine.is_finished()
        assert engine.get_winner() is None
    
    @pytest.mark.unit
    def test_engine_tick_produces_snapshot(self, mock_turtles):
        """Test single tick produces valid snapshot."""
        from src.engine.race_engine import RaceEngine
        
        engine = RaceEngine(turtles=mock_turtles)
        snapshot = engine.tick()
        
        assert isinstance(snapshot, RaceSnapshot)
        assert snapshot.tick == 1
        assert len(snapshot.turtles) == 2
    
    @pytest.mark.unit
    def test_engine_snapshot_serializable(self, mock_turtles):
        """Test snapshot can be JSON serialized."""
        from src.engine.race_engine import RaceEngine
        
        engine = RaceEngine(turtles=mock_turtles)
        snapshot = engine.tick()
        
        json_str = snapshot.to_broadcast_json()
        
        assert isinstance(json_str, str)
        assert '"tick":1' in json_str
    
    @pytest.mark.unit
    def test_engine_standings(self, mock_turtles):
        """Test engine provides ordered standings."""
        from src.engine.race_engine import RaceEngine
        
        mock_turtles[0].race_distance = 500.0
        mock_turtles[1].race_distance = 300.0
        
        engine = RaceEngine(turtles=mock_turtles)
        standings = engine.get_standings()
        
        assert standings[0].race_distance >= standings[1].race_distance
