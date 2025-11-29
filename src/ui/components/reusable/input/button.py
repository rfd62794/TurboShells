"""
Reusable Button component with auto-sizing and styling options.
"""

import pygame
import pygame_gui
from typing import Optional, Dict, Any, Callable
from .base_input import BaseInputComponent


class Button(BaseInputComponent):
    """Reusable button component with auto-sizing and styling options."""
    
    def __init__(self, rect: pygame.Rect, text: str, action: str, manager=None, container=None, config=None):
        """Initialize button component.
        
        Args:
            rect: Button position and size (will be auto-sized if too small)
            text: Button text
            action: Action identifier
            manager: pygame_gui UIManager
            container: pygame_gui container (optional)
            config: Configuration options
        """
        super().__init__(rect, action, manager, container, config)
        
        # Button-specific properties
        self.text = text
        
        # Style options
        self.style = self.config.get('style', 'primary')  # primary, secondary, danger
        self.size = self.config.get('size', 'medium')  # small, medium, large
        self.icon = self.config.get('icon', None)
        self.tooltip = self.config.get('tooltip', '')
        
        # Auto-sizing options (override base defaults for buttons)
        self.auto_resize = self.config.get('auto_resize', True)
        self.min_width = self.config.get('min_width', rect.width)
        self.padding = self.config.get('padding', 20)  # Horizontal padding for text
        
        if self.manager:
            self._create_button()
            
    def _create_button(self) -> None:
        """Create the pygame_gui button with auto-sizing."""
        # Calculate optimal size if auto_resize is enabled
        button_rect = self.rect
        if self.auto_resize:
            button_rect = self._calculate_optimal_rect()
            
        self.ui_element = pygame_gui.elements.UIButton(
            relative_rect=button_rect,
            text=self.text,
            manager=self.manager,
            container=self.container
        )
        
        # Store reference for backward compatibility
        self.button = self.ui_element
        
    def _calculate_optimal_rect(self) -> pygame.Rect:
        """Calculate the optimal button size based on text content."""
        if not self.manager:
            return self.rect
            
        # Create a temporary font to measure text
        try:
            # Try to get the theme's font
            ui_theme = self.manager.get_theme()
            font_size = 14  # Default font size
            font = pygame.font.Font(None, font_size * 2)  # Scale up for better measurement
        except:
            font = pygame.font.Font(None, 28)
            
        # Measure text dimensions
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_width = text_surface.get_width()
        text_height = text_surface.get_height()
        
        # Calculate optimal width with padding
        optimal_width = max(text_width + self.padding, self.min_width)
        optimal_height = max(text_height + 10, self.rect.height)  # Add vertical padding
        
        # Create new rect with same position but optimal size
        return pygame.Rect(self.rect.x, self.rect.y, optimal_width, optimal_height)
        
    def _handle_component_event(self, event: pygame.event.Event) -> bool:
        """Handle button press events."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.ui_element:
                self._emit_action_event()
                return True
        return False
        
    def set_text(self, text: str) -> None:
        """Update button text and resize if needed."""
        self.text = text
        if self.ui_element:
            # Update text first
            self.ui_element.set_text(text)
            
            # Recreate button with new size if auto-resizing
            if self.auto_resize:
                self._recreate_element_with_new_size()
                
    def _recreate_element_with_new_size(self) -> None:
        """Recreate the button with optimal size for current text."""
        if not self.ui_element:
            return
            
        # Store current state
        was_enabled = self.ui_element.is_enabled
        old_rect = self.ui_element.rect
        
        # Calculate new optimal size
        new_rect = self._calculate_optimal_rect()
        
        # Kill old button
        if hasattr(self.ui_element, 'kill'):
            self.ui_element.kill()
            
        # Create new button with optimal size
        self._create_button()
        
        # Restore enabled state
        if not was_enabled:
            self.ui_element.disable()
