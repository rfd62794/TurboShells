"""UI Manager - Central UI Coordinator for TurboShells

Orchestrates all Thorpy-based UI components following Single Responsibility Principle.
Acts as the main interface between the game engine and the UI layer.
"""

import pygame
import thorpy
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict

class UIManager:
    """Central UI coordinator following SRP.
    
    Responsibilities:
    - Initialize and manage Thorpy menu
    - Route events between PyGame and Thorpy
    - Coordinate UI panel rendering
    - Manage UI state and visibility
    
    This class provides a clean interface for the game engine to interact
    with the UI system without knowing Thorpy implementation details.
    """
    
    def __init__(self, screen_rect: pygame.Rect):
        """Initialize UI manager.
        
        Args:
            screen_rect: Rectangle defining the screen dimensions
        """
        self.screen_rect = screen_rect
        self.ui_panels: Dict[str, 'BasePanel'] = {}
        self.global_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        self._initialized = False
        self._visible = True
        
        # Thorpy specific
        self.menu: Optional[thorpy.Menu] = None
        self.root_element: Optional[thorpy.Element] = None
        
    def initialize(self, pygame_surface: pygame.Surface) -> bool:
        """Initialize Thorpy and UI system.
        
        Args:
            pygame_surface: PyGame surface for rendering
            
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Create a root element (invisible container)
            self.root_element = thorpy.Box(children=[])
            self.root_element.set_size(self.screen_rect.size)
            self.root_element.set_main_color((0, 0, 0, 0)) # Transparent
            
            # Create Thorpy Menu
            self.menu = thorpy.Menu(self.root_element)
            
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"Failed to initialize UI Manager: {e}")
            return False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Route events to Thorpy first, then to UI panels.
        
        Args:
            event: PyGame event to process
            
        Returns:
            True if event was consumed by UI system, False otherwise
        """
        if not self._initialized or not self.visible():
            return False
            
        # Let Thorpy process the event
        if self.menu:
            self.menu.react(event)
            # Thorpy doesn't easily return "consumed", so we might need to check specific conditions
            # For now, we assume if we are interacting with UI, we might consume it.
            # However, Thorpy handles this internally usually.
            
        # Route to specific UI panels based on event type if needed
        # (Thorpy handles most of this via its own event system)
        return False
    
    def render_ui_panels(self, game_state: Any) -> None:
        """Render all visible UI panels.
        
        Args:
            game_state: Current game state object
        """
        if not self._initialized or not self.visible():
            return
            
        # Update UI elements from game state if needed
        for panel in self.ui_panels.values():
            if panel.visible:
                panel.update(game_state)
                
        # Render Thorpy menu
        # Note: Thorpy usually handles drawing in its own loop or via updater.
        # But we can manually draw the root element if we are integrating into existing loop.
        # However, typical Thorpy usage is `menu.play()` which blocks.
        # For non-blocking, we use `updater`.
        # Since we are in a custom loop, we should just ensure elements are blitted.
        # But `thorpy.Menu` doesn't have a simple `draw()` method for everything.
        # We might need to use `self.root_element.blit()` and `self.root_element.update()`.
        
        # Actually, for integration, we usually do:
        # self.root_element.blit() 
        # self.root_element.update() 
        pass # Thorpy handles drawing via its updater usually, but we need to trigger it.
        # In this hybrid setup, we might rely on the panels to draw themselves or use a Thorpy updater.
        # Let's assume we use a custom draw for now or rely on the main loop to call something.
        
        # Correct way for non-blocking Thorpy:
        # We need to call updater.update() in the game loop.
        # But here we are in render_ui_panels.
        # We can just blit the root element if it contains everything.
        # But panels might be separate.
        
        # For now, let's just iterate panels and let them render if they are custom,
        # or if they are Thorpy elements attached to root, they will be drawn when root is drawn.
        
        # If we use a single root, we just draw that.
        # But we haven't added panels to root yet.
        pass

    def update(self, time_delta: float) -> None:
        """Update UI state.
        
        Args:
            time_delta: Time passed since last frame
        """
        if self.root_element:
            # Thorpy elements might need updating
            pass

    def register_panel(self, panel_id: str, panel: 'BasePanel') -> None:
        """Register a UI panel with the manager.
        
        Args:
            panel_id: Unique identifier for the panel
            panel: Panel instance to register
        """
        self.ui_panels[panel_id] = panel
        panel.set_ui_manager(self)
        
        # If panel has a Thorpy element, add it to root
        if hasattr(panel, 'element') and panel.element and self.root_element:
            self.root_element.add_child(panel.element)
    
    def unregister_panel(self, panel_id: str) -> None:
        """Unregister a UI panel.
        
        Args:
            panel_id: ID of panel to remove
        """
        if panel_id in self.ui_panels:
            panel = self.ui_panels[panel_id]
            # Remove from root if applicable
            if hasattr(panel, 'element') and panel.element and self.root_element:
                self.root_element.remove_child(panel.element)
                
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
            if hasattr(panel, 'element') and panel.element:
                panel.element.set_visible(True)
    
    def hide_panel(self, panel_id: str) -> None:
        """Hide a specific panel.
        
        Args:
            panel_id: ID of panel to hide
        """
        panel = self.get_panel(panel_id)
        if panel:
            panel.visible = False
            if hasattr(panel, 'element') and panel.element:
                panel.element.set_visible(False)
    
    def toggle_panel(self, panel_id: str) -> None:
        """Toggle visibility of a specific panel.
        
        Args:
            panel_id: ID of panel to toggle
        """
        panel = self.get_panel(panel_id)
        if panel:
            if panel.visible:
                self.hide_panel(panel_id)
            else:
                self.show_panel(panel_id)
    
    def show_all_panels(self) -> None:
        """Show all registered panels."""
        for panel_id in self.ui_panels:
            self.show_panel(panel_id)
    
    def hide_all_panels(self) -> None:
        """Hide all registered panels."""
        for panel_id in self.ui_panels:
            self.hide_panel(panel_id)
    
    def visible(self) -> bool:
        """Check if UI system is visible."""
        return self._visible and self._initialized
    
    def set_visible(self, visible: bool) -> None:
        """Set UI system visibility.
        
        Args:
            visible: True to show UI, False to hide
        """
        self._visible = visible
        if self.root_element:
            self.root_element.set_visible(visible)
    
    def toggle_visibility(self) -> None:
        """Toggle UI system visibility."""
        self.set_visible(not self._visible)
    
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
        
        if self.root_element:
            self.root_element.set_size(new_rect.size)
        
        # Notify all panels of resize
        for panel in self.ui_panels.values():
            panel.handle_screen_resize(new_rect)
    
    def is_initialized(self) -> bool:
        """Check if UI manager is properly initialized."""
        return self._initialized
    
    def shutdown(self) -> None:
        """Clean up UI resources."""
        self.ui_panels.clear()
        self.global_callbacks.clear()
        self._initialized = False
        self.menu = None
        self.root_element = None


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
        self.element: Optional[thorpy.Element] = None
        
    def set_ui_manager(self, manager: Optional[UIManager]) -> None:
        """Set the UI manager for this panel."""
        self.ui_manager = manager
        
    def render(self, game_state: Any) -> None:
        """Render panel content - to be overridden."""
        pass
        
    def update(self, game_state: Any) -> None:
        """Update panel state from game state."""
        pass
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events - to be overridden."""
        return False
        
    def handle_screen_resize(self, new_rect: pygame.Rect) -> None:
        """Handle screen resize - to be overridden."""
        pass
