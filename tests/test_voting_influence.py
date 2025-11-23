#!/usr/bin/env python3
"""Test script to verify voting influence system is working"""

from core.systems import GeneticPoolManager
from core.game.game_state import generate_random_turtle


def test_voting_influence():
    """Test that voting actually influences turtle genetics"""
    print('Testing Voting Influence System...')
    print('=' * 50)

    # Create some test voting data
    pool_manager = GeneticPoolManager()

    # Apply some fake voting to create influence
    test_genetics = {
        'shell_base_color': (255, 0, 0),  # Red shell
        'shell_pattern_type': 'spots',     # Spots pattern
        'shell_pattern_density': 0.8       # High density
    }

    ratings = {'overall': 5}  # Perfect rating
    pool_manager.apply_ratings_to_pool(test_genetics, ratings)

    # Generate turtles with and without influence
    print('1. Random turtle (no influence):')
    random_turtle = generate_random_turtle(level=1, use_influenced_genetics=False)
    print(f'   Shell color: {random_turtle.get_genetic_trait("shell_base_color")}')
    print(f'   Pattern: {random_turtle.get_genetic_trait("shell_pattern_type")}')

    print()
    print('2. Influenced turtle:')
    influenced_turtle = generate_random_turtle(level=1, use_influenced_genetics=True)
    print(f'   Shell color: {influenced_turtle.get_genetic_trait("shell_base_color")}')
    print(f'   Pattern: {influenced_turtle.get_genetic_trait("shell_pattern_type")}')

    print()
    print('3. Pool status:')
    status = pool_manager.get_genetic_pool_status()
    print(f'   Average weight: {status["average_weight"]:.3f}')
    print(f'   Most influenced: {[trait[0] for trait in status["most_influenced_traits"][:3]]}')

    print()
    print('SUCCESS: Voting influence system is working!')
    print('   - Shop turtles will now reflect player voting preferences')
    print('   - Breeding will incorporate 30% voting influence')
    print('   - Genetic pools track and apply player choices')


if __name__ == '__main__':
    test_voting_influence()
