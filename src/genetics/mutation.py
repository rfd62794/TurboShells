"""
Mutation System for TurboShells
Handles genetic mutations and variations
"""

import random
import math
from typing import Dict, List, Tuple, Union
from .gene_definitions import GeneDefinitions


class Mutation:
    """
    Implements genetic mutations with various patterns and intensities.
    Single responsibility: Handle gene mutation logic.
    """

    def __init__(self, gene_definitions: GeneDefinitions = None):
        self.gene_definitions = gene_definitions or GeneDefinitions()

    def mutate_genetics(self, genetics: Dict, mutation_rate: float = 0.1) -> Dict[str, Union[Tuple, str, float]]:
        """
        Apply mutations to genetics with specified rate
        """
        mutated_genetics = genetics.copy()

        for gene_name, value in genetics.items():
            if random.random() < mutation_rate:
                mutated_value = self.mutate_gene(gene_name, value)
                mutated_genetics[gene_name] = mutated_value

        return mutated_genetics

    def mutate_gene(self, gene_name: str, value: Union[Tuple, str, float]) -> Union[Tuple, str, float]:
        """
        Apply mutation to a single gene value
        """
        gene_def = self.gene_definitions.get_gene_definition(gene_name)
        if not gene_def:
            return value

        gene_type = gene_def['type']
        value_range = gene_def['range']

        if gene_type == 'rgb':
            return self._mutate_rgb_color(value, value_range)
        elif gene_type == 'discrete':
            return self._mutate_discrete_value(value, value_range)
        elif gene_type == 'continuous':
            return self._mutate_continuous_value(value, value_range)

        return value

    def _mutate_rgb_color(self, color: Tuple[int, int, int],
                          value_range: List[Tuple[int, int]]) -> Tuple[int, int, int]:
        """
        Mutate RGB color with slight variations
        """
        mutated = list(color)

        for i in range(3):
            # Small color shift
            shift = random.randint(-30, 30)
            mutated[i] = max(value_range[i][0], min(value_range[i][1], color[i] + shift))

        return tuple(mutated)

    def _mutate_discrete_value(self, value: str, value_range: List[str]) -> str:
        """
        Mutate discrete value by selecting a different option
        """
        available_options = [v for v in value_range if v != value]
        return random.choice(available_options) if available_options else value

    def _mutate_continuous_value(self, value: float, value_range: Tuple[float, float]) -> float:
        """
        Mutate continuous value with gaussian noise
        """
        # Calculate mutation strength based on range
        range_size = value_range[1] - value_range[0]
        mutation_strength = range_size * 0.1  # 10% of range

        # Apply gaussian mutation
        mutation = random.gauss(0, mutation_strength)
        mutated_value = value + mutation

        # Clamp to valid range
        return max(value_range[0], min(value_range[1], mutated_value))

    def mutate_with_intensity(self, genetics: Dict, intensity: str = 'moderate') -> Dict[str, Union[Tuple, str, float]]:
        """
        Apply mutations with different intensity levels
        """
        intensity_rates = {
            'low': 0.05,
            'moderate': 0.1,
            'high': 0.2,
            'extreme': 0.3
        }

        mutation_rate = intensity_rates.get(intensity, 0.1)
        return self.mutate_genetics(genetics, mutation_rate)

    def targeted_mutation(self, genetics: Dict, target_genes: List[str],
                          mutation_rate: float = 0.3) -> Dict[str, Union[Tuple, str, float]]:
        """
        Apply mutations only to specific target genes
        """
        mutated_genetics = genetics.copy()

        for gene_name in target_genes:
            if gene_name in genetics:
                value = genetics[gene_name]
                if random.random() < mutation_rate:
                    mutated_value = self.mutate_gene(gene_name, value)
                    mutated_genetics[gene_name] = mutated_value

        return mutated_genetics

    def adaptive_mutation(self, genetics: Dict, parent_similarity: float) -> Dict[str, Union[Tuple, str, float]]:
        """
        Apply mutations based on parent similarity
        Higher similarity = higher mutation rate (to avoid stagnation)
        """
        # Adaptive mutation rate based on similarity
        if parent_similarity > 0.9:
            mutation_rate = 0.3  # High mutation for very similar parents
        elif parent_similarity > 0.7:
            mutation_rate = 0.2  # Moderate-high mutation
        elif parent_similarity > 0.5:
            mutation_rate = 0.1  # Moderate mutation
        else:
            mutation_rate = 0.05  # Low mutation for diverse parents

        return self.mutate_genetics(genetics, mutation_rate)

    def pattern_mutation(self, genetics: Dict) -> Dict[str, Union[Tuple, str, float]]:
        """
        Apply pattern-based mutations (coordinated changes)
        """
        mutated_genetics = genetics.copy()

        # Pattern 1: Shell color coordination
        if random.random() < 0.1:  # 10% chance
            shell_base = genetics.get('shell_base_color', (34, 139, 34))
            pattern_color = genetics.get('pattern_color', (255, 255, 255))

            # Make pattern color complementary to shell
            mutated_genetics['pattern_color'] = tuple(
                255 - c for c in shell_base
            )

        # Pattern 2: Body part coordination
        if random.random() < 0.1:  # 10% chance
            head_color = genetics.get('head_color', (139, 90, 43))
            leg_color = genetics.get('leg_color', (101, 67, 33))

            # Coordinate head and leg colors
            if random.random() < 0.5:
                mutated_genetics['leg_color'] = head_color
            else:
                # Make leg color darker version of head
                mutated_genetics['leg_color'] = tuple(
                    max(0, int(c * 0.7)) for c in head_color
                )

        # Pattern 3: Size coordination
        if random.random() < 0.15:  # 15% chance
            size_modifier = random.uniform(0.9, 1.1)

            size_genes = ['shell_size_modifier', 'head_size_modifier', 'leg_length']
            for gene in size_genes:
                if gene in genetics:
                    current_value = genetics[gene]
                    gene_def = self.gene_definitions.get_gene_definition(gene)
                    if gene_def and gene_def['type'] == 'continuous':
                        mutated_value = current_value * size_modifier
                        # Clamp to valid range
                        mutated_value = max(gene_def['range'][0],
                                            min(gene_def['range'][1], mutated_value))
                        mutated_genetics[gene] = mutated_value

        return mutated_genetics

    def calculate_mutation_strength(self, original_genetics: Dict,
                                    mutated_genetics: Dict) -> float:
        """
        Calculate the strength of mutations applied
        """
        total_difference = 0
        gene_count = 0

        for gene_name in self.gene_definitions.get_all_gene_names():
            if gene_name in original_genetics and gene_name in mutated_genetics:
                original_value = original_genetics[gene_name]
                mutated_value = mutated_genetics[gene_name]

                gene_def = self.gene_definitions.get_gene_definition(gene_name)

                if gene_def['type'] == 'rgb':
                    # Color difference
                    difference = sum(abs(original_value[i] - mutated_value[i]) for i in range(3))
                    max_difference = 255 * 3  # Maximum possible difference
                    total_difference += difference / max_difference
                elif gene_def['type'] == 'continuous':
                    # Continuous difference
                    value_range = gene_def['range']
                    range_size = value_range[1] - value_range[0]
                    difference = abs(original_value - mutated_value) / range_size
                    total_difference += difference
                elif gene_def['type'] == 'discrete':
                    # Discrete difference (0 or 1)
                    total_difference += 0 if original_value == mutated_value else 1

                gene_count += 1

        return total_difference / gene_count if gene_count > 0 else 0
