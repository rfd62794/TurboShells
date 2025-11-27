"""
Profile Panel for TurboShells
Displays detailed information about a selected turtle including stats, 
race history, and management options like Release.
"""

import pygame
import pygame_gui
from typing import Optional
from settings import *
from core.rendering.pygame_turtle_renderer import render_turtle_pygame


class ProfilePanel:
    """Profile panel showing turtle details with pygame_gui"""
    
    def __init__(self, manager: pygame_gui.UIManager, game_state):
        self.manager = manager
        self.game_state = game_state
        self.visible = False
        self.current_turtle = None
        self.current_index = None
        
        # Create main window
        self.size = (700, 550)
        self.window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect((50, 25), self.size),
            window_display_title="Turtle Profile",
            manager=self.manager,
            object_id="#profile_window"
        )
        self.window.hide()
        
        # Create UI elements
        self._create_window()
        
    def _create_window(self):
        """Create all UI elements inside the window"""
        container = self.window.get_container()
        width = self.size[0] - 40
        
        # Header
        header = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 0), (width + 40, 60)),
            manager=self.manager,
            container=container,
            object_id="#profile_header"
        )
        
        # Back Button
        self.btn_back = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width - 100, 10), (100, 40)),
            text="Back",
            manager=self.manager,
            container=header
        )
        
        # Left Panel - Turtle Visual
        self.panel_visual = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((10, 70), (300, 280)),
            manager=self.manager,
            container=container,
            object_id="#profile_visual_panel"
        )
        
        # Turtle Image (will be updated dynamically)
        self.img_turtle = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect((90, 30), (120, 120)),
            image_surface=pygame.Surface((120, 120)),
            manager=self.manager,
            container=self.panel_visual
        )
        
        # Turtle Name
        self.lbl_name = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 160), (280, 30)),
            text="",
            manager=self.manager,
            container=self.panel_visual
        )
        
        # Status Label  
        self.lbl_status = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 195), (280, 25)),
            text="",
            manager=self.manager,
            container=self.panel_visual
        )
        
        # Age Label
        self.lbl_age = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 225), (280, 25)),
            text="",
            manager=self.manager,
            container=self.panel_visual
        )
        
        # Right Panel - Stats
        self.panel_stats = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((320, 70), (360, 280)),
            manager=self.manager,
            container=container,
            object_id="#profile_stats_panel"
        )
        
        # Stats Header
        stats_header = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 10), (340, 25)),
            text="DETAILED STATS",
            manager=self.manager,
            container=self.panel_stats
        )
        
        # Stats Text Box (will show all stats)
        self.txt_stats = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect((10, 40), (340, 180)),
            html_text="",
            manager=self.manager,
            container=self.panel_stats
        )
        
        # Energy Bar (for active turtles)
        self.lbl_energy = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 230), (340, 20)),
            text="",
            manager=self.manager,
            container=self.panel_stats
        )
        
        # Bottom Panel - Race History
        self.panel_history = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((10, 360), (670, 120)),
            manager=self.manager,
            container=container,
            object_id="#profile_history_panel"
        )
        
        history_header = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 10), (300, 25)),
            text="RACE HISTORY (Last 5)",
            manager=self.manager,
            container=self.panel_history
        )
        
        self.txt_history = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect((10, 40), (650, 70)),
            html_text="",
            manager=self.manager,
            container=self.panel_history
        )
        
        # Action Buttons
        self.btn_release = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, 490), (150, 35)),
            text="Release Turtle",
            manager=self.manager,
            container=container,
            object_id="#btn_release_turtle"
        )
        
    def show(self):
        """Show the profile panel and load turtle data"""
        self.window.show()
        self.visible = True
        
        # Get turtle index from game state
        index = self.game_state.get('profile_turtle_index', 0)
        show_retired = self.game_state.get('show_retired_view', False)
        
        # Get turtle
        if show_retired:
            retired_roster = self.game_state.get('retired_roster', [])
            if index < len(retired_roster):
                self.current_turtle = retired_roster[index]
                self.current_index = index
                self.is_retired = True
        else:
            roster = self.game_state.get('roster', [])
            if index < len(roster) and roster[index]:
                self.current_turtle = roster[index]
                self.current_index = index
                self.is_retired = False
        
        # Update UI with turtle data
        if self.current_turtle:
            self._update_turtle_display()
        
    def hide(self):
        """Hide the profile panel"""
        self.window.hide()
        self.visible = False
        
    def _update_turtle_display(self):
        """Update all UI elements with current turtle data"""
        if not self.current_turtle:
            return
        
        t = self.current_turtle
        
        # Update turtle image
        try:
            turtle_img = render_turtle_pygame(t, size=120)
            self.img_turtle.set_image(turtle_img)
        except Exception as e:
            print(f"[DEBUG] Error rendering turtle image: {e}")
        
        # Update name
        self.lbl_name.set_text(f"<b><font size=5>{t.name}</font></b>")
        
        # Update status
        status = "ACTIVE" if self.is_retired == False else "RETIRED"
        status_color = "#00FF00" if self.is_retired == False else "#FFFF00"
        self.lbl_status.set_text(f"<font color={status_color}>[{status}]</font>")
        
        # Update age
        self.lbl_age.set_text(f"Age: {t.age}")
        
        # Update stats
        stats_html = f"""
        <b>Speed:</b> {t.speed}<br>
        <b>Max Energy:</b> {t.max_energy}<br>
        <b>Recovery:</b> {t.recovery}<br>
        <b>Swim:</b> {t.swim}<br>
        <b>Climb:</b> {t.climb}
        """
        self.txt_stats.set_text(stats_html)
        
        # Update energy (for active turtles)
        if not self.is_retired:
            energy_pct = int((t.current_energy / t.max_energy) * 100)
            self.lbl_energy.set_text(f"Energy: {t.current_energy}/{t.max_energy} ({energy_pct}%)")
        else:
            self.lbl_energy.set_text("")
        
        # Update race history
        race_history = getattr(t, 'race_history', [])
        if race_history:
            history_html = "<br>".join([
                f"Race {race.get('number', '?')}: Position {race.get('position', '?')} - ${race.get('earnings', 0)}"
                for race in race_history[-5:]
            ])
        else:
            history_html = "<i>No race history yet</i>"
        self.txt_history.set_text(history_html)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for this panel"""
        # Handle window close
        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.window:
                self.game_state.set('state', 'ROSTER')
                return True
        
        # Handle button clicks
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_back:
                self.game_state.set('state', 'ROSTER')
                return True
            elif event.ui_element == self.btn_release:
                # Confirm release
                if self.current_index is not None:
                    self.game_state.set('release_turtle', self.current_index)
                    # Go back to roster
                    self.game_state.set('state', 'ROSTER')
                return True
        
        return False
    
    def update(self, time_delta: float):
        """Update panel (if needed)"""
        pass
