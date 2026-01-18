"""FastAPI application for TurboShells server.

This is the main entry point for the WebSocket server. It configures:
    - CORS for frontend access
    - Lifespan handlers for startup/shutdown
    - Route registration
    - Structured logging

Usage:
    uvicorn src.server.app:app --reload --port 8000
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.engine.logging_config import configure_logging, get_logger
from src.server.routes import race_router
from src.server.routes.race import manager

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler.
    
    Startup:
        - Configure logging
        - Start zombie cleanup loop
        
    Shutdown:
        - Stop zombie cleanup
        - Close all WebSocket connections
    """
    configure_logging(level="INFO")
    
    if logger:
        logger.info("TurboShells server starting")
    
    await manager.start_zombie_cleanup_loop(interval_seconds=60.0)
    
    yield
    
    if logger:
        logger.info("TurboShells server shutting down")
    
    await manager.stop_zombie_cleanup_loop()
    await manager.close_all()


app = FastAPI(
    title="TurboShells Engine",
    description="Headless turtle racing simulation with WebSocket broadcasting",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(race_router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "TurboShells Engine",
        "version": "1.0.0",
        "status": "online",
        "connections": manager.connection_count,
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "connections": manager.connection_count,
    }
