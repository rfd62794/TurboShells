"""
MoneyDisplay component for formatted money display.
"""

import pygame
import pygame_gui
from typing import Optional, Dict, Any
from .base_display import BaseDisplayComponent


class MoneyDisplay(BaseDisplayComponent):
    """Specialized component for displaying money with formatting."""
    
    def __init__(self, rect: pygame.Rect, amount: int = 0, manager=None, container=None, config: Optional[Dict] = None):
        """Initialize money display component.
        
        Args:
            rect: Component position and size
            amount: Money amount to display
            manager: pygame_gui UIManager
            container: pygame_gui container
            config: Configuration options
        """
        super().__init__(rect, manager, config)
        self.amount = amount
        
        # Style options
        self.prefix = self.config.get('prefix', '$')
        self.show_cents = self.config.get('show_cents', False)
        self.text_color = self.config.get('text_color', (0, 100, 0))
        self.font_size = self.config.get('font_size', 20)
        
        self.label: Optional[pygame_gui.elements.UILabel] = None
        self.font = pygame.font.Font(None, self.font_size)
        
        if self.manager:
            self._create_label()
            
    def _create_label(self) -> None:
        """Create the pygame_gui label."""
        formatted_text = self._format_amount()
        self.label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, self.rect.width, self.rect.height),
            text=formatted_text,
            manager=self.manager,
            container=self.container
        )
        
    def _format_amount(self) -> str:
        """Format the amount for display."""
        if self.show_cents:
            return f"{self.prefix}{self.amount:.2f}"
        else:
            return f"{self.prefix}{self.amount:,}"
            
    def render(self, surface: pygame.Surface) -> None:
        """Render money display."""
        if self.label:
            # Handled by pygame_gui
            pass
        else:
            # Custom rendering
            abs_rect = self.get_absolute_rect()
            formatted_text = self._format_amount()
            text_surface = self.font.render(formatted_text, True, self.text_color)
            text_rect = text_surface.get_rect()
            text_rect.center = abs_rect.center
            surface.blit(text_surface, text_rect)
            
    def set_amount(self, amount: int) -> None:
        """Update the money amount."""
        self.amount = amount
        if self.label:
            self.label.set_text(self._format_amount())
            
    def get_amount(self) -> int:
        """Get current amount."""
        return self.amount
