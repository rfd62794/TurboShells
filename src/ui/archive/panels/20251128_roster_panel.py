import pygame
import pygame_gui
from .base_panel import BasePanel
from game.game_state_interface import TurboShellsGameStateInterface
from core.rendering.turtle_render_engine import turtle_render_engine

class RosterPanel(BasePanel):
    """Roster Panel using pygame_gui."""
    
    def __init__(self, game_state_interface: TurboShellsGameStateInterface, event_bus=None):
        super().__init__("roster", "Roster", event_bus=event_bus)
        self.game_state = game_state_interface
        
        self.size = (800, 600)
        self.position = (112, 84)
        
        self.lbl_money = None
        self.btn_race = None
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
        self.game_state.observe('current_bet', self._on_bet_changed)
        
    def _create_window(self) -> None:
        print(f"[RosterPanel] _create_window() called")
        super()._create_window()
        if not self.window:
            print(f"[RosterPanel] _create_window() failed - no window")
            return
            
        if self.manager and self.manager.window_resolution:
            screen_w, screen_h = self.manager.window_resolution
            self.position = ((screen_w - self.size[0]) // 2, (screen_h - self.size[1]) // 2)
            self.window.set_position(self.position)
            
        container = self.window.get_container()
        width = self.size[0] - 40
        
        # Clear any existing UI elements
        print(f"[RosterPanel] Clearing existing UI elements")
        self._clear_ui_elements()
        
        # Header
        top_bar = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 0), (width + 40, 60)),
            manager=self.manager,
            container=container,
            object_id="#roster_header"
        )
        print(f"[RosterPanel] Created top_bar panel")
        
        self.lbl_money = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20, 15), (200, 30)),
            text=f"Funds: ${self.game_state.get('money', 0)}",
            manager=self.manager,
            container=top_bar
        )
        print(f"[RosterPanel] Created money label")
        
        # Race Button (middle right, with betting controls)
        self.btn_race = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width - 440, 70), (100, 30)),
            text="Race",
            manager=self.manager,
            container=container
        )
        
        self.btn_menu = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width - 100, 10), (100, 40)),
            text="Menu",
            manager=self.manager,
            container=top_bar
        )
        print(f"[RosterPanel] Created menu button")
        
        # View Toggles (Active / Retired) - back in main content area
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
        
        # Slots Container
        self.container_slots = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 110), (width + 40, 420)),
            manager=self.manager,
            container=container,
            object_id="#roster_slots_container"
        )
        print(f"[RosterPanel] Created slots container")
        
        # Start Race Button (for select mode)
        # Positioned with betting controls for better UX
        self.btn_start_race = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width - 440, 70), (100, 30)),
            text="START RACE",
            manager=self.manager,
            container=container,
            visible=False,
            object_id="#btn_start_race"
        )
        print(f"[RosterPanel] Created start race button")
        
        self._populate_slots()
        self._update_visibility()
        print(f"[RosterPanel] Window creation completed")
        
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
                    relative_rect=pygame.Rect((70, 270), (100, 30)),
                    text="Train",
                    manager=self.manager,
                    container=panel
                )
                
                # View Button (view profile)
                btn_view = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect((10, 310), (50, 30)),
                    text="View",
                    manager=self.manager,
                    container=panel
                )
                
                # Retire Button
                btn_retire = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect((180, 310), (50, 30)),
                    text="Retire",
                    manager=self.manager,
                    container=panel
                )
                
                # Select Button (for race selection)
                btn_select = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect((70, 310), (100, 30)),
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
                    'btn_view': btn_view,
                    'btn_retire': btn_retire,
                    'btn_select': btn_select,
                    'index': i
                })
                
        self._update_slot_content()

    def _update_slot_content(self):
        print(f"[DEBUG] RosterPanel _update_slot_content() called")
        if not self.slots:
            print(f"[DEBUG] RosterPanel _update_slot_content() - no slots, returning")
            return
            
        show_retired = self.game_state.get('show_retired_view', False)
        if show_retired:
            turtles = list(self.game_state.get('retired_roster', []))[:3]
        else:
            turtles = list(self.game_state.get('roster', []))
            
        print(f"[DEBUG] RosterPanel update: {len(turtles)} turtles")
            
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
                    # Use the new UI method from TurtleRenderEngine
                    sprite_surface = turtle_render_engine.get_turtle_sprite_surface(turtle, (100, 100))
                    if sprite_surface:
                        slot['img'].set_image(sprite_surface)
                        print(f"[DEBUG] RosterPanel: Set sprite surface for {turtle.name}")
                    else:
                        # Fallback to simple colored rectangle
                        surf = pygame.Surface((100, 100), pygame.SRCALPHA)
                        surf.fill((100, 150, 100))
                        font = pygame.font.Font(None, 20)
                        text = font.render(turtle.name[:8], True, (255, 255, 255))
                        text_rect = text.get_rect(center=(50, 50))
                        surf.blit(text, text_rect)
                        slot['img'].set_image(surf)
                        print(f"[DEBUG] RosterPanel: Used fallback surface for {turtle.name}")
                except Exception as e:
                    print(f"[ERROR] Failed to render turtle {turtle.name}: {e}")
                    # Create fallback surface
                    surf = pygame.Surface((100, 100), pygame.SRCALPHA)
                    surf.fill((100, 100, 100))
                    font = pygame.font.Font(None, 20)
                    text = font.render(turtle.name[:8], True, (255, 255, 255))
                    text_rect = text.get_rect(center=(50, 50))
                    surf.blit(text, text_rect)
                    slot['img'].set_image(surf)
                    
                # Buttons visibility
                if show_retired:
                    slot['btn_train'].hide()
                    slot['btn_retire'].hide()
                    slot['btn_select'].hide()
                else:
                    if select_mode:
                        slot['btn_train'].hide()
                        # Keep Retire button visible even in select mode for active turtles
                        slot['btn_retire'].show()
                        slot['btn_select'].show()
                        if i == active_racer_idx:
                            slot['btn_select'].set_text("[Selected]")
                            slot['panel'].set_relative_position((slot['panel'].relative_rect.x, 0)) # Highlight effect?
                        else:
                            slot['btn_select'].set_text("Select")
                            slot['panel'].set_relative_position((slot['panel'].relative_rect.x, 10))
                    else:
                        slot['btn_train'].show()
                        slot['btn_retire'].show()
                        slot['btn_select'].hide()
                        slot['panel'].set_relative_position((slot['panel'].relative_rect.x, 10))
            else:
                slot['lbl_name'].set_text("Empty Slot")
                slot['txt_stats'].set_text("")
                slot['img'].set_image(pygame.Surface((100, 100))) # Clear image
                slot['btn_train'].hide()
                slot['btn_retire'].hide()
                slot['btn_select'].hide()

    def _update_visibility(self):
        select_mode = self.game_state.get('select_racer_mode', False)
        
        if select_mode:
            # Always show Active/Retired toggles, even in select mode
            self.btn_view_active.show()
            self.btn_view_retired.show()
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
        # Let base panel handle window close first
        if super().handle_event(event):
            return True
                
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            print(f"[DEBUG] RosterPanel button pressed: {event.ui_element}")
            print(f"[DEBUG] Main buttons:")
            print(f"  btn_menu: {self.btn_menu}")
            print(f"  btn_race: {self.btn_race}")
            print(f"  btn_view_active: {self.btn_view_active}")
            print(f"  btn_view_retired: {self.btn_view_retired}")
            print(f"  btn_bet_0: {self.btn_bet_0}")
            print(f"  btn_start_race: {self.btn_start_race}")
            print(f"[DEBUG] Checking against {len(self.slots)} slots")
            
            if event.ui_element == self.btn_menu:
                print(f"[DEBUG] ✓ MATCHED Menu button")
                self.game_state.set('select_racer_mode', False)
                self._navigate('MENU')
                return True
            elif event.ui_element == self.btn_race:
                print(f"[DEBUG] ✓ MATCHED Race button")
                self.game_state.set('select_racer_mode', False)
                self._navigate('RACE')
                return True
            elif event.ui_element == self.btn_view_active:
                print(f"[DEBUG] ✓ MATCHED View Active button")
                self.game_state.set('toggle_view', False)
                self._update_slot_content()
                return True
            elif event.ui_element == self.btn_view_retired:
                print(f"[DEBUG] ✓ MATCHED View Retired button")
                self.game_state.set('toggle_view', True)
                self._update_slot_content()
                return True
            elif event.ui_element == self.btn_bet_0:
                print(f"[DEBUG] ✓ MATCHED Bet $0 button")
                self.game_state.set('set_bet', 0)
                return True
            elif event.ui_element == self.btn_bet_5:
                print(f"[DEBUG] ✓ MATCHED Bet $5 button")
                self.game_state.set('set_bet', 5)
                return True
            elif event.ui_element == self.btn_bet_10:
                print(f"[DEBUG] ✓ MATCHED Bet $10 button")
                self.game_state.set('set_bet', 10)
                return True
            elif self.btn_start_race and event.ui_element == self.btn_start_race:
                print(f"[DEBUG] ✓ MATCHED START RACE button!")
                self.game_state.set('start_race', True)
                return True
            else:
                # Check slot buttons
                for slot_idx, slot in enumerate(self.slots):
                    if event.ui_element == slot['btn_train']:
                        print(f"[DEBUG] ✓ MATCHED Train button for slot {slot['index']}")
                        self.game_state.set('train_turtle', slot['index'])
                        self._update_slot_content()
                        return True
                    elif event.ui_element == slot['btn_view']:
                        print(f"[DEBUG] ✓ MATCHED View button for slot {slot['index']}")
                        self.game_state.set('view_profile', slot['index'])
                        return True
                    elif event.ui_element == slot['btn_retire']:
                        print(f"[DEBUG] ✓ MATCHED Retire button for slot {slot['index']}")
                        self.game_state.set('retire_turtle', slot['index'])
                        self._update_slot_content()
                        return True
                    elif event.ui_element == slot['btn_select']:
                        print(f"[DEBUG] ✓ MATCHED Select button for slot {slot['index']}")
                        self.game_state.set('set_active_racer', slot['index'])
                        self._update_slot_content()
                        return True
                
                print(f"[DEBUG] ✗ NO MATCH found for button: {event.ui_element}")
                if hasattr(event.ui_element, 'object_ids'):
                    print(f"[DEBUG] Button Object IDs: {event.ui_element.object_ids}")
                elif hasattr(event.ui_element, 'object_id'):
                    obj_id = event.ui_element.object_id
                    if obj_id == '#close_button':
                        print(f"[DEBUG] Ignoring close button event")
                    else:
                        print(f"[DEBUG] Button Object ID: {obj_id}")
        return False

    def _clear_ui_elements(self):
        """Clear all existing UI elements to prevent duplicates."""
        print(f"[RosterPanel] _clear_ui_elements() called")
        
        # Clear all UI element references
        self.lbl_money = None
        self.btn_race = None
        self.btn_menu = None
        self.btn_view_active = None
        self.btn_view_retired = None
        self.btn_bet_0 = None
        self.btn_bet_5 = None
        self.btn_bet_10 = None
        self.btn_start_race = None
        self.container_slots = None
        self.slots = []
        
        print(f"[RosterPanel] UI element references cleared")

    def _navigate(self, state: str) -> None:
        if self.event_bus:
            self.event_bus.emit("ui:navigate", {"state": state})
        else:
            self.game_state.set('state', state)

    def _on_money_changed(self, key, old, new):
        if self.lbl_money:
            self.lbl_money.set_text(f"Funds: ${new}")
            
    def _on_view_changed(self, key, old, new):
        self._update_slot_content()
        
    def _on_mode_changed(self, key, old, new):
        self._update_visibility()
        
    def _on_bet_changed(self, key, old, new):
        """Update betting button visual feedback based on current bet."""
        if not all([self.btn_bet_0, self.btn_bet_5, self.btn_bet_10]):
            return
            
        # Reset all buttons to normal appearance
        self.btn_bet_0.set_text("Bet: $0")
        self.btn_bet_5.set_text("Bet: $5")
        self.btn_bet_10.set_text("Bet: $10")
        
        # Highlight the active bet button
        if new == 0:
            self.btn_bet_0.set_text("Bet: $0 ✓")
        elif new == 5:
            self.btn_bet_5.set_text("Bet: $5 ✓")
        elif new == 10:
            self.btn_bet_10.set_text("Bet: $10 ✓")

    def show(self):
        print(f"[RosterPanel] SHOW() CALLED!")
        super().show()
        print(f"[RosterPanel] AFTER SUPER().SHOW()")
        self._update_visibility()
        self._update_slot_content()
        print(f"[RosterPanel] SHOW() COMPLETED")
    
    def hide(self):
        super().hide()
        
    def update(self, time_delta: float) -> None:
        super().update(time_delta)
        # Maybe periodically refresh stats if training happens elsewhere?
        # For now, explicit refresh on action is enough.
