import pygame
import pygame_gui
from .base_panel import BasePanel
from game.game_state_interface import TurboShellsGameStateInterface
from settings import STATE_ROSTER, STATE_SHOP, STATE_BREEDING, STATE_VOTING

class MainMenuPanel(BasePanel):
    """Main Menu Panel using pygame_gui."""
    
    def __init__(self, game_state_interface: TurboShellsGameStateInterface, event_bus=None):
        super().__init__("main_menu", "Turbo Shells", event_bus=event_bus)
        self.game_state = game_state_interface
        
        # Full screen centered
        self.size = (400, 500)
        self.position = (312, 134) # Centered roughly on 1024x768
        
        self.btn_roster = None
        self.btn_shop = None
        self.btn_breeding = None
        self.btn_race = None
        self.btn_voting = None
        self.btn_settings = None
        self.btn_quit = None
        
        self.lbl_money = None
        
    def _create_window(self) -> None:
        super()._create_window()
        if not self.window:
            return
            
        # Center the window on screen if manager is available
        if self.manager and self.manager.window_resolution:
            screen_w, screen_h = self.manager.window_resolution
            self.position = ((screen_w - self.size[0]) // 2, (screen_h - self.size[1]) // 2)
            self.window.set_position(self.position)
            
        container = self.window.get_container()
        width = self.size[0] - 40
        y_pos = 20
        
        # Money Display
        self.lbl_money = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, y_pos), (width, 30)),
            text=f"Money: ${self.game_state.get('money', 0)}",
            manager=self.manager,
            container=container
        )
        y_pos += 50
        
        # Buttons
        btn_height = 40
        spacing = 10
        
        self.btn_roster = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, y_pos), (width, btn_height)),
            text="Roster",
            manager=self.manager,
            container=container
        )
        y_pos += btn_height + spacing
        
        self.btn_shop = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, y_pos), (width, btn_height)),
            text="Shop",
            manager=self.manager,
            container=container
        )
        y_pos += btn_height + spacing
        
        self.btn_breeding = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, y_pos), (width, btn_height)),
            text="Breeding",
            manager=self.manager,
            container=container
        )
        y_pos += btn_height + spacing
        
        self.btn_race = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, y_pos), (width, btn_height)),
            text="Race",
            manager=self.manager,
            container=container
        )
        y_pos += btn_height + spacing
        
        self.btn_voting = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, y_pos), (width, btn_height)),
            text="Voting",
            manager=self.manager,
            container=container
        )
        y_pos += btn_height + spacing
        
        self.btn_settings = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, y_pos), (width, btn_height)),
            text="Settings",
            manager=self.manager,
            container=container
        )
        y_pos += btn_height + spacing
        
        self.btn_quit = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, y_pos), (width, btn_height)),
            text="Quit",
            manager=self.manager,
            container=container
        )
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        # Handle window close event with confirmation
        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.window:
                print(f"[MainMenuPanel] X button clicked - showing confirmation")
                self._show_quit_confirmation()
                return True  # Prevent default window destruction
            elif hasattr(self, 'confirmation_dialog') and event.ui_element == self.confirmation_dialog:
                self._hide_quit_confirmation()
                return True
                
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_roster:
                self._navigate(STATE_ROSTER)
                return True
            elif event.ui_element == self.btn_shop:
                self._navigate(STATE_SHOP)
                return True
            elif event.ui_element == self.btn_breeding:
                self._navigate(STATE_BREEDING)
                return True
            elif event.ui_element == self.btn_race:
                self.game_state.set('select_racer_mode', True)
                self._navigate(STATE_ROSTER)
                return True
            elif event.ui_element == self.btn_voting:
                self._navigate(STATE_VOTING)
                return True
            elif event.ui_element == self.btn_settings:
                # Toggle settings panel via game instance if possible, or just show it
                # Assuming UIManager is accessible via game or we use a global event
                # For now, let's try to access ui_manager from game
                if hasattr(self.game_state.game, 'ui_manager'):
                    self.game_state.game.ui_manager.toggle_panel('settings')
                return True
            elif event.ui_element == self.btn_quit:
                self._show_quit_confirmation()
                return True
            # Handle confirmation dialog buttons
            elif hasattr(self, 'confirm_quit_yes') and event.ui_element == self.confirm_quit_yes:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                return True
            elif hasattr(self, 'confirm_quit_no') and event.ui_element == self.confirm_quit_no:
                self._hide_quit_confirmation()
                return True
                
        return False

    def _navigate(self, state: str) -> None:
        if self.event_bus:
            self.event_bus.emit("ui:navigate", {"state": state})
        else:
            self.game_state.set('state', state)

    def _show_quit_confirmation(self) -> None:
        """Show a confirmation dialog for quitting."""
        if hasattr(self, 'confirmation_dialog') and self.confirmation_dialog:
            return  # Already showing
            
        # Create confirmation dialog window
        dialog_rect = pygame.Rect(250, 250, 300, 120)
        self.confirmation_dialog = pygame_gui.elements.UIWindow(
            rect=dialog_rect,
            manager=self.manager,
            draggable=False,
            resizable=False
        )
        
        container = self.confirmation_dialog.get_container()
        
        # Add a title label
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 5), (280, 20)),
            text='Quit Game',
            manager=self.manager,
            container=container
        )
        
        # Confirmation message
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 25), (280, 30)),
            text='Are you sure you want to quit?',
            manager=self.manager,
            container=container
        )
        
        # Yes button
        self.confirm_quit_yes = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((50, 65), (80, 30)),
            text='Yes',
            manager=self.manager,
            container=container
        )
        
        # No button
        self.confirm_quit_no = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((170, 65), (80, 30)),
            text='No',
            manager=self.manager,
            container=container
        )
        
    def _hide_quit_confirmation(self) -> None:
        """Hide the confirmation dialog."""
        if hasattr(self, 'confirmation_dialog') and self.confirmation_dialog:
            self.confirmation_dialog.kill()
            self.confirmation_dialog = None
            self.confirm_quit_yes = None
            self.confirm_quit_no = None

    def update(self, time_delta: float) -> None:
        super().update(time_delta)
        # Update money display if changed
        if self.lbl_money and self.visible:
            current_money = self.game_state.get('money', 0)
            self.lbl_money.set_text(f"Money: ${current_money}")
