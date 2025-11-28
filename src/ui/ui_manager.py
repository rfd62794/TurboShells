import pygame
import pygame_gui
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict

class UIManager:
    """Manages the UI system using pygame_gui.
    
    Handles:
    - UI Manager initialization
    - Event processing
    - UI Rendering
    - Panel management
    """
    
    def __init__(self, screen_rect: pygame.Rect):
        """Initialize UI Manager.
        
        Args:
            screen_rect: Rectangle defining the screen dimensions
        """
        self.screen_rect = screen_rect
        self.manager: Optional[pygame_gui.UIManager] = None
        self._panels: Dict[str, Any] = {}
        self._active_panels: List[str] = []
        self._initialized = False
        
    def initialize(self, surface: pygame.Surface) -> bool:
        """Initialize the UI system.
        
        Args:
            surface: Main display surface
            
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Initialize pygame_gui UIManager
            self.manager = pygame_gui.UIManager(self.screen_rect.size)
            
            self._initialized = True
            print("UI Manager initialized successfully (pygame_gui)")
            return True
            
        except Exception as e:
            print(f"Failed to initialize UI Manager: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Process PyGame event through UI system.
        
        Args:
            event: PyGame event to process
            
        Returns:
            True if event was consumed by UI, False otherwise
        """
        if not self._initialized or not self.manager:
            return False
        
        # Intercept window close events to prevent panel destruction
        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            for panel_id, panel in self._panels.items():
                if hasattr(panel, 'window') and panel.window == event.ui_element:
                    print(f"[UIManager] Intercepting close event for panel '{panel_id}'")
                    # Let the panel handle it with hide instead of destroy
                    panel.handle_event(event)
                    return True  # Consume the event to prevent default destruction
        
        # Pass event to pygame_gui
        consumed = self.manager.process_events(event)
        return consumed
        
    def update(self, time_delta: float) -> None:
        """Update UI state.
        
        Args:
            time_delta: Time passed since last frame in seconds
        """
        if not self._initialized or not self.manager:
            return
            
        self.manager.update(time_delta)
        
        # Update custom panel logic if needed
        for panel_id in self._active_panels:
            panel = self._panels.get(panel_id)
            if panel:
                panel.update(time_delta)

    def render_ui_panels(self, game_state: Any) -> None:
        """Render all active UI panels.
        
        Args:
            game_state: Current game state object
        """
        # pygame_gui rendering is handled by draw_ui, usually called from main loop
        pass

    def draw_ui(self, surface: pygame.Surface) -> None:
        """Draw the UI to the given surface.
        
        Args:
            surface: Surface to draw on
        """
        if self._initialized and self.manager:
            self.manager.draw_ui(surface)

    def register_panel(self, panel_id: str, panel: Any) -> None:
        """Register a UI panel.
        
        Args:
            panel_id: Unique identifier for the panel
            panel: Panel instance
        """
        self._panels[panel_id] = panel
        # Initialize panel with our manager
        if hasattr(panel, 'setup_ui'):
            panel.setup_ui(self.manager)
            
    def unregister_panel(self, panel_id: str) -> None:
        """Unregister a UI panel.
        
        Args:
            panel_id: ID of panel to remove
        """
        if panel_id in self._panels:
            # Cleanup panel resources
            panel = self._panels[panel_id]
            if hasattr(panel, 'destroy'):
                panel.destroy()
            del self._panels[panel_id]
            
        if panel_id in self._active_panels:
            self._active_panels.remove(panel_id)
            
    def show_panel(self, panel_id: str) -> None:
        """Show a specific panel by ID."""
        panel = self._panels.get(panel_id)
        if not panel:
            print(f"[UIManager] show_panel: Panel '{panel_id}' not found")
            return
        print(f"[UIManager] show_panel: Showing panel '{panel_id}'")
        panel.show()
            
                
    def hide_panel(self, panel_id: str) -> None:
        """Hide a registered panel.
        
        Args:
            panel_id: ID of panel to hide
        """
        panel = self._panels.get(panel_id)
        if not panel:
            print(f"[UIManager] hide_panel: Panel '{panel_id}' not found")
            return
        print(f"[UIManager] hide_panel: Hiding panel '{panel_id}'")
        if panel_id in self._active_panels:
            self._active_panels.remove(panel_id)
        if hasattr(panel, 'hide'):
            panel.hide()
        else:
            print(f"[UIManager] hide_panel: Panel '{panel_id}' has no hide method")
                
    def toggle_panel(self, panel_id: str) -> None:
        """Toggle visibility of a panel.
        
        Args:
            panel_id: ID of panel to toggle
        """
        if panel_id in self._active_panels:
            self.hide_panel(panel_id)
        else:
            self.show_panel(panel_id)
            
    def handle_screen_resize(self, new_rect: pygame.Rect) -> None:
        """Handle screen resize event.
        
        Args:
            new_rect: New screen rectangle
        """
        self.screen_rect = new_rect
        if self.manager:
            self.manager.set_window_resolution(new_rect.size)
            
    def shutdown(self) -> None:
        """Clean up UI resources."""
        self._panels.clear()
        self._active_panels.clear()
        self.manager = None
        self._initialized = False
