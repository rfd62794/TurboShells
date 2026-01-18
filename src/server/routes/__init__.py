"""Routes package for TurboShells server."""

from src.server.routes.race import router as race_router
from src.server.routes.race import api_router as race_api_router

__all__ = ["race_router", "race_api_router"]
