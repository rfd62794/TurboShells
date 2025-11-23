"""
Layout system types and enums.

This module defines the core types and enums used by the layout system,
providing a consistent interface for layout configuration.
"""

from enum import Enum
from typing import Optional, Tuple, List, Any
from dataclasses import dataclass


class LayoutType(Enum):
    """Layout type enumeration."""
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    GRID = "grid"
    FLEX = "flex"
    ABSOLUTE = "absolute"


class Alignment(Enum):
    """Alignment enumeration."""
    START = "start"
    CENTER = "center"
    END = "end"
    STRETCH = "stretch"


class SizePolicy(Enum):
    """Size policy enumeration."""
    FIXED = "fixed"
    CONTENT = "content"
    EXPAND = "expand"
    SHRINK = "shrink"


class Direction(Enum):
    """Direction enumeration."""
    ROW = "row"
    COLUMN = "column"
    ROW_REVERSE = "row_reverse"
    COLUMN_REVERSE = "column_reverse"


class WrapMode(Enum):
    """Wrap mode enumeration."""
    NO_WRAP = "no_wrap"
    WRAP = "wrap"
    WRAP_REVERSE = "wrap_reverse"


@dataclass
class GridPosition:
    """Grid position specification."""
    row: int
    column: int
    row_span: int = 1
    column_span: int = 1


@dataclass
class FlexProperties:
    """Flex layout properties."""
    grow: float = 0.0
    shrink: float = 1.0
    basis: Optional[int] = None
    align_self: Optional[Alignment] = None


@dataclass
class LayoutProperties:
    """Comprehensive layout properties for components."""
    # Basic layout
    layout_type: LayoutType = LayoutType.VERTICAL
    alignment: Alignment = Alignment.START
    size_policy: SizePolicy = SizePolicy.CONTENT
    
    # Sizing
    min_width: Optional[int] = None
    max_width: Optional[int] = None
    min_height: Optional[int] = None
    max_height: Optional[int] = None
    preferred_width: Optional[int] = None
    preferred_height: Optional[int] = None
    
    # Positioning
    x: Optional[int] = None
    y: Optional[int] = None
    anchor_x: Optional[float] = None  # 0.0 to 1.0
    anchor_y: Optional[float] = None  # 0.0 to 1.0
    
    # Margins and padding
    margin_top: int = 0
    margin_right: int = 0
    margin_bottom: int = 0
    margin_left: int = 0
    padding_top: int = 0
    padding_right: int = 0
    padding_bottom: int = 0
    padding_left: int = 0
    
    # Grid-specific
    grid_position: Optional[GridPosition] = None
    
    # Flex-specific
    flex_properties: Optional[FlexProperties] = None
    
    # Visibility
    visible: bool = True
    enabled: bool = True
    
    # Z-order
    z_index: int = 0
    
    # Custom properties
    custom_properties: dict = None
    
    def __post_init__(self) -> None:
        if self.custom_properties is None:
            self.custom_properties = {}
    
    def get_margin_total(self) -> Tuple[int, int]:
        """Get total horizontal and vertical margins."""
        return (self.margin_left + self.margin_right, 
                self.margin_top + self.margin_bottom)
    
    def get_padding_total(self) -> Tuple[int, int]:
        """Get total horizontal and vertical padding."""
        return (self.padding_left + self.padding_right,
                self.padding_top + self.padding_bottom)
    
    def get_total_spacing(self) -> Tuple[int, int]:
        """Get total spacing (margins + padding)."""
        margin_h, margin_v = self.get_margin_total()
        padding_h, padding_v = self.get_padding_total()
        return (margin_h + padding_h, margin_v + padding_v)


@dataclass
class LayoutMetrics:
    """Layout calculation metrics."""
    available_width: int
    available_height: int
    content_width: int
    content_height: int
    used_width: int
    used_height: int
    remaining_width: int
    remaining_height: int
    
    def has_space(self) -> bool:
        """Check if there's remaining space."""
        return self.remaining_width > 0 or self.remaining_height > 0
    
    def space_ratio(self) -> Tuple[float, float]:
        """Get space usage ratio."""
        return (self.used_width / self.available_width if self.available_width > 0 else 0,
                self.used_height / self.available_height if self.available_height > 0 else 0)


class LayoutDirection(Enum):
    """Layout direction for container flow."""
    NORMAL = "normal"
    REVERSE = "reverse"


class OverflowMode(Enum):
    """Overflow handling mode."""
    VISIBLE = "visible"
    HIDDEN = "hidden"
    SCROLL = "scroll"
    CLIP = "clip"


@dataclass
class ContainerLayout:
    """Container layout configuration."""
    layout_type: LayoutType = LayoutType.VERTICAL
    direction: LayoutDirection = LayoutDirection.NORMAL
    wrap_mode: WrapMode = WrapMode.NO_WRAP
    overflow_mode: OverflowMode = OverflowMode.VISIBLE
    
    # Alignment
    main_axis_alignment: Alignment = Alignment.START
    cross_axis_alignment: Alignment = Alignment.START
    
    # Spacing
    item_spacing: int = 5
    line_spacing: int = 5
    
    # Grid-specific
    grid_columns: int = 1
    grid_rows: int = 1
    column_gap: int = 5
    row_gap: int = 5
    
    # Flex-specific
    flex_direction: Direction = Direction.COLUMN
    flex_wrap: WrapMode = WrapMode.NO_WRAP
    justify_content: Alignment = Alignment.START
    align_items: Alignment = Alignment.START
    align_content: Alignment = Alignment.START
    
    def __post_init__(self) -> None:
        # Set defaults based on layout type
        if self.layout_type == LayoutType.HORIZONTAL:
            self.flex_direction = Direction.ROW
        elif self.layout_type == LayoutType.VERTICAL:
            self.flex_direction = Direction.COLUMN


class LayoutState(Enum):
    """Layout calculation state."""
    CLEAN = "clean"
    DIRTY = "dirty"
    CALCULATING = "calculating"
    ERROR = "error"


@dataclass
class LayoutResult:
    """Result of layout calculation."""
    success: bool
    error_message: Optional[str] = None
    calculated_rects: dict = None
    metrics: Optional[LayoutMetrics] = None
    
    def __post_init__(self) -> None:
        if self.calculated_rects is None:
            self.calculated_rects = {}


# Type aliases for better readability
ComponentRects = Dict[str, Any]  # Component ID to rectangle mapping
LayoutConstraints = Dict[str, Any]  # Component ID to constraints mapping
