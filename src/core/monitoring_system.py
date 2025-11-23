"""
Comprehensive monitoring and debugging system for TurboShells.
Builds on existing logging and profiling infrastructure to provide real-time
performance tracking, error monitoring, and development tools.
"""

import time
import psutil
import threading
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import deque
import json

from .logging_config import get_logger, GameLogger
from .profiler import GameLoopProfiler, performance_tracker


@dataclass
class PerformanceMetrics:
    """Data class for performance metrics."""
    fps: float = 0.0
    frame_time: float = 0.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ErrorReport:
    """Data class for error reporting."""
    timestamp: datetime
    error_type: str
    message: str
    context: str
    stack_trace: str
    user_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GameStatistics:
    """Data class for game statistics."""
    races_completed: int = 0
    races_won: int = 0
    total_earnings: float = 0.0
    turtles_bred: int = 0
    playtime_minutes: int = 0
    session_start: datetime = field(default_factory=datetime.now)


class RealTimeMonitor:
    """Real-time performance monitoring system."""
    
    def __init__(self, update_interval: float = 1.0):
        """
        Initialize real-time monitor.
        
        Args:
            update_interval: How often to update metrics (seconds)
        """
        self.update_interval = update_interval
        self.is_running = False
        self.monitor_thread = None
        
        # Performance tracking
        self.metrics_history = deque(maxlen=300)  # 5 minutes at 1Hz
        self.fps_history = deque(maxlen=300)
        self.memory_history = deque(maxlen=300)
        
        # Alert thresholds
        self.fps_threshold = 30.0
        self.memory_threshold = 500.0  # MB
        self.cpu_threshold = 80.0  # %
        
        # Callbacks for alerts
        self.alert_callbacks: List[Callable] = []
        
        self.logger = get_logger("monitoring")
        
    def start_monitoring(self):
        """Start real-time monitoring in background thread."""
        if self.is_running:
            return
            
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Real-time monitoring started")
        
    def stop_monitoring(self):
        """Stop real-time monitoring."""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        self.logger.info("Real-time monitoring stopped")
        
    def _monitor_loop(self):
        """Main monitoring loop running in background thread."""
        while self.is_running:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                self._check_alerts(metrics)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                
            time.sleep(self.update_interval)
            
    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics."""
        try:
            # Get FPS from game loop profiler
            fps = game_loop_profiler.get_fps()
            
            # Get memory usage
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            # Get CPU usage
            cpu_percent = process.cpu_percent()
            
            # Calculate frame time
            frame_time = 1.0 / fps if fps > 0 else 0.0
            
            return PerformanceMetrics(
                fps=fps,
                frame_time=frame_time,
                memory_usage=memory_mb,
                cpu_usage=cpu_percent,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
            return PerformanceMetrics()
            
    def _check_alerts(self, metrics: PerformanceMetrics):
        """Check for performance alerts and trigger callbacks."""
        alerts = []
        
        if metrics.fps < self.fps_threshold:
            alerts.append(f"Low FPS: {metrics.fps:.1f}")
            
        if metrics.memory_usage > self.memory_threshold:
            alerts.append(f"High memory: {metrics.memory_usage:.1f}MB")
            
        if metrics.cpu_usage > self.cpu_threshold:
            alerts.append(f"High CPU: {metrics.cpu_usage:.1f}%")
            
        for alert in alerts:
            self.logger.warning(alert)
            for callback in self.alert_callbacks:
                try:
                    callback(alert, metrics)
                except Exception as e:
                    self.logger.error(f"Error in alert callback: {e}")
                    
    def add_alert_callback(self, callback: Callable[[str, PerformanceMetrics], None]):
        """Add a callback for performance alerts."""
        self.alert_callbacks.append(callback)
        
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Get the most recent metrics."""
        return self.metrics_history[-1] if self.metrics_history else None
        
    def get_metrics_history(self, minutes: int = 5) -> List[PerformanceMetrics]:
        """Get metrics history for the specified time period."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of current performance."""
        current = self.get_current_metrics()
        if not current:
            return {}
            
        recent_metrics = self.get_metrics_history(5)  # Last 5 minutes
        
        if len(recent_metrics) < 2:
            return {
                "current_fps": current.fps,
                "current_memory": current.memory_usage,
                "current_cpu": current.cpu_usage,
                "status": "insufficient_data"
            }
            
        fps_values = [m.fps for m in recent_metrics]
        memory_values = [m.memory_usage for m in recent_metrics]
        cpu_values = [m.cpu_usage for m in recent_metrics]
        
        return {
            "current_fps": current.fps,
            "avg_fps": sum(fps_values) / len(fps_values),
            "min_fps": min(fps_values),
            "max_fps": max(fps_values),
            "current_memory": current.memory_usage,
            "avg_memory": sum(memory_values) / len(memory_values),
            "max_memory": max(memory_values),
            "current_cpu": current.cpu_usage,
            "avg_cpu": sum(cpu_values) / len(cpu_values),
            "status": "healthy" if current.fps >= self.fps_threshold else "performance_issue"
        }


