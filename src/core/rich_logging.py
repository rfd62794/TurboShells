"""
Rich logging system using Loguru and Rich libraries.
Provides beautiful, color-coded console output with advanced formatting.
"""

import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass
from datetime import datetime

try:
    from loguru import logger
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False
    print("WARNING: loguru not installed. Run: pip install loguru")

try:
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.theme import Theme
    from rich.style import Style
    from rich.text import Text
    from rich.panel import Panel
    from rich.table import Table
    from rich.columns import Columns
    from rich.align import Align
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("WARNING: rich not installed. Run: pip install rich")


@dataclass
class RichLogConfig:
    """Configuration for rich logging system."""
    level: str = "INFO"
    log_to_file: bool = True
    log_to_console: bool = True
    file_path: Optional[str] = None
    rotation: str = "10 MB"
    retention: str = "7 days"
    compression: str = "zip"
    enable_rich_console: bool = True
    show_path: bool = False
    show_time: bool = True
    show_level: bool = True
    rich_theme: Optional[str] = None


class RichThemeManager:
    """Manages custom themes for Rich console output."""
    
    DEFAULT_THEME = Theme({
        "logging.level.debug": Style(color="blue", bold=True),
        "logging.level.info": Style(color="green", bold=True),
        "logging.level.warning": Style(color="yellow", bold=True),
        "logging.level.error": Style(color="red", bold=True),
        "logging.level.critical": Style(color="red", bold=True, blink=True),
        "logging.level.success": Style(color="green", bold=True),
        "path": Style(dim=True),
        "time": Style(dim=True),
        "component": Style(color="magenta", bold=True),
    })
    
    GAME_THEME = Theme({
        "logging.level.debug": Style(color="cyan", dim=True),
        "logging.level.info": Style(color="bright_green"),
        "logging.level.warning": Style(color="bright_yellow"),
        "logging.level.error": Style(color="bright_red", bold=True),
        "logging.level.critical": Style(color="red", bold=True, reverse=True),
        "logging.level.success": Style(color="bright_green", bold=True),
        "path": Style(dim=True, color="grey50"),
        "time": Style(dim=True, color="grey50"),
        "component": Style(color="bright_magenta", bold=True),
        "game": Style(color="bright_blue", bold=True),
        "ui": Style(color="bright_cyan", bold=True),
        "component_sys": Style(color="bright_yellow", bold=True),
    })


