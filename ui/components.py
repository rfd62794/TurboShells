"""
UI components library for TurboShells.

This module provides reusable UI components for the game interface,
including buttons, sliders, dropdowns, and other interactive elements.
"""

import pygame
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

from core.logging_config import get_logger


class ComponentState(Enum):
    """Component interaction states."""
    NORMAL = "normal"
    HOVER = "hover"
    PRESSED = "pressed"
    DISABLED = "disabled"
    FOCUSED = "focused"


@dataclass
class ComponentStyle:
    """Style configuration for UI components."""
    background_color: Tuple[int, int, int]
    border_color: Tuple[int, int, int]
    text_color: Tuple[int, int, int]
    hover_color: Tuple[int, int, int]
    pressed_color: Tuple[int, int, int]
    disabled_color: Tuple[int, int, int]
    border_width: int = 1
    corner_radius: int = 0


class UIComponent:
    """Base class for all UI components."""
    
    def __init__(self, rect: pygame.Rect, style: ComponentStyle = None):
        """
        Initialize UI component.
        
        Args:
            rect: Component rectangle
            style: Component style configuration
        """
        self.rect = rect
        self.style = style or self._get_default_style()
        self.state = ComponentState.NORMAL
        self.visible = True
        self.enabled = True
        self.tooltip = ""
        self.logger = get_logger(__name__)
        
        # Callbacks
        self.on_click: Optional[Callable] = None
        self.on_hover: Optional[Callable] = None
        self.on_change: Optional[Callable] = None
        
        # Internal state
        self._hover_time = 0
        self._pressed_time = 0
    
    def _get_default_style(self) -> ComponentStyle:
        """Get default component style."""
        return ComponentStyle(
            background_color=(80, 80, 80),
            border_color=(100, 100, 100),
            text_color=(255, 255, 255),
            hover_color=(100, 100, 100),
            pressed_color=(120, 120, 120),
            disabled_color=(60, 60, 60)
        )
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events.
        
        Args:
            event: Pygame event
            
        Returns:
            True if event was handled, False otherwise
        """
        if not self.visible or not self.enabled:
            return False
        
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(mouse_pos):
                if self.state != ComponentState.HOVER and self.state != ComponentState.PRESSED:
                    self.state = ComponentState.HOVER
                    self._hover_time = pygame.time.get_ticks()
                    if self.on_hover:
                        self.on_hover(self)
                return True
            else:
                if self.state == ComponentState.HOVER:
                    self.state = ComponentState.NORMAL
                return False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(mouse_pos):
                self.state = ComponentState.PRESSED
                self._pressed_time = pygame.time.get_ticks()
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.state == ComponentState.PRESSED:
                self.state = ComponentState.HOVER
                if self.on_click:
                    self.on_click(self)
                return True
        
        return False
    
    def update(self, dt: float) -> None:
        """
        Update component state.
        
        Args:
            dt: Time delta since last update
        """
        # Update animations, tooltips, etc.
        pass
    
    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the component.
        
        Args:
            screen: Surface to draw on
        """
        if not self.visible:
            return
    
    def get_color_for_state(self) -> Tuple[int, int, int]:
        """Get appropriate color based on component state."""
        if not self.enabled:
            return self.style.disabled_color
        elif self.state == ComponentState.PRESSED:
            return self.style.pressed_color
        elif self.state == ComponentState.HOVER:
            return self.style.hover_color
        else:
            return self.style.background_color


