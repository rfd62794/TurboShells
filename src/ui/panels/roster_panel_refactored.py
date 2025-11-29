"""Refactored Roster Panel using component-based architecture."""

import pygame
import pygame_gui
from .base_panel import BasePanel
from game.game_state_interface import TurboShellsGameStateInterface
from core.rendering.turtle_render_engine import turtle_render_engine
from ..components.roster.roster_view_toggle import RosterViewToggle
from ..components.roster.turtle_action_buttons import TurtleActionButtons
from ..components.roster.betting_controls import BettingControls
from ..components.roster.header_component import HeaderComponent
from ..components.roster.navigation_component import NavigationComponent


class RosterPanelRefactored(BasePanel):
    """Refactored Roster Panel using component-based architecture.
    
    Now follows SRP by delegating responsibilities to specialized components.
    """
    
    def __init__(self, game_state_interface: TurboShellsGameStateInterface, event_bus=None):
        super().__init__("roster", "Roster", event_bus=event_bus)
        self.game_state = game_state_interface
        
        self.size = (800, 600)
        self.position = (112, 84)
        
        # SRP Component Architecture
        self.header_component = None
        self.navigation_component = None
        self.view_toggle = None
        self.betting_controls = None
        self.turtle_slots = []  # List of TurtleActionButtons components
        
        # Container for slots
        self.container_slots = None
        
        # Observers
        self.game_state.observe('money', self._on_money_changed)
        self.game_state.observe('show_retired_view', self._on_view_changed)
        self.game_state.observe('select_racer_mode', self._on_mode_changed)
        self.game_state.observe('current_bet', self._on_bet_changed)
        self.game_state.observe('active_racer_index', self._on_active_racer_changed)
        
    def _create_window(self) -> None:
        """Create the roster panel window using SRP components."""
        print(f"[RosterPanelRefactored] _create_window() called")
        super()._create_window()
        if not self.window:
            print(f"[RosterPanelRefactored] _create_window() failed - no window")
            return
            
        if self.manager and self.manager.window_resolution:
            screen_w, screen_h = self.manager.window_resolution
            self.position = ((screen_w - self.size[0]) // 2, (screen_h - self.size[1]) // 2)
            self.window.set_position(self.position)
            
        container = self.window.get_container()
        width = self.size[0] - 40
        
        # Clear any existing UI elements
        print(f"[RosterPanelRefactored] Clearing existing UI elements")
        self._clear_ui_elements()
        
        # Create header component (money + menu)
        self.header_component = HeaderComponent(
            rect=pygame.Rect((0, 0), (width + 40, 60)),
            manager=self.manager,
            game_state=self.game_state,
            container=container
        )
        
        # Create navigation component (race button)
        self.navigation_component = NavigationComponent(
            rect=pygame.Rect((0, 70), (width + 40, 30)),
            manager=self.manager,
            game_state=self.game_state,
            container=container,
            on_navigate=self._navigate
        )
        
        # Create view toggle component (active/retired)
        self.view_toggle = RosterViewToggle(
            rect=pygame.Rect((20, 70), (210, 30)),
            manager=self.manager,
            game_state=self.game_state,
            container=container
        )
        self.view_toggle.on_view_changed = self._on_view_toggle_changed
        
        # Create betting controls component
        self.betting_controls = BettingControls(
            rect=pygame.Rect((0, 70), (width + 40, 30)),
            manager=self.manager,
            game_state=self.game_state,
            container=container
        )
        
        # Create slots container (matches original exactly)
        self.container_slots = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 110), (width + 40, 420)),
            manager=self.manager,
            container=container,
            object_id="#roster_slots_container"
        )
        print(f"[RosterPanelRefactored] Created slots container")
        
        # Create turtle slots using original structure
        self._populate_slots()
        
        # Update initial state
        self._update_slot_content()
        self._update_visibility()
        
        print(f"[RosterPanelRefactored] Window creation completed")
        
    def _populate_slots(self):
        """Populate slots using original structure but with componentized buttons."""
        if not self.container_slots:
            return
            
        # Clear existing slots
        self.turtle_slots.clear()
        
        if not self.turtle_slots:
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
                
                # Create action buttons component instead of individual buttons
                action_buttons = TurtleActionButtons(
                    rect=pygame.Rect((0, 0), (slot_width, slot_height)),
                    turtle_index=i,
                    manager=self.manager,
                    game_state=self.game_state,
                    container=panel
                )
                
                self.turtle_slots.append({
                    'panel': panel,
                    'img': img,
                    'lbl_name': lbl_name,
                    'txt_stats': txt_stats,
                    'action_buttons': action_buttons,
                    'index': i
                })
                
        self._update_slot_content()
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events using SRP component delegation."""
        # Handle window close events manually
        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if hasattr(self, 'window') and event.ui_element == self.window:
                self.hide()
                return True
                
        # Delegate to components first (following SRP)
        if self.header_component and self.header_component.handle_event(event):
            return True
            
        if self.navigation_component and self.navigation_component.handle_event(event):
            return True
            
        if self.view_toggle and self.view_toggle.handle_event(event):
            return True
            
        if self.betting_controls and self.betting_controls.handle_event(event):
            return True
            
        for slot in self.turtle_slots:
            if slot['action_buttons'].handle_event(event):
                return True
                
        # No component handled the event
        return False
        
    def _update_slot_content(self) -> None:
        """Update turtle slot content using component architecture."""
        show_retired = self.game_state.get('show_retired_view', False)
        select_mode = self.game_state.get('select_racer_mode', False)
        active_racer_idx = self.game_state.get('active_racer_index', 0)
        
        print(f"[DEBUG] RosterPanelRefactored _update_slot_content() called")
        
        # Get appropriate roster with exact original logic (lines 255-264)
        if show_retired:
            turtles = list(self.game_state.get('retired_roster', []))[:3]
        else:
            turtles = list(self.game_state.get('roster', []))
            
        print(f"[DEBUG] RosterPanelRefactored update: {len(turtles)} turtles")
        
        # Pad to exactly 3 slots (matches original line 263-264)
        while len(turtles) < 3:
            turtles.append(None)
            
        # Update each slot
        for i, slot in enumerate(self.turtle_slots):
            if i < len(turtles):
                if turtles[i]:
                    self._populate_slot(slot, turtles[i], show_retired, select_mode, active_racer_idx, i)
                else:
                    self._clear_slot(slot)
                
    def _populate_slot(self, slot, turtle, show_retired, select_mode, active_racer_idx, i) -> None:
        """Populate a single turtle slot with exact original logic."""
        # Set name
        slot['lbl_name'].set_text(turtle.name)
        
        # Set image with fallback rendering
        try:
            sprite_surface = turtle_render_engine.get_turtle_sprite_surface(turtle, (100, 100))
            if sprite_surface:
                slot['img'].set_image(sprite_surface)
                print(f"[DEBUG] RosterPanelRefactored: Set sprite surface for {turtle.name}")
            else:
                # Fallback to simple colored rectangle (matches original lines 291-298)
                surf = pygame.Surface((100, 100), pygame.SRCALPHA)
                surf.fill((100, 150, 100))
                font = pygame.font.Font(None, 20)
                text = font.render(turtle.name[:8], True, (255, 255, 255))
                text_rect = text.get_rect(center=(50, 50))
                surf.blit(text, text_rect)
                slot['img'].set_image(surf)
                print(f"[DEBUG] RosterPanelRefactored: Used fallback surface for {turtle.name}")
        except Exception as e:
            print(f"[ERROR] Failed to render turtle {turtle.name}: {e}")
            # Create fallback surface (matches original lines 303-309)
            surf = pygame.Surface((100, 100), pygame.SRCALPHA)
            surf.fill((100, 100, 100))
            font = pygame.font.Font(None, 20)
            text = font.render(turtle.name[:8], True, (255, 255, 255))
            text_rect = text.get_rect(center=(50, 50))
            surf.blit(text, text_rect)
            slot['img'].set_image(surf)
            
        # Set stats (matches original exactly)
        stats_text = (
            f"Spd: {turtle.stats['speed']}<br>"
            f"Eng: {turtle.stats['max_energy']}<br>"
            f"Rec: {turtle.stats['recovery']}<br>"
            f"Swm: {turtle.stats['swim']}<br>"
            f"Clm: {turtle.stats['climb']}"
        )
        slot['txt_stats'].set_text(stats_text)
        
        # Update action buttons component with original visibility logic
        action_buttons = slot['action_buttons']
        
        # Exact original button visibility logic (lines 311-339)
        if show_retired:
            action_buttons.update_mode(is_retired_turtle=True, is_select_mode=False)
            slot['panel'].set_relative_position((slot['panel'].relative_rect.x, 10))
        else:
            if select_mode:
                action_buttons.update_mode(is_retired_turtle=False, is_select_mode=True)
                # Keep Retire button visible even in select mode for active turtles
                if i == active_racer_idx:
                    # Update select button text to "[Selected]"
                    action_buttons.update_select_button_text("[Selected]")
                    slot['panel'].set_relative_position((slot['panel'].relative_rect.x, 0))  # Highlight effect
                else:
                    action_buttons.update_select_button_text("Select")
                    slot['panel'].set_relative_position((slot['panel'].relative_rect.x, 10))
            else:
                action_buttons.update_mode(is_retired_turtle=False, is_select_mode=False)
                slot['panel'].set_relative_position((slot['panel'].relative_rect.x, 10))
        
    def _clear_slot(self, slot) -> None:
        """Clear a turtle slot (matches original lines 333-339)."""
        slot['lbl_name'].set_text("Empty Slot")
        slot['txt_stats'].set_text("")
        slot['img'].set_image(pygame.Surface((100, 100))) # Clear image
        
        # Hide all action buttons (matches original)
        action_buttons = slot['action_buttons']
        action_buttons.update_mode(is_retired_turtle=True, is_select_mode=False)
        
    def _update_visibility(self) -> None:
        """Update visibility of betting controls using components."""
        select_mode = self.game_state.get('select_racer_mode', False)
        
        # Update betting controls
        if self.betting_controls:
            self.betting_controls.update_mode(select_mode)
            
        # Update window title
        if select_mode:
            self.window.set_display_title("Select Racer")
        else:
            self.window.set_display_title("Roster")
            
        self._update_slot_content()
        
    def _on_view_toggle_changed(self, show_retired: bool) -> None:
        """Handle view toggle change."""
        print(f"[DEBUG] View toggle changed to: {'retired' if show_retired else 'active'}")
        self._update_slot_content()
        
    def _on_money_changed(self, key, old, new):
        """Handle money change using component."""
        if self.header_component:
            self.header_component.update_money(new)
        if self.betting_controls:
            self.betting_controls.update_money(new)
            
    def _on_view_changed(self, key, old, new):
        """Handle view change."""
        self._update_slot_content()
        
    def _on_mode_changed(self, key, old, new):
        """Handle mode change."""
        self._update_visibility()
        
    def _on_bet_changed(self, key, old, new):
        """Handle bet change using component."""
        if self.betting_controls:
            self.betting_controls.update_bet_feedback(new)
            
    def _on_active_racer_changed(self, key, old, new):
        """Handle active racer change - update UI immediately."""
        print(f"[DEBUG] Active racer changed from {old} to {new}")
        self._update_slot_content()
            
    def show(self):
        print(f"[RosterPanelRefactored] SHOW() CALLED!")
        super().show()
        print(f"[RosterPanelRefactored] AFTER SUPER().SHOW()")
        self._update_visibility()
        self._update_slot_content()
        print(f"[RosterPanelRefactored] SHOW() COMPLETED")
    
    def hide(self):
        super().hide()
        
    def update(self, time_delta: float) -> None:
        super().update(time_delta)
        # Maybe periodically refresh stats if training happens elsewhere?
        # For now, explicit refresh on action is enough.
            
    def _start_race(self) -> bool:
        """Start the race."""
        active_racer_idx = self.game_state.get('active_racer_index', -1)
        if active_racer_idx >= 0:
            self.game_state.set('start_race', active_racer_idx)
            return True
        return False
        
    def _clear_ui_elements(self):
        """Clear all existing UI elements to prevent duplicates."""
        print(f"[RosterPanelRefactored] _clear_ui_elements() called")
        
        # Clean up SRP components
        if self.header_component:
            self.header_component.destroy()
            self.header_component = None
            
        if self.navigation_component:
            self.navigation_component.destroy()
            self.navigation_component = None
            
        if self.view_toggle:
            self.view_toggle.destroy()
            self.view_toggle = None
            
        if self.betting_controls:
            self.betting_controls.destroy()
            self.betting_controls = None
            
        # Clean up turtle slots
        for slot in self.turtle_slots:
            slot['action_buttons'].destroy()
            if slot['panel']:
                slot['panel'].kill()
        
        self.turtle_slots.clear()
        
        # Clear container
        if self.container_slots:
            self.container_slots.kill()
            self.container_slots = None
        
        print(f"[RosterPanelRefactored] UI element references cleared")
            
    def _navigate(self, state: str) -> None:
        """Navigate to another state."""
        if self.event_bus:
            self.event_bus.emit("ui:navigate", {"state": state})
        else:
            self.game_state.set('state', state)
