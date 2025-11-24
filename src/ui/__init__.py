"""
UI module for TurboShells.

This module provides user interface components, views, and layout management.
"""

# Compatibility imports for backward compatibility
from .views.menu_view import draw_menu
from .views.roster_view import draw_roster
from .views.race_view import draw_race, draw_race_result
from .views.shop_view import draw_shop
from .views.breeding_view import draw_breeding
from .views.profile_view import draw_profile
from .views.voting_interface import draw_voting
from .views.turtle_card import draw_stable_turtle_slot, format_turtle_label_basic
from .views.renderer import Renderer

# Component imports
from .components.tab_manager import TabManager
from .components.ui_renderer import UIRenderer
from .components.event_handler import EventHandler
from .components.layout_manager import LayoutManager

# Layout imports
from .layouts.positions import *

# Legacy compatibility
try:
    from .menu_view import draw_menu as draw_main_menu_view
    from .roster_view import draw_roster as draw_menu_view
except ImportError:
    pass

# Additional compatibility for renderer
from .views.renderer import Renderer as renderer

__all__ = [
    'draw_menu',
    'draw_roster', 
    'draw_race',
    'draw_race_result',
    'draw_shop',
    'draw_breeding',
    'draw_profile',
    'draw_voting',
    'draw_stable_turtle_slot',
    'format_turtle_label_basic',
    'Renderer',
    'renderer',
    'TabManager',
    'UIRenderer', 
    'EventHandler',
    'LayoutManager'
]
