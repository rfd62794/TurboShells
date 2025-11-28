"""
Test utility classes and helpers for TurboShells testing.

This module contains reusable classes that support test functionality
but are not pytest fixtures themselves.
"""

from typing import Dict, List, Any, Optional
from unittest.mock import Mock
import pytest

# Try to import game modules, handle gracefully if not found
try:
    from src.core.game.entities import Turtle
    GAME_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Game modules not available: {e}")
    GAME_MODULES_AVAILABLE = False
    Turtle = None

# Try to import pygame, handle gracefully if not found
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    print("Warning: pygame not available")
    PYGAME_AVAILABLE = False
    pygame = None


class AssertHelpers:
    """Custom assertion helpers for game testing"""
    
    @staticmethod
    def assert_valid_turtle(turtle):
        """Assert turtle has valid attributes"""
        if not GAME_MODULES_AVAILABLE or Turtle is None:
            pytest.skip("Game modules not available")
            
        assert isinstance(turtle.name, str) and len(turtle.name) > 0
        assert hasattr(turtle, 'stats')
        assert 1.0 <= turtle.stats['speed'] <= 10.0
        assert 50.0 <= turtle.stats['max_energy'] <= 150.0
        assert 0.5 <= turtle.stats['recovery'] <= 5.0
        assert 0.5 <= turtle.stats['swim'] <= 3.0
        assert 0.5 <= turtle.stats['climb'] <= 3.0
        assert 0 <= turtle.age <= 20
        assert isinstance(turtle.is_active, bool)
        assert turtle.current_energy >= 0
        assert turtle.race_distance >= 0
        assert isinstance(turtle.is_resting, bool)
        assert isinstance(turtle.finished, bool)
        assert turtle.rank is None or turtle.rank >= 0
    
    @staticmethod
    def assert_valid_race_result(results):
        """Assert race results are valid"""
        assert isinstance(results, list)
        for result in results:
            assert 'turtle' in result
            assert 'rank' in result
            assert 'time' in result
            assert 1 <= result['rank'] <= len(results)
    
    @staticmethod
    def assert_valid_save_data(data):
        """Assert save data structure is valid"""
        required_keys = ['version', 'money', 'roster', 'retired_roster', 'shop_inventory']
        for key in required_keys:
            assert key in data
        assert isinstance(data['money'], int) and data['money'] >= 0
        assert isinstance(data['roster'], list)
        assert isinstance(data['retired_roster'], list)


class UIAssertHelpers:
    """Custom assertion helpers for UI testing"""
    
    @staticmethod
    def assert_valid_button(button):
        """Assert button has valid attributes"""
        assert hasattr(button, 'text')
        assert hasattr(button, 'action')
        assert hasattr(button, 'rect')
        assert hasattr(button, 'config')
        assert hasattr(button, 'button')  # pygame_gui element
        assert isinstance(button.text, str) and len(button.text) > 0
        assert isinstance(button.action, str) and len(button.action) > 0
        assert isinstance(button.rect, tuple) or hasattr(button.rect, 'x')
        assert isinstance(button.config, dict)
    
    @staticmethod
    def assert_valid_money_display(money_display):
        """Assert money display has valid attributes"""
        assert hasattr(money_display, 'amount')
        assert hasattr(money_display, 'rect')
        assert hasattr(money_display, 'config')
        assert hasattr(money_display, 'label')  # pygame_gui element
        assert isinstance(money_display.amount, (int, float))
        assert money_display.amount >= 0
        assert isinstance(money_display.config, dict)
    
    @staticmethod
    def assert_valid_panel(panel):
        """Assert panel has valid attributes"""
        assert hasattr(panel, 'panel_id')
        assert hasattr(panel, 'title')
        assert hasattr(panel, 'size')
        assert hasattr(panel, 'position')
        assert isinstance(panel.panel_id, str)
        assert isinstance(panel.title, str)
        assert isinstance(panel.size, (tuple, list)) and len(panel.size) == 2
        assert isinstance(panel.position, (tuple, list)) and len(panel.position) == 2
    
    @staticmethod
    def assert_button_layout(buttons, expected_count=None, spacing=None):
        """Assert buttons are laid out correctly"""
        if expected_count is not None:
            assert len(buttons) == expected_count
        
        # Check no overlapping
        for i in range(len(buttons) - 1):
            current = buttons[i]
            next_btn = buttons[i + 1]
            
            if hasattr(current, 'button') and hasattr(next_btn, 'button'):
                current_rect = current.button.rect
                next_rect = next_btn.button.rect
                
                # No vertical overlap
                assert current_rect.bottom <= next_rect.top, f"Buttons {i} and {i+1} overlap"
                
                # Check spacing if specified
                if spacing is not None:
                    actual_spacing = next_rect.top - current_rect.bottom
                    assert abs(actual_spacing - spacing) <= 1, f"Button spacing incorrect: expected {spacing}, got {actual_spacing}"
    
    @staticmethod
    def assert_component_positioning(component, expected_x=None, expected_y=None, expected_size=None):
        """Assert component is positioned correctly"""
        if hasattr(component, 'button'):  # Button component
            rect = component.button.rect
        elif hasattr(component, 'label'):  # MoneyDisplay component
            rect = component.label.rect
        elif hasattr(component, 'window'):  # Panel component
            rect = component.window.rect
        else:
            rect = component.rect
        
        if expected_x is not None:
            assert rect.x == expected_x, f"X position incorrect: expected {expected_x}, got {rect.x}"
        
        if expected_y is not None:
            assert rect.y == expected_y, f"Y position incorrect: expected {expected_y}, got {rect.y}"
        
        if expected_size is not None:
            assert rect.width == expected_size[0], f"Width incorrect: expected {expected_size[0]}, got {rect.width}"
            assert rect.height == expected_size[1], f"Height incorrect: expected {expected_size[1]}, got {rect.height}"
    
    @staticmethod
    def assert_ui_component_visible(component):
        """Assert UI component is visible"""
        if hasattr(component, 'button'):
            assert component.button.visible, "Button not visible"
        elif hasattr(component, 'label'):
            assert component.label.visible, "Label not visible"
        elif hasattr(component, 'window'):
            assert component.window.visible, "Window not visible"


