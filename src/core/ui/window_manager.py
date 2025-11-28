"""
Window Manager for TurboShells

Central authority for window sizing, space measurement, and panel coordination.
Handles all UI layout calculations, space utilization tracking, and panel sizing.
"""

import pygame
from typing import Tuple, Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class SpaceMetrics:
    """Data class for space utilization metrics."""
    total_window_area: int
    used_area: int
    unused_area: int
    utilization_percentage: float
    panel_metrics: Dict[str, Dict[str, Any]]


@dataclass
class PanelInfo:
    """Data class for panel information."""
    panel_type: str
    rect: pygame.Rect
    actual_size: Tuple[int, int]
    used_area: int
    utilization_ratio: float


class WindowManager:
    """Central window management authority for all UI components."""
    
    def __init__(self, initial_size: Tuple[int, int] = (1024, 768)):
        self.window_size = initial_size
        self.min_size = (800, 600)
        self.max_size = (1920, 1080)
        
        # Layout constants
        self.header_height = 20
        self.footer_height = 20
        self.margin = 10
        self.panel_spacing = 10
        
        # Panel size ratios (relative to available space)
        self.panel_ratios = {
            'main_menu': (0.9, 0.85),
            'shop': (0.9, 0.85),
            'roster': (0.9, 0.85),
            'breeding': (0.98, 0.95),  # Increased to use more space
            'voting': (0.95, 0.9),
            'profile': (0.8, 0.85),
            'race': (1.0, 0.3),  # Full width, bottom third
            'race_result': (0.7, 0.7)
        }
        
        # Track active panels and their actual usage
        self.active_panels: Dict[str, PanelInfo] = {}
        self.rendered_panels: List[str] = []
        
        # Space utilization tracking
        self.space_history: List[SpaceMetrics] = []
        self.max_history_size = 10
    
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
    
    def register_panel(self, panel_type: str, actual_rect: pygame.Rect) -> None:
        """Register a panel with its actual rendered dimensions."""
        self.active_panels[panel_type] = PanelInfo(
            panel_type=panel_type,
            rect=actual_rect,
            actual_size=(actual_rect.width, actual_rect.height),
            used_area=actual_rect.width * actual_rect.height,
            utilization_ratio=self._calculate_utilization_ratio(panel_type, actual_rect)
        )
        self.rendered_panels.append(panel_type)
    
    def unregister_panel(self, panel_type: str) -> None:
        """Unregister a panel when it's no longer active."""
        if panel_type in self.active_panels:
            del self.active_panels[panel_type]
        if panel_type in self.rendered_panels:
            self.rendered_panels.remove(panel_type)
    
    def calculate_space_utilization(self) -> SpaceMetrics:
        """Calculate current space utilization metrics."""
        total_window_area = self.window_size[0] * self.window_size[1]
        
        # Calculate used area from active panels
        used_area = sum(panel.used_area for panel in self.active_panels.values())
        
        # Calculate unused area
        unused_area = total_window_area - used_area
        utilization_percentage = (used_area / total_window_area) * 100 if total_window_area > 0 else 0
        
        # Calculate panel-specific metrics
        panel_metrics = {}
        for panel_type, panel_info in self.active_panels.items():
            expected_rect = self.get_panel_rect(panel_type)
            panel_metrics[panel_type] = {
                'expected_size': (expected_rect.width, expected_rect.height),
                'actual_size': panel_info.actual_size,
                'size_difference': (
                    expected_rect.width - panel_info.actual_size[0],
                    expected_rect.height - panel_info.actual_size[1]
                ),
                'utilization_ratio': panel_info.utilization_ratio,
                'area_efficiency': (panel_info.used_area / (expected_rect.width * expected_rect.height)) * 100
            }
        
        metrics = SpaceMetrics(
            total_window_area=total_window_area,
            used_area=used_area,
            unused_area=unused_area,
            utilization_percentage=utilization_percentage,
            panel_metrics=panel_metrics
        )
        
        # Store in history
        self.space_history.append(metrics)
        if len(self.space_history) > self.max_history_size:
            self.space_history.pop(0)
        
        return metrics
    
    def get_unused_space_regions(self) -> List[pygame.Rect]:
        """Calculate unused space regions in the window."""
        unused_regions = []
        available_area = self.get_available_area()
        
        # If no panels are active, return the entire available area
        if not self.active_panels:
            unused_regions.append(available_area)
            return unused_regions
        
        # Calculate unused regions by subtracting panel areas
        # This is a simplified version - could be enhanced with more complex geometry
        for panel_info in self.active_panels.values():
            panel_rect = panel_info.rect
            if available_area.colliderect(panel_rect):
                # Subtract panel area from available area
                remaining_rects = self._subtract_rect(available_area, panel_rect)
                unused_regions.extend(remaining_rects)
        
        return unused_regions
    
    def optimize_panel_sizes(self) -> Dict[str, pygame.Rect]:
        """Optimize panel sizes to better utilize available space."""
        current_metrics = self.calculate_space_utilization()
        
        # If utilization is low, suggest size increases
        if current_metrics.utilization_percentage < 70:
            optimizations = {}
            
            for panel_type in self.active_panels:
                current_rect = self.active_panels[panel_type].rect
                current_ratio = self.panel_ratios.get(panel_type, (0.8, 0.75))
                
                # Suggest increased ratios for better utilization
                new_width_ratio = min(current_ratio[0] * 1.1, 0.98)
                new_height_ratio = min(current_ratio[1] * 1.1, 0.95)
                
                available_area = self.get_available_area()
                new_size = (
                    int(available_area.width * new_width_ratio),
                    int(available_area.height * new_height_ratio)
                )
                new_pos = self.calculate_panel_position(panel_type, new_size)
                
                optimizations[panel_type] = pygame.Rect(new_pos, new_size)
            
            return optimizations
        
        return {}
    
    def suggest_layout_improvements(self) -> List[str]:
        """Suggest layout improvements based on current space utilization."""
        metrics = self.calculate_space_utilization()
        suggestions = []
        
        if metrics.utilization_percentage < 60:
            suggestions.append("Low space utilization. Consider increasing panel size ratios.")
        
        if metrics.unused_area > 50000:  # Large unused area
            suggestions.append("Significant unused space detected. Panels could be enlarged.")
        
        # Check for panel-specific inefficiencies
        for panel_type, panel_metrics in metrics.panel_metrics.items():
            if panel_metrics['area_efficiency'] < 80:
                suggestions.append(f"{panel_type.title()} panel has low area efficiency.")
            
            size_diff = panel_metrics['size_difference']
            if abs(size_diff[0]) > 50 or abs(size_diff[1]) > 50:
                suggestions.append(f"{panel_type.title()} panel size differs from expected by {size_diff}.")
        
        return suggestions
    
    def get_window_report(self) -> str:
        """Generate a comprehensive window utilization report."""
        metrics = self.calculate_space_utilization()
        suggestions = self.suggest_layout_improvements()
        
        report = f"""
=== Window Utilization Report ===
Window Size: {self.window_size[0]}x{self.window_size[1]}
Total Area: {metrics.total_window_area:,} pixels²
Used Area: {metrics.used_area:,} pixels²
Unused Area: {metrics.unused_area:,} pixels²
Utilization: {metrics.utilization_percentage:.1f}%

Active Panels: {len(self.active_panels)}
"""
        
        for panel_type, panel_metrics in metrics.panel_metrics.items():
            report += f"""
{panel_type.title()} Panel:
  Expected: {panel_metrics['expected_size'][0]}x{panel_metrics['expected_size'][1]}
  Actual: {panel_metrics['actual_size'][0]}x{panel_metrics['actual_size'][1]}
  Efficiency: {panel_metrics['area_efficiency']:.1f}%
"""
        
        if suggestions:
            report += "\nSuggestions:\n"
            for suggestion in suggestions:
                report += f"  • {suggestion}\n"
        
        return report
    
    def _calculate_utilization_ratio(self, panel_type: str, actual_rect: pygame.Rect) -> float:
        """Calculate how well a panel utilizes its allocated space."""
        expected_rect = self.get_panel_rect(panel_type)
        expected_area = expected_rect.width * expected_rect.height
        actual_area = actual_rect.width * actual_rect.height
        
        return (actual_area / expected_area) if expected_area > 0 else 0
    
    def _subtract_rect(self, base_rect: pygame.Rect, subtract_rect: pygame.Rect) -> List[pygame.Rect]:
        """Subtract one rectangle from another, returning remaining regions."""
        if not base_rect.colliderect(subtract_rect):
            return [base_rect]
        
        remaining = []
        
        # Top strip
        if subtract_rect.top > base_rect.top:
            top_rect = pygame.Rect(
                base_rect.left, base_rect.top,
                base_rect.width, subtract_rect.top - base_rect.top
            )
            remaining.append(top_rect)
        
        # Bottom strip
        if subtract_rect.bottom < base_rect.bottom:
            bottom_rect = pygame.Rect(
                base_rect.left, subtract_rect.bottom,
                base_rect.width, base_rect.bottom - subtract_rect.bottom
            )
            remaining.append(bottom_rect)
        
        # Left strip
        if subtract_rect.left > base_rect.left:
            left_rect = pygame.Rect(
                base_rect.left, max(base_rect.top, subtract_rect.top),
                subtract_rect.left - base_rect.left,
                min(base_rect.bottom, subtract_rect.bottom) - max(base_rect.top, subtract_rect.top)
            )
            remaining.append(left_rect)
        
        # Right strip
        if subtract_rect.right < base_rect.right:
            right_rect = pygame.Rect(
                subtract_rect.right, max(base_rect.top, subtract_rect.top),
                base_rect.right - subtract_rect.right,
                min(base_rect.bottom, subtract_rect.bottom) - max(base_rect.top, subtract_rect.top)
            )
            remaining.append(right_rect)
        
        return remaining


# Global window manager instance
window_manager = WindowManager()
