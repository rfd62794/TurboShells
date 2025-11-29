"""Specialized Profile Panel Components built from reusable components."""

import pygame
import pygame_gui
from typing import Optional, Dict, Any
from ...components.reusable.input import Button
from ...components.reusable.stats_panel import StatsPanel
from ...components.reusable.race_history_panel import RaceHistoryPanel
from ...components.reusable.turtle_info_panel import TurtleInfoPanel
from core.rich_logging import get_ui_rich_logger


class ProfileHeader:
    """Profile header component with back button."""
    
    def __init__(self, rect: pygame.Rect, width: int, manager, container=None, event_bus=None):
        """Initialize profile header."""
        self.rect = rect
        self.width = width
        self.manager = manager
        self.container = container
        self.event_bus = event_bus
        self.logger = get_ui_rich_logger()
        
        # UI elements
        self.panel = None
        self.back_button = None
        
        self._create_header()
        
    def _create_header(self) -> None:
        """Create the header panel and back button."""
        # Header panel
        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=self.rect,
            manager=self.manager,
            container=self.container,
            object_id="#profile_header"
        )
        
        # Back button using reusable Button component
        self.back_button = Button(
            rect=pygame.Rect((self.width - 100, 10), (80, 40)),
            text="Back",
            action="back",
            manager=self.manager,
            container=self.panel,
            config={'auto_resize': False, 'min_width': 80, 'padding': 20}  # Disable auto-resize
        )
        
    def show(self) -> None:
        """Show the header."""
        if self.panel and hasattr(self.panel, 'show'):
            self.panel.show()
            
    def hide(self) -> None:
        """Hide the header."""
        if self.panel and hasattr(self.panel, 'hide'):
            self.panel.hide()
            
    def destroy(self) -> None:
        """Clean up the header."""
        if self.back_button:
            self.back_button.destroy()
        if self.panel:
            self.panel.kill() if hasattr(self.panel, 'kill') else None


class ProfileActionPanel:
    """Profile action panel component with release button."""
    
    def __init__(self, rect: pygame.Rect, manager, container=None):
        """Initialize profile action panel."""
        self.rect = rect
        self.manager = manager
        self.container = container
        self.logger = get_ui_rich_logger()
        
        # UI elements
        self.panel = None
        self.release_button = None
        
        self._create_action_panel()
        
    def _create_action_panel(self) -> None:
        """Create the action panel and release button."""
        # Action panel
        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=self.rect,
            manager=self.manager,
            container=self.container,
            object_id="#action_panel"
        )
        
        # Release button using reusable Button component
        self.release_button = Button(
            rect=pygame.Rect((240, 50), (80, 40)),  # Positioned 20px from left
            text="Release",
            action="release",
            manager=self.manager,
            container=self.panel,
            config={'auto_resize': False, 'min_width': 80, 'padding': 20}  # Disable auto-resize
        )
        
    def update_button_state(self, can_release: bool, text: str = "Release") -> None:
        """Update the release button state and text."""
        if self.release_button:
            self.release_button.set_enabled(can_release)
            self.release_button.set_text(text)
            
    def show(self) -> None:
        """Show the action panel."""
        if self.panel and hasattr(self.panel, 'show'):
            self.panel.show()
            
    def hide(self) -> None:
        """Hide the action panel."""
        if self.panel and hasattr(self.panel, 'hide'):
            self.panel.hide()
            
    def destroy(self) -> None:
        """Clean up the action panel."""
        if self.release_button:
            self.release_button.destroy()
        if self.panel:
            self.panel.kill() if hasattr(self.panel, 'kill') else None


class ProfileLayout:
    """Profile layout manager that organizes all profile components."""
    
    def __init__(self, container_rect: pygame.Rect, manager, container=None):
        """Initialize profile layout."""
        self.container_rect = container_rect
        self.manager = manager
        self.container = container
        self.logger = get_ui_rich_logger()
        
        # Component positions
        self.positions = self._calculate_positions()
        
    def _calculate_positions(self) -> Dict[str, pygame.Rect]:
        """Calculate component positions within the container."""
        width = self.container_rect.width - 40
        
        return {
            'header': pygame.Rect((0, 0), (width + 40, 60)),
            'turtle_info': pygame.Rect((10, 70), (300, 280)),
            'stats': pygame.Rect((320, 70), (340, 250)),
            'history': pygame.Rect((10, 360), (300, 140)),
            'actions': pygame.Rect((320, 360), (360, 140))
        }
        
    def get_position(self, component_name: str) -> pygame.Rect:
        """Get the position for a specific component."""
        return self.positions.get(component_name, pygame.Rect(0, 0, 100, 100))
        
    def update_layout(self, new_container_rect: pygame.Rect) -> None:
        """Update layout for new container size."""
        self.container_rect = new_container_rect
        self.positions = self._calculate_positions()
