"""
Inheritance System for TurboShells
Handles Mendelian inheritance between parent turtles
"""

import random
from typing import Dict, List, Tuple, Union
from .gene_definitions import GeneDefinitions


class Inheritance:
    """
    Implements Mendelian inheritance patterns for genetic traits.
    Single responsibility: Handle gene inheritance logic.
    """
    
    def __init__(self, gene_definitions: GeneDefinitions = None):
        self.gene_definitions = gene_definitions or GeneDefinitions()
    
    def inherit_genetics(self, parent1_genetics: Dict, parent2_genetics: Dict) -> Dict[str, Union[Tuple, str, float]]:
        """
        Inherit genetics from two parents with random selection
        Implements basic Mendelian inheritance (50/50 chance from each parent)
        """
        child_genetics = {}
        
        for gene_name in self.gene_definitions.get_all_gene_names():
            # Get parent values or use defaults
            parent1_value = parent1_genetics.get(gene_name, 
                self.gene_definitions.get_gene_definition(gene_name).get('default'))
            parent2_value = parent2_genetics.get(gene_name, 
                self.gene_definitions.get_gene_definition(gene_name).get('default'))
            
            # Inherit from one parent (50/50 chance)
            if random.random() < 0.5:
                child_genetics[gene_name] = parent1_value
            else:
                child_genetics[gene_name] = parent2_value
        
        return child_genetics
    
    def inherit_with_dominance(self, parent1_genetics: Dict, parent2_genetics: Dict,
                              dominant_genes: Dict[str, str] = None) -> Dict[str, Union[Tuple, str, float]]:
        """
        Inherit genetics with dominant gene patterns
        dominant_genes: {'gene_name': 'parent1' or 'parent2'}
        """
        child_genetics = {}
        dominant_genes = dominant_genes or {}
        
        for gene_name in self.gene_definitions.get_all_gene_names():
            parent1_value = parent1_genetics.get(gene_name, 
                self.gene_definitions.get_gene_definition(gene_name).get('default'))
            parent2_value = parent2_genetics.get(gene_name, 
                self.gene_definitions.get_gene_definition(gene_name).get('default'))
            
            # Check for dominance
            dominance = dominant_genes.get(gene_name)
            if dominance == 'parent1':
                child_genetics[gene_name] = parent1_value
            elif dominance == 'parent2':
                child_genetics[gene_name] = parent2_value
            else:
                # Random inheritance
                child_genetics[gene_name] = parent1_value if random.random() < 0.5 else parent2_value
        
        return child_genetics
    
    def inherit_blended(self, parent1_genetics: Dict, parent2_genetics: Dict,
                       blend_genes: List[str] = None) -> Dict[str, Union[Tuple, str, float]]:
        """
        Inherit genetics with blending for continuous values
        blend_genes: List of gene names to blend (average)
        """
        child_genetics = {}
        blend_genes = blend_genes or []
        
        for gene_name in self.gene_definitions.get_all_gene_names():
            parent1_value = parent1_genetics.get(gene_name, 
                self.gene_definitions.get_gene_definition(gene_name).get('default'))
            parent2_value = parent2_genetics.get(gene_name, 
                self.gene_definitions.get_gene_definition(gene_name).get('default'))
            
            gene_def = self.gene_definitions.get_gene_definition(gene_name)
            
            if gene_name in blend_genes and gene_def['type'] == 'continuous':
                # Blend continuous values
                child_genetics[gene_name] = (parent1_value + parent2_value) / 2
            elif gene_name in blend_genes and gene_def['type'] == 'rgb':
                # Blend colors
                child_genetics[gene_name] = tuple(
                    int((parent1_value[i] + parent2_value[i]) / 2)
                    for i in range(3)
                )
            else:
                # Random inheritance
                child_genetics[gene_name] = parent1_value if random.random() < 0.5 else parent2_value
        
        return child_genetics
    
    def inherit_color_patterns(self, parent1_genetics: Dict, parent2_genetics: Dict) -> Dict[str, Union[Tuple, str, float]]:
        """
        Specialized inheritance for color patterns with mixing
        """
        child_genetics = {}
        
        for gene_name in self.gene_definitions.get_all_gene_names():
            gene_def = self.gene_definitions.get_gene_definition(gene_name)
            parent1_value = parent1_genetics.get(gene_name, gene_def.get('default'))
            parent2_value = parent2_genetics.get(gene_name, gene_def.get('default'))
            
            if gene_def['type'] == 'rgb':
                # Color mixing with random bias
                bias = random.uniform(0.3, 0.7)  # Bias towards one parent
                child_genetics[gene_name] = tuple(
                    int(parent1_value[i] * bias + parent2_value[i] * (1 - bias))
                    for i in range(3)
                )
            elif gene_def['type'] == 'discrete' and 'pattern' in gene_name:
                # Pattern inheritance with preference
                if random.random() < 0.7:  # 70% chance to inherit pattern type
                    child_genetics[gene_name] = parent1_value if random.random() < 0.5 else parent2_value
                else:
                    # Random pattern
                    child_genetics[gene_name] = random.choice(gene_def['range'])
            else:
                # Standard inheritance
                child_genetics[gene_name] = parent1_value if random.random() < 0.5 else parent2_value
        
        return child_genetics
    
    def calculate_genetic_similarity(self, genetics1: Dict, genetics2: Dict) -> float:
        """
        Calculate similarity percentage between two genetic profiles
        """
        total_genes = len(self.gene_definitions.get_all_gene_names())
        similar_genes = 0
        
        for gene_name in self.gene_definitions.get_all_gene_names():
            gene_def = self.gene_definitions.get_gene_definition(gene_name)
            value1 = genetics1.get(gene_name, gene_def.get('default'))
            value2 = genetics2.get(gene_name, gene_def.get('default'))
            
            if gene_def['type'] == 'rgb':
                # Color similarity (Euclidean distance in RGB space)
                distance = sum((value1[i] - value2[i]) ** 2 for i in range(3)) ** 0.5
                max_distance = (255 ** 2 * 3) ** 0.5  # Maximum possible distance
                similarity = 1 - (distance / max_distance)
                if similarity > 0.8:  # Consider similar if >80% similar
                    similar_genes += 1
            elif value1 == value2:
                similar_genes += 1
        
        return similar_genes / total_genes if total_genes > 0 else 0
