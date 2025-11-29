"""
Slider component for numeric value selection.
"""

import pygame
import pygame_gui
from typing import Optional, Dict, Any, Callable
from .base_input import BaseInputComponent


class Slider(BaseInputComponent):
    """Slider component for numeric value selection."""
    
    def __init__(self, rect: pygame.Rect, min_value: float, max_value: float, 
                 action: str, manager=None, container=None, config=None):
        """Initialize slider component.
        
        Args:
            rect: Component position and size
            min_value: Minimum slider value
            max_value: Maximum slider value
            action: Action identifier
            manager: pygame_gui UIManager
            container: pygame_gui container (optional)
            config: Configuration options
        """
        super().__init__(rect, action, manager, container, config)
        
        # Slider-specific properties
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = (min_value + max_value) / 2  # Default to middle
        self.step_size = self.config.get('step_size', 1.0)
        self.show_value = self.config.get('show_value', True)
        
        # Callbacks
        self.on_value_change: Optional[Callable[[float], None]] = None
        
        # Additional UI elements
        self.value_label: Optional[pygame_gui.elements.UILabel] = None
        
        if self.manager:
            self._create_slider()
            
    def _create_slider(self) -> None:
        """Create the pygame_gui slider."""
        # Calculate initial value as percentage
        value_range = self.max_value - self.min_value
        if value_range > 0:
            start_value = ((self.current_value - self.min_value) / value_range) * 100
        else:
            start_value = 50
            
        self.ui_element = pygame_gui.elements.UIHorizontalSlider(
            start_value=start_value,
            value_range=(0, 100),  # Use 0-100 for internal representation
            relative_rect=self.rect,
            manager=self.manager,
            container=self.container
        )
        
        # Store reference for backward compatibility
        self.slider = self.ui_element
        
        # Create value label if enabled
        if self.show_value:
            label_rect = pygame.Rect(
                self.rect.x + self.rect.width + 10,
                self.rect.y,
                60,
                self.rect.height
            )
            self.value_label = pygame_gui.elements.UILabel(
                relative_rect=label_rect,
                text=f"{self.current_value:.1f}",
                manager=self.manager,
                container=self.container
            )
            
    def _handle_component_event(self, event: pygame.event.Event) -> bool:
        """Handle slider value change events."""
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.ui_element:
                # Convert from 0-100 to actual value range
                value_range = self.max_value - self.min_value
                if value_range > 0:
                    new_value = self.min_value + (event.value / 100.0) * value_range
                else:
                    new_value = self.min_value
                    
                # Apply step size if specified
                if self.step_size > 0:
                    new_value = round(new_value / self.step_size) * self.step_size
                    
                # Update current value
                self.current_value = new_value
                
                # Update value label
                if self.value_label:
                    self.value_label.set_text(f"{self.current_value:.1f}")
                    
                # Call value change callback
                if self.on_value_change:
                    self.on_value_change(self.current_value)
                    
                # Emit value change event
                self._emit_action_event({
                    'value': self.current_value
                })
                
                return True
        return False
        
    def set_value(self, value: float) -> None:
        """Set slider value programmatically."""
        # Clamp to range
        value = max(self.min_value, min(self.max_value, value))
        self.current_value = value
        
        if self.ui_element:
            # Convert to 0-100 range for pygame_gui
            value_range = self.max_value - self.min_value
            if value_range > 0:
                slider_value = ((value - self.min_value) / value_range) * 100
            else:
                slider_value = 50
                
            self.ui_element.set_current_value(slider_value)
            
        # Update value label
        if self.value_label:
            self.value_label.set_text(f"{self.current_value:.1f}")
            
    def get_value(self) -> float:
        """Get current slider value."""
        return self.current_value
        
    def set_range(self, min_value: float, max_value: float) -> None:
        """Update slider value range."""
        self.min_value = min_value
        self.max_value = max_value
        
        # Adjust current value if needed
        self.set_value(self.current_value)
        
    def set_value_change_callback(self, callback: Callable[[float], None]) -> None:
        """Set value change callback."""
        self.on_value_change = callback
        
    def destroy(self) -> None:
        """Clean up component resources."""
        if self.value_label and hasattr(self.value_label, 'kill'):
            self.value_label.kill()
        super().destroy()
