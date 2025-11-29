"""
Reusable input components that can be used across all UI panels.
"""

import pygame
import pygame_gui
from typing import Optional, Dict, Any, Callable, List, Union
from ..base_component import BaseComponent


class Button(BaseComponent):
    """Reusable button component with styling options."""
    
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
        super().__init__(rect, manager)
        self.text = text
        self.action = action
        self.config = config or {}
        self.container = container
        
        # Style options
        self.style = self.config.get('style', 'primary')  # primary, secondary, danger
        self.size = self.config.get('size', 'medium')  # small, medium, large
        self.icon = self.config.get('icon', None)
        self.tooltip = self.config.get('tooltip', '')
        
        # Auto-sizing options
        self.auto_resize = self.config.get('auto_resize', True)
        self.min_width = self.config.get('min_width', rect.width)
        self.padding = self.config.get('padding', 20)  # Horizontal padding for text
        
        self.button: Optional[pygame_gui.elements.UIButton] = None
        self.on_action: Optional[Callable[[str], None]] = None
        
        if self.manager:
            self._create_button()
            
    def _create_button(self) -> None:
        """Create the pygame_gui button with auto-sizing."""
        # Calculate optimal size if auto_resize is enabled
        button_rect = self.rect
        if self.auto_resize:
            button_rect = self._calculate_optimal_rect()
            
        self.button = pygame_gui.elements.UIButton(
            relative_rect=button_rect,
            text=self.text,
            manager=self.manager,
            container=self.container
        )
        
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
        
    def render(self, surface: pygame.Surface) -> None:
        """Render button (handled by pygame_gui)."""
        # Button is rendered by pygame_gui automatically
        pass
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events."""
        return self._handle_component_event(event)
        
    def _handle_component_event(self, event: pygame.event.Event) -> bool:
        """Handle button press events."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.button:
                if self.on_action:
                    self.on_action(self.action)
                self._emit_event('button_press', {'action': self.action})
                return True
        return False
        
    def set_text(self, text: str) -> None:
        """Update button text and resize if needed."""
        self.text = text
        if self.button:
            # Update text first
            self.button.set_text(text)
            
            # Recreate button with new size if auto-resizing
            if self.auto_resize:
                self._recreate_button_with_new_size()
                
    def _recreate_button_with_new_size(self) -> None:
        """Recreate the button with optimal size for current text."""
        if not self.button:
            return
            
        # Store current state
        was_enabled = self.button.is_enabled
        old_rect = self.button.rect
        
        # Calculate new optimal size
        new_rect = self._calculate_optimal_rect()
        
        # Kill old button
        if hasattr(self.button, 'kill'):
            self.button.kill()
            
        # Create new button with optimal size
        self.button = pygame_gui.elements.UIButton(
            relative_rect=new_rect,
            text=self.text,
            manager=self.manager,
            container=self.container
        )
        
        # Restore enabled state
        if not was_enabled:
            self.button.disable()
            
    def set_enabled(self, enabled: bool) -> None:
        """Set button enabled state."""
        super().set_enabled(enabled)
        if self.button:
            if enabled:
                self.button.enable()
            else:
                self.button.disable()
                
    def set_action_callback(self, callback: Callable[[str], None]) -> None:
        """Set action callback."""
        self.on_action = callback


class IconButton(Button):
    """Button with icon support."""
    
    def __init__(self, rect: pygame.Rect, icon: str = "", action: str = "",
                 manager=None, config: Optional[Dict] = None):
        """Initialize icon button.
        
        Args:
            rect: Component position and size
            icon: Icon identifier or path
            action: Action identifier
            manager: pygame_gui UIManager
            config: Configuration options
        """
        super().__init__(rect, "", action, manager, config)
        self.icon = icon
        self.icon_size = self.config.get('icon_size', 16)
        
        # Update text to include icon if needed
        if self.icon and self.button:
            self._update_button_text()
            
    def _update_button_text(self) -> None:
        """Update button text with icon."""
        # Simple icon implementation - could be enhanced with proper icon fonts
        icon_text = f"[{self.icon}] {self.text}" if self.text else f"[{self.icon}]"
        if self.button:
            self.button.set_text(icon_text)


