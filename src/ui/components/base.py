"""
Base UI component system implementing Single Responsibility Principle.

This module provides the foundational component architecture for the entire UI system,
establishing proper parent-child relationships, lifecycle management, and event delegation.
"""

import pygame
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum

from .style import Style, StyleManager


class ComponentState(Enum):
    """Component lifecycle states."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    DISABLED = "disabled"
    HIDDEN = "hidden"
    DESTROYED = "destroyed"


@dataclass
class EventResult:
    """Result of event handling."""
    handled: bool = False
    stop_propagation: bool = False
    data: Optional[Dict[str, Any]] = None


class UIComponent(ABC):
    """
    Base component class implementing Single Responsibility Principle.
    
    Responsibilities:
    - Component lifecycle management
    - Parent-child relationship management
    - Event delegation to children
    - Basic state management
    
    Note: Each subclass should have a single, well-defined responsibility.
    """
    
    def __init__(self, rect: pygame.Rect, style: Optional[Style] = None, component_id: str = ""):
        """
        Initialize base component.
        
        Args:
            rect: Component position and dimensions
            style: Styling information (uses default if None)
            component_id: Unique identifier for the component
        """
        self.rect = rect
        self.style = style or StyleManager.get_default()
        self.component_id = component_id or self.__class__.__name__
        
        # Component hierarchy
        self.parent: Optional['UIComponent'] = None
        self.children: List['UIComponent'] = []
        
        # Component state
        self.state = ComponentState.INITIALIZING
        self.visible = True
        self.enabled = True
        self.focused = False
        
        # Event handling
        self.event_handlers: Dict[str, List[Callable]] = {}
        self._hovered = False
        
        # Lifecycle callbacks
        self.on_init: Optional[Callable[[], None]] = None
        self.on_destroy: Optional[Callable[[], None]] = None
        
        # Initialize component
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize component and call init callback."""
        self.state = ComponentState.ACTIVE
        if self.on_init:
            self.on_init()
    
    def add_child(self, child: 'UIComponent') -> None:
        """
        Add a child component to this component.
        
        Args:
            child: Child component to add
        """
        if child.parent:
            child.parent.remove_child(child)
        
        child.parent = self
        self.children.append(child)
        
        # Update child's rect to be relative to parent
        child.rect.x += self.rect.x
        child.rect.y += self.rect.y
    
    def remove_child(self, child: 'UIComponent') -> None:
        """
        Remove a child component from this component.
        
        Args:
            child: Child component to remove
        """
        if child in self.children:
            child.parent = None
            self.children.remove(child)
            
            # Update child's rect to be absolute
            child.rect.x -= self.rect.x
            child.rect.y -= self.rect.y
    
    def get_child_by_id(self, component_id: str) -> Optional['UIComponent']:
        """
        Find child component by ID.
        
        Args:
            component_id: ID to search for
            
        Returns:
            Child component if found, None otherwise
        """
        for child in self.children:
            if child.component_id == component_id:
                return child
            # Recursively search
            found = child.get_child_by_id(component_id)
            if found:
                return found
        return None
    
    def get_absolute_rect(self) -> pygame.Rect:
        """
        Get absolute rectangle position on screen.
        
        Returns:
            Absolute rectangle considering parent positions
        """
        if self.parent:
            parent_rect = self.parent.get_absolute_rect()
            return pygame.Rect(
                self.rect.x + parent_rect.x,
                self.rect.y + parent_rect.y,
                self.rect.width,
                self.rect.height
            )
        return self.rect
    
    def handle_event(self, event: pygame.event.Event) -> EventResult:
        """
        Handle pygame event with proper delegation.
        
        Event handling order:
        1. Check if component can handle events (visible + enabled)
        2. Delegate to children first (reverse order for proper z-index)
        3. Handle component-specific events
        4. Call registered event handlers
        
        Args:
            event: Pygame event to handle
            
        Returns:
            EventResult indicating if event was handled
        """
        if not self._can_handle_events():
            return EventResult(handled=False)
        
        # Delegate to children first (reverse order for proper z-index)
        for child in reversed(self.children):
            result = child.handle_event(event)
            if result.handled:
                if result.stop_propagation:
                    return result
                return EventResult(handled=True)
        
        # Handle component-specific events
        component_result = self._handle_own_event(event)
        if component_result.handled:
            return component_result
        
        # Call registered event handlers
        event_type = pygame.event.event_name(event.type)
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                handler(event)
            return EventResult(handled=True)
        
        return EventResult(handled=False)
    
    def _can_handle_events(self) -> bool:
        """Check if component can handle events."""
        return self.visible and self.enabled and self.state == ComponentState.ACTIVE
    
    @abstractmethod
    def _handle_own_event(self, event: pygame.event.Event) -> EventResult:
        """
        Handle component-specific events.
        
        This method should be implemented by subclasses to handle
        events specific to that component type.
        
        Args:
            event: Pygame event to handle
            
        Returns:
            EventResult indicating if event was handled
        """
        return EventResult(handled=False)
    
    def update(self, dt: float) -> None:
        """
        Update component and all children.
        
        Args:
            dt: Time delta since last update
        """
        if self.state != ComponentState.ACTIVE:
            return
        
        # Update children first
        for child in self.children:
            child.update(dt)
        
        # Update component-specific logic
        self._update_component(dt)
        
        # Update hover state
        self._update_hover_state()
    
    @abstractmethod
    def _update_component(self, dt: float) -> None:
        """
        Update component-specific logic.
        
        This method should be implemented by subclasses to handle
        component-specific update logic.
        
        Args:
            dt: Time delta since last update
        """
        pass
    
    def _update_hover_state(self) -> None:
        """Update hover state based on mouse position."""
        mouse_pos = pygame.mouse.get_pos()
        absolute_rect = self.get_absolute_rect()
        self._hovered = absolute_rect.collidepoint(mouse_pos)
    
    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw component and all children.
        
        Args:
            screen: Surface to draw on
        """
        if not self.visible or self.state == ComponentState.DESTROYED:
            return
        
        # Create clipping rect for this component
        absolute_rect = self.get_absolute_rect()
        screen.set_clip(absolute_rect)
        
        # Draw component-specific content
        self._draw_self(screen)
        
        # Draw children
        for child in self.children:
            if child.visible:
                child.draw(screen)
        
        # Reset clipping
        screen.set_clip(None)
    
    @abstractmethod
    def _draw_self(self, screen: pygame.Surface) -> None:
        """
        Draw component-specific content.
        
        This method should be implemented by subclasses to handle
        component-specific drawing logic.
        
        Args:
            screen: Surface to draw on
        """
        pass
    
    def add_event_handler(self, event_type: str, handler: Callable[[pygame.event.Event], None]) -> None:
        """
        Add event handler for specific event type.
        
        Args:
            event_type: Pygame event type name
            handler: Handler function
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def remove_event_handler(self, event_type: str, handler: Callable[[pygame.event.Event], None]) -> None:
        """
        Remove event handler for specific event type.
        
        Args:
            event_type: Pygame event type name
            handler: Handler function to remove
        """
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type].remove(handler)
            except ValueError:
                pass
    
    def show(self) -> None:
        """Show component."""
        self.visible = True
        self.state = ComponentState.ACTIVE
    
    def hide(self) -> None:
        """Hide component."""
        self.visible = False
        self.state = ComponentState.HIDDEN
    
    def enable(self) -> None:
        """Enable component."""
        self.enabled = True
        if self.visible:
            self.state = ComponentState.ACTIVE
    
    def disable(self) -> None:
        """Disable component."""
        self.enabled = False
        self.state = ComponentState.DISABLED
    
    def focus(self) -> None:
        """Set component focus."""
        self.focused = True
        # Remove focus from siblings
        if self.parent:
            for sibling in self.parent.children:
                if sibling != self:
                    sibling.focused = False
    
    def unfocus(self) -> None:
        """Remove component focus."""
        self.focused = False
    
    def destroy(self) -> None:
        """Destroy component and all children."""
        self.state = ComponentState.DESTROYED
        
        # Destroy children
        for child in self.children[:]:  # Copy list to avoid modification during iteration
            child.destroy()
        
        # Remove from parent
        if self.parent:
            self.parent.remove_child(self)
        
        # Call destroy callback
        if self.on_destroy:
            self.on_destroy()
    
    def get_properties(self) -> Dict[str, Any]:
        """
        Get component properties for debugging/serialization.
        
        Returns:
            Dictionary of component properties
        """
        return {
            "component_id": self.component_id,
            "type": self.__class__.__name__,
            "rect": str(self.rect),
            "visible": self.visible,
            "enabled": self.enabled,
            "state": self.state.value,
            "children_count": len(self.children),
            "hovered": self._hovered,
            "focused": self.focused
        }
    
    def __str__(self) -> str:
        """String representation of component."""
        return f"{self.__class__.__name__}(id='{self.component_id}', rect={self.rect})"
    
    def __repr__(self) -> str:
        """Detailed string representation of component."""
        return f"{self.__class__.__name__}(id='{self.component_id}', rect={self.rect}, state={self.state.value})"


