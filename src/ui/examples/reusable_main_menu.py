"""
Example: Building Main Menu with Reusable Components

This demonstrates how to compose reusable components to create a complete UI.
"""

import pygame
import pygame_gui
from typing import Optional, Callable
from ui.components.reusable import (
    Panel, Button, MoneyDisplay, Container, Label
)


class ReusableMainMenu:
    """Main menu built entirely from reusable components."""
    
    def __init__(self, rect: pygame.Rect, manager=None, game_state=None):
        """Initialize reusable main menu.
        
        Args:
            rect: Menu position and size
            manager: pygame_gui UIManager
            game_state: Game state for data access
        """
        self.rect = rect
        self.manager = manager
        self.game_state = game_state
        
        # Main panel container
        self.main_panel: Optional[Panel] = None
        
        # Sub-components
        self.money_display: Optional[MoneyDisplay] = None
        self.menu_container: Optional[Container] = None
        self.menu_buttons: list[Button] = []
        
        # Callbacks
        self.on_navigate: Optional[Callable[[str], None]] = None
        self.on_quit: Optional[Callable[[], None]] = None
        
        # Create components
        self._create_components()
        
    def _create_components(self) -> None:
        """Create all reusable components."""
        # Main panel with header
        self.main_panel = Panel(
            rect=self.rect,
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
        
        # Money display in header area
        money_rect = pygame.Rect(
            self.rect.width - 150, 8, 140, 25
        )
        self.money_display = MoneyDisplay(
            rect=money_rect,
            amount=self.game_state.get('money', 0) if self.game_state else 0,
            manager=self.manager,
            config={
                'font_size': 16,
                'text_color': (255, 255, 255)
            }
        )
        
        # Menu container for buttons
        content_rect = self.main_panel.get_content_rect()
        menu_rect = pygame.Rect(
            content_rect.x + 10, content_rect.y + 10,
            content_rect.width - 20, content_rect.height - 20
        )
        
        self.menu_container = Container(
            rect=menu_rect,
            manager=self.manager,
            config={
                'layout_type': 'vertical',
                'spacing': 10,
                'padding': 0
            }
        )
        
        # Create menu buttons
        self._create_menu_buttons()
        
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
        
        button_height = 40
        button_width = self.menu_container.rect.width
        
        for text, action in menu_items:
            button_rect = pygame.Rect(0, 0, button_width, button_height)
            
            # Style configuration based on action
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
                config=config
            )
            
            # Set action callback
            button.set_action_callback(self._on_button_action)
            
            self.menu_buttons.append(button)
            self.menu_container.add_child(button)
            
    def _on_button_action(self, action: str) -> None:
        """Handle button actions."""
        if action.startswith('navigate_'):
            state = action.replace('navigate_', '').upper()
            if self.on_navigate:
                self.on_navigate(state)
            elif self.game_state:
                self.game_state.set('state', state)
                
        elif action == 'toggle_settings':
            # Handle settings toggle
            if hasattr(self.game_state.game, 'ui_manager'):
                self.game_state.game.ui_manager.toggle_panel('settings')
                
        elif action == 'quit':
            if self.on_quit:
                self.on_quit()
                
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events through component delegation."""
        # Let components handle their own events
        if self.money_display and self.money_display.handle_event(event):
            return True
            
        if self.menu_container and self.menu_container.handle_event(event):
            return True
            
        return False
        
    def update(self, dt: float) -> None:
        """Update all components."""
        # Update money display
        if self.money_display and self.game_state:
            current_money = self.game_state.get('money', 0)
            self.money_display.set_amount(current_money)
            
        # Update container and children
        if self.menu_container:
            self.menu_container.update(dt)
            
    def render(self, surface: pygame.Surface) -> None:
        """Render the main menu."""
        if not self.main_panel:
            return
            
        # Render panel (includes header and background)
        self.main_panel.render(surface)
        
        # Render money display
        if self.money_display:
            self.money_display.render(surface)
            
        # Render menu container with buttons
        if self.menu_container:
            self.menu_container.render(surface)
            
    def set_navigation_callback(self, callback: Callable[[str], None]) -> None:
        """Set navigation callback."""
        self.on_navigate = callback
        
    def set_quit_callback(self, callback: Callable[[], None]) -> None:
        """Set quit callback."""
        self.on_quit = callback
        
    def get_button(self, text: str) -> Optional[Button]:
        """Get a specific menu button."""
        for button in self.menu_buttons:
            if button.text == text:
                return button
        return None
        
    def set_button_enabled(self, text: str, enabled: bool) -> None:
        """Enable/disable a specific button."""
        button = self.get_button(text)
        if button:
            button.set_enabled(enabled)


class ComponentComparison:
    """Compare old vs new component approaches."""
    
    @staticmethod
    def old_approach(rect: pygame.Rect, manager=None, game_state=None):
        """Old monolithic approach (simplified)."""
        class OldMainMenuPanel:
            def __init__(self, rect, manager, game_state):
                self.rect = rect
                self.manager = manager
                self.game_state = game_state
                
                # Create everything in one place
                self.window = pygame_gui.elements.UIWindow(rect, manager, "Turbo Shells")
                container = self.window.get_container()
                
                # Money display
                self.lbl_money = pygame_gui.elements.UILabel(
                    pygame.Rect(10, 20, 150, 30),
                    f"Money: ${game_state.get('money', 0)}",
                    manager,
                    container
                )
                
                # Buttons - hardcoded
                self.btn_roster = pygame_gui.elements.UIButton(
                    pygame.Rect(10, 60, 200, 40), "Roster", manager, container
                )
                # ... more buttons ...
                
            def handle_event(self, event):
                # Handle all events in one large method
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.btn_roster:
                        # Navigate logic here
                        pass
                    # ... more event handling ...
                return False
                
            def update(self, dt):
                # Update money display
                self.lbl_money.set_text(f"Money: ${self.game_state.get('money', 0)}")
                
        return OldMainMenuPanel(rect, manager, game_state)
        
    @staticmethod
    def new_approach(rect: pygame.Rect, manager=None, game_state=None):
        """New component-based approach."""
        return ReusableMainMenu(rect, manager, game_state)


def demo_reusable_components():
    """Demonstrate the power of reusable components."""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("Reusable Components Demo")
    
    manager = pygame_gui.UIManager((1200, 800))
    
    # Mock game state
    class MockGameState:
        def get(self, key, default=0):
            return getattr(self, key, default)
        def set(self, key, value):
            setattr(self, key, value)
            
    game_state = MockGameState()
    game_state.money = 1000
    
    # Create reusable main menu
    menu_rect = pygame.Rect(400, 150, 400, 500)
    main_menu = ReusableMainMenu(menu_rect, manager, game_state)
    
    # Set up callbacks
    def on_navigate(state: str):
        print(f"Navigate to: {state}")
        
    def on_quit():
        print("Quit requested")
        
    main_menu.set_navigation_callback(on_navigate)
    main_menu.set_quit_callback(on_quit)
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Handle events through components
            main_menu.handle_event(event)
            manager.process_events(event)
            
        # Update
        manager.update(dt)
        main_menu.update(dt)
        
        # Render
        screen.fill((200, 200, 200))
        main_menu.render(screen)
        manager.draw_ui(screen)
        
        # Draw demo info
        font = pygame.font.Font(None, 24)
        info_lines = [
            "Reusable Components Demo",
            "Main Menu built with:",
            "- Panel (header + body)",
            "- MoneyDisplay", 
            "- Container (vertical layout)",
            "- Button (with actions)",
            "",
            "Benefits:",
            "- Each component has single responsibility",
            "- Components can be reused anywhere",
            "- Easy to test and maintain",
            "- Configurable styling"
        ]
        
        for i, line in enumerate(info_lines):
            text_surface = font.render(line, True, (0, 0, 0))
            screen.blit(text_surface, (20, 20 + i * 25))
            
        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    demo_reusable_components()
