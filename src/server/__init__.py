"""TurboShells FastAPI Server Package.

Provides the WebSocket bridge between the headless RaceEngine and web clients.
Handles connection lifecycle, state broadcasting, and REST API endpoints.

Exports:
    app: FastAPI application instance
    ConnectionManager: WebSocket connection lifecycle manager
"""

# Lazy imports to avoid requiring FastAPI at module import time
# This allows tests to import specific components without full stack

def get_app():
    """Get the FastAPI app instance (lazy load)."""
    from src.server.app import app
    return app


def get_connection_manager():
    """Get the ConnectionManager class (lazy load)."""
    from src.server.websocket_manager import ConnectionManager
    return ConnectionManager


__all__ = ["get_app", "get_connection_manager"]
