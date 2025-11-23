"""
Interactive UI components for user interaction.

This module provides interactive components that handle user input and maintain
interaction states, following Single Responsibility Principle.
"""

import pygame
from typing import List, Optional, Dict, Any, Callable, Union
from dataclasses import dataclass
from enum import Enum

from .base import InteractiveComponent, EventResult
from .style import Style, StyleManager


class ButtonState(Enum):
    """Button interaction states."""
    NORMAL = "normal"
    HOVER = "hover"
    PRESSED = "pressed"
    DISABLED = "disabled"


class SliderOrientation(Enum):
    """Slider orientation."""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


@dataclass
class DropdownOption:
    """Dropdown option definition."""
    value: Any
    label: str
    enabled: bool = True


class Button(InteractiveComponent):
    """
    Interactive button component.
    
    Responsibility: Handle click interactions and visual feedback.
    """
    
    def __init__(
        self, 
        rect: pygame.Rect, 
        text: str = "",
        style: Optional[Style] = None,
        component_id: str = ""
    ):
        super().__init__(rect, style, component_id)
        
        # Button properties
        self.text = text
        self.state = ButtonState.NORMAL
        
        # Event callbacks
        self.on_click: Optional[Callable[[], None]] = None
        self.on_right_click: Optional[Callable[[], None]] = None
        self.on_hover_enter: Optional[Callable[[], None]] = None
        self.on_hover_exit: Optional[Callable[[], None]] = None
        
        # Visual properties
        self.show_border = True
        self.corner_radius = self.style.corner_radius
        self.text_alignment = "center"
        
        # State tracking
        self._was_hovered = False
    
    def set_text(self, text: str) -> None:
        """Set button text."""
        self.text = text
    
    def set_callback(self, callback: Callable[[], None]) -> None:
        """Set click callback."""
        self.on_click = callback
    
    def _handle_own_event(self, event: pygame.event.Event) -> EventResult:
        """Handle button-specific events."""
        if not self.enabled:
            return EventResult(handled=False)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.rect.collidepoint(event.pos):
                    self.state = ButtonState.PRESSED
                    return EventResult(handled=True)
            elif event.button == 3 and self.on_right_click:  # Right click
                if self.rect.collidepoint(event.pos):
                    self.on_right_click()
                    return EventResult(handled=True)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                if self.state == ButtonState.PRESSED:
                    if self.rect.collidepoint(event.pos):
                        if self.on_click:
                            self.on_click()
                        self.state = ButtonState.HOVER
                    else:
                        self.state = ButtonState.NORMAL
                    return EventResult(handled=True)
        
        return EventResult(handled=False)
    
    def _update_component(self, dt: float) -> None:
        """Update button state based on hover."""
        if not self.enabled:
            self.state = ButtonState.DISABLED
            return
        
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Handle hover state transitions
        if is_hovered and self.state == ButtonState.NORMAL:
            self.state = ButtonState.HOVER
            if self.on_hover_enter:
                self.on_hover_enter()
        elif not is_hovered and self.state == ButtonState.HOVER:
            self.state = ButtonState.NORMAL
            if self.on_hover_exit:
                self.on_hover_exit()
        
        # Update hover tracking
        if self._was_hovered != is_hovered:
            self._was_hovered = is_hovered
    
    def _draw_self(self, screen: pygame.Surface) -> None:
        """Draw button with current state styling."""
        # Get color based on state
        if self.state == ButtonState.DISABLED:
            bg_color = self.style.get_color("button_disabled")
            text_color = self.style.get_color("text_disabled")
            border_color = self.style.get_color("border_disabled")
        elif self.state == ButtonState.PRESSED:
            bg_color = self.style.get_color("button_active")
            text_color = self.style.get_color("text")
            border_color = self.style.get_color("border_active")
        elif self.state == ButtonState.HOVER:
            bg_color = self.style.get_color("button_hover")
            text_color = self.style.get_color("text")
            border_color = self.style.get_color("border_active")
        else:  # NORMAL
            bg_color = self.style.get_color("button")
            text_color = self.style.get_color("text")
            border_color = self.style.get_color("border")
        
        # Draw button background
        if self.corner_radius > 0:
            # Draw rounded rectangle
            self._draw_rounded_rect(screen, bg_color, self.rect, self.corner_radius)
        else:
            pygame.draw.rect(screen, bg_color, self.rect)
        
        # Draw border
        if self.show_border:
            if self.corner_radius > 0:
                self._draw_rounded_rect(screen, border_color, self.rect, self.corner_radius, self.style.border_width)
            else:
                pygame.draw.rect(screen, border_color, self.rect, self.style.border_width)
        
        # Draw text
        if self.text:
            font = self.style.get_font("normal")
            text_surface = font.render(self.text, True, text_color)
            
            # Position text based on alignment
            if self.text_alignment == "center":
                text_rect = text_surface.get_rect(center=self.rect.center)
            elif self.text_alignment == "left":
                text_rect = text_surface.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
            else:  # right
                text_rect = text_surface.get_rect(midright=(self.rect.right - 10, self.rect.centery))
            
            screen.blit(text_surface, text_rect)
    
    def _draw_rounded_rect(self, screen: pygame.Surface, color: pygame.Color, rect: pygame.Rect, radius: int, width: int = 0) -> None:
        """Draw rounded rectangle."""
        if width == 0:
            # Filled rounded rectangle
            pygame.draw.rect(screen, color, rect, border_radius=radius)
        else:
            # Rounded rectangle outline
            pygame.draw.rect(screen, color, rect, width, border_radius=radius)


