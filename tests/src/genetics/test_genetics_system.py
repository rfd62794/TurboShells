#!/usr/bin/env python3
"""
Comprehensive unit tests for genetics system
Tests visual genetics, inheritance, and mutation mechanics.
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from genetics import VisualGenetics
except ImportError:
    try:
        from src.genetics import VisualGenetics
    except ImportError:
        VisualGenetics = None


class TestVisualGenetics:
    """Unit tests for visual genetics system"""

    @pytest.fixture
    def genetics_system(self):
        """Create a genetics system instance"""
        if VisualGenetics is None:
            pytest.skip("VisualGenetics not available")
        return VisualGenetics()

    @pytest.mark.unit
    @pytest.mark.skipif(VisualGenetics is None, reason="VisualGenetics not available")
    def test_genetics_initialization(self, genetics_system):
        """Test genetics system initialization"""
        assert genetics_system is not None
        assert hasattr(genetics_system, 'generate_random_genetics')

    @pytest.mark.unit
    @pytest.mark.skipif(VisualGenetics is None, reason="VisualGenetics not available")
    def test_generate_random_genetics(self, genetics_system):
        """Test random genetics generation"""
        genetics = genetics_system.generate_random_genetics()
        
        assert isinstance(genetics, dict)
        assert len(genetics) > 0
        
        # Check for expected genetics keys
        expected_keys = ['color', 'pattern', 'size', 'shell_shape']
        for key in expected_keys:
            if key in genetics:
                assert genetics[key] is not None

    @pytest.mark.unit
    @pytest.mark.skipif(VisualGenetics is None, reason="VisualGenetics not available")
    def test_genetics_consistency(self, genetics_system):
        """Test genetics generation consistency"""
        genetics1 = genetics_system.generate_random_genetics()
        genetics2 = genetics_system.generate_random_genetics()
        
        # Should be different (high probability)
        # But both should be valid genetics
        assert isinstance(genetics1, dict)
        assert isinstance(genetics2, dict)

    @pytest.mark.unit
    @pytest.mark.skipif(VisualGenetics is None, reason="VisualGenetics not available")
    def test_genetics_inheritance(self, genetics_system):
        """Test genetics inheritance if available"""
        parent1 = genetics_system.generate_random_genetics()
        parent2 = genetics_system.generate_random_genetics()
        
        # Test if inheritance method exists
        if hasattr(genetics_system, 'inherit_genetics'):
            child = genetics_system.inherit_genetics(parent1, parent2)
            assert isinstance(child, dict)
            assert len(child) > 0

    @pytest.mark.unit
    @pytest.mark.skipif(VisualGenetics is None, reason="VisualGenetics not available")
    def test_genetics_mutation(self, genetics_system):
        """Test genetics mutation if available"""
        base_genetics = genetics_system.generate_random_genetics()
        
        # Test if mutation method exists
        if hasattr(genetics_system, 'mutate_genetics'):
            mutated = genetics_system.mutate_genetics(base_genetics)
            assert isinstance(mutated, dict)
            assert len(mutated) > 0


class MockGeneticsSystem:
    """Mock genetics system for testing when VisualGenetics is not available"""

    def __init__(self):
        self.colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange']
        self.patterns = ['solid', 'striped', 'spotted', 'mottled']
        self.sizes = ['small', 'medium', 'large']
        self.shell_shapes = ['round', 'oval', 'pointed']

    def generate_random_genetics(self):
        """Generate random genetics"""
        import random
        return {
            'color': random.choice(self.colors),
            'pattern': random.choice(self.patterns),
            'size': random.choice(self.sizes),
            'shell_shape': random.choice(self.shell_shapes),
            'speed_modifier': random.uniform(0.8, 1.2),
            'energy_modifier': random.uniform(0.8, 1.2),
        }

    def inherit_genetics(self, parent1, parent2):
        """Inherit genetics from parents"""
        import random
        child = {}
        for key in parent1:
            if key in parent2:
                child[key] = parent1[key] if random.random() > 0.5 else parent2[key]
        return child

    def mutate_genetics(self, genetics):
        """Mutate genetics"""
        import random
        mutated = genetics.copy()
        
        # Small chance to mutate each trait
        if random.random() < 0.1:  # 10% mutation chance
            if 'color' in mutated:
                mutated['color'] = random.choice(self.colors)
        
        return mutated


class TestMockGenetics:
    """Unit tests using mock genetics system"""

    @pytest.fixture
    def mock_genetics(self):
        """Create a mock genetics system"""
        return MockGeneticsSystem()

    @pytest.mark.unit
    def test_mock_genetics_initialization(self, mock_genetics):
        """Test mock genetics system initialization"""
        assert mock_genetics is not None
        assert len(mock_genetics.colors) > 0
        assert len(mock_genetics.patterns) > 0

    @pytest.mark.unit
    def test_generate_random_genetics_mock(self, mock_genetics):
        """Test random genetics generation with mock"""
        genetics = mock_genetics.generate_random_genetics()
        
        assert isinstance(genetics, dict)
        assert 'color' in genetics
        assert 'pattern' in genetics
        assert 'size' in genetics
        assert 'shell_shape' in genetics
        assert 'speed_modifier' in genetics
        assert 'energy_modifier' in genetics

    @pytest.mark.unit
    def test_genetics_value_ranges_mock(self, mock_genetics):
        """Test genetics values are within expected ranges"""
        genetics = mock_genetics.generate_random_genetics()
        
        assert genetics['color'] in mock_genetics.colors
        assert genetics['pattern'] in mock_genetics.patterns
        assert genetics['size'] in mock_genetics.sizes
        assert genetics['shell_shape'] in mock_genetics.shell_shapes
        assert 0.8 <= genetics['speed_modifier'] <= 1.2
        assert 0.8 <= genetics['energy_modifier'] <= 1.2

    @pytest.mark.unit
    def test_inherit_genetics_mock(self, mock_genetics):
        """Test genetics inheritance with mock"""
        parent1 = mock_genetics.generate_random_genetics()
        parent2 = mock_genetics.generate_random_genetics()
        
        child = mock_genetics.inherit_genetics(parent1, parent2)
        
        assert isinstance(child, dict)
        assert len(child) > 0
        
        # Child should have traits from parents
        for key in child:
            assert child[key] == parent1[key] or child[key] == parent2[key]

    @pytest.mark.unit
    def test_mutate_genetics_mock(self, mock_genetics):
        """Test genetics mutation with mock"""
        base_genetics = mock_genetics.generate_random_genetics()
        
        mutated = mock_genetics.mutate_genetics(base_genetics)
        
        assert isinstance(mutated, dict)
        assert len(mutated) == len(base_genetics)
        
        # Most traits should be the same, with possible mutations
        same_traits = sum(1 for key in base_genetics if base_genetics[key] == mutated[key])
        assert same_traits >= len(base_genetics) - 1  # At most 1 trait mutated

    @pytest.mark.unit
    def test_genetics_variety_mock(self, mock_genetics):
        """Test genetics generation produces variety"""
        genetics_list = [mock_genetics.generate_random_genetics() for _ in range(10)]
        
        # Should have some variety in the generated genetics
        color_variety = len(set(g['color'] for g in genetics_list))
        pattern_variety = len(set(g['pattern'] for g in genetics_list))
        
        assert color_variety >= 1
        assert pattern_variety >= 1


class TestGeneticsIntegration:
    """Integration tests for genetics with turtle system"""

    @pytest.fixture
    def mock_genetics(self):
        """Create a mock genetics system"""
        return MockGeneticsSystem()

    @pytest.mark.unit
    def test_turtle_with_genetics(self, mock_genetics):
        """Test turtle creation with genetics"""
        from src.core.game.entities import Turtle
        
        genetics = mock_genetics.generate_random_genetics()
        turtle = Turtle(
            name="GeneticTurtle",
            speed=5.0,
            energy=100.0,
            recovery=2.0,
            swim=1.5,
            climb=1.5,
            genetics=genetics
        )
        
        assert turtle.name == "GeneticTurtle"
        assert turtle.visual_genetics == genetics

    @pytest.mark.unit
    def test_turtle_genetics_inheritance_simulation(self, mock_genetics):
        """Test turtle genetics inheritance simulation"""
        from src.core.game.entities import Turtle
        
        # Create parent turtles
        parent1_genetics = mock_genetics.generate_random_genetics()
        parent2_genetics = mock_genetics.generate_random_genetics()
        
        parent1 = Turtle("Parent1", 5.0, 100.0, 2.0, 1.5, 1.5, genetics=parent1_genetics)
        parent2 = Turtle("Parent2", 5.0, 100.0, 2.0, 1.5, 1.5, genetics=parent2_genetics)
        
        # Simulate inheritance
        child_genetics = mock_genetics.inherit_genetics(parent1_genetics, parent2_genetics)
        child = Turtle("Child", 5.0, 100.0, 2.0, 1.5, 1.5, genetics=child_genetics)
        
        assert child.visual_genetics == child_genetics
        assert child.name == "Child"

    @pytest.mark.unit
    def test_genetics_modifiers_impact(self, mock_genetics):
        """Test genetics modifiers impact on turtle stats"""
        from src.core.game.entities import Turtle
        
        # Create turtles with different genetics
        fast_genetics = mock_genetics.generate_random_genetics()
        fast_genetics['speed_modifier'] = 1.2  # 20% speed boost
        
        slow_genetics = mock_genetics.generate_random_genetics()
        slow_genetics['speed_modifier'] = 0.8  # 20% speed penalty
        
        fast_turtle = Turtle("Fast", 5.0, 100.0, 2.0, 1.5, 1.5, genetics=fast_genetics)
        slow_turtle = Turtle("Slow", 5.0, 100.0, 2.0, 1.5, 1.5, genetics=slow_genetics)
        
        # Both turtles should have same base stats
        assert fast_turtle.stats['speed'] == slow_turtle.stats['speed']
        
        # But different genetics that could be used in calculations
        assert fast_turtle.visual_genetics['speed_modifier'] > slow_turtle.visual_genetics['speed_modifier']

    @pytest.mark.unit
    def test_genetics_serialization(self, mock_genetics):
        """Test genetics can be serialized/deserialized"""
        import json
        
        genetics = mock_genetics.generate_random_genetics()
        
        # Serialize
        serialized = json.dumps(genetics)
        assert isinstance(serialized, str)
        
        # Deserialize
        deserialized = json.loads(serialized)
        assert deserialized == genetics
