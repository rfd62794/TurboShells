"""
TextInput component for text entry.
"""

import pygame
import pygame_gui
from typing import Optional, Dict, Any, Callable
from ...base_component import BaseComponent


class TextInput(BaseComponent):
    """Text input component for user text entry."""
    
    def __init__(self, rect: pygame.Rect, action: str, manager=None, 
                 container=None, config=None):
        """Initialize text input component.
        
        Args:
            rect: Component position and size
            action: Action identifier
            manager: pygame_gui UIManager
            container: pygame_gui container (optional)
            config: Configuration options
        """
        super().__init__(rect, manager)
        self.action = action
        self.config = config or {}
        self.container = container
        
        # Text input options
        self.placeholder = self.config.get('placeholder', 'Enter text...')
        self.max_length = self.config.get('max_length', -1)  # -1 = no limit
        self.password_mode = self.config.get('password_mode', False)
        self.initial_text = self.config.get('initial_text', '')
        
        # Callbacks
        self.on_text_change: Optional[Callable[[str], None]] = None
        self.on_text_submit: Optional[Callable[[str], None]] = None
        self.on_action: Optional[Callable[[str], None]] = None
        
        self.text_input: Optional[pygame_gui.elements.UITextEntryLine] = None
        
        if self.manager:
            self._create_text_input()
            
    def _create_text_input(self) -> None:
        """Create the pygame_gui text input."""
        self.text_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=self.rect,
            manager=self.manager,
            container=self.container,
            initial_text=self.initial_text
        )
        
        # Set placeholder if supported
        if hasattr(self.text_input, 'set_placeholder_text'):
            self.text_input.set_placeholder_text(self.placeholder)
            
        # Set max length if specified
        if self.max_length > 0 and hasattr(self.text_input, 'set_text_length_limit'):
            self.text_input.set_text_length_limit(self.max_length)
            
    def render(self, surface: pygame.Surface) -> None:
        """Render text input (handled by pygame_gui)."""
        # Text input is rendered by pygame_gui automatically
        pass
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events."""
        return self._handle_component_event(event)
        
    def _handle_component_event(self, event: pygame.event.Event) -> bool:
        """Handle text input events."""
        if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            if event.ui_element == self.text_input:
                current_text = event.text
                
                # Call text change callback
                if self.on_text_change:
                    self.on_text_change(current_text)
                    
                # Emit text change event
                self._emit_event('text_changed', {
                    'action': self.action,
                    'text': current_text
                })
                
                return True
                
        elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == self.text_input:
                final_text = event.text
                
                # Call text submit callback
                if self.on_text_submit:
                    self.on_text_submit(final_text)
                    
                # Emit text submit event
                self._emit_event('text_submit', {
                    'action': self.action,
                    'text': final_text
                })
                
                # Call action callback
                if self.on_action:
                    self.on_action(self.action)
                    
                return True
                
        elif event.type == pygame.KEYDOWN:
            # Handle Enter key for submission
            if event.key == pygame.K_RETURN and self.text_input:
                if self.text_input.is_focused:
                    current_text = self.text_input.get_text()
                    
                    # Call text submit callback
                    if self.on_text_submit:
                        self.on_text_submit(current_text)
                        
                    # Emit text submit event
                    self._emit_event('text_submit', {
                        'action': self.action,
                        'text': current_text
                    })
                    
                    # Call action callback
                    if self.on_action:
                        self.on_action(self.action)
                        
                    return True
                    
        return False
        
    def set_text(self, text: str) -> None:
        """Set text input value."""
        if self.text_input:
            self.text_input.set_text(text)
            
    def get_text(self) -> str:
        """Get current text input value."""
        if self.text_input:
            return self.text_input.get_text()
        return ""
        
    def clear(self) -> None:
        """Clear text input."""
        self.set_text("")
        
    def set_placeholder(self, placeholder: str) -> None:
        """Set placeholder text."""
        self.placeholder = placeholder
        if self.text_input and hasattr(self.text_input, 'set_placeholder_text'):
            self.text_input.set_placeholder_text(placeholder)
            
    def set_max_length(self, max_length: int) -> None:
        """Set maximum text length."""
        self.max_length = max_length
        if self.text_input and hasattr(self.text_input, 'set_text_length_limit'):
            if max_length > 0:
                self.text_input.set_text_length_limit(max_length)
            else:
                self.text_input.set_text_length_limit(-1)  # No limit
                
    def set_focus(self, focused: bool) -> None:
        """Set focus state."""
        if self.text_input:
            if focused:
                self.text_input.focus()
            else:
                self.text_input.unfocus()
                
    def is_focused(self) -> bool:
        """Check if text input has focus."""
        return self.text_input.is_focused if self.text_input else False
        
    def set_text_change_callback(self, callback: Callable[[str], None]) -> None:
        """Set text change callback."""
        self.on_text_change = callback
        
    def set_text_submit_callback(self, callback: Callable[[str], None]) -> None:
        """Set text submit callback."""
        self.on_text_submit = callback
        
    def set_action_callback(self, callback: Callable[[str], None]) -> None:
        """Set action callback."""
        self.on_action = callback