class PerformanceTracker:
    """Track performance metrics during tests"""
    
    def __init__(self):
        self.metrics = {}
    
    def start_timer(self, name: str):
        """Start timing an operation"""
        import time
        self.metrics[f"{name}_start"] = time.time()
    
    def end_timer(self, name: str):
        """End timing an operation"""
        import time
        if f"{name}_start" in self.metrics:
            duration = time.time() - self.metrics[f"{name}_start"]
            self.metrics[f"{name}_duration"] = duration
            return duration
        return None
    
    def track_memory(self, name: str):
        """Track memory usage"""
        try:
            import psutil
            process = psutil.Process()
            self.metrics[f"{name}_memory"] = process.memory_info().rss
        except ImportError:
            pass
    
    def get_metric(self, name: str):
        """Get a specific metric"""
        return self.metrics.get(name)
    
    def all_metrics(self) -> Dict:
        """Get all metrics"""
        return self.metrics.copy()


class UIPerformanceTracker(PerformanceTracker):
    """Track UI-specific performance metrics"""
    
    def track_creation_time(self, component_name: str, create_func):
        """Track UI component creation time"""
        self.start_timer(f"{component_name}_creation")
        component = create_func()
        duration = self.end_timer(f"{component_name}_creation")
        return component, duration
    
    def track_render_time(self, component_name: str, render_func):
        """Track UI component render time"""
        self.start_timer(f"{component_name}_render")
        result = render_func()
        duration = self.end_timer(f"{component_name}_render")
        return result, duration
    
    def track_event_handling_time(self, component_name: str, event_func):
        """Track UI component event handling time"""
        self.start_timer(f"{component_name}_events")
        result = event_func()
        duration = self.end_timer(f"{component_name}_events")
        return result, duration


class TestDataFactory:
    """Factory for creating test data"""
    
    @staticmethod
    def create_minimal_turtle(name: str = "Minimal"):
        """Create turtle with minimal stats for edge case testing"""
        if not GAME_MODULES_AVAILABLE or Turtle is None:
            pytest.skip("Game modules not available")
        return Turtle(
            name=name,
            speed=1.0,  # Minimum
            energy=50.0,  # Minimum
            recovery=0.5,  # Minimum
            swim=0.5,  # Minimum
            climb=0.5,  # Minimum
        )

    @staticmethod
    def create_extreme_turtle(name: str = "Extreme"):
        """Create turtle with maximum stats for testing"""
        if not GAME_MODULES_AVAILABLE or Turtle is None:
            pytest.skip("Game modules not available")
        return Turtle(
            name=name,
            speed=10.0,  # Maximum
            energy=150.0,  # Maximum
            recovery=5.0,  # Maximum
            swim=3.0,  # Maximum
            climb=3.0,  # Maximum
        )

    @staticmethod
    def create_exhausted_turtle(name: str = "Exhausted"):
        """Create turtle with zero energy for testing recovery"""
        if not GAME_MODULES_AVAILABLE or Turtle is None:
            pytest.skip("Game modules not available")
        turtle = TestDataFactory.create_minimal_turtle(name)
        turtle.current_energy = 0.0
        turtle.is_resting = True
        return turtle


class UITestDataFactory:
    """Factory for creating UI test data"""
    
    @staticmethod
    def create_mock_button(text="Test Button", action="test_action", rect=None):
        """Create mock button for testing"""
        if rect is None:
            rect = pygame.Rect(10, 10, 100, 30) if PYGAME_AVAILABLE else (10, 10, 100, 30)
        
        button = Mock()
        button.text = text
        button.action = action
        button.rect = rect
        button.config = {'style': 'primary'}
        button.button = Mock()
        button.button.visible = True
        button.button.rect = rect
        button.enabled = True
        return button
    
    @staticmethod
    def create_mock_money_display(amount=1000, rect=None):
        """Create mock money display for testing"""
        if rect is None:
            rect = pygame.Rect(10, 10, 150, 25) if PYGAME_AVAILABLE else (10, 10, 150, 25)
        
        display = Mock()
        display.amount = amount
        display.rect = rect
        display.config = {'font_size': 16, 'prefix': '$'}
        display.label = Mock()
        display.label.visible = True
        display.label.rect = rect
        return display
    
    @staticmethod
    def create_mock_panel(panel_id="test_panel", title="Test Panel", size=(400, 300)):
        """Create mock panel for testing"""
        panel = Mock()
        panel.panel_id = panel_id
        panel.title = title
        panel.size = size
        panel.position = (100, 100)
        panel.window = Mock()
        panel.window.visible = True
        panel.window.rect = pygame.Rect(100, 100, size[0], size[1]) if PYGAME_AVAILABLE else Mock()
        return panel
    
    @staticmethod
    def create_mock_event(event_type, **kwargs):
        """Create mock pygame event for testing"""
        event = Mock()
        event.type = event_type
        for key, value in kwargs.items():
            setattr(event, key, value)
        return event
