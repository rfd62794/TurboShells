"""
Dynamic layout manager for responsive UI design.

This module provides a comprehensive layout system that adapts to screen size changes,
supports multiple layout types, and enables responsive design patterns.
"""

import pygame
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from enum import Enum
import math

from .types import LayoutType, Alignment, SizePolicy
from .container import Container
from ..components.style import StyleManager


@dataclass
class LayoutConstraints:
    """Layout constraints for components."""
    min_width: Optional[int] = None
    max_width: Optional[int] = None
    min_height: Optional[int] = None
    max_height: Optional[int] = None
    
    # Aspect ratio constraints (width/height)
    aspect_ratio: Optional[float] = None
    
    # Margins and padding
    margin_top: int = 0
    margin_right: int = 0
    margin_bottom: int = 0
    margin_left: int = 0
    
    # Position constraints
    anchor_x: Optional[float] = None  # 0.0 (left) to 1.0 (right)
    anchor_y: Optional[float] = None  # 0.0 (top) to 1.0 (bottom)


@dataclass
class Breakpoint:
    """Responsive breakpoint definition."""
    width: int
    name: str
    layout_overrides: Dict[str, Any] = None


class LayoutManager:
    """
    Dynamic layout manager with responsive design capabilities.
    
    Responsibilities:
    - Calculate responsive layouts based on screen size
    - Manage layout containers and constraints
    - Handle screen size changes and layout updates
    - Provide layout debugging and validation tools
    """
    
    def __init__(self, screen_rect: pygame.Rect):
        """
        Initialize layout manager.
        
        Args:
            screen_rect: Initial screen rectangle
        """
        self.screen_rect = screen_rect
        self.containers: Dict[str, Container] = {}
        self.constraints: Dict[str, LayoutConstraints] = {}
        self.breakpoints: List[Breakpoint] = []
        self.current_breakpoint: Optional[Breakpoint] = None
        
        # Layout calculation cache
        self._layout_cache: Dict[str, pygame.Rect] = {}
        self._needs_recalculation = True
        
        # Event callbacks
        self.on_screen_resize: Optional[Callable[[pygame.Rect], None]] = None
        self.on_breakpoint_change: Optional[Callable[[Breakpoint], None]] = None
        
        # Initialize default breakpoints
        self._initialize_default_breakpoints()
        
        # Initialize default layouts
        self._initialize_default_layouts()
    
    def _initialize_default_breakpoints(self) -> None:
        """Initialize default responsive breakpoints."""
        self.breakpoints = [
            Breakpoint(width=800, name="small", layout_overrides={
                "panel_width_ratio": 0.95,
                "panel_height_ratio": 0.9,
                "font_size_scale": 0.8
            }),
            Breakpoint(width=1024, name="medium", layout_overrides={
                "panel_width_ratio": 0.85,
                "panel_height_ratio": 0.85,
                "font_size_scale": 0.9
            }),
            Breakpoint(width=1280, name="large", layout_overrides={
                "panel_width_ratio": 0.75,
                "panel_height_ratio": 0.8,
                "font_size_scale": 1.0
            }),
            Breakpoint(width=1600, name="xlarge", layout_overrides={
                "panel_width_ratio": 0.7,
                "panel_height_ratio": 0.75,
                "font_size_scale": 1.1
            })
        ]
    
    def _initialize_default_layouts(self) -> None:
        """Initialize default layout containers."""
        # Main settings panel
        self.create_container(
            "settings_main_panel",
            self.get_settings_panel_rect(),
            LayoutType.VERTICAL
        )
        
        # Tab bar
        self.create_container(
            "settings_tab_bar",
            self.get_tab_bar_rect(),
            LayoutType.HORIZONTAL
        )
        
        # Content area
        self.create_container(
            "settings_content",
            self.get_content_rect(),
            LayoutType.VERTICAL
        )
        
        # Button bar
        self.create_container(
            "settings_button_bar",
            self.get_button_bar_rect(),
            LayoutType.HORIZONTAL
        )
    
    def update_screen_rect(self, screen_rect: pygame.Rect) -> None:
        """
        Update screen rectangle and recalculate layouts.
        
        Args:
            screen_rect: New screen rectangle
        """
        old_rect = self.screen_rect
        self.screen_rect = screen_rect
        self._needs_recalculation = True
        
        # Check for breakpoint changes
        self._update_breakpoint()
        
        # Recalculate all layouts
        self._recalculate_all_layouts()
        
        # Notify of screen resize
        if self.on_screen_resize and old_rect != screen_rect:
            self.on_screen_resize(screen_rect)
    
    def _update_breakpoint(self) -> None:
        """Update current breakpoint based on screen width."""
        new_breakpoint = None
        
        for breakpoint in reversed(self.breakpoints):
            if self.screen_rect.width >= breakpoint.width:
                new_breakpoint = breakpoint
                break
        
        if new_breakpoint != self.current_breakpoint:
            old_breakpoint = self.current_breakpoint
            self.current_breakpoint = new_breakpoint
            
            if self.on_breakpoint_change and new_breakpoint:
                self.on_breakpoint_change(new_breakpoint)
    
    def create_container(
        self, 
        name: str, 
        rect: pygame.Rect, 
        layout_type: LayoutType,
        padding: int = 10,
        spacing: int = 5
    ) -> Container:
        """
        Create a layout container.
        
        Args:
            name: Container name for reference
            rect: Container rectangle
            layout_type: Type of layout
            padding: Internal padding
            spacing: Spacing between children
            
        Returns:
            Created container
        """
        container = Container(rect, layout_type, padding, spacing)
        self.containers[name] = container
        return container
    
    def get_container(self, name: str) -> Optional[Container]:
        """
        Get container by name.
        
        Args:
            name: Container name
            
        Returns:
            Container if found, None otherwise
        """
        return self.containers.get(name)
    
    def set_constraints(self, container_name: str, constraints: LayoutConstraints) -> None:
        """
        Set layout constraints for a container.
        
        Args:
            container_name: Name of container
            constraints: Layout constraints
        """
        self.constraints[container_name] = constraints
        self._needs_recalculation = True
    
    def get_constraints(self, container_name: str) -> LayoutConstraints:
        """
        Get layout constraints for a container.
        
        Args:
            container_name: Name of container
            
        Returns:
            Layout constraints (default if none set)
        """
        return self.constraints.get(container_name, LayoutConstraints())
    
    def _recalculate_all_layouts(self) -> None:
        """Recalculate all container layouts."""
        for name, container in self.containers.items():
            constraints = self.get_constraints(name)
            self._apply_constraints(container, constraints)
            container.recalculate_layout()
        
        self._needs_recalculation = False
    
    def _apply_constraints(self, container: Container, constraints: LayoutConstraints) -> None:
        """
        Apply layout constraints to a container.
        
        Args:
            container: Container to apply constraints to
            constraints: Constraints to apply
        """
        rect = container.rect
        
        # Apply size constraints
        if constraints.min_width is not None:
            rect.width = max(rect.width, constraints.min_width)
        
        if constraints.max_width is not None:
            rect.width = min(rect.width, constraints.max_width)
        
        if constraints.min_height is not None:
            rect.height = max(rect.height, constraints.min_height)
        
        if constraints.max_height is not None:
            rect.height = min(rect.height, constraints.max_height)
        
        # Apply aspect ratio
        if constraints.aspect_ratio is not None:
            current_ratio = rect.width / rect.height
            if current_ratio > constraints.aspect_ratio:
                # Too wide, reduce width
                rect.width = int(rect.height * constraints.aspect_ratio)
            else:
                # Too tall, reduce height
                rect.height = int(rect.width / constraints.aspect_ratio)
        
        # Apply margins
        rect.x += constraints.margin_left
        rect.y += constraints.margin_top
        
        # Apply anchor positioning
        if constraints.anchor_x is not None:
            rect.x = int(self.screen_rect.x + (self.screen_rect.width - rect.width) * constraints.anchor_x)
        
        if constraints.anchor_y is not None:
            rect.y = int(self.screen_rect.y + (self.screen_rect.height - rect.height) * constraints.anchor_y)
        
        container.rect = rect
    
    def needs_update(self) -> bool:
        """Check if layout needs recalculation."""
        return self._needs_recalculation
    
    def force_update(self) -> None:
        """Force layout recalculation."""
        self._needs_recalculation = True
        self._recalculate_all_layouts()
    
    # Settings-specific layout methods
    
    def get_settings_panel_rect(self) -> pygame.Rect:
        """
        Get main settings panel rectangle with responsive sizing.
        
        Returns:
            Responsive panel rectangle
        """
        # Get breakpoint-specific overrides
        panel_width_ratio = 0.95
        panel_height_ratio = 0.9
        max_panel_width = 950
        max_panel_height = 700
        
        if self.current_breakpoint and self.current_breakpoint.layout_overrides:
            overrides = self.current_breakpoint.layout_overrides
            panel_width_ratio = overrides.get("panel_width_ratio", panel_width_ratio)
            panel_height_ratio = overrides.get("panel_height_ratio", panel_height_ratio)
        
        # Calculate responsive dimensions
        panel_width = min(int(self.screen_rect.width * panel_width_ratio), max_panel_width)
        panel_height = min(int(self.screen_rect.height * panel_height_ratio), max_panel_height)
        
        # Upper-left positioning
        return pygame.Rect(30, 30, panel_width, panel_height)
    
    def get_tab_bar_rect(self) -> pygame.Rect:
        """
        Get tab bar rectangle.
        
        Returns:
            Tab bar rectangle
        """
        main_panel = self.get_settings_panel_rect()
        return pygame.Rect(
            main_panel.x + 10,
            main_panel.y + 10,
            main_panel.width - 20,
            40
        )
    
    def get_content_rect(self) -> pygame.Rect:
        """
        Get content area rectangle.
        
        Returns:
            Content area rectangle
        """
        tab_bar = self.get_tab_bar_rect()
        main_panel = self.get_settings_panel_rect()
        
        return pygame.Rect(
            main_panel.x + 10,
            tab_bar.bottom + 10,
            main_panel.width - 20,
            main_panel.height - tab_bar.height - 60
        )
    
    def get_button_bar_rect(self) -> pygame.Rect:
        """
        Get button bar rectangle.
        
        Returns:
            Button bar rectangle
        """
        main_panel = self.get_settings_panel_rect()
        
        return pygame.Rect(
            main_panel.x + 10,
            main_panel.bottom - 50,
            main_panel.width - 20,
            40
        )
    
    def get_responsive_font_size(self, base_size: int) -> int:
        """
        Get responsive font size based on screen size.
        
        Args:
            base_size: Base font size
            
        Returns:
            Responsive font size
        """
        scale = 1.0
        
        if self.current_breakpoint and self.current_breakpoint.layout_overrides:
            scale = self.current_breakpoint.layout_overrides.get("font_size_scale", 1.0)
        
        return max(10, int(base_size * scale))
    
    def calculate_tab_widths(self, tab_count: int, tab_names: List[str]) -> List[int]:
        """
        Calculate responsive tab widths.
        
        Args:
            tab_count: Number of tabs
            tab_names: List of tab names for text measurement
            
        Returns:
            List of tab widths
        """
        tab_bar_rect = self.get_tab_bar_rect()
        available_width = tab_bar_rect.width
        spacing = 5
        
        # Get font for text measurement
        style = StyleManager.instance().get_default()
        font = style.get_font("small")
        
        # Calculate minimum widths based on text
        min_widths = []
        for name in tab_names:
            text_width = font.size(name)[0] + 20  # Add padding
            min_widths.append(text_width)
        
        # Calculate equal distribution
        equal_width = (available_width - spacing * (tab_count - 1)) // tab_count
        
        # Check if equal distribution works for all tabs
        if all(min_width <= equal_width for min_width in min_widths):
            return [equal_width] * tab_count
        
        # Use minimum widths and distribute remaining space
        total_min_width = sum(min_widths)
        remaining_width = available_width - total_min_width - spacing * (tab_count - 1)
        
        if remaining_width <= 0:
            # Not enough space, truncate text
            return min_widths
        
        # Distribute remaining space proportionally
        widths = []
        for min_width in min_widths:
            extra = int(remaining_width * (min_width / total_min_width))
            widths.append(min_width + extra)
        
        return widths
    
    def get_debug_info(self) -> Dict[str, Any]:
        """
        Get debug information about layout system.
        
        Returns:
            Debug information dictionary
        """
        return {
            "screen_rect": str(self.screen_rect),
            "current_breakpoint": self.current_breakpoint.name if self.current_breakpoint else None,
            "container_count": len(self.containers),
            "needs_recalculation": self._needs_recalculation,
            "containers": {
                name: {
                    "rect": str(container.rect),
                    "layout_type": container.layout_type.value,
                    "child_count": len(container.children)
                }
                for name, container in self.containers.items()
            }
        }
    
    def validate_layout(self) -> List[str]:
        """
        Validate layout configuration and return issues.
        
        Returns:
            List of validation issues
        """
        issues = []
        
        # Check for overlapping containers
        container_rects = [(name, container.get_absolute_rect()) 
                          for name, container in self.containers.items()]
        
        for i, (name1, rect1) in enumerate(container_rects):
            for name2, rect2 in container_rects[i+1:]:
                if rect1.colliderect(rect2):
                    issues.append(f"Container '{name1}' overlaps with '{name2}'")
        
        # Check for containers outside screen bounds
        for name, container in self.containers.items():
            rect = container.get_absolute_rect()
            if not self.screen_rect.contains(rect):
                issues.append(f"Container '{name}' extends outside screen bounds")
        
        # Check for zero-size containers
        for name, container in self.containers.items():
            if container.rect.width <= 0 or container.rect.height <= 0:
                issues.append(f"Container '{name}' has zero or negative size")
        
        return issues
    
    def create_layout_snapshot(self) -> Dict[str, Any]:
        """
        Create a snapshot of current layout state for debugging.
        
        Returns:
            Layout snapshot dictionary
        """
        return {
            "timestamp": pygame.time.get_ticks(),
            "screen_rect": self.screen_rect,
            "breakpoint": self.current_breakpoint.name if self.current_breakpoint else None,
            "containers": {
                name: {
                    "rect": container.rect,
                    "absolute_rect": container.get_absolute_rect(),
                    "layout_type": container.layout_type.value,
                    "children": len(container.children),
                    "constraints": self.get_constraints(name).__dict__
                }
                for name, container in self.containers.items()
            }
        }


# Global layout manager instance
_layout_manager: Optional[LayoutManager] = None


def get_layout_manager(screen_rect: Optional[pygame.Rect] = None) -> LayoutManager:
    """
    Get global layout manager instance.
    
    Args:
        screen_rect: Screen rectangle (only used for first initialization)
        
    Returns:
        Layout manager instance
    """
    global _layout_manager
    if _layout_manager is None:
        if screen_rect is None:
            screen_rect = pygame.Rect(0, 0, 800, 600)
        _layout_manager = LayoutManager(screen_rect)
    return _layout_manager


def update_screen_size(screen_rect: pygame.Rect) -> None:
    """
    Update screen size for global layout manager.
    
    Args:
        screen_rect: New screen rectangle
    """
    layout_manager = get_layout_manager()
    layout_manager.update_screen_rect(screen_rect)
