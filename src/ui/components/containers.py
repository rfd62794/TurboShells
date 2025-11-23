"""
Specialized container components for common UI patterns.

This module provides high-level container components that implement common
UI patterns like panels, tabs, and scrollable areas with proper SRP.
"""

import pygame
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum

from .base import ContainerComponent, InteractiveComponent, EventResult
from .style import Style, StyleManager
from ..layout.types import LayoutType, Alignment
from ..layout.container import Container


class TabState(Enum):
    """Tab state enumeration."""
    NORMAL = "normal"
    HOVER = "hover"
    ACTIVE = "active"
    DISABLED = "disabled"


@dataclass
class TabInfo:
    """Information about a tab."""
    id: str
    title: str
    content: Optional[ContainerComponent] = None
    enabled: bool = True
    tooltip: str = ""


class Panel(ContainerComponent):
    """
    Generic panel container with title and border.
    
    Responsibility: Provide a styled container with optional title.
    """
    
    def __init__(
        self, 
        rect: pygame.Rect, 
        title: str = "", 
        style: Optional[Style] = None,
        component_id: str = ""
    ):
        super().__init__(rect, style, component_id)
        self.title = title
        self.title_height = 30 if title else 0
        self.content_area = self._calculate_content_area()
        
        # Panel-specific styling
        self.show_border = True
        self.show_title = bool(title)
        self.title_alignment = Alignment.CENTER
        
        # Update layout for content area
        self.set_layout_type(LayoutType.VERTICAL)
    
    def _calculate_content_area(self) -> pygame.Rect:
        """Calculate content area excluding title and padding."""
        content_rect = pygame.Rect(
            self.rect.x + self.padding,
            self.rect.y + self.padding + self.title_height,
            self.rect.width - 2 * self.padding,
            self.rect.height - 2 * self.padding - self.title_height
        )
        return content_rect
    
    def set_title(self, title: str) -> None:
        """Set panel title."""
        self.title = title
        self.show_title = bool(title)
        self.title_height = 30 if title else 0
        self.content_area = self._calculate_content_area()
        self.mark_layout_dirty()
    
    def _recalculate_layout(self) -> None:
        """Recalculate layout for children within content area."""
        if not self.children:
            return
        
        # Update content area
        self.content_area = self._calculate_content_area()
        
        # Position children within content area
        y_offset = self.content_area.y
        
        for child in self.children:
            if not child.visible:
                continue
            
            # Position child
            child.rect.x = self.content_area.x
            child.rect.y = y_offset
            
            # Ensure child fits within content area
            child.rect.width = min(child.rect.width, self.content_area.width)
            
            y_offset += child.rect.height + self.spacing
    
    def _draw_self(self, screen: pygame.Surface) -> None:
        """Draw panel background, border, and title."""
        # Draw background
        pygame.draw.rect(screen, self.style.get_color("panel"), self.rect)
        
        # Draw border
        if self.show_border:
            pygame.draw.rect(screen, self.style.get_color("border"), self.rect, self.style.border_width)
        
        # Draw title background
        if self.show_title:
            title_rect = pygame.Rect(
                self.rect.x,
                self.rect.y,
                self.rect.width,
                self.title_height
            )
            pygame.draw.rect(screen, self.style.get_color("surface"), title_rect)
            
            # Draw title text
            title_font = self.style.get_font("large")
            title_surface = title_font.render(self.title, True, self.style.get_color("text"))
            
            # Position title based on alignment
            if self.title_alignment == Alignment.CENTER:
                title_rect = title_surface.get_rect(centerx=self.rect.centerx, centery=self.rect.y + self.title_height // 2)
            elif self.title_alignment == Alignment.END:
                title_rect = title_surface.get_rect(right=self.rect.right - self.padding, centery=self.rect.y + self.title_height // 2)
            else:  # START
                title_rect = title_surface.get_rect(left=self.rect.x + self.padding, centery=self.rect.y + self.title_height // 2)
            
            screen.blit(title_surface, title_rect)
            
            # Draw title separator line
            pygame.draw.line(
                screen,
                self.style.get_color("border"),
                (self.rect.x, self.rect.y + self.title_height),
                (self.rect.right, self.rect.y + self.title_height),
                self.style.border_width
            )


class TabContainer(InteractiveComponent):
    """
    Tab navigation container.
    
    Responsibility: Manage tab selection and navigation.
    """
    
    def __init__(
        self, 
        rect: pygame.Rect, 
        tabs: List[str], 
        style: Optional[Style] = None,
        component_id: str = ""
    ):
        super().__init__(rect, style, component_id)
        
        # Tab configuration
        self.tabs: List[TabInfo] = []
        self.active_tab = 0
        self.tab_height = 30
        
        # Create tab info from string list
        for i, tab_title in enumerate(tabs):
            self.tabs.append(TabInfo(id=f"tab_{i}", title=tab_title))
        
        # Calculate tab widths
        self.tab_widths = self._calculate_tab_widths()
        
        # Event callbacks
        self.on_tab_change: Optional[Callable[[int], None]] = None
        
        # Interaction state
        self._hovered_tab = -1
        self._pressed_tab = -1
    
    def add_tab(self, title: str, content: Optional[ContainerComponent] = None) -> int:
        """
        Add a new tab.
        
        Args:
            title: Tab title
            content: Optional content component
            
        Returns:
            Index of added tab
        """
        tab_id = f"tab_{len(self.tabs)}"
        tab_info = TabInfo(id=tab_id, title=title, content=content)
        self.tabs.append(tab_info)
        
        # Recalculate tab widths
        self.tab_widths = self._calculate_tab_widths()
        
        return len(self.tabs) - 1
    
    def remove_tab(self, index: int) -> None:
        """
        Remove a tab.
        
        Args:
            index: Tab index to remove
        """
        if 0 <= index < len(self.tabs):
            del self.tabs[index]
            
            # Adjust active tab if necessary
            if self.active_tab >= len(self.tabs):
                self.active_tab = max(0, len(self.tabs) - 1)
            
            # Recalculate tab widths
            self.tab_widths = self._calculate_tab_widths()
    
    def set_active_tab(self, index: int) -> None:
        """
        Set active tab by index.
        
        Args:
            index: Tab index to activate
        """
        if 0 <= index < len(self.tabs) and self.tabs[index].enabled:
            old_tab = self.active_tab
            self.active_tab = index
            
            if old_tab != index and self.on_tab_change:
                self.on_tab_change(index)
    
    def get_active_tab(self) -> int:
        """Get current active tab index."""
        return self.active_tab
    
    def get_tab_content(self, index: int) -> Optional[ContainerComponent]:
        """Get content component for tab."""
        if 0 <= index < len(self.tabs):
            return self.tabs[index].content
        return None
    
    def _calculate_tab_widths(self) -> List[int]:
        """Calculate responsive tab widths."""
        if not self.tabs:
            return []
        
        # Get font for text measurement
        font = self.style.get_font("small")
        
        # Calculate minimum widths
        min_widths = []
        for tab in self.tabs:
            text_width = font.size(tab.title)[0] + 20  # Add padding
            min_widths.append(text_width)
        
        # Calculate equal distribution
        available_width = self.rect.width
        spacing = 5
        total_spacing = spacing * (len(self.tabs) - 1)
        available_for_tabs = available_width - total_spacing
        
        equal_width = available_for_tabs // len(self.tabs)
        
        # Check if equal distribution works
        if all(min_width <= equal_width for min_width in min_widths):
            return [equal_width] * len(self.tabs)
        
        # Use minimum widths
        return min_widths
    
    def _get_tab_rect(self, index: int) -> pygame.Rect:
        """Get rectangle for specific tab."""
        if index < 0 or index >= len(self.tabs):
            return pygame.Rect(0, 0, 0, 0)
        
        x_offset = self.rect.x
        for i in range(index):
            x_offset += self.tab_widths[i] + 5  # spacing
        
        return pygame.Rect(
            x_offset,
            self.rect.y,
            self.tab_widths[index],
            self.tab_height
        )
    
    def _get_tab_at_position(self, pos: Tuple[int, int]) -> int:
        """Get tab index at mouse position."""
        for i in range(len(self.tabs)):
            tab_rect = self._get_tab_rect(i)
            if tab_rect.collidepoint(pos):
                return i
        return -1
    
    def _update_hover_state(self) -> None:
        """Update hover state for tabs."""
        mouse_pos = pygame.mouse.get_pos()
        self._hovered_tab = self._get_tab_at_position(mouse_pos)
    
    def _handle_own_event(self, event: pygame.event.Event) -> EventResult:
        """Handle tab-specific events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            tab_index = self._get_tab_at_position(event.pos)
            if tab_index >= 0 and self.tabs[tab_index].enabled:
                self._pressed_tab = tab_index
                return EventResult(handled=True)
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._pressed_tab >= 0:
                tab_index = self._get_tab_at_position(event.pos)
                if tab_index == self._pressed_tab:
                    self.set_active_tab(tab_index)
                self._pressed_tab = -1
                return EventResult(handled=True)
        
        return EventResult(handled=False)
    
    def _update_component(self, dt: float) -> None:
        """Update tab hover state."""
        self._update_hover_state()
    
    def _draw_self(self, screen: pygame.Surface) -> None:
        """Draw tab bar and tabs."""
        # Draw tab bar background
        pygame.draw.rect(screen, self.style.get_color("surface"), self.rect)
        
        # Draw tabs
        font = self.style.get_font("small")
        
        for i, tab in enumerate(self.tabs):
            tab_rect = self._get_tab_rect(i)
            
            # Determine tab state and color
            if i == self.active_tab:
                color = self.style.get_color("tab_active")
                text_color = self.style.get_color("text")
            elif not tab.enabled:
                color = self.style.get_color("button_disabled")
                text_color = self.style.get_color("text_disabled")
            elif i == self._hovered_tab:
                color = self.style.get_color("tab_hover")
                text_color = self.style.get_color("text")
            else:
                color = self.style.get_color("tab")
                text_color = self.style.get_color("text")
            
            # Draw tab background
            pygame.draw.rect(screen, color, tab_rect)
            
            # Draw tab border
            border_color = self.style.get_color("border_active") if i == self.active_tab else self.style.get_color("border")
            pygame.draw.rect(screen, border_color, tab_rect, self.style.border_width)
            
            # Draw tab text
            text_surface = font.render(tab.title, True, text_color)
            text_rect = text_surface.get_rect(center=tab_rect.center)
            screen.blit(text_surface, text_rect)
        
        # Draw bottom border for tab bar
        pygame.draw.line(
            screen,
            self.style.get_color("border"),
            (self.rect.x, self.rect.bottom - 1),
            (self.rect.right, self.rect.bottom - 1),
            self.style.border_width
        )


class ScrollContainer(ContainerComponent):
    """
    Scrollable content container.
    
    Responsibility: Manage scrolling for content that exceeds container bounds.
    """
    
    def __init__(
        self, 
        rect: pygame.Rect, 
        content_height: int = 0,
        style: Optional[Style] = None,
        component_id: str = ""
    ):
        super().__init__(rect, style, component_id)
        
        # Scrolling state
        self.content_height = content_height
        self.scroll_offset = 0
        self.scrollbar_width = 20
        self.scrollbar_visible = True
        
        # Interaction state
        self._scrolling = False
        self._scroll_start_y = 0
        self._scroll_start_offset = 0
        self._hovered_scrollbar = False
        
        # Update content area
        self.content_area = self._calculate_content_area()
    
    def set_content_height(self, height: int) -> None:
        """Set total content height."""
        self.content_height = height
        self._update_scrollbar_visibility()
    
    def set_scroll_offset(self, offset: int) -> None:
        """Set scroll offset."""
        max_offset = max(0, self.content_height - self.content_area.height)
        self.scroll_offset = max(0, min(offset, max_offset))
    
    def scroll_by(self, delta: int) -> None:
        """Scroll by relative amount."""
        self.set_scroll_offset(self.scroll_offset + delta)
    
    def scroll_to_top(self) -> None:
        """Scroll to top."""
        self.scroll_offset = 0
    
    def scroll_to_bottom(self) -> None:
        """Scroll to bottom."""
        if self.content_height > self.content_area.height:
            self.scroll_offset = self.content_height - self.content_area.height
    
    def _calculate_content_area(self) -> pygame.Rect:
        """Calculate content area excluding scrollbar."""
        scrollbar_width = self.scrollbar_width if self.scrollbar_visible else 0
        
        return pygame.Rect(
            self.rect.x + self.padding,
            self.rect.y + self.padding,
            self.rect.width - 2 * self.padding - scrollbar_width,
            self.rect.height - 2 * self.padding
        )
    
    def _update_scrollbar_visibility(self) -> None:
        """Update scrollbar visibility based on content size."""
        self.scrollbar_visible = self.content_height > self.content_area.height
        self.content_area = self._calculate_content_area()
    
    def _get_scrollbar_rect(self) -> pygame.Rect:
        """Get scrollbar rectangle."""
        if not self.scrollbar_visible:
            return pygame.Rect(0, 0, 0, 0)
        
        # Calculate scrollbar height
        available_height = self.content_area.height
        scrollbar_height = max(20, int(available_height * available_height / self.content_height))
        
        # Calculate scrollbar position
        if self.content_height > available_height:
            scroll_ratio = self.scroll_offset / (self.content_height - available_height)
            scrollbar_y = self.content_area.y + int(scroll_ratio * (available_height - scrollbar_height))
        else:
            scrollbar_y = self.content_area.y
        
        return pygame.Rect(
            self.content_area.right,
            scrollbar_y,
            self.scrollbar_width,
            scrollbar_height
        )
    
    def _recalculate_layout(self) -> None:
        """Recalculate layout for children with scroll offset."""
        if not self.children:
            return
        
        # Update scrollbar visibility
        self._update_scrollbar_visibility()
        
        # Position children vertically with scroll offset
        y_offset = self.content_area.y - self.scroll_offset
        
        for child in self.children:
            if not child.visible:
                continue
            
            # Position child
            child.rect.x = self.content_area.x
            child.rect.y = y_offset
            
            # Ensure child fits within content area width
            child.rect.width = min(child.rect.width, self.content_area.width)
            
            y_offset += child.rect.height + self.spacing
    
    def _handle_own_event(self, event: pygame.event.Event) -> EventResult:
        """Handle scrolling events."""
        if not self.scrollbar_visible:
            return EventResult(handled=False)
        
        scrollbar_rect = self._get_scrollbar_rect()
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if scrollbar_rect.collidepoint(event.pos):
                self._scrolling = True
                self._scroll_start_y = event.pos[1]
                self._scroll_start_offset = self.scroll_offset
                return EventResult(handled=True)
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._scrolling:
                self._scrolling = False
                return EventResult(handled=True)
        
        elif event.type == pygame.MOUSEMOTION:
            if self._scrolling:
                # Calculate new scroll offset
                delta_y = event.pos[1] - self._scroll_start_y
                available_height = self.content_area.height
                scrollbar_height = scrollbar_rect.height
                
                if scrollbar_height > 0:
                    scroll_ratio = delta_y / (available_height - scrollbar_height)
                    max_offset = self.content_height - available_height
                    new_offset = self._scroll_start_offset + int(scroll_ratio * max_offset)
                    self.set_scroll_offset(new_offset)
                
                return EventResult(handled=True)
        
        elif event.type == pygame.MOUSEWHEEL:
            # Handle mouse wheel scrolling
            self.scroll_by(-event.y * 20)  # Negative because pygame wheel is inverted
            return EventResult(handled=True)
        
        return EventResult(handled=False)
    
    def _update_component(self, dt: float) -> None:
        """Update scrollbar hover state."""
        if self.scrollbar_visible:
            mouse_pos = pygame.mouse.get_pos()
            scrollbar_rect = self._get_scrollbar_rect()
            self._hovered_scrollbar = scrollbar_rect.collidepoint(mouse_pos)
    
    def _draw_self(self, screen: pygame.Surface) -> None:
        """Draw container and scrollbar."""
        # Draw background
        pygame.draw.rect(screen, self.style.get_color("panel"), self.rect)
        
        # Draw border
        pygame.draw.rect(screen, self.style.get_color("border"), self.rect, self.style.border_width)
        
        # Draw content area background
        pygame.draw.rect(screen, self.style.get_color("background"), self.content_area)
        
        # Draw scrollbar if visible
        if self.scrollbar_visible:
            scrollbar_rect = self._get_scrollbar_rect()
            
            # Draw scrollbar track
            track_rect = pygame.Rect(
                scrollbar_rect.x,
                self.content_area.y,
                self.scrollbar_width,
                self.content_area.height
            )
            pygame.draw.rect(screen, self.style.get_color("surface"), track_rect)
            
            # Draw scrollbar handle
            if self._hovered_scrollbar or self._scrolling:
                color = self.style.get_color("button_hover")
            else:
                color = self.style.get_color("button")
            
            pygame.draw.rect(screen, color, scrollbar_rect)
            pygame.draw.rect(screen, self.style.get_color("border"), scrollbar_rect, 1)
        
        # Set clipping rect for content
        screen.set_clip(self.content_area)
    
    def get_scroll_percentage(self) -> float:
        """Get current scroll position as percentage."""
        if self.content_height <= self.content_area.height:
            return 0.0
        return self.scroll_offset / (self.content_height - self.content_area.height)
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about scroll container."""
        info = super().get_debug_info()
        info.update({
            "content_height": self.content_height,
            "scroll_offset": self.scroll_offset,
            "scrollbar_visible": self.scrollbar_visible,
            "scroll_percentage": self.get_scroll_percentage(),
            "content_area": str(self.content_area)
        })
        return info