class ToggleButton(Button):
    """Button with toggle states."""
    
    def __init__(self, rect: pygame.Rect, text: str = "", action: str = "",
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
        self.is_toggled = False
        self.toggle_text_on = self.config.get('toggle_text_on', text)
        self.toggle_text_off = self.config.get('toggle_text_off', text)
        
    def _handle_component_event(self, event: pygame.event.Event) -> bool:
        """Handle toggle events."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.button:
                self.toggle()
                if self.on_action:
                    self.on_action(self.action)
                self._emit_event('toggle', {'action': self.action, 'toggled': self.is_toggled})
                return True
        return False
        
    def toggle(self) -> None:
        """Toggle button state."""
        self.is_toggled = not self.is_toggled
        self._update_text()
        
    def set_toggled(self, toggled: bool) -> None:
        """Set toggle state."""
        self.is_toggled = toggled
        self._update_text()
        
    def _update_text(self) -> None:
        """Update text based on toggle state."""
        text = self.toggle_text_on if self.is_toggled else self.toggle_text_off
        self.set_text(text)


class Dropdown(BaseComponent):
    """Reusable dropdown component."""
    
    def __init__(self, rect: pygame.Rect, options: List[str] = None, 
                 selected: str = "", manager=None, config: Optional[Dict] = None):
        """Initialize dropdown component.
        
        Args:
            rect: Component position and size
            options: List of options
            selected: Currently selected option
            manager: pygame_gui UIManager
            config: Configuration options
        """
        super().__init__(rect, manager)
        self.options = options or []
        self.selected = selected
        self.config = config or {}
        
        # Style options
        self.placeholder = self.config.get('placeholder', 'Select...')
        self.searchable = self.config.get('searchable', False)
        
        self.dropdown: Optional[pygame_gui.elements.UIDropDownMenu] = None
        self.on_selection_changed: Optional[Callable[[str], None]] = None
        
        if self.manager:
            self._create_dropdown()
            
    def _create_dropdown(self) -> None:
        """Create the pygame_gui dropdown."""
        if not self.options:
            self.options = [self.placeholder]
            
        starting_option = self.selected if self.selected in self.options else self.options[0]
        
        self.dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=self.options,
            starting_option=starting_option,
            relative_rect=pygame.Rect(0, 0, self.rect.width, self.rect.height),
            manager=self.manager
        )
        
    def render(self, surface: pygame.Surface) -> None:
        """Render dropdown (handled by pygame_gui)."""
        # Dropdown is rendered by pygame_gui automatically
        pass
        
    def _handle_component_event(self, event: pygame.event.Event) -> bool:
        """Handle dropdown selection events."""
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.dropdown:
                self.selected = event.text
                if self.on_selection_changed:
                    self.on_selection_changed(self.selected)
                self._emit_event('selection_changed', {'selected': self.selected})
                return True
        return False
        
    def set_options(self, options: List[str]) -> None:
        """Update dropdown options."""
        self.options = options
        # Note: pygame_gui dropdown doesn't support dynamic option updates
        # Would need to recreate the dropdown
        
    def set_selected(self, selected: str) -> None:
        """Update selected option."""
        self.selected = selected
        if self.dropdown and selected in self.options:
            self.dropdown.selected_option = selected
            
    def get_selected(self) -> str:
        """Get selected option."""
        return self.selected


class Slider(BaseComponent):
    """Reusable slider component."""
    
    def __init__(self, rect: pygame.Rect, min_value: float = 0, max_value: float = 100,
                 current_value: float = 50, manager=None, config: Optional[Dict] = None):
        """Initialize slider component.
        
        Args:
            rect: Component position and size
            min_value: Minimum slider value
            max_value: Maximum slider value
            current_value: Current slider value
            manager: pygame_gui UIManager
            config: Configuration options
        """
        super().__init__(rect, manager)
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = current_value
        self.config = config or {}
        
        # Style options
        self.orientation = self.config.get('orientation', 'horizontal')
        self.show_value = self.config.get('show_value', True)
        self.step = self.config.get('step', 1)
        
        self.slider: Optional[pygame_gui.elements.UIHorizontalSlider] = None
        self.value_label: Optional[pygame_gui.elements.UILabel] = None
        self.on_value_changed: Optional[Callable[[float], None]] = None
        
        if self.manager:
            self._create_slider()
            
    def _create_slider(self) -> None:
        """Create the pygame_gui slider."""
        slider_height = 20 if self.show_value else self.rect.height
        
        self.slider = pygame_gui.elements.UIHorizontalSlider(
            start_value=self.current_value,
            value_range=(self.min_value, self.max_value),
            relative_rect=pygame.Rect(0, 0, self.rect.width, slider_height),
            manager=self.manager
        )
        
        if self.show_value:
            self.value_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(0, slider_height + 5, self.rect.width, 20),
                text=str(int(self.current_value)),
                manager=self.manager
            )
            
    def render(self, surface: pygame.Surface) -> None:
        """Render slider (handled by pygame_gui)."""
        # Slider is rendered by pygame_gui automatically
        pass
        
    def _handle_component_event(self, event: pygame.event.Event) -> bool:
        """Handle slider value changes."""
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.slider:
                self.current_value = event.value
                self._update_value_label()
                if self.on_value_changed:
                    self.on_value_changed(self.current_value)
                self._emit_event('value_changed', {'value': self.current_value})
                return True
        return False
        
    def _update_value_label(self) -> None:
        """Update value label display."""
        if self.value_label:
            self.value_label.set_text(str(int(self.current_value)))
            
    def set_value(self, value: float) -> None:
        """Set slider value."""
        self.current_value = max(self.min_value, min(self.max_value, value))
        if self.slider:
            self.slider.set_current_progress(self.current_value)
        self._update_value_label()
        
    def get_value(self) -> float:
        """Get current slider value."""
        return self.current_value


class TextInput(BaseComponent):
    """Reusable text input component."""
    
    def __init__(self, rect: pygame.Rect, text: str = "", manager=None, config: Optional[Dict] = None):
        """Initialize text input component.
        
        Args:
            rect: Component position and size
            text: Initial text
            manager: pygame_gui UIManager
            config: Configuration options
        """
        super().__init__(rect, manager)
        self.text = text
        self.config = config or {}
        
        # Style options
        self.placeholder = self.config.get('placeholder', 'Enter text...')
        self.max_length = self.config.get('max_length', None)
        self.password_mode = self.config.get('password_mode', False)
        
        self.text_input: Optional[pygame_gui.elements.UITextEntryLine] = None
        self.on_text_changed: Optional[Callable[[str], None]] = None
        
        if self.manager:
            self._create_text_input()
            
    def _create_text_input(self) -> None:
        """Create the pygame_gui text input."""
        self.text_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(0, 0, self.rect.width, self.rect.height),
            manager=self.manager
        )
        if self.text:
            self.text_input.set_text(self.text)
            
    def render(self, surface: pygame.Surface) -> None:
        """Render text input (handled by pygame_gui)."""
        # Text input is rendered by pygame_gui automatically
        pass
        
    def _handle_component_event(self, event: pygame.event.Event) -> bool:
        """Handle text input events."""
        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == self.text_input:
                self.text = event.text
                if self.on_text_changed:
                    self.on_text_changed(self.text)
                self._emit_event('text_changed', {'text': self.text})
                return True
        elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            if event.ui_element == self.text_input:
                self.text = event.text
                if self.on_text_changed:
                    self.on_text_changed(self.text)
                return True
        return False
        
    def set_text(self, text: str) -> None:
        """Set text input value."""
        self.text = text
        if self.text_input:
            self.text_input.set_text(text)
            
    def get_text(self) -> str:
        """Get current text."""
        return self.text
        
    def set_placeholder(self, placeholder: str) -> None:
        """Set placeholder text."""
        self.placeholder = placeholder
        if self.text_input:
            self.text_input.set_placeholder_text(placeholder)
