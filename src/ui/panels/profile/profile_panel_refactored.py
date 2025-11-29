"""Profile Panel using specialized components built from reusable components."""

import pygame
import pygame_gui
from pygame_gui import UIManager
from typing import Optional, Dict, Any, List
from ..base_panel import BasePanel
from game.game_state_interface import TurboShellsGameStateInterface
from .components import ProfileHeader, ProfileActionPanel, ProfileLayout
from ...components.reusable.stats_panel import StatsPanel
from ...components.reusable.race_history_panel import RaceHistoryPanel
from ...components.reusable.turtle_info_panel import TurtleInfoPanel
from core.rich_logging import get_ui_rich_logger


class ProfilePanelRefactored(BasePanel):
    """Profile Panel using specialized components built from reusable components.
    
    Architecture:
    - BasePanel: Window management and lifecycle
    - Specialized Components: Profile-specific UI elements
    - Reusable Components: Generic UI building blocks
    - Game State: Data management and business logic
    """
    
    def __init__(self, panel_id: str, title: str, game_state: TurboShellsGameStateInterface, 
                 event_bus: Optional[Any] = None):
        """Initialize the profile panel."""
        super().__init__(panel_id, title, event_bus, auto_close_event=False)  # Disable auto-close
        self.game_state = game_state
        self.logger = get_ui_rich_logger()
        
        # Profile data
        self.current_turtle = None
        self.current_index = None
        self.is_retired = False
        
        # Specialized components
        self.header = None
        self.action_panel = None
        self.layout = None
        
        # Reusable components
        self.turtle_info_panel = None
        self.stats_panel = None
        self.race_history_panel = None
        
        # Panel configuration
        self.size = (700, 550)
        self.position = (50, 25)
        
    def _create_window(self) -> None:
        """Create the profile panel window using specialized components."""
        super()._create_window()
        if not self.window:
            return
            
        # Get the window's container for proper positioning
        container = self.window.get_container()
        # Create layout manager with container reference (positions will be calculated relative to container)
        self.layout = ProfileLayout(container, self.manager, container)
        
        # Create specialized components
        self._create_header()
        self._create_action_panel()
        
        # Create reusable components
        self._create_turtle_info_section()
        self._create_stats_section()
        self._create_history_section()
        
    def _create_header(self) -> None:
        """Create the header section using specialized component."""
        header_rect = self.layout.get_position('header')
        self.header = ProfileHeader(
            rect=header_rect,
            width=self.size[0] - 40,
            manager=self.manager,
            container=self.window.get_container(),
            event_bus=self.event_bus
        )
        
    def _create_action_panel(self) -> None:
        """Create the action panel using specialized component."""
        action_rect = self.layout.get_position('actions')
        self.action_panel = ProfileActionPanel(
            rect=action_rect,
            manager=self.manager,
            container=self.window.get_container()
        )
        
    def _create_turtle_info_section(self) -> None:
        """Create the turtle info section using reusable component."""
        info_rect = self.layout.get_position('turtle_info')
        self.turtle_info_panel = TurtleInfoPanel(
            rect=info_rect,
            manager=self.manager,
            container=self.window.get_container(),
            config={
                'image_size': (120, 120),
                'show_status': True,
                'show_age': True
            }
        )
        
    def _create_stats_section(self) -> None:
        """Create the stats section using reusable component."""
        stats_rect = self.layout.get_position('stats')
        self.logger.debug(f"[ProfilePanel] Creating stats section at {stats_rect}")
        self.stats_panel = StatsPanel(
            rect=stats_rect,
            manager=self.manager,
            container=self.window.get_container(),
            config={
                'header_text': 'DETAILED STATS',
                'show_energy': True
            }
        )
        self.logger.debug(f"[ProfilePanel] Stats panel created: {self.stats_panel is not None}")
            
    def _create_history_section(self) -> None:
        """Create the race history section using reusable component."""
        history_rect = self.layout.get_position('history')
        self.race_history_panel = RaceHistoryPanel(
            rect=history_rect,
            manager=self.manager,
            container=self.window.get_container(),
            config={
                'header_text': 'RECENT RACE HISTORY',
                'max_races': 5,
                'show_header': True
            }
        )
        
    def show(self) -> None:
        """Show the profile panel and load turtle data."""
        if not self.manager:
            return
        self.logger.info(f"[ProfilePanel] Showing profile panel for turtle index: {self.game_state.get('profile_turtle_index', 'unknown')}")
        self.logger.debug(f"[ProfilePanel] auto_close_event disabled: {not self.auto_close_event}")
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
            
        # Update release button state through specialized action panel
        if self.action_panel:
            # Don't allow releasing the only active turtle
            active_turtles = [t for t in self.game_state.get('roster', []) if t is not None]
            if len(active_turtles) <= 1 and not self.is_retired:
                self.action_panel.update_button_state(False, "Cannot Release")
            else:
                self.action_panel.update_button_state(True, "Release")
                
    def _show_no_turtle(self) -> None:
        """Show UI when no turtle is selected."""
        # Clear all modular components
        if self.turtle_info_panel:
            self.turtle_info_panel._clear_info()
        if self.stats_panel:
            self.stats_panel.update_stats(None)
        if self.race_history_panel:
            self.race_history_panel.clear()
            
        # Disable release button through specialized action panel
        if self.action_panel:
            self.action_panel.update_button_state(False, "No Turtle")
                
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events for the profile panel."""
        # Let base panel handle window close first
        base_result = super().handle_event(event)
        if base_result:
            self.logger.debug(f"[ProfilePanel] Base panel handled event: {event}")
            return True
                
        # Handle button events through specialized components
        if hasattr(event, 'ui_element'):
            if self.header and event.ui_element == self.header.back_button.button:
                self.logger.debug("[ProfilePanel] Back button clicked")
                # Navigate back to roster
                if self.event_bus:
                    self.event_bus.emit("ui:navigate", {"state": "ROSTER"})
                else:
                    self.game_state.set('state', 'ROSTER')
                return True
                
            elif self.action_panel and event.ui_element == self.action_panel.release_button.button:
                self.logger.debug("[ProfilePanel] Release button clicked")
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
