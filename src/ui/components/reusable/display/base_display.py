"""
Base display component for all display UI elements.
"""

import pygame
from typing import Optional, Dict, Any
from ...base_component import BaseComponent


class BaseDisplayComponent(BaseComponent):
    """Base class for display components following SRP."""
    
    def __init__(self, rect: pygame.Rect, manager=None, config: Optional[Dict] = None):
        """Initialize base display component.
        
        Args:
            rect: Component position and size
            manager: pygame_gui UIManager
            config: Configuration options
        """
        super().__init__(rect, manager)
        self.config = config or {}
        
        # Common display properties
        self.visible = self.config.get('visible', True)
        self.bg_color = self.config.get('bg_color', None)
        self.border_color = self.config.get('border_color', None)
        self.border_width = self.config.get('border_width', 0)
        
    def set_visible(self, visible: bool) -> None:
        """Set component visibility."""
        self.visible = visible
        
    def get_visible(self) -> bool:
        """Get component visibility."""
        return self.visible
        
    def _draw_background(self, surface: pygame.Surface, abs_rect: pygame.Rect) -> None:
        """Draw background if specified."""
        if self.bg_color:
            pygame.draw.rect(surface, self.bg_color, abs_rect)
            
    def _draw_border(self, surface: pygame.Surface, abs_rect: pygame.Rect) -> None:
        """Draw border if specified."""
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, abs_rect, self.border_width)
