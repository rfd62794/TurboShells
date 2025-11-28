"""Base Dialog System for Modal Dialogs

Provides a base class for modal dialogs that can be owned by panels
without going through the UIManager system.
"""

import pygame
import pygame_gui
from typing import Optional, Callable


class BaseDialog:
    """Base class for modal dialogs that overlay on panels.
    
    This dialog exists independently of the UIManager panel system,
    avoiding conflicts with window recreation and navigation events.
    """
    
    def __init__(self, parent_panel, title: str, manager: pygame_gui.UIManager):
        """Initialize the base dialog.
        
        Args:
            parent_panel: The panel that owns this dialog
            title: Window title for the dialog
            manager: pygame_gui.UIManager instance
        """
        self.parent_panel = parent_panel
        self.title = title
        self.manager = manager
        self.window: Optional[pygame_gui.elements.UIWindow] = None
        self.visible = False
        
        # Callbacks for actions
        self.confirm_callback: Optional[Callable] = None
        self.cancel_callback: Optional[Callable] = None
        
    def show(self) -> None:
        """Create and show the dialog window."""
        if self.visible:
            return  # Already visible
            
        self._create_window()
        if self.window:
            self.window.show()
            self.visible = True
            
    def hide(self) -> None:
        """Hide and destroy the dialog."""
        if self.window:
            self.window.kill()
            self.window = None
        self.visible = False
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle dialog-specific events.
        
        Args:
            event: pygame event to handle
            
        Returns:
            True if event was handled, False otherwise
        """
        if not self.visible or not self.window:
            return False
            
        # Handle window close event
        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.window:
                self._on_close()
                return True
                
        # Handle button presses
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            return self._handle_button_event(event)
            
        return False
        
    def _create_window(self) -> None:
        """Create the dialog window. Override in subclasses."""
        # Default window creation
        dialog_rect = pygame.Rect(250, 250, 400, 200)
        self.window = pygame_gui.elements.UIWindow(
            rect=dialog_rect,
            manager=self.manager,
            draggable=False,
            resizable=False
        )
        
    def _handle_button_event(self, event: pygame.event.Event) -> bool:
        """Handle button press events. Override in subclasses."""
        return False
        
    def _on_close(self) -> None:
        """Called when dialog is closed via X button."""
        if self.cancel_callback:
            self.cancel_callback()
        else:
            self.hide()
            
    def set_callbacks(self, confirm_callback: Callable = None, cancel_callback: Callable = None) -> None:
        """Set the callback functions for dialog actions.
        
        Args:
            confirm_callback: Function to call when user confirms
            cancel_callback: Function to call when user cancels
        """
        self.confirm_callback = confirm_callback
        self.cancel_callback = cancel_callback
