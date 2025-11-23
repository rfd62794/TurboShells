"""
Logging configuration for TurboShells game.
Provides centralized logging setup for development and debugging.
"""

import logging
import os
from datetime import datetime
from pathlib import Path


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


def log_performance(operation, duration, details="", level=logging.DEBUG):
    """
    Log performance information.

    Args:
        operation: Operation being measured
        duration: Duration in seconds
        details: Additional details
        level: Logging level
    """
    logger = get_logger("performance")
    logger.log(level, f"Performance - {operation}: {duration:.3f}s {details}")


# Initialize logging when module is imported
if not logging.getLogger().handlers:
    setup_logging()
