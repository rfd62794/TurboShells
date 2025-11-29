"""Refactored Profile Panel using modular reusable components."""

import pygame
import pygame_gui
from pygame_gui import UIManager
from typing import Optional, Dict, Any, List
from .base_panel import BasePanel
from game.game_state_interface import TurboShellsGameStateInterface
from ui.components.reusable.input import Button
from ui.components.reusable.stats_panel import StatsPanel
from ui.components.reusable.race_history_panel import RaceHistoryPanel
from ui.components.reusable.turtle_info_panel import TurtleInfoPanel
from core.rich_logging import get_ui_rich_logger


class ProfilePanelRefactored(BasePanel):
    """Refactored Profile Panel using modular component architecture.
    
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
        self.logger = get_ui_rich_logger()
        
        # Profile data
        self.current_turtle = None
        self.current_index = None
        self.is_retired = False
        
        # UI components will be created in _create_window
        self.back_button = None
        self.release_button = None
        
        # Modular components
        self.turtle_info_panel = None
        self.stats_panel = None
        self.race_history_panel = None
        
        # Panel configuration
        self.size = (700, 550)
        self.position = (50, 25)
        
    def _create_window(self) -> None:
        """Create the profile panel window using modular components."""
        super()._create_window()
        if not self.window:
            return
            
        # Get the window's container for proper positioning
        container = self.window.get_container()
        width = self.size[0] - 40
        
        # Create UI elements using modular components
        self._create_header_section(container, width)
        self._create_turtle_info_section(container)  # Left panel with turtle image
        self._create_stats_section(container)        # Right panel with detailed stats
        self._create_history_section(container)       # Bottom left with race history
        self._create_action_buttons(container, width) # Bottom right with actions
        
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
        self.back_button = Button(
            rect=pygame.Rect((width - 100, 10), (80, 40)),
            text="Back",
            action="back",
            manager=self.manager,
            container=header,
            config={'auto_resize': True, 'min_width': 80, 'padding': 20}
        )
        
    def _create_turtle_info_section(self, container) -> None:
        """Create the left turtle info section using modular component."""
        # Turtle info panel - left side
        self.turtle_info_panel = TurtleInfoPanel(
            rect=pygame.Rect((10, 70), (300, 280)),
            manager=self.manager,
            container=container,
            config={
                'image_size': (120, 120),
                'show_status': True,
                'show_age': True
            }
        )
        
    def _create_stats_section(self, container) -> None:
        """Create the stats section using modular component."""
        # Stats panel - right side
        self.stats_panel = StatsPanel(
            rect=pygame.Rect((320, 70), (340, 250)),
            manager=self.manager,
            container=container,
            config={
                'header_text': 'DETAILED STATS',
                'show_energy': True
            }
        )
            
    def _create_history_section(self, container) -> None:
        """Create the race history section using modular component."""
        # History panel - bottom left
        self.race_history_panel = RaceHistoryPanel(
            rect=pygame.Rect((10, 360), (300, 140)),
            manager=self.manager,
            container=container,
            config={
                'header_text': 'RECENT RACE HISTORY',
                'max_races': 5,
                'show_header': True
            }
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
        self.release_button = Button(
            rect=pygame.Rect((240, 50), (80, 40)),  # Moved 20px left from (260, 50)
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
        self.logger.info(f"Showing profile panel for turtle index: {self.game_state.get('profile_turtle_index', 'unknown')}")
        super().show()
        self._load_turtle_data()
        
    def _load_turtle_data(self) -> None:
        """Load the current turtle's data and update UI."""
        # Get turtle index from game state
        index = self.game_state.get('profile_turtle_index', 0)
        show_retired = self.game_state.get('show_retired_view', False)
        
        self.logger.debug(f"Loading turtle data: index={index}, retired={show_retired}")
        
        # Get turtle from appropriate roster
        if show_retired:
            retired_roster = self.game_state.get('retired_roster', [])
            if index < len(retired_roster):
                self.current_turtle = retired_roster[index]
                self.current_index = index
                self.is_retired = True
                self.logger.info(f"Loaded retired turtle: {self.current_turtle.name}")
            else:
                self.current_turtle = None
                self.current_index = None
                self.is_retired = False
                self.logger.warning(f"Retired turtle index {index} out of range")
        else:
            roster = self.game_state.get('roster', [])
            if index < len(roster) and roster[index]:
                self.current_turtle = roster[index]
                self.current_index = index
                self.is_retired = False
                self.logger.info(f"Loaded active turtle: {self.current_turtle.name}")
            else:
                self.current_turtle = None
                self.current_index = None
                self.is_retired = False
                self.logger.warning(f"Active turtle index {index} out of range or empty")
                
        # Update UI with turtle data
        if self.current_turtle:
            self._update_ui()
        else:
            self._show_no_turtle()
            
    def _update_ui(self) -> None:
        """Update UI elements with current turtle data using modular components."""
        if not self.current_turtle:
            self._show_no_turtle()
            return
            
        # Update turtle info panel
        if self.turtle_info_panel:
            self.turtle_info_panel.update_turtle_info(self.current_turtle, self.is_retired)
            
        # Update stats panel
        if self.stats_panel:
            self.stats_panel.update_stats(self.current_turtle, self.is_retired)
                
        # Update race history panel
        if self.race_history_panel:
            if hasattr(self.current_turtle, 'race_history') and self.current_turtle.race_history:
                self.race_history_panel.update_history(self.current_turtle.race_history)
            else:
                self.race_history_panel.clear()
            
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
        # Clear all modular components
        if self.turtle_info_panel:
            self.turtle_info_panel._clear_info()
        if self.stats_panel:
            self.stats_panel.update_stats(None)
        if self.race_history_panel:
            self.race_history_panel.clear()
            
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
