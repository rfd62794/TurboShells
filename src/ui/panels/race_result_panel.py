import pygame
import pygame_gui
from .base_panel import BasePanel
from game.game_state_interface import TurboShellsGameStateInterface

class RaceResultPanel(BasePanel):
    """Race Result Panel using pygame_gui."""
    
    def __init__(self, game_state_interface: TurboShellsGameStateInterface):
        super().__init__("race_result", "Race Results")
        self.game_state = game_state_interface
        
        self.size = (500, 600)
        self.position = (262, 84)
        
        self.container_results = None
        self.btn_menu = None
        self.btn_race_again = None
        
        # Observers
        # We refresh on show() usually
        
    def _create_window(self) -> None:
        super()._create_window()
        if not self.window:
            return
            
        if self.manager and self.manager.window_resolution:
            screen_w, screen_h = self.manager.window_resolution
            self.position = ((screen_w - self.size[0]) // 2, (screen_h - self.size[1]) // 2)
            self.window.set_position(self.position)
            
        container = self.window.get_container()
        width = self.size[0] - 40
        
        # Results Container
        self.container_results = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect((0, 10), (width + 40, 400)),
            manager=self.manager,
            container=container
        )
        
        # Buttons
        self.btn_menu = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((20, 450), (150, 40)),
            text="Menu",
            manager=self.manager,
            container=container
        )
        
        self.btn_race_again = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width - 150, 450), (150, 40)),
            text="Race Again",
            manager=self.manager,
            container=container
        )
        
        self._populate_results()
        
    def _populate_results(self):
        if not self.container_results:
            return
            
        self.container_results.clear()
        
        results = self.game_state.get('race_results', [])
        active_racer_idx = self.game_state.get('active_racer_index', 0)
        roster = self.game_state.get('roster', [])
        player_turtle = roster[active_racer_idx] if active_racer_idx < len(roster) else None
        
        y_pos = 10
        for i, turtle in enumerate(results):
            # Check if this is the player's turtle
            is_player = (player_turtle and turtle.name == player_turtle.name)
            
            text = f"{i+1}. {turtle.name} (Age: {turtle.age})"
            if is_player:
                text = f"<b>{text} [YOU]</b>"
                
            pygame_gui.elements.UITextBox(
                relative_rect=pygame.Rect((10, y_pos), (400, 40)),
                html_text=text,
                manager=self.manager,
                container=self.container_results
            )
            y_pos += 50
            
        # Reward message
        if player_turtle and hasattr(player_turtle, 'rank'):
             # This might be tricky as 'rank' is on the race copy, not original?
             # But RaceManager updates original turtle too?
             # Actually RaceManager updates `race_results` with race copies.
             # We iterate `results` which are race copies.
             # So we can find player rank from `results`.
             pass
             
        self.container_results.set_scrollable_area_dimensions((400, y_pos))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_menu:
                self.game_state.set('goto_menu', True)
                return True
            elif event.ui_element == self.btn_race_again:
                self.game_state.set('race_again', True)
                return True
        return False

    def show(self):
        super().show()
        self._populate_results()
