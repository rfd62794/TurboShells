import pygame
import pygame_gui
from typing import Optional, Tuple, Any

from settings import STATE_MENU

class BasePanel:
    """Base class for UI panels using pygame_gui.
    
    Provides common functionality for:
    - Panel initialization
    - Visibility management
    - Event handling
    """
    
    def __init__(self, panel_id: str, title: str):
        """Initialize base panel.
        
        Args:
            panel_id: Unique identifier for the panel
            title: Display title for the panel
        """
        self.panel_id = panel_id
        self.title = title
        self.manager: Optional[pygame_gui.UIManager] = None
        self.window: Optional[pygame_gui.elements.UIWindow] = None
        self.visible = False
        
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
            
        if not self.window:
            self._create_window()
            
        if self.window:
            self.window.show()
            self.visible = True
            
    def hide(self) -> None:
        """Hide the panel."""
        if self.window:
            self.window.hide()
        self.visible = False
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle base panel events. Override in subclasses."""
        if event.type == pygame_gui.UI_WINDOW_CLOSE and event.ui_element == self.window:
            if hasattr(self, 'game_state') and self.game_state:
                if self.panel_id == 'main_menu':
                    # Main menu handles confirmation itself
                    return False

                # Return to main menu for any secondary panel
                self.game_state.set('state', STATE_MENU)
                self.hide()
                return True
            return False
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
