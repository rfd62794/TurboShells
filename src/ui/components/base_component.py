"""
Base component class for UI components following SRP.
"""

import pygame
from abc import ABC, abstractmethod
from typing import Optional, List, Any, Tuple, Dict
from pygame_gui import UIManager


class BaseComponent(ABC):
    """Base class for all UI components following Single Responsibility Principle."""
    
    def __init__(self, rect: pygame.Rect, manager: Optional[UIManager] = None, container=None):
        """Initialize base component.
        
        Args:
            rect: Component position and size
            manager: pygame_gui UIManager instance
            container: pygame_gui container for this component
        """
        self.rect = rect
        self.manager = manager
        self.container = container
        self.visible = True
        self.enabled = True
        self.parent: Optional['BaseComponent'] = None
        self.children: List['BaseComponent'] = []
        self.event_handlers: Dict[str, List[callable]] = {}
        
    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        """Render the component. Must be implemented by subclasses."""
        pass
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events. Return True if event was consumed."""
        # Let children handle events first
        for child in self.children:
            if child.handle_event(event):
                return True
                
        # Handle component-specific events
        return self._handle_component_event(event)
        
    def _handle_component_event(self, event: pygame.event.Event) -> bool:
        """Handle component-specific events. Override in subclasses."""
        return False
        
    def add_child(self, child: 'BaseComponent') -> None:
        """Add a child component."""
        child.parent = self
        self.children.append(child)
        
    def remove_child(self, child: 'BaseComponent') -> None:
        """Remove a child component."""
        if child in self.children:
            child.parent = None
            self.children.remove(child)
            
    def get_absolute_rect(self) -> pygame.Rect:
        """Get absolute rect accounting for parent positions."""
        if self.parent:
            parent_rect = self.parent.get_absolute_rect()
            return pygame.Rect(
                self.rect.x + parent_rect.x,
                self.rect.y + parent_rect.y,
                self.rect.width,
                self.rect.height
            )
        return self.rect
        
    def set_visible(self, visible: bool) -> None:
        """Set component visibility."""
        self.visible = visible
        for child in self.children:
            child.set_visible(visible)
            
    def set_enabled(self, enabled: bool) -> None:
        """Set component enabled state."""
        self.enabled = enabled
        for child in self.children:
            child.set_enabled(enabled)
            
    def add_event_handler(self, event_type: str, handler: callable) -> None:
        """Add an event handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        
    def remove_event_handler(self, event_type: str, handler: callable) -> None:
        """Remove an event handler."""
        if event_type in self.event_handlers:
            if handler in self.event_handlers[event_type]:
                self.event_handlers[event_type].remove(handler)
                
    def _emit_event(self, event_type: str, data: Any = None) -> None:
        """Emit an event to registered handlers."""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                handler(data)
                
    def update(self, dt: float) -> None:
        """Update component and children. Override in subclasses."""
        for child in self.children:
            child.update(dt)
            
    def destroy(self) -> None:
        """Clean up component and children."""
        for child in self.children:
            child.destroy()
        self.children.clear()
        self.event_handlers.clear()
