"""
Real-time monitoring overlay for displaying performance and debugging information
during gameplay. Provides a heads-up display with FPS, memory usage, and other metrics.
"""

import pygame
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from .monitoring_system import monitoring_system, PerformanceMetrics
from .logging_config import get_logger


@dataclass
class OverlayConfig:
    """Configuration for the monitoring overlay."""
    enabled: bool = False  # Disabled by default, toggle with 'O' key
    position: str = "top-left"  # top-left, top-right, bottom-left, bottom-right
    font_size: int = 14
    background_alpha: int = 180  # 0-255
    show_fps: bool = True
    show_memory: bool = True
    show_cpu: bool = True
    show_errors: bool = True
    show_stats: bool = False
    update_interval: float = 0.5  # seconds


class MonitoringOverlay:
    """Real-time monitoring overlay for gameplay."""
    
    def __init__(self, config: OverlayConfig = None):
        """
        Initialize monitoring overlay.
        
        Args:
            config: Overlay configuration
        """
        self.config = config or OverlayConfig()
        self.logger = get_logger("overlay")
        
        # Pygame components
        self.font = None
        self.background_surface = None
        self.last_update = 0
        
        # Display data
        self.current_metrics: Optional[PerformanceMetrics] = None
        self.error_count = 0
        self.last_errors: List[str] = []
        
        # Position calculations
        self.margin = 10
        self.line_height = 20
        
        self.margin = 10
        self.line_height = 20
        
        # Defer initialization until pygame is ready
        # self._initialize_pygame_components()
        
    def initialize(self):
        """Initialize pygame components. Must be called after pygame.init()."""
        self._initialize_pygame_components()
        
    def _initialize_pygame_components(self):
        """Initialize pygame components for the overlay."""
        try:
            # Initialize font
            self.font = pygame.font.Font(None, self.config.font_size)
            
            # Create background surface
            self.background_surface = pygame.Surface((300, 200))
            self.background_surface.set_alpha(self.config.background_alpha)
            
            self.logger.info("Monitoring overlay initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize overlay: {e}")
            self.config.enabled = False
            
    def update(self, current_time: float):
        """Update overlay data."""
        if not self.config.enabled:
            return
            
        # Update at specified interval
        if current_time - self.last_update < self.config.update_interval:
            return
            
        self.last_update = current_time
        
        # Get current metrics
        self.current_metrics = monitoring_system.performance_monitor.get_current_metrics()
        
        # Update error count
        error_summary = monitoring_system.error_monitor.get_error_summary()
        self.error_count = error_summary.get("total_errors", 0)
        
        # Get recent errors
        recent_errors = error_summary.get("recent_errors", [])
        self.last_errors = [f"{e['type']}: {e['message'][:30]}..." for e in recent_errors[-3:]]
        
    def render(self, screen: pygame.Surface):
        """Render the overlay to the screen."""
        if not self.config.enabled or not self.font:
            return
            
        # Build display lines
        lines = self._build_display_lines()
        if not lines:
            return
            
        # Calculate dimensions
        max_width = max(self.font.size(line)[0] for line in lines) + 20
        height = len(lines) * self.line_height + 20
        
        # Create background
        background = pygame.Surface((max_width, height))
        background.set_alpha(self.config.background_alpha)
        background.fill((0, 0, 0))
        
        # Calculate position
        x, y = self._calculate_position(max_width, height)
        
        # Draw background
        screen.blit(background, (x, y))
        
        # Draw text
        for i, line in enumerate(lines):
            color = self._get_line_color(line)
            text_surface = self.font.render(line, True, color)
            screen.blit(text_surface, (x + 10, y + 10 + i * self.line_height))
            
    def _build_display_lines(self) -> List[str]:
        """Build the list of lines to display."""
        lines = []
        
        # Header
        lines.append("=== TurboShells Monitor ===")
        
        # Performance metrics
        if self.config.show_fps and self.current_metrics:
            fps_color = self._get_fps_color(self.current_metrics.fps)
            lines.append(f"FPS: {self.current_metrics.fps:.1f}")
            
        if self.config.show_memory and self.current_metrics:
            memory_color = self._get_memory_color(self.current_metrics.memory_usage)
            lines.append(f"Memory: {self.current_metrics.memory_usage:.1f}MB")
            
        if self.config.show_cpu and self.current_metrics:
            cpu_color = self._get_cpu_color(self.current_metrics.cpu_usage)
            lines.append(f"CPU: {self.current_metrics.cpu_usage:.1f}%")
            
        # Error information
        if self.config.show_errors and self.error_count > 0:
            lines.append(f"Errors: {self.error_count}")
            for error in self.last_errors:
                lines.append(f"  {error}")
                
        # Game statistics
        if self.config.show_stats:
            stats = monitoring_system.stats_tracker.get_statistics_summary()
            lifetime = stats.get("lifetime", {})
            lines.append(f"Races: {lifetime.get('races_completed', 0)}")
            lines.append(f"Win Rate: {lifetime.get('win_rate', 0):.1f}%")
            
        # Timestamp
        lines.append(f"Updated: {datetime.now().strftime('%H:%M:%S')}")
        
        return lines
        
    def _calculate_position(self, width: int, height: int) -> Tuple[int, int]:
        """Calculate the position for the overlay."""
        screen_width, screen_height = pygame.display.get_surface().get_size()
        
        if self.config.position == "top-left":
            return (self.margin, self.margin)
        elif self.config.position == "top-right":
            return (screen_width - width - self.margin, self.margin)
        elif self.config.position == "bottom-left":
            return (self.margin, screen_height - height - self.margin)
        elif self.config.position == "bottom-right":
            return (screen_width - width - self.margin, screen_height - height - self.margin)
        else:
            return (self.margin, self.margin)  # Default to top-left
            
    def _get_fps_color(self, fps: float) -> Tuple[int, int, int]:
        """Get color based on FPS value."""
        if fps >= 50:
            return (0, 255, 0)  # Green
        elif fps >= 30:
            return (255, 255, 0)  # Yellow
        else:
            return (255, 0, 0)  # Red
            
    def _get_memory_color(self, memory: float) -> Tuple[int, int, int]:
        """Get color based on memory usage."""
        if memory <= 200:
            return (0, 255, 0)  # Green
        elif memory <= 400:
            return (255, 255, 0)  # Yellow
        else:
            return (255, 0, 0)  # Red
            
    def _get_cpu_color(self, cpu: float) -> Tuple[int, int, int]:
        """Get color based on CPU usage."""
        if cpu <= 50:
            return (0, 255, 0)  # Green
        elif cpu <= 75:
            return (255, 255, 0)  # Yellow
        else:
            return (255, 0, 0)  # Red
            
    def _get_line_color(self, line: str) -> Tuple[int, int, int]:
        """Get color for a specific line."""
        if "FPS:" in line:
            return self._get_fps_color(float(line.split(":")[1]))
        elif "Memory:" in line:
            return self._get_memory_color(float(line.split(":")[1].replace("MB", "")))
        elif "CPU:" in line:
            return self._get_cpu_color(float(line.split(":")[1].replace("%", "")))
        elif "Errors:" in line:
            return (255, 100, 100)  # Light red
        elif "  " in line:  # Error detail line
            return (200, 100, 100)  # Dimmer red
        elif "===" in line:
            return (100, 200, 255)  # Light blue
        else:
            return (255, 255, 255)  # White
            
    def toggle_visibility(self):
        """Toggle overlay visibility."""
        self.config.enabled = not self.config.enabled
        self.logger.info(f"Overlay visibility: {self.config.enabled}")
        
    def set_position(self, position: str):
        """Set overlay position."""
        valid_positions = ["top-left", "top-right", "bottom-left", "bottom-right"]
        if position in valid_positions:
            self.config.position = position
            self.logger.info(f"Overlay position: {position}")
        else:
            self.logger.warning(f"Invalid position: {position}")
            
    def toggle_fps_display(self):
        """Toggle FPS display."""
        self.config.show_fps = not self.config.show_fps
        
    def toggle_memory_display(self):
        """Toggle memory display."""
        self.config.show_memory = not self.config.show_memory
        
    def toggle_cpu_display(self):
        """Toggle CPU display."""
        self.config.show_cpu = not self.config.show_cpu
        
    def toggle_error_display(self):
        """Toggle error display."""
        self.config.show_errors = not self.config.show_errors
        
    def toggle_stats_display(self):
        """Toggle statistics display."""
        self.config.show_stats = not self.config.show_stats
        
    def handle_key_event(self, event: pygame.event.Event):
        """Handle keyboard events for overlay control."""
        if event.type == pygame.KEYDOWN:
            # Toggle overlay with F1
            if event.key == pygame.K_F1:
                self.toggle_visibility()
                
            # Change position with F2
            elif event.key == pygame.K_F2:
                positions = ["top-left", "top-right", "bottom-left", "bottom-right"]
                current_index = positions.index(self.config.position)
                new_position = positions[(current_index + 1) % len(positions)]
                self.set_position(new_position)
                
            # Toggle individual displays with F3-F7
            elif event.key == pygame.K_F3:
                self.toggle_fps_display()
            elif event.key == pygame.K_F4:
                self.toggle_memory_display()
            elif event.key == pygame.K_F5:
                self.toggle_cpu_display()
            elif event.key == pygame.K_F6:
                self.toggle_error_display()
            elif event.key == pygame.K_F7:
                self.toggle_stats_display()
                
            # Export report with F12
            elif event.key == pygame.K_F12:
                monitoring_system.export_report()
                
    def get_help_text(self) -> str:
        """Get help text for overlay controls."""
        return """
Monitoring Overlay Controls:
F1  - Toggle overlay visibility
F2  - Change position
F3  - Toggle FPS display
F4  - Toggle memory display
F5  - Toggle CPU display
F6  - Toggle error display
F7  - Toggle statistics display
F12 - Export monitoring report
        """.strip()


# Global overlay instance
monitoring_overlay = MonitoringOverlay()
