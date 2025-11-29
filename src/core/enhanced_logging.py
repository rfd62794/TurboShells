"""
Enhanced logging system with color support and component-specific loggers.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass


# ANSI color codes for console output
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'


@dataclass
class LogConfig:
    """Configuration for enhanced logging."""
    level: int = logging.INFO
    log_to_file: bool = True
    log_to_console: bool = True
    use_colors: bool = True
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""
    
    COLORS = {
        'DEBUG': Colors.BLUE,
        'INFO': Colors.GREEN,
        'WARNING': Colors.YELLOW,
        'ERROR': Colors.RED,
        'CRITICAL': Colors.RED + Colors.BOLD,
    }
    
    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors
        
    def format(self, record):
        # Create base format
        if self.use_colors and hasattr(record, 'stream') and record.stream == 'console':
            color = self.COLORS.get(record.levelname, Colors.WHITE)
            record.levelname = f"{color}{record.levelname}{Colors.RESET}"
            record.name = f"{Colors.CYAN}{record.name}{Colors.RESET}"
            
        # Format the message
        formatted = super().format(record)
        
        # Add component-specific formatting
        if hasattr(record, 'component'):
            formatted = f"[{Colors.MAGENTA}{record.component}{Colors.RESET}] {formatted}"
            
        return formatted


class ComponentLogger:
    """Enhanced logger for specific components."""
    
    def __init__(self, component_name: str, config: LogConfig = None):
        self.component_name = component_name
        self.config = config or LogConfig()
        self.logger = logging.getLogger(f"component.{component_name}")
        self.logger.setLevel(self.config.level)
        
        # Set up handlers if not already configured
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up console and file handlers."""
        # Console handler
        if self.config.log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.config.level)
            
            # Custom formatter for console
            console_formatter = ColoredFormatter(self.config.use_colors)
            console_handler.setFormatter(console_formatter)
            
            # Add stream attribute to record for color formatting
            console_handler.emit = self._add_stream_to_record(console_handler.emit, 'console')
            
            self.logger.addHandler(console_handler)
        
        # File handler
        if self.config.log_to_file:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            file_path = self.config.file_path or log_dir / f"turboshells_{datetime.now().strftime('%Y%m%d')}.log"
            
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                file_path,
                maxBytes=self.config.max_file_size,
                backupCount=self.config.backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(self.config.level)
            
            # Plain formatter for file
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            
            self.logger.addHandler(file_handler)
    
    def _add_stream_to_record(self, original_emit, stream_name):
        """Add stream attribute to log records."""
        def emit(record):
            record.stream = stream_name
            record.component = self.component_name
            return original_emit(record)
        return emit
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log(logging.CRITICAL, message, **kwargs)
    
    def _log(self, level: int, message: str, **kwargs):
        """Internal logging method with extra context."""
        extra = {'component': self.component_name}
        if 'extra' in kwargs:
            extra.update(kwargs['extra'])
        self.logger.log(level, message, extra=extra)


class LoggingManager:
    """Central logging manager for the entire application."""
    
    def __init__(self, config: LogConfig = None):
        self.config = config or LogConfig()
        self.loggers: Dict[str, ComponentLogger] = {}
        
        # Configure root logger
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """Set up the root logger."""
        root_logger = logging.getLogger()
        root_logger.setLevel(self.config.level)
        
        # Clear existing handlers
        root_logger.handlers.clear()
    
    def get_logger(self, component_name: str) -> ComponentLogger:
        """Get or create a component-specific logger."""
        if component_name not in self.loggers:
            self.loggers[component_name] = ComponentLogger(component_name, self.config)
        return self.loggers[component_name]
    
    def set_level(self, level: int):
        """Set logging level for all loggers."""
        self.config.level = level
        for logger in self.loggers.values():
            logger.logger.setLevel(level)
            for handler in logger.logger.handlers:
                handler.setLevel(level)


# Global logging manager instance
_logging_manager: Optional[LoggingManager] = None


def get_logging_manager(config: LogConfig = None) -> LoggingManager:
    """Get the global logging manager."""
    global _logging_manager
    if _logging_manager is None:
        _logging_manager = LoggingManager(config)
    return _logging_manager


def get_logger(component_name: str) -> ComponentLogger:
    """Get a component-specific logger."""
    return get_logging_manager().get_logger(component_name)


def setup_enhanced_logging(config: LogConfig = None) -> LoggingManager:
    """Set up enhanced logging system."""
    return get_logging_manager(config)


# Convenience functions for common components
def get_ui_logger() -> ComponentLogger:
    """Get logger for UI components."""
    return get_logger("UI")


def get_game_logger() -> ComponentLogger:
    """Get logger for game logic."""
    return get_logger("GAME")


def get_component_logger() -> ComponentLogger:
    """Get logger for component system."""
    return get_logger("COMPONENT")


def get_debug_logger() -> ComponentLogger:
    """Get logger for debug information."""
    return get_logger("DEBUG")
