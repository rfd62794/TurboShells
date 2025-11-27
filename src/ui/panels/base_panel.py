"""Base Panel System for TurboShells Thorpy UI

Foundation for all UI panels following Single Responsibility Principle.
Provides common functionality and consistent interface for all panels.
"""

import pygame
import thorpy
from typing import Optional, Dict, Any, Callable, Tuple, List
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum


class PanelState(Enum):
    """Panel visibility and interaction states."""
    HIDDEN = "hidden"
    MINIMIZED = "minimized"
    NORMAL = "normal"
    FOCUSED = "focused"


@dataclass
class PanelStyle:
    """Styling configuration for panels."""
    title_color: Tuple[int, int, int] = (255, 255, 255)
    background_color: Tuple[int, int, int, int] = (25, 25, 40, 230)
    border_color: Tuple[int, int, int] = (76, 76, 102)
    padding: Tuple[int, int] = (10, 10)
    rounding: float = 5.0
    flags: int = 0


class BasePanel(ABC):
    """Base class for all UI panels with SRP.
    
    Responsibilities:
    - Manage panel lifecycle and state
    - Handle common Thorpy element operations
    - Provide event handling interface
    - Support data binding framework
    - Maintain consistent styling behavior
    
    This abstract class ensures all panels follow the same interface
    and behavior patterns while allowing specific implementations.
    """
    
    def __init__(self, panel_id: str, title: str = "", style: Optional[PanelStyle] = None):
        """Initialize base panel.
        
        Args:
            panel_id: Unique identifier for the panel
            title: Display title for the panel
            style: Optional styling configuration
        """
        self.panel_id = panel_id
        self.title = title
        self.style = style or PanelStyle()
        
        # State management
        self.state = PanelState.NORMAL
        self.visible = True
        self.enabled = True
        self.focused = False
        
        # Position and size
        self.position = (100, 100)
        self.size = (300, 200)
        
        # UI Manager reference
        self.ui_manager: Optional['UIManager'] = None
        
        # Data bindings
        self.data_bindings: Dict[str, Any] = {}
        self.change_callbacks: Dict[str, List[Callable]] = {}
        
        # Thorpy element
        self.element: Optional[thorpy.Element] = None
        self._create_element()
        
    def _create_element(self) -> None:
        """Create the Thorpy element for this panel."""
        # Default implementation creates a draggable box (window-like)
        self.element = thorpy.Draggable(text=self.title)
        self.element.set_size(self.size)
        self.element.set_topleft(self.position)
        # Apply style
        # Thorpy styling is different, we can set main color etc.
        # self.element.set_main_color(self.style.background_color)
        
    def set_ui_manager(self, manager: Optional['UIManager']) -> None:
        """Set the UI manager for this panel.
        
        Args:
            manager: UI manager instance or None
        """
        self.ui_manager = manager
    
    def render(self, game_state: Any) -> None:
        """Render the panel and its children.
        
        Args:
            game_state: Current game state object
        """
        # Thorpy handles rendering via updater, but if we need manual updates:
        pass
        
    def update(self, game_state: Any) -> None:
        """Update panel content from game state.
        
        Args:
            game_state: Current game state object
        """
        pass
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events specific to this panel.
        
        Args:
            event: PyGame event to handle
            
        Returns:
            True if event was consumed, False otherwise
        """
        # Thorpy handles events via menu.react(), but we can add custom logic here
        return False
    
    def handle_screen_resize(self, new_rect: pygame.Rect) -> None:
        """Handle screen resize events.
        
        Args:
            new_rect: New screen rectangle
        """
        # Adjust panel position if needed
        screen_width, screen_height = new_rect.width, new_rect.height
        
        if self.element:
            # Ensure panel stays on screen
            rect = self.element.get_rect()
            x, y = rect.x, rect.y
            w, h = rect.width, rect.height
            
            new_x = min(x, screen_width - w)
            new_y = min(y, screen_height - h)
            
            if new_x != x or new_y != y:
                self.element.set_topleft((max(0, new_x), max(0, new_y)))
    
    # Data binding methods
    def bind_data(self, key: str, data_source: Any) -> None:
        """Bind UI element to game data.
        
        Args:
            key: Data binding key
            data_source: Data source object
        """
        self.data_bindings[key] = data_source
    
    def get_bound_data(self, key: str, default: Any = None) -> Any:
        """Get bound data value.
        
        Args:
            key: Data binding key
            default: Default value if not found
            
        Returns:
            Bound data value or default
        """
        return self.data_bindings.get(key, default)
    
    def set_bound_data(self, key: str, value: Any) -> None:
        """Set bound data value and trigger callbacks.
        
        Args:
            key: Data binding key
            value: New value to set
        """
        if key in self.data_bindings:
            old_value = self.data_bindings[key]
            self.data_bindings[key] = value
            
            # Trigger change callbacks
            for callback in self.change_callbacks.get(key, []):
                try:
                    callback(old_value, value)
                except Exception as e:
                    print(f"Error in data change callback: {e}")
    
    def register_change_callback(self, key: str, callback: Callable) -> None:
        """Register callback for data changes.
        
        Args:
            key: Data binding key
            callback: Callback function (old_value, new_value) -> None
        """
        if key not in self.change_callbacks:
            self.change_callbacks[key] = []
        self.change_callbacks[key].append(callback)
    
    # State management methods
    def show(self) -> None:
        """Show the panel."""
        self.visible = True
        self.state = PanelState.NORMAL
        if self.element:
            self.element.set_visible(True)
    
    def hide(self) -> None:
        """Hide the panel."""
        self.visible = False
        self.state = PanelState.HIDDEN
        if self.element:
            self.element.set_visible(False)
    
    def toggle_visibility(self) -> None:
        """Toggle panel visibility."""
        if self.visible:
            self.hide()
        else:
            self.show()
    
    def is_visible(self) -> bool:
        """Check if panel is visible.
        
        Returns:
            True if visible, False otherwise
        """
        return self.visible and self.state != PanelState.HIDDEN
    
    # Utility methods
    def get_screen_rect(self) -> pygame.Rect:
        """Get panel screen rectangle.
        
        Returns:
            Rectangle representing panel position and size
        """
        if self.element:
            return self.element.get_rect()
        return pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])
    
    def contains_point(self, point: Tuple[int, int]) -> bool:
        """Check if point is within panel bounds.
        
        Args:
            point: Point to check (x, y)
            
        Returns:
            True if point is within panel, False otherwise
        """
        return self.get_screen_rect().collidepoint(point)
