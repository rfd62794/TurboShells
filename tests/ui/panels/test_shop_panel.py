#!/usr/bin/env python3
"""
Comprehensive test suite for Shop Panel (pygame_gui version).

This test suite verifies:
1. Shop panel initialization and setup
2. Shop inventory display and management
3. Purchase interactions and validation
4. Money handling and game state integration
5. UI Manager integration
6. Event handling and callbacks
"""

import sys
import os
import pytest
import pygame
import pygame_gui
from unittest.mock import Mock, patch, MagicMock

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from ui.panels.shop_panel import ShopPanel
from game.game_state_interface import TurboShellsGameStateInterface
from game.entities import Turtle


class TestShopPanel:
    """Test suite for Shop Panel with pygame_gui."""
    
    @pytest.fixture
    def pygame_setup(self):
        """Setup pygame for testing."""
        pygame.init()
        screen = pygame.display.set_mode((1024, 768))
        manager = pygame_gui.UIManager((1024, 768))
        yield screen, manager
        pygame.quit()
    
    @pytest.fixture
    def mock_game_state(self):
        """Create mock game state for testing."""
        class MockGame:
            def __init__(self):
                self.money = 1000
                self.shop_inventory = []
                self.shop_message = ""
                self.roster = [None, None, None]
                
            def get(self, key, default=None):
                return getattr(self, key, default)
                
            def set(self, key, value):
                setattr(self, key, value)
                
            def add_turtle_to_roster(self, turtle):
                """Add turtle to first available slot."""
                for i, slot in enumerate(self.roster):
                    if slot is None:
                        self.roster[i] = turtle
                        return True
                return False
                
            def can_afford(self, cost):
                return self.money >= cost
                
            def spend_money(self, amount):
                if self.can_afford(amount):
                    self.money -= amount
                    return True
                return False
        
        return MockGame()
    
    @pytest.fixture
    def sample_turtles(self):
        """Create sample turtles for shop inventory."""
        turtles = []
        traits = ['speed', 'energy', 'recovery', 'swim', 'climb']
        
        for i in range(5):
            turtle = Turtle(f"Shop Turtle {i+1}")
            # Randomize stats
            for trait in traits:
                setattr(turtle, trait, 3 + (i % 5))
            turtles.append(turtle)
            
        return turtles
    
    @pytest.fixture
    def shop_panel(self, pygame_setup, mock_game_state, sample_turtles):
        """Create shop panel for testing."""
        screen, manager = pygame_setup
        game_state_interface = TurboShellsGameStateInterface(mock_game_state)
        
        # Add sample turtles to shop inventory
        mock_game_state.shop_inventory = sample_turtles
        
        panel = ShopPanel(game_state_interface)
        panel.initialize(manager)
        
        return panel, manager, mock_game_state, sample_turtles
    
    def test_shop_panel_initialization(self, shop_panel):
        """Test shop panel initialization."""
        panel, manager, game_state, turtles = shop_panel
        
        # Verify panel creation
        assert panel is not None
        assert hasattr(panel, 'window')
        assert hasattr(panel, 'turtle_cards')
        assert hasattr(panel, 'money_display')
        
        # Verify game state integration
        assert panel.game_state_interface is not None
        
        # Verify UI manager integration
        assert panel.ui_manager == manager
        
        # Verify initial setup
        assert len(panel.turtle_cards) == len(turtles)
        assert panel.money_display is not None
    
    def test_turtle_card_creation(self, shop_panel):
        """Test turtle card creation and display."""
        panel, manager, game_state, turtles = shop_panel
        
        # Verify each turtle has a card
        for i, turtle in enumerate(turtles):
            assert i < len(panel.turtle_cards)
            card = panel.turtle_cards[i]
            
            # Verify card displays turtle info
            assert card.turtle == turtle
            assert hasattr(card, 'name_label')
            assert hasattr(card, 'stats_labels')
            assert hasattr(card, 'price_label')
            assert hasattr(card, 'buy_button')
            
            # Verify card displays correct info
            assert turtle.name in card.name_label.text
            assert f"${turtle.calculate_price()}" in card.price_label.text
    
    def test_money_display(self, shop_panel):
        """Test money display functionality."""
        panel, manager, game_state, turtles = shop_panel
        
        # Verify initial money display
        assert panel.money_display is not None
        assert f"${game_state.money}" in panel.money_display.text
        
        # Update money and verify display updates
        game_state.money = 1500
        panel.update_money_display()
        assert f"${game_state.money}" in panel.money_display.text
    
    def test_purchase_interaction(self, shop_panel):
        """Test turtle purchase interaction."""
        panel, manager, game_state, turtles = shop_panel
        
        # Get first turtle and its card
        turtle = turtles[0]
        card = panel.turtle_cards[0]
        buy_button = card.buy_button
        
        # Verify initial state
        initial_money = game_state.money
        turtle_price = turtle.calculate_price()
        assert game_state.can_afford(turtle_price)
        assert buy_button.enabled
        
        # Simulate purchase
        buy_button.on_clicked()
        
        # Verify purchase processed
        assert game_state.money == initial_money - turtle_price
        assert turtle in game_state.roster
        assert not buy_button.enabled  # Should be disabled after purchase
        
        # Verify shop message
        assert "purchased" in game_state.shop_message.lower()
    
    def test_insufficient_funds(self, shop_panel):
        """Test purchase with insufficient funds."""
        panel, manager, game_state, turtles = shop_panel
        
        # Set money to insufficient amount
        game_state.money = 50
        panel.update_money_display()
        
        # Get first turtle's buy button
        card = panel.turtle_cards[0]
        buy_button = card.buy_button
        turtle_price = turtles[0].calculate_price()
        
        # Verify button disabled
        assert not game_state.can_afford(turtle_price)
        assert not buy_button.enabled
        
        # Try to purchase (should fail)
        buy_button.on_clicked()
        
        # Verify no purchase made
        assert game_state.money == 50
        assert turtles[0] not in game_state.roster
        
        # Verify error message
        assert "cannot afford" in game_state.shop_message.lower()
    
    def test_roster_full_handling(self, shop_panel):
        """Test purchase when roster is full."""
        panel, manager, game_state, turtles = shop_panel
        
        # Fill roster
        for i in range(3):
            game_state.roster[i] = Turtle(f"Roster Turtle {i+1}")
        
        # Try to purchase
        card = panel.turtle_cards[0]
        buy_button = card.buy_button
        
        # Verify purchase fails
        buy_button.on_clicked()
        
        # Verify no purchase made
        assert turtles[0] not in game_state.roster
        
        # Verify error message
        assert "roster is full" in game_state.shop_message.lower()
    
    def test_shop_refresh(self, shop_panel):
        """Test shop refresh functionality."""
        panel, manager, game_state, turtles = shop_panel
        
        # Get refresh button
        refresh_button = panel.refresh_button
        
        # Verify button exists
        assert refresh_button is not None
        
        # Mock shop manager refresh
        with patch.object(panel, 'refresh_shop_inventory') as mock_refresh:
            refresh_button.on_clicked()
            mock_refresh.assert_called_once()
    
    def test_inventory_update(self, shop_panel):
        """Test inventory update and UI refresh."""
        panel, manager, game_state, turtles = shop_panel
        
        # Add new turtle to inventory
        new_turtle = Turtle("New Shop Turtle")
        game_state.shop_inventory.append(new_turtle)
        
        # Update inventory display
        panel.update_inventory_display()
        
        # Verify new card created
        assert len(panel.turtle_cards) == len(turtles) + 1
        
        # Verify new card displays new turtle
        new_card = panel.turtle_cards[-1]
        assert new_card.turtle == new_turtle
        assert new_turtle.name in new_card.name_label.text
    
    def test_card_hover_effects(self, shop_panel):
        """Test turtle card hover effects."""
        panel, manager, game_state, turtles = shop_panel
        
        # Get first card
        card = panel.turtle_cards[0]
        
        # Simulate mouse hover
        mouse_pos = card.rect.center
        hover_event = pygame.event.Event(
            pygame.MOUSEMOTION,
            {'pos': mouse_pos}
        )
        
        # Handle hover event
        panel.handle_event(hover_event)
        
        # Verify hover state (implementation dependent)
        # This would test visual feedback like highlighting
    
    def test_window_resize_handling(self, shop_panel):
        """Test window resize handling."""
        panel, manager, game_state, turtles = shop_panel
        
        # Simulate window resize
        new_size = (1280, 720)
        
        # Handle resize
        panel.handle_window_resize(new_size)
        
        # Verify UI manager updated
        assert manager.window_resolution == new_size
        
        # Verify panel adjusted
        assert panel.window.rect.width <= new_size[0]
        assert panel.window.rect.height <= new_size[1]
        
        # Verify cards repositioned
        for card in panel.turtle_cards:
            assert card.rect.right <= new_size[0]
            assert card.rect.bottom <= new_size[1]
    
    def test_event_handling(self, shop_panel):
        """Test event handling integration."""
        panel, manager, game_state, turtles = shop_panel
        
        # Create test events
        mouse_click_event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {'pos': (100, 100), 'button': 1}
        )
        
        key_press_event = pygame.event.Event(
            pygame.KEYDOWN,
            {'key': pygame.K_ESCAPE, 'mod': 0}
        )
        
        # Test event handling
        result1 = panel.handle_event(mouse_click_event)
        result2 = panel.handle_event(key_press_event)
        
        # Events should be processed
        assert isinstance(result1, bool)
        assert isinstance(result2, bool)
    
    def test_panel_visibility(self, shop_panel):
        """Test panel show/hide functionality."""
        panel, manager, game_state, turtles = shop_panel
        
        # Initially visible
        assert panel.visible
        
        # Hide panel
        panel.hide()
        assert not panel.visible
        assert not panel.window.visible
        
        # Show panel
        panel.show()
        assert panel.visible
        assert panel.window.visible
    
    def test_turtle_price_calculation(self, shop_panel):
        """Test turtle price calculation and display."""
        panel, manager, game_state, turtles = shop_panel
        
        for i, turtle in enumerate(turtles):
            card = panel.turtle_cards[i]
            
            # Calculate expected price
            expected_price = turtle.calculate_price()
            
            # Verify price displayed correctly
            assert f"${expected_price}" in card.price_label.text
            
            # Verify price is reasonable
            assert 50 <= expected_price <= 1000
    
    def test_stats_display(self, shop_panel):
        """Test turtle stats display on cards."""
        panel, manager, game_state, turtles = shop_panel
        
        for i, turtle in enumerate(turtles):
            card = panel.turtle_cards[i]
            
            # Verify stats labels exist
            assert hasattr(card, 'stats_labels')
            assert len(card.stats_labels) >= 5  # speed, energy, recovery, swim, climb
            
            # Verify stats displayed
            stats = ['speed', 'energy', 'recovery', 'swim', 'climb']
            for stat in stats:
                stat_value = getattr(turtle, stat)
                # Check if stat value appears in any label
                found = any(str(stat_value) in label.text for label in card.stats_labels)
                assert found, f"Stat {stat} with value {stat_value} not found in display"
    
    def test_error_handling(self, shop_panel):
        """Test error handling in shop panel."""
        panel, manager, game_state, turtles = shop_panel
        
        # Test invalid turtle in inventory
        invalid_turtle = None
        game_state.shop_inventory.append(invalid_turtle)
        
        try:
            panel.update_inventory_display()
            # Should handle gracefully
        except Exception as e:
            pytest.fail(f"Error handling failed: {e}")
        
        # Test missing game state
        try:
            panel.game_state_interface = None
            panel.update_money_display()
        except Exception as e:
            # Should handle gracefully
            assert isinstance(e, (AttributeError, ValueError))
    
    def test_performance_with_large_inventory(self, shop_panel):
        """Test performance with large shop inventory."""
        panel, manager, game_state, turtles = shop_panel
        
        import time
        
        # Add many turtles to inventory
        large_inventory = []
        for i in range(50):
            turtle = Turtle(f"Bulk Turtle {i}")
            large_inventory.append(turtle)
        
        game_state.shop_inventory = large_inventory
        
        # Test inventory update performance
        start_time = time.time()
        panel.update_inventory_display()
        end_time = time.time()
        
        # Should complete quickly (under 2 seconds)
        assert (end_time - start_time) < 2.0
        
        # Verify all cards created
        assert len(panel.turtle_cards) == len(large_inventory)
    
    @pytest.mark.parametrize("money_amount", [0, 50, 500, 1000, 5000])
    def test_different_money_amounts(self, shop_panel, money_amount):
        """Test shop behavior with different money amounts."""
        panel, manager, game_state, turtles = shop_panel
        
        # Set money amount
        game_state.money = money_amount
        panel.update_money_display()
        
        # Verify money display updated
        assert f"${money_amount}" in panel.money_display.text
        
        # Verify buy button states
        for i, turtle in enumerate(turtles):
            card = panel.turtle_cards[i]
            buy_button = card.buy_button
            
            if game_state.can_afford(turtle.calculate_price()):
                assert buy_button.enabled
            else:
                assert not buy_button.enabled
    
    def test_shop_message_display(self, shop_panel):
        """Test shop message display and clearing."""
        panel, manager, game_state, turtles = shop_panel
        
        # Set shop message
        test_message = "Test shop message"
        game_state.shop_message = test_message
        panel.update_message_display()
        
        # Verify message displayed
        assert panel.message_label is not None
        assert test_message in panel.message_label.text
        
        # Clear message
        game_state.shop_message = ""
        panel.update_message_display()
        
        # Verify message cleared (or shows default)
        assert test_message not in panel.message_label.text
