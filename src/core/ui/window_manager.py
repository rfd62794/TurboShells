"""
Window Manager for TurboShells

Top-level window sizing system that all panels and components can use
to adjust their size based on window dimensions.
"""

import pygame
from typing import Tuple, Dict, Any


class WindowManager:
    """Manages window sizing and provides layout calculations for UI components."""
    
    def __init__(self, initial_size: Tuple[int, int] = (1024, 768)):
        self.window_size = initial_size
        self.min_size = (800, 600)
        self.max_size = (1920, 1080)
        
        # Layout constants
        self.header_height = 40
        self.footer_height = 40
        self.margin = 20
        self.panel_spacing = 10
        
        # Panel size ratios (relative to available space)
        self.panel_ratios = {
            'main_menu': (0.8, 0.7),
            'shop': (0.8, 0.7),
            'roster': (0.8, 0.7),
            'breeding': (0.8, 0.75),
            'voting': (0.8, 0.75),
            'profile': (0.7, 0.8),
            'race': (1.0, 0.3),  # Full width, bottom third
            'race_result': (0.6, 0.6)
        }
    
    def set_window_size(self, size: Tuple[int, int]) -> None:
        """Update window size and validate constraints."""
        width, height = size
        width = max(self.min_size[0], min(width, self.max_size[0]))
        height = max(self.min_size[1], min(height, self.max_size[1]))
        self.window_size = (width, height)
    
    def get_available_area(self) -> pygame.Rect:
        """Get the available area for UI components (excluding header/footer)."""
        return pygame.Rect(
            0, 
            self.header_height,
            self.window_size[0],
            self.window_size[1] - self.header_height - self.footer_height
        )
    
    def calculate_panel_size(self, panel_type: str) -> Tuple[int, int]:
        """Calculate panel size based on window dimensions and panel type."""
        if panel_type not in self.panel_ratios:
            panel_type = 'main_menu'  # Default fallback
        
        available_area = self.get_available_area()
        width_ratio, height_ratio = self.panel_ratios[panel_type]
        
        panel_width = int(available_area.width * width_ratio)
        panel_height = int(available_area.height * height_ratio)
        
        return (panel_width, panel_height)
    
    def calculate_panel_position(self, panel_type: str, panel_size: Tuple[int, int]) -> Tuple[int, int]:
        """Calculate centered position for a panel."""
        available_area = self.get_available_area()
        
        # Center the panel in the available area
        x = (available_area.width - panel_size[0]) // 2
        y = (available_area.height - panel_size[1]) // 2
        
        return (x, y)
    
    def get_panel_rect(self, panel_type: str) -> pygame.Rect:
        """Get the complete rect (position + size) for a panel."""
        size = self.calculate_panel_size(panel_type)
        pos = self.calculate_panel_position(panel_type, size)
        return pygame.Rect(pos, size)
    
    def adjust_for_window_resize(self, new_size: Tuple[int, int]) -> Dict[str, Any]:
        """Calculate all panel adjustments for a window resize."""
        old_size = self.window_size
        self.set_window_size(new_size)
        
        adjustments = {}
        for panel_type in self.panel_ratios:
            adjustments[panel_type] = {
                'size': self.calculate_panel_size(panel_type),
                'position': self.calculate_panel_position(panel_type, self.calculate_panel_size(panel_type)),
                'rect': self.get_panel_rect(panel_type)
            }
        
        return {
            'window_size': self.window_size,
            'available_area': self.get_available_area(),
            'panels': adjustments,
            'size_change': (new_size[0] - old_size[0], new_size[1] - old_size[1])
        }
    
    def get_slot_layout(self, panel_type: str, grid_size: Tuple[int, int]) -> Dict[str, Any]:
        """Calculate slot layout for grids (like breeding panel)."""
        panel_rect = self.get_panel_rect(panel_type)
        cols, rows = grid_size
        
        # Calculate slot dimensions with spacing
        total_spacing_x = (cols - 1) * self.panel_spacing
        total_spacing_y = (rows - 1) * self.panel_spacing
        
        slot_width = (panel_rect.width - 2 * self.margin - total_spacing_x) // cols
        slot_height = (panel_rect.height - 2 * self.margin - total_spacing_y) // rows
        
        positions = []
        for row in range(rows):
            for col in range(cols):
                x = panel_rect.x + self.margin + col * (slot_width + self.panel_spacing)
                y = panel_rect.y + self.margin + row * (slot_height + self.panel_spacing)
                positions.append((x, y))
        
        return {
            'slot_size': (slot_width, slot_height),
            'positions': positions,
            'total_area': panel_rect
        }


# Global window manager instance
window_manager = WindowManager()
