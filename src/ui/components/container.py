"""
Container components for layout management.
"""

import pygame
from typing import Optional, List, Tuple
from .base_component import BaseComponent


class Container(BaseComponent):
    """Container component that holds other components."""
    
    def __init__(self, rect: pygame.Rect, manager=None, layout_type: str = 'vertical'):
        """Initialize container.
        
        Args:
            rect: Container position and size
            manager: pygame_gui UIManager
            layout_type: 'vertical', 'horizontal', or 'grid'
        """
        super().__init__(rect, manager)
        self.layout_type = layout_type
        self.padding = 10
        self.spacing = 5
        self.scroll_offset = 0
        self.scrollable = False
        self.content_height = 0
        
    def render(self, surface: pygame.Surface) -> None:
        """Render container and children."""
        if not self.visible:
            return
            
        # Create clipping region for container
        clip_rect = self.get_absolute_rect()
        surface.set_clip(clip_rect)
        
        # Apply scroll offset to children rendering
        original_positions = []
        for child in self.children:
            original_positions.append(child.rect.copy())
            if self.scrollable:
                child.rect.y -= self.scroll_offset
                
        # Render children
        for child in self.children:
            if child.visible:
                child.render(surface)
                
        # Restore original positions
        for i, child in enumerate(self.children):
            child.rect = original_positions[i]
            
        # Reset clipping
        surface.set_clip(None)
        
    def add_child(self, child: 'BaseComponent') -> None:
        """Add child and update layout."""
        super().add_child(child)
        self._update_layout()
        
    def _update_layout(self) -> None:
        """Update child positions based on layout type."""
        if self.layout_type == 'vertical':
            self._update_vertical_layout()
        elif self.layout_type == 'horizontal':
            self._update_horizontal_layout()
        elif self.layout_type == 'grid':
            self._update_grid_layout()
            
    def _update_vertical_layout(self) -> None:
        """Update vertical layout."""
        y = self.padding
        for child in self.children:
            child.rect.x = self.padding
            child.rect.y = y
            y += child.rect.height + self.spacing
            
        self.content_height = y - self.spacing + self.padding
        
    def _update_horizontal_layout(self) -> None:
        """Update horizontal layout."""
        x = self.padding
        for child in self.children:
            child.rect.x = x
            child.rect.y = self.padding
            x += child.rect.width + self.spacing
            
    def _update_grid_layout(self, columns: int = 2) -> None:
        """Update grid layout."""
        x, y = self.padding, self.padding
        col = 0
        
        for child in self.children:
            child.rect.x = x
            child.rect.y = y
            col += 1
            
            if col >= columns:
                col = 0
                y += self.children[0].rect.height + self.spacing
                x = self.padding
            else:
                x += self.children[0].rect.width + self.spacing
                
    def scroll_up(self, amount: int = 30) -> None:
        """Scroll up."""
        if self.scrollable and self.scroll_offset > 0:
            self.scroll_offset = max(0, self.scroll_offset - amount)
            
    def scroll_down(self, amount: int = 30) -> None:
        """Scroll down."""
        if self.scrollable:
            max_scroll = max(0, self.content_height - self.rect.height)
            self.scroll_offset = min(max_scroll, self.scroll_offset + amount)
            
    def set_scrollable(self, scrollable: bool) -> None:
        """Enable/disable scrolling."""
        self.scrollable = scrollable
        if scrollable:
            self._update_layout()  # Recalculate content height


class ScrollableContainer(Container):
    """Specialized scrollable container."""
    
    def __init__(self, rect: pygame.Rect, manager=None):
        super().__init__(rect, manager, 'vertical')
        self.scrollable = True
        self.scrollbar_width = 12
        self.scrollbar_color = (200, 200, 200)
        self.scrollbar_thumb_color = (150, 150, 150)
        
    def render(self, surface: pygame.Surface) -> None:
        """Render scrollable container with scrollbar."""
        if not self.visible:
            return
            
        # Render container content
        super().render(surface)
        
        # Render scrollbar if needed
        if self.content_height > self.rect.height:
            self._render_scrollbar(surface)
            
    def _render_scrollbar(self, surface: pygame.Surface) -> None:
        """Render scrollbar."""
        abs_rect = self.get_absolute_rect()
        
        # Scrollbar background
        scrollbar_x = abs_rect.right - self.scrollbar_width
        scrollbar_rect = pygame.Rect(
            scrollbar_x, abs_rect.y, 
            self.scrollbar_width, abs_rect.height
        )
        pygame.draw.rect(surface, self.scrollbar_color, scrollbar_rect, border_radius=6)
        
        # Scrollbar thumb
        if self.content_height > 0:
            thumb_ratio = abs_rect.height / self.content_height
            thumb_height = max(30, int(abs_rect.height * thumb_ratio))
            thumb_y = abs_rect.y + int(
                (self.scroll_offset / (self.content_height - abs_rect.height)) 
                * (abs_rect.height - thumb_height)
            )
            
            thumb_rect = pygame.Rect(
                scrollbar_x, thumb_y,
                self.scrollbar_width, thumb_height
            )
            pygame.draw.rect(surface, self.scrollbar_thumb_color, thumb_rect, border_radius=6)
            
    def _handle_component_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse wheel scrolling."""
        if event.type == pygame.MOUSEWHEEL:
            if event.y > 0:  # Scroll up
                self.scroll_up()
            elif event.y < 0:  # Scroll down
                self.scroll_down()
            return True
        return False
