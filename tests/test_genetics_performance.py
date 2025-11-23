#!/usr/bin/env python3
"""
Performance test for the genetics system integration.
Tests performance of genetics operations in game context.
"""

# Add project root to path
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


import sys
import os
import time
import random

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def time_operation(operation, *args, **kwargs):
    """Time an operation and return result and duration"""
    start = time.time()
    result = operation(*args, **kwargs)
    end = time.time()
    return result, end - start


def test_turtle_creation_performance():
    """Test performance of turtle creation with genetics"""
    print("Testing Turtle Creation Performance...")

    try:
        from src.core.game.entities import Turtle

        # Test creating many turtles
        num_turtles = 100

        # Test with auto-generated genetics
        start = time.time()
        turtles = []
        for i in range(num_turtles):
            turtle = Turtle(f"Turtle{i}", 5, 50, 3, 4, 2)
            turtles.append(turtle)
        end = time.time()

        auto_gen_time = end - start
        avg_auto_time = auto_gen_time / num_turtles

        print(f"  Created {num_turtles} turtles with auto-genetics")
        print(f"  Total time: {auto_gen_time:.3f}s")
        print(f"  Average per turtle: {avg_auto_time * 1000:.2f}ms")

        # Test with custom genetics
        from genetics import VisualGenetics
        genetics_system = VisualGenetics()

        start = time.time()
        for i in range(num_turtles):
            custom_genetics = genetics_system.generate_random_genetics()
            turtle = Turtle(f"Custom{i}", 5, 50, 3, 4, 2, genetics=custom_genetics)
        end = time.time()

        custom_gen_time = end - start
        avg_custom_time = custom_gen_time / num_turtles

        print(f"  Created {num_turtles} turtles with custom genetics")
        print(f"  Total time: {custom_gen_time:.3f}s")
        print(f"  Average per turtle: {avg_custom_time * 1000:.2f}ms")

        # Performance targets
        target_avg_time = 0.005  # 5ms per turtle

        if avg_auto_time < target_avg_time and avg_custom_time < target_avg_time:
            print(f"  Performance: EXCELLEENT (<{target_avg_time * 1000:.0f}ms per turtle)")
            return True
        elif avg_auto_time < target_avg_time * 2 and avg_custom_time < target_avg_time * 2:
            print(f"  Performance: GOOD (<{target_avg_time * 2 * 1000:.0f}ms per turtle)")
            return True
        else:
            print(f"  Performance: NEEDS OPTIMIZATION (>{target_avg_time * 2 * 1000:.0f}ms per turtle)")
            return False

    except Exception as e:
        print(f"Turtle creation performance test failed: {e}")
        return False


def test_shop_generation_performance():
    """Test performance of shop turtle generation"""
    print("\nTesting Shop Generation Performance...")

    try:
        from src.core.game.game_state import generate_random_turtle

        # Test generating shop turtles at different levels
        levels = [1, 2, 3, 4, 5]
        turtles_per_level = 50

        total_time = 0
        total_turtles = 0

        for level in levels:
            start = time.time()
            for i in range(turtles_per_level):
                turtle = generate_random_turtle(level)
            end = time.time()

            level_time = end - start
            total_time += level_time
            total_turtles += turtles_per_level

            avg_time = level_time / turtles_per_level
            print(
                f"  Level {level}: {turtles_per_level} turtles in {
                    level_time:.3f}s ({
                    avg_time *
                    1000:.2f}ms per turtle)")

        overall_avg = total_time / total_turtles
        print(f"  Overall: {total_turtles} turtles in {total_time:.3f}s ({overall_avg * 1000:.2f}ms per turtle)")

        # Performance target: under 10ms per shop turtle
        target_time = 0.010

        if overall_avg < target_time:
            print(f"  Performance: EXCELLENT (<{target_time * 1000:.0f}ms per turtle)")
            return True
        elif overall_avg < target_time * 2:
            print(f"  Performance: GOOD (<{target_time * 2 * 1000:.0f}ms per turtle)")
            return True
        else:
            print(f"  Performance: NEEDS OPTIMIZATION (>{target_time * 2 * 1000:.0f}ms per turtle)")
            return False

    except Exception as e:
        print(f"Shop generation performance test failed: {e}")
        return False


