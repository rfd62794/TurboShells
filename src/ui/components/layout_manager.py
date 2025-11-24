"""
Layout management component for settings interface.

Handles responsive layout calculations following SRP principles.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import pygame

from core.logging_config import get_logger


@dataclass
class LayoutConstraints:
    """Layout constraints for UI elements."""
    min_width: Optional[int] = None
    max_width: Optional[int] = None
    min_height: Optional[int] = None
    max_height: Optional[int] = None
    padding: int = 10
    spacing: int = 5


class LayoutManager:
    """
    Manages responsive layout calculations for the settings interface.
    
    Single responsibility: Handle layout and positioning only.
    """
    
    def __init__(self, screen_rect: pygame.Rect):
        """
        Initialize layout manager.
        
        Args:
            screen_rect: Screen rectangle for layout calculations
        """
        self.screen_rect = screen_rect
        self.logger = get_logger(__name__)
        
        # Layout constraints
        self.panel_constraints = LayoutConstraints(
            min_width=600,
            max_width=950,
            min_height=400,
            max_height=700,
            padding=30
        )
        
        self.tab_bar_constraints = LayoutConstraints(
            min_height=40,
            max_height=40,
            padding=10
        )
        
        self.content_constraints = LayoutConstraints(
            padding=10,
            spacing=20
        )
        
        # Calculated layout rectangles
        self.panel_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.tab_bar_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.content_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        
        # Calculate initial layout
        self.calculate_layout()
        
        self.logger.debug("LayoutManager initialized")
    
    def calculate_layout(self) -> None:
        """Calculate all layout rectangles based on current screen dimensions."""
        # Calculate panel dimensions
        panel_width = min(
            self.screen_rect.width * 0.95, 
            self.panel_constraints.max_width
        )
        panel_height = min(
            self.screen_rect.height * 0.9,
            self.panel_constraints.max_height
        )
        
        # Ensure minimum dimensions
        panel_width = max(panel_width, self.panel_constraints.min_width)
        panel_height = max(panel_height, self.panel_constraints.min_height)
        
        # Position panel in upper-left corner with padding
        self.panel_rect = pygame.Rect(
            self.panel_constraints.padding,
            self.panel_constraints.padding,
            panel_width,
            panel_height
        )
        
        # Calculate tab bar rectangle
        self.tab_bar_rect = pygame.Rect(
            self.panel_rect.x + self.tab_bar_constraints.padding,
            self.panel_rect.y + self.tab_bar_constraints.padding,
            self.panel_rect.width - (self.tab_bar_constraints.padding * 2),
            self.tab_bar_constraints.min_height
        )
        
        # Calculate content rectangle (area below tab bar)
        content_top = self.tab_bar_rect.bottom + self.content_constraints.padding
        content_height = (
            self.panel_rect.height - 
            self.tab_bar_rect.height - 
            (self.content_constraints.padding * 3)  # Top, bottom, and separator
        )
        
        self.content_rect = pygame.Rect(
            self.panel_rect.x + self.content_constraints.padding,
            content_top,
            self.panel_rect.width - (self.content_constraints.padding * 2),
            content_height
        )
        
        self.logger.debug(f"Layout calculated: {self.panel_rect.width}x{self.panel_rect.height}")
    
    def update_screen_size(self, new_screen_rect: pygame.Rect) -> None:
        """
        Update layout for new screen dimensions.
        
        Args:
            new_screen_rect: New screen rectangle
        """
        old_panel_rect = self.panel_rect.copy()
        self.screen_rect = new_screen_rect
        self.calculate_layout()
        
        # Log if panel size changed significantly
        if abs(self.panel_rect.width - old_panel_rect.width) > 50 or \
           abs(self.panel_rect.height - old_panel_rect.height) > 50:
            self.logger.info(f"Layout resized from {old_panel_rect.size} to {self.panel_rect.size}")
    
    def get_panel_rect(self) -> pygame.Rect:
        """Get the main panel rectangle."""
        return self.panel_rect
    
    def get_tab_bar_rect(self) -> pygame.Rect:
        """Get the tab bar rectangle."""
        return self.tab_bar_rect
    
    def get_content_rect(self) -> pygame.Rect:
        """Get the content area rectangle."""
        return self.content_rect
    
    def calculate_element_positions(self, elements: List[Dict], area_rect: pygame.Rect) -> List[pygame.Rect]:
        """
        Calculate positions for a list of UI elements within an area.
        
        Args:
            elements: List of element dictionaries with size info
            area_rect: Area rectangle to position elements in
            
        Returns:
            List of calculated rectangles for each element
        """
        positions = []
        current_y = area_rect.y + self.content_constraints.padding
        line_height = self.content_constraints.spacing + 35  # Element height + spacing
        
        for element in elements:
            element_height = element.get('height', 25)
            element_width = element.get('width', 200)
            
            # Determine element position
            element_rect = pygame.Rect(
                area_rect.x + self.content_constraints.padding,
                current_y,
                element_width,
                element_height
            )
            
            positions.append(element_rect)
            current_y += line_height
        
        return positions
    
    def calculate_button_positions(self, button_count: int, button_size: Tuple[int, int], 
                                 area_rect: pygame.Rect, alignment: str = "right") -> List[pygame.Rect]:
        """
        Calculate positions for action buttons.
        
        Args:
            button_count: Number of buttons
            button_size: Tuple of (width, height) for each button
            area_rect: Area to position buttons in (usually bottom of panel)
            alignment: Alignment strategy ("left", "center", "right")
            
        Returns:
            List of calculated rectangles for each button
        """
        button_width, button_height = button_size
        spacing = 10
        
        if alignment == "right":
            # Position buttons from right edge
            start_x = area_rect.right - button_width - 10
            positions = []
            
            for i in range(button_count):
                x = start_x - (i * (button_width + spacing))
                y = area_rect.bottom - button_height - 10
                positions.append(pygame.Rect(x, y, button_width, button_height))
            
            return positions
        
        elif alignment == "center":
            # Center buttons
            total_width = button_count * button_width + (button_count - 1) * spacing
            start_x = area_rect.centerx - (total_width // 2)
            positions = []
            
            for i in range(button_count):
                x = start_x + i * (button_width + spacing)
                y = area_rect.bottom - button_height - 10
                positions.append(pygame.Rect(x, y, button_width, button_height))
            
            return positions
        
        else:  # left alignment
            # Position buttons from left edge
            start_x = area_rect.x + 10
            positions = []
            
            for i in range(button_count):
                x = start_x + i * (button_width + spacing)
                y = area_rect.bottom - button_height - 10
                positions.append(pygame.Rect(x, y, button_width, button_height))
            
            return positions
    
    def calculate_grid_layout(self, items: List[Dict], area_rect: pygame.Rect, 
                             columns: int = 2) -> List[pygame.Rect]:
        """
        Calculate grid layout for items.
        
        Args:
            items: List of items to arrange in grid
            area_rect: Area to arrange grid in
            columns: Number of columns in grid
            
        Returns:
            List of calculated rectangles for each item
        """
        if not items:
            return []
        
        item_width = (area_rect.width - (columns + 1) * self.content_constraints.padding) // columns
        item_height = 30  # Default item height
        
        positions = []
        current_row = 0
        current_col = 0
        
        for i, item in enumerate(items):
            x = area_rect.x + self.content_constraints.padding + current_col * (item_width + self.content_constraints.padding)
            y = area_rect.y + self.content_constraints.padding + current_row * (item_height + self.content_constraints.spacing)
            
            positions.append(pygame.Rect(x, y, item_width, item_height))
            
            current_col += 1
            if current_col >= columns:
                current_col = 0
                current_row += 1
        
        return positions
    
    def calculate_vertical_layout(self, elements: List[Dict], area_rect: pygame.Rect) -> List[pygame.Rect]:
        """
        Calculate vertical layout for elements.
        
        Args:
            elements: List of elements with size information
            area_rect: Area to arrange elements in
            
        Returns:
            List of calculated rectangles for each element
        """
        positions = []
        current_y = area_rect.y + self.content_constraints.padding
        
        for element in elements:
            element_height = element.get('height', 25)
            element_width = min(element.get('width', area_rect.width - 20), area_rect.width - 20)
            
            element_rect = pygame.Rect(
                area_rect.x + self.content_constraints.padding,
                current_y,
                element_width,
                element_height
            )
            
            positions.append(element_rect)
            current_y += element_height + self.content_constraints.spacing
        
        return positions
    
    def calculate_horizontal_layout(self, elements: List[Dict], area_rect: pygame.Rect) -> List[pygame.Rect]:
        """
        Calculate horizontal layout for elements.
        
        Args:
            elements: List of elements with size information
            area_rect: Area to arrange elements in
            
        Returns:
            List of calculated rectangles for each element
        """
        positions = []
        current_x = area_rect.x + self.content_constraints.padding
        
        # Calculate total width needed
        total_width = sum(e.get('width', 100) for e in elements)
        total_spacing = (len(elements) - 1) * self.content_constraints.spacing
        
        if total_width + total_spacing > area_rect.width:
            # Not enough space, use proportional sizing
            available_width = area_rect.width - (self.content_constraints.padding * 2)
            spacing = max(5, (available_width - total_width) // (len(elements) - 1) if len(elements) > 1 else 0)
            
            for i, element in enumerate(elements):
                element_width = element.get('width', 100)
                element_height = element.get('height', 25)
                
                element_rect = pygame.Rect(
                    current_x,
                    area_rect.y + self.content_constraints.padding,
                    element_width,
                    element_height
                )
                
                positions.append(element_rect)
                current_x += element_width + spacing
        else:
            # Enough space, use normal spacing
            for element in elements:
                element_width = element.get('width', 100)
                element_height = element.get('height', 25)
                
                element_rect = pygame.Rect(
                    current_x,
                    area_rect.y + self.content_constraints.padding,
                    element_width,
                    element_height
                )
                
                positions.append(element_rect)
                current_x += element_width + self.content_constraints.spacing
        
        return positions
    
    def get_layout_info(self) -> Dict[str, any]:
        """
        Get current layout information.
        
        Returns:
            Dictionary with layout dimensions and constraints
        """
        return {
            "screen_size": self.screen_rect.size,
            "panel_size": self.panel_rect.size,
            "tab_bar_size": self.tab_bar_rect.size,
            "content_size": self.content_rect.size,
            "panel_position": self.panel_rect.topleft,
            "utilization": {
                "width_percent": (self.panel_rect.width / self.screen_rect.width) * 100,
                "height_percent": (self.panel_rect.height / self.screen_rect.height) * 100
            }
        }
    
    def validate_layout(self) -> List[str]:
        """
        Validate current layout for potential issues.
        
        Returns:
            List of validation warnings/errors
        """
        issues = []
        
        # Check if panel fits on screen
        if self.panel_rect.right > self.screen_rect.width:
            issues.append("Panel extends beyond screen width")
        
        if self.panel_rect.bottom > self.screen_rect.height:
            issues.append("Panel extends beyond screen height")
        
        # Check minimum sizes
        if self.panel_rect.width < self.panel_constraints.min_width:
            issues.append(f"Panel width {self.panel_rect.width} below minimum {self.panel_constraints.min_width}")
        
        if self.panel_rect.height < self.panel_constraints.min_height:
            issues.append(f"Panel height {self.panel_rect.height} below minimum {self.panel_constraints.min_height}")
        
        # Check content area
        if self.content_rect.width < 100:
            issues.append("Content area too narrow")
        
        if self.content_rect.height < 100:
            issues.append("Content area too short")
        
        # Check tab bar
        if self.tab_bar_rect.width < 200:
            issues.append("Tab bar too narrow for tabs")
        
        return issues
    
    def reset_to_defaults(self) -> None:
        """Reset layout manager to default state."""
        self.calculate_layout()
        self.logger.debug("LayoutManager reset to defaults")
