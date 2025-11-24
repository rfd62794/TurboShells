"""
Settings menu view for TurboShells - Refactored SRP Version.

This module provides a comprehensive settings interface with tabbed navigation
for managing all game configuration options using SRP-compliant components.

This is the new refactored version that replaces the monolithic settings_view.py
with a clean, modular architecture.
"""

import sys
import os

# Add the current directory to Python path for relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the refactored components
from components.settings_view_refactored import SettingsViewRefactored

# Re-export the class for backward compatibility
SettingsView = SettingsViewRefactored

# For legacy imports that might reference the old class directly
__all__ = ['SettingsView', 'SettingsViewRefactored']
