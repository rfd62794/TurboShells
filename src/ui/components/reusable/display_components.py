"""
Reusable display components that can be used across all UI panels.
"""

import pygame
import pygame_gui
from typing import Optional, Dict, Any, Union
from ..base_component import BaseComponent


class Label(BaseComponent):
    """Reusable label component with styling options."""
    
    def __init__(self, rect: pygame.Rect, text: str = "", manager=None, config: Optional[Dict] = None):
        """Initialize label component.
        
        Args:
            rect: Component position and size
            text: Display text
            manager: pygame_gui UIManager
            config: Configuration options
        """
        super().__init__(rect, manager)
        self.text = text
        self.config = config or {}
        
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
            manager=self.manager
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


class TextBox(BaseComponent):
    """Reusable text box component for multi-line text."""
    
    def __init__(self, rect: pygame.Rect, text: str = "", manager=None, config: Optional[Dict] = None):
        """Initialize text box component.
        
        Args:
            rect: Component position and size
            text: Display text
            manager: pygame_gui UIManager
            config: Configuration options
        """
        super().__init__(rect, manager)
        self.text = text
        self.config = config or {}
        
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
            manager=self.manager
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


class ImageDisplay(BaseComponent):
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
        super().__init__(rect, manager)
        self.image_path = image_path
        self.surface = surface
        self.config = config or {}
        
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
                manager=self.manager
            )
        elif self.image_path:
            try:
                surface = pygame.image.load(self.image_path)
                self.image = pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect(0, 0, self.rect.width, self.rect.height),
                    image_surface=surface,
                    manager=self.manager
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
                manager=self.manager
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


class ProgressBar(BaseComponent):
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
        super().__init__(rect, manager)
        self.current = current
        self.maximum = maximum
        self.config = config or {}
        
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
            manager=self.manager
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


class MoneyDisplay(BaseComponent):
    """Specialized component for displaying money with formatting."""
    
    def __init__(self, rect: pygame.Rect, amount: int = 0, manager=None, container=None, config: Optional[Dict] = None):
        """Initialize money display component.
        
        Args:
            rect: Component position and size
            amount: Money amount to display
            manager: pygame_gui UIManager
            container: pygame_gui container (optional)
            config: Configuration options
        """
        super().__init__(rect, manager)
        self.amount = amount
        self.container = container
        self.config = config or {}
        
        # Style options
        self.font_size = self.config.get('font_size', 20)
        self.text_color = self.config.get('text_color', (0, 0, 0))
        self.prefix = self.config.get('prefix', '$')
        self.show_prefix = self.config.get('show_prefix', True)
        
        self.label: Optional[pygame_gui.elements.UILabel] = None
        self.font = pygame.font.Font(None, self.font_size)
        
        if self.manager:
            self._create_label()
            
    def _create_label(self) -> None:
        """Create the money label."""
        self.label = pygame_gui.elements.UILabel(
            relative_rect=self.rect,  # Use the component's rect directly
            text=self._format_amount(),
            manager=self.manager,
            container=self.container
        )
        
    def _format_amount(self) -> str:
        """Format amount with currency."""
        return f"{self.prefix}{self.amount:,}"
        
    def render(self, surface: pygame.Surface) -> None:
        """Render money display."""
        if self.label:
            # Handled by pygame_gui
            pass
        else:
            # Custom rendering
            abs_rect = self.get_absolute_rect()
            text = self._format_amount()
            text_surface = self.font.render(text, True, self.text_color)
            text_rect = text_surface.get_rect()
            text_rect.center = abs_rect.center
            surface.blit(text_surface, text_rect)
            
    def set_amount(self, amount: int) -> None:
        """Update money amount."""
        self.amount = amount
        if self.label:
            self.label.set_text(self._format_amount())
            
    def get_amount(self) -> int:
        """Get current amount."""
        return self.amount
        
    def add_amount(self, amount: int) -> None:
        """Add to current amount."""
        self.set_amount(self.amount + amount)
