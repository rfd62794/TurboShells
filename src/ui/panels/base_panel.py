import pygame
import pygame_gui
from typing import Optional, Tuple, Any

class BasePanel:
    """Base class for UI panels using pygame_gui.
    
    Provides common functionality for:
    - Panel initialization
    - Visibility management
    - Event handling
    - Window resize handling
    - Dynamic sizing and positioning
    """
    
    def __init__(self, panel_id: str, title: str, event_bus: Optional[Any] = None, use_window_manager: bool = False):
        """Initialize base panel.
        
        Args:
            panel_id: Unique identifier for the panel
            title: Display title for the panel
            event_bus: Event bus for communication
            use_window_manager: Whether to use window manager for dynamic sizing
        """
        self.panel_id = panel_id
        self.title = title
        self.manager: Optional[pygame_gui.UIManager] = None
        self.window: Optional[pygame_gui.elements.UIWindow] = None
        self.visible = False
        self.event_bus = event_bus
        self.use_window_manager = use_window_manager
        
        # Window manager integration
        if self.use_window_manager:
            try:
                from core.ui.window_manager import window_manager
                self.window_manager = window_manager
                self.panel_rect = self.window_manager.get_panel_rect(panel_id)
                self.size = (self.panel_rect.width, self.panel_rect.height)
                self.position = (self.panel_rect.x, self.panel_rect.y)
            except ImportError:
                print(f"[BasePanel] Warning: window_manager not available for panel '{panel_id}', using defaults")
                self.use_window_manager = False
                self.window_manager = None
                self.panel_rect = None
                self.position = (100, 100)
                self.size = (400, 300)
        else:
            self.window_manager = None
            self.panel_rect = None
            # Default configuration
            self.position = (100, 100)
            self.size = (400, 300)
        
    def setup_ui(self, manager: pygame_gui.UIManager) -> None:
        """Setup UI elements.
        
        Args:
            manager: The pygame_gui UIManager
        """
        self.manager = manager
        # We don't create the window here immediately, usually on show()
        # or we create it hidden.
        
    def show(self) -> None:
        """Show the panel."""
        if not self.manager:
            return
            
        # Always recreate the window to ensure clean state
        if self.window:
            print(f"[BasePanel] Recreating window for panel '{self.panel_id}' (old window existed)")
            # Clean up old window properly
            if hasattr(self.window, 'kill'):
                self.window.kill()
            self.window = None
            
        self._create_window()
        
        if self.window:
            self.window.show()
            self.visible = True
            print(f"[BasePanel] Panel '{self.panel_id}' shown with new window")
            
    def hide(self) -> None:
        """Hide the panel."""
        if self.window:
            self.window.hide()
        self.visible = False
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events for this panel."""
        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.window:
                print(f"[BasePanel] X button clicked for panel '{self.panel_id}'")
                print(f"[BasePanel] Before hide - window exists: {self.window is not None}, visible: {self.visible}")
                # Prevent window destruction by just hiding it instead of killing it
                self.hide()
                print(f"[BasePanel] After hide - window exists: {self.window is not None}, visible: {self.visible}")
                # Emit panel closed event for navigation
                if self.event_bus:
                    print(f"[BasePanel] Emitting ui:panel_closed for '{self.panel_id}'")
                    self.event_bus.emit("ui:panel_closed", {"panel_id": self.panel_id})
                else:
                    print(f"[BasePanel] No event_bus available for panel '{self.panel_id}'")
                # Return True to prevent the default window destruction behavior
                return True
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Check if this is the close button within our window
            if hasattr(event, 'ui_element') and event.ui_element:
                # Look for close button by object_id or class
                if (hasattr(event.ui_element, 'object_id') and 
                    event.ui_element.object_id == f"#{self.panel_id}_window.close_button"):
                    print(f"[BasePanel] Close button pressed for panel '{self.panel_id}'")
                    self.hide()
                    if self.event_bus:
                        self.event_bus.emit("ui:panel_closed", {"panel_id": self.panel_id})
                    return True
        return False
            
    def toggle(self) -> None:
        """Toggle visibility."""
        if self.visible:
            self.hide()
        else:
            self.show()
            
    def update(self, time_delta: float) -> None:
        """Update panel logic.
        
        Args:
            time_delta: Time passed since last frame
        """
        pass
        
    def handle_window_resize(self, new_size: Tuple[int, int]) -> None:
        """Handle window resize events. Default implementation for all panels.
        
        Args:
            new_size: New window size (width, height)
        """
        if not self.use_window_manager or not self.window_manager:
            # Fallback to basic centering for panels without window manager
            self._handle_basic_resize(new_size)
            return
            
        try:
            # Update panel size and position using window manager
            adjustments = self.window_manager.adjust_for_window_resize(new_size)
            self.panel_rect = self.window_manager.get_panel_rect(self.panel_id)
            self.size = (self.panel_rect.width, self.panel_rect.height)
            self.position = (self.panel_rect.x, self.panel_rect.y)
            
            # Recreate window with new dimensions
            if self.window:
                self.window.kill()
                self.window = None
                self._create_window()
                
            # Call panel-specific resize logic
            self._on_window_resize(new_size)
            
        except Exception as e:
            print(f"[BasePanel] Error during resize for panel '{self.panel_id}': {e}")
            # Fallback to basic resize
            self._handle_basic_resize(new_size)
    
    def _handle_basic_resize(self, new_size: Tuple[int, int]) -> None:
        """Basic resize handling - center panel in window.
        
        Args:
            new_size: New window size (width, height)
        """
        # Calculate centered position
        center_x = new_size[0] // 2
        center_y = new_size[1] // 2
        
        # Update position to center
        self.position = (center_x - self.size[0] // 2, center_y - self.size[1] // 2)
        
        # Update window if it exists
        if self.window:
            self.window.set_position(self.position)
            self.window.set_dimensions(self.size)
    
    def _on_window_resize(self, new_size: Tuple[int, int]) -> None:
        """Called after window resize is handled. Override in subclasses for custom logic.
        
        Args:
            new_size: New window size (width, height)
        """
        # Default implementation does nothing
        # Override in subclasses for panel-specific resize logic
        pass
        
    def destroy(self) -> None:
        """Destroy panel resources."""
        if self.window:
            self.window.kill()
            self.window = None
            
    def _create_window(self) -> None:
        """Create the UI window. Should be overridden or implemented here."""
        rect = pygame.Rect(self.position, self.size)
        self.window = pygame_gui.elements.UIWindow(
            rect=rect,
            manager=self.manager,
            window_display_title=self.title,
            object_id=f"#{self.panel_id}_window",
            draggable=False,  # Disable dragging for main panels
            resizable=False  # Disable resizing
        )
