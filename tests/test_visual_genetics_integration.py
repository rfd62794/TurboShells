"""
Visual Genetics Integration Test
Complete integration test for the SVG generation and voting system
"""

import sys
import os
import time
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import pygame
    pygame_available = True
except ImportError:
    pygame_available = False
    print("Warning: PyGame not available, some tests will be skipped")

# Import core components
from core.visual_genetics import VisualGenetics
from core.genetic_svg_mapper import GeneticToSVGMapper
from core.turtle_svg_generator import TurtleSVGGenerator
from core.pattern_generators import PatternGenerators
from core.voting_system import VotingSystem
from core.genetic_pool_manager import GeneticPoolManager


def test_visual_genetics():
    """Test VisualGenetics system"""
    print("\n=== Testing VisualGenetics ===")
    
    vg = VisualGenetics()
    
    # Test random genetics generation
    random_genetics = vg.generate_random_genetics()
    print(f"Generated {len(random_genetics)} genetic traits")
    
    # Test genetics validation
    validation = vg.validate_genetics(random_genetics)
    print(f"Genetics validation: {'PASS' if all(validation.values()) else 'FAIL'}")
    
    # Test inheritance
    parent1 = vg.generate_random_genetics()
    parent2 = vg.generate_random_genetics()
    child = vg.inherit_genetics(parent1, parent2)
    print(f"Inheritance test: {'PASS' if len(child) == len(parent1) else 'FAIL'}")
    
    # Test rarity calculation
    rarity = vg.get_rarity_score(random_genetics)
    print(f"Rarity score: {rarity:.2f}")
    
    return True


def test_genetic_svg_mapper():
    """Test GeneticToSVGMapper system"""
    print("\n=== Testing GeneticToSVGMapper ===")
    
    vg = VisualGenetics()
    mapper = GeneticToSVGMapper()
    
    # Test genetics to SVG mapping
    genetics = vg.generate_random_genetics()
    svg_params = mapper.map_genetics_to_svg_params(genetics)
    print(f"Mapped {len(svg_params)} SVG elements")
    
    # Test parameter validation
    validation = mapper.validate_svg_params(svg_params)
    print(f"SVG validation: {'PASS' if all(validation.values()) else 'FAIL'}")
    
    # Test RGB conversion
    rgb_color = (255, 128, 64)
    hex_color = mapper.rgb_to_hex(rgb_color)
    converted_rgb = mapper.hex_to_rgb(hex_color)
    print(f"RGB conversion: {'PASS' if rgb_color == converted_rgb else 'FAIL'}")
    
    return True


def test_pattern_generators():
    """Test PatternGenerators system"""
    print("\n=== Testing PatternGenerators ===")
    
    pg = PatternGenerators()
    
    # Test all shell patterns
    patterns = pg.get_available_patterns()
    print(f"Available patterns: {patterns}")
    
    for pattern in patterns:
        validation = pg.validate_pattern_parameters(pattern, 100, '#FF0000', 0.5, 0.8)
        print(f"  {pattern}: {'PASS' if all(validation.values()) else 'FAIL'}")
    
    # Test body patterns
    body_patterns = pg.get_available_body_patterns()
    print(f"Body patterns: {body_patterns}")
    
    return True


def test_turtle_svg_generator():
    """Test TurtleSVGGenerator system"""
    print("\n=== Testing TurtleSVGGenerator ===")
    
    vg = VisualGenetics()
    generator = TurtleSVGGenerator()
    
    # Test random turtle generation
    random_genetics = vg.generate_random_genetics()
    svg_drawing = generator.generate_turtle_svg(random_genetics)
    print(f"SVG generation: {'PASS' if svg_drawing is not None else 'FAIL'}")
    
    # Test validation
    validation = generator.validate_svg_generation(random_genetics)
    print(f"Generation validation: {'PASS' if validation['overall'] else 'FAIL'}")
    
    # Test statistics
    stats = generator.get_generation_stats(random_genetics)
    print(f"Generation stats: {stats['gene_count']} genes, {stats['color_count']} colors")
    
    # Test inheritance
    parent1 = vg.generate_random_genetics()
    parent2 = vg.generate_random_genetics()
    child_svg = generator.generate_turtle_from_parents(parent1, parent2)
    print(f"Inheritance generation: {'PASS' if child_svg is not None else 'FAIL'}")
    
    return True


