
"""
Unit tests for the SQLite persistence layer.
Focuses on session lifecycle management and "DetachedInstanceError" prevention.
"""
import pytest
import os
from sqlmodel import SQLModel, create_engine, Session, select
from src.engine.persistence import TurtleDB, RaceResultDB, turtle_to_db

# Use in-memory SQLite for tests
TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture(name="engine")
def fixture_engine():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture(name="session")
def fixture_session(engine):
    # CRITICAL: Replicate the expire_on_commit=False setting from production
    # This is what we are verifying!
    with Session(engine, expire_on_commit=False) as session:
        yield session

def test_turtle_creation(session):
    """Verify we can create and persist a turtle."""
    turtle = TurtleDB(
        turtle_id="test-1",
        name="TestTurtle",
        speed=10.0,
        genome="B0-S0-P0-C228B22"
    )
    session.add(turtle)
    session.commit()
    session.refresh(turtle)

    assert turtle.id is not None
    assert turtle.name == "TestTurtle"

def test_detached_session_guard(engine):
    """
    The 'Stability Test':
    Verify that TurtleDB objects remain valid after the session closes.
    This confirms `expire_on_commit=False` is working.
    """
    # 1. Setup data in a separate scope
    with Session(engine, expire_on_commit=False) as session:
        turtle = TurtleDB(
            turtle_id="detached-1",
            name="DetachedTurtle",
            speed=50.0,
            genome="B0-S0-P0-C228B22"
        )
        session.add(turtle)
        session.commit()
        session.refresh(turtle)
        turtle_id = turtle.id

    # 2. Fetch the object and CLOSE the session explicitly
    turtle_obj = None
    with Session(engine, expire_on_commit=False) as session:
        stmt = select(TurtleDB).where(TurtleDB.id == turtle_id)
        turtle_obj = session.exec(stmt).first()
        # Session closes here upon exit
    
    # 3. Access properties AFTER session is closed
    # If expire_on_commit=True (default), this would raise DetachedInstanceError
    assert turtle_obj is not None
    assert turtle_obj.name == "DetachedTurtle"
    assert turtle_obj.speed == 50.0
    # Access a property that wasn't explicitly touched above to ensure it's loaded
    assert turtle_obj.genome == "B0-S0-P0-C228B22" 

def test_race_result_persistence(session):
    """Verify saving race results."""
    # Setup turtle
    turtle = TurtleDB(turtle_id="racer-1", name="Racer", genome="G")
    session.add(turtle)
    session.commit()

    # Save result
    result = RaceResultDB(
        race_id="race-123",
        turtle_id=turtle.id,
        rank=1,
        final_distance=1000.0,
        final_time_ms=5000.0,
        speed_at_race=turtle.speed
    )
    session.add(result)
    session.commit()
    session.refresh(result)

    assert result.id is not None
    assert result.rank == 1
    assert result.turtle_id == turtle.id
