"""
Display UI components for pure rendering.

This module provides display components that render content without handling
user interaction, following Single Responsibility Principle.
"""

import pygame
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from .base import DisplayComponent, EventResult
from .style import Style, StyleManager


class Alignment(Enum):
    """Text alignment enumeration."""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"


class TextWrap(Enum):
    """Text wrapping behavior."""
    NONE = "none"
    WORD = "word"
    CHARACTER = "character"


class IconType(Enum):
    """Icon type enumeration."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    SETTINGS = "settings"
    SAVE = "save"
    LOAD = "load"
    DELETE = "delete"
    EDIT = "edit"
    PLAY = "play"
    PAUSE = "pause"
    STOP = "stop"
    NEXT = "next"
    PREVIOUS = "previous"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    PLUS = "plus"
    MINUS = "minus"
    CHECK = "check"
    CROSS = "cross"
    ARROW_UP = "arrow_up"
    ARROW_DOWN = "arrow_down"
    ARROW_LEFT = "arrow_left"
    ARROW_RIGHT = "arrow_right"


@dataclass
class TextFormat:
    """Text formatting options."""
    font_size: str = "normal"
    bold: bool = False
    italic: bool = False
    underline: bool = False
    color: Optional[Tuple[int, int, int]] = None
    shadow: bool = False
    shadow_offset: Tuple[int, int] = (1, 1)
    shadow_color: Tuple[int, int, int] = (0, 0, 0)


class Label(DisplayComponent):
    """
    Text label component for pure text display.
    
    Responsibility: Display text with formatting and alignment.
    """
    
    def __init__(
        self, 
        rect: pygame.Rect, 
        text: str = "",
        alignment: Alignment = Alignment.LEFT,
        style: Optional[Style] = None,
        component_id: str = ""
    ):
        super().__init__(rect, style, component_id)
        
        # Text properties
        self.text = text
        self.alignment = alignment
        self.wrap_mode = TextWrap.NONE
        self.format = TextFormat()
        
        # Rendering cache
        self._text_surface: Optional[pygame.Surface] = None
        self._text_lines: list[str] = []
        self._needs_redraw = True
    
    def set_text(self, text: str) -> None:
        """Set label text."""
        if self.text != text:
            self.text = text
            self._needs_redraw = True
    
    def set_alignment(self, alignment: Alignment) -> None:
        """Set text alignment."""
        if self.alignment != alignment:
            self.alignment = alignment
            self._needs_redraw = True
    
    def set_wrap_mode(self, wrap_mode: TextWrap) -> None:
        """Set text wrapping mode."""
        if self.wrap_mode != wrap_mode:
            self.wrap_mode = wrap_mode
            self._needs_redraw = True
    
    def set_format(self, format: TextFormat) -> None:
        """Set text formatting."""
        self.format = format
        self._needs_redraw = True
    
    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> list[str]:
        """Wrap text to fit within maximum width."""
        if self.wrap_mode == TextWrap.NONE:
            return [text]
        
        lines = []
        words = text.split(' ') if self.wrap_mode == TextWrap.WORD else list(text)
        
        current_line = ""
        
        for word in words:
            test_line = current_line + ('' if not current_line else ' ') + word
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Word is too long, break it
                    if self.wrap_mode == TextWrap.CHARACTER:
                        for char in word:
                            test_char_line = current_line + char
                            test_char_width = font.size(test_char_line)[0]
                            if test_char_width <= max_width:
                                current_line = test_char_line
                            else:
                                if current_line:
                                    lines.append(current_line)
                                current_line = char
                    else:
                        lines.append(word)
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _render_text(self) -> pygame.Surface:
        """Render text to surface."""
        if not self.text:
            return pygame.Surface((0, 0), pygame.SRCALPHA)
        
        # Get font
        font = self.style.get_font(self.format.font_size)
        
        # Apply formatting
        if self.format.bold:
            font.set_bold(True)
        if self.format.italic:
            font.set_italic(True)
        if self.format.underline:
            font.set_underline(True)
        
        # Get text color
        color = self.format.color or self.style.get_color("text")
        
        # Wrap text if needed
        if self.wrap_mode != TextWrap.NONE:
            self._text_lines = self._wrap_text(self.text, font, self.rect.width)
        else:
            self._text_lines = [self.text]
        
        # Calculate total height
        line_height = font.get_height()
        total_height = len(self._text_lines) * line_height
        
        # Create surface
        surface = pygame.Surface((self.rect.width, total_height), pygame.SRCALPHA)
        
        # Render each line
        for i, line in enumerate(self._text_lines):
            y = i * line_height
            
            # Add shadow if enabled
            if self.format.shadow:
                shadow_surface = font.render(line, True, self.format.shadow_color)
                shadow_rect = shadow_surface.get_rect(
                    x=self.format.shadow_offset[0],
                    y=y + self.format.shadow_offset[1]
                )
                surface.blit(shadow_surface, shadow_rect)
            
            # Render text
            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect(y=y)
            surface.blit(text_surface, text_rect)
        
        # Reset font formatting
        font.set_bold(False)
        font.set_italic(False)
        font.set_underline(False)
        
        return surface
    
    def _update_component(self, dt: float) -> None:
        """Update label rendering if needed."""
        pass  # Label updates are handled in draw method
    
    def _handle_own_event(self, event: pygame.event.Event) -> EventResult:
        """Labels don't handle events."""
        return EventResult(handled=False)
    
    def _draw_self(self, screen: pygame.Surface) -> None:
        """Draw label text."""
        if not self.text:
            return
        
        # Render text if needed
        if self._needs_redraw or self._text_surface is None:
            self._text_surface = self._render_text()
            self._needs_redraw = False
        
        if self._text_surface is None:
            return
        
        # Calculate position based on alignment
        text_rect = self._text_surface.get_rect()
        
        if self.alignment == Alignment.CENTER:
            text_rect.centerx = self.rect.centerx
            text_rect.centery = self.rect.centery
        elif self.alignment == Alignment.RIGHT:
            text_rect.right = self.rect.right
            text_rect.centery = self.rect.centery
        else:  # LEFT
            text_rect.left = self.rect.left
            text_rect.centery = self.rect.centery
        
        # Clip to rect
        if text_rect.height > self.rect.height:
            # Clip vertically
            clip_rect = pygame.Rect(
                text_rect.x,
                text_rect.y,
                text_rect.width,
                self.rect.height
            )
            screen.set_clip(clip_rect)
        
        screen.blit(self._text_surface, text_rect)
        screen.set_clip(None)  # Reset clipping
    
    def get_text_size(self) -> Tuple[int, int]:
        """Get rendered text size."""
        if self._needs_redraw or self._text_surface is None:
            self._text_surface = self._render_text()
            self._needs_redraw = False
        
        if self._text_surface:
            return self._text_surface.get_size()
        return (0, 0)


