"""
Logging configuration for TurboShells game.
Provides centralized logging setup for development and debugging.

This is a portfolio project - logging focuses on development needs
rather than production monitoring.
"""

import logging
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


def setup_logging(log_level=logging.INFO, log_to_file=True, log_to_console=True):
    """
    Set up logging configuration for the game.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to a file
        log_to_console: Whether to log to console
    """
    # Create logs directory if it doesn't exist
    if log_to_file:
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File handler
    if log_to_file:
        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"turboshells_{timestamp}.log"

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name):
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_game_event(event_type, details, level=logging.INFO):
    """
    Log a game-specific event.

    Args:
        event_type: Type of game event (e.g., 'race_start', 'turtle_bred')
        details: Event details
        level: Logging level
    """
    logger = get_logger("game_events")
    logger.log(level, f"{event_type}: {details}")


def log_error(error, context="", level=logging.ERROR):
    """
    Log an error with context.

    Args:
        error: Exception or error message
        context: Additional context information
        level: Logging level
    """
    logger = get_logger("game_errors")
    if context:
        logger.log(level, f"Error in {context}: {error}")
    else:
        logger.log(level, f"Error: {error}")


def log_debug_info(context: str, data: Dict[str, Any] = None) -> None:
    """
    Log detailed debug information for development.
    
    Args:
        context: Context where debug info is being logged
        data: Dictionary of debug data to log
    """
    logger = get_logger("debug")
    logger.debug(f"DEBUG INFO - {context}")
    if data:
        for key, value in data.items():
            logger.debug(f"  {key}: {value}")


def log_exception_with_context(
    exception: Exception, 
    context: str = "", 
    user_data: Dict[str, Any] = None
) -> None:
    """
    Log an exception with full traceback and context.
    
    Args:
        exception: The exception that occurred
        context: Context where the exception occurred
        user_data: Additional user/game state data
    """
    logger = get_logger("exceptions")
    
    # Log the exception with full traceback
    exc_info = (type(exception), exception, exception.__traceback__)
    logger.error(f"Exception in {context}: {exception}", exc_info=exc_info)
    
    # Log additional context if provided
    if user_data:
        logger.error("Context data:")
        for key, value in user_data.items():
            logger.error(f"  {key}: {value}")


def log_game_state(state: Dict[str, Any], level: int = logging.DEBUG) -> None:
    """
    Log current game state for debugging.
    
    Args:
        state: Game state dictionary
        level: Logging level to use
    """
    logger = get_logger("game_state")
    logger.log(level, "Current game state:")
    for key, value in state.items():
        logger.log(level, f"  {key}: {value}")


def create_development_logger(name: str) -> logging.Logger:
    """
    Create a logger specifically configured for development debugging.
    
    Args:
        name: Logger name
        
    Returns:
        Logger configured for development
    """
    logger = get_logger(f"dev.{name}")
    logger.setLevel(logging.DEBUG)
    return logger


def setup_performance_logging() -> logging.Logger:
    """
    Set up a dedicated performance logger.
    
    Returns:
        Logger for performance monitoring
    """
    logger = get_logger("performance")
    logger.setLevel(logging.DEBUG)
    return logger


class GameLogger:
    """
    Convenience class for game-specific logging operations.
    Provides easy access to different logging contexts.
    """
    
    def __init__(self, module_name: str):
        """Initialize with module name."""
        self.module_name = module_name
        self.logger = get_logger(module_name)
        self.debug_logger = create_development_logger(module_name)
        self.perf_logger = setup_performance_logging()
    
    def debug(self, message: str, data: Dict[str, Any] = None) -> None:
        """Log debug message with optional data."""
        self.debug_logger.debug(message)
        if data:
            for key, value in data.items():
                self.debug_logger.debug(f"  {key}: {value}")
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str, exception: Optional[Exception] = None) -> None:
        """Log error message with optional exception."""
        if exception:
            log_exception_with_context(exception, self.module_name)
        else:
            self.logger.error(message)
    
    def game_event(self, event_type: str, details: str) -> None:
        """Log a game event."""
        log_game_event(event_type, details)
    
    def performance(self, operation: str, duration: float, details: str = "") -> None:
        """Log performance information."""
        log_performance(operation, duration, details)


# Initialize logging when module is imported
if not logging.getLogger().handlers:
    setup_logging()
