"""
UI Components Package

Component-based UI architecture following Single Responsibility Principle.
"""

# Core Foundation
from .base_component import BaseComponent

# Reusable Components (Primary)
from .reusable import (
    # Display Components
    Label,
    TextBox,
    ImageDisplay,
    ProgressBar,
    MoneyDisplay,
    
    # Input Components
    Button,
    IconButton,
    ToggleButton,
    Dropdown,
    Slider,
    TextInput,
    
    # Layout Components
    Container,
    ScrollContainer,
    GridContainer,
    FlexContainer,
    Panel,
    
    # Game-Specific Components
    TurtleCard,
    ItemCard,
    BetSelector,
    RaceHUD,
)

# Specialized Components (Panel-Specific)
from .container import Container as LegacyContainer, ScrollableContainer
from .rating_component import StarRating, DropdownRating, RatingCategory
from .turtle_display import TurtleDisplay, DesignDisplay
from .panel_component import PanelComponent, VotingPanelComponent
from .menu_components import MoneyDisplay as MenuMoneyDisplay, MenuButton, NavigationMenu, MainMenuComponent

# Legacy components (to be refactored)
from .button import Button as LegacyButton, ToggleButton as LegacyToggleButton
from .turtle_card import TurtleCard as LegacyTurtleCard

__all__ = [
    # Core Foundation
    'BaseComponent',
    
    # Reusable Components (Primary - Use These!)
    'Label',
    'TextBox',
    'ImageDisplay',
    'ProgressBar',
    'MoneyDisplay',
    'Button',
    'IconButton',
    'ToggleButton',
    'Dropdown',
    'Slider',
    'TextInput',
    'Container',
    'ScrollContainer',
    'GridContainer',
    'FlexContainer',
    'Panel',
    'TurtleCard',
    'ItemCard',
    'BetSelector',
    'RaceHUD',
    
    # Specialized Components (Panel-Specific)
    'StarRating',
    'DropdownRating',
    'RatingCategory',
    'TurtleDisplay',
    'DesignDisplay',
    'PanelComponent',
    'VotingPanelComponent',
    'MenuMoneyDisplay',
    'MenuButton',
    'NavigationMenu',
    'MainMenuComponent',
    
    # Legacy Components (Avoid Using)
    'LegacyButton',
    'LegacyToggleButton',
    'LegacyTurtleCard',
    'LegacyContainer',
    'ScrollableContainer',
]