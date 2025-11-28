#!/usr/bin/env python3
"""
Comprehensive test suite for Voting Panel (pygame_gui version).

This test suite verifies:
1. Voting panel initialization and setup
2. Voting options and candidate display
3. Vote submission and validation
4. Results display and statistics
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

from ui.panels.voting_panel import VotingPanel
from game.game_state_interface import TurboShellsGameStateInterface
from game.entities import Turtle


class TestVotingPanel:
    """Test suite for Voting Panel with pygame_gui."""
    
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
                self.current_vote = None
                self.voting_session_active = True
                self.voting_results = {}
                self.available_votes = []
                self.voting_history = []
                self.vote_cost = 50
                
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
                
            def submit_vote(self, vote_option):
                """Submit a vote and return success."""
                if self.current_vote is None:
                    return False
                    
                if vote_option not in self.current_vote['options']:
                    return False
                    
                if vote_option in self.voting_results:
                    self.voting_results[vote_option] += 1
                else:
                    self.voting_results[vote_option] = 1
                    
                self.voting_history.append({
                    'vote_id': self.current_vote['id'],
                    'choice': vote_option,
                    'timestamp': pygame.time.get_ticks()
                })
                
                return True
        
        return MockGame()
    
    @pytest.fixture
    def sample_voting_data(self):
        """Create sample voting data."""
        return {
            'id': 'vote_001',
            'title': 'Next Generation Trait Focus',
            'description': 'Vote on which trait should be enhanced in the next generation',
            'options': [
                {'id': 'speed', 'name': 'Enhanced Speed', 'description': 'Turtles will be faster'},
                {'id': 'energy', 'name': 'Enhanced Energy', 'description': 'Turtles will have more stamina'},
                {'id': 'recovery', 'name': 'Enhanced Recovery', 'description': 'Turtles will recover faster'},
                {'id': 'swim', 'name': 'Enhanced Swimming', 'description': 'Turtles will swim better'},
                {'id': 'climb', 'name': 'Enhanced Climbing', 'description': 'Turtles will climb better'}
            ],
            'cost': 50,
            'end_time': pygame.time.get_ticks() + 3600000  # 1 hour from now
        }
    
    @pytest.fixture
    def voting_panel(self, pygame_setup, mock_game_state, sample_voting_data):
        """Create voting panel for testing."""
        screen, manager = pygame_setup
        game_state_interface = TurboShellsGameStateInterface(mock_game_state)
        
        # Set up current vote
        mock_game_state.current_vote = sample_voting_data
        
        panel = VotingPanel(game_state_interface)
        panel.initialize(manager)
        
        return panel, manager, mock_game_state, sample_voting_data
    
    def test_voting_panel_initialization(self, voting_panel):
        """Test voting panel initialization."""
        panel, manager, game_state, vote_data = voting_panel
        
        # Verify panel creation
        assert panel is not None
        assert hasattr(panel, 'window')
        assert hasattr(panel, 'vote_options')
        assert hasattr(panel, 'vote_button')
        assert hasattr(panel, 'results_display')
        
        # Verify game state integration
        assert panel.game_state_interface is not None
        
        # Verify UI manager integration
        assert panel.ui_manager == manager
        
        # Verify initial setup
        assert len(panel.vote_options) == len(vote_data['options'])
        assert panel.vote_button is not None
        assert panel.results_display is not None
    
    def test_vote_option_display(self, voting_panel):
        """Test vote option display functionality."""
        panel, manager, game_state, vote_data = voting_panel
        
        # Verify each option has a display
        for i, option in enumerate(vote_data['options']):
            assert i < len(panel.vote_options)
            option_display = panel.vote_options[i]
            
            # Verify option display components
            assert option_display is not None
            assert hasattr(option_display, 'radio_button')
            assert hasattr(option_display, 'name_label')
            assert hasattr(option_display, 'description_label')
            
            # Verify option info displayed
            assert option['name'] in option_display.name_label.text
            assert option['description'] in option_display.description_label.text
            
            # Verify radio button not selected initially
            assert not option_display.radio_button.is_selected
    
    def test_vote_selection(self, voting_panel):
        """Test vote selection functionality."""
        panel, manager, game_state, vote_data = voting_panel
        
        # Get first option
        first_option = vote_data['options'][0]
        option_display = panel.vote_options[0]
        
        # Select option
        option_display.radio_button.selected = True
        option_display.radio_button.on_changed()
        
        # Verify selection processed
        assert option_display.radio_button.is_selected
        assert panel.selected_option == first_option['id']
        
        # Verify other options deselected
        for i in range(1, len(panel.vote_options)):
            other_option = panel.vote_options[i]
            assert not other_option.radio_button.is_selected
    
    def test_vote_button_state(self, voting_panel):
        """Test vote button state management."""
        panel, manager, game_state, vote_data = voting_panel
        
        # Initially disabled (no option selected)
        assert not panel.vote_button.enabled
        
        # Select an option
        option_display = panel.vote_options[0]
        option_display.radio_button.selected = True
        option_display.radio_button.on_changed()
        
        # Now enabled (option selected)
        assert panel.vote_button.enabled
        
        # Test insufficient funds
        game_state.money = 25  # Less than vote cost
        panel.update_vote_button_state()
        assert not panel.vote_button.enabled
        
        # Test voting session inactive
        game_state.voting_session_active = False
        game_state.money = 1000  # Restore funds
        panel.update_vote_button_state()
        assert not panel.vote_button.enabled
    
    def test_vote_submission(self, voting_panel):
        """Test vote submission process."""
        panel, manager, game_state, vote_data = voting_panel
        
        # Select an option
        option_display = panel.vote_options[0]
        option_display.radio_button.selected = True
        option_display.radio_button.on_changed()
        
        # Verify initial state
        initial_money = game_state.money
        vote_cost = vote_data['cost']
        assert game_state.can_afford(vote_cost)
        assert len(game_state.voting_results) == 0
        
        # Submit vote
        panel.vote_button.on_clicked()
        
        # Verify money deducted
        assert game_state.money == initial_money - vote_cost
        
        # Verify vote recorded
        assert len(game_state.voting_results) > 0
        selected_option_id = vote_data['options'][0]['id']
        assert selected_option_id in game_state.voting_results
        assert game_state.voting_results[selected_option_id] == 1
        
        # Verify voting history updated
        assert len(game_state.voting_history) == 1
        assert game_state.voting_history[0]['vote_id'] == vote_data['id']
        assert game_state.voting_history[0]['choice'] == selected_option_id
        
        # Verify vote button disabled after voting
        assert not panel.vote_button.enabled
        assert not option_display.radio_button.enabled
    
    def test_results_display(self, voting_panel):
        """Test voting results display."""
        panel, manager, game_state, vote_data = voting_panel
        
        # Add some mock results
        game_state.voting_results = {
            'speed': 15,
            'energy': 8,
            'recovery': 12,
            'swim': 5,
            'climb': 3
        }
        
        # Update results display
        panel.update_results_display()
        
        # Verify results displayed
        assert panel.results_display is not None
        assert hasattr(panel.results_display, 'result_labels')
        
        # Check each result displayed
        for option_id, vote_count in game_state.voting_results.items():
            # Find option name
            option_name = next(opt['name'] for opt in vote_data['options'] if opt['id'] == option_id)
            
            # Verify result displayed
            found = any(f"{option_name}" in label.text and f"{vote_count}" in label.text 
                       for label in panel.results_display.result_labels)
            assert found, f"Result for {option_name} with {vote_count} votes not found"
    
    def test_voting_cost_display(self, voting_panel):
        """Test voting cost display."""
        panel, manager, game_state, vote_data = voting_panel
        
        # Verify cost displayed
        assert hasattr(panel, 'cost_label')
        assert f"${vote_data['cost']}" in panel.cost_label.text
        
        # Update cost and verify display
        new_cost = 75
        game_state.current_vote['cost'] = new_cost
        panel.update_cost_display()
        assert f"${new_cost}" in panel.cost_label.text
    
    def test_voting_timer(self, voting_panel):
        """Test voting timer functionality."""
        panel, manager, game_state, vote_data = voting_panel
        
        # Verify timer display
        assert hasattr(panel, 'timer_label')
        
        # Test timer update
        current_time = pygame.time.get_ticks()
        end_time = vote_data['end_time']
        time_remaining = end_time - current_time
        
        panel.update_timer_display()
        
        # Verify timer shows remaining time
        # Note: Exact format depends on implementation
        assert panel.timer_label.text != ""
        
        # Test expired voting
        expired_time = current_time - 1000  # Expired
        game_state.current_vote['end_time'] = expired_time
        panel.update_timer_display()
        
        # Should show expired or voting closed
        assert "expired" in panel.timer_label.text.lower() or "closed" in panel.timer_label.text.lower()
    
    def test_voting_history_display(self, voting_panel):
        """Test voting history display."""
        panel, manager, game_state, vote_data = voting_panel
        
        # Add voting history
        game_state.voting_history = [
            {'vote_id': 'vote_001', 'choice': 'speed', 'timestamp': pygame.time.get_ticks() - 3600000},
            {'vote_id': 'vote_002', 'choice': 'energy', 'timestamp': pygame.time.get_ticks() - 7200000},
            {'vote_id': 'vote_003', 'choice': 'recovery', 'timestamp': pygame.time.get_ticks() - 10800000}
        ]
        
        # Update history display
        panel.update_history_display()
        
        # Verify history displayed
        assert hasattr(panel, 'history_display')
        assert len(panel.history_display.history_items) == len(game_state.voting_history)
        
        # Check each history item displayed
        for i, history_item in enumerate(game_state.voting_history):
            history_display = panel.history_display.history_items[i]
            assert history_item['choice'] in history_display.text
            assert history_item['vote_id'] in history_display.text
    
    def test_window_resize_handling(self, voting_panel):
        """Test window resize handling."""
        panel, manager, game_state, vote_data = voting_panel
        
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
        for option_display in panel.vote_options:
            assert option_display.radio_button.rect.right <= new_size[0]
            assert option_display.radio_button.rect.bottom <= new_size[1]
    
    def test_event_handling(self, voting_panel):
        """Test event handling integration."""
        panel, manager, game_state, vote_data = voting_panel
        
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
    
    def test_panel_visibility(self, voting_panel):
        """Test panel show/hide functionality."""
        panel, manager, game_state, vote_data = voting_panel
        
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
    
    def test_no_active_vote(self, voting_panel):
        """Test panel behavior when no active vote."""
        panel, manager, game_state, vote_data = voting_panel
        
        # Clear active vote
        game_state.current_vote = None
        panel.update_for_no_active_vote()
        
        # Verify panel shows no active vote message
        assert hasattr(panel, 'no_vote_label')
        assert "no active vote" in panel.no_vote_label.text.lower()
        
        # Verify voting options hidden
        for option_display in panel.vote_options:
            assert not option_display.visible
        
        # Verify vote button disabled
        assert not panel.vote_button.enabled
    
    def test_vote_validation(self, voting_panel):
        """Test vote validation logic."""
        panel, manager, game_state, vote_data = voting_panel
        
        # Test voting without selection
        panel.vote_button.on_clicked()
        
        # Should not process vote
        assert len(game_state.voting_results) == 0
        assert game_state.money == 1000  # Money not deducted
        
        # Test voting with insufficient funds
        option_display = panel.vote_options[0]
        option_display.radio_button.selected = True
        option_display.radio_button.on_changed()
        
        game_state.money = 25  # Less than cost
        panel.vote_button.on_clicked()
        
        # Should not process vote
        assert len(game_state.voting_results) == 0
        assert game_state.money == 25  # Money unchanged
        
        # Test voting when session inactive
        game_state.money = 1000  # Restore funds
        game_state.voting_session_active = False
        panel.vote_button.on_clicked()
        
        # Should not process vote
        assert len(game_state.voting_results) == 0
    
    def test_error_handling(self, voting_panel):
        """Test error handling in voting panel."""
        panel, manager, game_state, vote_data = voting_panel
        
        # Test invalid vote option
        try:
            panel.selected_option = 'invalid_option'
            panel.submit_vote()
            # Should handle gracefully
        except Exception as e:
            pytest.fail(f"Error handling failed: {e}")
        
        # Test missing game state
        try:
            panel.game_state_interface = None
            panel.update_vote_button_state()
        except Exception as e:
            # Should handle gracefully
            assert isinstance(e, (AttributeError, ValueError))
    
    def test_performance_with_many_options(self, voting_panel):
        """Test performance with many voting options."""
        panel, manager, game_state, vote_data = voting_panel
        
        import time
        
        # Create vote with many options
        many_options = []
        for i in range(50):
            many_options.append({
                'id': f'option_{i}',
                'name': f'Option {i}',
                'description': f'Description for option {i}'
            })
        
        game_state.current_vote['options'] = many_options
        
        # Test option creation performance
        start_time = time.time()
        panel.update_vote_options()
        end_time = time.time()
        
        # Should complete quickly (under 1 second)
        assert (end_time - start_time) < 1.0
        
        # Verify all options created
        assert len(panel.vote_options) == len(many_options)
    
    @pytest.mark.parametrize("vote_cost", [0, 25, 50, 100, 500])
    def test_different_vote_costs(self, voting_panel, vote_cost):
        """Test voting with different costs."""
        panel, manager, game_state, vote_data = voting_panel
        
        # Set vote cost
        game_state.current_vote['cost'] = vote_cost
        panel.update_cost_display()
        
        # Verify cost displayed
        assert f"${vote_cost}" in panel.cost_label.text
        
        # Test voting with exact funds
        game_state.money = vote_cost
        panel.update_vote_button_state()
        
        # Select option
        option_display = panel.vote_options[0]
        option_display.radio_button.selected = True
        option_display.radio_button.on_changed()
        
        # Should be able to vote
        if vote_cost > 0:
            assert panel.vote_button.enabled
        else:
            # Free vote should always be enabled
            assert panel.vote_button.enabled
    
    def test_voting_message_display(self, voting_panel):
        """Test voting message display and clearing."""
        panel, manager, game_state, vote_data = voting_panel
        
        # Set voting message
        test_message = "Vote submitted successfully!"
        panel.set_message(test_message)
        
        # Verify message displayed
        assert test_message in panel.message_label.text
        
        # Clear message
        panel.clear_message()
        
        # Verify message cleared
        assert test_message not in panel.message_label.text
    
    def test_vote_influence_calculation(self, voting_panel):
        """Test vote influence calculation and display."""
        panel, manager, game_state, vote_data = voting_panel
        
        # Add some voting results
        total_votes = 43
        game_state.voting_results = {
            'speed': 15,
            'energy': 8,
            'recovery': 12,
            'swim': 5,
            'climb': 3
        }
        
        # Update influence display
        panel.update_influence_display()
        
        # Verify influence percentages displayed
        assert hasattr(panel, 'influence_display')
        
        for option_id, vote_count in game_state.voting_results.items():
            expected_percentage = (vote_count / total_votes) * 100
            
            # Find option display
            option_name = next(opt['name'] for opt in vote_data['options'] if opt['id'] == option_id)
            
            # Verify percentage displayed (approximately)
            found = False
            for label in panel.influence_display.percentage_labels:
                if option_name in label.text:
                    # Check if percentage is displayed (format may vary)
                    if f"{expected_percentage:.1f}%" in label.text or f"{int(expected_percentage)}%" in label.text:
                        found = True
                        break
            
            assert found, f"Influence percentage for {option_name} not found"
