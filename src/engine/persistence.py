"""SQLite Persistence Layer for TurboShells.

Maps existing Pydantic models to SQLModel tables for persistent storage.
This gives the simulation "memory" across browser sessions.

Tables:
    TurtleDB: Core turtle entity with stats and genome
    RaceResultDB: Historical race results for analytics
    
Usage:
    from src.engine.persistence import init_db, get_session, TurtleDB
    
    init_db()  # Create tables
    with get_session() as session:
        turtle = TurtleDB(name="Speedy", genome="B0-S0-P0-C228B22", ...)
        session.add(turtle)
        session.commit()
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from contextlib import contextmanager

from sqlmodel import Field, Session, SQLModel, create_engine

from src.engine.logging_config import get_logger

logger = get_logger(__name__)

# Database configuration
DATABASE_URL = "sqlite:///turboshells.db"
engine = create_engine(DATABASE_URL, echo=False)


class TurtleDB(SQLModel, table=True):
    """Persistent turtle entity.
    
    Maps to the in-memory Turtle class from src/game/entities.py.
    Stores the "DNA" that persists across races.
    """
    __tablename__ = "turtles"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    turtle_id: str = Field(index=True, unique=True, description="UUID from Turtle.id")
    name: str = Field(index=True)
    
    # Core stats (the "DNA")
    speed: float = Field(default=10.0)
    max_energy: float = Field(default=100.0)
    recovery: float = Field(default=5.0)
    swim: float = Field(default=5.0)
    climb: float = Field(default=5.0)
    stamina: float = Field(default=0.0)
    luck: float = Field(default=0.0)
    
    # Visual genetics (Paper Doll genome string)
    genome: str = Field(default="B0-S0-P0-C228B22")
    
    # Metadata
    age: int = Field(default=0)
    is_active: bool = Field(default=True)
    generation: int = Field(default=0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Aggregate stats (updated after each race)
    total_races: int = Field(default=0)
    total_wins: int = Field(default=0)
    total_earnings: int = Field(default=0)


class RaceResultDB(SQLModel, table=True):
    """Historical race result for analytics.
    
    Stores the outcome of each race for performance graphs.
    """
    __tablename__ = "race_history"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    race_id: str = Field(index=True, description="Unique race identifier")
    
    # Turtle reference (FK only, no ORM relationship for simplicity)
    turtle_db_id: Optional[int] = Field(default=None, foreign_key="turtles.id")
    
    # Race outcome
    rank: int = Field(description="Finishing position (1-indexed)")
    final_distance: float = Field(description="Distance traveled")
    final_time_ms: float = Field(description="Time to finish in milliseconds")
    finished: bool = Field(default=True)
    
    # Snapshot of stats at race time
    speed_at_race: float = Field(default=0.0)
    energy_at_race: float = Field(default=0.0)
    
    # Timestamp
    raced_at: datetime = Field(default_factory=datetime.utcnow)


def init_db() -> None:
    """Initialize database and create all tables."""
    SQLModel.metadata.create_all(engine)
    if logger:
        logger.info("Database initialized", url=DATABASE_URL)


def get_engine():
    """Get the database engine."""
    return engine


@contextmanager
def get_session():
    """Get a database session context manager."""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def turtle_to_db(turtle) -> TurtleDB:
    """Convert an in-memory Turtle to a TurtleDB record.
    
    Args:
        turtle: Turtle instance from src/game/entities.py
        
    Returns:
        TurtleDB instance ready for persistence
    """
    from src.engine.genome_codec import GenomeCodec
    
    genome = GenomeCodec.encode(turtle.visual_genetics)
    
    return TurtleDB(
        turtle_id=turtle.id,
        name=turtle.name,
        speed=turtle.stats["speed"],
        max_energy=turtle.stats["max_energy"],
        recovery=turtle.stats["recovery"],
        swim=turtle.stats["swim"],
        climb=turtle.stats["climb"],
        stamina=turtle.stats.get("stamina", 0),
        luck=turtle.stats.get("luck", 0),
        genome=genome,
        age=turtle.age,
        is_active=turtle.is_active,
        generation=turtle.generation,
        total_races=turtle.total_races,
        total_earnings=turtle.total_earnings,
    )


def db_to_turtle(db_turtle: TurtleDB):
    """Convert a TurtleDB record to an in-memory Turtle.
    
    Args:
        db_turtle: TurtleDB instance from database
        
    Returns:
        Turtle instance for the RaceEngine
    """
    from src.game.entities import Turtle
    from src.engine.genome_codec import GenomeCodec
    
    # Decode genome to visual genetics dict
    genetics = GenomeCodec.decode(db_turtle.genome)
    
    turtle = Turtle(
        name=db_turtle.name,
        speed=db_turtle.speed,
        energy=db_turtle.max_energy,
        recovery=db_turtle.recovery,
        swim=db_turtle.swim,
        climb=db_turtle.climb,
        stamina=db_turtle.stamina,
        luck=db_turtle.luck,
        genetics=genetics,
    )
    
    # Restore non-constructor fields
    turtle.id = db_turtle.turtle_id
    turtle.age = db_turtle.age
    turtle.is_active = db_turtle.is_active
    turtle.generation = db_turtle.generation
    turtle.total_races = db_turtle.total_races
    turtle.total_earnings = db_turtle.total_earnings
    
    return turtle


def save_race_result(
    race_id: str,
    turtle,
    rank: int,
    final_distance: float,
    final_time_ms: float,
    finished: bool = True,
) -> None:
    """Save a race result to the database.
    
    Args:
        race_id: Unique race identifier
        turtle: Turtle instance that participated
        rank: Finishing position
        final_distance: Distance traveled
        final_time_ms: Time to finish
        finished: Whether turtle crossed finish line
    """
    with get_session() as session:
        # Find or create turtle in DB
        from sqlmodel import select
        
        stmt = select(TurtleDB).where(TurtleDB.turtle_id == turtle.id)
        db_turtle = session.exec(stmt).first()
        
        if not db_turtle:
            db_turtle = turtle_to_db(turtle)
            session.add(db_turtle)
            session.commit()
            session.refresh(db_turtle)
        
        # Create race result
        result = RaceResultDB(
            race_id=race_id,
            turtle_id=db_turtle.id,
            rank=rank,
            final_distance=final_distance,
            final_time_ms=final_time_ms,
            finished=finished,
            speed_at_race=turtle.stats["speed"],
            energy_at_race=turtle.stats["max_energy"],
        )
        session.add(result)
        
        # Update turtle aggregate stats
        db_turtle.total_races += 1
        if rank == 1:
            db_turtle.total_wins += 1
        db_turtle.updated_at = datetime.utcnow()
        
        if logger:
            logger.info(
                "Race result saved",
                race_id=race_id,
                turtle_name=turtle.name,
                rank=rank,
            )


def get_all_turtles() -> list[TurtleDB]:
    """Fetch all turtles from the database."""
    with get_session() as session:
        from sqlmodel import select
        stmt = select(TurtleDB).where(TurtleDB.is_active == True)
        return list(session.exec(stmt).all())


def get_turtle_by_id(turtle_id: str) -> Optional[TurtleDB]:
    """Fetch a turtle by its UUID."""
    with get_session() as session:
        from sqlmodel import select
        stmt = select(TurtleDB).where(TurtleDB.turtle_id == turtle_id)
        return session.exec(stmt).first()
