"""Reusable Race History Panel Component for displaying race results."""

import pygame
import pygame_gui
from typing import Optional, List, Dict, Any
from .display import TextBox
from core.rich_logging import get_ui_rich_logger


class RaceHistoryPanel:
    """Reusable race history panel component.
    
    Can be reused in Profile, Race Results, and other panels.
    """
    
    def __init__(self, rect: pygame.Rect, manager, container=None, config=None):
        """Initialize race history panel.
        
        Args:
            rect: Panel position and size
            manager: pygame_gui UIManager
            container: pygame_gui container (optional)
            config: Configuration options
        """
        self.rect = rect
        self.manager = manager
        self.container = container
        self.config = config or {}
        self.logger = get_ui_rich_logger()
        
        # UI elements
        self.panel = None
        self.history_text = None
        
        # Configuration
        self.max_races = self.config.get('max_races', 5)
        self.show_header = self.config.get('show_header', True)
        
        # Create the panel
        self._create_panel()
        
    def _create_panel(self) -> None:
        """Create the race history panel UI."""
        # Main panel
        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=self.rect,
            manager=self.manager,
            container=self.container,
            object_id="#race_history_panel"
        )
        
        # Header (optional)
        header_y = 10
        if self.show_header:
            header_text = self.config.get('header_text', 'RECENT RACE HISTORY')
            history_title = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((10, header_y), (self.rect.width - 20, 25)),
                text=header_text,
                manager=self.manager,
                container=self.panel,
                object_id="#history_title"
            )
            header_y += 35
        
        # History Text Box
        text_y = header_y
        text_height = self.rect.height - text_y - 10
        self.history_text = TextBox(
            rect=pygame.Rect((10, text_y), (self.rect.width - 20, text_height)),
            text="",
            manager=self.manager,
            config={'read_only': True}
        )
        self.history_text.container = self.panel
        
    def update_history(self, race_history: List[Dict[str, Any]], title: str = None) -> None:
        """Update the race history display.
        
        Args:
            race_history: List of race result dictionaries
            title: Optional custom title for the display
        """
        if not self.history_text:
            return
            
        if not race_history:
            self.history_text.set_text("No race history yet")
            return
            
        # Build history lines
        history_lines = []
        
        # Add custom title if provided
        if title:
            history_lines.append(f"{title}")
            history_lines.append("-" * len(title))
            history_lines.append("")
        
        # Show recent races
        recent_races = race_history[-self.max_races:]
        for race in recent_races:
            race_num = race.get('number', '?')
            position = race.get('position', '?')
            earnings = race.get('earnings', 0)
            time_str = race.get('time', '')
            
            line = f"Race {race_num}: Position {position}"
            if earnings > 0:
                line += f" - ${earnings}"
            if time_str:
                line += f" ({time_str})"
                
            history_lines.append(line)
            
        # Update history text
        history_text = "\n".join(history_lines)
        self.history_text.set_text(history_text)
        
    def update_race_results(self, race_results: List[Dict[str, Any]], turtle_name: str = None) -> None:
        """Update with race results (alternative format).
        
        Args:
            race_results: List of race result dictionaries
            turtle_name: Name of the turtle to focus on
        """
        if not self.history_text:
            return
            
        if not race_results:
            self.history_text.set_text("No race results yet")
            return
            
        # Filter results for specific turtle if provided
        if turtle_name:
            turtle_results = [
                result for result in race_results 
                if result.get('turtle_name') == turtle_name
            ]
        else:
            turtle_results = race_results
            
        if not turtle_results:
            self.history_text.set_text(f"No results for {turtle_name}" if turtle_name else "No race results yet")
            return
            
        # Build results lines
        results_lines = []
        if turtle_name:
            results_lines.append(f"Results for {turtle_name}")
            results_lines.append("-" * (len(f"Results for {turtle_name}")))
            results_lines.append("")
        
        # Show recent results
        recent_results = turtle_results[-self.max_races:]
        for result in recent_results:
            race_num = result.get('race_number', '?')
            position = result.get('position', '?')
            earnings = result.get('earnings', 0)
            participants = result.get('participants', 0)
            
            line = f"Race {race_num}: {position}/{participants}"
            if earnings > 0:
                line += f" - ${earnings}"
                
            results_lines.append(line)
            
        # Update history text
        history_text = "\n".join(results_lines)
        self.history_text.set_text(history_text)
        
    def clear(self) -> None:
        """Clear the race history display."""
        if self.history_text:
            self.history_text.set_text("")
            
    def show(self) -> None:
        """Show the race history panel."""
        if self.panel and hasattr(self.panel, 'show'):
            self.panel.show()
            
    def hide(self) -> None:
        """Hide the race history panel."""
        if self.panel and hasattr(self.panel, 'hide'):
            self.panel.hide()
            
    def destroy(self) -> None:
        """Clean up the race history panel."""
        if self.history_text:
            self.history_text.destroy()
        if self.panel:
            self.panel.kill() if hasattr(self.panel, 'kill') else None