class ContainerComponent(UIComponent):
    """
    Base container component for layout management.
    
    Responsibility: Manage child component layout and positioning.
    """
    
    def __init__(self, rect: pygame.Rect, style: Optional[Style] = None, component_id: str = ""):
        super().__init__(rect, style, component_id)
        self.layout_dirty = True
        self.padding = 10
        self.spacing = 5
    
    def add_child(self, child: UIComponent) -> None:
        """Add child and mark layout as dirty."""
        super().add_child(child)
        self.layout_dirty = True
    
    def remove_child(self, child: UIComponent) -> None:
        """Remove child and mark layout as dirty."""
        super().remove_child(child)
        self.layout_dirty = True
    
    def _update_component(self, dt: float) -> None:
        """Update layout if dirty."""
        if self.layout_dirty:
            self._recalculate_layout()
            self.layout_dirty = False
    
    @abstractmethod
    def _recalculate_layout(self) -> None:
        """
        Recalculate child positions based on layout type.
        
        This method should be implemented by subclasses to handle
        specific layout calculations (vertical, horizontal, grid, etc.).
        """
        pass
    
    def _handle_own_event(self, event: pygame.event.Event) -> EventResult:
        """Containers typically don't handle their own events."""
        return EventResult(handled=False)
    
    def _draw_self(self, screen: pygame.Surface) -> None:
        """Containers typically don't draw their own content."""
        pass