class Button(UIComponent):
    """Interactive button component."""
    
    def __init__(self, rect: pygame.Rect, text: str, style: ComponentStyle = None):
        """
        Initialize button.
        
        Args:
            rect: Button rectangle
            text: Button text
            style: Button style
        """
        super().__init__(rect, style)
        self.text = text
        self.font = pygame.font.Font(None, 16)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the button."""
        if not self.visible:
            return
        
        # Draw button background
        color = self.get_color_for_state()
        if self.style.corner_radius > 0:
            pygame.draw.rect(screen, color, self.rect, border_radius=self.style.corner_radius)
            pygame.draw.rect(screen, self.style.border_color, self.rect, 
                           self.style.border_width, border_radius=self.style.corner_radius)
        else:
            pygame.draw.rect(screen, color, self.rect)
            pygame.draw.rect(screen, self.style.border_color, self.rect, self.style.border_width)
        
        # Draw text
        text_color = self.style.text_color if self.enabled else (150, 150, 150)
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class Checkbox(UIComponent):
    """Checkbox component for boolean values."""
    
    def __init__(self, rect: pygame.Rect, checked: bool = False, style: ComponentStyle = None):
        """
        Initialize checkbox.
        
        Args:
            rect: Checkbox rectangle
            checked: Initial checked state
            style: Checkbox style
        """
        super().__init__(rect, style)
        self.checked = checked
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle checkbox events."""
        handled = super().handle_event(event)
        
        if handled and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.checked = not self.checked
            if self.on_change:
                self.on_change(self)
        
        return handled
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the checkbox."""
        if not self.visible:
            return
        
        # Draw checkbox background
        color = self.get_color_for_state()
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, self.style.border_color, self.rect, self.style.border_width)
        
        # Draw checkmark if checked
        if self.checked:
            check_color = self.style.text_color if self.enabled else (150, 150, 150)
            check_points = [
                (self.rect.left + 3, self.rect.centery),
                (self.rect.left + 8, self.rect.bottom - 3),
                (self.rect.right - 3, self.rect.top + 3)
            ]
            pygame.draw.lines(screen, check_color, False, check_points, 2)


class Slider(UIComponent):
    """Slider component for numeric values."""
    
    def __init__(self, rect: pygame.Rect, min_value: float = 0.0, max_value: float = 1.0, 
                 initial_value: float = 0.5, style: ComponentStyle = None):
        """
        Initialize slider.
        
        Args:
            rect: Slider rectangle
            min_value: Minimum slider value
            max_value: Maximum slider value
            initial_value: Initial slider value
            style: Slider style
        """
        super().__init__(rect, style)
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.dragging = False
        self.font = pygame.font.Font(None, 14)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle slider events."""
        if not self.visible or not self.enabled:
            return False
        
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(mouse_pos):
                self.dragging = True
                self.state = ComponentState.PRESSED
                self._update_value_from_mouse(mouse_pos)
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging:
                self.dragging = False
                self.state = ComponentState.HOVER
                if self.on_change:
                    self.on_change(self)
                return True
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self._update_value_from_mouse(mouse_pos)
                return True
            else:
                return super().handle_event(event)
        
        return False
    
    def _update_value_from_mouse(self, mouse_pos: Tuple[int, int]) -> None:
        """Update slider value based on mouse position."""
        relative_x = mouse_pos[0] - self.rect.x
        relative_x = max(0, min(self.rect.width, relative_x))
        
        self.value = self.min_value + (relative_x / self.rect.width) * (self.max_value - self.min_value)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the slider."""
        if not self.visible:
            return
        
        # Draw track
        track_rect = pygame.Rect(self.rect.x, self.rect.centery - 2, self.rect.width, 4)
        track_color = self.style.border_color if self.enabled else (60, 60, 60)
        pygame.draw.rect(screen, track_color, track_rect)
        
        # Draw handle
        handle_x = self.rect.x + int((self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width)
        handle_rect = pygame.Rect(handle_x - 8, self.rect.centery - 8, 16, 16)
        
        handle_color = self.get_color_for_state()
        pygame.draw.rect(screen, handle_color, handle_rect)
        pygame.draw.rect(screen, self.style.border_color, handle_rect, self.style.border_width)
        
        # Draw value text
        value_text = f"{int(self.value * 100)}%" if self.max_value == 1.0 else f"{self.value:.1f}"
        text_color = self.style.text_color if self.enabled else (150, 150, 150)
        text_surface = self.font.render(value_text, True, text_color)
        text_rect = text_surface.get_rect(
            left=self.rect.right + 10,
            centery=self.rect.centery
        )
        screen.blit(text_surface, text_rect)


class Dropdown(UIComponent):
    """Dropdown component for selecting from multiple options."""
    
    def __init__(self, rect: pygame.Rect, options: List[str], selected_index: int = 0, 
                 style: ComponentStyle = None):
        """
        Initialize dropdown.
        
        Args:
            rect: Dropdown rectangle
            options: List of option strings
            selected_index: Initially selected option index
            style: Dropdown style
        """
        super().__init__(rect, style)
        self.options = options
        self.selected_index = selected_index
        self.expanded = False
        self.font = pygame.font.Font(None, 14)
        
        # Calculate dropdown item height
        self.item_height = 25
        self.max_display_items = 5
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle dropdown events."""
        if not self.visible or not self.enabled:
            return False
        
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(mouse_pos):
                    self.expanded = not self.expanded
                    return True
                elif self.expanded:
                    # Check if clicking on an option
                    expanded_rect = self._get_expanded_rect()
                    if expanded_rect.collidepoint(mouse_pos):
                        item_index = (mouse_pos[1] - expanded_rect.y) // self.item_height
                        if 0 <= item_index < len(self.options):
                            self.selected_index = item_index
                            self.expanded = False
                            if self.on_change:
                                self.on_change(self)
                            return True
                    else:
                        self.expanded = False
                        return True
        
        return False
    
    def _get_expanded_rect(self) -> pygame.Rect:
        """Get the rectangle for the expanded dropdown."""
        display_count = min(len(self.options), self.max_display_items)
        height = display_count * self.item_height
        return pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, height)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the dropdown."""
        if not self.visible:
            return
        
        # Draw main dropdown box
        color = self.get_color_for_state()
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, self.style.border_color, self.rect, self.style.border_width)
        
        # Draw selected option
        selected_text = self.options[self.selected_index] if self.selected_index < len(self.options) else ""
        text_color = self.style.text_color if self.enabled else (150, 150, 150)
        text_surface = self.font.render(selected_text, True, text_color)
        text_rect = text_surface.get_rect(
            left=self.rect.left + 5,
            centery=self.rect.centery
        )
        screen.blit(text_surface, text_rect)
        
        # Draw dropdown arrow
        arrow_color = self.style.text_color if self.enabled else (150, 150, 150)
        if self.expanded:
            arrow_points = [
                (self.rect.right - 15, self.rect.centery + 5),
                (self.rect.right - 5, self.rect.centery + 5),
                (self.rect.right - 10, self.rect.centery - 5)
            ]
        else:
            arrow_points = [
                (self.rect.right - 15, self.rect.centery - 5),
                (self.rect.right - 5, self.rect.centery - 5),
                (self.rect.right - 10, self.rect.centery + 5)
            ]
        pygame.draw.polygon(screen, arrow_color, arrow_points)
        
        # Draw expanded options
        if self.expanded:
            expanded_rect = self._get_expanded_rect()
            pygame.draw.rect(screen, self.style.background_color, expanded_rect)
            pygame.draw.rect(screen, self.style.border_color, expanded_rect, self.style.border_width)
            
            # Draw options
            for i, option in enumerate(self.options[:self.max_display_items]):
                option_rect = pygame.Rect(
                    expanded_rect.x,
                    expanded_rect.y + i * self.item_height,
                    expanded_rect.width,
                    self.item_height
                )
                
                # Highlight selected option
                if i == self.selected_index:
                    pygame.draw.rect(screen, self.style.hover_color, option_rect)
                
                # Draw option text
                option_surface = self.font.render(option, True, text_color)
                option_text_rect = option_surface.get_rect(
                    left=option_rect.left + 5,
                    centery=option_rect.centery
                )
                screen.blit(option_surface, option_text_rect)


class Label(UIComponent):
    """Simple text label component."""
    
    def __init__(self, rect: pygame.Rect, text: str, font_size: int = 14, 
                 text_color: Tuple[int, int, int] = (255, 255, 255)):
        """
        Initialize label.
        
        Args:
            rect: Label rectangle
            text: Label text
            font_size: Font size
            text_color: Text color
        """
        super().__init__(rect)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.text_color = text_color
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the label."""
        if not self.visible:
            return
        
        color = self.text_color if self.enabled else (150, 150, 150)
        text_surface = self.font.render(self.text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class Panel(UIComponent):
    """Container panel for grouping other components."""
    
    def __init__(self, rect: pygame.Rect, style: ComponentStyle = None):
        """
        Initialize panel.
        
        Args:
            rect: Panel rectangle
            style: Panel style
        """
        super().__init__(rect, style)
        self.children: List[UIComponent] = []
    
    def add_child(self, child: UIComponent) -> None:
        """Add a child component."""
        self.children.append(child)
    
    def remove_child(self, child: UIComponent) -> None:
        """Remove a child component."""
        if child in self.children:
            self.children.remove(child)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for all children."""
        handled = False
        for child in self.children:
            if child.handle_event(event):
                handled = True
        return handled
    
    def update(self, dt: float) -> None:
        """Update all children."""
        super().update(dt)
        for child in self.children:
            child.update(dt)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the panel and all children."""
        if not self.visible:
            return
        
        # Draw panel background
        color = self.get_color_for_state()
        if self.style.corner_radius > 0:
            pygame.draw.rect(screen, color, self.rect, border_radius=self.style.corner_radius)
            pygame.draw.rect(screen, self.style.border_color, self.rect, 
                           self.style.border_width, border_radius=self.style.corner_radius)
        else:
            pygame.draw.rect(screen, color, self.rect)
            pygame.draw.rect(screen, self.style.border_color, self.rect, self.style.border_width)
        
        # Draw children
        for child in self.children:
            child.draw(screen)


class TooltipManager:
    """Manager for displaying tooltips."""
    
    def __init__(self):
        """Initialize tooltip manager."""
        self.font = pygame.font.Font(None, 12)
        self.tooltip_text = ""
        self.tooltip_rect = pygame.Rect(0, 0, 0, 0)
        self.visible = False
        self.show_delay = 500  # milliseconds
        self.hover_start_time = 0
    
    def show_tooltip(self, text: str, pos: Tuple[int, int]) -> None:
        """Show a tooltip at the specified position."""
        self.tooltip_text = text
        self.hover_start_time = pygame.time.get_ticks()
        self.visible = True
        
        # Calculate tooltip size
        text_surface = self.font.render(text, True, (255, 255, 255))
        padding = 6
        self.tooltip_rect = pygame.Rect(
            pos[0] + 10,
            pos[1] - 20,
            text_surface.get_width() + padding * 2,
            text_surface.get_height() + padding * 2
        )
    
    def hide_tooltip(self) -> None:
        """Hide the tooltip."""
        self.visible = False
        self.tooltip_text = ""
    
    def update(self, mouse_pos: Tuple[int, int]) -> None:
        """Update tooltip visibility based on hover time."""
        if self.visible and pygame.time.get_ticks() - self.hover_start_time < self.show_delay:
            self.visible = False
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the tooltip if visible."""
        if not self.visible or pygame.time.get_ticks() - self.hover_start_time < self.show_delay:
            return
        
        # Draw tooltip background
        pygame.draw.rect(screen, (40, 40, 40), self.tooltip_rect)
        pygame.draw.rect(screen, (100, 100, 100), self.tooltip_rect, 1)
        
        # Draw tooltip text
        text_surface = self.font.render(self.tooltip_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.tooltip_rect.center)
        screen.blit(text_surface, text_rect)


# Global tooltip manager instance
tooltip_manager = TooltipManager()