class ErrorMonitor:
    """Enhanced error monitoring and reporting system."""
    
    def __init__(self, max_reports: int = 100):
        """
        Initialize error monitor.
        
        Args:
            max_reports: Maximum number of error reports to keep
        """
        self.max_reports = max_reports
        self.error_reports = deque(maxlen=max_reports)
        self.error_counts: Dict[str, int] = {}
        
        self.logger = get_logger("error_monitor")
        
    def report_error(self, 
                    exception: Exception, 
                    context: str = "", 
                    user_data: Dict[str, Any] = None,
                    severity: str = "error"):
        """
        Report an error with full context.
        
        Args:
            exception: The exception that occurred
            context: Context where the error occurred
            user_data: Additional user/game state data
            severity: Error severity level
        """
        error_type = type(exception).__name__
        message = str(exception)
        stack_trace = traceback.format_exc()
        
        report = ErrorReport(
            timestamp=datetime.now(),
            error_type=error_type,
            message=message,
            context=context,
            stack_trace=stack_trace,
            user_data=user_data or {}
        )
        
        self.error_reports.append(report)
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Log the error
        log_method = getattr(self.logger, severity, self.logger.error)
        log_method(f"{error_type} in {context}: {message}")
        
        # Check for error patterns
        self._check_error_patterns()
        
    def _check_error_patterns(self):
        """Check for patterns in errors and report issues."""
        if len(self.error_reports) < 5:
            return
            
        # Check for repeated errors
        recent_errors = list(self.error_reports)[-10:]
        error_types = [e.error_type for e in recent_errors]
        
        for error_type, count in self.error_counts.items():
            if count >= 3:
                self.logger.warning(f"Repeated error pattern detected: {error_type} (occurred {count} times)")
                
    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of recent errors."""
        if not self.error_reports:
            return {"total_errors": 0, "recent_errors": []}
            
        recent_errors = list(self.error_reports)[-10:]
        error_types = {}
        
        for report in recent_errors:
            error_types[report.error_type] = error_types.get(report.error_type, 0) + 1
            
        return {
            "total_errors": len(self.error_reports),
            "recent_errors": [
                {
                    "timestamp": report.timestamp.isoformat(),
                    "type": report.error_type,
                    "message": report.message,
                    "context": report.context
                }
                for report in recent_errors
            ],
            "error_types": error_types,
            "most_common": max(error_types.items(), key=lambda x: x[1]) if error_types else None
        }


class GameStatisticsTracker:
    """Track game statistics and analytics."""
    
    def __init__(self):
        """Initialize statistics tracker."""
        self.stats = GameStatistics()
        self.race_history = deque(maxlen=1000)
        self.session_history = deque(maxlen=100)
        
        self.logger = get_logger("statistics")
        
    def start_session(self):
        """Start a new gaming session."""
        self.stats.session_start = datetime.now()
        self.logger.info("New gaming session started")
        
    def end_session(self):
        """End the current gaming session."""
        session_duration = datetime.now() - self.stats.session_start
        self.stats.playtime_minutes += int(session_duration.total_seconds() / 60)
        
        # Store session data
        session_data = {
            "start_time": self.stats.session_start.isoformat(),
            "duration_minutes": int(session_duration.total_seconds() / 60),
            "races_completed": self.stats.races_completed,
            "races_won": self.stats.races_won,
            "earnings": self.stats.total_earnings
        }
        
        self.session_history.append(session_data)
        self.logger.info(f"Session ended: {session_data}")
        
        # Reset session-specific stats
        self.stats.races_completed = 0
        self.stats.races_won = 0
        self.stats.total_earnings = 0.0
        
    def record_race_result(self, won: bool, earnings: float, position: int):
        """Record the result of a race."""
        self.stats.races_completed += 1
        if won:
            self.stats.races_won += 1
        self.stats.total_earnings += earnings
        
        race_data = {
            "timestamp": datetime.now().isoformat(),
            "won": won,
            "earnings": earnings,
            "position": position
        }
        
        self.race_history.append(race_data)
        
        self.logger.info(f"Race recorded: {'Won' if won else 'Lost'}, ${earnings:.2f}, Position {position}")
        
    def record_turtle_bred(self):
        """Record that a turtle was bred."""
        self.stats.turtles_bred += 1
        self.logger.info(f"Turtle bred (total: {self.stats.turtles_bred})")
        
    def get_statistics_summary(self) -> Dict[str, Any]:
        """Get a comprehensive statistics summary."""
        win_rate = (self.stats.races_won / self.stats.races_completed * 100) if self.stats.races_completed > 0 else 0
        
        # Calculate recent performance
        recent_races = list(self.race_history)[-20:]  # Last 20 races
        recent_wins = sum(1 for r in recent_races if r["won"])
        recent_win_rate = (recent_wins / len(recent_races) * 100) if recent_races else 0
        
        return {
            "lifetime": {
                "races_completed": self.stats.races_completed,
                "races_won": self.stats.races_won,
                "win_rate": win_rate,
                "total_earnings": self.stats.total_earnings,
                "turtles_bred": self.stats.turtles_bred,
                "playtime_minutes": self.stats.playtime_minutes
            },
            "recent": {
                "races_completed": len(recent_races),
                "win_rate": recent_win_rate,
                "avg_earnings": sum(r["earnings"] for r in recent_races) / len(recent_races) if recent_races else 0
            },
            "session": {
                "current_session_duration": int((datetime.now() - self.stats.session_start).total_seconds() / 60),
                "session_races": self.stats.races_completed,
                "session_earnings": self.stats.total_earnings
            }
        }


class DevelopmentDebugger:
    """Development-focused debugging tools."""
    
    def __init__(self):
        """Initialize development debugger."""
        self.debug_data: Dict[str, Any] = {}
        self.debug_callbacks: List[Callable] = []
        
        self.logger = get_logger("debugger")
        
    def add_debug_data(self, key: str, value: Any):
        """Add debug data for monitoring."""
        self.debug_data[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        
    def get_debug_data(self, key: str = None) -> Any:
        """Get debug data, optionally filtered by key."""
        if key:
            return self.debug_data.get(key)
        return self.debug_data
        
    def add_debug_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add a callback for debug data updates."""
        self.debug_callbacks.append(callback)
        
    def dump_debug_state(self, file_path: str = None):
        """Dump current debug state to file."""
        if file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"logs/debug_state_{timestamp}.json"
            
        try:
            # Ensure logs directory exists
            Path(file_path).parent.mkdir(exist_ok=True)
            
            with open(file_path, 'w') as f:
                json.dump(self.debug_data, f, indent=2, default=str)
                
            self.logger.info(f"Debug state dumped to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to dump debug state: {e}")
            
    def create_performance_report(self) -> str:
        """Create a comprehensive performance report."""
        report_lines = [
            "=== TurboShells Performance Report ===",
            f"Generated: {datetime.now().isoformat()}",
            ""
        ]
        
        # Add performance metrics
        if hasattr(self, 'performance_monitor'):
            summary = self.performance_monitor.get_performance_summary()
            report_lines.extend([
                "Performance Metrics:",
                f"  FPS: {summary.get('current_fps', 'N/A')} (avg: {summary.get('avg_fps', 'N/A')})",
                f"  Memory: {summary.get('current_memory', 'N/A')}MB (max: {summary.get('max_memory', 'N/A')}MB)",
                f"  CPU: {summary.get('current_cpu', 'N/A')}%",
                f"  Status: {summary.get('status', 'unknown')}",
                ""
            ])
            
        # Add error summary
        if hasattr(self, 'error_monitor'):
            error_summary = self.error_monitor.get_error_summary()
            report_lines.extend([
                "Error Summary:",
                f"  Total Errors: {error_summary.get('total_errors', 0)}",
                f"  Error Types: {error_summary.get('error_types', {})}",
                ""
            ])
            
        # Add game statistics
        if hasattr(self, 'stats_tracker'):
            stats = self.stats_tracker.get_statistics_summary()
            report_lines.extend([
                "Game Statistics:",
                f"  Races Completed: {stats['lifetime']['races_completed']}",
                f"  Win Rate: {stats['lifetime']['win_rate']:.1f}%",
                f"  Total Earnings: ${stats['lifetime']['total_earnings']:.2f}",
                f"  Playtime: {stats['lifetime']['playtime_minutes']} minutes",
                ""
            ])
            
        return "\n".join(report_lines)


