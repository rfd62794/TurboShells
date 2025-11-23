"""
Gene Generator for TurboShells
Responsible for generating random genetic values
"""

import random
from typing import Dict, List, Tuple, Union
from .gene_definitions import GeneDefinitions


class GeneGenerator:
    """
    Generates random genetic values based on gene definitions.
    Single responsibility: Create random genetic variations.
    """
    
    def __init__(self, gene_definitions: GeneDefinitions = None):
        self.gene_definitions = gene_definitions or GeneDefinitions()
    
    def generate_random_genetics(self) -> Dict[str, Union[Tuple, str, float]]:
        """
        Generate completely random visual genetics
        Returns a dictionary of all genetic traits with random values
        """
        genetics = {}
        for gene_name, gene_def in self.gene_definitions.definitions.items():
            genetics[gene_name] = self.generate_random_gene_value(gene_def)
        return genetics
    
    def generate_random_gene_value(self, gene_def: Dict) -> Union[Tuple, str, float]:
        """
        Generate random value for a specific gene based on its definition
        """
        gene_type = gene_def['type']
        value_range = gene_def['range']
        
        if gene_type == 'rgb':
            return (
                random.randint(value_range[0][0], value_range[0][1]),
                random.randint(value_range[1][0], value_range[1][1]),
                random.randint(value_range[2][0], value_range[2][1])
            )
        elif gene_type == 'discrete':
            return random.choice(value_range)
        elif gene_type == 'continuous':
            return random.uniform(value_range[0], value_range[1])
        else:
            return gene_def['default']
    
    def generate_partial_genetics(self, gene_names: List[str]) -> Dict[str, Union[Tuple, str, float]]:
        """
        Generate random values for specific genes only
        """
        genetics = {}
        for gene_name in gene_names:
            gene_def = self.gene_definitions.get_gene_definition(gene_name)
            if gene_def:
                genetics[gene_name] = self.generate_random_gene_value(gene_def)
        return genetics
    
    def generate_weighted_genetics(self, weights: Dict[str, float]) -> Dict[str, Union[Tuple, str, float]]:
        """
        Generate genetics with weighted probability distributions
        """
        genetics = {}
        for gene_name, gene_def in self.gene_definitions.definitions.items():
            weight = weights.get(gene_name, 1.0)
            if random.random() < weight:
                genetics[gene_name] = self.generate_random_gene_value(gene_def)
            else:
                genetics[gene_name] = gene_def['default']
        return genetics
    
    def generate_color_variations(self, base_color: Tuple[int, int, int], 
                                variation_range: int = 30) -> List[Tuple[int, int, int]]:
        """
        Generate variations of a base color
        """
        variations = []
        for _ in range(5):  # Generate 5 variations
            variation = tuple(
                max(0, min(255, base_color[i] + random.randint(-variation_range, variation_range)))
                for i in range(3)
            )
            variations.append(variation)
        return variations
    
    def generate_pattern_variations(self, base_pattern: str) -> List[str]:
        """
        Generate variations of a pattern type
        """
        all_patterns = ['hex', 'spots', 'stripes', 'rings']
        variations = []
        
        # Include the base pattern
        variations.append(base_pattern)
        
        # Add 2-3 other random patterns
        other_patterns = [p for p in all_patterns if p != base_pattern]
        variations.extend(random.sample(other_patterns, min(3, len(other_patterns))))
        
        return variations
    
    def generate_size_variations(self, base_size: float, variation_percent: float = 0.2) -> List[float]:
        """
        Generate size variations around a base size
        """
        variations = []
        for _ in range(3):
            variation = base_size * (1 + random.uniform(-variation_percent, variation_percent))
            # Clamp to reasonable bounds
            variation = max(0.1, min(3.0, variation))
            variations.append(variation)
        return variations
