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
        self.result_rows = []
        
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
            
        # Clear existing
        for row in self.result_rows:
            row.kill()
        self.result_rows = []
        
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
                
            row = pygame_gui.elements.UITextBox(
                relative_rect=pygame.Rect((10, y_pos), (400, 40)),
                html_text=text,
                manager=self.manager,
                container=self.container_results
            )
            self.result_rows.append(row)
            y_pos += 50
            
        # Reward message
        if player_turtle:
            # Find player's rank from the results
            player_rank = None
            player_winnings = 0
            
            for i, turtle in enumerate(results):
                if turtle.name == player_turtle.name:
                    player_rank = i + 1
                    # Calculate winnings based on rank (example: 1st=$100, 2nd=$50, 3rd=$25, others=$10)
                    if player_rank == 1:
                        player_winnings = 100
                    elif player_rank == 2:
                        player_winnings = 50
                    elif player_rank == 3:
                        player_winnings = 25
                    else:
                        player_winnings = 10
                    break
            
            if player_rank:
                reward_text = f"You finished {player_rank}{'st' if player_rank == 1 else 'nd' if player_rank == 2 else 'rd' if player_rank == 3 else 'th'} and won ${player_winnings}!"
                
                reward_label = pygame_gui.elements.UITextBox(
                    relative_rect=pygame.Rect((10, y_pos), (400, 60)),
                    html_text=f"<b>{reward_text}</b>",
                    manager=self.manager,
                    container=self.container_results
                )
                self.result_rows.append(reward_label)
                y_pos += 70
            else:
                # Player didn't finish or wasn't found
                reward_label = pygame_gui.elements.UITextBox(
                    relative_rect=pygame.Rect((10, y_pos), (400, 40)),
                    html_text="<b>You did not finish the race</b>",
                    manager=self.manager,
                    container=self.container_results
                )
                self.result_rows.append(reward_label)
                y_pos += 50
             
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