class RichLogger:
    """Enhanced logger using Loguru and Rich."""
    
    def __init__(self, component_name: str, config: RichLogConfig = None):
        self.component_name = component_name
        self.config = config or RichLogConfig()
        
        if not LOGURU_AVAILABLE:
            # Fallback to standard logging
            self.logger = logging.getLogger(f"rich.{component_name}")
            self._use_standard_logging()
            return
            
        self.logger = logger.bind(component=component_name)
        self._setup_loguru()
    
    def _use_standard_logging(self):
        """Fallback to standard logging when Loguru not available."""
        self.logger.setLevel(getattr(logging, self.config.level.upper()))
        
        if not self.logger.handlers:
            # Console handler
            if self.config.log_to_console:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(getattr(logging, self.config.level))
                formatter = logging.Formatter(
                    f"%(asctime)s - [{self.component_name}] - %(levelname)s - %(message)s"
                )
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)
    
    def _setup_loguru(self):
        """Set up Loguru with Rich console if available."""
        # Remove default handlers
        logger.remove()
        
        # Console handler with Rich
        if self.config.log_to_console and RICH_AVAILABLE and self.config.enable_rich_console:
            console = Console(theme=self._get_theme())
            
            rich_handler = RichHandler(
                console=console,
                show_path=self.config.show_path,
                show_time=self.config.show_time,
                show_level=self.config.show_level,
                markup=True,
                rich_tracebacks=True,
                tracebacks_show_locals=True,
                tracebacks_extra_lines=2,
            )
            
            logger.add(
                rich_handler,
                level=self.config.level,
                format=f"<level>{self.config.level}</level> | <component>[{self.component_name}]</component> | <level>{'{message}'}</level>",
                colorize=True,
                backtrace=True,
                diagnose=True
            )
        elif self.config.log_to_console:
            # Fallback console handler without Rich
            logger.add(
                sys.stderr,
                level=self.config.level,
                format=f"<green>{datetime.now().strftime('%H:%M:%S')}</green> | <level>{self.config.level: <8}</level> | <cyan>[{self.component_name}]</cyan> | <level>{'{message}'}</level>",
                colorize=True,
                backtrace=True,
                diagnose=True
            )
        
        # File handler
        if self.config.log_to_file:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            file_path = self.config.file_path or log_dir / f"turboshells_{datetime.now().strftime('%Y%m%d')}.log"
            
            logger.add(
                file_path,
                level=self.config.level,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | [{extra[component]}] | {message}",
                rotation=self.config.rotation,
                retention=self.config.retention,
                compression=self.config.compression,
                backtrace=True,
                diagnose=True,
                enqueue=True  # Thread-safe
            )
    
    def _get_theme(self) -> Theme:
        """Get the appropriate Rich theme."""
        if self.config.rich_theme == "game":
            return RichThemeManager.GAME_THEME
        return RichThemeManager.DEFAULT_THEME
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log("DEBUG", message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log("ERROR", message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log("CRITICAL", message, **kwargs)
    
    def success(self, message: str, **kwargs):
        """Log success message (Loguru specific)."""
        if LOGURU_AVAILABLE:
            self._log("SUCCESS", message, **kwargs)
        else:
            self._log("INFO", f"✅ {message}", **kwargs)
    
    def _log(self, level: str, message: str, **kwargs):
        """Internal logging method."""
        if LOGURU_AVAILABLE:
            # Use Loguru's structured logging
            extra = kwargs.get('extra', {})
            extra['component'] = self.component_name
            
            # Log with bound logger
            bound_logger = self.logger.bind(**extra)
            getattr(bound_logger, level.lower())(message)
        else:
            # Fallback to standard logging
            getattr(self.logger, level.lower())(message)


class RichLoggingManager:
    """Central manager for Rich logging system."""
    
    def __init__(self, config: RichLogConfig = None):
        self.config = config or RichLogConfig()
        self.loggers: Dict[str, RichLogger] = {}
        
        # Set up global configuration
        if LOGURU_AVAILABLE:
            self._setup_global_loguru()
    
    def _setup_global_loguru(self):
        """Set up global Loguru configuration."""
        logger.configure(
            handlers=[
                {
                    "sink": sys.stderr,
                    "format": "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{extra[component]}</cyan> | <level>{message}</level>",
                    "level": self.config.level,
                    "colorize": True,
                    "backtrace": True,
                    "diagnose": True,
                }
            ]
        )
    
    def get_logger(self, component_name: str) -> RichLogger:
        """Get or create a component-specific logger."""
        if component_name not in self.loggers:
            self.loggers[component_name] = RichLogger(component_name, self.config)
        return self.loggers[component_name]
    
    def set_level(self, level: str):
        """Set logging level for all loggers."""
        self.config.level = level.upper()
        if LOGURU_AVAILABLE:
            # Update all Loguru handlers
            logger.remove()
            for logger_instance in self.loggers.values():
                logger_instance._setup_loguru()
    
    def create_game_log_panel(self, console: Optional[Console] = None) -> Panel:
        """Create a Rich panel showing game log information."""
        if not RICH_AVAILABLE:
            return Panel("Rich library not available")
        
        console = console or Console(theme=RichThemeManager.GAME_THEME)
        
        table = Table(title="🎮 TurboShells Logging System", show_header=True, header_style="bold magenta")
        table.add_column("Component", style="cyan", width=15)
        table.add_column("Status", style="green", width=10)
        table.add_column("Log Level", style="yellow", width=10)
        table.add_column("Features", style="blue", width=30)
        
        table.add_row("Game", "✅ Active", self.config.level, "✅ Rich Output ✅ File Logging")
        table.add_row("UI", "✅ Active", self.config.level, "✅ Component Tracking ✅ Events")
        table.add_row("Components", "✅ Active", self.config.level, "✅ SRP Logging ✅ Debug")
        
        return Panel(
            table,
            border_style="bright_blue",
            padding=(1, 2)
        )


# Global logging manager instance
_rich_logging_manager: Optional[RichLoggingManager] = None


def get_rich_logging_manager(config: RichLogConfig = None) -> RichLoggingManager:
    """Get the global Rich logging manager."""
    global _rich_logging_manager
    if _rich_logging_manager is None:
        _rich_logging_manager = RichLoggingManager(config)
    return _rich_logging_manager


def get_rich_logger(component_name: str) -> RichLogger:
    """Get a component-specific Rich logger."""
    return get_rich_logging_manager().get_logger(component_name)


def setup_rich_logging(config: RichLogConfig = None) -> RichLoggingManager:
    """Set up Rich logging system."""
    return get_rich_logging_manager(config)


# Convenience functions for common components
def get_game_rich_logger() -> RichLogger:
    """Get Rich logger for game logic."""
    return get_rich_logger("GAME")


def get_ui_rich_logger() -> RichLogger:
    """Get Rich logger for UI components."""
    return get_rich_logger("UI")


def get_component_rich_logger() -> RichLogger:
    """Get Rich logger for component system."""
    return get_rich_logger("COMPONENTS")


def get_debug_rich_logger() -> RichLogger:
    """Get Rich logger for debug information."""
    return get_rich_logger("DEBUG")


def show_logging_info():
    """Display logging system information using Rich."""
    if not RICH_AVAILABLE:
        print("Rich library not available for fancy display")
        return
    
    console = Console(theme=RichThemeManager.GAME_THEME)
    manager = get_rich_logging_manager()
    
    console.print(manager.create_game_log_panel(console))


# Installation check and helper functions
def check_dependencies():
    """Check if required dependencies are installed."""
    missing = []
    
    if not LOGURU_AVAILABLE:
        missing.append("loguru")
    if not RICH_AVAILABLE:
        missing.append("rich")
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install loguru rich")
        return False
    else:
        print("✅ All dependencies available")
        return True


def install_dependencies():
    """Helper function to install missing dependencies."""
    import subprocess
    
    missing = []
    if not LOGURU_AVAILABLE:
        missing.append("loguru")
    if not RICH_AVAILABLE:
        missing.append("rich")
    
    if missing:
        print(f"Installing missing dependencies: {', '.join(missing)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            print("✅ Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    else:
        print("✅ All dependencies already installed")
        return True
