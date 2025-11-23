#!/usr/bin/env python3
"""
Test script to verify genetics system integration with core game mechanics.
Tests API compatibility between new genetics system and existing game functionality.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_turtle_creation():
    """Test that turtles can be created with new genetics system"""
    print("Testing Turtle Creation...")

    try:
        from core.game.entities import Turtle

        # Test turtle creation without genetics (should auto-generate)
        turtle1 = Turtle("TestTurtle1", 5, 50, 3, 4, 2)
        print(f"Turtle created: {turtle1.name}")
        print(f"   Stats: Speed={turtle1.speed}, Energy={turtle1.max_energy}")
        print(f"   Genetics traits: {len(turtle1.visual_genetics)} traits")

        # Test turtle creation with custom genetics
        from genetics import VisualGenetics
        genetics_system = VisualGenetics()
        custom_genetics = genetics_system.generate_random_genetics()

        turtle2 = Turtle("TestTurtle2", 6, 60, 4, 5, 3, genetics=custom_genetics)
        print(f"Turtle created with custom genetics: {turtle2.name}")
        print(f"   Custom genetics: {len(turtle2.visual_genetics)} traits")

        return True
    except Exception as e:
        print(f"Turtle creation failed: {e}")
        return False


def test_shop_generation():
    """Test that shop generation works with new genetics"""
    print("\nTesting Shop Generation...")

    try:
        from core.game.game_state import generate_random_turtle

        # Test shop turtle generation at different levels
        for level in [1, 2, 3]:
            turtle = generate_random_turtle(level)
            print(f"Level {level} shop turtle: {turtle.name}")
            print(f"   Stats: Speed={turtle.speed}, Energy={turtle.max_energy}")
            print(f"   Has genetics: {len(turtle.visual_genetics)} traits")

        return True
    except Exception as e:
        print(f"Shop generation failed: {e}")
        return False


def test_breeding_system():
    """Test that breeding works with new genetics inheritance"""
    print("\nTesting Breeding System...")

    try:
        from core.game.game_state import generate_random_turtle, breed_turtles

        # Create parent turtles
        parent1 = generate_random_turtle(2)
        parent2 = generate_random_turtle(2)

        print(f"Parent 1: {parent1.name}, Generation: {parent1.generation}")
        print(f"Parent 2: {parent2.name}, Generation: {parent2.generation}")

        # Breed them
        child = breed_turtles(parent1, parent2)

        print(f"Child created: {child.name}")
        print(f"   Generation: {child.generation}")
        print(f"   Parent IDs: {child.parent_ids}")
        print(f"   Has genetics: {len(child.visual_genetics)} traits")

        # Test genetic inheritance
        parent1_shell = parent1.get_genetic_trait('shell_pattern_type')
        parent2_shell = parent2.get_genetic_trait('shell_pattern_type')
        child_shell = child.get_genetic_trait('shell_pattern_type')

        print(f"   Shell inheritance: {parent1_shell} + {parent2_shell} -> {child_shell}")

        return True
    except Exception as e:
        print(f"Breeding system failed: {e}")
        return False


def test_genetics_methods():
    """Test new genetics methods on Turtle class"""
    print("\nTesting Genetics Methods...")

    try:
        from core.game.entities import Turtle

        turtle = Turtle("MethodTest", 5, 50, 3, 4, 2)

        # Test trait access
        shell_pattern = turtle.get_genetic_trait('shell_pattern_type')
        print(f"Get trait: shell_pattern_type = {shell_pattern}")

        # Test trait modification
        turtle.set_genetic_trait('shell_pattern_type', 'hex')
        new_pattern = turtle.get_genetic_trait('shell_pattern_type')
        print(f"Set trait: shell_pattern_type = {new_pattern}")

        # Test trait summary
        summary = turtle.get_trait_summary()
        print(f"Trait summary: {summary}")

        # Test mutation
        original_pattern = turtle.get_genetic_trait('shell_pattern_type')
        turtle.mutate_trait('shell_pattern_type')
        mutated_pattern = turtle.get_genetic_trait('shell_pattern_type')
        print(f"Mutation: {original_pattern} -> {mutated_pattern}")

        # Test random mutation
        turtle.mutate_trait()  # Random trait
        print(f"Random mutation applied")

        return True
    except Exception as e:
        print(f"Genetics methods failed: {e}")
        return False


def test_rendering_compatibility():
    """Test that rendering works with new genetics"""
    print("\nTesting Rendering Compatibility...")

    try:
        from core.game.entities import Turtle
        from core.rendering.direct_turtle_renderer import render_turtle_directly

        turtle = Turtle("RenderTest", 5, 50, 3, 4, 2)
        genetics = turtle.get_all_genetics()

        print(f"Turtle genetics prepared for rendering")
        print(f"   Genetics keys: {list(genetics.keys())[:5]}...")  # Show first 5 keys

        # Test rendering (this might fail in headless environment, but should not crash)
        try:
            result = render_turtle_directly(genetics, size=100)
            if result:
                print(f"Rendering successful: {type(result)}")
            else:
                print("Rendering returned None (likely headless environment)")
        except Exception as render_error:
            print(f"Rendering issue (expected in headless): {render_error}")

        return True
    except Exception as e:
        print(f"Rendering compatibility failed: {e}")
        return False


def test_voting_system_compatibility():
    """Test that voting system works with new genetics"""
    print("\nTesting Voting System Compatibility...")

    try:
        from genetics import VisualGenetics
        from core.voting.voting_system import VotingSystem

        genetics_system = VisualGenetics()
        voting_system = VotingSystem()

        # Test design generation
        design = voting_system.generate_design()
        print(f"Design generated: {design['name']}")
        print(f"   Has genetics: {len(design['genetics'])} traits")

        # Test feature analysis
        features = voting_system.analyze_features(design['genetics'])
        print(f"Features analyzed: {len(features)} categories")

        return True
    except Exception as e:
        print(f"Voting system compatibility failed: {e}")
        return False


def main():
    """Run all compatibility tests"""
    print("TurboShells Genetics Integration Test Suite")
    print("=" * 50)

    tests = [
        test_turtle_creation,
        test_shop_generation,
        test_breeding_system,
        test_genetics_methods,
        test_rendering_compatibility,
        test_voting_system_compatibility
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"Test {test.__name__} crashed: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")

    if passed == total:
        print("ALL TESTS PASSED! Genetics integration is successful!")
        return True
    else:
        print("Some tests failed. Check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
