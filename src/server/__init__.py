"""TurboShells FastAPI Server Package.

Provides the WebSocket bridge between the headless RaceEngine and web clients.
Handles connection lifecycle, state broadcasting, and REST API endpoints.

Exports:
    app: FastAPI application instance
    ConnectionManager: WebSocket connection lifecycle manager
"""

from src.server.app import app
from src.server.websocket_manager import ConnectionManager

__all__ = ["app", "ConnectionManager"]
