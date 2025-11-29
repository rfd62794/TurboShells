"""
IconButton component with icon support.
"""

import pygame
import pygame_gui
from typing import Optional, Dict, Any
from .button import Button


class IconButton(Button):
    """Button with icon support."""
    
    def __init__(self, rect: pygame.Rect, text: str, icon: str = "", action: str = "",
                 manager=None, config: Optional[Dict] = None):
        """Initialize icon button.
        
        Args:
            rect: Component position and size
            text: Button text
            icon: Icon identifier or path
            action: Action identifier
            manager: pygame_gui UIManager
            config: Configuration options
        """
        # Initialize with empty text first, we'll add icon later
        super().__init__(rect, text, action, manager, config)
        
        # Icon-specific properties
        self.icon = icon
        self.icon_surface: Optional[pygame.Surface] = None
        self.icon_size = config.get('icon_size', 24) if config else 24
        
        # Load icon if provided
        if self.icon:
            self._load_icon()
            
        # Update button text to include icon
        self._update_button_text()
        
    def _load_icon(self) -> None:
        """Load icon from file or create placeholder."""
        try:
            # Try to load from file
            self.icon_surface = pygame.image.load(self.icon)
            # Scale to appropriate size
            self.icon_surface = pygame.transform.scale(
                self.icon_surface, (self.icon_size, self.icon_size)
            )
        except:
            # Create placeholder icon
            self.icon_surface = pygame.Surface((self.icon_size, self.icon_size))
            self.icon_surface.fill((100, 100, 100))
            
    def _update_button_text(self) -> None:
        """Update button text to include icon."""
        if self.ui_element:
            # For now, just set text. In a full implementation,
            # we'd need to handle icon rendering separately
            display_text = f"[{self.icon}] {self.text}" if self.text else f"[{self.icon}]"
            self.ui_element.set_text(display_text)
            
    def set_icon(self, icon: str) -> None:
        """Update button icon."""
        self.icon = icon
        if icon:
            self._load_icon()
        else:
            self.icon_surface = None
        self._update_button_text()
        
    def set_text(self, text: str) -> None:
        """Update button text."""
        super().set_text(text)
        self._update_button_text()
