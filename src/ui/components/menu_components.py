"""
Menu-specific components following SRP principles.
"""

import pygame
import pygame_gui
from typing import Optional, Callable, Dict, Any, List
from .base_component import BaseComponent


class MoneyDisplay(BaseComponent):
    """Component for displaying player money."""
    
    def __init__(self, rect: pygame.Rect, manager=None, game_state=None):
        """Initialize money display.
        
        Args:
            rect: Component position and size
            manager: pygame_gui UIManager
            game_state: Game state for money access
        """
        super().__init__(rect, manager)
        self.game_state = game_state
        self.money_label: Optional[pygame_gui.elements.UILabel] = None
        
        if self.manager:
            self._create_ui_element()
            
    def _create_ui_element(self) -> None:
        """Create the money label UI element."""
        self.money_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, self.rect.width, self.rect.height),
            text="Money: $0",
            manager=self.manager
        )
        
    def render(self, surface: pygame.Surface) -> None:
        """Render money display (handled by pygame_gui)."""
        # Label is rendered by pygame_gui automatically
        pass
        
    def update(self, dt: float) -> None:
        """Update money display."""
        super().update(dt)
        
        if self.money_label and self.game_state:
            current_money = self.game_state.get('money', 0)
            self.money_label.set_text(f"Money: ${current_money}")