class Slider(InteractiveComponent):
    """
    Interactive slider component for value selection.
    
    Responsibility: Handle value selection through dragging.
    """
    
    def __init__(
        self, 
        rect: pygame.Rect, 
        min_val: float = 0.0, 
        max_val: float = 1.0, 
        initial_val: float = 0.5,
        orientation: SliderOrientation = SliderOrientation.HORIZONTAL,
        style: Optional[Style] = None,
        component_id: str = ""
    ):
        super().__init__(rect, style, component_id)
        
        # Slider properties
        self.min_val = min_val
        self.max_val = max_val
        self.value = max(min_val, min(max_val, initial_val))
        self.orientation = orientation
        
        # Visual properties
        self.track_height = 6
        self.handle_size = 20
        self.show_value_label = True
        self.value_format = "{:.2f}"
        
        # Event callbacks
        self.on_change: Optional[Callable[[float], None]] = None
        self.on_change_start: Optional[Callable[[float], None]] = None
        self.on_change_end: Optional[Callable[[float], None]] = None
        
        # Interaction state
        self._dragging = False
        self._drag_start_pos = None
        self._drag_start_value = None
    
    def set_value(self, value: float) -> None:
        """Set slider value."""
        old_value = self.value
        self.value = max(self.min_val, min(self.max_val, value))
        
        if old_value != self.value and self.on_change:
            self.on_change(self.value)
    
    def set_range(self, min_val: float, max_val: float) -> None:
        """Set value range."""
        self.min_val = min_val
        self.max_val = max_val
        self.set_value(self.value)  # Clamp current value
    
    def get_value(self) -> float:
        """Get current slider value."""
        return self.value
    
    def get_normalized_value(self) -> float:
        """Get normalized value (0.0 to 1.0)."""
        if self.max_val - self.min_val == 0:
            return 0.0
        return (self.value - self.min_val) / (self.max_val - self.min_val)
    
    def _get_track_rect(self) -> pygame.Rect:
        """Get track rectangle."""
        if self.orientation == SliderOrientation.HORIZONTAL:
            return pygame.Rect(
                self.rect.x,
                self.rect.centery - self.track_height // 2,
                self.rect.width,
                self.track_height
            )
        else:  # VERTICAL
            return pygame.Rect(
                self.rect.centerx - self.track_height // 2,
                self.rect.y,
                self.track_height,
                self.rect.height
            )
    
    def _get_handle_rect(self) -> pygame.Rect:
        """Get handle rectangle."""
        normalized = self.get_normalized_value()
        
        if self.orientation == SliderOrientation.HORIZONTAL:
            handle_x = self.rect.x + int(normalized * (self.rect.width - self.handle_size))
            return pygame.Rect(
                handle_x,
                self.rect.centery - self.handle_size // 2,
                self.handle_size,
                self.handle_size
            )
        else:  # VERTICAL
            handle_y = self.rect.bottom - self.handle_size - int(normalized * (self.rect.height - self.handle_size))
            return pygame.Rect(
                self.rect.centerx - self.handle_size // 2,
                handle_y,
                self.handle_size,
                self.handle_size
            )
    
    def _value_from_position(self, pos: Tuple[int, int]) -> float:
        """Convert mouse position to value."""
        if self.orientation == SliderOrientation.HORIZONTAL:
            relative_x = pos[0] - self.rect.x
            normalized = max(0.0, min(1.0, relative_x / self.rect.width))
        else:  # VERTICAL
            relative_y = self.rect.bottom - pos[1]
            normalized = max(0.0, min(1.0, relative_y / self.rect.height))
        
        return self.min_val + normalized * (self.max_val - self.min_val)
    
    def _handle_own_event(self, event: pygame.event.Event) -> EventResult:
        """Handle slider-specific events."""
        if not self.enabled:
            return EventResult(handled=False)
        
        handle_rect = self._get_handle_rect()
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if handle_rect.collidepoint(event.pos):
                self._dragging = True
                self._drag_start_pos = event.pos
                self._drag_start_value = self.value
                
                if self.on_change_start:
                    self.on_change_start(self.value)
                
                return EventResult(handled=True)
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._dragging:
                self._dragging = False
                
                if self.on_change_end:
                    self.on_change_end(self.value)
                
                return EventResult(handled=True)
        
        elif event.type == pygame.MOUSEMOTION:
            if self._dragging:
                new_value = self._value_from_position(event.pos)
                self.set_value(new_value)
                return EventResult(handled=True)
        
        return EventResult(handled=False)
    
    def _update_component(self, dt: float) -> None:
        """Update slider visual state."""
        pass  # Slider visual state is updated in draw method
    
    def _draw_self(self, screen: pygame.Surface) -> None:
        """Draw slider track and handle."""
        # Draw track
        track_rect = self._get_track_rect()
        pygame.draw.rect(screen, self.style.get_color("slider_track"), track_rect)
        
        # Draw track highlight (showing current value)
        normalized = self.get_normalized_value()
        if self.orientation == SliderOrientation.HORIZONTAL:
            highlight_rect = pygame.Rect(
                track_rect.x,
                track_rect.y,
                int(track_rect.width * normalized),
                track_rect.height
            )
        else:  # VERTICAL
            highlight_rect = pygame.Rect(
                track_rect.x,
                track_rect.bottom - int(track_rect.height * normalized),
                track_rect.width,
                int(track_rect.height * normalized)
            )
        pygame.draw.rect(screen, self.style.get_color("accent"), highlight_rect)
        
        # Draw handle
        handle_rect = self._get_handle_rect()
        handle_color = self.style.get_color("slider_handle")
        if self._dragging:
            handle_color = self.style.get_color("button_hover")
        elif handle_rect.collidepoint(pygame.mouse.get_pos()):
            handle_color = self.style.get_color("button_active")
        
        pygame.draw.rect(screen, handle_color, handle_rect, border_radius=self.handle_size // 2)
        pygame.draw.rect(screen, self.style.get_color("border"), handle_rect, 1, border_radius=self.handle_size // 2)
        
        # Draw value label
        if self.show_value_label:
            value_text = self.value_format.format(self.value)
            font = self.style.get_font("small")
            text_surface = font.render(value_text, True, self.style.get_color("text"))
            
            if self.orientation == SliderOrientation.HORIZONTAL:
                text_rect = text_surface.get_rect(midtop=(self.rect.centerx, self.rect.bottom + 5))
            else:  # VERTICAL
                text_rect = text_surface.get_rect(midleft=(self.rect.right + 5, self.rect.centery))
            
            screen.blit(text_surface, text_rect)


class Checkbox(InteractiveComponent):
    """
    Interactive checkbox component for boolean selection.
    
    Responsibility: Handle toggle state and visual feedback.
    """
    
    def __init__(
        self, 
        rect: pygame.Rect, 
        label: str = "",
        checked: bool = False,
        style: Optional[Style] = None,
        component_id: str = ""
    ):
        super().__init__(rect, style, component_id)
        
        # Checkbox properties
        self.label = label
        self.checked = checked
        self.box_size = 20
        self.label_spacing = 10
        
        # Event callbacks
        self.on_toggle: Optional[Callable[[bool], None]] = None
        
        # Calculate label position
        self._update_label_position()
    
    def set_checked(self, checked: bool) -> None:
        """Set checkbox state."""
        if self.checked != checked:
            self.checked = checked
            if self.on_toggle:
                self.on_toggle(checked)
    
    def toggle(self) -> None:
        """Toggle checkbox state."""
        self.set_checked(not self.checked)
    
    def is_checked(self) -> bool:
        """Get checkbox state."""
        return self.checked
    
    def _update_label_position(self) -> None:
        """Update label position based on box size."""
        self.label_x = self.rect.x + self.box_size + self.label_spacing
        self.label_y = self.rect.y + (self.rect.height - self.box_size) // 2
    
    def _get_box_rect(self) -> pygame.Rect:
        """Get checkbox box rectangle."""
        return pygame.Rect(
            self.rect.x,
            self.rect.y + (self.rect.height - self.box_size) // 2,
            self.box_size,
            self.box_size
        )
    
    def _handle_own_event(self, event: pygame.event.Event) -> EventResult:
        """Handle checkbox-specific events."""
        if not self.enabled:
            return EventResult(handled=False)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if click is on box or label
            box_rect = self._get_box_rect()
            
            # Create expanded rect for label click area
            label_rect = pygame.Rect(
                self.label_x,
                self.label_y - 5,
                200,  # Generous width for label
                self.box_size + 10
            )
            
            if box_rect.collidepoint(event.pos) or (self.label and label_rect.collidepoint(event.pos)):
                self.toggle()
                return EventResult(handled=True)
        
        return EventResult(handled=False)
    
    def _update_component(self, dt: float) -> None:
        """Update checkbox visual state."""
        pass
    
    def _draw_self(self, screen: pygame.Surface) -> None:
        """Draw checkbox box and label."""
        box_rect = self._get_box_rect()
        
        # Draw box background
        if self.checked:
            bg_color = self.style.get_color("checkbox_checked")
        else:
            bg_color = self.style.get_color("checkbox")
        
        pygame.draw.rect(screen, bg_color, box_rect, border_radius=self.style.corner_radius)
        
        # Draw border
        border_color = self.style.get_color("border")
        if not self.enabled:
            border_color = self.style.get_color("border_disabled")
        pygame.draw.rect(screen, border_color, box_rect, self.style.border_width, border_radius=self.style.corner_radius)
        
        # Draw checkmark if checked
        if self.checked:
            # Draw checkmark
            check_color = self.style.get_color("text")
            check_points = [
                (box_rect.x + 4, box_rect.centery),
                (box_rect.x + 8, box_rect.bottom - 4),
                (box_rect.right - 4, box_rect.y + 4)
            ]
            pygame.draw.lines(screen, check_color, False, check_points, 2)
        
        # Draw label
        if self.label:
            text_color = self.style.get_color("text") if self.enabled else self.style.get_color("text_disabled")
            font = self.style.get_font("normal")
            text_surface = font.render(self.label, True, text_color)
            
            screen.blit(text_surface, (self.label_x, self.label_y))


class Dropdown(InteractiveComponent):
    """
    Interactive dropdown component for option selection.
    
    Responsibility: Handle option selection and dropdown menu display.
    """
    
    def __init__(
        self, 
        rect: pygame.Rect, 
        options: List[Union[str, DropdownOption]] = None,
        style: Optional[Style] = None,
        component_id: str = ""
    ):
        super().__init__(rect, style, component_id)
        
        # Dropdown properties
        self.options: List[DropdownOption] = []
        self.selected_index = 0
        self.is_open = False
        self.max_visible_items = 8
        self.item_height = 25
        
        # Convert string options to DropdownOption objects
        if options:
            for option in options:
                if isinstance(option, str):
                    self.options.append(DropdownOption(value=option, label=option))
                else:
                    self.options.append(option)
        
        # Visual properties
        self.arrow_size = 10
        self.show_arrow = True
        
        # Event callbacks
        self.on_change: Optional[Callable[[Any], None]] = None
        self.on_open: Optional[Callable[[], None]] = None
        self.on_close: Optional[Callable[[], None]] = None
        
        # Calculate dropdown menu rectangle
        self._update_menu_rect()
    
    def add_option(self, value: Any, label: str, enabled: bool = True) -> None:
        """Add an option to the dropdown."""
        self.options.append(DropdownOption(value=value, label=label, enabled=enabled))
        self._update_menu_rect()
    
    def remove_option(self, index: int) -> None:
        """Remove an option by index."""
        if 0 <= index < len(self.options):
            del self.options[index]
            if self.selected_index >= len(self.options):
                self.selected_index = max(0, len(self.options) - 1)
            self._update_menu_rect()
    
    def set_selected_index(self, index: int) -> None:
        """Set selected option by index."""
        if 0 <= index < len(self.options) and self.options[index].enabled:
            old_index = self.selected_index
            self.selected_index = index
            
            if old_index != index and self.on_change:
                self.on_change(self.options[index].value)
    
    def set_selected_value(self, value: Any) -> None:
        """Set selected option by value."""
        for i, option in enumerate(self.options):
            if option.value == value and option.enabled:
                self.set_selected_index(i)
                break
    
    def get_selected_value(self) -> Any:
        """Get selected option value."""
        if 0 <= self.selected_index < len(self.options):
            return self.options[self.selected_index].value
        return None
    
    def get_selected_label(self) -> str:
        """Get selected option label."""
        if 0 <= self.selected_index < len(self.options):
            return self.options[self.selected_index].label
        return ""
    
    def _update_menu_rect(self) -> None:
        """Update dropdown menu rectangle."""
        visible_count = min(len(self.options), self.max_visible_items)
        menu_height = visible_count * self.item_height
        
        self.menu_rect = pygame.Rect(
            self.rect.x,
            self.rect.bottom,
            self.rect.width,
            menu_height
        )
    
    def _get_item_rect(self, index: int) -> pygame.Rect:
        """Get rectangle for menu item."""
        return pygame.Rect(
            self.menu_rect.x,
            self.menu_rect.y + index * self.item_height,
            self.menu_rect.width,
            self.item_height
        )
    
    def _get_item_at_position(self, pos: Tuple[int, int]) -> int:
        """Get item index at mouse position."""
        if not self.menu_rect.collidepoint(pos):
            return -1
        
        relative_y = pos[1] - self.menu_rect.y
        index = relative_y // self.item_height
        
        if 0 <= index < len(self.options):
            return index
        
        return -1
    
    def _handle_own_event(self, event: pygame.event.Event) -> EventResult:
        """Handle dropdown-specific events."""
        if not self.enabled:
            return EventResult(handled=False)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                # Toggle dropdown
                if self.is_open:
                    self.close()
                else:
                    self.open()
                return EventResult(handled=True)
            
            elif self.is_open:
                # Check menu item clicks
                item_index = self._get_item_at_position(event.pos)
                if item_index >= 0 and self.options[item_index].enabled:
                    self.set_selected_index(item_index)
                    self.close()
                    return EventResult(handled=True)
                elif not self.menu_rect.collidepoint(event.pos):
                    # Click outside dropdown
                    self.close()
                    return EventResult(handled=True)
        
        return EventResult(handled=False)
    
    def open(self) -> None:
        """Open dropdown menu."""
        if not self.is_open and len(self.options) > 0:
            self.is_open = True
            if self.on_open:
                self.on_open()
    
    def close(self) -> None:
        """Close dropdown menu."""
        if self.is_open:
            self.is_open = False
            if self.on_close:
                self.on_close()
    
    def _update_component(self, dt: float) -> None:
        """Update dropdown visual state."""
        pass
    
    def _draw_self(self, screen: pygame.Surface) -> None:
        """Draw dropdown button and menu."""
        # Draw main button
        bg_color = self.style.get_color("button")
        if not self.enabled:
            bg_color = self.style.get_color("button_disabled")
        elif self.rect.collidepoint(pygame.mouse.get_pos()):
            bg_color = self.style.get_color("button_hover")
        
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=self.style.corner_radius)
        pygame.draw.rect(screen, self.style.get_color("border"), self.rect, self.style.border_width, border_radius=self.style.corner_radius)
        
        # Draw selected text
        if self.options:
            text_color = self.style.get_color("text") if self.enabled else self.style.get_color("text_disabled")
            font = self.style.get_font("normal")
            text_surface = font.render(self.get_selected_label(), True, text_color)
            
            text_rect = text_surface.get_rect(
                left=self.rect.x + 10,
                centery=self.rect.centery
            )
            screen.blit(text_surface, text_rect)
        
        # Draw dropdown arrow
        if self.show_arrow:
            arrow_color = self.style.get_color("text") if self.enabled else self.style.get_color("text_disabled")
            arrow_x = self.rect.right - self.arrow_size - 10
            arrow_y = self.rect.centery
            
            # Draw triangle
            if self.is_open:
                # Upward arrow
                points = [
                    (arrow_x, arrow_y + self.arrow_size // 2),
                    (arrow_x - self.arrow_size // 2, arrow_y - self.arrow_size // 2),
                    (arrow_x + self.arrow_size // 2, arrow_y - self.arrow_size // 2)
                ]
            else:
                # Downward arrow
                points = [
                    (arrow_x, arrow_y - self.arrow_size // 2),
                    (arrow_x - self.arrow_size // 2, arrow_y + self.arrow_size // 2),
                    (arrow_x + self.arrow_size // 2, arrow_y + self.arrow_size // 2)
                ]
            
            pygame.draw.polygon(screen, arrow_color, points)
        
        # Draw dropdown menu if open
        if self.is_open:
            # Draw menu background
            pygame.draw.rect(screen, self.style.get_color("panel"), self.menu_rect)
            pygame.draw.rect(screen, self.style.get_color("border"), self.menu_rect, self.style.border_width)
            
            # Draw menu items
            font = self.style.get_font("normal")
            for i, option in enumerate(self.options):
                item_rect = self._get_item_rect(i)
                
                # Highlight hovered item
                if item_rect.collidepoint(pygame.mouse.get_pos()):
                    if option.enabled:
                        pygame.draw.rect(screen, self.style.get_color("button_hover"), item_rect)
                    else:
                        pygame.draw.rect(screen, self.style.get_color("surface"), item_rect)
                
                # Draw item text
                text_color = self.style.get_color("text") if option.enabled else self.style.get_color("text_disabled")
                text_surface = font.render(option.label, True, text_color)
                
                text_rect = text_surface.get_rect(
                    left=item_rect.x + 10,
                    centery=item_rect.centery
                )
                screen.blit(text_surface, text_rect)
                
                # Draw separator line (except last item)
                if i < len(self.options) - 1:
                    pygame.draw.line(
                        screen,
                        self.style.get_color("border"),
                        (item_rect.x, item_rect.bottom),
                        (item_rect.right, item_rect.bottom),
                        1
                    )
