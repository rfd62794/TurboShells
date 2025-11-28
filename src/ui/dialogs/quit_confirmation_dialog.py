"""Quit Confirmation Dialog

A specific dialog for confirming game quit action.
"""

import pygame
import pygame_gui
from .base_dialog import BaseDialog
from typing import Optional


class QuitConfirmationDialog(BaseDialog):
    """Dialog for confirming game quit action."""
    
    def __init__(self, parent_panel, manager: pygame_gui.UIManager):
        """Initialize the quit confirmation dialog.
        
        Args:
            parent_panel: The MainMenuPanel that owns this dialog
            manager: pygame_gui.UIManager instance
        """
        super().__init__(parent_panel, "Quit Game", manager)
        
        # UI elements
        self.message_label: Optional[pygame_gui.elements.UILabel] = None
        self.yes_button: Optional[pygame_gui.elements.UIButton] = None
        self.no_button: Optional[pygame_gui.elements.UIButton] = None
        
    def _create_window(self) -> None:
        """Create the quit confirmation dialog window."""
        # Create the window
        dialog_rect = pygame.Rect(250, 250, 300, 120)
        self.window = pygame_gui.elements.UIWindow(
            rect=dialog_rect,
            manager=self.manager,
            draggable=False,
            resizable=False
        )
        
        if not self.window:
            return
            
        container = self.window.get_container()
        
        # Add a title label
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 5), (280, 20)),
            text='Quit Game',
            manager=self.manager,
            container=container
        )
        
        # Confirmation message
        self.message_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 25), (280, 30)),
            text='Are you sure you want to quit?',
            manager=self.manager,
            container=container
        )
        
        # Yes button
        self.yes_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((50, 65), (80, 30)),
            text='Yes',
            manager=self.manager,
            container=container
        )
        
        # No button
        self.no_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((170, 65), (80, 30)),
            text='No',
            manager=self.manager,
            container=container
        )
        
        print(f"[QuitConfirmationDialog] Dialog window created")
        
    def _handle_button_event(self, event: pygame.event.Event) -> bool:
        """Handle button press events."""
        if not self.visible:
            return False
            
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.yes_button:
                print(f"[QuitConfirmationDialog] Yes button clicked")
                if self.confirm_callback:
                    self.confirm_callback()
                else:
                    # Default behavior: quit game
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                return True
                
            elif event.ui_element == self.no_button:
                print(f"[QuitConfirmationDialog] No button clicked")
                if self.cancel_callback:
                    self.cancel_callback()
                else:
                    # Default behavior: just hide
                    self.hide()
                return True
                
        return False
