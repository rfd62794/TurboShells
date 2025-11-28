"""
Performance tracking fixtures.

This module contains fixtures for performance testing,
timing measurements, and benchmarking.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Generator
import pytest
import sys

# Ensure project root is in path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Import utility classes
from tests.utils import PerformanceTracker, UIPerformanceTracker


@pytest.fixture
def performance_test_data():
    """Provide data for performance testing"""
    return {
        'large_roster_size': 50,
        'race_iterations': 100,
        'memory_test_iterations': 1000,
        'timeout_seconds': 30,
        'ui_performance': {
            'creation_threshold': 0.1,  # 100ms
            'update_threshold': 0.001,   # 1ms  
            'render_threshold': 0.01     # 10ms
        }
    }


@pytest.fixture
def perf_tracker():
    """Provide performance tracker"""
    return PerformanceTracker()


@pytest.fixture
def ui_perf_tracker():
    """Provide UI performance tracker"""
    return UIPerformanceTracker()
