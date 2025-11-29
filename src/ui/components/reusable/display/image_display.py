"""
ImageDisplay component for showing images.
"""

import pygame
import pygame_gui
from typing import Optional, Dict, Any
from .base_display import BaseDisplayComponent


class ImageDisplay(BaseDisplayComponent):
    """Reusable image display component."""
    
    def __init__(self, rect: pygame.Rect, image_path: Optional[str] = None, 
                 surface: Optional[pygame.Surface] = None, manager=None, config: Optional[Dict] = None):
        """Initialize image display component.
        
        Args:
            rect: Component position and size
            image_path: Path to image file
            surface: Direct surface to display
            manager: pygame_gui UIManager
            config: Configuration options
        """
        super().__init__(rect, manager, config)
        self.image_path = image_path
        self.surface = surface
        
        # Style options
        self.maintain_aspect_ratio = self.config.get('maintain_aspect_ratio', True)
        self.fill_mode = self.config.get('fill_mode', 'contain')  # contain, cover, stretch
        self.placeholder_color = self.config.get('placeholder_color', (200, 200, 200))
        
        self.image: Optional[pygame_gui.elements.UIImage] = None
        
        if self.manager:
            self._create_image()
        else:
            # Custom rendering when no manager
            self._load_surface()
            
    def _create_image(self) -> None:
        """Create the pygame_gui image."""
        if self.surface:
            self.image = pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect(0, 0, self.rect.width, self.rect.height),
                image_surface=self.surface,
                manager=self.manager,
                container=self.container
            )
        elif self.image_path:
            try:
                surface = pygame.image.load(self.image_path)
                self.image = pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect(0, 0, self.rect.width, self.rect.height),
                    image_surface=surface,
                    manager=self.manager,
                    container=self.container
                )
            except:
                # Create placeholder
                self._create_placeholder()
        else:
            self._create_placeholder()
            
    def _create_placeholder(self) -> None:
        """Create a placeholder surface."""
        placeholder = pygame.Surface((self.rect.width, self.rect.height))
        placeholder.fill(self.placeholder_color)
        
        if self.manager:
            self.image = pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect(0, 0, self.rect.width, self.rect.height),
                image_surface=placeholder,
                manager=self.manager,
                container=self.container
            )
        else:
            self.surface = placeholder
            
    def _load_surface(self) -> None:
        """Load surface for custom rendering."""
        if self.image_path:
            try:
                self.surface = pygame.image.load(self.image_path)
            except:
                self._create_placeholder_surface()
        elif not self.surface:
            self._create_placeholder_surface()
            
    def _create_placeholder_surface(self) -> None:
        """Create placeholder surface for custom rendering."""
        self.surface = pygame.Surface((self.rect.width, self.rect.height))
        self.surface.fill(self.placeholder_color)
        
    def render(self, surface: pygame.Surface) -> None:
        """Render image display."""
        if self.image:
            # Handled by pygame_gui
            pass
        elif self.surface:
            # Custom rendering
            abs_rect = self.get_absolute_rect()
            if self.maintain_aspect_ratio:
                # Scale maintaining aspect ratio
                img_rect = self.surface.get_rect()
                target_rect = self.rect.copy()
                
                # Calculate scaling
                scale_x = target_rect.width / img_rect.width
                scale_y = target_rect.height / img_rect.height
                scale = min(scale_x, scale_y)
                
                new_width = int(img_rect.width * scale)
                new_height = int(img_rect.height * scale)
                
                # Center the scaled image
                target_rect.width = new_width
                target_rect.height = new_height
                target_rect.centerx = self.rect.centerx
                target_rect.centery = self.rect.centery
                
                scaled_surface = pygame.transform.scale(self.surface, (new_width, new_height))
                surface.blit(scaled_surface, target_rect)
            else:
                # Stretch to fill
                scaled_surface = pygame.transform.scale(self.surface, (self.rect.width, self.rect.height))
                surface.blit(scaled_surface, self.rect)
                
    def set_image(self, surface: pygame.Surface) -> None:
        """Update the image surface."""
        self.surface = surface
        if self.image:
            self.image.set_image(surface)
            
    def set_image_path(self, path: str) -> None:
        """Update image from file path."""
        self.image_path = path
        try:
            surface = pygame.image.load(path)
            self.set_image(surface)
        except:
            self._create_placeholder()
