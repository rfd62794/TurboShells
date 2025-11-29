"""
Base class for all input components with shared functionality.
"""

import pygame
import pygame_gui
from typing import Optional, Dict, Any, Callable
from ...base_component import BaseComponent


class BaseInputComponent(BaseComponent):
    """Base class for all input components with shared functionality."""
    
    def __init__(self, rect: pygame.Rect, action: str, manager=None, container=None, config=None):
        """Initialize base input component.
        
        Args:
            rect: Component position and size
            action: Action identifier
            manager: pygame_gui UIManager
            container: pygame_gui container (optional)
            config: Configuration options
        """
        super().__init__(rect, manager)
        self.action = action
        self.config = config or {}
        self.container = container
        
        # Common callback system
        self.on_action: Optional[Callable[[str], None]] = None
        
        # Auto-sizing options (shared)
        self.auto_resize = self.config.get('auto_resize', False)
        self.min_width = self.config.get('min_width', rect.width)
        self.padding = self.config.get('padding', 20)
        
        # The pygame_gui element (to be set by subclasses)
        self.ui_element: Optional[Any] = None
        
    def render(self, surface: pygame.Surface) -> None:
        """Render component (handled by pygame_gui)."""
        # Most pygame_gui elements render automatically
        pass
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events."""
        return self._handle_component_event(event)
        
    def _handle_component_event(self, event: pygame.event.Event) -> bool:
        """Handle component-specific events. Override in subclasses."""
        return False
        
    def _emit_action_event(self, additional_data: Optional[Dict] = None) -> None:
        """Emit the standard action event."""
        event_data = {'action': self.action}
        if additional_data:
            event_data.update(additional_data)
        self._emit_event('action', event_data)
        
        # Call action callback
        if self.on_action:
            self.on_action(self.action)
            
    def set_action_callback(self, callback: Callable[[str], None]) -> None:
        """Set action callback."""
        self.on_action = callback
        
    def _calculate_optimal_rect(self) -> pygame.Rect:
        """Calculate the optimal size based on content. Override in subclasses."""
        if not self.manager:
            return self.rect
            
        # Default implementation - subclasses should override
        return self.rect
        
    def _recreate_element_with_new_size(self) -> None:
        """Recreate the UI element with optimal size. Override in subclasses."""
        # Subclasses should implement this to handle auto-sizing
        pass
        
    def set_enabled(self, enabled: bool) -> None:
        """Set component enabled state."""
        super().set_enabled(enabled)
        if self.ui_element:
            if hasattr(self.ui_element, 'enable'):
                if enabled:
                    self.ui_element.enable()
                else:
                    self.ui_element.disable()
                    
    def is_enabled(self) -> bool:
        """Check if component is enabled."""
        if self.ui_element and hasattr(self.ui_element, 'is_enabled'):
            return self.ui_element.is_enabled
        return super().is_enabled()
        
    def show(self) -> None:
        """Show the component."""
        super().show()
        if self.ui_element and hasattr(self.ui_element, 'show'):
            self.ui_element.show()
            
    def hide(self) -> None:
        """Hide the component."""
        super().hide()
        if self.ui_element and hasattr(self.ui_element, 'hide'):
            self.ui_element.hide()
            
    def destroy(self) -> None:
        """Clean up component resources."""
        if self.ui_element and hasattr(self.ui_element, 'kill'):
            self.ui_element.kill()
        super().destroy()
