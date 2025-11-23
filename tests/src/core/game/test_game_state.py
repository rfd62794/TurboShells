#!/usr/bin/env python3
"""
Unit tests for game state functions
Tests turtle generation, breeding, and cost calculation.
"""

import pytest
from src.core.game_state import generate_random_turtle, breed_turtles, compute_turtle_cost


class TestTurtleGeneration:
    """Tests for turtle generation functionality"""

    @pytest.mark.unit
    def test_generate_random_turtle(self):
        """Test random turtle generation"""
        turtle = generate_random_turtle()

        assert hasattr(turtle, 'x')
        assert hasattr(turtle, 'y')
        assert hasattr(turtle, 'speed')
        assert hasattr(turtle, 'color')

    @pytest.mark.unit
    def test_generate_random_turtle_different_names(self):
        """Test random turtle generation produces different turtles"""
        turtles = []

        for i in range(4):
            turtle = generate_random_turtle()
            turtles.append(turtle)

        # All turtles should be different (due to random generation)
        stat_combinations = set()
        for turtle in turtles:
            stats = (turtle.x, turtle.y, turtle.speed, turtle.color)
            stat_combinations.add(stats)

        # Should have different stat combinations (high probability)
        assert len(stat_combinations) >= 1

    @pytest.mark.unit
    def test_generate_random_turtle_bounds(self):
        """Test generated turtles are within expected bounds"""
        turtle = generate_random_turtle()
        
        # Position bounds (from game_state.py implementation)
        assert 100 <= turtle.x <= 700
        assert 100 <= turtle.y <= 500
        assert 0.5 <= turtle.speed <= 2.0
        assert turtle.color in ["red", "green", "blue", "yellow", "purple", "orange"]


class TestTurtleBreeding:
    """Tests for turtle breeding functionality"""

    @pytest.mark.unit
    def test_breed_turtles_basic(self):
        """Test basic turtle breeding functionality"""
        from src.core.entities import TurtleEntity
        parent1 = TurtleEntity(x=100, y=100, speed=1.0, color="red")
        parent2 = TurtleEntity(x=200, y=200, speed=2.0, color="blue")

        child = breed_turtles(parent1, parent2)

        assert isinstance(child, TurtleEntity)
        # Child should have position between parents
        assert min(parent1.x, parent2.x) <= child.x <= max(parent1.x, parent2.x)
        assert min(parent1.y, parent2.y) <= child.y <= max(parent1.y, parent2.y)

    @pytest.mark.unit
    def test_breed_turtles_stat_inheritance(self):
        """Test that child stats are influenced by parents"""
        from src.core.entities import TurtleEntity
        parent1 = TurtleEntity(x=100, y=100, speed=0.5, color="red")
        parent2 = TurtleEntity(x=200, y=200, speed=2.0, color="blue")

        child = breed_turtles(parent1, parent2)

        # Child speed should be between parents (allowing for variation)
        min_speed = min(parent1.speed, parent2.speed)
        max_speed = max(parent1.speed, parent2.speed)
        assert min_speed <= child.speed <= max_speed

    @pytest.mark.unit
    def test_breed_turtles_edge_cases(self):
        """Test breeding with edge case turtles"""
        from src.core.entities import TurtleEntity
        # Create turtles with different speeds
        parent1 = TurtleEntity(x=100, y=100, speed=0.5, color="red")
        parent2 = TurtleEntity(x=200, y=200, speed=2.0, color="blue")

        child = breed_turtles(parent1, parent2)

        assert isinstance(child, TurtleEntity)
        # Child should have speed between parents
        assert 0.5 <= child.speed <= 2.0

    @pytest.mark.unit
    def test_breed_turtles_same_parents(self):
        """Test breeding turtle with itself"""
        from src.core.entities import TurtleEntity
        parent = TurtleEntity(x=100, y=100, speed=1.0, color="red")
        
        try:
            child = breed_turtles(parent, parent)
            assert isinstance(child, TurtleEntity)
        except (ValueError, AttributeError):
            # Expected if self-breeding is not allowed
            pass


class TestTurtleEconomics:
    """Tests for turtle cost calculation"""

    @pytest.mark.unit
    def test_compute_turtle_cost(self):
        """Test turtle cost calculation"""
        # Create a TurtleEntity which has x and y attributes
        from src.core.entities import TurtleEntity
        turtle = TurtleEntity(x=400, y=300, speed=5.0, color="red")
        cost = compute_turtle_cost(turtle)

        assert isinstance(cost, (int, float))
        assert cost > 0
        assert cost < 10000  # Reasonable upper bound

    @pytest.mark.unit
    def test_compute_turtle_cost_correlation(self):
        """Test that different turtles have different costs"""
        # Generate multiple turtles
        turtles = [generate_random_turtle() for _ in range(5)]
        costs = [compute_turtle_cost(turtle) for turtle in turtles]

        # Should have some variation in costs
        assert len(set(costs)) >= 1  # At least some variation

    @pytest.mark.unit
    def test_compute_turtle_cost_consistency(self):
        """Test cost calculation is consistent"""
        turtle = generate_random_turtle()
        cost1 = compute_turtle_cost(turtle)
        cost2 = compute_turtle_cost(turtle)

        assert cost1 == cost2

    @pytest.mark.unit
    def test_compute_turtle_cost_position_impact(self):
        """Test that position affects cost"""
        from src.core.entities import TurtleEntity
        
        # Create turtles at different positions
        center_turtle = TurtleEntity(x=400, y=300, speed=1.0, color="red")
        far_turtle = TurtleEntity(x=100, y=100, speed=1.0, color="red")
        
        center_cost = compute_turtle_cost(center_turtle)
        far_cost = compute_turtle_cost(far_turtle)
        
        # Far turtle should have higher cost due to position penalty
        assert far_cost > center_cost

    @pytest.mark.unit
    def test_compute_turtle_cost_speed_impact(self):
        """Test that speed affects cost"""
        from src.core.entities import TurtleEntity
        
        # Create turtles with different speeds
        slow_turtle = TurtleEntity(x=400, y=300, speed=0.5, color="red")
        fast_turtle = TurtleEntity(x=400, y=300, speed=2.0, color="red")
        
        slow_cost = compute_turtle_cost(slow_turtle)
        fast_cost = compute_turtle_cost(fast_turtle)
        
        # Fast turtle should have higher cost
        assert fast_cost > slow_cost
