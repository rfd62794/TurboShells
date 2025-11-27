"""UI Manager - Central UI Coordinator for TurboShells

Orchestrates all ImGui-based UI components following Single Responsibility Principle.
Acts as the main interface between the game engine and the UI layer.
"""

import pygame
import imgui
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict

from .imgui_context import ImGuiContext


class UIManager:
    """Central UI coordinator following SRP.
    
    Responsibilities:
    - Initialize and manage ImGui context
    - Route events between PyGame and ImGui
    - Coordinate UI panel rendering
    - Manage UI state and visibility
    
    This class provides a clean interface for the game engine to interact
    with the UI system without knowing ImGui implementation details.
    """
    
    def __init__(self, screen_rect: pygame.Rect):
        """Initialize UI manager.
        
        Args:
            screen_rect: Rectangle defining the screen dimensions
        """
        self.screen_rect = screen_rect
        self.imgui_context: Optional[ImGuiContext] = None
        self.ui_panels: Dict[str, 'BasePanel'] = {}
        self.global_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        self._initialized = False
        self._visible = True
        
    def initialize(self, pygame_surface: pygame.Surface) -> bool:
        """Initialize ImGui and UI system.
        
        Args:
            pygame_surface: PyGame surface for rendering
            
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Create ImGui context
            self.imgui_context = ImGuiContext(pygame_surface)
            
            if not self.imgui_context.initialize():
                return False
                
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"Failed to initialize UI Manager: {e}")
            return False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Route events to ImGui first, then to UI panels.
        
        Args:
            event: PyGame event to process
            
        Returns:
            True if event was consumed by UI system, False otherwise
        """
        if not self._initialized or not self.visible():
            return False
            
        # Let ImGui process the event first
        if self.imgui_context and self.imgui_context.handle_event(event):
            return True
            
        # Route to specific UI panels based on event type
        for panel in self.ui_panels.values():
            if panel.visible and panel.handle_event(event):
                return True
                
        return False
    
    def render_ui_panels(self, game_state: Any) -> None:
        """Render all visible UI panels.
        
        Args:
            game_state: Current game state object
        """
        if not self._initialized or not self.visible():
            return
            
        # Begin ImGui frame
        self.imgui_context.begin_frame()
        
        # Render each visible panel
        for panel in self.ui_panels.values():
            if panel.visible:
                panel.render(game_state)
        
        # End ImGui frame and render
        self.imgui_context.end_frame()
    
    def register_panel(self, panel_id: str, panel: 'BasePanel') -> None:
        """Register a UI panel with the manager.
        
        Args:
            panel_id: Unique identifier for the panel
            panel: Panel instance to register
        """
        self.ui_panels[panel_id] = panel
        panel.set_ui_manager(self)
    
    def unregister_panel(self, panel_id: str) -> None:
        """Unregister a UI panel.
        
        Args:
            panel_id: ID of panel to remove
        """
        if panel_id in self.ui_panels:
            panel = self.ui_panels[panel_id]
            panel.set_ui_manager(None)
            del self.ui_panels[panel_id]
    
    def get_panel(self, panel_id: str) -> Optional['BasePanel']:
        """Get a registered panel by ID.
        
        Args:
            panel_id: ID of panel to retrieve
            
        Returns:
            Panel instance if found, None otherwise
        """
        return self.ui_panels.get(panel_id)
    
    def show_panel(self, panel_id: str) -> None:
        """Show a specific panel.
        
        Args:
            panel_id: ID of panel to show
        """
        panel = self.get_panel(panel_id)
        if panel:
            panel.visible = True
    
    def hide_panel(self, panel_id: str) -> None:
        """Hide a specific panel.
        
        Args:
            panel_id: ID of panel to hide
        """
        panel = self.get_panel(panel_id)
        if panel:
            panel.visible = False
    
    def toggle_panel(self, panel_id: str) -> None:
        """Toggle visibility of a specific panel.
        
        Args:
            panel_id: ID of panel to toggle
        """
        panel = self.get_panel(panel_id)
        if panel:
            panel.visible = not panel.visible
    
    def show_all_panels(self) -> None:
        """Show all registered panels."""
        for panel in self.ui_panels.values():
            panel.visible = True
    
    def hide_all_panels(self) -> None:
        """Hide all registered panels."""
        for panel in self.ui_panels.values():
            panel.visible = False
    
    def visible(self) -> bool:
        """Check if UI system is visible."""
        return self._visible and self._initialized
    
    def set_visible(self, visible: bool) -> None:
        """Set UI system visibility.
        
        Args:
            visible: True to show UI, False to hide
        """
        self._visible = visible
    
    def toggle_visibility(self) -> None:
        """Toggle UI system visibility."""
        self._visible = not self._visible
    
    def register_global_callback(self, event_type: str, callback: Callable) -> None:
        """Register a global callback for UI events.
        
        Args:
            event_type: Type of event (e.g., 'button_click', 'slider_change')
            callback: Function to call when event occurs
        """
        self.global_callbacks[event_type].append(callback)
    
    def trigger_global_callback(self, event_type: str, *args, **kwargs) -> None:
        """Trigger all callbacks for a specific event type.
        
        Args:
            event_type: Type of event to trigger
            *args: Arguments to pass to callbacks
            **kwargs: Keyword arguments to pass to callbacks
        """
        for callback in self.global_callbacks[event_type]:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"Error in UI callback: {e}")
    
    def handle_screen_resize(self, new_rect: pygame.Rect) -> None:
        """Handle screen resize events.
        
        Args:
            new_rect: New screen rectangle
        """
        self.screen_rect = new_rect
        
        if self.imgui_context:
            width, height = new_rect.width, new_rect.height
            self.imgui_context.set_display_size(width, height)
        
        # Notify all panels of resize
        for panel in self.ui_panels.values():
            panel.handle_screen_resize(new_rect)
    
    def is_initialized(self) -> bool:
        """Check if UI manager is properly initialized."""
        return self._initialized and self.imgui_context is not None
    
    def shutdown(self) -> None:
        """Clean up UI resources."""
        if self.imgui_context:
            self.imgui_context.shutdown()
            self.imgui_context = None
            
        self.ui_panels.clear()
        self.global_callbacks.clear()
        self._initialized = False


# Forward declaration for BasePanel
class BasePanel:
    """Base class for all UI panels."""
    
    def __init__(self, panel_id: str, title: str = ""):
        self.panel_id = panel_id
        self.title = title
        self.visible = True
        self.position = (0, 0)
        self.size = (300, 200)
        self.ui_manager: Optional[UIManager] = None
        
    def set_ui_manager(self, manager: Optional[UIManager]) -> None:
        """Set the UI manager for this panel."""
        self.ui_manager = manager
        
    def render(self, game_state: Any) -> None:
        """Render panel content - to be overridden."""
        raise NotImplementedError
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events - to be overridden."""
        return False
        
    def handle_screen_resize(self, new_rect: pygame.Rect) -> None:
        """Handle screen resize - to be overridden."""
        pass
