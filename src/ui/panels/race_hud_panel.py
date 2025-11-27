import pygame
import pygame_gui
from .base_panel import BasePanel
from game.game_state_interface import TurboShellsGameStateInterface

class RaceHUDPanel(BasePanel):
    """Race HUD Panel using pygame_gui."""
    
    def __init__(self, game_state_interface: TurboShellsGameStateInterface):
        super().__init__("race_hud", "Race HUD")
        self.game_state = game_state_interface
        
        # We won't use self.window as a single container
        # Instead we manage multiple elements
        self.panel_bottom = None
        self.lbl_header = None
        self.lbl_progress = None
        self.progress_bar = None
        
        self.btn_1x = None
        self.btn_2x = None
        self.btn_4x = None
        
        # Observers
        self.game_state.observe('race_speed_multiplier', self._on_speed_changed)
        # We need to update progress bar every frame in update()
        
    def _create_window(self) -> None:
        # Override to create custom layout
        if self.panel_bottom:
            return
            
        screen_w, screen_h = self.manager.window_resolution
        
        # Top Header Label
        self.lbl_header = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20, 20), (600, 30)),
            text="RACE",
            manager=self.manager,
            object_id="#race_header"
        )
        
        # Bottom HUD Panel
        hud_height = 100
        self.panel_bottom = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, screen_h - hud_height), (screen_w, hud_height)),
            manager=self.manager,
            object_id="#race_hud_panel"
        )
        
        # Speed Buttons
        btn_width = 60
        btn_y = 20
        start_x = 20
        
        self.btn_1x = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((start_x, btn_y), (btn_width, 40)),
            text="1x",
            manager=self.manager,
            container=self.panel_bottom
        )
        
        self.btn_2x = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((start_x + btn_width + 10, btn_y), (btn_width, 40)),
            text="2x",
            manager=self.manager,
            container=self.panel_bottom
        )
        
        self.btn_4x = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((start_x + (btn_width + 10)*2, btn_y), (btn_width, 40)),
            text="4x",
            manager=self.manager,
            container=self.panel_bottom
        )
        
        # Progress Bar
        bar_x = start_x + (btn_width + 10)*3 + 40
        bar_width = screen_w - bar_x - 40
        
        self.lbl_progress = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((bar_x, 10), (200, 20)),
            text="Progress",
            manager=self.manager,
            container=self.panel_bottom
        )
        
        self.progress_bar = pygame_gui.elements.UIProgressBar(
            relative_rect=pygame.Rect((bar_x, 35), (bar_width, 30)),
            manager=self.manager,
            container=self.panel_bottom
        )
        
        # Set initial state
        self._update_header()
        
    def show(self):
        if not self.manager:
            return
        self._create_window()
        
        if self.panel_bottom:
            self.panel_bottom.show()
        if self.lbl_header:
            self.lbl_header.show()
        self.visible = True
        
    def hide(self):
        if self.panel_bottom:
            self.panel_bottom.hide()
        if self.lbl_header:
            self.lbl_header.hide()
        self.visible = False
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_1x:
                self.game_state.set('set_race_speed', 1)
                self._update_header()
                return True
            elif event.ui_element == self.btn_2x:
                self.game_state.set('set_race_speed', 2)
                self._update_header()
                return True
            elif event.ui_element == self.btn_4x:
                self.game_state.set('set_race_speed', 4)
                self._update_header()
                return True
        return False

    def update(self, time_delta: float) -> None:
        super().update(time_delta)
        if self.visible:
            # Update progress bar - get from race manager
            race_roster = None
            if hasattr(self.game_state, 'race_manager') and hasattr(self.game_state.race_manager, 'race_roster'):
                race_roster = self.game_state.race_manager.race_roster
                print(f"[DEBUG] RaceHUD: Found race roster with {len(race_roster)} turtles")
            else:
                print(f"[DEBUG] RaceHUD: No race_manager or race_roster found")
                
            if race_roster and len(race_roster) > 0:
                # Get player turtle (first in roster)
                player = race_roster[0]
                if hasattr(player, 'race_distance'):
                    # Use correct track length from settings
                    from settings import TRACK_LENGTH_LOGIC
                    progress = min(1.0, player.race_distance / TRACK_LENGTH_LOGIC)
                    if self.progress_bar:
                        self.progress_bar.set_current_progress(progress)
                        # Debug progress updates
                        if int(progress * 100) % 10 == 0:  # Log every 10% progress
                            print(f"[DEBUG] Race progress: {progress:.1%} ({player.race_distance:.1f}/{TRACK_LENGTH_LOGIC})")
                    else:
                        print(f"[DEBUG] RaceHUD: No progress bar available")
                else:
                    print(f"[DEBUG] RaceHUD: Player turtle has no race_distance attribute")
            else:
                print(f"[DEBUG] No race roster found for progress bar update")
            
            # Update header text periodically or on change
            # self._update_header() # Only if needed

    def _on_speed_changed(self, key, old, new):
        self._update_header()
        
    def _update_header(self):
        if self.lbl_header:
            speed = self.game_state.get('race_speed_multiplier', 1)
            bet = self.game_state.get('current_bet', 0)
            self.lbl_header.set_text(f"RACE (Speed: {speed}x | Bet: ${bet})")
