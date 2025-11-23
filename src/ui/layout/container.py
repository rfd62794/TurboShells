"""
Layout container implementation.

This module provides the container classes that implement different layout algorithms
for arranging child components in various patterns.
"""

import pygame
from typing import List, Optional, Dict, Any, Tuple
from abc import ABC, abstractmethod

from .types import (
    LayoutType, Alignment, SizePolicy, Direction, WrapMode,
    LayoutProperties, LayoutMetrics, ContainerLayout, LayoutState,
    LayoutResult, GridPosition, FlexProperties
)
from ..components.base import UIComponent


class LayoutAlgorithm(ABC):
    """Base class for layout algorithms."""
    
    @abstractmethod
    def calculate_layout(
        self, 
        container_rect: pygame.Rect,
        children: List[UIComponent],
        properties: ContainerLayout
    ) -> LayoutResult:
        """
        Calculate layout for children.
        
        Args:
            container_rect: Container rectangle
            children: List of child components
            properties: Container layout properties
            
        Returns:
            Layout calculation result
        """
        pass


class VerticalLayoutAlgorithm(LayoutAlgorithm):
    """Vertical stack layout algorithm."""
    
    def calculate_layout(
        self, 
        container_rect: pygame.Rect,
        children: List[UIComponent],
        properties: ContainerLayout
    ) -> LayoutResult:
        """Calculate vertical layout."""
        try:
            calculated_rects = {}
            y_offset = container_rect.y + properties.item_spacing
            
            for child in children:
                if not child.visible:
                    continue
                
                # Get child's preferred size
                child_rect = child.rect
                
                # Apply horizontal alignment
                if properties.cross_axis_alignment == Alignment.CENTER:
                    child_rect.x = container_rect.centerx - child_rect.width // 2
                elif properties.cross_axis_alignment == Alignment.END:
                    child_rect.x = container_rect.right - child_rect.width - properties.item_spacing
                else:  # START
                    child_rect.x = container_rect.x + properties.item_spacing
                
                # Apply vertical positioning
                child_rect.y = y_offset
                
                calculated_rects[child.component_id] = child_rect
                y_offset += child_rect.height + properties.item_spacing
            
            # Calculate metrics
            total_height = y_offset - container_rect.y
            metrics = LayoutMetrics(
                available_width=container_rect.width,
                available_height=container_rect.height,
                content_width=container_rect.width - 2 * properties.item_spacing,
                content_height=total_height,
                used_width=container_rect.width,
                used_height=total_height,
                remaining_width=0,
                remaining_height=max(0, container_rect.height - total_height)
            )
            
            return LayoutResult(success=True, calculated_rects=calculated_rects, metrics=metrics)
            
        except Exception as e:
            return LayoutResult(success=False, error_message=str(e))


class HorizontalLayoutAlgorithm(LayoutAlgorithm):
    """Horizontal stack layout algorithm."""
    
    def calculate_layout(
        self, 
        container_rect: pygame.Rect,
        children: List[UIComponent],
        properties: ContainerLayout
    ) -> LayoutResult:
        """Calculate horizontal layout."""
        try:
            calculated_rects = {}
            x_offset = container_rect.x + properties.item_spacing
            
            for child in children:
                if not child.visible:
                    continue
                
                child_rect = child.rect
                
                # Apply vertical alignment
                if properties.cross_axis_alignment == Alignment.CENTER:
                    child_rect.y = container_rect.centery - child_rect.height // 2
                elif properties.cross_axis_alignment == Alignment.END:
                    child_rect.y = container_rect.bottom - child_rect.height - properties.item_spacing
                else:  # START
                    child_rect.y = container_rect.y + properties.item_spacing
                
                # Apply horizontal positioning
                child_rect.x = x_offset
                
                calculated_rects[child.component_id] = child_rect
                x_offset += child_rect.width + properties.item_spacing
            
            # Calculate metrics
            total_width = x_offset - container_rect.x
            metrics = LayoutMetrics(
                available_width=container_rect.width,
                available_height=container_rect.height,
                content_width=total_width,
                content_height=container_rect.height - 2 * properties.item_spacing,
                used_width=total_width,
                used_height=container_rect.height,
                remaining_width=max(0, container_rect.width - total_width),
                remaining_height=0
            )
            
            return LayoutResult(success=True, calculated_rects=calculated_rects, metrics=metrics)
            
        except Exception as e:
            return LayoutResult(success=False, error_message=str(e))


