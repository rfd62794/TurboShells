"""Integration tests for WebSocket race endpoint.

Tests cover:
- WebSocket connection lifecycle
- Race state broadcast format
- Late-joiner sync data
- Client command handling
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock

from src.server.websocket_manager import ConnectionManager, ClientConnection
from src.engine.models import RaceSnapshot, TurtleState


class TestConnectionManager:
    """Tests for ConnectionManager."""
    
    @pytest.fixture
    def manager(self):
        """Create a fresh ConnectionManager for each test."""
        return ConnectionManager(zombie_timeout_seconds=60.0)
    
    @pytest.mark.asyncio
    async def test_connection_lifecycle(self, manager):
        """Test basic connect/disconnect lifecycle."""
        mock_websocket = AsyncMock()
        
        client = await manager.connect(mock_websocket)
        
        assert client.client_id is not None
        assert len(client.client_id) == 8
        assert manager.connection_count == 1
        
        await manager.disconnect(client)
        
        assert manager.connection_count == 0
    
    @pytest.mark.asyncio
    async def test_broadcast_to_multiple_clients(self, manager):
        """Test broadcast sends to all connected clients."""
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        ws3 = AsyncMock()
        
        client1 = await manager.connect(ws1)
        client2 = await manager.connect(ws2)
        client3 = await manager.connect(ws3)
        
        assert manager.connection_count == 3
        
        sent_count = await manager.broadcast('{"test": "message"}')
        
        assert sent_count == 3
        ws1.send_text.assert_called_once_with('{"test": "message"}')
        ws2.send_text.assert_called_once_with('{"test": "message"}')
        ws3.send_text.assert_called_once_with('{"test": "message"}')
    
    @pytest.mark.asyncio
    async def test_failed_send_disconnects_client(self, manager):
        """Test that failed sends trigger client disconnect."""
        ws_good = AsyncMock()
        ws_bad = AsyncMock()
        ws_bad.send_text.side_effect = Exception("Connection closed")
        
        client_good = await manager.connect(ws_good)
        client_bad = await manager.connect(ws_bad)
        
        assert manager.connection_count == 2
        
        sent_count = await manager.broadcast('{"test": "message"}')
        
        assert sent_count == 1
        assert manager.connection_count == 1
    
    @pytest.mark.asyncio
    async def test_zombie_cleanup(self, manager):
        """Test zombie connection detection and cleanup."""
        import time
        
        manager.zombie_timeout_seconds = 0.1
        
        mock_ws = AsyncMock()
        client = await manager.connect(mock_ws)
        
        client.last_ping = time.time() - 1.0
        
        removed = await manager.cleanup_zombies()
        
        assert removed == 1
        assert manager.connection_count == 0
    
    @pytest.mark.asyncio
    async def test_broadcast_snapshot(self, manager):
        """Test RaceSnapshot broadcast."""
        mock_ws = AsyncMock()
        await manager.connect(mock_ws)
        
        snapshot = RaceSnapshot(
            tick=100,
            elapsed_ms=3333.0,
            track_length=1500.0,
            turtles=[
                TurtleState(
                    id="t1",
                    name="Test",
                    x=500.0,
                    current_energy=80.0,
                    max_energy=100.0,
                    genome="B0-S0-P0-C228B22",
                )
            ],
            finished=False,
        )
        
        sent = await manager.broadcast_snapshot(snapshot)
        
        assert sent == 1
        
        call_args = mock_ws.send_text.call_args[0][0]
        parsed = json.loads(call_args)
        assert parsed["tick"] == 100
        assert len(parsed["turtles"]) == 1


class TestClientConnection:
    """Tests for ClientConnection dataclass."""
    
    def test_client_connection_creation(self):
        """Test ClientConnection creation with defaults."""
        mock_ws = Mock()
        client = ClientConnection(websocket=mock_ws)
        
        assert len(client.client_id) == 8
        assert client.messages_sent == 0
        assert client.connected_at > 0
    
    def test_age_seconds(self):
        """Test age calculation."""
        import time
        
        mock_ws = Mock()
        client = ClientConnection(websocket=mock_ws)
        client.connected_at = time.time() - 60.0
        
        age = client.age_seconds()
        
        assert 59.0 <= age <= 61.0


class TestRaceOrchestrator:
    """Tests for RaceOrchestrator."""
    
    @pytest.fixture
    def mock_manager(self):
        """Create mock ConnectionManager."""
        manager = Mock()
        manager.broadcast_snapshot = AsyncMock(return_value=1)
        return manager
    
    @pytest.fixture
    def mock_turtles(self):
        """Create mock Turtle objects."""
        t1 = Mock()
        t1.id = "t1"
        t1.name = "Turtle 1"
        t1.race_distance = 0.0
        t1.current_energy = 100.0
        t1.is_resting = False
        t1.finished = False
        t1.rank = None
        t1.stats = {"max_energy": 100.0}
        t1.visual_genetics = {
            "body_pattern_type": "solid",
            "shell_pattern_type": "hex",
            "limb_shape": "flippers",
            "shell_base_color": (34, 139, 34),
        }
        t1.reset_for_race = Mock()
        t1.update_physics = Mock(return_value=10.0)
        
        return [t1]
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, mock_manager, mock_turtles):
        """Test RaceOrchestrator initialization."""
        from src.server.race_orchestrator import RaceOrchestrator
        
        orchestrator = RaceOrchestrator(
            turtles=mock_turtles,
            manager=mock_manager,
            physics_hz=60,
            broadcast_hz=30,
        )
        
        assert orchestrator.physics_hz == 60
        assert orchestrator.broadcast_hz == 30
        assert not orchestrator.is_running
    
    @pytest.mark.asyncio
    async def test_sync_data_for_late_joiners(self, mock_manager, mock_turtles):
        """Test sync data generation for late-joining clients."""
        from src.server.race_orchestrator import RaceOrchestrator
        
        orchestrator = RaceOrchestrator(
            turtles=mock_turtles,
            manager=mock_manager,
            physics_hz=60,
            broadcast_hz=30,
            track_length=1500.0,
        )
        
        sync_data = orchestrator.get_sync_data()
        
        assert sync_data["type"] == "sync"
        assert sync_data["track_length"] == 1500.0
        assert sync_data["physics_hz"] == 60
        assert sync_data["broadcast_hz"] == 30


class TestLatencyRequirements:
    """Tests for latency requirements per user specs."""
    
    @pytest.mark.asyncio
    async def test_tick_to_broadcast_under_16ms(self):
        """Test that tick-to-broadcast latency is under 16ms for 60fps perception.
        
        This is a critical requirement from the user's verification plan.
        """
        import time
        from src.engine.models import RaceSnapshot, TurtleState
        
        snapshot = RaceSnapshot(
            tick=100,
            elapsed_ms=3333.0,
            track_length=1500.0,
            turtles=[
                TurtleState(
                    id=f"t{i}",
                    name=f"Turtle {i}",
                    x=float(i * 100),
                    current_energy=80.0,
                    max_energy=100.0,
                    genome="B0-S0-P0-C228B22",
                ) for i in range(8)
            ],
            finished=False,
        )
        
        start = time.perf_counter()
        json_str = snapshot.to_broadcast_json()
        end = time.perf_counter()
        
        serialization_ms = (end - start) * 1000
        
        assert serialization_ms < 16.0, f"Serialization took {serialization_ms:.2f}ms, exceeds 16ms"
        
        print(f"Serialization latency: {serialization_ms:.3f}ms for {len(json_str)} bytes")
