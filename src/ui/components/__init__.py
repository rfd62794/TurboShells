"""
UI Components Package

Component-based UI architecture following Single Responsibility Principle.
"""

from .base_component import BaseComponent
from .container import Container, ScrollableContainer
from .rating_component import StarRating, DropdownRating, RatingCategory
from .turtle_display import TurtleDisplay, DesignDisplay
from .panel_component import PanelComponent, VotingPanelComponent

# Legacy components (to be refactored)
from .button import Button, ToggleButton
from .turtle_card import TurtleCard

__all__ = [
    # New component-based architecture
    'BaseComponent',
    'Container',
    'ScrollableContainer', 
    'StarRating',
    'DropdownRating',
    'RatingCategory',
    'TurtleDisplay',
    'DesignDisplay',
    'PanelComponent',
    'VotingPanelComponent',
    
    # Legacy components
    'Button',
    'ToggleButton',
    'TurtleCard',
]