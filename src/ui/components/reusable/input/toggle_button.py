"""
ToggleButton component with on/off states.
"""

import pygame
import pygame_gui
from typing import Optional, Dict, Any, Callable
from .button import Button


class ToggleButton(Button):
    """Button with toggle functionality (on/off states)."""
    
    def __init__(self, rect: pygame.Rect, text: str, action: str, 
                 manager=None, config: Optional[Dict] = None):
        """Initialize toggle button.
        
        Args:
            rect: Component position and size
            text: Button text
            action: Action identifier
            manager: pygame_gui UIManager
            config: Configuration options
        """
        super().__init__(rect, text, action, manager, config)
        
        # Toggle state
        self.is_toggled = False
        self.on_text = config.get('on_text', text) if config else text
        self.off_text = config.get('off_text', text) if config else text
        self.on_style = config.get('on_style', 'success') if config else 'success'
        self.off_style = config.get('off_style', self.style) if config else self.style
        
        # Toggle callback
        self.on_toggle: Optional[Callable[[bool], None]] = None
        
        # Update initial appearance
        self._update_appearance()
        
    def _handle_component_event(self, event: pygame.event.Event) -> bool:
        """Handle toggle button events."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.button:
                # Toggle state
                self.is_toggled = not self.is_toggled
                
                # Update appearance
                self._update_appearance()
                
                # Call toggle callback
                if self.on_toggle:
                    self.on_toggle(self.is_toggled)
                    
                # Emit toggle event
                self._emit_event('toggle', {
                    'action': self.action,
                    'toggled': self.is_toggled
                })
                
                # Call regular action callback
                if self.on_action:
                    self.on_action(self.action)
                    
                self._emit_event('button_press', {'action': self.action})
                return True
        return False
        
    def _update_appearance(self) -> None:
        """Update button appearance based on toggle state."""
        if self.button:
            # Update text
            current_text = self.on_text if self.is_toggled else self.off_text
            self.button.set_text(current_text)
            
            # Update style (in a full implementation, we'd apply different colors)
            # For now, the text change is sufficient
            
    def set_toggled(self, toggled: bool) -> None:
        """Set toggle state programmatically."""
        if self.is_toggled != toggled:
            self.is_toggled = toggled
            self._update_appearance()
            
    def set_toggle_callback(self, callback: Callable[[bool], None]) -> None:
        """Set toggle state change callback."""
        self.on_toggle = callback
        
    def set_texts(self, on_text: str, off_text: str) -> None:
        """Set on/off texts."""
        self.on_text = on_text
        self.off_text = off_text
        self._update_appearance()
