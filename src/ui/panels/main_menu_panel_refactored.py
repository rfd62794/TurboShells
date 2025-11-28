"""
Refactored Main Menu Panel using only reusable components.

This replaces the monolithic MainMenuPanel with a clean component-based approach
that follows SRP and uses the reusable component library.
"""

import pygame
import pygame_gui
from typing import Optional, Callable
from .base_panel import BasePanel
from ..dialogs.quit_confirmation_dialog import QuitConfirmationDialog
from ..components.reusable import Panel, MoneyDisplay, Container, Button
from game.game_state_interface import TurboShellsGameStateInterface


class MainMenuPanelRefactored(BasePanel):
    """Main Menu Panel built entirely from reusable components."""
    
    def __init__(self, game_state_interface: TurboShellsGameStateInterface, event_bus=None):
        """Initialize refactored main menu panel.
        
        Args:
            game_state_interface: Game state interface for data access
            event_bus: Event bus for communication
        """
        super().__init__("main_menu", "Turbo Shells", event_bus=event_bus)
        self.game_state = game_state_interface
        
        # Panel dimensions (will be centered)
        self.size = (400, 500)
        self.position = (312, 134)  # Centered on 1024x768
        
        # Reusable components
        self.main_panel: Optional[Panel] = None
        self.money_display: Optional[MoneyDisplay] = None
        self.menu_container: Optional[Container] = None
        self.menu_buttons: list[Button] = []
        
        # Dialog system
        self.quit_dialog: Optional[QuitConfirmationDialog] = None
        
        # Callbacks
        self.on_navigate: Optional[Callable[[str], None]] = None
        self.on_quit: Optional[Callable[[], None]] = None
        
    def _create_window(self) -> None:
        """Create the main menu using reusable components."""
        super()._create_window()
        
        if not self.window:
            return
            
        # Center the window on screen
        if self.manager and self.manager.window_resolution:
            screen_w, screen_h = self.manager.window_resolution
            self.position = ((screen_w - self.size[0]) // 2, (screen_h - self.size[1]) // 2)
            self.window.set_position(self.position)
            
        # Get the window's container for proper positioning
        self.container = self.window.get_container()
        
        # Create reusable components
        self._create_money_display()
        self._create_menu_container()
        self._create_menu_buttons()
        self._initialize_quit_dialog()
        
    def _create_main_panel(self) -> None:
        """Create the main panel with header."""
        self.main_panel = Panel(
            rect=pygame.Rect(0, 0, self.size[0], self.size[1]),
            title="Turbo Shells",
            manager=self.manager,
            config={
                'header_height': 40,
                'header_color': (50, 50, 50),
                'body_color': (240, 240, 240),
                'border_color': (100, 100, 100),
                'border_width': 2,
                'padding': 10
            }
        )
        
    def _create_money_display(self) -> None:
        """Create money display in header area."""
        # Position in header area (top-right) relative to container
        width = self.size[0] - 40
        money_rect = pygame.Rect(
            (width - 140, 8), (140, 25)  # Top-right positioning
        )
        
        self.money_display = MoneyDisplay(
            rect=money_rect,
            amount=self.game_state.get('money', 0),
            manager=self.manager,
            container=self.container,  # Use window container
            config={
                'font_size': 16,
                'text_color': (255, 255, 255)
            }
        )
        
    def _create_menu_container(self) -> None:
        """Create container for menu buttons."""
        # Position in body area below header, relative to container
        width = self.size[0] - 40
        y_pos = 20  # Start 20px from top of container (not 60)
        
        # Create buttons directly in the container instead of using a nested container
        self.button_width = width
        self.button_height = 40
        self.button_spacing = 10
        self.button_start_y = y_pos
        
    def _create_menu_buttons(self) -> None:
        """Create menu navigation buttons."""
        menu_items = [
            ("Roster", "navigate_roster"),
            ("Shop", "navigate_shop"),
            ("Breeding", "navigate_breeding"),
            ("Race", "navigate_race"),
            ("Voting", "navigate_voting"),
            ("Settings", "toggle_settings"),
            ("Quit", "quit")
        ]
        
        y_pos = self.button_start_y
        
        for text, action in menu_items:
            button_rect = pygame.Rect(
                (10, y_pos),  # Left margin with 10px padding
                (self.button_width, self.button_height)
            )
            
            # Style configuration based on action type
            config = {'style': 'primary'}
            if action == 'quit':
                config = {'style': 'danger'}
            elif action == 'toggle_settings':
                config = {'style': 'secondary'}
                
            button = Button(
                rect=button_rect,
                text=text,
                action=action,
                manager=self.manager,
                container=self.container,  # Use window container
                config=config
            )
            
            # Set action callback
            button.set_action_callback(self._on_button_action)
            
            self.menu_buttons.append(button)
            y_pos += self.button_height + self.button_spacing
            
    def _initialize_quit_dialog(self) -> None:
        """Initialize quit confirmation dialog."""
        if self.manager and not self.quit_dialog:
            self.quit_dialog = QuitConfirmationDialog(self, self.manager)
            self.quit_dialog.set_callbacks(
                confirm_callback=self._on_quit_confirmed,
                cancel_callback=self._on_quit_cancelled
            )
            
    def _on_button_action(self, action: str) -> None:
        """Handle button actions."""
        if action.startswith('navigate_'):
            state = action.replace('navigate_', '').upper()
            self._navigate(state)
            
        elif action == 'toggle_settings':
            self._toggle_settings()
            
        elif action == 'quit':
            self._show_quit_confirmation()
            
    def _navigate(self, state: str) -> None:
        """Navigate to specified state."""
        if state == "ROSTER":
            # Special handling for race mode
            self.game_state.set('select_racer_mode', True)
            
        # Navigate to state
        if self.event_bus:
            self.event_bus.emit("ui:navigate", {"state": state})
        else:
            self.game_state.set('state', state)
            
    def _toggle_settings(self) -> None:
        """Toggle settings panel."""
        if hasattr(self.game_state.game, 'ui_manager'):
            self.game_state.game.ui_manager.toggle_panel('settings')
            
    def _show_quit_confirmation(self) -> None:
        """Show quit confirmation dialog."""
        if self.quit_dialog:
            self.quit_dialog.show()
            
    def _on_quit_confirmed(self) -> None:
        """Handle quit confirmation."""
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        
    def _on_quit_cancelled(self) -> None:
        """Handle quit cancellation."""
        if self.quit_dialog:
            self.quit_dialog.hide()
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events through component delegation."""
        # Handle window close event with confirmation
        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.window:
                self._show_quit_confirmation()
                return True
                
        # Let dialog handle its events first
        if self.quit_dialog and self.quit_dialog.handle_event(event):
            return True
            
        # Delegate to reusable components
        if self.money_display and self.money_display.handle_event(event):
            return True
            
        if self.menu_container and self.menu_container.handle_event(event):
            return True
            
        # Handle any remaining events
        return super().handle_event(event)
        
    def update(self, time_delta: float) -> None:
        """Update panel and components."""
        super().update(time_delta)
        
        # Update money display with current amount
        if self.money_display and self.game_state:
            current_money = self.game_state.get('money', 0)
            self.money_display.set_amount(current_money)
            
        # Buttons are automatically updated by pygame_gui
        # No custom update needed since we use the window's container
            
    def render(self, surface: pygame.Surface) -> None:
        """Render the main menu using components."""
        if not self.visible:
            return
            
        # Components are now rendered by pygame_gui within the window container
        # No custom rendering needed since we use the window's container
        pass
            
    def set_navigation_callback(self, callback: Callable[[str], None]) -> None:
        """Set navigation callback for external handling."""
        self.on_navigate = callback
        
    def set_quit_callback(self, callback: Callable[[], None]) -> None:
        """Set quit callback for external handling."""
        self.on_quit = callback
        
    def get_button(self, text: str) -> Optional[Button]:
        """Get a specific menu button by text."""
        for button in self.menu_buttons:
            if button.text == text:
                return button
        return None
        
    def set_button_enabled(self, text: str, enabled: bool) -> None:
        """Enable/disable a specific button."""
        button = self.get_button(text)
        if button:
            button.set_enabled(enabled)
            
    def get_money_display(self) -> Optional[MoneyDisplay]:
        """Get the money display component."""
        return self.money_display
        
    def get_menu_container(self) -> Optional[Container]:
        """Get the menu container component."""
        return self.menu_container