def test_voting_system():
    """Test VotingSystem"""
    print("\n=== Testing VotingSystem ===")
    
    voting_system = VotingSystem()
    genetic_pool_manager = GeneticPoolManager()
    voting_system.set_genetic_pool_manager(genetic_pool_manager)
    
    # Generate daily designs
    designs = voting_system.generate_daily_designs()
    print(f"Generated {len(designs)} daily designs")
    
    test_passed = True
    
    # Test voting
    if designs:
        design = designs[0]
        test_ratings = {
            'overall': 4.0,
            'shell_appearance': 3.5,
            'color_harmony': 4.5,
            'pattern_quality': 3.0,
            'proportions': 4.0
        }
        
        result = voting_system.submit_ratings(design.id, test_ratings)
        vote_success = result.get('success', False)
        reward_earned = result.get('reward_earned', 0) > 0
        
        print(f"Vote submission: {'PASS' if vote_success else 'FAIL'}")
        print(f"Reward earned: ${result.get('reward_earned', 0)}")
        
        test_passed = test_passed and vote_success and reward_earned
    
    # Test status
    status = voting_system.get_daily_status()
    print(f"Daily status: {status['completed_votes']}/{status['total_designs']} completed")
    
    # Test statistics
    stats = voting_system.get_statistics()
    print(f"Total votes cast: {stats['total_votes_cast']}")
    
    return test_passed


def test_genetic_pool_manager():
    """Test GeneticPoolManager"""
    print("\n=== Testing GeneticPoolManager ===")
    
    vg = VisualGenetics()
    pool_manager = GeneticPoolManager()
    
    test_passed = True
    
    # Test applying ratings
    design_genetics = vg.generate_random_genetics()
    test_ratings = {
        'overall': 4.0,
        'shell_appearance': 3.5,
        'color_harmony': 4.5
    }
    
    impact = pool_manager.apply_ratings_to_pool(design_genetics, test_ratings)
    trait_changes = len(impact.get('trait_changes', []))
    print(f"Applied ratings impact: {trait_changes} traits changed")
    
    test_passed = test_passed and trait_changes > 0
    
    # Test influenced genetics generation
    influenced_genetics = pool_manager.generate_influenced_genetics()
    trait_count = len(influenced_genetics)
    print(f"Generated influenced genetics: {trait_count} traits")
    
    test_passed = test_passed and trait_count > 0
    
    # Test pool status
    pool_status = pool_manager.get_genetic_pool_status()
    avg_weight = pool_status.get('average_weight', 0)
    print(f"Pool average weight: {avg_weight:.2f}")
    
    test_passed = test_passed and avg_weight > 0
    
    # Test most influenced traits
    most_influenced = pool_status.get('most_influenced_traits', [])[:3]
    trait_names = [trait[0] for trait in most_influenced]
    print(f"Most influenced traits: {trait_names}")
    
    return test_passed


