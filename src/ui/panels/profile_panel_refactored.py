"""Refactored Profile Panel using SRP components."""

import pygame
import pygame_gui
from pygame_gui import UIManager
from typing import Optional, Dict, Any, List
from .base_panel import BasePanel
from game.game_state_interface import TurboShellsGameStateInterface


class ProfilePanelRefactored(BasePanel):
    """Refactored Profile Panel using component-based architecture.
    
    Follows SRP by separating concerns:
    - BasePanel: Window management and lifecycle
    - Components: Individual UI elements and behaviors
    - Game State: Data management and business logic
    """
    
    def __init__(self, panel_id: str, title: str, game_state: TurboShellsGameStateInterface, 
                 event_bus: Optional[Any] = None):
        """Initialize the refactored profile panel."""
        super().__init__(panel_id, title, event_bus)
        self.game_state = game_state
        
        # Profile data
        self.current_turtle = None
        self.current_index = None
        
        # UI components will be created in _create_window
        self.back_button = None
        self.release_button = None
        self.name_label = None
        self.stats_labels = {}
        self.history_text = None
        
        # Panel configuration
        self.size = (700, 550)
        self.position = (50, 25)
        
    def _create_window(self) -> None:
        """Create the profile panel window using SRP components."""
        super()._create_window()
        if not self.window:
            return
            
        # Get the window's container for proper positioning
        container = self.window.get_container()
        width = self.size[0] - 40
        
        # Create UI elements matching original layout
        self._create_header_section(container, width)
        self._create_visual_section(container)  # Left panel with turtle image
        self._create_stats_section(container)    # Right panel with detailed stats
        self._create_history_section(container, width)
        self._create_action_buttons(container, width)
        
    def _create_header_section(self, container, width: int) -> None:
        """Create the header section with back button."""
        # Header panel
        header = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 0), (width + 40, 60)),
            manager=self.manager,
            container=container,
            object_id="#profile_header"
        )
        
        # Back button using our auto-sizing component
        from ..components.reusable.input import Button
        self.back_button = Button(
            rect=pygame.Rect((width - 100, 10), (80, 40)),
            text="Back",
            action="back",
            manager=self.manager,
            container=header,
            config={'auto_resize': True, 'min_width': 80, 'padding': 20}
        )
        
    def _create_visual_section(self, container) -> None:
        """Create the left visual section with turtle image and basic info."""
        # Visual panel - left side
        self.visual_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((10, 70), (300, 280)),
            manager=self.manager,
            container=container,
            object_id="#profile_visual_panel"
        )
        
        # Turtle Image (will be updated dynamically)
        self.turtle_image = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect((90, 30), (120, 120)),
            image_surface=pygame.Surface((120, 120)),
            manager=self.manager,
            container=self.visual_panel
        )
        
        # Turtle Name
        self.name_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 160), (280, 30)),
            text="",
            manager=self.manager,
            container=self.visual_panel
        )
        
        # Status Label  
        self.status_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 195), (280, 25)),
            text="",
            manager=self.manager,
            container=self.visual_panel
        )
        
        # Age Label
        self.age_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 225), (280, 25)),
            text="",
            manager=self.manager,
            container=self.visual_panel
        )
        
    def _create_stats_section(self, container) -> None:
        """Create the right stats section with detailed turtle attributes."""
        # Stats panel - right side
        self.stats_panel = pygame_gui.elements.UIPanel(
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
            container=self.stats_panel
        )
        
        # Stats Text Box (will show all stats in HTML format like original)
        self.stats_text = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect((10, 40), (340, 180)),
            html_text="",
            manager=self.manager,
            container=self.stats_panel
        )
        
        # Energy Label (for active turtles)
        self.energy_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 230), (340, 20)),
            text="",
            manager=self.manager,
            container=self.stats_panel
        )
            
    def _create_history_section(self, container, width: int) -> None:
        """Create the race history section."""
        # History panel - bottom left
        history_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((10, 360), (300, 140)),
            manager=self.manager,
            container=container,
            object_id="#history_panel"
        )
        
        # History title
        history_title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 10), (200, 25)),
            text="RECENT RACE HISTORY",
            manager=self.manager,
            container=history_panel,
            object_id="#history_title"
        )
        
        # History text
        self.history_text = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect((10, 40), (280, 90)),
            html_text="No race history yet",
            manager=self.manager,
            container=history_panel,
            object_id="#history_text"
        )
        
    def _create_action_buttons(self, container, width: int) -> None:
        """Create the action buttons section."""
        # Action panel - bottom right
        action_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((320, 360), (360, 140)),
            manager=self.manager,
            container=container,
            object_id="#action_panel"
        )
        
        # Release button using our auto-sizing component
        from ..components.reusable.input import Button
        self.release_button = Button(
            rect=pygame.Rect((260, 50), (80, 40)),
            text="Release",
            action="release",
            manager=self.manager,
            container=action_panel,
            config={'auto_resize': True, 'min_width': 80, 'padding': 20}
        )
        
    def show(self) -> None:
        """Show the profile panel and load turtle data."""
        if not self.manager:
            return
        super().show()
        self._load_turtle_data()
        
    def _load_turtle_data(self) -> None:
        """Load the current turtle's data and update UI."""
        # Get turtle index from game state
        index = self.game_state.get('profile_turtle_index', 0)
        show_retired = self.game_state.get('show_retired_view', False)
        
        # Get turtle from appropriate roster
        if show_retired:
            retired_roster = self.game_state.get('retired_roster', [])
            if index < len(retired_roster):
                self.current_turtle = retired_roster[index]
                self.current_index = index
                self.is_retired = True
            else:
                self.current_turtle = None
                self.current_index = None
                self.is_retired = False
        else:
            roster = self.game_state.get('roster', [])
            if index < len(roster) and roster[index]:
                self.current_turtle = roster[index]
                self.current_index = index
                self.is_retired = False
            else:
                self.current_turtle = None
                self.current_index = None
                self.is_retired = False
                
        # Update UI with turtle data
        if self.current_turtle:
            self._update_ui()
        else:
            self._show_no_turtle()
            
    def _update_ui(self) -> None:
        """Update UI elements with current turtle data."""
        if not self.current_turtle:
            self._show_no_turtle()
            return
            
        # Import turtle renderer for image
        from core.rendering.pygame_turtle_renderer import render_turtle_pygame
        
        # Update turtle image
        try:
            turtle_img = render_turtle_pygame(self.current_turtle, size=120)
            if self.turtle_image:
                self.turtle_image.set_image(turtle_img)
        except Exception as e:
            print(f"[DEBUG] Error rendering turtle image: {e}")
            
        # Update name with HTML formatting like original
        if self.name_label:
            self.name_label.set_text(f"<b><font size=5>{self.current_turtle.name}</font></b>")
            
        # Update status
        if self.status_label:
            status = "ACTIVE" if not self.is_retired else "RETIRED"
            status_color = "#00FF00" if not self.is_retired else "#FFFF00"
            self.status_label.set_text(f"<font color={status_color}>[{status}]</font>")
            
        # Update age
        if self.age_label:
            self.age_label.set_text(f"Age: {self.current_turtle.age}")
            
        # Update detailed stats in HTML format like original
        if self.stats_text:
            stats_html = f"""
            <b>Speed:</b> {self.current_turtle.speed}<br>
            <b>Max Energy:</b> {self.current_turtle.max_energy}<br>
            <b>Recovery:</b> {self.current_turtle.recovery}<br>
            <b>Swim:</b> {self.current_turtle.swim}<br>
            <b>Climb:</b> {self.current_turtle.climb}<br>
            <b>Stamina:</b> {self.current_turtle.stamina}<br>
            <b>Luck:</b> {self.current_turtle.luck}<br>
            <b>Total Races:</b> {len(self.current_turtle.race_history)}<br>
            <b>Total Wins:</b> {self.current_turtle.wins}
            """
            self.stats_text.set_text(stats_html)
            
        # Update energy (for active turtles only)
        if self.energy_label:
            if not self.is_retired:
                energy_pct = int((self.current_turtle.current_energy / self.current_turtle.max_energy) * 100)
                self.energy_label.set_text(f"Energy: {self.current_turtle.current_energy}/{self.current_turtle.max_energy} ({energy_pct}%)")
            else:
                self.energy_label.set_text("")
                
        # Update history
        if self.history_text:
            race_history = self.current_turtle.race_history
            if race_history:
                history_html = "<br>".join([
                    f"Race {race.get('number', '?')}: Position {race.get('position', '?')} - ${race.get('earnings', 0)}"
                    for race in race_history[-5:]
                ])
            else:
                history_html = "<i>No race history yet</i>"
            self.history_text.set_text(history_html)
            
        # Update release button state
        if self.release_button:
            # Don't allow releasing the only active turtle
            active_turtles = [t for t in self.game_state.get('roster', []) if t is not None]
            if len(active_turtles) <= 1 and not self.is_retired:
                self.release_button.set_enabled(False)
                self.release_button.set_text("Cannot Release")
            else:
                self.release_button.set_enabled(True)
                self.release_button.set_text("Release")
                
    def _show_no_turtle(self) -> None:
        """Show UI when no turtle is selected."""
        # Clear turtle image
        if self.turtle_image:
            self.turtle_image.set_image(pygame.Surface((120, 120)))
            
        # Update name
        if self.name_label:
            self.name_label.set_text("No turtle selected")
            
        # Clear status and age
        if self.status_label:
            self.status_label.set_text("")
        if self.age_label:
            self.age_label.set_text("")
            
        # Clear stats
        if self.stats_text:
            self.stats_text.set_text("Select a turtle to view profile")
            
        # Clear energy
        if self.energy_label:
            self.energy_label.set_text("")
            
        # Clear history
        if self.history_text:
            self.history_text.set_text("Select a turtle to view profile")
            
        # Disable release button
        if self.release_button:
            self.release_button.set_enabled(False)
            self.release_button.set_text("No Turtle")
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events for the profile panel."""
        # Let base panel handle window close first
        if super().handle_event(event):
            return True
                
        # Handle button events through our Button components
        if hasattr(event, 'ui_element'):
            if event.ui_element == self.back_button.button:
                # Navigate back to roster
                if self.event_bus:
                    self.event_bus.emit("ui:navigate", {"state": "ROSTER"})
                else:
                    self.game_state.set('state', 'ROSTER')
                return True
                
            elif event.ui_element == self.release_button.button:
                # Release the turtle
                if self.current_index is not None and self.current_turtle:
                    self.game_state.set('release_turtle', self.current_index)
                    # Navigate back to roster
                    if self.event_bus:
                        self.event_bus.emit("ui:navigate", {"state": "ROSTER"})
                    else:
                        self.game_state.set('state', 'ROSTER')
                return True
                
        return False
        
    def update(self, time_delta: float) -> None:
        """Update the profile panel."""
        super().update(time_delta)
        
        # Reload data if turtle index changed
        current_index = self.game_state.get('profile_turtle_index', None)
        if current_index != self.current_index:
            self._load_turtle_data()