class ProgressBar(DisplayComponent):
    """
    Progress bar component for visualizing progress.
    
    Responsibility: Display progress value with visual feedback.
    """
    
    def __init__(
        self, 
        rect: pygame.Rect, 
        value: float = 0.0,
        min_val: float = 0.0,
        max_val: float = 1.0,
        style: Optional[Style] = None,
        component_id: str = ""
    ):
        super().__init__(rect, style, component_id)
        
        # Progress properties
        self.value = value
        self.min_val = min_val
        self.max_val = max_val
        
        # Visual properties
        self.show_percentage = True
        self.show_text = True
        self.custom_text = ""
        self.orientation = "horizontal"  # or "vertical"
        self.border_radius = self.style.corner_radius
        
        # Color scheme (can be customized)
        self.progress_color = None  # Use default if None
        self.background_color = None  # Use default if None
        
        # Animation
        self.animated = False
        self.target_value = value
        self.animation_speed = 2.0
    
    def set_value(self, value: float) -> None:
        """Set progress value."""
        self.value = max(self.min_val, min(self.max_val, value))
        if self.animated:
            self.target_value = self.value
        else:
            self.target_value = value
    
    def set_range(self, min_val: float, max_val: float) -> None:
        """Set value range."""
        self.min_val = min_val
        self.max_val = max_val
        self.set_value(self.value)  # Clamp current value
    
    def get_percentage(self) -> float:
        """Get progress as percentage (0.0 to 1.0)."""
        if self.max_val - self.min_val == 0:
            return 0.0
        return (self.value - self.min_val) / (self.max_val - self.min_val)
    
    def set_text(self, text: str) -> None:
        """Set custom text to display."""
        self.custom_text = text
        self.show_text = bool(text)
    
    def _update_component(self, dt: float) -> None:
        """Update progress bar animation."""
        if self.animated and abs(self.value - self.target_value) > 0.01:
            # Animate towards target value
            diff = self.target_value - self.value
            self.value += diff * self.animation_speed * dt
    
    def _handle_own_event(self, event: pygame.event.Event) -> EventResult:
        """Progress bars don't handle events."""
        return EventResult(handled=False)
    
    def _draw_self(self, screen: pygame.Surface) -> None:
        """Draw progress bar."""
        percentage = self.get_percentage()
        
        # Get colors
        bg_color = self.background_color or self.style.get_color("surface")
        progress_color = self.progress_color or self.style.get_color("accent")
        border_color = self.style.get_color("border")
        text_color = self.style.get_color("text")
        
        # Draw background
        if self.border_radius > 0:
            pygame.draw.rect(screen, bg_color, self.rect, border_radius=self.border_radius)
        else:
            pygame.draw.rect(screen, bg_color, self.rect)
        
        # Draw progress fill
        if self.orientation == "horizontal":
            fill_width = int(self.rect.width * percentage)
            fill_rect = pygame.Rect(
                self.rect.x,
                self.rect.y,
                fill_width,
                self.rect.height
            )
        else:  # vertical
            fill_height = int(self.rect.height * percentage)
            fill_rect = pygame.Rect(
                self.rect.x,
                self.rect.bottom - fill_height,
                self.rect.width,
                fill_height
            )
        
        if self.border_radius > 0:
            # Clip progress fill to rounded corners
            if self.orientation == "horizontal":
                clip_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.y,
                    min(fill_width, self.rect.width - 2 * self.border_radius),
                    self.rect.height
                )
            else:
                clip_rect = pygame.Rect(
                    self.rect.x,
                    max(self.rect.y + self.border_radius, self.rect.bottom - fill_height),
                    self.rect.width,
                    min(fill_height, self.rect.height - 2 * self.border_radius)
                )
            
            screen.set_clip(clip_rect)
            pygame.draw.rect(screen, progress_color, self.rect, border_radius=self.border_radius)
            screen.set_clip(None)
        else:
            pygame.draw.rect(screen, progress_color, fill_rect)
        
        # Draw border
        if self.border_radius > 0:
            pygame.draw.rect(screen, border_color, self.rect, self.style.border_width, border_radius=self.border_radius)
        else:
            pygame.draw.rect(screen, border_color, self.rect, self.style.border_width)
        
        # Draw text
        if self.show_text:
            if self.custom_text:
                display_text = self.custom_text
            elif self.show_percentage:
                display_text = f"{int(percentage * 100)}%"
            else:
                display_text = f"{self.value:.1f}/{self.max_val:.1f}"
            
            font = self.style.get_font("small")
            text_surface = font.render(display_text, True, text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            
            # Ensure text fits
            if text_rect.width <= self.rect.width - 10:
                screen.blit(text_surface, text_rect)


class Icon(DisplayComponent):
    """
    Icon component for displaying symbolic graphics.
    
    Responsibility: Draw icon graphics with customizable appearance.
    """
    
    def __init__(
        self, 
        rect: pygame.Rect, 
        icon_type: IconType = IconType.INFO,
        color: Optional[Tuple[int, int, int]] = None,
        style: Optional[Style] = None,
        component_id: str = ""
    ):
        super().__init__(rect, style, component_id)
        
        # Icon properties
        self.icon_type = icon_type
        self.color = color
        self.size = min(rect.width, rect.height)
        self.rotation = 0
        self.scale = 1.0
        
        # Drawing cache
        self._icon_surface: Optional[pygame.Surface] = None
        self._needs_redraw = True
    
    def set_icon_type(self, icon_type: IconType) -> None:
        """Set icon type."""
        if self.icon_type != icon_type:
            self.icon_type = icon_type
            self._needs_redraw = True
    
    def set_color(self, color: Tuple[int, int, int]) -> None:
        """Set icon color."""
        if self.color != color:
            self.color = color
            self._needs_redraw = True
    
    def set_rotation(self, rotation: float) -> None:
        """Set icon rotation in degrees."""
        if self.rotation != rotation:
            self.rotation = rotation
            self._needs_redraw = True
    
    def set_scale(self, scale: float) -> None:
        """Set icon scale."""
        if self.scale != scale:
            self.scale = scale
            self._needs_redraw = True
    
    def _get_icon_color(self) -> Tuple[int, int, int]:
        """Get icon color based on type or custom color."""
        if self.color:
            return self.color
        
        # Default colors based on icon type
        color_map = {
            IconType.INFO: self.style.get_color("info"),
            IconType.WARNING: self.style.get_color("warning"),
            IconType.ERROR: self.style.get_color("error"),
            IconType.SUCCESS: self.style.get_color("success"),
            IconType.SETTINGS: self.style.get_color("text"),
            IconType.SAVE: self.style.get_color("success"),
            IconType.LOAD: self.style.get_color("info"),
            IconType.DELETE: self.style.get_color("error"),
            IconType.EDIT: self.style.get_color("text"),
            IconType.PLAY: self.style.get_color("success"),
            IconType.PAUSE: self.style.get_color("warning"),
            IconType.STOP: self.style.get_color("error"),
            IconType.NEXT: self.style.get_color("text"),
            IconType.PREVIOUS: self.style.get_color("text"),
            IconType.UP: self.style.get_color("text"),
            IconType.DOWN: self.style.get_color("text"),
            IconType.LEFT: self.style.get_color("text"),
            IconType.RIGHT: self.style.get_color("text"),
            IconType.PLUS: self.style.get_color("success"),
            IconType.MINUS: self.style.get_color("error"),
            IconType.CHECK: self.style.get_color("success"),
            IconType.CROSS: self.style.get_color("error"),
        }
        
        return color_map.get(self.icon_type, self.style.get_color("text"))
    
    def _draw_icon_shape(self, surface: pygame.Surface, color: Tuple[int, int, int]) -> None:
        """Draw icon shape based on type."""
        center = surface.get_width() // 2, surface.get_height() // 2
        size = int(self.size * self.scale)
        
        if self.icon_type in [IconType.INFO, IconType.WARNING, IconType.ERROR, IconType.SUCCESS]:
            # Circle with symbol
            pygame.draw.circle(surface, color, center, size // 2, 3)
            
            if self.icon_type == IconType.INFO:
                # 'i' symbol
                pygame.draw.line(surface, color, (center[0], center[1] - size // 4), (center[0], center[1] + size // 6), 3)
                pygame.draw.circle(surface, color, (center[0], center[1] - size // 6), 2)
            elif self.icon_type == IconType.WARNING:
                # '!' symbol
                pygame.draw.line(surface, color, (center[0], center[1] - size // 4), (center[0], center[1] + size // 8), 3)
                pygame.draw.circle(surface, color, (center[0], center[1] + size // 4), 2)
            elif self.icon_type == IconType.ERROR:
                # 'X' symbol
                offset = size // 4
                pygame.draw.line(surface, color, (center[0] - offset, center[1] - offset), (center[0] + offset, center[1] + offset), 3)
                pygame.draw.line(surface, color, (center[0] + offset, center[1] - offset), (center[0] - offset, center[1] + offset), 3)
            elif self.icon_type == IconType.SUCCESS:
                # Checkmark
                points = [
                    (center[0] - size // 4, center[1]),
                    (center[0] - size // 8, center[1] + size // 8),
                    (center[0] + size // 4, center[1] - size // 6)
                ]
                pygame.draw.lines(surface, color, False, points, 3)
        
        elif self.icon_type in [IconType.PLUS, IconType.MINUS]:
            # Plus/minus sign
            pygame.draw.line(surface, color, (center[0] - size // 3, center[1]), (center[0] + size // 3, center[1]), 3)
            if self.icon_type == IconType.PLUS:
                pygame.draw.line(surface, color, (center[0], center[1] - size // 3), (center[0], center[1] + size // 3), 3)
        
        elif self.icon_type in [IconType.PLAY, IconType.PAUSE, IconType.STOP]:
            # Media controls
            if self.icon_type == IconType.PLAY:
                # Triangle
                points = [
                    (center[0] - size // 4, center[1] - size // 3),
                    (center[0] - size // 4, center[1] + size // 3),
                    (center[0] + size // 4, center[1])
                ]
                pygame.draw.polygon(surface, color, points)
            elif self.icon_type == IconType.PAUSE:
                # Two vertical bars
                bar_width = size // 6
                pygame.draw.rect(surface, color, (center[0] - size // 4, center[1] - size // 3, bar_width, size * 2 // 3))
                pygame.draw.rect(surface, color, (center[0] + size // 4 - bar_width, center[1] - size // 3, bar_width, size * 2 // 3))
            elif self.icon_type == IconType.STOP:
                # Square
                square_size = size // 2
                square_rect = pygame.Rect(center[0] - square_size // 2, center[1] - square_size // 2, square_size, square_size)
                pygame.draw.rect(surface, color, square_rect)
        
        elif self.icon_type in [IconType.UP, IconType.DOWN, IconType.LEFT, IconType.RIGHT, 
                                IconType.ARROW_UP, IconType.ARROW_DOWN, IconType.ARROW_LEFT, IconType.ARROW_RIGHT]:
            # Arrows
            arrow_size = size // 3
            
            if self.icon_type in [IconType.UP, IconType.ARROW_UP]:
                points = [
                    (center[0], center[1] - arrow_size),
                    (center[0] - arrow_size // 2, center[1] + arrow_size // 2),
                    (center[0] + arrow_size // 2, center[1] + arrow_size // 2)
                ]
            elif self.icon_type in [IconType.DOWN, IconType.ARROW_DOWN]:
                points = [
                    (center[0], center[1] + arrow_size),
                    (center[0] - arrow_size // 2, center[1] - arrow_size // 2),
                    (center[0] + arrow_size // 2, center[1] - arrow_size // 2)
                ]
            elif self.icon_type in [IconType.LEFT, IconType.ARROW_LEFT]:
                points = [
                    (center[0] - arrow_size, center[1]),
                    (center[0] + arrow_size // 2, center[1] - arrow_size // 2),
                    (center[0] + arrow_size // 2, center[1] + arrow_size // 2)
                ]
            else:  # RIGHT
                points = [
                    (center[0] + arrow_size, center[1]),
                    (center[0] - arrow_size // 2, center[1] - arrow_size // 2),
                    (center[0] - arrow_size // 2, center[1] + arrow_size // 2)
                ]
            
            pygame.draw.polygon(surface, color, points)
        
        elif self.icon_type in [IconType.CHECK, IconType.CROSS]:
            # Checkmark or X
            if self.icon_type == IconType.CHECK:
                points = [
                    (center[0] - size // 4, center[1]),
                    (center[0] - size // 8, center[1] + size // 8),
                    (center[0] + size // 4, center[1] - size // 6)
                ]
                pygame.draw.lines(surface, color, False, points, 3)
            else:
                offset = size // 4
                pygame.draw.line(surface, color, (center[0] - offset, center[1] - offset), (center[0] + offset, center[1] + offset), 3)
                pygame.draw.line(surface, color, (center[0] + offset, center[1] - offset), (center[0] - offset, center[1] + offset), 3)
        
        else:
            # Default: draw a simple square
            square_size = size // 2
            square_rect = pygame.Rect(center[0] - square_size // 2, center[1] - square_size // 2, square_size, square_size)
            pygame.draw.rect(surface, color, square_rect, 2)
    
    def _render_icon(self) -> pygame.Surface:
        """Render icon to surface."""
        surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        color = self._get_icon_color()
        
        self._draw_icon_shape(surface, color)
        
        # Apply rotation if needed
        if self.rotation != 0:
            surface = pygame.transform.rotate(surface, self.rotation)
        
        return surface
    
    def _update_component(self, dt: float) -> None:
        """Update icon rendering if needed."""
        pass
    
    def _handle_own_event(self, event: pygame.event.Event) -> EventResult:
        """Icons don't handle events."""
        return EventResult(handled=False)
    
    def _draw_self(self, screen: pygame.Surface) -> None:
        """Draw icon."""
        # Render icon if needed
        if self._needs_redraw or self._icon_surface is None:
            self._icon_surface = self._render_icon()
            self._needs_redraw = False
        
        if self._icon_surface is None:
            return
        
        # Center icon in rect
        icon_rect = self._icon_surface.get_rect(center=self.rect.center)
        screen.blit(self._icon_surface, icon_rect)
