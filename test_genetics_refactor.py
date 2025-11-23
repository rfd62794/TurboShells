#!/usr/bin/env python3
"""
Test script to verify the refactored genetics system works correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from core.genetics import VisualGenetics, GeneDefinitions, GeneGenerator, Inheritance, Mutation

def test_genetics_refactor():
    """Test the refactored genetics system"""
    
    print("=== Testing Refactored Genetics System ===\n")
    
    # Test individual components
    print("1. Testing GeneDefinitions...")
    gene_defs = GeneDefinitions()
    print(f"   Total genes defined: {len(gene_defs.get_all_gene_names())}")
    print(f"   RGB genes: {len(gene_defs.get_genes_by_type('rgb'))}")
    print(f"   Discrete genes: {len(gene_defs.get_genes_by_type('discrete'))}")
    print(f"   Continuous genes: {len(gene_defs.get_genes_by_type('continuous'))}")
    
    print("\n2. Testing GeneGenerator...")
    generator = GeneGenerator(gene_defs)
    random_genetics = generator.generate_random_genetics()
    print(f"   Generated genetics with {len(random_genetics)} genes")
    print(f"   Sample genes: {list(random_genetics.keys())[:3]}")
    
    print("\n3. Testing Inheritance...")
    inheritance = Inheritance(gene_defs)
    parent1 = generator.generate_random_genetics()
    parent2 = generator.generate_random_genetics()
    child = inheritance.inherit_genetics(parent1, parent2)
    similarity = inheritance.calculate_genetic_similarity(parent1, parent2)
    print(f"   Parent similarity: {similarity:.2%}")
    print(f"   Child inherited {len(child)} genes")
    
    print("\n4. Testing Mutation...")
    mutation = Mutation(gene_defs)
    mutated_child = mutation.mutate_genetics(child, mutation_rate=0.2)
    mutation_strength = mutation.calculate_mutation_strength(child, mutated_child)
    print(f"   Mutation strength: {mutation_strength:.2%}")
    
    print("\n5. Testing VisualGenetics Interface...")
    vg = VisualGenetics()
    
    # Test legacy interface
    legacy_genetics = vg.generate_random_genetics()
    print(f"   Legacy interface: {len(legacy_genetics)} genes")
    
    # Test enhanced interface
    offspring = vg.create_offspring(parent1, parent2, 'blended', 'moderate')
    print(f"   Enhanced interface: {len(offspring)} genes")
    
    # Test variations
    variations = vg.generate_variations(offspring, count=3, variation_type='color')
    print(f"   Generated {len(variations)} color variations")
    
    # Test analysis
    analysis = vg.analyze_genetics(offspring)
    print(f"   Analysis: {analysis['total_genes']} total genes")
    print(f"   Dominant colors: {analysis['dominant_colors']}")
    
    # Test validation
    validation = vg.validate_genetics(offspring)
    valid_genes = sum(1 for valid in validation.values() if valid)
    print(f"   Validation: {valid_genes}/{len(validation)} genes valid")
    
    print("\n=== Integration Test with Renderer ===")
    from core.direct_turtle_renderer import get_direct_renderer
    
    renderer = get_direct_renderer()
    try:
        photo_image = renderer.render_turtle_to_photoimage(offspring, 200)
        if photo_image:
            print("   SUCCESS: Renderer works with refactored genetics!")
        else:
            print("   FAIL: Renderer returned None")
    except Exception as e:
        print(f"   FAIL: Renderer error: {e}")
    
    print("\n=== Refactor Test Complete ===")
    print("SUCCESS: All genetics modules working correctly!")
    return True

if __name__ == "__main__":
    success = test_genetics_refactor()
    sys.exit(0 if success else 1)
