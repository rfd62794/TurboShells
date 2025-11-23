"""
Simple profiling utilities for TurboShells game performance monitoring.
"""

import time
import functools
from typing import Callable, Any
from .logging_config import get_logger


class SimpleProfiler:
    """Simple context manager for profiling code execution time."""

    def __init__(self, operation_name: str, log_results: bool = True):
        """
        Initialize profiler.

        Args:
            operation_name: Name of the operation being profiled
            log_results: Whether to log results automatically
        """
        self.operation_name = operation_name
        self.log_results = log_results
        self.start_time = None
        self.end_time = None
        self.duration = None

    def __enter__(self):
        """Start timing."""
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and optionally log results."""
        self.end_time = time.perf_counter()
        self.duration = self.end_time - self.start_time

        if self.log_results:
            logger = get_logger('performance')
            logger.debug(f"Profile - {self.operation_name}: {self.duration:.3f}s")

    def get_duration(self) -> float:
        """Get the duration in seconds."""
        return self.duration if self.duration is not None else 0.0


def profile_function(operation_name: str = None) -> Callable:
    """
    Decorator to profile a function.

    Args:
        operation_name: Name for the operation (defaults to function name)

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        name = operation_name or f"{func.__module__}.{func.__name__}"

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            with SimpleProfiler(name):
                return func(*args, **kwargs)

        return wrapper
    return decorator


class PerformanceTracker:
    """Track performance metrics over time."""

    def __init__(self, max_samples: int = 100):
        """
        Initialize performance tracker.

        Args:
            max_samples: Maximum number of samples to keep
        """
        self.max_samples = max_samples
        self.samples = {}

    def add_sample(self, operation: str, duration: float):
        """
        Add a performance sample.

        Args:
            operation: Operation name
            duration: Duration in seconds
        """
        if operation not in self.samples:
            self.samples[operation] = []

        self.samples[operation].append(duration)

        # Keep only the most recent samples
        if len(self.samples[operation]) > self.max_samples:
            self.samples[operation] = self.samples[operation][-self.max_samples:]

    def get_stats(self, operation: str) -> dict:
        """
        Get statistics for an operation.

        Args:
            operation: Operation name

        Returns:
            Dictionary with statistics
        """
        if operation not in self.samples or not self.samples[operation]:
            return {}

        durations = self.samples[operation]
        return {
            'count': len(durations),
            'avg': sum(durations) / len(durations),
            'min': min(durations),
            'max': max(durations),
            'latest': durations[-1]
        }

    def get_all_stats(self) -> dict:
        """
        Get statistics for all operations.

        Returns:
            Dictionary with all statistics
        """
        return {op: self.get_stats(op) for op in self.samples.keys()}


# Global performance tracker instance
performance_tracker = PerformanceTracker()


def track_performance(operation: str):
    """
    Context manager to track performance over time.

    Args:
        operation: Operation name

    Returns:
        Context manager
    """
    class Tracker:
        def __enter__(self):
            self.start_time = time.perf_counter()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.perf_counter() - self.start_time
            performance_tracker.add_sample(operation, duration)

            # Log if it's unusually slow
            stats = performance_tracker.get_stats(operation)
            if stats.get('count', 0) > 5 and duration > stats['avg'] * 2:
                logger = get_logger('performance')
                logger.warning(f"Slow execution detected - {operation}: {duration:.3f}s "
                               f"(avg: {stats['avg']:.3f}s)")

    return Tracker()


def log_fps(frame_time: float):
    """
    Log FPS information.

    Args:
        frame_time: Time per frame in seconds
    """
    fps = 1.0 / frame_time if frame_time > 0 else 0
    logger = get_logger('performance')
    logger.debug(f"FPS: {fps:.1f} (frame time: {frame_time * 1000:.1f}ms)")


def log_memory_usage():
    """Log current memory usage (basic implementation)."""
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024

        logger = get_logger('performance')
        logger.debug(f"Memory usage: {memory_mb:.1f} MB")
    except ImportError:
        # psutil not available, skip memory logging
        pass


class GameLoopProfiler:
    """Specialized profiler for game loop performance."""

    def __init__(self):
        self.frame_times = []
        self.max_samples = 300  # 5 seconds at 60 FPS

    def start_frame(self):
        """Start timing a frame."""
        self.frame_start = time.perf_counter()

    def end_frame(self):
        """End timing a frame and record metrics."""
        if hasattr(self, 'frame_start'):
            frame_time = time.perf_counter() - self.frame_start
            self.frame_times.append(frame_time)

            # Keep only recent samples
            if len(self.frame_times) > self.max_samples:
                self.frame_times = self.frame_times[-self.max_samples:]

            # Log FPS every 60 frames
            if len(self.frame_times) % 60 == 0:
                avg_frame_time = sum(self.frame_times[-60:]) / 60
                log_fps(avg_frame_time)

    def get_fps(self) -> float:
        """Get current FPS estimate."""
        if not self.frame_times:
            return 0.0

        # Use average of last 60 frames
        recent_frames = self.frame_times[-60:]
        avg_frame_time = sum(recent_frames) / len(recent_frames)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0


# Global game loop profiler
game_loop_profiler = GameLoopProfiler()
