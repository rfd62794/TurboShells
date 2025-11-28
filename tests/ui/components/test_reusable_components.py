"""
Test suite for reusable UI components.

This test suite verifies:
1. Component isolation and SRP compliance
2. Component configuration and customization
3. Event handling within components
4. Container positioning and rendering
5. Component reusability across different contexts
"""

import sys
import os
import pytest
import pygame
import pygame_gui
from unittest.mock import Mock, patch

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from ui.components.reusable import Button, MoneyDisplay, Container, Panel


class TestButtonComponent:
    """Test suite for Button component."""
    
    @pytest.fixture
    def pygame_setup(self):
        """Setup pygame for testing."""
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        manager = pygame_gui.UIManager((800, 600))
        yield screen, manager
        pygame.quit()
    
    @pytest.fixture
    def button(self, pygame_setup):
        """Create button instance for testing."""
        screen, manager = pygame_setup
        return Button(
            rect=pygame.Rect(10, 10, 200, 40),
            text="Test Button",
            action="test_action",
            manager=manager
        )
    
    def test_button_initialization(self, pygame_setup):
        """Test button initialization."""
        screen, manager = pygame_setup
        button = Button(
            rect=pygame.Rect(10, 10, 200, 40),
            text="Test Button",
            action="test_action",
            manager=manager,
            config={'style': 'primary'}
        )
        
        assert button.text == "Test Button"
        assert button.action == "test_action"
        assert button.config['style'] == 'primary'
        assert button.button is not None  # pygame_gui element created
    
    def test_button_with_container(self, pygame_setup):
        """Test button creation with container."""
        screen, manager = pygame_setup
        
        # Create a container
        container_rect = pygame.Rect(100, 100, 400, 300)
        window = pygame_gui.elements.UIWindow(
            rect=container_rect,
            manager=manager,
            window_title="Test Window"
        )
        container = window.get_container()
        
        # Create button in container
        button = Button(
            rect=pygame.Rect(10, 10, 200, 40),
            text="Container Button",
            action="container_action",
            manager=manager,
            container=container
        )
        
        assert button.container == container
        assert button.button is not None
    
    def test_button_styling(self, pygame_setup):
        """Test button styling options."""
        screen, manager = pygame_setup
        
        # Test primary style
        primary_button = Button(
            rect=pygame.Rect(10, 10, 100, 30),
            text="Primary",
            action="primary",
            manager=manager,
            config={'style': 'primary'}
        )
        assert primary_button.config['style'] == 'primary'
        
        # Test danger style
        danger_button = Button(
            rect=pygame.Rect(10, 50, 100, 30),
            text="Danger",
            action="danger",
            manager=manager,
            config={'style': 'danger'}
        )
        assert danger_button.config['style'] == 'danger'
        
        # Test secondary style
        secondary_button = Button(
            rect=pygame.Rect(10, 90, 100, 30),
            text="Secondary",
            action="secondary",
            manager=manager,
            config={'style': 'secondary'}
        )
        assert secondary_button.config['style'] == 'secondary'
    
    def test_button_action_callback(self, button):
        """Test button action callback."""
        callback_called = False
        callback_action = None
        
        def test_callback(action):
            nonlocal callback_called, callback_action
            callback_called = True
            callback_action = action
        
        button.set_action_callback(test_callback)
        
        # Simulate button press
        button._on_button_action()
        
        assert callback_called
        assert callback_action == button.action
    
    def test_button_event_handling(self, button):
        """Test button event handling."""
        # Create a mock UI button press event
        mock_event = Mock()
        mock_event.type = pygame_gui.UI_BUTTON_PRESSED
        mock_event.ui_element = button.button
        
        # Set callback
        callback_called = False
        def test_callback(action):
            nonlocal callback_called
            callback_called = True
        
        button.set_action_callback(test_callback)
        
        # Handle event
        result = button.handle_event(mock_event)
        
        assert result is True
        assert callback_called
    
    def test_button_text_update(self, button):
        """Test button text update."""
        new_text = "Updated Button"
        button.set_text(new_text)
        
        assert button.text == new_text
        # Note: pygame_gui button text would also be updated
    
    def test_button_enable_disable(self, button):
        """Test button enable/disable functionality."""
        # Test disable
        button.set_enabled(False)
        assert button.enabled is False
        
        # Test enable
        button.set_enabled(True)
        assert button.enabled is True


