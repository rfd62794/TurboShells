"""
Component-based Main Menu Panel following SRP principles.
"""

import pygame
import pygame_gui
from typing import Optional
from .base_panel import BasePanel
from ..components.menu_components import MainMenuComponent
from ..dialogs.quit_confirmation_dialog import QuitConfirmationDialog
from game.game_state_interface import TurboShellsGameStateInterface


class MainMenuPanelComponent(BasePanel):
    """Main Menu Panel using component-based architecture."""
    
    def __init__(self, game_state_interface: TurboShellsGameStateInterface, event_bus=None):
        """Initialize main menu panel component.
        
        Args:
            game_state_interface: Game state interface
            event_bus: Event bus for communication
        """
        super().__init__("main_menu", "Turbo Shells", event_bus=event_bus)
        self.game_state = game_state_interface
        
        # Panel size (will be centered)
        self.size = (400, 500)
        self.position = (312, 134)  # Centered on 1024x768
        
        # Component-based menu
        self.main_menu_component: Optional[MainMenuComponent] = None
        
        # Dialog system
        self.quit_dialog: Optional[QuitConfirmationDialog] = None
        
    def _create_window(self) -> None:
        """Create the main menu window and components."""
        super()._create_window()
        
        if not self.window:
            return
            
        # Center the window on screen
        if self.manager and self.manager.window_resolution:
            screen_w, screen_h = self.manager.window_resolution
            self.position = ((screen_w - self.size[0]) // 2, (screen_h - self.size[1]) // 2)
            self.window.set_position(self.position)
            
        # Create main menu component
        self._create_main_menu_component()
        
        # Initialize quit dialog
        self._initialize_quit_dialog()
        
    def _create_main_menu_component(self) -> None:
        """Create the main menu component."""
        if not self.window:
            return
            
        container = self.window.get_container()
        
        # Create main menu component
        menu_rect = pygame.Rect(0, 0, self.size[0] - 40, self.size[1] - 40)
        self.main_menu_component = MainMenuComponent(
            rect=menu_rect,
            manager=self.manager,
            game_state=self.game_state
        )
        
        # Set up callbacks
        self.main_menu_component.set_navigation_callback(self._on_navigate)
        self.main_menu_component.set_quit_callback(self._show_quit_confirmation)
        
    def _initialize_quit_dialog(self) -> None:
        """Initialize the quit confirmation dialog."""
        if self.manager and not self.quit_dialog:
            self.quit_dialog = QuitConfirmationDialog(self, self.manager)
            self.quit_dialog.set_callbacks(
                confirm_callback=self._on_quit_confirmed,
                cancel_callback=self._on_quit_cancelled
            )
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events with component delegation."""
        # Handle window close event with confirmation
        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.window:
                self._show_quit_confirmation()
                return True
                
        # Let dialog handle its events first
        if self.quit_dialog and self.quit_dialog.handle_event(event):
            return True
            
        # Let main menu component handle events
        if self.main_menu_component and self.main_menu_component.handle_event(event):
            return True
            
        # Handle any remaining events
        return super().handle_event(event)
        
    def _on_navigate(self, state: str) -> None:
        """Handle navigation requests."""
        if state == "ROSTER":
            # Special handling for race mode
            self.game_state.set('select_racer_mode', True)
            
        # Navigate to state
        if self.event_bus:
            self.event_bus.emit("ui:navigate", {"state": state})
        else:
            self.game_state.set('state', state)
            
    def _show_quit_confirmation(self) -> None:
        """Show the quit confirmation dialog."""
        if self.quit_dialog:
            self.quit_dialog.show()
            
    def _on_quit_confirmed(self) -> None:
        """Called when user confirms quit action."""
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        
    def _on_quit_cancelled(self) -> None:
        """Called when user cancels quit action."""
        if self.quit_dialog:
            self.quit_dialog.hide()
            
    def update(self, time_delta: float) -> None:
        """Update panel and components."""
        super().update(time_delta)
        
        # Update main menu component
        if self.main_menu_component:
            self.main_menu_component.update(time_delta)
            
    def get_main_menu_component(self) -> Optional[MainMenuComponent]:
        """Get the main menu component for advanced customization."""
        return self.main_menu_component
        
    def enable_menu_button(self, button_text: str, enabled: bool = True) -> None:
        """Enable or disable a specific menu button."""
        if self.main_menu_component:
            nav_menu = self.main_menu_component.get_navigation_menu()
            if nav_menu:
                nav_menu.set_button_enabled(button_text, enabled)
                
    def get_money_display(self):
        """Get the money display component."""
        if self.main_menu_component:
            return self.main_menu_component.get_money_display()
        return None
