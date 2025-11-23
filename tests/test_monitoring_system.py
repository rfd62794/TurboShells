"""
Comprehensive tests for the monitoring and debugging system.
Tests all components of Phase 3: Basic Monitoring & Debugging.
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Import the monitoring system components
from src.core.monitoring_system import (
    PerformanceMetrics, ErrorReport, GameStatistics,
    RealTimeMonitor, ErrorMonitor, GameStatisticsTracker,
    DevelopmentDebugger, IntegratedMonitoringSystem
)
from src.core.monitoring_overlay import MonitoringOverlay, OverlayConfig
from src.core.profiler import game_loop_profiler


class TestPerformanceMetrics:
    """Test the PerformanceMetrics data class."""
    
    def test_performance_metrics_creation(self):
        """Test creating performance metrics."""
        metrics = PerformanceMetrics(
            fps=60.0,
            frame_time=0.016,
            memory_usage=256.0,
            cpu_usage=45.0
        )
        
        assert metrics.fps == 60.0
        assert metrics.frame_time == 0.016
        assert metrics.memory_usage == 256.0
        assert metrics.cpu_usage == 45.0
        assert isinstance(metrics.timestamp, datetime)
        
    def test_performance_metrics_defaults(self):
        """Test performance metrics with default values."""
        metrics = PerformanceMetrics()
        
        assert metrics.fps == 0.0
        assert metrics.frame_time == 0.0
        assert metrics.memory_usage == 0.0
        assert metrics.cpu_usage == 0.0
        assert isinstance(metrics.timestamp, datetime)


class TestErrorReport:
    """Test the ErrorReport data class."""
    
    def test_error_report_creation(self):
        """Test creating an error report."""
        error = ValueError("Test error")
        report = ErrorReport(
            timestamp=datetime.now(),
            error_type="ValueError",
            message="Test error",
            context="test_function",
            stack_trace="Traceback..."
        )
        
        assert report.error_type == "ValueError"
        assert report.message == "Test error"
        assert report.context == "test_function"
        assert report.stack_trace == "Traceback..."
        assert isinstance(report.timestamp, datetime)


class TestRealTimeMonitor:
    """Test the real-time performance monitor."""
    
    def test_monitor_initialization(self):
        """Test monitor initialization."""
        monitor = RealTimeMonitor(update_interval=0.1)
        
        assert monitor.update_interval == 0.1
        assert not monitor.is_running
        assert monitor.fps_threshold == 30.0
        assert monitor.memory_threshold == 500.0
        assert monitor.cpu_threshold == 80.0
        assert len(monitor.alert_callbacks) == 0
        
    def test_add_alert_callback(self):
        """Test adding alert callbacks."""
        monitor = RealTimeMonitor()
        callback = Mock()
        
        monitor.add_alert_callback(callback)
        assert len(monitor.alert_callbacks) == 1
        assert monitor.alert_callbacks[0] == callback
        
    @patch('src.core.monitoring_system.psutil.Process')
    def test_collect_metrics(self, mock_process):
        """Test collecting performance metrics."""
        # Mock psutil.Process
        mock_process_instance = Mock()
        mock_process.return_value = mock_process_instance
        
        # Mock memory info
        mock_memory_info = Mock()
        mock_memory_info.rss = 256 * 1024 * 1024  # 256 MB
        mock_process_instance.memory_info.return_value = mock_memory_info
        mock_process_instance.cpu_percent.return_value = 45.0
        
        # Mock game loop profiler
        with patch('src.core.monitoring_system.game_loop_profiler') as mock_profiler:
            mock_profiler.get_fps.return_value = 60.0
            
            monitor = RealTimeMonitor()
            metrics = monitor._collect_metrics()
            
            assert metrics.fps == 60.0
            assert metrics.memory_usage == 256.0
            assert metrics.cpu_usage == 45.0
            assert metrics.frame_time == 1.0 / 60.0
            
    def test_get_performance_summary_empty(self):
        """Test performance summary with no data."""
        monitor = RealTimeMonitor()
        summary = monitor.get_performance_summary()
        
        assert summary == {}
        
    def test_start_stop_monitoring(self):
        """Test starting and stopping monitoring."""
        monitor = RealTimeMonitor(update_interval=0.01)
        
        # Start monitoring
        monitor.start_monitoring()
        assert monitor.is_running
        assert monitor.monitor_thread is not None
        
        # Let it run briefly
        time.sleep(0.02)
        
        # Stop monitoring
        monitor.stop_monitoring()
        assert not monitor.is_running


class TestErrorMonitor:
    """Test the error monitoring system."""
    
    def test_error_monitor_initialization(self):
        """Test error monitor initialization."""
        monitor = ErrorMonitor(max_reports=50)
        
        assert monitor.max_reports == 50
        assert len(monitor.error_reports) == 0
        assert len(monitor.error_counts) == 0
        
    def test_report_error(self):
        """Test reporting an error."""
        monitor = ErrorMonitor()
        error = ValueError("Test error")
        
        monitor.report_error(error, "test_context", {"key": "value"})
        
        assert len(monitor.error_reports) == 1
        assert len(monitor.error_counts) == 1
        assert monitor.error_counts["ValueError"] == 1
        
        report = monitor.error_reports[0]
        assert report.error_type == "ValueError"
        assert report.message == "Test error"
        assert report.context == "test_context"
        assert report.user_data == {"key": "value"}
        
    def test_error_patterns(self):
        """Test error pattern detection."""
        monitor = ErrorMonitor()
        
        # Report same error multiple times
        error = ValueError("Repeated error")
        for i in range(5):
            monitor.report_error(error, f"context_{i}")
            
        # Should detect pattern after 3+ occurrences
        assert monitor.error_counts["ValueError"] == 5
        
    def test_get_error_summary(self):
        """Test getting error summary."""
        monitor = ErrorMonitor()
        
        # Add some errors
        monitor.report_error(ValueError("Error 1"), "context1")
        monitor.report_error(RuntimeError("Error 2"), "context2")
        monitor.report_error(ValueError("Error 3"), "context3")
        
        summary = monitor.get_error_summary()
        
        assert summary["total_errors"] == 3
        assert len(summary["recent_errors"]) == 3
        assert "ValueError" in summary["error_types"]
        assert "RuntimeError" in summary["error_types"]
        assert summary["most_common"] == ("ValueError", 2)


class TestGameStatisticsTracker:
    """Test the game statistics tracker."""
    
    def test_statistics_initialization(self):
        """Test statistics tracker initialization."""
        tracker = GameStatisticsTracker()
        
        assert tracker.stats.races_completed == 0
        assert tracker.stats.races_won == 0
        assert tracker.stats.total_earnings == 0.0
        assert tracker.stats.turtles_bred == 0
        assert tracker.stats.playtime_minutes == 0
        assert isinstance(tracker.stats.session_start, datetime)
        
    def test_start_end_session(self):
        """Test session tracking."""
        tracker = GameStatisticsTracker()
        original_start = tracker.stats.session_start
        
        # End session
        tracker.end_session()
        
        # Should have recorded session time
        assert tracker.stats.playtime_minutes >= 0
        
        # Start new session
        tracker.start_session()
        assert tracker.stats.session_start > original_start
        
    def test_record_race_result(self):
        """Test recording race results."""
        tracker = GameStatisticsTracker()
        
        # Record a win
        tracker.record_race_result(won=True, earnings=100.0, position=1)
        assert tracker.stats.races_completed == 1
        assert tracker.stats.races_won == 1
        assert tracker.stats.total_earnings == 100.0
        
        # Record a loss
        tracker.record_race_result(won=False, earnings=5.0, position=3)
        assert tracker.stats.races_completed == 2
        assert tracker.stats.races_won == 1
        assert tracker.stats.total_earnings == 105.0
        
    def test_record_turtle_bred(self):
        """Test recording turtle breeding."""
        tracker = GameStatisticsTracker()
        
        tracker.record_turtle_bred()
        assert tracker.stats.turtles_bred == 1
        
        tracker.record_turtle_bred()
        assert tracker.stats.turtles_bred == 2
        
    def test_get_statistics_summary(self):
        """Test getting statistics summary."""
        tracker = GameStatisticsTracker()
        
        # Add some data
        tracker.record_race_result(won=True, earnings=100.0, position=1)
        tracker.record_race_result(won=False, earnings=5.0, position=3)
        tracker.record_turtle_bred()
        
        summary = tracker.get_statistics_summary()
        
        assert summary["lifetime"]["races_completed"] == 2
        assert summary["lifetime"]["races_won"] == 1
        assert summary["lifetime"]["win_rate"] == 50.0
        assert summary["lifetime"]["total_earnings"] == 105.0
        assert summary["lifetime"]["turtles_bred"] == 1
        
        assert summary["recent"]["races_completed"] == 2
        assert summary["recent"]["win_rate"] == 50.0
        assert summary["recent"]["avg_earnings"] == 52.5


class TestDevelopmentDebugger:
    """Test the development debugger."""
    
    def test_debugger_initialization(self):
        """Test debugger initialization."""
        debugger = DevelopmentDebugger()
        
        assert len(debugger.debug_data) == 0
        assert len(debugger.debug_callbacks) == 0
        
    def test_add_debug_data(self):
        """Test adding debug data."""
        debugger = DevelopmentDebugger()
        
        debugger.add_debug_data("test_key", "test_value")
        
        assert "test_key" in debugger.debug_data
        assert debugger.debug_data["test_key"]["value"] == "test_value"
        assert "timestamp" in debugger.debug_data["test_key"]
        
    def test_get_debug_data(self):
        """Test getting debug data."""
        debugger = DevelopmentDebugger()
        
        debugger.add_debug_data("key1", "value1")
        debugger.add_debug_data("key2", "value2")
        
        # Get all data
        all_data = debugger.get_debug_data()
        assert len(all_data) == 2
        
        # Get specific key
        specific_data = debugger.get_debug_data("key1")
        assert specific_data["value"] == "value1"
        
    def test_add_debug_callback(self):
        """Test adding debug callbacks."""
        debugger = DevelopmentDebugger()
        callback = Mock()
        
        debugger.add_debug_callback(callback)
        assert len(debugger.debug_callbacks) == 1
        assert debugger.debug_callbacks[0] == callback
        
    def test_create_performance_report(self):
        """Test creating performance report."""
        debugger = DevelopmentDebugger()
        
        # Mock the monitoring components
        debugger.performance_monitor = Mock()
        debugger.error_monitor = Mock()
        debugger.stats_tracker = Mock()
        
        # Setup mock returns
        debugger.performance_monitor.get_performance_summary.return_value = {
            "current_fps": 60.0,
            "status": "healthy"
        }
        debugger.error_monitor.get_error_summary.return_value = {
            "total_errors": 0,
            "error_types": {}
        }
        debugger.stats_tracker.get_statistics_summary.return_value = {
            "lifetime": {"races_completed": 10}
        }
        
        report = debugger.create_performance_report()
        
        assert "TurboShells Performance Report" in report
        assert "Performance Metrics:" in report
        assert "Error Summary:" in report
        assert "Game Statistics:" in report


class TestMonitoringOverlay:
    """Test the monitoring overlay system."""
    
    def test_overlay_config(self):
        """Test overlay configuration."""
        config = OverlayConfig(
            enabled=True,
            position="top-right",
            font_size=16,
            show_fps=True,
            show_memory=False
        )
        
        assert config.enabled is True
        assert config.position == "top-right"
        assert config.font_size == 16
        assert config.show_fps is True
        assert config.show_memory is False
        
    @patch('pygame.font.Font')
    @patch('pygame.display.get_surface')
    def test_overlay_initialization(self, mock_get_surface, mock_font):
        """Test overlay initialization."""
        # Mock pygame components
        mock_surface = Mock()
        mock_surface.get_size.return_value = (800, 600)
        mock_get_surface.return_value = mock_surface
        
        mock_font_instance = Mock()
        mock_font.return_value = mock_font_instance
        
        config = OverlayConfig(enabled=True)
        overlay = MonitoringOverlay(config)
        
        assert overlay.config.enabled is True
        assert overlay.font == mock_font_instance
        
    def test_overlay_controls(self):
        """Test overlay control methods."""
        overlay = MonitoringOverlay()
        
        # Test toggle visibility
        original_enabled = overlay.config.enabled
        overlay.toggle_visibility()
        assert overlay.config.enabled != original_enabled
        
        # Test position changes
        overlay.set_position("bottom-right")
        assert overlay.config.position == "bottom-right"
        
        # Test display toggles
        original_fps = overlay.config.show_fps
        overlay.toggle_fps_display()
        assert overlay.config.show_fps != original_fps
        
    def test_help_text(self):
        """Test help text generation."""
        overlay = MonitoringOverlay()
        help_text = overlay.get_help_text()
        
        assert "F1" in help_text
        assert "Toggle overlay visibility" in help_text
        assert "F12" in help_text
        assert "Export monitoring report" in help_text


class TestIntegratedMonitoringSystem:
    """Test the integrated monitoring system."""
    
    def test_system_initialization(self):
        """Test system initialization."""
        system = IntegratedMonitoringSystem()
        
        assert system.performance_monitor is not None
        assert system.error_monitor is not None
        assert system.stats_tracker is not None
        assert system.debugger is not None
        
        # Check cross-component references
        assert system.debugger.performance_monitor == system.performance_monitor
        assert system.debugger.error_monitor == system.error_monitor
        assert system.debugger.stats_tracker == system.stats_tracker
        
    def test_start_stop(self):
        """Test starting and stopping the system."""
        system = IntegratedMonitoringSystem()
        
        # Start system
        system.start()
        assert system.performance_monitor.is_running
        
        # Stop system
        system.stop()
        assert not system.performance_monitor.is_running
        
    def test_comprehensive_report(self):
        """Test getting comprehensive report."""
        system = IntegratedMonitoringSystem()
        
        # Mock the components
        system.performance_monitor.get_performance_summary.return_value = {
            "current_fps": 60.0,
            "status": "healthy"
        }
        system.error_monitor.get_error_summary.return_value = {
            "total_errors": 0
        }
        system.stats_tracker.get_statistics_summary.return_value = {
            "lifetime": {"races_completed": 5}
        }
        system.debugger.get_debug_data.return_value = {
            "test_key": {"value": "test_value"}
        }
        
        report = system.get_comprehensive_report()
        
        assert "performance" in report
        assert "errors" in report
        assert "statistics" in report
        assert "debug" in report
        assert "timestamp" in report
        
        assert report["performance"]["current_fps"] == 60.0
        assert report["errors"]["total_errors"] == 0
        assert report["statistics"]["lifetime"]["races_completed"] == 5


class TestIntegration:
    """Integration tests for the monitoring system."""
    
    def test_full_monitoring_workflow(self):
        """Test a complete monitoring workflow."""
        system = IntegratedMonitoringSystem()
        
        # Start monitoring
        system.start()
        
        try:
            # Simulate some activity
            system.stats_tracker.record_race_result(won=True, earnings=100.0, position=1)
            system.stats_tracker.record_turtle_bred()
            
            # Report an error
            system.error_monitor.report_error(ValueError("Test error"), "test_context")
            
            # Add debug data
            system.debugger.add_debug_data("test_metric", 42)
            
            # Get comprehensive report
            report = system.get_comprehensive_report()
            
            # Verify data was collected
            assert report["statistics"]["lifetime"]["races_completed"] == 1
            assert report["statistics"]["lifetime"]["turtles_bred"] == 1
            assert report["errors"]["total_errors"] == 1
            assert "test_metric" in report["debug"]
            
        finally:
            # Stop monitoring
            system.stop()
            
    @patch('src.core.monitoring_system.psutil.Process')
    def test_performance_alerts(self, mock_process):
        """Test performance alert system."""
        # Mock psutil to return high CPU usage
        mock_process_instance = Mock()
        mock_process.return_value = mock_process_instance
        mock_process_instance.cpu_percent.return_value = 90.0  # High CPU
        mock_process_instance.memory_info.return_value = Mock(rss=256 * 1024 * 1024)
        
        with patch('src.core.monitoring_system.game_loop_profiler') as mock_profiler:
            mock_profiler.get_fps.return_value = 25.0  # Low FPS
            
            system = IntegratedMonitoringSystem()
            
            # Set up alert callback
            alert_received = threading.Event()
            alert_data = {}
            
            def alert_callback(alert, metrics):
                alert_data["alert"] = alert
                alert_data["metrics"] = metrics
                alert_received.set()
                
            system.performance_monitor.add_alert_callback(alert_callback)
            system.performance_monitor.cpu_threshold = 80.0
            system.performance_monitor.fps_threshold = 30.0
            
            # Start monitoring
            system.start()
            
            try:
                # Wait for alert (with timeout)
                alert_received.wait(timeout=2.0)
                
                # Verify alert was triggered
                assert "alert" in alert_data
                assert "metrics" in alert_data
                assert "Low FPS" in alert_data["alert"] or "High CPU" in alert_data["alert"]
                
            finally:
                system.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
