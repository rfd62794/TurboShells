"""Base Panel System for TurboShells ImGui UI

Foundation for all UI panels following Single Responsibility Principle.
Provides common functionality and consistent interface for all panels.
"""

import pygame
import imgui
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
    title_color: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    background_color: Tuple[float, float, float, float] = (0.1, 0.1, 0.15, 0.9)
    border_color: Tuple[float, float, float] = (0.3, 0.3, 0.4)
    padding: Tuple[int, int] = (10, 10)
    rounding: float = 5.0
    flags: int = 0


class BasePanel(ABC):
    """Base class for all UI panels with SRP.
    
    Responsibilities:
    - Manage panel lifecycle and state
    - Handle common ImGui window operations
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
        self.auto_resize = True
        
        # UI Manager reference
        self.ui_manager: Optional['UIManager'] = None
        
        # Data bindings
        self.data_bindings: Dict[str, Any] = {}
        self.change_callbacks: Dict[str, List[Callable]] = {}
        
        # Child components
        self.children: List['BasePanel'] = []
        self.parent: Optional['BasePanel'] = None
        
        # ImGui-specific state
        self._imgui_window_open = True
        self._last_frame_visible = False
        
    def set_ui_manager(self, manager: Optional['UIManager']) -> None:
        """Set the UI manager for this panel.
        
        Args:
            manager: UI manager instance or None
        """
        self.ui_manager = manager
        
        # Propagate to children
        for child in self.children:
            child.set_ui_manager(manager)
    
    def render(self, game_state: Any) -> None:
        """Render the panel and its children.
        
        Args:
            game_state: Current game state object
        """
        if not self.visible or self.state == PanelState.HIDDEN:
            self._last_frame_visible = False
            return
        
        self._last_frame_visible = True
        
        # Set up window properties
        self._setup_window_properties()
        
        # Begin ImGui window
        expanded, opened = imgui.begin(self._get_window_title(), self._imgui_window_open, self.style.flags)
        
        # Update open state
        self._imgui_window_open = opened
        if not opened:
            self.visible = False
        
        # Update focus state
        self.focused = imgui.is_window_focused()
        
        if expanded:
            # Apply panel styling
            self._apply_styling()
            
            # Render panel content
            self.render_content(game_state)
            
            # Render child panels
            self._render_children(game_state)
        
        # End ImGui window
        imgui.end()
        
        # Handle post-render logic
        self._post_render(game_state)
    
    @abstractmethod
    def render_content(self, game_state: Any) -> None:
        """Render panel-specific content.
        
        Args:
            game_state: Current game state object
            
        Note:
            This method must be implemented by subclasses
        """
        pass
    
    def _setup_window_properties(self) -> None:
        """Set up ImGui window properties."""
        if self.auto_resize:
            imgui.set_next_window_size(self.size[0], self.size[1])
        else:
            imgui.set_next_window_size_constraints(
                (self.size[0], self.size[1]),
                (self.size[0] * 2, self.size[1] * 2)
            )
        
        imgui.set_next_window_position(self.position[0], self.position[1])
    
    def _get_window_title(self) -> str:
        """Get the window title with state indicators.
        
        Returns:
            Window title string
        """
        title = self.title
        if not title:
            title = self.panel_id.replace('_', ' ').title()
        
        # Add state indicators
        if self.state == PanelState.MINIMIZED:
            title += " [Minimized]"
        elif self.state == PanelState.FOCUSED:
            title += " [Focused]"
        
        return title
    
    def _apply_styling(self) -> None:
        """Apply panel-specific styling."""
        # This could apply custom colors, fonts, etc.
        # For now, we'll rely on the global style
        pass
    
    def _render_children(self, game_state: Any) -> None:
        """Render child panels.
        
        Args:
            game_state: Current game state object
        """
        for child in self.children:
            if child.visible:
                child.render(game_state)
    
    def _post_render(self, game_state: Any) -> None:
        """Handle post-render logic.
        
        Args:
            game_state: Current game state object
        """
        # Update position and size from ImGui
        if self._last_frame_visible:
            pos = imgui.get_window_position()
            size = imgui.get_window_size()
            self.position = (int(pos.x), int(pos.y))
            self.size = (int(size.x), int(size.y))
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events specific to this panel.
        
        Args:
            event: PyGame event to handle
            
        Returns:
            True if event was consumed, False otherwise
        """
        # Let children handle events first
        for child in self.children:
            if child.visible and child.handle_event(event):
                return True
        
        # Handle panel-specific events
        return self._handle_panel_event(event)
    
    def _handle_panel_event(self, event: pygame.event.Event) -> bool:
        """Handle panel-specific events.
        
        Args:
            event: PyGame event to handle
            
        Returns:
            True if event was consumed, False otherwise
        """
        # Default implementation doesn't handle any events
        return False
    
    def handle_screen_resize(self, new_rect: pygame.Rect) -> None:
        """Handle screen resize events.
        
        Args:
            new_rect: New screen rectangle
        """
        # Adjust panel position if needed
        screen_width, screen_height = new_rect.width, new_rect.height
        panel_right = self.position[0] + self.size[0]
        panel_bottom = self.position[1] + self.size[1]
        
        # Keep panel on screen
        if panel_right > screen_width:
            self.position = (screen_width - self.size[0] - 10, self.position[1])
        
        if panel_bottom > screen_height:
            self.position = (self.position[0], screen_height - self.size[1] - 10)
        
        # Propagate to children
        for child in self.children:
            child.handle_screen_resize(new_rect)
    
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
    
    # Child management methods
    def add_child(self, child: 'BasePanel') -> None:
        """Add a child panel.
        
        Args:
            child: Child panel to add
        """
        if child not in self.children:
            self.children.append(child)
            child.parent = self
            child.set_ui_manager(self.ui_manager)
    
    def remove_child(self, child: 'BasePanel') -> bool:
        """Remove a child panel.
        
        Args:
            child: Child panel to remove
            
        Returns:
            True if child was found and removed, False otherwise
        """
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            child.set_ui_manager(None)
            return True
        return False
    
    # State management methods
    def show(self) -> None:
        """Show the panel."""
        self.visible = True
        self.state = PanelState.NORMAL
        self._imgui_window_open = True
    
    def hide(self) -> None:
        """Hide the panel."""
        self.visible = False
        self.state = PanelState.HIDDEN
    
    def toggle_visibility(self) -> None:
        """Toggle panel visibility."""
        if self.visible:
            self.hide()
        else:
            self.show()
    
    def minimize(self) -> None:
        """Minimize the panel."""
        self.state = PanelState.MINIMIZED
    
    def restore(self) -> None:
        """Restore the panel to normal state."""
        self.state = PanelState.NORMAL
    
    def focus(self) -> None:
        """Focus the panel."""
        self.state = PanelState.FOCUSED
        self.focused = True
    
    def is_visible(self) -> bool:
        """Check if panel is visible.
        
        Returns:
            True if visible, False otherwise
        """
        return self.visible and self.state != PanelState.HIDDEN
    
    def is_focused(self) -> bool:
        """Check if panel has focus.
        
        Returns:
            True if focused, False otherwise
        """
        return self.focused
    
    # Utility methods
    def get_screen_rect(self) -> pygame.Rect:
        """Get panel screen rectangle.
        
        Returns:
            Rectangle representing panel position and size
        """
        return pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])
    
    def contains_point(self, point: Tuple[int, int]) -> bool:
        """Check if point is within panel bounds.
        
        Args:
            point: Point to check (x, y)
            
        Returns:
            True if point is within panel, False otherwise
        """
        return self.get_screen_rect().collidepoint(point)
    
    def get_info(self) -> Dict[str, Any]:
        """Get panel information.
        
        Returns:
            Dictionary with panel information
        """
        return {
            'panel_id': self.panel_id,
            'title': self.title,
            'state': self.state.value,
            'visible': self.visible,
            'enabled': self.enabled,
            'focused': self.focused,
            'position': self.position,
            'size': self.size,
            'children': len(self.children),
            'data_bindings': len(self.data_bindings)
        }
    
    def print_info(self) -> None:
        """Print panel information for debugging."""
        info = self.get_info()
        print(f"=== Panel Info: {self.panel_id} ===")
        for key, value in info.items():
            print(f"  {key}: {value}")
        print("=" * 35)