class GridLayoutAlgorithm(LayoutAlgorithm):
    """Grid layout algorithm."""
    
    def calculate_layout(
        self, 
        container_rect: pygame.Rect,
        children: List[UIComponent],
        properties: ContainerLayout
    ) -> LayoutResult:
        """Calculate grid layout."""
        try:
            calculated_rects = {}
            
            # Calculate cell dimensions
            cell_width = (container_rect.width - properties.column_gap * (properties.grid_columns - 1)) // properties.grid_columns
            cell_height = (container_rect.height - properties.row_gap * (properties.grid_rows - 1)) // properties.grid_rows
            
            # Create grid map
            grid_map = {}
            for child in children:
                if not child.visible:
                    continue
                
                # Get grid position from child properties or auto-assign
                grid_pos = self._get_grid_position(child, len(grid_map), properties.grid_columns, properties.grid_rows)
                grid_map[grid_pos] = child
            
            # Position children in grid
            for (row, col), child in grid_map.items():
                child_rect = child.rect
                
                # Calculate cell position
                x = container_rect.x + col * (cell_width + properties.column_gap)
                y = container_rect.y + row * (cell_height + properties.row_gap)
                
                # Center child in cell (or stretch if specified)
                if properties.cross_axis_alignment == Alignment.STRETCH:
                    child_rect.width = cell_width
                    child_rect.height = cell_height
                    child_rect.x = x
                    child_rect.y = y
                else:
                    # Center in cell
                    child_rect.x = x + (cell_width - child_rect.width) // 2
                    child_rect.y = y + (cell_height - child_rect.height) // 2
                
                calculated_rects[child.component_id] = child_rect
            
            # Calculate metrics
            metrics = LayoutMetrics(
                available_width=container_rect.width,
                available_height=container_rect.height,
                content_width=container_rect.width,
                content_height=container_rect.height,
                used_width=container_rect.width,
                used_height=container_rect.height,
                remaining_width=0,
                remaining_height=0
            )
            
            return LayoutResult(success=True, calculated_rects=calculated_rects, metrics=metrics)
            
        except Exception as e:
            return LayoutResult(success=False, error_message=str(e))
    
    def _get_grid_position(
        self, 
        child: UIComponent, 
        index: int, 
        max_columns: int, 
        max_rows: int
    ) -> Tuple[int, int]:
        """Get grid position for child."""
        # Try to get position from child properties
        if hasattr(child, 'layout_properties') and child.layout_properties.grid_position:
            pos = child.layout_properties.grid_position
            return (pos.row, pos.column)
        
        # Auto-assign position
        row = index // max_columns
        col = index % max_columns
        
        # Ensure within bounds
        row = min(row, max_rows - 1)
        col = min(col, max_columns - 1)
        
        return (row, col)


