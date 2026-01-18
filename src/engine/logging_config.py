"""Structured logging configuration using Loguru.

Provides consistent, structured logging across the TurboShells engine.
Configures file rotation, JSON formatting for telemetry, and pretty
console output for development.

Usage:
    from src.engine.logging_config import configure_logging
    configure_logging()  # Call once at startup
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

try:
    from loguru import logger
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False
    logger = None  # type: ignore


LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class LoggingConfig:
    """Centralized logging configuration for the TurboShells engine.
    
    Single Responsibility: Configure and manage logging handlers.
    """
    
    DEFAULT_FORMAT = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    JSON_FORMAT = "{message}"
    
    def __init__(
        self,
        level: LogLevel = "INFO",
        log_dir: Path | None = None,
        enable_console: bool = True,
        enable_file: bool = True,
        enable_json: bool = False,
    ):
        self.level = level
        self.log_dir = log_dir or Path("logs")
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.enable_json = enable_json
    
    def configure(self) -> None:
        """Apply logging configuration.
        
        Removes default handlers and configures:
        - Console handler with pretty formatting
        - Rotating file handler for persistent logs
        - Optional JSON handler for telemetry ingestion
        """
        if not LOGURU_AVAILABLE:
            return
        
        logger.remove()
        
        if self.enable_console:
            logger.add(
                sys.stderr,
                format=self.DEFAULT_FORMAT,
                level=self.level,
                colorize=True,
            )
        
        if self.enable_file:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            logger.add(
                self.log_dir / "engine_{time:YYYY-MM-DD}.log",
                format=self.DEFAULT_FORMAT,
                level=self.level,
                rotation="10 MB",
                retention="7 days",
                compression="gz",
            )
        
        if self.enable_json:
            logger.add(
                self.log_dir / "engine_telemetry.jsonl",
                format=self.JSON_FORMAT,
                level=self.level,
                rotation="50 MB",
                retention="3 days",
                serialize=True,
            )


def configure_logging(
    level: LogLevel = "INFO",
    log_dir: Path | None = None,
) -> None:
    """Convenience function to configure logging with defaults.
    
    Args:
        level: Minimum log level to capture
        log_dir: Directory for log files (default: ./logs)
    """
    config = LoggingConfig(level=level, log_dir=log_dir)
    config.configure()


def get_logger(name: str):
    """Get a contextualized logger instance.
    
    Args:
        name: Logger name/context (usually __name__)
        
    Returns:
        Loguru logger bound with context, or None if Loguru unavailable
    """
    if not LOGURU_AVAILABLE:
        return None
    return logger.bind(name=name)
