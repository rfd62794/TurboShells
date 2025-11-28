"""
Reusable layout components for organizing UI elements.
"""

import pygame
import pygame_gui
from typing import Optional, Dict, Any, List, Union, Tuple
from ..base_component import BaseComponent


class Container(BaseComponent):
    """Basic container for organizing child components."""
    
    def __init__(self, rect: pygame.Rect, manager=None, config: Optional[Dict] = None):
        """Initialize container.
        
        Args:
            rect: Container position and size
            manager: pygame_gui UIManager
            config: Configuration options
        """
        super().__init__(rect, manager)
        self.config = config or {}
        
        # Layout options
        self.padding = self.config.get('padding', 10)
        self.spacing = self.config.get('spacing', 5)
        self.background_color = self.config.get('background_color', None)
        self.border_color = self.config.get('border_color', None)
        self.border_width = self.config.get('border_width', 0)
        
        # Layout type
        self.layout_type = self.config.get('layout_type', 'vertical')  # vertical, horizontal, grid
        self.grid_columns = self.config.get('grid_columns', 2)
        
    def render(self, surface: pygame.Surface) -> None:
        """Render container and children."""
        if not self.visible:
            return
            
        abs_rect = self.get_absolute_rect()
        
        # Draw background
        if self.background_color:
            pygame.draw.rect(surface, self.background_color, abs_rect)
            
        # Draw border
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, abs_rect, self.border_width)
            
        # Render children
        for child in self.children:
            if child.visible:
                child.render(surface)
                
    def add_child(self, child: 'BaseComponent') -> None:
        """Add child and update layout."""
        super().add_child(child)
        self._update_layout()
        
    def _update_layout(self) -> None:
        """Update child positions based on layout type."""
        if self.layout_type == 'vertical':
            self._vertical_layout()
        elif self.layout_type == 'horizontal':
            self._horizontal_layout()
        elif self.layout_type == 'grid':
            self._grid_layout()
            
    def _vertical_layout(self) -> None:
        """Arrange children vertically."""
        x = self.padding
        y = self.padding
        
        for child in self.children:
            child.rect.x = x
            child.rect.y = y
            y += child.rect.height + self.spacing
            
    def _horizontal_layout(self) -> None:
        """Arrange children horizontally."""
        x = self.padding
        y = self.padding
        
        for child in self.children:
            child.rect.x = x
            child.rect.y = y
            x += child.rect.width + self.spacing
            
    def _grid_layout(self) -> None:
        """Arrange children in a grid."""
        x = self.padding
        y = self.padding
        col = 0
        
        for child in self.children:
            child.rect.x = x
            child.rect.y = y
            col += 1
            
            if col >= self.grid_columns:
                col = 0
                y += self.children[0].rect.height + self.spacing
                x = self.padding
            else:
                x += self.children[0].rect.width + self.spacing


