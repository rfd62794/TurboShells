"""REST API routes for turtle roster and race history.

Provides endpoints for persistent data access:
    GET /api/turtles - Fetch all turtles
    GET /api/turtles/{id} - Fetch single turtle
    POST /api/turtles - Create new turtle
    GET /api/history - Fetch race history
"""

from __future__ import annotations

from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.engine.persistence import (
    init_db,
    get_all_turtles,
    get_turtle_by_id,
    get_session,
    TurtleDB,
    RaceResultDB,
)
from src.engine.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["roster"])


# Pydantic response models
class TurtleResponse(BaseModel):
    """Turtle data for API response."""
    id: int
    turtle_id: str
    name: str
    speed: float
    max_energy: float
    recovery: float
    swim: float
    climb: float
    genome: str
    total_races: int
    total_wins: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class TurtleCreateRequest(BaseModel):
    """Request to create a new turtle."""
    name: str
    speed: float = 10.0
    max_energy: float = 100.0
    recovery: float = 5.0
    swim: float = 5.0
    climb: float = 5.0
    genome: str = "B0-S0-P0-C228B22"


class RaceResultResponse(BaseModel):
    """Race result for API response."""
    id: int
    race_id: str
    turtle_name: str
    rank: int
    final_distance: float
    final_time_ms: float
    raced_at: datetime


@router.on_event("startup")
async def startup():
    """Initialize database on server startup."""
    init_db()
    if logger:
        logger.info("Database initialized via API startup")


@router.get("/turtles", response_model=list[TurtleResponse])
async def list_turtles():
    """Fetch all active turtles from the roster."""
    turtles = get_all_turtles()
    return [TurtleResponse.model_validate(t) for t in turtles]


@router.get("/turtles/{turtle_id}", response_model=TurtleResponse)
async def get_turtle(turtle_id: str):
    """Fetch a single turtle by UUID."""
    turtle = get_turtle_by_id(turtle_id)
    if not turtle:
        raise HTTPException(status_code=404, detail="Turtle not found")
    return TurtleResponse.model_validate(turtle)


@router.post("/turtles", response_model=TurtleResponse)
async def create_turtle(request: TurtleCreateRequest):
    """Create a new turtle in the roster."""
    import uuid
    
    with get_session() as session:
        turtle = TurtleDB(
            turtle_id=str(uuid.uuid4())[:8],
            name=request.name,
            speed=request.speed,
            max_energy=request.max_energy,
            recovery=request.recovery,
            swim=request.swim,
            climb=request.climb,
            genome=request.genome,
        )
        session.add(turtle)
        session.commit()
        session.refresh(turtle)
        
        if logger:
            logger.info("Turtle created", name=turtle.name, id=turtle.turtle_id)
        
        return TurtleResponse.model_validate(turtle)


@router.get("/history", response_model=list[RaceResultResponse])
async def list_race_history(limit: int = 50):
    """Fetch recent race history."""
    with get_session() as session:
        from sqlmodel import select
        
        stmt = (
            select(RaceResultDB, TurtleDB.name)
            .join(TurtleDB)
            .order_by(RaceResultDB.raced_at.desc())
            .limit(limit)
        )
        results = session.exec(stmt).all()
        
        return [
            RaceResultResponse(
                id=result[0].id,
                race_id=result[0].race_id,
                turtle_name=result[1],
                rank=result[0].rank,
                final_distance=result[0].final_distance,
                final_time_ms=result[0].final_time_ms,
                raced_at=result[0].raced_at,
            )
            for result in results
        ]


@router.get("/stats/{turtle_id}")
async def get_turtle_stats(turtle_id: str):
    """Get performance statistics for a turtle."""
    turtle = get_turtle_by_id(turtle_id)
    if not turtle:
        raise HTTPException(status_code=404, detail="Turtle not found")
    
    with get_session() as session:
        from sqlmodel import select, func
        
        # Get race history stats
        stmt = (
            select(
                func.count(RaceResultDB.id).label("total_races"),
                func.avg(RaceResultDB.rank).label("avg_rank"),
                func.min(RaceResultDB.final_time_ms).label("best_time"),
            )
            .where(RaceResultDB.turtle_id == turtle.id)
        )
        stats = session.exec(stmt).first()
        
        win_rate = 0.0
        if turtle.total_races > 0:
            win_rate = (turtle.total_wins / turtle.total_races) * 100
        
        return {
            "turtle_id": turtle.turtle_id,
            "name": turtle.name,
            "total_races": turtle.total_races,
            "total_wins": turtle.total_wins,
            "win_rate": round(win_rate, 1),
            "avg_rank": round(stats.avg_rank, 2) if stats.avg_rank else None,
            "best_time_ms": stats.best_time if stats.best_time else None,
        }
