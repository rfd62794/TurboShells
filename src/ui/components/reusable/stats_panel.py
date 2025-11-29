"""Reusable Stats Panel Component for displaying turtle statistics."""

import pygame
import pygame_gui
from typing import Optional, Dict, Any
from .display import TextBox
from core.rich_logging import get_ui_rich_logger


class StatsPanel:
    """Reusable stats panel component for displaying turtle statistics.
    
    Can be reused in Profile, Breeding, and other panels.
    """
    
    def __init__(self, rect: pygame.Rect, manager, container=None, config=None):
        """Initialize stats panel.
        
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
        self.stats_text = None
        self.energy_label = None
        
        # Create the panel
        self._create_panel()
        
    def _create_panel(self) -> None:
        """Create the stats panel UI."""
        # Main panel
        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=self.rect,
            manager=self.manager,
            container=self.container,
            object_id="#stats_panel"
        )
        
        # Stats Header
        header_text = self.config.get('header_text', 'DETAILED STATS')
        stats_header = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 10), (self.rect.width - 20, 25)),
            text=header_text,
            manager=self.manager,
            container=self.panel
        )
        
        # Stats Text Box
        text_height = self.rect.height - 80  # Leave space for header and energy label
        self.stats_text = TextBox(
            rect=pygame.Rect((10, 40), (self.rect.width - 20, text_height)),
            text="",
            manager=self.manager,
            config={'read_only': True}
        )
        self.stats_text.container = self.panel
        
        # Energy Label (optional, for active turtles)
        if self.config.get('show_energy', True):
            self.energy_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((10, self.rect.height - 30), (self.rect.width - 20, 20)),
                text="",
                manager=self.manager,
                container=self.panel
            )
            
    def update_stats(self, turtle: Any, is_retired: bool = False) -> None:
        """Update the stats display with turtle data.
        
        Args:
            turtle: Turtle entity with stats
            is_retired: Whether this is a retired turtle
        """
        if not turtle or not self.stats_text:
            return
            
        # Build stats lines
        stats_lines = [
            f"Speed: {turtle.speed}",
            f"Max Energy: {turtle.max_energy}",
            f"Recovery: {turtle.recovery}",
            f"Swim: {turtle.swim}",
            f"Climb: {turtle.climb}",
            f"Stamina: {getattr(turtle, 'stamina', 0)}",
            f"Luck: {getattr(turtle, 'luck', 0)}",
        ]
        
        # Add race stats if available
        if hasattr(turtle, 'race_history') and turtle.race_history:
            stats_lines.extend([
                f"Total Races: {len(turtle.race_history)}",
                f"Total Wins: {turtle.wins}"
            ])
            
        # Update stats text
        stats_text = "\n".join(stats_lines)
        self.stats_text.set_text(stats_text)
        
        # Update energy label for active turtles
        if self.energy_label and not is_retired:
            if hasattr(turtle, 'current_energy'):
                energy_pct = int((turtle.current_energy / turtle.max_energy) * 100)
                self.energy_label.set_text(
                    f"Energy: {turtle.current_energy}/{turtle.max_energy} ({energy_pct}%)"
                )
            else:
                self.energy_label.set_text("")
        elif self.energy_label:
            self.energy_label.set_text("")
            
    def show(self) -> None:
        """Show the stats panel."""
        if self.panel and hasattr(self.panel, 'show'):
            self.panel.show()
            
    def hide(self) -> None:
        """Hide the stats panel."""
        if self.panel and hasattr(self.panel, 'hide'):
            self.panel.hide()
            
    def destroy(self) -> None:
        """Clean up the stats panel."""
        if self.stats_text:
            self.stats_text.destroy()
        if self.energy_label:
            self.energy_label.kill() if hasattr(self.energy_label, 'kill') else None
        if self.panel:
            self.panel.kill() if hasattr(self.panel, 'kill') else None
