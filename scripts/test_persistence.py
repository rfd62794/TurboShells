"""Test script for persistence layer verification."""

from src.engine.persistence import init_db, TurtleDB, RaceResultDB, get_session
import uuid

print("Testing persistence layer...")

# Initialize database
init_db()
print("✅ Database initialized")

# Test session
with get_session() as session:
    print("✅ Session works")
    
    # Create test turtle
    turtle = TurtleDB(
        turtle_id=str(uuid.uuid4())[:8],
        name="Test Turtle",
        speed=10.0,
        max_energy=100.0,
        recovery=5.0,
        swim=5.0,
        climb=5.0,
        genome="B1-S2-P0-CFF0000",
    )
    session.add(turtle)
    session.commit()
    session.refresh(turtle)
    print(f"✅ Created turtle: {turtle.name} (id: {turtle.turtle_id})")

# Verify persistence
from sqlmodel import select
with get_session() as session:
    stmt = select(TurtleDB)
    turtles = session.exec(stmt).all()
    print(f"✅ Found {len(turtles)} turtle(s) in database")

print("\n✅ Persistence layer verified!")