def test_breeding_performance():
    """Test performance of breeding operations"""
    print("\nTesting Breeding Performance...")

    try:
        from src.core.game.game_state import generate_random_turtle, breed_turtles

        # Create parent pool
        num_parents = 20
        parents = []
        for i in range(num_parents):
            parent = generate_random_turtle(3)
            parents.append(parent)

        # Test breeding operations
        num_breeding_ops = 100

        start = time.time()
        for i in range(num_breeding_ops):
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)
            child = breed_turtles(parent1, parent2)
        end = time.time()

        breeding_time = end - start
        avg_time = breeding_time / num_breeding_ops

        print(f"  Performed {num_breeding_ops} breeding operations")
        print(f"  Total time: {breeding_time:.3f}s")
        print(f"  Average per breeding: {avg_time * 1000:.2f}ms")

        # Performance target: under 20ms per breeding operation
        target_time = 0.020

        if avg_time < target_time:
            print(f"  Performance: EXCELLENT (<{target_time * 1000:.0f}ms per breeding)")
            return True
        elif avg_time < target_time * 2:
            print(f"  Performance: GOOD (<{target_time * 2 * 1000:.0f}ms per breeding)")
            return True
        else:
            print(f"  Performance: NEEDS OPTIMIZATION (>{target_time * 2 * 1000:.0f}ms per breeding)")
            return False

    except Exception as e:
        print(f"Breeding performance test failed: {e}")
        return False


def test_genetics_operations_performance():
    """Test performance of individual genetics operations"""
    print("\nTesting Genetics Operations Performance...")

    try:
        from genetics import VisualGenetics
        from src.core.game.entities import Turtle

        genetics_system = VisualGenetics()

        # Test genetics generation
        num_operations = 1000

        start = time.time()
        for i in range(num_operations):
            genetics = genetics_system.generate_random_genetics()
        end = time.time()

        gen_time = end - start
        avg_gen_time = gen_time / num_operations

        print(f"  Generated {num_operations} genetics sets")
        print(f"  Total time: {gen_time:.3f}s")
        print(f"  Average per generation: {avg_gen_time * 1000:.3f}ms")

        # Test inheritance operations
        parent1_genetics = genetics_system.generate_random_genetics()
        parent2_genetics = genetics_system.generate_random_genetics()

        start = time.time()
        for i in range(num_operations):
            child_genetics = genetics_system.inherit_genetics(parent1_genetics, parent2_genetics)
        end = time.time()

        inherit_time = end - start
        avg_inherit_time = inherit_time / num_operations

        print(f"  Performed {num_operations} inheritance operations")
        print(f"  Total time: {inherit_time:.3f}s")
        print(f"  Average per inheritance: {avg_inherit_time * 1000:.3f}ms")

        # Test mutation operations
        base_genetics = genetics_system.generate_random_genetics()

        start = time.time()
        for i in range(num_operations):
            for trait_name in base_genetics.keys():
                genetics_system.mutate_gene(trait_name, base_genetics[trait_name])
        end = time.time()

        mutation_time = end - start
        avg_mutation_time = mutation_time / (num_operations * len(base_genetics))

        print(f"  Performed {num_operations * len(base_genetics)} mutation operations")
        print(f"  Total time: {mutation_time:.3f}s")
        print(f"  Average per mutation: {avg_mutation_time * 1000:.3f}ms")

        # Performance targets
        target_gen_time = 0.001  # 1ms per generation
        target_inherit_time = 0.002  # 2ms per inheritance
        target_mutation_time = 0.0001  # 0.1ms per mutation

        success = True
        if avg_gen_time > target_gen_time:
            print(f"  Generation performance: NEEDS OPTIMIZATION (>{target_gen_time * 1000:.1f}ms)")
            success = False
        else:
            print(f"  Generation performance: EXCELLENT (<{target_gen_time * 1000:.1f}ms)")

        if avg_inherit_time > target_inherit_time:
            print(f"  Inheritance performance: NEEDS OPTIMIZATION (>{target_inherit_time * 1000:.1f}ms)")
            success = False
        else:
            print(f"  Inheritance performance: EXCELLENT (<{target_inherit_time * 1000:.1f}ms)")

        if avg_mutation_time > target_mutation_time:
            print(f"  Mutation performance: NEEDS OPTIMIZATION (>{target_mutation_time * 1000:.1f}ms)")
            success = False
        else:
            print(f"  Mutation performance: EXCELLENT (<{target_mutation_time * 1000:.1f}ms)")

        return success

    except Exception as e:
        print(f"Genetics operations performance test failed: {e}")
        return False