class FlexLayoutAlgorithm(LayoutAlgorithm):
    """Flex layout algorithm."""
    
    def calculate_layout(
        self, 
        container_rect: pygame.Rect,
        children: List[UIComponent],
        properties: ContainerLayout
    ) -> LayoutResult:
        """Calculate flex layout."""
        try:
            calculated_rects = {}
            
            # Separate children by visibility
            visible_children = [child for child in children if child.visible]
            if not visible_children:
                return LayoutResult(success=True, calculated_rects={}, metrics=LayoutMetrics(
                    available_width=container_rect.width,
                    available_height=container_rect.height,
                    content_width=0, content_height=0,
                    used_width=0, used_height=0,
                    remaining_width=container_rect.width,
                    remaining_height=container_rect.height
                ))
            
            # Determine main and cross axis
            is_row = properties.flex_direction in [Direction.ROW, Direction.ROW_REVERSE]
            
            # Calculate total flex basis
            total_flex_grow = 0.0
            fixed_space = 0
            
            for child in visible_children:
                flex_props = self._get_flex_properties(child)
                total_flex_grow += flex_props.grow
                
                if flex_props.basis is not None:
                    if is_row:
                        fixed_space += flex_props.basis
                    else:
                        fixed_space += flex_props.basis
                else:
                    if is_row:
                        fixed_space += child.rect.width
                    else:
                        fixed_space += child.rect.height
            
            # Calculate available space for flex items
            if is_row:
                available_space = container_rect.width - properties.item_spacing * (len(visible_children) - 1)
            else:
                available_space = container_rect.height - properties.item_spacing * (len(visible_children) - 1)
            
            remaining_space = max(0, available_space - fixed_space)
            
            # Position children
            if is_row:
                self._layout_flex_row(
                    visible_children, container_rect, properties,
                    remaining_space, total_flex_grow, calculated_rects
                )
            else:
                self._layout_flex_column(
                    visible_children, container_rect, properties,
                    remaining_space, total_flex_grow, calculated_rects
                )
            
            # Calculate metrics
            used_width = max((rect.right for rect in calculated_rects.values()), default=container_rect.x) - container_rect.x
            used_height = max((rect.bottom for rect in calculated_rects.values()), default=container_rect.y) - container_rect.y
            
            metrics = LayoutMetrics(
                available_width=container_rect.width,
                available_height=container_rect.height,
                content_width=used_width,
                content_height=used_height,
                used_width=used_width,
                used_height=used_height,
                remaining_width=max(0, container_rect.width - used_width),
                remaining_height=max(0, container_rect.height - used_height)
            )
            
            return LayoutResult(success=True, calculated_rects=calculated_rects, metrics=metrics)
            
        except Exception as e:
            return LayoutResult(success=False, error_message=str(e))
    
    def _get_flex_properties(self, child: UIComponent) -> FlexProperties:
        """Get flex properties for child."""
        if hasattr(child, 'layout_properties') and child.layout_properties.flex_properties:
            return child.layout_properties.flex_properties
        return FlexProperties()
    
    def _layout_flex_row(
        self,
        children: List[UIComponent],
        container_rect: pygame.Rect,
        properties: ContainerLayout,
        remaining_space: int,
        total_flex_grow: float,
        calculated_rects: Dict[str, pygame.Rect]
    ) -> None:
        """Layout children in a flex row."""
        x_offset = container_rect.x
        
        # Handle justify content
        if properties.justify_content == Alignment.CENTER:
            x_offset += remaining_space // 2
        elif properties.justify_content == Alignment.END:
            x_offset += remaining_space
        
        for child in children:
            child_rect = child.rect.copy()
            flex_props = self._get_flex_properties(child)
            
            # Calculate width
            if flex_props.basis is not None:
                child_rect.width = flex_props.basis
            
            # Add flex grow space
            if total_flex_grow > 0 and flex_props.grow > 0:
                extra_space = int(remaining_space * (flex_props.grow / total_flex_grow))
                child_rect.width += extra_space
            
            # Set horizontal position
            child_rect.x = x_offset
            
            # Handle vertical alignment
            if properties.align_items == Alignment.CENTER:
                child_rect.y = container_rect.centery - child_rect.height // 2
            elif properties.align_items == Alignment.END:
                child_rect.y = container_rect.bottom - child_rect.height
            elif properties.align_items == Alignment.STRETCH:
                child_rect.height = container_rect.height
                child_rect.y = container_rect.y
            else:  # START
                child_rect.y = container_rect.y
            
            calculated_rects[child.component_id] = child_rect
            x_offset += child_rect.width + properties.item_spacing
    
    def _layout_flex_column(
        self,
        children: List[UIComponent],
        container_rect: pygame.Rect,
        properties: ContainerLayout,
        remaining_space: int,
        total_flex_grow: float,
        calculated_rects: Dict[str, pygame.Rect]
    ) -> None:
        """Layout children in a flex column."""
        y_offset = container_rect.y
        
        # Handle justify content
        if properties.justify_content == Alignment.CENTER:
            y_offset += remaining_space // 2
        elif properties.justify_content == Alignment.END:
            y_offset += remaining_space
        
        for child in children:
            child_rect = child.rect.copy()
            flex_props = self._get_flex_properties(child)
            
            # Calculate height
            if flex_props.basis is not None:
                child_rect.height = flex_props.basis
            
            # Add flex grow space
            if total_flex_grow > 0 and flex_props.grow > 0:
                extra_space = int(remaining_space * (flex_props.grow / total_flex_grow))
                child_rect.height += extra_space
            
            # Set vertical position
            child_rect.y = y_offset
            
            # Handle horizontal alignment
            if properties.align_items == Alignment.CENTER:
                child_rect.x = container_rect.centerx - child_rect.width // 2
            elif properties.align_items == Alignment.END:
                child_rect.x = container_rect.right - child_rect.width
            elif properties.align_items == Alignment.STRETCH:
                child_rect.width = container_rect.width
                child_rect.x = container_rect.x
            else:  # START
                child_rect.x = container_rect.x
            
            calculated_rects[child.component_id] = child_rect
            y_offset += child_rect.height + properties.item_spacing