class ScrollContainer(Container):
    """Container with scrolling support."""
    
    def __init__(self, rect: pygame.Rect, manager=None, config: Optional[Dict] = None):
        """Initialize scroll container.
        
        Args:
            rect: Container position and size
            manager: pygame_gui UIManager
            config: Configuration options
        """
        super().__init__(rect, manager, config)
        
        # Scrolling options
        self.scroll_offset = 0
        self.scrollable = self.config.get('scrollable', True)
        self.show_scrollbar = self.config.get('show_scrollbar', True)
        self.scrollbar_width = self.config.get('scrollbar_width', 12)
        self.scroll_step = self.config.get('scroll_step', 30)
        
        # Content tracking
        self.content_height = 0
        self.max_scroll = 0
        
        # Scrollbar colors
        self.scrollbar_color = self.config.get('scrollbar_color', (200, 200, 200))
        self.scrollbar_thumb_color = self.config.get('scrollbar_thumb_color', (150, 150, 150))
        
    def render(self, surface: pygame.Surface) -> None:
        """Render scroll container with clipping."""
        if not self.visible:
            return
            
        abs_rect = self.get_absolute_rect()
        
        # Set clipping region
        surface.set_clip(abs_rect)
        
        # Apply scroll offset to children
        original_positions = []
        for child in self.children:
            original_positions.append(child.rect.copy())
            child.rect.y -= self.scroll_offset
            
        # Render background and border
        if self.background_color:
            pygame.draw.rect(surface, self.background_color, abs_rect)
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, abs_rect, self.border_width)
            
        # Render children
        for child in self.children:
            if child.visible:
                child.render(surface)
                
        # Restore original positions
        for i, child in enumerate(self.children):
            child.rect = original_positions[i]
            
        # Reset clipping
        surface.set_clip(None)
        
        # Draw scrollbar if needed
        if self.show_scrollbar and self.scrollable and self.content_height > abs_rect.height:
            self._draw_scrollbar(surface)
            
    def _draw_scrollbar(self, surface: pygame.Surface) -> None:
        """Draw scrollbar."""
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
                (self.scroll_offset / self.max_scroll) * (abs_rect.height - thumb_height)
            )
            
            thumb_rect = pygame.Rect(
                scrollbar_x, thumb_y,
                self.scrollbar_width, thumb_height
            )
            pygame.draw.rect(surface, self.scrollbar_thumb_color, thumb_rect, border_radius=6)
            
    def _handle_component_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse wheel scrolling."""
        if event.type == pygame.MOUSEWHEEL and self.scrollable:
            if event.y > 0:  # Scroll up
                self.scroll_up()
            elif event.y < 0:  # Scroll down
                self.scroll_down()
            return True
        return False
        
    def _update_layout(self) -> None:
        """Update layout and scroll limits."""
        super()._update_layout()
        
        # Calculate content height
        self.content_height = 0
        for child in self.children:
            child_bottom = child.rect.y + child.rect.height
            self.content_height = max(self.content_height, child_bottom)
        self.content_height += self.padding
        
        # Update max scroll
        abs_rect = self.get_absolute_rect()
        self.max_scroll = max(0, self.content_height - abs_rect.height)
        
        # Ensure scroll offset is within bounds
        self.scroll_offset = min(self.scroll_offset, self.max_scroll)
        
    def scroll_up(self, amount: Optional[int] = None) -> None:
        """Scroll up."""
        if amount is None:
            amount = self.scroll_step
        self.scroll_offset = max(0, self.scroll_offset - amount)
        
    def scroll_down(self, amount: Optional[int] = None) -> None:
        """Scroll down."""
        if amount is None:
            amount = self.scroll_step
        self.scroll_offset = min(self.max_scroll, self.scroll_offset + amount)
        
    def set_scroll_offset(self, offset: int) -> None:
        """Set scroll offset."""
        self.scroll_offset = max(0, min(self.max_scroll, offset))
        
    def get_scroll_offset(self) -> int:
        """Get current scroll offset."""
        return self.scroll_offset


class GridContainer(Container):
    """Container with grid layout support."""
    
    def __init__(self, rect: pygame.Rect, columns: int = 2, manager=None, config: Optional[Dict] = None):
        """Initialize grid container.
        
        Args:
            rect: Container position and size
            columns: Number of grid columns
            manager: pygame_gui UIManager
            config: Configuration options
        """
        super().__init__(rect, manager, config)
        self.columns = columns
        self.layout_type = 'grid'
        self.grid_columns = columns
        
        # Grid options
        self.cell_width = self.config.get('cell_width', None)
        self.cell_height = self.config.get('cell_height', None)
        self.horizontal_spacing = self.config.get('horizontal_spacing', self.spacing)
        self.vertical_spacing = self.config.get('vertical_spacing', self.spacing)
        
    def _grid_layout(self) -> None:
        """Arrange children in a grid with automatic sizing."""
        if not self.children:
            return
            
        # Calculate cell sizes if not specified
        if self.cell_width is None:
            available_width = self.rect.width - (self.padding * 2) - ((self.columns - 1) * self.horizontal_spacing)
            self.cell_width = available_width // self.columns
            
        if self.cell_height is None:
            # Use height of first child as reference
            self.cell_height = self.children[0].rect.height
            
        # Position children in grid
        row = 0
        col = 0
        x = self.padding
        y = self.padding
        
        for child in self.children:
            # Set child position and size
            child.rect.x = x
            child.rect.y = y
            
            if self.cell_width:
                child.rect.width = self.cell_width
            if self.cell_height:
                child.rect.height = self.cell_height
                
            # Move to next position
            col += 1
            if col >= self.columns:
                col = 0
                row += 1
                x = self.padding
                y += self.cell_height + self.vertical_spacing
            else:
                x += self.cell_width + self.horizontal_spacing


class FlexContainer(Container):
    """Container with flexbox-like layout."""
    
    def __init__(self, rect: pygame.Rect, direction: str = 'row', manager=None, config: Optional[Dict] = None):
        """Initialize flex container.
        
        Args:
            rect: Container position and size
            direction: 'row' or 'column'
            manager: pygame_gui UIManager
            config: Configuration options
        """
        super().__init__(rect, manager, config)
        self.direction = direction
        self.layout_type = 'flex'
        
        # Flex options
        self.justify_content = self.config.get('justify_content', 'flex-start')  # flex-start, center, flex-end, space-between, space-around
        self.align_items = self.config.get('align_items', 'stretch')  # flex-start, center, flex-end, stretch
        self.wrap = self.config.get('wrap', False)  # nowrap, wrap
        
    def _update_layout(self) -> None:
        """Update layout using flexbox principles."""
        if self.direction == 'row':
            self._flex_row_layout()
        else:
            self._flex_column_layout()
            
    def _flex_row_layout(self) -> None:
        """Arrange children in a row with flex behavior."""
        if not self.children:
            return
            
        # Calculate total width of children
        total_width = sum(child.rect.width for child in self.children)
        total_spacing = (len(self.children) - 1) * self.spacing
        available_width = self.rect.width - (self.padding * 2)
        
        # Calculate spacing based on justify_content
        if self.justify_content == 'space-between' and len(self.children) > 1:
            spacing = (available_width - total_width) / (len(self.children) - 1)
        elif self.justify_content == 'space-around':
            spacing = (available_width - total_width) / len(self.children)
        else:
            spacing = self.spacing
            
        # Position children
        x = self._get_start_x(total_width, total_spacing)
        y = self._get_start_y()
        
        for child in self.children:
            child.rect.x = x
            child.rect.y = y
            x += child.rect.width + spacing
            
    def _flex_column_layout(self) -> None:
        """Arrange children in a column with flex behavior."""
        if not self.children:
            return
            
        # Calculate total height of children
        total_height = sum(child.rect.height for child in self.children)
        total_spacing = (len(self.children) - 1) * self.spacing
        available_height = self.rect.height - (self.padding * 2)
        
        # Calculate spacing based on justify_content
        if self.justify_content == 'space-between' and len(self.children) > 1:
            spacing = (available_height - total_height) / (len(self.children) - 1)
        elif self.justify_content == 'space-around':
            spacing = (available_height - total_height) / len(self.children)
        else:
            spacing = self.spacing
            
        # Position children
        x = self._get_start_x()
        y = self._get_start_y(total_height, total_spacing)
        
        for child in self.children:
            child.rect.x = x
            child.rect.y = y
            y += child.rect.height + spacing
            
    def _get_start_x(self, total_width: int = 0, total_spacing: int = 0) -> int:
        """Get starting x position based on justify_content."""
        available_width = self.rect.width - (self.padding * 2)
        
        if self.justify_content == 'center':
            return self.padding + (available_width - total_width - total_spacing) // 2
        elif self.justify_content == 'flex-end':
            return self.padding + (available_width - total_width - total_spacing)
        else:  # flex-start or space-between/space-around
            return self.padding
            
    def _get_start_y(self, total_height: int = 0, total_spacing: int = 0) -> int:
        """Get starting y position based on align_items."""
        available_height = self.rect.height - (self.padding * 2)
        
        if self.align_items == 'center':
            return self.padding + (available_height - total_height - total_spacing) // 2
        elif self.align_items == 'flex-end':
            return self.padding + (available_height - total_height - total_spacing)
        else:  # flex-start or stretch
            return self.padding


class Panel(Container):
    """Styled container panel with header."""
    
    def __init__(self, rect: pygame.Rect, title: str = "", manager=None, config: Optional[Dict] = None):
        """Initialize panel.
        
        Args:
            rect: Panel position and size
            title: Panel title
            manager: pygame_gui UIManager
            config: Configuration options
        """
        super().__init__(rect, manager, config)
        self.title = title
        
        # Panel styling
        self.header_height = self.config.get('header_height', 30)
        self.header_color = self.config.get('header_color', (50, 50, 50))
        self.body_color = self.config.get('body_color', (240, 240, 240))
        self.border_color = self.config.get('border_color', (100, 100, 100))
        self.border_width = self.config.get('border_width', 2)
        
        # Header font
        self.font = pygame.font.Font(None, 18)
        self.header_text_color = self.config.get('header_text_color', (255, 255, 255))
        
        # Content area
        self.content_rect = pygame.Rect(
            self.rect.x + self.padding,
            self.rect.y + self.header_height + self.padding,
            self.rect.width - (self.padding * 2),
            self.rect.height - self.header_height - (self.padding * 2)
        )
        
    def render(self, surface: pygame.Surface) -> None:
        """Render panel with header and body."""
        if not self.visible:
            return
            
        abs_rect = self.get_absolute_rect()
        
        # Draw header
        header_rect = pygame.Rect(abs_rect.x, abs_rect.y, abs_rect.width, self.header_height)
        pygame.draw.rect(surface, self.header_color, header_rect)
        
        # Draw header title
        if self.title:
            title_surface = self.font.render(self.title, True, self.header_text_color)
            title_rect = title_surface.get_rect()
            title_rect.left = abs_rect.x + 10
            title_rect.centery = header_rect.centery
            surface.blit(title_surface, title_rect)
            
        # Draw body background
        body_rect = pygame.Rect(
            abs_rect.x, abs_rect.y + self.header_height,
            abs_rect.width, abs_rect.height - self.header_height
        )
        pygame.draw.rect(surface, self.body_color, body_rect)
        
        # Draw border
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, abs_rect, self.border_width)
            
        # Render children in content area
        for child in self.children:
            if child.visible:
                child.render(surface)
                
    def get_content_rect(self) -> pygame.Rect:
        """Get the content area rectangle."""
        return self.content_rect.copy()
        
    def set_title(self, title: str) -> None:
        """Update panel title."""
        self.title = title