class TestMoneyDisplayComponent:
    """Test suite for MoneyDisplay component."""
    
    @pytest.fixture
    def pygame_setup(self):
        """Setup pygame for testing."""
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        manager = pygame_gui.UIManager((800, 600))
        yield screen, manager
        pygame.quit()
    
    @pytest.fixture
    def money_display(self, pygame_setup):
        """Create money display instance for testing."""
        screen, manager = pygame_setup
        return MoneyDisplay(
            rect=pygame.Rect(10, 10, 150, 30),
            amount=1000,
            manager=manager
        )
    
    def test_money_display_initialization(self, pygame_setup):
        """Test money display initialization."""
        screen, manager = pygame_setup
        money_display = MoneyDisplay(
            rect=pygame.Rect(10, 10, 150, 30),
            amount=2741,
            manager=manager,
            config={
                'font_size': 16,
                'text_color': (255, 255, 255),
                'prefix': '$',
                'show_prefix': True
            }
        )
        
        assert money_display.amount == 2741
        assert money_display.config['font_size'] == 16
        assert money_display.config['text_color'] == (255, 255, 255)
        assert money_display.config['prefix'] == '$'
        assert money_display.config['show_prefix'] is True
        assert money_display.label is not None
    
    def test_money_display_with_container(self, pygame_setup):
        """Test money display with container."""
        screen, manager = pygame_setup
        
        # Create container
        window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect(100, 100, 400, 300),
            manager=manager,
            window_title="Test Window"
        )
        container = window.get_container()
        
        money_display = MoneyDisplay(
            rect=pygame.Rect(10, 10, 150, 30),
            amount=500,
            manager=manager,
            container=container
        )
        
        assert money_display.container == container
        assert money_display.label is not None
    
    def test_money_display_formatting(self, money_display):
        """Test money amount formatting."""
        # Test basic formatting
        money_display.amount = 1000
        formatted = money_display._format_amount()
        assert formatted == "$1,000"
        
        # Test large number
        money_display.amount = 2500000
        formatted = money_display._format_amount()
        assert formatted == "$2,500,000"
        
        # Test zero
        money_display.amount = 0
        formatted = money_display._format_amount()
        assert formatted == "$0"
    
    def test_money_display_update(self, money_display):
        """Test money display amount update."""
        # Update amount
        new_amount = 5000
        money_display.set_amount(new_amount)
        
        assert money_display.get_amount() == new_amount
    
    def test_money_display_add(self, money_display):
        """Test adding to money display amount."""
        initial_amount = money_display.get_amount()
        addition = 500
        
        money_display.add_amount(addition)
        
        assert money_display.get_amount() == initial_amount + addition
    
    def test_money_display_custom_prefix(self, pygame_setup):
        """Test custom prefix configuration."""
        screen, manager = pygame_setup
        
        money_display = MoneyDisplay(
            rect=pygame.Rect(10, 10, 150, 30),
            amount=100,
            manager=manager,
            config={'prefix': '€', 'show_prefix': True}
        )
        
        formatted = money_display._format_amount()
        assert formatted == "€100"
        
        # Test no prefix
        money_display.config['show_prefix'] = False
        formatted = money_display._format_amount()
        assert formatted == "100"


