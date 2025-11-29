"""Refactored Roster Panel using component-based architecture."""

import pygame
import pygame_gui
from .base_panel import BasePanel
from game.game_state_interface import TurboShellsGameStateInterface
from core.rendering.turtle_render_engine import turtle_render_engine
from ..components.roster_view_toggle import RosterViewToggle
from ..components.turtle_action_buttons import TurtleActionButtons


class RosterPanelRefactored(BasePanel):
    """Refactored Roster Panel using component-based architecture.
    
    Now follows SRP by delegating responsibilities to specialized components.
    """
    
    def __init__(self, game_state_interface: TurboShellsGameStateInterface, event_bus=None):
        super().__init__("roster", "Roster", event_bus=event_bus)
        self.game_state = game_state_interface
        
        self.size = (800, 600)
        self.position = (112, 84)
        
        # Main UI elements (reduced from 15+ to just essentials)
        self.lbl_money = None
        self.btn_race = None
        self.btn_menu = None
        self.container_slots = None
        
        # Component-based architecture
        self.view_toggle = None
        self.turtle_slots = []  # List of TurtleActionButtons components
        
        # Betting controls (still monolithic - could be extracted next)
        self.btn_bet_0 = None
        self.btn_bet_5 = None
        self.btn_bet_10 = None
        self.btn_start_race = None
        
        # Observers
        self.game_state.observe('money', self._on_money_changed)
        self.game_state.observe('show_retired_view', self._on_view_changed)
        self.game_state.observe('select_racer_mode', self._on_mode_changed)
        self.game_state.observe('current_bet', self._on_bet_changed)
        
    def _create_window(self) -> None:
        """Create the roster panel window using components."""
        print(f"[RosterPanelRefactored] _create_window() called")
        super()._create_window()
        if not self.window:
            return
            
        if self.manager and self.manager.window_resolution:
            screen_w, screen_h = self.manager.window_resolution
            self.position = ((screen_w - self.size[0]) // 2, (screen_h - self.size[1]) // 2)
            self.window.set_position(self.position)
            
        container = self.window.get_container()
        width = self.size[0] - 40
        
        # Create header panel
        top_bar = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((10, 10), (width, 50)),
            manager=self.manager,
            container=container
        )
        
        # Money label
        self.lbl_money = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20, 15), (200, 30)),
            text=f"Funds: ${self.game_state.get('money', 0)}",
            manager=self.manager,
            container=top_bar
        )
        
        # Race button
        self.btn_race = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width - 440, 70), (100, 30)),
            text="Race",
            manager=self.manager,
            container=container
        )
        
        # Menu button
        self.btn_menu = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width - 100, 10), (100, 40)),
            text="Menu",
            manager=self.manager,
            container=top_bar
        )
        
        # Create view toggle component
        self.view_toggle = RosterViewToggle(
            rect=pygame.Rect((20, 70), (210, 30)),
            manager=self.manager,
            game_state=self.game_state,
            container=container
        )
        self.view_toggle.on_view_changed = self._on_view_toggle_changed
        
        # Create betting controls
        self._create_betting_controls(container, width)
        
        # Create turtle slots container
        self.container_slots = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((10, 120), (width, 450)),
            manager=self.manager,
            container=container
        )
        
        # Create turtle action button components
        self._create_turtle_slots()
        
        # Update initial state
        self._update_slot_content()
        self._update_visibility()
        
    def _create_betting_controls(self, container, width) -> None:
        """Create betting controls (could be extracted to component)."""
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
        
        self.btn_start_race = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width - 220, 110), (200, 40)),
            text="Start Race",
            manager=self.manager,
            container=container,
            visible=False
        )
        
    def _create_turtle_slots(self) -> None:
        """Create turtle slot components using component architecture."""
        if not self.container_slots:
            return
            
        self.turtle_slots.clear()
        
        for i in range(3):
            # Create slot panel
            slot_panel = pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect((10 + i * 250, 10), (240, 400)),
                manager=self.manager,
                container=self.container_slots
            )
            
            # Create turtle image placeholder
            img = pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect((70, 10), (100, 100)),
                image_surface=pygame.Surface((100, 100)),
                manager=self.manager,
                container=slot_panel
            )
            
            # Create name label
            lbl_name = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((10, 120), (220, 30)),
                text="",
                manager=self.manager,
                container=slot_panel
            )
            
            # Create stats text box
            txt_stats = pygame_gui.elements.UITextBox(
                relative_rect=pygame.Rect((10, 150), (220, 150)),
                html_text="",
                manager=self.manager,
                container=slot_panel
            )
            
            # Create action buttons component
            action_buttons = TurtleActionButtons(
                rect=pygame.Rect((0, 0), (240, 400)),
                turtle_index=i,
                manager=self.manager,
                game_state=self.game_state,
                container=slot_panel
            )
            
            # Store slot data
            self.turtle_slots.append({
                'panel': slot_panel,
                'img': img,
                'lbl_name': lbl_name,
                'txt_stats': txt_stats,
                'action_buttons': action_buttons,
                'index': i
            })
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events using component delegation."""
        # Let base panel handle window close first
        if super().handle_event(event):
            return True
            
        # Delegate to view toggle component
        if self.view_toggle and self.view_toggle.handle_event(event):
            return True
            
        # Delegate to turtle action button components
        for slot in self.turtle_slots:
            if slot['action_buttons'].handle_event(event):
                return True
                
        # Handle remaining events (betting, navigation)
        return self._handle_legacy_events(event)
        
    def _handle_legacy_events(self, event: pygame.event.Event) -> bool:
        """Handle legacy events not yet componentized."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_menu:
                self.game_state.set('select_racer_mode', False)
                self._navigate('MENU')
                return True
            elif event.ui_element == self.btn_race:
                self.game_state.set('select_racer_mode', False)
                self._navigate('RACE')
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
            elif event.ui_element == self.btn_start_race:
                return self._start_race()
        return False
        
    def _update_slot_content(self) -> None:
        """Update turtle slot content using component architecture."""
        show_retired = self.game_state.get('show_retired_view', False)
        select_mode = self.game_state.get('select_racer_mode', False)
        active_racer_idx = self.game_state.get('active_racer_index', -1)
        
        # Get appropriate roster
        if show_retired:
            turtles = self.game_state.get('retired_roster', [])
        else:
            turtles = self.game_state.get('roster', [])
            
        print(f"[DEBUG] RosterPanelRefactored update: {len(turtles)} turtles")
        
        # Update each slot
        for i, slot in enumerate(self.turtle_slots):
            if i < len(turtles):
                self._populate_slot(slot, turtles[i], show_retired, select_mode, active_racer_idx)
            else:
                self._clear_slot(slot)
                
    def _populate_slot(self, slot, turtle, show_retired, select_mode, active_racer_idx) -> None:
        """Populate a single turtle slot."""
        # Set name
        slot['lbl_name'].set_text(turtle.name)
        
        # Set image
        try:
            surf = turtle_render_engine.generate_ui_surface(turtle, size=(100, 100))
            if surf:
                slot['img'].set_image(surf)
        except Exception as e:
            print(f"[ERROR] Failed to render turtle {turtle.name}: {e}")
            
        # Set stats
        stats_text = f"""
        Speed: {turtle.speed}
        Energy: {turtle.energy}
        Wins: {getattr(turtle, 'wins', 0)}
        """
        slot['txt_stats'].set_text(stats_text)
        
        # Update action buttons component
        action_buttons = slot['action_buttons']
        action_buttons.update_mode(
            is_retired_turtle=show_retired,
            is_select_mode=select_mode,
            is_active_racer=(i == active_racer_idx)
        )
        
    def _clear_slot(self, slot) -> None:
        """Clear a turtle slot."""
        slot['lbl_name'].set_text("")
        slot['txt_stats'].set_text("")
        slot['img'].set_image(pygame.Surface((100, 100)))
        
        # Hide action buttons
        action_buttons = slot['action_buttons']
        action_buttons.update_mode(is_retired_turtle=True, is_select_mode=False)
        
    def _update_visibility(self) -> None:
        """Update visibility of betting controls."""
        select_mode = self.game_state.get('select_racer_mode', False)
        
        if select_mode:
            self.btn_bet_0.show()
            self.btn_bet_5.show()
            self.btn_bet_10.show()
            if self.btn_start_race:
                self.btn_start_race.show()
            self.window.set_display_title("Select Racer")
        else:
            self.btn_bet_0.hide()
            self.btn_bet_5.hide()
            self.btn_bet_10.hide()
            if self.btn_start_race:
                self.btn_start_race.hide()
            self.window.set_display_title("Roster")
            
        self._update_slot_content()
        
    def _on_view_toggle_changed(self, show_retired: bool) -> None:
        """Handle view toggle change."""
        print(f"[DEBUG] View toggle changed to: {'retired' if show_retired else 'active'}")
        self._update_slot_content()
        
    def _on_money_changed(self, key, old, new):
        """Handle money change."""
        if self.lbl_money:
            self.lbl_money.set_text(f"Funds: ${new}")
            
    def _on_view_changed(self, key, old, new):
        """Handle view change."""
        self._update_slot_content()
        
    def _on_mode_changed(self, key, old, new):
        """Handle mode change."""
        self._update_visibility()
        
    def _on_bet_changed(self, key, old, new):
        """Handle bet change."""
        if self.btn_bet_0:
            self.btn_bet_0.set_text("Bet: $0" if new != 0 else "[Bet: $0]")
        if self.btn_bet_5:
            self.btn_bet_5.set_text("Bet: $5" if new != 5 else "[Bet: $5]")
        if self.btn_bet_10:
            self.btn_bet_10.set_text("Bet: $10" if new != 10 else "[Bet: $10]")
            
    def _start_race(self) -> bool:
        """Start the race."""
        active_racer_idx = self.game_state.get('active_racer_index', -1)
        if active_racer_idx >= 0:
            self.game_state.set('start_race', active_racer_idx)
            return True
        return False
        
    def _clear_ui_elements(self):
        """Clear UI elements."""
        # Clear components
        if self.view_toggle:
            self.view_toggle.destroy()
            self.view_toggle = None
            
        for slot in self.turtle_slots:
            slot['action_buttons'].destroy()
            
        self.turtle_slots.clear()
        
        # Clear legacy elements
        self.lbl_money = None
        self.btn_race = None
        self.btn_menu = None
        self.btn_bet_0 = None
        self.btn_bet_5 = None
        self.btn_bet_10 = None
        self.btn_start_race = None
        self.container_slots = None