class IntegratedMonitoringSystem:
    """Main monitoring system that integrates all components."""
    
    def __init__(self):
        """Initialize the integrated monitoring system."""
        self.performance_monitor = RealTimeMonitor()
        self.error_monitor = ErrorMonitor()
        self.stats_tracker = GameStatisticsTracker()
        self.debugger = DevelopmentDebugger()
        
        # Set up cross-component references
        self.debugger.performance_monitor = self.performance_monitor
        self.debugger.error_monitor = self.error_monitor
        self.debugger.stats_tracker = self.stats_tracker
        
        # Set up alert callbacks
        self.performance_monitor.add_alert_callback(self._on_performance_alert)
        
        self.logger = get_logger("monitoring_system")
        self.logger.info("Integrated monitoring system initialized")
        
    def _on_performance_alert(self, alert: str, metrics: PerformanceMetrics):
        """Handle performance alerts."""
        self.debugger.add_debug_data("performance_alert", {
            "alert": alert,
            "metrics": metrics.__dict__
        })
        
    def start(self):
        """Start all monitoring systems."""
        self.performance_monitor.start_monitoring()
        self.stats_tracker.start_session()
        self.logger.info("Monitoring system started")
        
    def stop(self):
        """Stop all monitoring systems."""
        self.performance_monitor.stop_monitoring()
        self.stats_tracker.end_session()
        self.logger.info("Monitoring system stopped")
        
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Get a comprehensive monitoring report."""
        return {
            "performance": self.performance_monitor.get_performance_summary(),
            "errors": self.error_monitor.get_error_summary(),
            "statistics": self.stats_tracker.get_statistics_summary(),
            "debug": self.debugger.get_debug_data(),
            "timestamp": datetime.now().isoformat()
        }
        
    def export_report(self, file_path: str = None):
        """Export comprehensive report to file."""
        if file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"logs/monitoring_report_{timestamp}.json"
            
        try:
            Path(file_path).parent.mkdir(exist_ok=True)
            
            report = self.get_comprehensive_report()
            with open(file_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
                
            self.logger.info(f"Monitoring report exported to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to export report: {e}")


# Global monitoring system instance
monitoring_system = IntegratedMonitoringSystem()
