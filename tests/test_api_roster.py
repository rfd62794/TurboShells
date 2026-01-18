
"""
Integration tests for the Roster API.
Ensures the API contract is maintained and JSON serialization works correctly,
validating that no lazy-load errors occur during response model validation.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select

from src.server.app import app
from src.engine.persistence import TurtleDB, get_engine
from src.server.routes.roster import TurtleResponse

from sqlmodel.pool import StaticPool

# --- Test Database Setup ---
# We override the dependency or database engine for tests
TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture(name="engine")
def fixture_engine():
    engine = create_engine(
        TEST_DB_URL, 
        connect_args={"check_same_thread": False}, 
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture(name="client")
def fixture_client(engine):
    # Dependency override or monkeypatching might be needed if the app uses
    # a global engine. For now, we'll monkeypatch src.engine.persistence.engine
    # CAUTION: This affects the global state for the duration of the test run.
    import src.engine.persistence
    original_engine = src.engine.persistence.engine
    src.engine.persistence.engine = engine
    
    # Also override the get_session used in routes if it relies on the global engine
    # fortunately get_session uses the global engine variable, so patching it works.
    
    with TestClient(app) as client:
        yield client
    
    # Restore
    src.engine.persistence.engine = original_engine

@pytest.fixture
def sample_turtle(engine):
    with Session(engine, expire_on_commit=False) as session:
        turtle = TurtleDB(
            turtle_id="api-test-1",
            name="API Turtle",
            speed=12.5,
            genome="B0-S0-P0-C228B22"
        )
        session.add(turtle)
        session.commit()
    return turtle

def test_list_turtles(client, sample_turtle):
    """
    GET /api/turtles
    Verifies that the endpoint returns 200 and the correct JSON structure.
    Implicitly tests that model_validate works without DetachedInstanceError.
    """
    response = client.get("/api/turtles")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    
    t = data[0]
    assert t["name"] == "API Turtle"
    assert t["turtle_id"] == "api-test-1"
    # Verify a computed or defaulted field
    assert "total_wins" in t
    assert t["genome"] == "B0-S0-P0-C228B22"

def test_get_turtle_by_id(client, sample_turtle):
    """GET /api/turtles/{id}"""
    response = client.get(f"/api/turtles/{sample_turtle.turtle_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "API Turtle"

def test_get_turtle_not_found(client):
    """GET /api/turtles/{id} - 404"""
    response = client.get("/api/turtles/non-existent-id")
    assert response.status_code == 404

def test_create_turtle(client):
    """POST /api/turtles"""
    payload = {
        "name": "New Born",
        "speed": 15.0,
        "max_energy": 80.0,
        "genome": "B1-S1-P1-C123456"
    }
    response = client.post("/api/turtles", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Born"
    assert data["speed"] == 15.0
    assert "turtle_id" in data
