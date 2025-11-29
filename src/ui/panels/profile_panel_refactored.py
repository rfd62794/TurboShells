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
        
        # Create UI elements
        self._create_header_section(container, width)
        self._create_stats_section(container, width)
        self._create_history_section(container, width)
        self._create_action_buttons(container, width)
        
    def _create_header_section(self, container, width: int) -> None:
        """Create the header section with turtle name and image."""
        # Header panel
        header = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 0), (width + 40, 80)),
            manager=self.manager,
            container=container,
            object_id="#profile_header"
        )
        
        # Back button
        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, 10), (80, 30)),
            text="Back",
            manager=self.manager,
            container=header,
            object_id="#back_button"
        )
        
        # Turtle name label (will be updated when turtle data loads)
        self.name_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((100, 20), (width - 120, 40)),
            text="Select a turtle to view profile",
            manager=self.manager,
            container=header,
            object_id="#turtle_name"
        )
        
    def _create_stats_section(self, container, width: int) -> None:
        """Create the stats section showing turtle attributes."""
        # Stats panel
        stats_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 90), (width + 40, 200)),
            manager=self.manager,
            container=container,
            object_id="#stats_panel"
        )
        
        # Create stat labels
        stats = [
            ("Speed", "speed"),
            ("Energy", "energy"),
            ("Stamina", "stamina"),
            ("Luck", "luck"),
            ("Races", "races"),
            ("Wins", "wins")
        ]
        
        y_offset = 10
        for label_text, stat_key in stats:
            # Stat label
            label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((20, y_offset), (100, 25)),
                text=f"{label_text}:",
                manager=self.manager,
                container=stats_panel,
                object_id=f"#{stat_key}_label"
            )
            
            # Stat value
            value_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((130, y_offset), (100, 25)),
                text="-",
                manager=self.manager,
                container=stats_panel,
                object_id=f"#{stat_key}_value"
            )
            
            self.stats_labels[stat_key] = value_label
            y_offset += 30
            
    def _create_history_section(self, container, width: int) -> None:
        """Create the race history section."""
        # History panel
        history_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 300), (width + 40, 180)),
            manager=self.manager,
            container=container,
            object_id="#history_panel"
        )
        
        # History title
        history_title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20, 10), (200, 25)),
            text="Recent Race History:",
            manager=self.manager,
            container=history_panel,
            object_id="#history_title"
        )
        
        # History text
        self.history_text = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect((20, 40), (width - 40, 120)),
            html_text="No race history yet",
            manager=self.manager,
            container=history_panel,
            object_id="#history_text"
        )
        
    def _create_action_buttons(self, container, width: int) -> None:
        """Create the action buttons section."""
        # Action panel
        action_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, 490), (width + 40, 50)),
            manager=self.manager,
            container=container,
            object_id="#action_panel"
        )
        
        # Release button
        self.release_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((width - 120, 10), (100, 30)),
            text="Release",
            manager=self.manager,
            container=action_panel,
            object_id="#release_button"
        )
        
    def show(self) -> None:
        """Show the profile panel and load turtle data."""
        if not self.manager:
            return
        super().show()
        self._load_turtle_data()
        
    def _load_turtle_data(self) -> None:
        """Load the current turtle's data and update UI."""
        # Get current turtle index from game state
        if hasattr(self.game_state.game, 'profile_turtle_index'):
            self.current_index = self.game_state.game.profile_turtle_index
        else:
            self.current_index = self.game_state.get('profile_turtle_index', 0)
            
        # Get turtle data
        if self.current_index is not None:
            turtle_data = self.game_state.get('roster', [])
            if self.current_index < len(turtle_data):
                self.current_turtle = turtle_data[self.current_index]
                self._update_ui()
            else:
                self.current_turtle = None
                self._show_no_turtle()
        else:
            self.current_turtle = None
            self._show_no_turtle()
            
    def _update_ui(self) -> None:
        """Update UI elements with current turtle data."""
        if not self.current_turtle:
            self._show_no_turtle()
            return
            
        # Update name
        if self.name_label:
            turtle_name = self.current_turtle.get('name', 'Unknown Turtle')
            self.name_label.set_text(f"Profile: {turtle_name}")
            
        # Update stats
        stats_to_update = {
            'speed': self.current_turtle.get('speed', 0),
            'energy': self.current_turtle.get('energy', 0),
            'stamina': self.current_turtle.get('stamina', 0),
            'luck': self.current_turtle.get('luck', 0),
            'races': len(self.current_turtle.get('race_history', [])),
            'wins': self.current_turtle.get('wins', 0)
        }
        
        for stat_key, value in stats_to_update.items():
            if stat_key in self.stats_labels:
                self.stats_labels[stat_key].set_text(str(value))
                
        # Update history
        if self.history_text:
            race_history = self.current_turtle.get('race_history', [])
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
            if len(active_turtles) <= 1:
                self.release_button.disable()
                self.release_button.set_text("Cannot Release")
            else:
                self.release_button.enable()
                self.release_button.set_text("Release")
                
    def _show_no_turtle(self) -> None:
        """Show UI when no turtle is selected."""
        if self.name_label:
            self.name_label.set_text("No turtle selected")
            
        # Clear all stats
        for stat_label in self.stats_labels.values():
            stat_label.set_text("-")
            
        # Clear history
        if self.history_text:
            self.history_text.set_text("Select a turtle to view profile")
            
        # Disable release button
        if self.release_button:
            self.release_button.disable()
            self.release_button.set_text("No Turtle")
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events for the profile panel."""
        # Let base panel handle window close first
        if super().handle_event(event):
            return True
                
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.back_button:
                # Navigate back to roster
                if self.event_bus:
                    self.event_bus.emit("ui:navigate", {"state": "ROSTER"})
                else:
                    self.game_state.set('state', 'ROSTER')
                return True
                
            elif event.ui_element == self.release_button:
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
