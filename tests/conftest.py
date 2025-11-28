"""
Clean root conftest.py using Local Plugins pattern.

This file serves only to register the fixture plugins and handle
global configuration. All actual fixtures are in the fixtures/ package.
"""

import pytest
import sys
from pathlib import Path

# Keep path insertion here so it applies to all sub-plugins
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# 1. REGISTER THE NEW FILES
pytest_plugins = [
    "tests.fixtures.core",
    "tests.fixtures.game",
    "tests.fixtures.ui",
    "tests.fixtures.performance",
]

# 2. KEEP GLOBAL HOOKS HERE
def pytest_configure(config):
    """Configure pytest markers"""
    markers = [
        "unit: Mark test as unit test",
        "integration: Mark test as integration test",
        "performance: Mark test as performance test",
        "ui: Mark test as UI test",
        "ui_components: Mark test as UI component test",
        "ui_panels: Mark test as UI panel test",
        "ui_integration: Mark test as UI integration test",
        "slow: Mark test as slow running",
        "genetics: Mark test as genetics-related",
        "save_load: Mark test as save/load related",
    ]
    for marker in markers:
        config.addinivalue_line("markers", marker)
