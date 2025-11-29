"""
TextBox component for multi-line text display.
"""

import pygame
import pygame_gui
from typing import Optional, Dict, Any
from .base_display import BaseDisplayComponent


class TextBox(BaseDisplayComponent):
    """Reusable text box component for multi-line text."""
    
    def __init__(self, rect: pygame.Rect, text: str = "", manager=None, config: Optional[Dict] = None):
        """Initialize text box component.
        
        Args:
            rect: Component position and size
            text: Display text
            manager: pygame_gui UIManager
            config: Configuration options
        """
        super().__init__(rect, manager, config)
        self.text = text
        
        # Style options
        self.read_only = self.config.get('read_only', True)
        self.scrollable = self.config.get('scrollable', True)
        
        self.text_box: Optional[pygame_gui.elements.UITextBox] = None
        
        if self.manager:
            self._create_text_box()
            
    def _create_text_box(self) -> None:
        """Create the pygame_gui text box."""
        self.text_box = pygame_gui.elements.UITextBox(
            html_text=self.text,
            relative_rect=pygame.Rect(0, 0, self.rect.width, self.rect.height),
            manager=self.manager,
            container=self.container
        )
        
    def render(self, surface: pygame.Surface) -> None:
        """Render text box (handled by pygame_gui)."""
        # Text box is rendered by pygame_gui automatically
        pass
        
    def set_text(self, text: str) -> None:
        """Update text box content."""
        self.text = text
        if self.text_box:
            self.text_box.set_text(text)
            
    def append_text(self, text: str) -> None:
        """Append text to existing content."""
        self.text += text
        if self.text_box:
            self.text_box.append_text(text)
