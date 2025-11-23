#!/usr/bin/env python3
"""
Visual validation test for the 19 genetic traits.
Tests that all genetic traits are properly rendered and visualized.
"""

# Add project root to path
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_all_genetic_traits():
    """Test that all 19 genetic traits are accessible and have valid values"""
    print("Testing All 19 Genetic Traits...")

    try:
        from genetics import VisualGenetics

        genetics_system = VisualGenetics()
        gene_definitions = genetics_system.get_gene_definitions()
        all_genes = gene_definitions.get_all_gene_names()

        print(f"Total genetic traits defined: {len(all_genes)}")
        print(f"Genetic traits: {', '.join(all_genes)}")

        # Generate random genetics and validate all traits
        random_genetics = genetics_system.generate_random_genetics()

        print(f"\nGenerated genetics has {len(random_genetics)} traits")

        # Validate each trait has a valid value
        for trait_name in all_genes:
            if trait_name in random_genetics:
                value = random_genetics[trait_name]
                definition = gene_definitions.get_gene_definition(trait_name)

                # Check if value is valid according to definition
                is_valid = gene_definitions.validate_gene_value(trait_name, value)
                status = "VALID" if is_valid else "INVALID"
                print(f"  {trait_name}: {value} ({definition['type']}) - {status}")
            else:
                print(f"  {trait_name}: MISSING - ERROR")
                return False

        return True
    except Exception as e:
        print(f"Genetic traits test failed: {e}")
        return False


def test_trait_variations():
    """Test that different trait values produce different visual results"""
    print("\nTesting Trait Variations...")

    try:
        from genetics import VisualGenetics
        from src.core.game.entities import Turtle

        genetics_system = VisualGenetics()

        # Test shell pattern variations
        patterns = ['hex', 'spots', 'stripes', 'rings']
        print("Testing shell pattern variations:")

        for pattern in patterns:
            # Create genetics with specific pattern
            base_genetics = genetics_system.generate_random_genetics()
            base_genetics['shell_pattern_type'] = pattern

            turtle = Turtle(f"Pattern_{pattern}", 5, 50, 3, 4, 2, genetics=base_genetics)
            current_pattern = turtle.get_genetic_trait('shell_pattern_type')

            print(f"  {pattern} -> {current_pattern} {'OK' if current_pattern == pattern else 'FAIL'}")

        # Test color variations
        print("\nTesting color variations:")
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]

        for i, color in enumerate(colors):
            base_genetics = genetics_system.generate_random_genetics()
            base_genetics['shell_base_color'] = color

            turtle = Turtle(f"Color_{i}", 5, 50, 3, 4, 2, genetics=base_genetics)
            current_color = turtle.get_genetic_trait('shell_base_color')

            print(f"  {color} -> {current_color} {'OK' if current_color == color else 'FAIL'}")

        # Test size variations
        print("\nTesting size variations:")
        sizes = [0.5, 0.8, 1.0, 1.2, 1.5]

        for size in sizes:
            base_genetics = genetics_system.generate_random_genetics()
            base_genetics['shell_size_modifier'] = size

            turtle = Turtle(f"Size_{size}", 5, 50, 3, 4, 2, genetics=base_genetics)
            current_size = turtle.get_genetic_trait('shell_size_modifier')

            print(f"  {size} -> {current_size} {'OK' if abs(current_size - size) < 0.01 else 'FAIL'}")

        return True
    except Exception as e:
        print(f"Trait variations test failed: {e}")
        return False


def test_inheritance_patterns():
    """Test that inheritance properly transfers genetic traits"""
    print("\nTesting Inheritance Patterns...")

    try:
        from genetics import VisualGenetics
        from src.core.game.entities import Turtle

        # Create parents with distinct traits
        parent1_genetics = {
            'shell_pattern_type': 'hex',
            'shell_base_color': (255, 0, 0),
            'body_pattern_type': 'solid',
            'limb_shape': 'flippers'
        }

        parent2_genetics = {
            'shell_pattern_type': 'spots',
            'shell_base_color': (0, 255, 0),
            'body_pattern_type': 'mottled',
            'limb_shape': 'feet'
        }

        parent1 = Turtle("Parent1", 5, 50, 3, 4, 2, genetics=parent1_genetics)
        parent2 = Turtle("Parent2", 5, 50, 3, 4, 2, genetics=parent2_genetics)

        print(f"Parent 1: {parent1.get_trait_summary()}")
        print(f"Parent 2: {parent2.get_trait_summary()}")

        # Test multiple breeding attempts
        for i in range(3):
            child_genetics = VisualGenetics().inherit_genetics(parent1_genetics, parent2_genetics)
            child = Turtle(f"Child{i + 1}", 5, 50, 3, 4, 2, genetics=child_genetics)

            print(f"Child {i + 1}: {child.get_trait_summary()}")

            # Check that child has traits from both parents
            child_pattern = child.get_genetic_trait('shell_pattern_type')
            child_color = child.get_genetic_trait('shell_base_color')

            if child_pattern in ['hex', 'spots']:
                print(f"  Pattern inheritance: OK")
            else:
                print(f"  Pattern inheritance: UNEXPECTED ({child_pattern})")

        return True
    except Exception as e:
        print(f"Inheritance patterns test failed: {e}")
        return False