class InteractiveComponent(UIComponent):
    """
    Base interactive component for user interaction.
    
    Responsibility: Handle user input and interaction states.
    """
    
    def __init__(self, rect: pygame.Rect, style: Optional[Style] = None, component_id: str = ""):
        super().__init__(rect, style, component_id)
        self.interactive = True
        self.tab_index = -1  # For keyboard navigation
    
    def _can_handle_events(self) -> bool:
        """Interactive components can handle events even if disabled (for visual feedback)."""
        return self.visible and self.state in [ComponentState.ACTIVE, ComponentState.DISABLED]
    
    @abstractmethod
    def _handle_own_event(self, event: pygame.event.Event) -> EventResult:
        """Handle interaction-specific events."""
        return EventResult(handled=False)


class DisplayComponent(UIComponent):
    """
    Base display component for pure rendering.
    
    Responsibility: Display content without interaction.
    """
    
    def __init__(self, rect: pygame.Rect, style: Optional[Style] = None, component_id: str = ""):
        super().__init__(rect, style, component_id)
        self.interactive = False
    
    def _can_handle_events(self) -> bool:
        """Display components don't handle events."""
        return False
    
    def _handle_own_event(self, event: pygame.event.Event) -> EventResult:
        """Display components don't handle events."""
        return EventResult(handled=False)