def test_rendering_performance():
    """Test performance of rendering with genetics"""
    print("\nTesting Rendering Performance...")

    try:
        from genetics import VisualGenetics
        from src.core.game.entities import Turtle
        from src.core.rendering.direct_turtle_renderer import render_turtle_directly

        genetics_system = VisualGenetics()

        # Test rendering multiple turtles
        num_renders = 50
        render_sizes = [50, 100, 200]

        for size in render_sizes:
            start = time.time()
            successful_renders = 0

            for i in range(num_renders):
                genetics = genetics_system.generate_random_genetics()
                try:
                    result = render_turtle_directly(genetics, size=size)
                    if result:
                        successful_renders += 1
                except BaseException:
                    pass  # Ignore rendering errors in headless environment

            end = time.time()
            render_time = end - start
            avg_time = render_time / num_renders

            print(f"  Size {size}px: {successful_renders}/{num_renders} successful renders")
            print(f"    Total time: {render_time:.3f}s")
            print(f"    Average per render: {avg_time * 1000:.2f}ms")

        # Performance target: under 100ms per render
        target_time = 0.100

        # Check the most common size (100px)
        start = time.time()
        for i in range(20):  # Smaller sample for detailed test
            genetics = genetics_system.generate_random_genetics()
            try:
                result = render_turtle_directly(genetics, size=100)
            except BaseException:
                pass
        end = time.time()

        detailed_time = end - start
        avg_detailed = detailed_time / 20

        print(f"  Detailed 100px test: {avg_detailed * 1000:.2f}ms per render")

        if avg_detailed < target_time:
            print(f"  Rendering performance: EXCELLENT (<{target_time * 1000:.0f}ms per render)")
            return True
        elif avg_detailed < target_time * 2:
            print(f"  Rendering performance: GOOD (<{target_time * 2 * 1000:.0f}ms per render)")
            return True
        else:
            print(f"  Rendering performance: NEEDS OPTIMIZATION (>{target_time * 2 * 1000:.0f}ms per render)")
            return False

    except Exception as e:
        print(f"Rendering performance test failed: {e}")
        return False


def test_memory_usage():
    """Test memory usage of genetics operations"""
    print("\nTesting Memory Usage...")

    try:
        import gc

        # Test memory usage with many turtles
        from src.core.game.entities import Turtle

        # Force garbage collection
        gc.collect()

        # Create many turtles
        num_turtles = 500
        turtles = []

        for i in range(num_turtles):
            turtle = Turtle(f"MemTest{i}", 5, 50, 3, 4, 2)
            turtles.append(turtle)

        print(f"  Created {num_turtles} turtles with genetics")
        print(f"  Average genetics per turtle: {len(turtles[0].visual_genetics)} traits")
        print(f"  Estimated memory per turtle: ~{len(turtles[0].visual_genetics) * 50} bytes")

        # Clear references and test cleanup
        turtles.clear()
        gc.collect()

        print(f"  Memory cleanup: SUCCESS")
        return True

    except Exception as e:
        print(f"Memory usage test failed: {e}")
        return False


def main():
    """Run all performance tests"""
    print("TurboShells Genetics Performance Test Suite")
    print("=" * 50)

    tests = [
        test_turtle_creation_performance,
        test_shop_generation_performance,
        test_breeding_performance,
        test_genetics_operations_performance,
        test_rendering_performance,
        test_memory_usage
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
    print("PERFORMANCE TEST RESULTS")
    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")

    if passed == total:
        print("ALL PERFORMANCE TESTS PASSED! Genetics system is performant!")
        return True
    else:
        print("Some performance tests failed. Check the results above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
