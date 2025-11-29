"""
Dropdown component for selection from a list of options.
"""

import pygame
import pygame_gui
from typing import Optional, Dict, Any, Callable, List
from ...base_component import BaseComponent


class Dropdown(BaseComponent):
    """Dropdown selection component."""
    
    def __init__(self, rect: pygame.Rect, options: List[str], action: str,
                 manager=None, container=None, config=None):
        """Initialize dropdown component.
        
        Args:
            rect: Component position and size
            options: List of option strings
            action: Action identifier
            manager: pygame_gui UIManager
            container: pygame_gui container (optional)
            config: Configuration options
        """
        super().__init__(rect, manager)
        self.options = options
        self.action = action
        self.config = config or {}
        self.container = container
        
        # Dropdown state
        self.selected_index = 0
        self.on_selection_change: Optional[Callable[[int, str], None]] = None
        
        # Style options
        self.placeholder = self.config.get('placeholder', 'Select an option...')
        
        self.dropdown: Optional[pygame_gui.elements.UIDropDownMenu] = None
        self.on_action: Optional[Callable[[str], None]] = None
        
        if self.manager and self.options:
            self._create_dropdown()
            
    def _create_dropdown(self) -> None:
        """Create the pygame_gui dropdown."""
        self.dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=self.options,
            starting_option=self.options[self.selected_index] if self.selected_index < len(self.options) else self.options[0],
            relative_rect=self.rect,
            manager=self.manager,
            container=self.container
        )
        
    def render(self, surface: pygame.Surface) -> None:
        """Render dropdown (handled by pygame_gui)."""
        # Dropdown is rendered by pygame_gui automatically
        pass
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events."""
        return self._handle_component_event(event)
        
    def _handle_component_event(self, event: pygame.event.Event) -> bool:
        """Handle dropdown selection events."""
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.dropdown:
                # Get selected text
                selected_text = event.text
                
                # Find index
                try:
                    self.selected_index = self.options.index(selected_text)
                except ValueError:
                    self.selected_index = 0
                    
                # Call selection change callback
                if self.on_selection_change:
                    self.on_selection_change(self.selected_index, selected_text)
                    
                # Emit selection event
                self._emit_event('dropdown_changed', {
                    'action': self.action,
                    'index': self.selected_index,
                    'value': selected_text
                })
                
                # Call action callback
                if self.on_action:
                    self.on_action(self.action)
                    
                return True
        return False
        
    def set_options(self, options: List[str]) -> None:
        """Update dropdown options."""
        self.options = options
        if self.dropdown:
            # Recreate dropdown with new options
            if hasattr(self.dropdown, 'kill'):
                self.dropdown.kill()
            self._create_dropdown()
            
    def set_selected_index(self, index: int) -> None:
        """Set selected option by index."""
        if 0 <= index < len(self.options):
            self.selected_index = index
            if self.dropdown:
                self.dropdown.selected_option = self.options[index]
                
    def set_selected_value(self, value: str) -> None:
        """Set selected option by value."""
        if value in self.options:
            self.set_selected_index(self.options.index(value))
            
    def get_selected_value(self) -> str:
        """Get currently selected value."""
        if 0 <= self.selected_index < len(self.options):
            return self.options[self.selected_index]
        return ""
        
    def get_selected_index(self) -> int:
        """Get currently selected index."""
        return self.selected_index
        
    def set_selection_callback(self, callback: Callable[[int, str], None]) -> None:
        """Set selection change callback."""
        self.on_selection_change = callback
        
    def set_action_callback(self, callback: Callable[[str], None]) -> None:
        """Set action callback."""
        self.on_action = callback
