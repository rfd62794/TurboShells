"""
ProgressBar component for showing progress.
"""

import pygame
import pygame_gui
from typing import Optional, Dict, Any
from .base_display import BaseDisplayComponent


class ProgressBar(BaseDisplayComponent):
    """Reusable progress bar component."""
    
    def __init__(self, rect: pygame.Rect, current: float = 0, maximum: float = 100,
                 manager=None, config: Optional[Dict] = None):
        """Initialize progress bar component.
        
        Args:
            rect: Component position and size
            current: Current progress value
            maximum: Maximum progress value
            manager: pygame_gui UIManager
            config: Configuration options
        """
        super().__init__(rect, manager, config)
        self.current = current
        self.maximum = maximum
        
        # Style options
        self.bg_color = self.config.get('bg_color', (200, 200, 200))
        self.fill_color = self.config.get('fill_color', (0, 150, 0))
        self.border_color = self.config.get('border_color', (100, 100, 100))
        self.border_width = self.config.get('border_width', 2)
        self.show_text = self.config.get('show_text', True)
        self.text_color = self.config.get('text_color', (0, 0, 0))
        
        self.progress_bar: Optional[pygame_gui.elements.UIProgressBar] = None
        self.font = pygame.font.Font(None, 16)
        
        if self.manager:
            self._create_progress_bar()
            
    def _create_progress_bar(self) -> None:
        """Create the pygame_gui progress bar."""
        self.progress_bar = pygame_gui.elements.UIProgressBar(
            relative_rect=pygame.Rect(0, 0, self.rect.width, self.rect.height),
            manager=self.manager,
            container=self.container
        )
        self._update_progress()
        
    def _update_progress(self) -> None:
        """Update progress bar value."""
        if self.maximum > 0:
            progress = self.current / self.maximum
        else:
            progress = 0
            
        if self.progress_bar:
            self.progress_bar.set_current_progress(progress)
            
    def render(self, surface: pygame.Surface) -> None:
        """Render progress bar."""
        if self.progress_bar:
            # Handled by pygame_gui
            pass
        else:
            # Custom rendering
            abs_rect = self.get_absolute_rect()
            
            # Draw background
            pygame.draw.rect(surface, self.bg_color, abs_rect)
            
            # Draw fill
            if self.maximum > 0:
                progress = min(1.0, max(0.0, self.current / self.maximum))
                fill_width = int(abs_rect.width * progress)
                fill_rect = pygame.Rect(abs_rect.x, abs_rect.y, fill_width, abs_rect.height)
                pygame.draw.rect(surface, self.fill_color, fill_rect)
                
            # Draw border
            if self.border_width > 0:
                pygame.draw.rect(surface, self.border_color, abs_rect, self.border_width)
                
            # Draw text
            if self.show_text:
                percentage = int((self.current / self.maximum) * 100) if self.maximum > 0 else 0
                text = f"{percentage}%"
                text_surface = self.font.render(text, True, self.text_color)
                text_rect = text_surface.get_rect()
                text_rect.center = abs_rect.center
                surface.blit(text_surface, text_rect)
                
    def set_progress(self, current: float, maximum: Optional[float] = None) -> None:
        """Update progress values."""
        self.current = current
        if maximum is not None:
            self.maximum = maximum
        self._update_progress()
        
    def get_progress(self) -> tuple[float, float]:
        """Get current progress values."""
        return self.current, self.maximum