class TestContainerComponent:
    """Test suite for Container component."""
    
    @pytest.fixture
    def pygame_setup(self):
        """Setup pygame for testing."""
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        manager = pygame_gui.UIManager((800, 600))
        yield screen, manager
        pygame.quit()
    
    def test_container_initialization(self, pygame_setup):
        """Test container initialization."""
        screen, manager = pygame_setup
        container = Container(
            rect=pygame.Rect(10, 10, 400, 300),
            manager=manager,
            config={
                'layout_type': 'vertical',
                'spacing': 10,
                'padding': 5
            }
        )
        
        assert container.config['layout_type'] == 'vertical'
        assert container.config['spacing'] == 10
        assert container.config['padding'] == 5
    
    def test_container_add_child(self, pygame_setup):
        """Test adding children to container."""
        screen, manager = pygame_setup
        container = Container(
            rect=pygame.Rect(10, 10, 400, 300),
            manager=manager
        )
        
        # Add a button as child
        button = Button(
            rect=pygame.Rect(10, 10, 100, 30),
            text="Child Button",
            action="child",
            manager=manager
        )
        
        container.add_child(button)
        assert button in container.children
    
    def test_container_layout_vertical(self, pygame_setup):
        """Test vertical layout."""
        screen, manager = pygame_setup
        container = Container(
            rect=pygame.Rect(10, 10, 400, 300),
            manager=manager,
            config={'layout_type': 'vertical', 'spacing': 10}
        )
        
        # Add multiple buttons
        for i in range(3):
            button = Button(
                rect=pygame.Rect(10, 10, 100, 30),
                text=f"Button {i}",
                action=f"button_{i}",
                manager=manager
            )
            container.add_child(button)
        
        # Update container to apply layout
        container.update(0.016)
        
        # Verify vertical positioning
        # (Implementation depends on specific layout logic)


class TestPanelComponent:
    """Test suite for Panel component."""
    
    @pytest.fixture
    def pygame_setup(self):
        """Setup pygame for testing."""
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        manager = pygame_gui.UIManager((800, 600))
        yield screen, manager
        pygame.quit()
    
    def test_panel_initialization(self, pygame_setup):
        """Test panel initialization."""
        screen, manager = pygame_setup
        panel = Panel(
            rect=pygame.Rect(10, 10, 400, 300),
            title="Test Panel",
            manager=manager,
            config={
                'header_height': 40,
                'header_color': (50, 50, 50),
                'body_color': (240, 240, 240),
                'border_color': (100, 100, 100),
                'border_width': 2,
                'padding': 10
            }
        )
        
        assert panel.title == "Test Panel"
        assert panel.config['header_height'] == 40
        assert panel.config['header_color'] == (50, 50, 50)
        assert panel.config['body_color'] == (240, 240, 240)


class TestComponentReusability:
    """Test component reusability across different contexts."""
    
    @pytest.fixture
    def pygame_setup(self):
        """Setup pygame for testing."""
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        manager = pygame_gui.UIManager((800, 600))
        yield screen, manager
        pygame.quit()
    
    def test_button_reusability(self, pygame_setup):
        """Test button can be reused in different contexts."""
        screen, manager = pygame_setup
        
        # Create button in main context
        button1 = Button(
            rect=pygame.Rect(10, 10, 100, 30),
            text="Button 1",
            action="action1",
            manager=manager
        )
        
        # Create button in container context
        window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect(200, 200, 400, 300),
            manager=manager,
            window_title="Window"
        )
        container = window.get_container()
        
        button2 = Button(
            rect=pygame.Rect(10, 10, 100, 30),
            text="Button 2",
            action="action2",
            manager=manager,
            container=container
        )
        
        # Both should work independently
        assert button1.text == "Button 1"
        assert button2.text == "Button 2"
        assert button1.container is None
        assert button2.container == container
    
    def test_money_display_reusability(self, pygame_setup):
        """Test money display can be reused."""
        screen, manager = pygame_setup
        
        # Different money displays with different configurations
        display1 = MoneyDisplay(
            rect=pygame.Rect(10, 10, 150, 30),
            amount=1000,
            manager=manager,
            config={'font_size': 16, 'prefix': '$'}
        )
        
        display2 = MoneyDisplay(
            rect=pygame.Rect(10, 50, 150, 30),
            amount=2000,
            manager=manager,
            config={'font_size': 20, 'prefix': '€'}
        )
        
        assert display1.get_amount() == 1000
        assert display2.get_amount() == 2000
        assert display1.config['font_size'] == 16
        assert display2.config['font_size'] == 20


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
