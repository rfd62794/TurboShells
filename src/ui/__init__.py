"""
UI module for TurboShells.

This module provides user interface components, views, and layout management.
"""

# Component imports
from .components.tab_manager import TabManager
from .components.ui_renderer import UIRenderer
from .components.event_handler import EventHandler
from .components.layout_manager import LayoutManager

# Layout imports
from .layouts.positions import *

# Renderer compatibility
from .views.renderer import Renderer

__all__ = [
    'Renderer',
    'TabManager',
    'UIRenderer', 
    'EventHandler',
    'LayoutManager'
]
