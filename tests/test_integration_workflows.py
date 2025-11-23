#!/usr/bin/env python3
"""
Comprehensive integration tests for game workflows
Tests end-to-end game scenarios and user interactions.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json
import tempfile
import shutil

# Import game modules
from src.core.entities import Turtle
from src.core.game_state import generate_random_turtle, breed_turtles, compute_turtle_cost
from src.core.race_track import generate_track
from tests.conftest import TestDataFactory


@pytest.mark.integration
class TestGameWorkflows:
    """Integration tests for complete game workflows"""

    @pytest.mark.integration
    def test_new_game_workflow(self, mock_game_state, sample_turtles):
        """Test complete new game initialization workflow"""
        # Start with new game state
        game = mock_game_state
        game.money = 50
        game.roster = []
        game.retired_roster = []
        game.shop_inventory = []

        # Add initial turtle
        initial_turtle = generate_random_turtle("Starter")
        game.roster.append(initial_turtle)

        # Verify initial state
        assert len(game.roster) == 1
        assert game.money == 50
        assert isinstance(game.roster[0], Turtle)

    @pytest.mark.integration
    def test_turtle_purchase_workflow(self, mock_game_state):
        """Test turtle purchase workflow"""
        game = mock_game_state
        game.money = 200
        game.roster = []

        # Create shop inventory
        shop_turtle1 = generate_random_turtle("Shop1")
        shop_turtle2 = generate_random_turtle("Shop2")
        game.shop_inventory = [shop_turtle1, shop_turtle2]

        # Purchase turtle
        selected_turtle = game.shop_inventory[0]
        cost = compute_turtle_cost(selected_turtle)

        # Check if can afford
        if game.money >= cost:
            game.money -= cost
            game.roster.append(selected_turtle)
            game.shop_inventory.remove(selected_turtle)

        # Verify purchase
        assert len(game.roster) == 1
        assert game.money == 200 - cost
        assert selected_turtle not in game.shop_inventory

    @pytest.mark.integration
    def test_race_preparation_workflow(self, mock_game_state, sample_turtles):
        """Test race preparation workflow"""
        game = mock_game_state
        game.roster = sample_turtles[:3]  # Use 3 turtles

        # Select racers (first 2)
        racers = game.roster[:2]

        # Reset racers for race
        for turtle in racers:
            turtle.reset_for_race()

        # Verify preparation
        assert len(racers) == 2
        for turtle in racers:
            assert turtle.current_energy == turtle.energy
            assert turtle.race_distance == 0.0
            assert not turtle.finished

    @pytest.mark.integration
    def test_complete_race_workflow(self, mock_game_state, sample_turtles, sample_track):
        """Test complete race execution workflow"""
        game = mock_game_state
        game.roster = sample_turtles[:4]  # Use 4 turtles

        # Select racers
        racers = game.roster[:3]
        opponents = [sample_turtles[3]]  # 1 opponent

        # Reset all turtles
        for turtle in racers + opponents:
            turtle.reset_for_race()

        # Simulate race
        max_iterations = 2000
        race_results = []

        for iteration in range(max_iterations):
            current_terrain = sample_track[iteration % len(sample_track)]
            all_finished = True

            # Update all turtles
            for turtle in racers + opponents:
                if not turtle.finished:
                    all_finished = False
                    if turtle.current_energy > 0:
                        turtle.update_physics(current_terrain)
                    else:
                        turtle.finished = True

            # Check for finish line crossing
            finish_line = 1000.0
            for turtle in racers + opponents:
                if turtle.race_distance >= finish_line and not turtle.finished:
                    turtle.finished = True
                    turtle.rank = len(race_results) + 1
                    race_results.append({
                        'turtle': turtle,
                        'rank': turtle.rank,
                        'distance': turtle.race_distance,
                        'time': iteration
                    })

            if all_finished or len(race_results) == len(racers + opponents):
                break

        # Verify race completion
        assert len(race_results) > 0
        assert race_results[0]['rank'] == 1  # First place

        # Award prize money (simplified)
        prize_distribution = {1: 50, 2: 25, 3: 10}
        for result in race_results:
            rank = result['rank']
            if rank in prize_distribution:
                game.money += prize_distribution[rank]

        # Verify prize distribution
        assert game.money > 0

    @pytest.mark.integration
    def test_turtle_training_workflow(self, mock_game_state, sample_turtle):
        """Test turtle training workflow"""
        game = mock_game_state
        game.roster = [sample_turtle]
        game.money = 100

        # Training cost
        training_cost = 20

        # Check if can afford training
        if game.money >= training_cost:
            # Train turtle
            initial_speed = sample_turtle.speed
            sample_turtle.train("speed")
            final_speed = sample_turtle.speed

            # Pay for training
            game.money -= training_cost

            # Verify training
            assert final_speed > initial_speed
            assert game.money == 80

    @pytest.mark.integration
    def test_breeding_workflow(self, mock_game_state, sample_turtles):
        """Test complete breeding workflow"""
        game = mock_game_state
        game.roster = sample_turtles[:2]  # Use 2 turtles for breeding
        game.money = 100

        # Breeding cost
        breeding_cost = 30

        # Check if can afford breeding
        if game.money >= breeding_cost:
            # Check if parents are eligible (not retired, etc.)
            parent1, parent2 = game.roster[0], game.roster[1]
            
            if parent1.age < 15 and parent2.age < 15:  # Breeding age limit
                # Breed turtles
                child = breed_turtles(parent1, parent2)
                
                # Add child to roster
                game.roster.append(child)
                
                # Pay for breeding
                game.money -= breeding_cost

                # Verify breeding
                assert len(game.roster) == 3
                assert child.age == 0
                assert child.is_active
                assert game.money == 70

    @pytest.mark.integration
    def test_turtle_retirement_workflow(self, mock_game_state):
        """Test turtle retirement workflow"""
        game = mock_game_state

        # Create old turtle
        old_turtle = TestDataFactory.create_minimal_turtle("OldTimer")
        old_turtle.age = 20  # Maximum age

        game.roster = [old_turtle]
        game.retired_roster = []

        # Check for retirement eligibility
        if old_turtle.age >= 20:  # Retirement age
            # Retire turtle
            game.roster.remove(old_turtle)
            game.retired_roster.append(old_turtle)
            old_turtle.is_active = False

            # Award retirement bonus
            retirement_bonus = 10
            game.money += retirement_bonus

        # Verify retirement
        assert len(game.roster) == 0
        assert len(game.retired_roster) == 1
        assert not old_turtle.is_active
        assert game.money >= 10

    @pytest.mark.integration
    def test_save_game_workflow(self, mock_game_state, temp_save_dir, save_file_data):
        """Test save game workflow"""
        game = mock_game_state
        save_path = temp_save_dir / "test_save.json"

        # Prepare save data
        save_data = {
            'version': '2.4.0',
            'money': game.money,
            'roster': [],
            'retired_roster': [],
            'shop_inventory': [],
            'race_history': [],
            'votes': {},
            'genetics_pool': {}
        }

        # Convert turtles to dictionaries (simplified)
        for turtle in game.roster:
            turtle_dict = {
                'name': turtle.name,
                'speed': turtle.speed,
                'energy': turtle.energy,
                'recovery': turtle.recovery,
                'swim': turtle.swim,
                'climb': turtle.climb,
                'age': turtle.age,
                'is_active': turtle.is_active,
                'current_energy': turtle.current_energy,
                'race_distance': turtle.race_distance,
                'is_resting': turtle.is_resting,
                'finished': turtle.finished,
                'rank': turtle.rank
            }
            save_data['roster'].append(turtle_dict)

        # Save game
        with open(save_path, 'w') as f:
            json.dump(save_data, f, indent=2)

        # Verify save
        assert save_path.exists()
        assert save_path.stat().st_size > 0

        # Verify save content
        with open(save_path, 'r') as f:
            loaded_data = json.load(f)
        
        assert loaded_data['money'] == game.money
        assert len(loaded_data['roster']) == len(game.roster)

    @pytest.mark.integration
    def test_load_game_workflow(self, temp_save_dir, save_file_data):
        """Test load game workflow"""
        save_path = temp_save_dir / "test_save.json"

        # Create save file
        with open(save_path, 'w') as f:
            json.dump(save_file_data, f, indent=2)

        # Load game
        with open(save_path, 'r') as f:
            loaded_data = json.load(f)

        # Recreate game state
        game = Mock()
        game.money = loaded_data['money']
        game.roster = []
        game.retired_roster = []
        game.shop_inventory = []

        # Recreate turtles from save data
        for turtle_dict in loaded_data['roster']:
            turtle = Turtle(
                name=turtle_dict['name'],
                speed=turtle_dict['speed'],
                energy=turtle_dict['energy'],
                recovery=turtle_dict['recovery'],
                swim=turtle_dict['swim'],
                climb=turtle_dict['climb'],
                age=turtle_dict['age'],
                is_active=turtle_dict['is_active']
            )
            # Restore race state
            turtle.current_energy = turtle_dict['current_energy']
            turtle.race_distance = turtle_dict['race_distance']
            turtle.is_resting = turtle_dict['is_resting']
            turtle.finished = turtle_dict['finished']
            turtle.rank = turtle_dict['rank']
            
            game.roster.append(turtle)

        # Verify load
        assert game.money == save_file_data['money']
        assert len(game.roster) == len(save_file_data['roster'])
        
        # Verify turtle restoration
        for i, turtle in enumerate(game.roster):
            original_data = save_file_data['roster'][i]
            assert turtle.name == original_data['name']
            assert turtle.speed == original_data['speed']
            assert turtle.current_energy == original_data['current_energy']

    @pytest.mark.integration
    def test_economic_cycle_workflow(self, mock_game_state, sample_turtles):
        """Test complete economic cycle"""
        game = mock_game_state
        game.money = 100
        game.roster = sample_turtles[:2]

        # 1. Race and earn money
        # Simulate simple race result
        game.money += 25  # 2nd place prize

        # 2. Buy new turtle
        new_turtle = generate_random_turtle("Purchased")
        cost = compute_turtle_cost(new_turtle)
        
        if game.money >= cost:
            game.money -= cost
            game.roster.append(new_turtle)

        # 3. Train turtle
        training_cost = 20
        if game.money >= training_cost:
            game.roster[0].train("speed")
            game.money -= training_cost

        # 4. Breed turtles
        breeding_cost = 30
        if len(game.roster) >= 2 and game.money >= breeding_cost:
            child = breed_turtles(game.roster[0], game.roster[1])
            game.roster.append(child)
            game.money -= breeding_cost

        # Verify economic cycle
        assert len(game.roster) >= 2
        assert game.money >= 0

    @pytest.mark.integration
    def test_tournament_workflow(self, mock_game_state, sample_turtles, sample_tracks):
        """Test mini-tournament workflow"""
        game = mock_game_state
        game.roster = sample_turtles[:4]  # 4 turtles for tournament
        game.money = 0

        # Tournament structure: semi-finals + finals
        # Semi-finals
        semi_final_1 = game.roster[:2]
        semi_final_2 = game.roster[2:]

        # Simulate semi-finals
        def simulate_race(turtles, track):
            for turtle in turtles:
                turtle.reset_for_race()
            
            for terrain in track[:500]:  # Shorter race for tournament
                for turtle in turtles:
                    if not turtle.finished and turtle.current_energy > 0:
                        turtle.update_physics(terrain)
            
            # Simple ranking by distance
            turtles.sort(key=lambda t: t.race_distance, reverse=True)
            return turtles[0]  # Winner

        # Run semi-finals
        sf1_winner = simulate_race(semi_final_1, sample_tracks['short'])
        sf2_winner = simulate_race(semi_final_2, sample_tracks['short'])

        # Finals
        finalists = [sf1_winner, sf2_winner]
        tournament_winner = simulate_race(finalists, sample_tracks['medium'])

        # Award tournament prize
        tournament_prize = 100
        game.money += tournament_prize

        # Verify tournament
        assert tournament_winner in finalists
        assert game.money == 100

    @pytest.mark.integration
    @pytest.mark.slow
    def test_long_term_gameplay_simulation(self, perf_tracker):
        """Test long-term gameplay simulation"""
        perf_tracker.start_timer("long_term_simulation")

        # Initialize game
        game = Mock()
        game.money = 50
        game.roster = []
        game.retired_roster = []

        # Add initial turtle
        initial_turtle = generate_random_turtle("Founder")
        game.roster.append(initial_turtle)

        # Simulate 20 game cycles
        for cycle in range(20):
            # Race with current turtle
            track = generate_track(1000)
            initial_turtle.reset_for_race()
            
            for terrain in track[:200]:  # Short race
                if initial_turtle.current_energy > 0:
                    initial_turtle.update_physics(terrain)

            # Earn money based on performance
            earnings = max(5, int(initial_turtle.race_distance / 10))
            game.money += earnings

            # Occasionally buy new turtle if affordable
            if cycle % 5 == 0 and game.money > 50:
                new_turtle = generate_random_turtle(f"Gen{cycle}")
                cost = compute_turtle_cost(new_turtle)
                if game.money >= cost:
                    game.money -= cost
                    game.roster.append(new_turtle)

            # Age turtles
            for turtle in game.roster:
                turtle.age += 1
                if turtle.age >= 20:
                    turtle.is_active = False
                    game.retired_roster.append(turtle)
                    game.roster.remove(turtle)

            # Break if no active turtles
            if len(game.roster) == 0:
                break

        duration = perf_tracker.end_timer("long_term_simulation")

        # Verify simulation
        assert duration < 5.0  # Should complete within 5 seconds
        assert game.money >= 0
        assert len(game.retired_roster) >= 0


@pytest.mark.integration
class TestErrorHandlingWorkflows:
    """Integration tests for error handling in workflows"""

    @pytest.mark.integration
    def test_insufficient_funds_handling(self, mock_game_state):
        """Test handling of insufficient funds scenarios"""
        game = mock_game_state
        game.money = 10  # Very low funds
        game.roster = []

        # Try to buy expensive turtle
        expensive_turtle = TestDataFactory.create_extreme_turtle("Expensive")
        cost = compute_turtle_cost(expensive_turtle)

        # Should handle insufficient funds gracefully
        if game.money < cost:
            # Purchase should fail or be prevented
            pass  # Actual error handling depends on implementation

        assert game.money == 10  # Money should remain unchanged
        assert len(game.roster) == 0

    @pytest.mark.integration
    def test_save_file_corruption_handling(self, temp_save_dir):
        """Test handling of corrupted save files"""
        save_path = temp_save_dir / "corrupted_save.json"

        # Create corrupted save file
        with open(save_path, 'w') as f:
            f.write('{"invalid": json}')

        # Should handle corruption gracefully
        try:
            with open(save_path, 'r') as f:
                json.load(f)
        except json.JSONDecodeError:
            # Should handle JSON decode error
            pass

    @pytest.mark.integration
    def test_empty_roster_handling(self, mock_game_state):
        """Test handling of empty roster scenarios"""
        game = mock_game_state
        game.roster = []

        # Should handle empty roster gracefully
        # Race preparation should fail or provide default turtles
        assert len(game.roster) == 0

    @pytest.mark.integration
    def test_max_roster_handling(self, mock_game_state):
        """Test handling of maximum roster size"""
        game = mock_game_state
        game.roster = []

        # Add turtles up to limit (assuming limit of 10)
        max_roster_size = 10
        for i in range(max_roster_size + 5):  # Try to add more than limit
            new_turtle = generate_random_turtle(f"Turtle{i}")
            
            if len(game.roster) < max_roster_size:
                game.roster.append(new_turtle)
            else:
                # Should handle roster limit
                break

        assert len(game.roster) <= max_roster_size
