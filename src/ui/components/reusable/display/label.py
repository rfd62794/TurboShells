"""
Label component for text display.
"""

import pygame
import pygame_gui
from typing import Optional, Dict, Any
from .base_display import BaseDisplayComponent


class Label(BaseDisplayComponent):
    """Reusable label component with styling options."""
    
    def __init__(self, rect: pygame.Rect, text: str = "", manager=None, config: Optional[Dict] = None):
        """Initialize label component.
        
        Args:
            rect: Component position and size
            text: Display text
            manager: pygame_gui UIManager
            config: Configuration options
        """
        super().__init__(rect, manager, config)
        self.text = text
        
        # Style options
        self.font_size = self.config.get('font_size', 18)
        self.text_color = self.config.get('text_color', (0, 0, 0))
        self.alignment = self.config.get('alignment', 'left')
        self.word_wrap = self.config.get('word_wrap', True)
        
        self.label: Optional[pygame_gui.elements.UILabel] = None
        
        if self.manager:
            self._create_label()
            
    def _create_label(self) -> None:
        """Create the pygame_gui label."""
        self.label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0, 0, self.rect.width, self.rect.height),
            text=self.text,
            manager=self.manager,
            container=self.container
        )
        
    def render(self, surface: pygame.Surface) -> None:
        """Render label (handled by pygame_gui)."""
        # Label is rendered by pygame_gui automatically
        pass
        
    def set_text(self, text: str) -> None:
        """Update label text."""
        self.text = text
        if self.label:
            self.label.set_text(text)
            
    def get_text(self) -> str:
        """Get current text."""
        return self.text