class Container(UIComponent):
    """
    Layout container that manages child component positioning.
    
    Responsibility: Arrange child components according to layout algorithm.
    """
    
    def __init__(
        self, 
        rect: pygame.Rect, 
        layout_type: LayoutType = LayoutType.VERTICAL,
        padding: int = 10,
        spacing: int = 5,
        component_id: str = ""
    ):
        super().__init__(rect, component_id=component_id)
        self.layout_type = layout_type
        self.padding = padding
        self.spacing = spacing
        
        # Layout configuration
        self.layout_config = ContainerLayout(
            layout_type=layout_type,
            item_spacing=spacing
        )
        
        # Layout state
        self._layout_state = LayoutState.DIRTY
        self._last_result: Optional[LayoutResult] = None
        
        # Layout algorithms
        self._algorithms = {
            LayoutType.VERTICAL: VerticalLayoutAlgorithm(),
            LayoutType.HORIZONTAL: HorizontalLayoutAlgorithm(),
            LayoutType.GRID: GridLayoutAlgorithm(),
            LayoutType.FLEX: FlexLayoutAlgorithm()
        }
    
    def add_child(self, child: UIComponent) -> None:
        """Add child and mark layout as dirty."""
        super().add_child(child)
        self._layout_state = LayoutState.DIRTY
    
    def remove_child(self, child: UIComponent) -> None:
        """Remove child and mark layout as dirty."""
        super().remove_child(child)
        self._layout_state = LayoutState.DIRTY
    
    def set_layout_type(self, layout_type: LayoutType) -> None:
        """Set layout type and recalculate."""
        self.layout_type = layout_type
        self.layout_config.layout_type = layout_type
        self._layout_state = LayoutState.DIRTY
    
    def set_spacing(self, spacing: int) -> None:
        """Set item spacing."""
        self.spacing = spacing
        self.layout_config.item_spacing = spacing
        self._layout_state = LayoutState.DIRTY
    
    def set_padding(self, padding: int) -> None:
        """Set container padding."""
        self.padding = padding
        self._layout_state = LayoutState.DIRTY
    
    def recalculate_layout(self) -> LayoutResult:
        """
        Recalculate layout for all children.
        
        Returns:
            Layout calculation result
        """
        if self._layout_state == LayoutState.CALCULATING:
            return self._last_result or LayoutResult(success=False, error_message="Recursive layout calculation")
        
        self._layout_state = LayoutState.CALCULATING
        
        try:
            # Get layout algorithm
            algorithm = self._algorithms.get(self.layout_type)
            if algorithm is None:
                return LayoutResult(success=False, error_message=f"Unsupported layout type: {self.layout_type}")
            
            # Calculate content area (excluding padding)
            content_rect = pygame.Rect(
                self.rect.x + self.padding,
                self.rect.y + self.padding,
                self.rect.width - 2 * self.padding,
                self.rect.height - 2 * self.padding
            )
            
            # Calculate layout
            result = algorithm.calculate_layout(content_rect, self.children, self.layout_config)
            
            if result.success:
                # Apply calculated positions to children
                for child_id, child_rect in result.calculated_rects.items():
                    child = self.get_child_by_id(child_id)
                    if child:
                        child.rect = child_rect
                
                self._layout_state = LayoutState.CLEAN
                self._last_result = result
            else:
                self._layout_state = LayoutState.ERROR
            
            return result
            
        except Exception as e:
            self._layout_state = LayoutState.ERROR
            return LayoutResult(success=False, error_message=str(e))
    
    def _update_component(self, dt: float) -> None:
        """Update component and recalculate layout if dirty."""
        if self._layout_state == LayoutState.DIRTY:
            self.recalculate_layout()
    
    def _handle_own_event(self, event: pygame.event.Event) -> EventResult:
        """Containers typically don't handle their own events."""
        return EventResult(handled=False)
    
    def _draw_self(self, screen: pygame.Surface) -> None:
        """Draw container background and border."""
        if self.style:
            # Draw background
            pygame.draw.rect(screen, self.style.get_color("panel"), self.rect)
            
            # Draw border
            pygame.draw.rect(screen, self.style.get_color("border"), self.rect, self.style.border_width)
    
    def get_layout_metrics(self) -> Optional[LayoutMetrics]:
        """Get layout calculation metrics."""
        return self._last_result.metrics if self._last_result else None
    
    def is_layout_dirty(self) -> bool:
        """Check if layout needs recalculation."""
        return self._layout_state == LayoutState.DIRTY
    
    def mark_layout_dirty(self) -> None:
        """Mark layout as needing recalculation."""
        self._layout_state = LayoutState.DIRTY
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about container layout."""
        return {
            "component_id": self.component_id,
            "layout_type": self.layout_type.value,
            "layout_state": self._layout_state.value,
            "child_count": len(self.children),
            "padding": self.padding,
            "spacing": self.spacing,
            "rect": str(self.rect),
            "last_result": {
                "success": self._last_result.success,
                "error": self._last_result.error_message,
                "metrics": self._last_result.metrics.__dict__ if self._last_result.metrics else None
            } if self._last_result else None
        }
