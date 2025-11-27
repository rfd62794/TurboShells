import pygame
import pygame_gui
from .base_panel import BasePanel
from game.game_state_interface import TurboShellsGameStateInterface

class MainMenuPanel(BasePanel):
    """Main Menu Panel using pygame_gui."""
    
    def __init__(self, game_state_interface: TurboShellsGameStateInterface):
        super().__init__("main_menu", "Turbo Shells")
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
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_roster:
                self.game_state.set('state', 'roster')
                return True
            elif event.ui_element == self.btn_shop:
                self.game_state.set('state', 'shop')
                return True
            elif event.ui_element == self.btn_breeding:
                self.game_state.set('state', 'breeding')
                return True
            elif event.ui_element == self.btn_race:
                self.game_state.set('state', 'race')
                return True
            elif event.ui_element == self.btn_voting:
                self.game_state.set('state', 'voting')
                return True
            elif event.ui_element == self.btn_settings:
                # Toggle settings panel via game instance if possible, or just show it
                # Assuming UIManager is accessible via game or we use a global event
                # For now, let's try to access ui_manager from game
                if hasattr(self.game_state.game, 'ui_manager'):
                    self.game_state.game.ui_manager.toggle_panel('settings')
                return True
            elif event.ui_element == self.btn_quit:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                return True
        return False

    def update(self, time_delta: float) -> None:
        super().update(time_delta)
        # Update money display if changed
        if self.lbl_money and self.visible:
            current_money = self.game_state.get('money', 0)
            self.lbl_money.set_text(f"Money: ${current_money}")