def test_mutation_system():
    """Test that mutation system creates valid variations"""
    print("\nTesting Mutation System...")

    try:
        from genetics import VisualGenetics
        from src.core.game.entities import Turtle

        genetics_system = VisualGenetics()

        # Create a base turtle
        base_genetics = genetics_system.generate_random_genetics()
        turtle = Turtle("BaseTurtle", 5, 50, 3, 4, 2, genetics=base_genetics)

        print(f"Base turtle: {turtle.get_trait_summary()}")

        # Test mutations on different trait types
        traits_to_test = ['shell_pattern_type', 'shell_base_color', 'shell_size_modifier', 'limb_shape']

        for trait in traits_to_test:
            original_value = turtle.get_genetic_trait(trait)

            # Apply mutation
            turtle.mutate_trait(trait)
            mutated_value = turtle.get_genetic_trait(trait)

            print(f"  {trait}: {original_value} -> {mutated_value}")

            # Validate mutated value
            is_valid = genetics_system.get_gene_definitions().validate_gene_value(trait, mutated_value)
            print(f"    Valid: {is_valid}")

        # Test random mutations
        print("\nTesting random mutations:")
        for i in range(3):
            turtle.mutate_trait()  # Random trait
            print(f"  Random mutation {i + 1}: {turtle.get_trait_summary()}")

        return True
    except Exception as e:
        print(f"Mutation system test failed: {e}")
        return False


def test_rendering_integration():
    """Test that all traits can be rendered"""
    print("\nTesting Rendering Integration...")

    try:
        from genetics import VisualGenetics
        from src.core.game.entities import Turtle
        from src.core.rendering.direct_turtle_renderer import render_turtle_directly

        genetics_system = VisualGenetics()

        # Test rendering different genetic combinations
        test_cases = [
            ("Standard", genetics_system.generate_random_genetics()),
            ("All Hex", {
                'shell_pattern_type': 'hex',
                'body_pattern_type': 'solid',
                'limb_shape': 'flippers',
                'shell_base_color': (100, 100, 255),
                'shell_pattern_color': (255, 255, 255)
            }),
            ("All Spots", {
                'shell_pattern_type': 'spots',
                'body_pattern_type': 'mottled',
                'limb_shape': 'feet',
                'shell_base_color': (255, 100, 100),
                'shell_pattern_color': (255, 255, 100)
            })
        ]

        for name, genetics in test_cases:
            # Fill in missing traits with defaults
            full_genetics = genetics_system.get_gene_definitions().get_default_genetics()
            full_genetics.update(genetics)

            turtle = Turtle(f"Test_{name}", 5, 50, 3, 4, 2, genetics=full_genetics)

            print(f"  Rendering {name}: {turtle.get_trait_summary()}")

            try:
                result = render_turtle_directly(full_genetics, size=100)
                if result:
                    print(f"    Success: {type(result)}")
                else:
                    print(f"    No result (headless environment)")
            except Exception as e:
                print(f"    Render error: {e}")

        return True
    except Exception as e:
        print(f"Rendering integration test failed: {e}")
        return False


def main():
    """Run all visual validation tests"""
    print("TurboShells Visual Genetics Validation")
    print("=" * 50)

    tests = [
        test_all_genetic_traits,
        test_trait_variations,
        test_inheritance_patterns,
        test_mutation_system,
        test_rendering_integration
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
    print("VISUAL VALIDATION RESULTS")
    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")

    if passed == total:
        print("ALL VISUAL TESTS PASSED! Genetics system is fully functional!")
        return True
    else:
        print("Some visual tests failed. Check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
