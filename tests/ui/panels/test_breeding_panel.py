#!/usr/bin/env python3
"""
Comprehensive test suite for Breeding Panel (pygame_gui version).

This test suite verifies:
1. Breeding panel initialization and setup
2. Parent selection and validation
3. Breeding mechanics and genetics inheritance
4. Offspring generation and traits
5. Game state integration
6. UI Manager integration
"""

import sys
import os
import pytest
import pygame
import pygame_gui
from unittest.mock import Mock, patch, MagicMock

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from ui.panels.breeding_panel import BreedingPanel
from game.game_state_interface import TurboShellsGameStateInterface
from game.entities import Turtle


class TestBreedingPanel:
    """Test suite for Breeding Panel with pygame_gui."""
    
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
                self.money = 2000
                self.breeding_parents = []
                self.roster = []
                self.retired_roster = []
                self.breeding_cost = 100
                
            def get(self, key, default=None):
                return getattr(self, key, default)
                
            def set(self, key, value):
                setattr(self, key, value)
                
            def can_afford(self, cost):
                return self.money >= cost
                
            def spend_money(self, amount):
                if self.can_afford(amount):
                    self.money -= amount
                    return True
                return False
                
            def get_available_parents(self):
                """Get all turtles available for breeding."""
                return [t for t in self.roster + self.retired_roster if t is not None]
        
        return MockGame()
    
    @pytest.fixture
    def sample_turtles(self):
        """Create sample turtles for breeding."""
        parents = []
        
        # Create diverse parents with different traits
        parent1 = Turtle("Speedy Parent")
        parent1.speed = 8
        parent1.energy = 5
        parent1.recovery = 4
        parent1.swim = 6
        parent1.climb = 3
        parent1.generation = 2
        
        parent2 = Turtle("Sturdy Parent")
        parent2.speed = 4
        parent2.energy = 8
        parent2.recovery = 7
        parent2.swim = 3
        parent2.climb = 6
        parent2.generation = 3
        
        parent3 = Turtle("Balanced Parent")
        parent3.speed = 5
        parent3.energy = 6
        parent3.recovery = 5
        parent3.swim = 5
        parent3.climb = 5
        parent3.generation = 1
        
        parents = [parent1, parent2, parent3]
        
        # Create some offspring
        offspring = []
        for i in range(3):
            child = Turtle(f"Offspring {i+1}")
            child.speed = 5 + (i % 3)
            child.energy = 5 + ((i + 1) % 3)
            child.recovery = 5 + ((i + 2) % 3)
            child.swim = 5 + (i % 2)
            child.climb = 5 + ((i + 1) % 2)
            child.generation = 4
            child.parents = [parent1, parent2]
            offspring.append(child)
            
        return parents, offspring
    
    @pytest.fixture
    def breeding_panel(self, pygame_setup, mock_game_state, sample_turtles):
        """Create breeding panel for testing."""
        screen, manager = pygame_setup
        game_state_interface = TurboShellsGameStateInterface(mock_game_state)
        
        parents, offspring = sample_turtles
        mock_game_state.roster = parents
        mock_game_state.retired_roster = offspring
        
        panel = BreedingPanel(game_state_interface)
        panel.initialize(manager)
        
        return panel, manager, mock_game_state, parents, offspring
    
    def test_breeding_panel_initialization(self, breeding_panel):
        """Test breeding panel initialization."""
        panel, manager, game_state, parents, offspring = breeding_panel
        
        # Verify panel creation
        assert panel is not None
        assert hasattr(panel, 'window')
        assert hasattr(panel, 'parent_selectors')
        assert hasattr(panel, 'breed_button')
        assert hasattr(panel, 'offspring_display')
        
        # Verify game state integration
        assert panel.game_state_interface is not None
        
        # Verify UI manager integration
        assert panel.ui_manager == manager
        
        # Verify initial setup
        assert len(panel.parent_selectors) == 2  # Two parent selectors
        assert panel.breed_button is not None
        assert panel.offspring_display is not None
    
    def test_parent_selector_initialization(self, breeding_panel):
        """Test parent selector initialization."""
        panel, manager, game_state, parents, offspring = breeding_panel
        
        # Verify parent selectors
        for i, selector in enumerate(panel.parent_selectors):
            assert selector is not None
            assert hasattr(selector, 'dropdown')
            assert hasattr(selector, 'info_display')
            
            # Verify dropdown populated with available turtles
            available_turtles = game_state.get_available_parents()
            assert len(selector.dropdown.options_list) == len(available_turtles)
            
            # Verify each turtle appears in dropdown
            for turtle in available_turtles:
                assert turtle.name in selector.dropdown.options_list
    
    def test_parent_selection(self, breeding_panel):
        """Test parent selection functionality."""
        panel, manager, game_state, parents, offspring = breeding_panel
        
        # Get first parent selector
        selector1 = panel.parent_selectors[0]
        selector2 = panel.parent_selectors[1]
        
        # Select first parent
        first_turtle = parents[0]
        selector1.dropdown.selected_option = first_turtle.name
        selector1.dropdown.on_changed()
        
        # Verify selection processed
        assert selector1.selected_turtle == first_turtle
        assert first_turtle.name in selector1.info_display.text
        
        # Select second parent (different from first)
        second_turtle = parents[1]
        selector2.dropdown.selected_option = second_turtle.name
        selector2.dropdown.on_changed()
        
        # Verify selection processed
        assert selector2.selected_turtle == second_turtle
        assert second_turtle.name in selector2.info_display.text
        
        # Verify breeding parents updated
        assert len(game_state.breeding_parents) == 2
        assert first_turtle in game_state.breeding_parents
        assert second_turtle in game_state.breeding_parents
    
    def test_same_parent_validation(self, breeding_panel):
        """Test validation preventing same parent selection."""
        panel, manager, game_state, parents, offspring = breeding_panel
        
        # Select same parent for both slots
        selector1 = panel.parent_selectors[0]
        selector2 = panel.parent_selectors[1]
        
        same_turtle = parents[0]
        
        # Select for first parent
        selector1.dropdown.selected_option = same_turtle.name
        selector1.dropdown.on_changed()
        
        # Try to select same turtle for second parent
        selector2.dropdown.selected_option = same_turtle.name
        selector2.dropdown.on_changed()
        
        # Should prevent selection
        assert selector2.selected_turtle != same_turtle
        assert len(game_state.breeding_parents) <= 1
    
    def test_breed_button_state(self, breeding_panel):
        """Test breed button state management."""
        panel, manager, game_state, parents, offspring = breeding_panel
        
        # Initially disabled (no parents selected)
        assert not panel.breed_button.enabled
        
        # Select one parent
        selector1 = panel.parent_selectors[0]
        selector1.dropdown.selected_option = parents[0].name
        selector1.dropdown.on_changed()
        
        # Still disabled (need two parents)
        assert not panel.breed_button.enabled
        
        # Select second parent
        selector2 = panel.parent_selectors[1]
        selector2.dropdown.selected_option = parents[1].name
        selector2.dropdown.on_changed()
        
        # Now enabled (have two parents)
        assert panel.breed_button.enabled
        
        # Test insufficient funds
        game_state.money = 50
        panel.update_breed_button_state()
        assert not panel.breed_button.enabled
    
    def test_breeding_process(self, breeding_panel):
        """Test the breeding process."""
        panel, manager, game_state, parents, offspring = breeding_panel
        
        # Select parents
        selector1 = panel.parent_selectors[0]
        selector2 = panel.parent_selectors[1]
        
        selector1.dropdown.selected_option = parents[0].name
        selector1.dropdown.on_changed()
        
        selector2.dropdown.selected_option = parents[1].name
        selector2.dropdown.on_changed()
        
        # Verify breeding cost
        breeding_cost = game_state.breeding_cost
        initial_money = game_state.money
        assert game_state.can_afford(breeding_cost)
        
        # Perform breeding
        panel.breed_button.on_clicked()
        
        # Verify money deducted
        assert game_state.money == initial_money - breeding_cost
        
        # Verify offspring created
        assert len(panel.offspring_display.offspring) > 0
        
        # Verify offspring traits
        offspring = panel.offspring_display.offspring[0]
        assert offspring.name.startswith("Offspring")
        assert offspring.generation > max(parents[0].generation, parents[1].generation)
        assert offspring.parents == [parents[0], parents[1]]
    
    def test_genetics_inheritance(self, breeding_panel):
        """Test genetics inheritance patterns."""
        panel, manager, game_state, parents, offspring = breeding_panel
        
        # Select parents with distinct traits
        selector1 = panel.parent_selectors[0]
        selector2 = panel.parent_selectors[1]
        
        selector1.dropdown.selected_option = parents[0].name  # High speed, low energy
        selector1.dropdown.on_changed()
        
        selector2.dropdown.selected_option = parents[1].name  # Low speed, high energy
        selector2.dropdown.on_changed()
        
        # Perform breeding
        panel.breed_button.on_clicked()
        
        # Verify offspring inherits traits
        child = panel.offspring_display.offspring[0]
        
        # Traits should be between parents (with some variation)
        parent1_speed = parents[0].speed
        parent2_speed = parents[1].speed
        
        # Allow for mutation (+/- 2)
        min_expected = min(parent1_speed, parent2_speed) - 2
        max_expected = max(parent1_speed, parent2_speed) + 2
        
        assert min_expected <= child.speed <= max_expected
        
        # Verify other traits also inherited
        traits = ['energy', 'recovery', 'swim', 'climb']
        for trait in traits:
            parent1_val = getattr(parents[0], trait)
            parent2_val = getattr(parents[1], trait)
            child_val = getattr(child, trait)
            
            min_expected = min(parent1_val, parent2_val) - 2
            max_expected = max(parent1_val, parent2_val) + 2
            assert min_expected <= child_val <= max_expected
    
    def test_offspring_display(self, breeding_panel):
        """Test offspring display functionality."""
        panel, manager, game_state, parents, offspring = breeding_panel
        
        # Select parents and breed
        selector1 = panel.parent_selectors[0]
        selector2 = panel.parent_selectors[1]
        
        selector1.dropdown.selected_option = parents[0].name
        selector1.dropdown.on_changed()
        
        selector2.dropdown.selected_option = parents[1].name
        selector2.dropdown.on_changed()
        
        panel.breed_button.on_clicked()
        
        # Verify offspring display updated
        assert len(panel.offspring_display.offspring_cards) > 0
        
        # Check first offspring card
        offspring_card = panel.offspring_display.offspring_cards[0]
        child = panel.offspring_display.offspring[0]
        
        # Verify card displays offspring info
        assert child.name in offspring_card.name_label.text
        assert f"Gen {child.generation}" in offspring_card.generation_label.text
        
        # Verify stats displayed
        stats = ['speed', 'energy', 'recovery', 'swim', 'climb']
        for stat in stats:
            stat_value = getattr(child, stat)
            found = any(str(stat_value) in label.text for label in offspring_card.stats_labels)
            assert found, f"Stat {stat} not found in offspring display"
    
    def test_keep_offspring_functionality(self, breeding_panel):
        """Test keeping offspring functionality."""
        panel, manager, game_state, parents, offspring = breeding_panel
        
        # Breed to create offspring
        selector1 = panel.parent_selectors[0]
        selector2 = panel.parent_selectors[1]
        
        selector1.dropdown.selected_option = parents[0].name
        selector1.dropdown.on_changed()
        
        selector2.dropdown.selected_option = parents[1].name
        selector2.dropdown.on_changed()
        
        panel.breed_button.on_clicked()
        
        # Get offspring and keep button
        child = panel.offspring_display.offspring[0]
        offspring_card = panel.offspring_display.offspring_cards[0]
        keep_button = offspring_card.keep_button
        
        # Verify roster has space
        initial_roster_size = len([t for t in game_state.roster if t is not None])
        assert initial_roster_size < 3  # Assuming max 3 roster slots
        
        # Keep offspring
        keep_button.on_clicked()
        
        # Verify offspring added to roster
        assert child in game_state.roster
        assert len([t for t in game_state.roster if t is not None]) == initial_roster_size + 1
        
        # Verify keep button disabled
        assert not keep_button.enabled
    
    def test_roster_full_handling(self, breeding_panel):
        """Test keeping offspring when roster is full."""
        panel, manager, game_state, parents, offspring = breeding_panel
        
        # Fill roster
        for i in range(3):
            game_state.roster[i] = Turtle(f"Roster Turtle {i+1}")
        
        # Breed offspring
        selector1 = panel.parent_selectors[0]
        selector2 = panel.parent_selectors[1]
        
        selector1.dropdown.selected_option = parents[0].name
        selector1.dropdown.on_changed()
        
        selector2.dropdown.selected_option = parents[1].name
        selector2.dropdown.on_changed()
        
        panel.breed_button.on_clicked()
        
        # Try to keep offspring
        child = panel.offspring_display.offspring[0]
        offspring_card = panel.offspring_display.offspring_cards[0]
        keep_button = offspring_card.keep_button
        
        # Should fail due to full roster
        keep_button.on_clicked()
        
        # Verify offspring not added to roster
        assert child not in game_state.roster
        
        # Verify error message displayed
        assert "roster is full" in panel.message_label.text.lower()
    
    def test_breeding_cost_display(self, breeding_panel):
        """Test breeding cost display."""
        panel, manager, game_state, parents, offspring = breeding_panel
        
        # Verify cost displayed
        assert hasattr(panel, 'cost_label')
        assert f"${game_state.breeding_cost}" in panel.cost_label.text
        
        # Update cost and verify display
        game_state.breeding_cost = 250
        panel.update_cost_display()
        assert f"${game_state.breeding_cost}" in panel.cost_label.text
    
    def test_window_resize_handling(self, breeding_panel):
        """Test window resize handling."""
        panel, manager, game_state, parents, offspring = breeding_panel
        
        # Simulate window resize
        new_size = (1280, 720)
        
        # Handle resize
        panel.handle_window_resize(new_size)
        
        # Verify UI manager updated
        assert manager.window_resolution == new_size
        
        # Verify panel adjusted
        assert panel.window.rect.width <= new_size[0]
        assert panel.window.rect.height <= new_size[1]
        
        # Verify components repositioned
        for selector in panel.parent_selectors:
            assert selector.dropdown.rect.right <= new_size[0]
            assert selector.dropdown.rect.bottom <= new_size[1]
    
    def test_event_handling(self, breeding_panel):
        """Test event handling integration."""
        panel, manager, game_state, parents, offspring = breeding_panel
        
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
    
    def test_panel_visibility(self, breeding_panel):
        """Test panel show/hide functionality."""
        panel, manager, game_state, parents, offspring = breeding_panel
        
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
    
    def test_error_handling(self, breeding_panel):
        """Test error handling in breeding panel."""
        panel, manager, game_state, parents, offspring = breeding_panel
        
        # Test invalid parent selection
        try:
            # Select non-existent parent
            selector = panel.parent_selectors[0]
            selector.dropdown.selected_option = "NonExistent Turtle"
            selector.dropdown.on_changed()
            # Should handle gracefully
        except Exception as e:
            pytest.fail(f"Error handling failed: {e}")
        
        # Test missing game state
        try:
            panel.game_state_interface = None
            panel.update_breed_button_state()
        except Exception as e:
            # Should handle gracefully
            assert isinstance(e, (AttributeError, ValueError))
    
    def test_performance_with_many_turtles(self, breeding_panel):
        """Test performance with many available turtles."""
        panel, manager, game_state, parents, offspring = breeding_panel
        
        import time
        
        # Add many turtles to roster
        large_roster = []
        for i in range(50):
            turtle = Turtle(f"Bulk Turtle {i}")
            large_roster.append(turtle)
        
        game_state.roster = large_roster
        
        # Test parent selector update performance
        start_time = time.time()
        panel.update_parent_selectors()
        end_time = time.time()
        
        # Should complete quickly (under 1 second)
        assert (end_time - start_time) < 1.0
        
        # Verify selectors updated
        for selector in panel.parent_selectors:
            assert len(selector.dropdown.options_list) == len(large_roster)
    
    @pytest.mark.parametrize("generation_diff", [0, 1, 2, 5])
    def test_generation_inheritance(self, breeding_panel, generation_diff):
        """Test generation inheritance with different generation gaps."""
        panel, manager, game_state, parents, offspring = breeding_panel
        
        # Set parent generations
        parents[0].generation = 2
        parents[1].generation = 2 + generation_diff
        
        # Select parents and breed
        selector1 = panel.parent_selectors[0]
        selector2 = panel.parent_selectors[1]
        
        selector1.dropdown.selected_option = parents[0].name
        selector1.dropdown.on_changed()
        
        selector2.dropdown.selected_option = parents[1].name
        selector2.dropdown.on_changed()
        
        panel.breed_button.on_clicked()
        
        # Verify offspring generation
        child = panel.offspring_display.offspring[0]
        expected_generation = max(parents[0].generation, parents[1].generation) + 1
        assert child.generation == expected_generation
    
    def test_breeding_message_display(self, breeding_panel):
        """Test breeding message display and clearing."""
        panel, manager, game_state, parents, offspring = breeding_panel
        
        # Set breeding message
        test_message = "Breeding successful!"
        panel.set_message(test_message)
        
        # Verify message displayed
        assert test_message in panel.message_label.text
        
        # Clear message
        panel.clear_message()
        
        # Verify message cleared
        assert test_message not in panel.message_label.text