def test_complete_integration():
    """Test complete system integration"""
    print("\n=== Testing Complete Integration ===")
    
    # Initialize all components
    vg = VisualGenetics()
    mapper = GeneticToSVGMapper()
    generator = TurtleSVGGenerator()
    voting_system = VotingSystem()
    pool_manager = GeneticPoolManager()
    
    # Connect systems
    voting_system.set_genetic_pool_manager(pool_manager)
    
    # Generate daily designs
    designs = voting_system.generate_daily_designs()
    print(f"Generated {len(designs)} designs for voting")
    
    test_passed = True
    
    # Simulate complete voting session
    total_rewards = 0
    successful_votes = 0
    for i, design in enumerate(designs):
        # Generate test ratings
        test_ratings = {
            'overall': 3.0 + (i * 0.5),  # Varying ratings
            'shell_appearance': 3.5,
            'color_harmony': 4.0,
            'pattern_quality': 3.0,
            'proportions': 4.0
        }
        
        # Submit ratings
        result = voting_system.submit_ratings(design.id, test_ratings)
        if result.get('success', False):
            total_rewards += result.get('reward_earned', 0)
            successful_votes += 1
            print(f"  Design {i+1}: Voted, earned ${result['reward_earned']}")
    
    test_passed = test_passed and successful_votes == len(designs)
    
    print(f"Total session rewards: ${total_rewards}")
    
    # Generate influenced turtle after voting
    influenced_genetics = pool_manager.generate_influenced_genetics()
    influenced_svg = generator.generate_turtle_svg(influenced_genetics)
    svg_success = influenced_svg is not None
    print(f"Influenced turtle generation: {'PASS' if svg_success else 'FAIL'}")
    
    test_passed = test_passed and svg_success
    
    # Test system statistics
    voting_stats = voting_system.get_statistics()
    pool_stats = pool_manager.get_genetic_pool_status()
    
    print(f"Final voting stats: {voting_stats['total_votes_cast']} votes, ${voting_stats['total_rewards_earned']} earned")
    print(f"Final pool stats: {pool_stats['average_weight']:.2f} average weight")
    
    return test_passed


def test_performance():
    """Test system performance"""
    print("\n=== Testing Performance ===")
    
    vg = VisualGenetics()
    generator = TurtleSVGGenerator()
    
    # Test generation speed
    start_time = time.time()
    for i in range(10):
        genetics = vg.generate_random_genetics()
        svg = generator.generate_turtle_svg(genetics)
    
    generation_time = time.time() - start_time
    avg_time = generation_time / 10
    print(f"Average turtle generation time: {avg_time:.3f}s")
    
    # Test inheritance speed
    start_time = time.time()
    parent1 = vg.generate_random_genetics()
    parent2 = vg.generate_random_genetics()
    
    for i in range(10):
        child_genetics = vg.inherit_genetics(parent1, parent2)
        child_svg = generator.generate_turtle_from_parents(parent1, parent2)
    
    inheritance_time = time.time() - start_time
    avg_inheritance_time = inheritance_time / 10
    print(f"Average inheritance time: {avg_inheritance_time:.3f}s")
    
    return True


def run_all_tests():
    """Run all integration tests"""
    print("Starting Visual Genetics Integration Tests")
    print("=" * 50)
    
    tests = [
        ("VisualGenetics", test_visual_genetics),
        ("GeneticToSVGMapper", test_genetic_svg_mapper),
        ("PatternGenerators", test_pattern_generators),
        ("TurtleSVGGenerator", test_turtle_svg_generator),
        ("VotingSystem", test_voting_system),
        ("GeneticPoolManager", test_genetic_pool_manager),
        ("Complete Integration", test_complete_integration),
        ("Performance", test_performance)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            start_time = time.time()
            result = test_func()
            duration = time.time() - start_time
            
            results.append({
                'name': test_name,
                'passed': result,
                'duration': duration
            })
            
            print(f"\n{test_name}: {'PASS' if result else 'FAIL'} ({duration:.2f}s)")
            
        except Exception as e:
            print(f"\n{test_name}: ERROR - {e}")
            results.append({
                'name': test_name,
                'passed': False,
                'duration': 0,
                'error': str(e)
            })
    
    # Print summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    
    for result in results:
        status = "PASS" if result['passed'] else "FAIL"
        duration = result['duration']
        print(f"{result['name']:20} {status:6} ({duration:.2f}s)")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! The visual genetics system is ready for integration.")
    else:
        print("Some tests failed. Please review the errors above.")
    
    return results


if __name__ == "__main__":
    run_all_tests()
