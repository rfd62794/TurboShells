import pygame
import pygame_gui
from .base_panel import BasePanel
from game.game_state_interface import TurboShellsGameStateInterface
from core.rendering.pygame_turtle_renderer import render_turtle_pygame

class RosterPanel(BasePanel):
    """Roster Panel using pygame_gui."""
    
    def __init__(self, game_state_interface: TurboShellsGameStateInterface):
        super().__init__("roster", "Roster")
        self.game_state = game_state_interface
        
        self.size = (800, 600)
        self.position = (112, 84)
        
        self.lbl_money = None
        self.btn_menu = None
        self.btn_view_active = None
        self.btn_view_retired = None
        
        self.container_slots = None
        self.slots = [] # List of dicts for slot UI elements
        
        # Betting buttons
        self.btn_bet_0 = None
        self.btn_bet_5 = None
        self.btn_bet_10 = None
        
        # Observers
        self.game_state.observe('money', self._on_money_changed)
        self.game_state.observe('show_retired_view', self._on_view_changed)
        self.game_state.observe('select_racer_mode', self._on_mode_changed)
        
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
        
        # Header
        top_bar = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 0), (width + 40, 60)),
            manager=self.manager,
            container=container,
            object_id="#roster_header"
        )
        
        self.lbl_money = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20, 15), (200, 30)),
            text=f"Funds: ${self.game_state.get('money', 0)}",
            manager=self.manager,
            container=top_bar
        )
        
        self.btn_menu = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width - 100, 10), (100, 40)),
            text="Menu",
            manager=self.manager,
            container=top_bar
        )
        
        # View Toggles (Active / Retired)
        self.btn_view_active = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((20, 70), (100, 30)),
            text="Active",
            manager=self.manager,
            container=container
        )
        
        self.btn_view_retired = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((130, 70), (100, 30)),
            text="Retired",
            manager=self.manager,
            container=container
        )
        
        # Betting Controls (Hidden by default, shown in select mode)
        self.btn_bet_0 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width - 330, 70), (100, 30)),
            text="Bet: $0",
            manager=self.manager,
            container=container,
            visible=False
        )
        self.btn_bet_5 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width - 220, 70), (100, 30)),
            text="Bet: $5",
            manager=self.manager,
            container=container,
            visible=False
        )
        self.btn_bet_10 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width - 110, 70), (100, 30)),
            text="Bet: $10",
            manager=self.manager,
            container=container,
            visible=False
        )
        
        # Start Race Button (for select mode)
        self.btn_start_race = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width - 220, 550), (200, 40)),
            text="START RACE",
            manager=self.manager,
            container=container,
            visible=False,
            object_id="#btn_start_race"
        )
        
        # Slots Container
        self.container_slots = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 110), (width + 40, 450)),
            manager=self.manager,
            container=container,
            object_id="#roster_slots_container"
        )
        
        self._populate_slots()
        self._update_visibility()
        
    def _populate_slots(self):
        if not self.container_slots:
            return
            
        # Clear existing slots (conceptually, by killing children)
        # pygame_gui doesn't have clear(), so we iterate children
        # But for now, let's just create them if empty, or update them
        # Since we have fixed 3 slots, we can create them once.
        
        if not self.slots:
            slot_width = 240
            slot_height = 400
            spacing = 20
            start_x = 20
            
            for i in range(3):
                x = start_x + (i * (slot_width + spacing))
                y = 10
                
                panel = pygame_gui.elements.UIPanel(
                    relative_rect=pygame.Rect((x, y), (slot_width, slot_height)),
                    manager=self.manager,
                    container=self.container_slots
                )
                
                # Image
                img = pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect((70, 10), (100, 100)),
                    image_surface=pygame.Surface((100, 100)), # Placeholder
                    manager=self.manager,
                    container=panel
                )
                
                # Name
                lbl_name = pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect((10, 120), (220, 25)),
                    text="Empty",
                    manager=self.manager,
                    container=panel
                )
                
                # Stats
                txt_stats = pygame_gui.elements.UITextBox(
                    relative_rect=pygame.Rect((10, 150), (220, 150)),
                    html_text="",
                    manager=self.manager,
                    container=panel
                )
                
                # Train Button
                btn_train = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect((70, 310), (100, 30)),
                    text="Train",
                    manager=self.manager,
                    container=panel
                )
                
                # Select Button (for race selection)
                btn_select = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect((70, 350), (100, 30)),
                    text="Select",
                    manager=self.manager,
                    container=panel,
                    visible=False
                )
                
                self.slots.append({
                    'panel': panel,
                    'img': img,
                    'lbl_name': lbl_name,
                    'txt_stats': txt_stats,
                    'btn_train': btn_train,
                    'btn_select': btn_select,
                    'index': i
                })
                
        self._update_slot_content()

    def _update_slot_content(self):
        show_retired = self.game_state.get('show_retired_view', False)
        if show_retired:
            turtles = list(self.game_state.get('retired_roster', []))[:3]
        else:
            turtles = list(self.game_state.get('roster', []))
            
        print(f"[DEBUG] RosterPanel update: {len(turtles)} turtles found. Content: {[t.name if t else None for t in turtles]}")
            
        # Pad
        while len(turtles) < 3:
            turtles.append(None)
            
        select_mode = self.game_state.get('select_racer_mode', False)
        active_racer_idx = self.game_state.get('active_racer_index', 0)
            
        for i, slot in enumerate(self.slots):
            turtle = turtles[i]
            
            if turtle:
                slot['lbl_name'].set_text(turtle.name)
                
                stats_text = (
                    f"Spd: {turtle.stats['speed']}<br>"
                    f"Eng: {turtle.stats['max_energy']}<br>"
                    f"Rec: {turtle.stats['recovery']}<br>"
                    f"Swm: {turtle.stats['swim']}<br>"
                    f"Clm: {turtle.stats['climb']}"
                )
                slot['txt_stats'].set_text(stats_text)
                
                try:
                    print(f"[DEBUG] Attempting to render turtle: {turtle.name}")
                    print(f"[DEBUG]   Has genetics_system: {turtle.genetics_system is not None}")
                    print(f"[DEBUG]   visual_genetics present: {bool(turtle.visual_genetics)}")
                    if turtle.visual_genetics:
                        print(f"[DEBUG]   genetics keys: {list(turtle.visual_genetics.keys())[:5]}")
                    
                    surf = render_turtle_pygame(turtle, size=100)
                    print(f"[DEBUG]   ✓ Render successful, surface type: {type(surf)}")
                    
                    slot['img'].set_image(surf)
                    print(f"[DEBUG]   ✓ Image set on UIImage element")
                except Exception as e:
                    print(f"[ERROR] Failed to render turtle {turtle.name}: {e}")
                    import traceback
                    traceback.print_exc()
                    
                # Buttons visibility
                if show_retired:
                    slot['btn_train'].hide()
                    slot['btn_select'].hide()
                else:
                    if select_mode:
                        slot['btn_train'].hide()
                        slot['btn_select'].show()
                        if i == active_racer_idx:
                            slot['btn_select'].set_text("[Selected]")
                            slot['panel'].set_relative_position((slot['panel'].relative_rect.x, 0)) # Highlight effect?
                        else:
                            slot['btn_select'].set_text("Select")
                            slot['panel'].set_relative_position((slot['panel'].relative_rect.x, 10))
                    else:
                        slot['btn_train'].show()
                        slot['btn_select'].hide()
                        slot['panel'].set_relative_position((slot['panel'].relative_rect.x, 10))
            else:
                slot['lbl_name'].set_text("Empty Slot")
                slot['txt_stats'].set_text("")
                slot['img'].set_image(pygame.Surface((100, 100))) # Clear image
                slot['btn_train'].hide()
                slot['btn_select'].hide()

    def _update_visibility(self):
        select_mode = self.game_state.get('select_racer_mode', False)
        
        if select_mode:
            self.btn_view_active.hide()
            self.btn_view_retired.hide()
            self.btn_bet_0.show()
            self.btn_bet_5.show()
            self.btn_bet_10.show()
            if self.btn_start_race:
                self.btn_start_race.show()
            self.window.set_display_title("Select Racer")
        else:
            self.btn_view_active.show()
            self.btn_view_retired.show()
            self.btn_bet_0.hide()
            self.btn_bet_5.hide()
            self.btn_bet_10.hide()
            if self.btn_start_race:
                self.btn_start_race.hide()
            self.window.set_display_title("Roster")
            
        self._update_slot_content()

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_menu:
                self.game_state.set('state', 'menu')
                self.game_state.set('select_racer_mode', False) # Reset mode
                return True
            elif event.ui_element == self.btn_view_active:
                self.game_state.set('toggle_view', False)
                return True
            elif event.ui_element == self.btn_view_retired:
                self.game_state.set('toggle_view', True)
                return True
            elif event.ui_element == self.btn_bet_0:
                self.game_state.set('set_bet', 0)
                return True
            elif event.ui_element == self.btn_bet_5:
                self.game_state.set('set_bet', 5)
                return True
            elif event.ui_element == self.btn_bet_10:
                self.game_state.set('set_bet', 10)
                return True
            elif self.btn_start_race and event.ui_element == self.btn_start_race:
                self.game_state.set('start_race', True)
                return True
            else:
                for slot in self.slots:
                    if event.ui_element == slot['btn_train']:
                        self.game_state.set('train_turtle', slot['index'])
                        self._update_slot_content() # Refresh stats
                        return True
                    elif event.ui_element == slot['btn_select']:
                        self.game_state.set('set_active_racer', slot['index'])
                        self._update_slot_content() # Refresh selection
                        return True
        return False

    def _on_money_changed(self, key, old, new):
        if self.lbl_money:
            self.lbl_money.set_text(f"Funds: ${new}")
            
    def _on_view_changed(self, key, old, new):
        self._update_slot_content()
        
    def _on_mode_changed(self, key, old, new):
        self._update_visibility()

    def show(self):
        print(f"[DEBUG] RosterPanel.show() called")
        super().show()
        self._update_visibility()
        self._update_slot_content()
        print(f"[DEBUG] RosterPanel.show() complete - window visible: {self.window.visible if self.window else 'NO WINDOW'}")
    
    def hide(self):
        print(f"[DEBUG] RosterPanel.hide() called")
        super().hide()
        
    def update(self, time_delta: float) -> None:
        super().update(time_delta)
        # Maybe periodically refresh stats if training happens elsewhere?
        # For now, explicit refresh on action is enough.
