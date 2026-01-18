"""Seed the database with fresh starter turtles.

WARNING: This wipes all existing data!
"""

import sys
import os

# Add root to path so we can import src
sys.path.append(os.getcwd())

from sqlmodel import Session, delete
from src.engine.persistence import engine, TurtleDB, RaceResultDB, init_db
from src.game.entities import Turtle
from src.engine.persistence import turtle_to_db

def seed():
    print("Initializing DB...")
    # Force drop of all tables to ensure schema freshness
    from sqlmodel import SQLModel
    SQLModel.metadata.drop_all(engine)
    init_db()
    
    with Session(engine) as session:
        print("Wiping existing data (Clean Schema)...")
        # No need to delete rows, table was dropped
        # session.exec(delete(RaceResultDB)) 
        # session.exec(delete(TurtleDB))
        # session.commit()
        
        print("Creating starter archetypes...")
        starters = [
            Turtle("Speedster", speed=12, energy=60, recovery=2, swim=5, climb=5),
            Turtle("Tank", speed=8, energy=100, recovery=8, swim=5, climb=5),
            Turtle("Balanced", speed=10, energy=80, recovery=5, swim=5, climb=5),
        ]
        
        for t in starters:
            db_t = turtle_to_db(t)
            session.add(db_t)
            print(f"Created: {t.name}")
            
        session.commit()
        print("Done! Roster reset.")

if __name__ == "__main__":
    seed()