class MenuButton(BaseComponent):
    """Individual menu button component."""
    
    def __init__(self, rect: pygame.Rect, text: str, action: str, manager=None):
        """Initialize menu button.
        
        Args:
            rect: Button position and size
            text: Button display text
            action: Action identifier (e.g., 'navigate_roster')
            manager: pygame_gui UIManager
        """
        super().__init__(rect, manager)
        self.text = text
        self.action = action
        self.button: Optional[pygame_gui.elements.UIButton] = None
        self.on_action: Optional[Callable[[str], None]] = None
        
        if self.manager:
            self._create_button()
            
    def _create_button(self) -> None:
        """Create the pygame_gui button."""
        self.button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, self.rect.width, self.rect.height),
            text=self.text,
            manager=self.manager
        )
        
    def render(self, surface: pygame.Surface) -> None:
        """Render button (handled by pygame_gui)."""
        # Button is rendered by pygame_gui automatically
        pass
        
    def _handle_component_event(self, event: pygame.event.Event) -> bool:
        """Handle button press events."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.button:
                if self.on_action:
                    self.on_action(self.action)
                return True
        return False
        
    def set_text(self, text: str) -> None:
        """Update button text."""
        self.text = text
        if self.button:
            self.button.set_text(text)
            
    def set_enabled(self, enabled: bool) -> None:
        """Set button enabled state."""
        super().set_enabled(enabled)
        if self.button:
            if enabled:
                self.button.enable()
            else:
                self.button.disable()


class NavigationMenu(BaseComponent):
    """Container for navigation menu buttons."""
    
    def __init__(self, rect: pygame.Rect, manager=None, game_state=None):
        """Initialize navigation menu.
        
        Args:
            rect: Menu position and size
            manager: pygame_gui UIManager
            game_state: Game state for navigation
        """
        super().__init__(rect, manager)
        self.game_state = game_state
        self.menu_buttons: List[MenuButton] = []
        self.on_navigate: Optional[Callable[[str], None]] = None
        
        # Define menu items
        self.menu_items = [
            ("Roster", "navigate_roster"),
            ("Shop", "navigate_shop"),
            ("Breeding", "navigate_breeding"),
            ("Race", "navigate_race"),
            ("Voting", "navigate_voting"),
            ("Settings", "toggle_settings"),
            ("Quit", "show_quit_confirmation")
        ]
        
        self._create_menu_buttons()
        
    def _create_menu_buttons(self) -> None:
        """Create menu buttons."""
        button_height = 40
        spacing = 10
        y_pos = 0
        
        for text, action in self.menu_items:
            button_rect = pygame.Rect(0, y_pos, self.rect.width, button_height)
            menu_button = MenuButton(button_rect, text, action, self.manager)
            
            # Set action callback
            menu_button.on_action = self._on_button_action
            
            self.menu_buttons.append(menu_button)
            self.add_child(menu_button)
            y_pos += button_height + spacing
            
    def _on_button_action(self, action: str) -> None:
        """Handle menu button actions."""
        if action.startswith("navigate_"):
            state = action.replace("navigate_", "").upper()
            if self.on_navigate:
                self.on_navigate(state)
            elif self.game_state:
                # Fallback navigation
                self.game_state.set('state', state)
                
        elif action == "toggle_settings":
            if hasattr(self.game_state.game, 'ui_manager'):
                self.game_state.game.ui_manager.toggle_panel('settings')
                
        elif action == "show_quit_confirmation":
            if self.on_navigate:
                self.on_navigate("quit")
                
        # Emit action event for parent handling
        self._emit_event(action)
        
    def get_button(self, text: str) -> Optional[MenuButton]:
        """Get a menu button by text."""
        for button in self.menu_buttons:
            if button.text == text:
                return button
        return None
        
    def set_button_enabled(self, text: str, enabled: bool) -> None:
        """Enable/disable a specific button."""
        button = self.get_button(text)
        if button:
            button.set_enabled(enabled)


class MainMenuComponent(BaseComponent):
    """Complete main menu component using composition."""
    
    def __init__(self, rect: pygame.Rect, manager=None, game_state=None):
        """Initialize main menu component.
        
        Args:
            rect: Menu position and size
            manager: pygame_gui UIManager
            game_state: Game state interface
        """
        super().__init__(rect, manager)
        self.game_state = game_state
        
        # Sub-components
        self.money_display: Optional[MoneyDisplay] = None
        self.navigation_menu: Optional[NavigationMenu] = None
        
        # Event callbacks
        self.on_navigate: Optional[Callable[[str], None]] = None
        self.on_quit: Optional[Callable[[], None]] = None
        
        self._create_subcomponents()
        
    def _create_subcomponents(self) -> None:
        """Create sub-components."""
        # Money display at top
        money_rect = pygame.Rect(10, 20, self.rect.width - 20, 30)
        self.money_display = MoneyDisplay(money_rect, self.manager, self.game_state)
        self.add_child(self.money_display)
        
        # Navigation menu below
        nav_rect = pygame.Rect(10, 70, self.rect.width - 20, 280)
        self.navigation_menu = NavigationMenu(nav_rect, self.manager, self.game_state)
        
        # Set navigation callback
        self.navigation_menu.on_navigate = self._on_navigate_request
        
        self.add_child(self.navigation_menu)
        
    def _on_navigate_request(self, state: str) -> None:
        """Handle navigation request."""
        if state == "quit":
            if self.on_quit:
                self.on_quit()
        elif self.on_navigate:
            self.on_navigate(state)
        else:
            # Fallback navigation
            if self.game_state:
                self.game_state.set('state', state)
                
    def render(self, surface: pygame.Surface) -> None:
        """Render main menu (components handle their own rendering)."""
        # Components render themselves
        pass
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events with component delegation."""
        # Let sub-components handle events first
        if self.money_display and self.money_display.handle_event(event):
            return True
            
        if self.navigation_menu and self.navigation_menu.handle_event(event):
            return True
            
        # Handle component-specific events
        return super().handle_event(event)
        
    def update(self, dt: float) -> None:
        """Update main menu and components."""
        super().update(dt)
        
        # Components update themselves
        
    def set_navigation_callback(self, callback: Callable[[str], None]) -> None:
        """Set navigation callback."""
        self.on_navigate = callback
        
    def set_quit_callback(self, callback: Callable[[], None]) -> None:
        """Set quit callback."""
        self.on_quit = callback
        
    def get_navigation_menu(self) -> Optional[NavigationMenu]:
        """Get the navigation menu for advanced customization."""
        return self.navigation_menu
        
    def get_money_display(self) -> Optional[MoneyDisplay]:
        """Get the money display for advanced customization."""
        return self.money_display
