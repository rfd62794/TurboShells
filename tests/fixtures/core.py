"""
Core test fixtures for basic setup and configuration.

This module contains fundamental fixtures that are used across
different test categories.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Generator
import pytest
import json

# Ensure project root is in path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Provide test data directory path"""
    return Path(__file__).parent.parent / "test_data"


@pytest.fixture
def temp_save_dir() -> Generator[Path, None, None]:
    """Provide temporary directory for save file testing"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def save_file_data():
    """Provide sample save file data"""
    return {
        'version': '2.4.0',
        'money': 150,
        'roster': [
            {
                'name': 'Test Turtle',
                'speed': 5.0,
                'energy': 100.0,
                'recovery': 2.0,
                'swim': 1.5,
                'climb': 1.5,
                'age': 3,
                'is_active': True,
                'current_energy': 100.0,
                'race_distance': 0.0,
                'is_resting': False,
                'finished': False,
                'rank': 0
            }
        ],
        'retired_roster': [],
        'shop_inventory': [],
        'race_history': [],
        'votes': {},
        'genetics_pool': {}
    }


@pytest.fixture
def error_scenarios():
    """Provide error scenario test data"""
    return {
        'invalid_turtle_data': {
            'name': '',
            'speed': -1.0,
            'energy': 0.0,
            'recovery': -1.0,
            'swim': -1.0,
            'climb': -1.0,
            'age': -1,
            'is_active': True
        },
        'corrupted_save_file': '{"invalid": json}',
        'empty_track': [],
        'negative_money': -100,
        'invalid_race_state': 'INVALID_STATE'
    }
