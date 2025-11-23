"""
Visual Genetics System for TurboShells
Complete genetic system for turtle visual appearance with full gene control
"""

import random
from typing import Dict, List, Tuple, Union


class VisualGenetics:
    """
    Complete visual genetics system for turtle generation
    Every visual aspect is controlled by genetic parameters
    """
    
    def __init__(self):
        self.gene_definitions = {
            # Shell Genetics
            'shell_base_color': {
                'type': 'rgb',
                'range': [(0, 255), (0, 255), (0, 255)],
                'default': (34, 139, 34),  # Forest green
                'description': 'Primary shell color'
            },
            'shell_pattern_type': {
                'type': 'discrete',
                'range': ['hex', 'spots', 'stripes', 'rings'],  # Updated to match renderer
                'default': 'hex',
                'description': 'Shell pattern type'
            },
            'shell_pattern_color': {
                'type': 'rgb',
                'range': [(0, 255), (0, 255), (0, 255)],
                'default': (255, 255, 255),  # White
                'description': 'Shell pattern color'
            },
            'shell_pattern_density': {
                'type': 'continuous',
                'range': (0.1, 1.0),
                'default': 0.5,
                'description': 'Pattern density/intensity'
            },
            'shell_pattern_opacity': {
                'type': 'continuous',
                'range': (0.3, 1.0),
                'default': 0.8,
                'description': 'Pattern transparency'
            },
            'shell_size_modifier': {
                'type': 'continuous',
                'range': (0.5, 1.5),
                'default': 1.0,
                'description': 'Shell size scaling'
            },
            
            # Body Genetics
            'body_base_color': {
                'type': 'rgb',
                'range': [(0, 255), (0, 255), (0, 255)],
                'default': (107, 142, 35),  # Olive green
                'description': 'Primary body color'
            },
            'body_pattern_type': {
                'type': 'discrete',
                'range': ['solid', 'mottled', 'speckled', 'marbled'],
                'default': 'solid',
                'description': 'Body pattern type'
            },
            'body_pattern_color': {
                'type': 'rgb',
                'range': [(0, 255), (0, 255), (0, 255)],
                'default': (85, 107, 47),  # Dark olive green
                'description': 'Body pattern color'
            },
            'body_pattern_density': {
                'type': 'continuous',
                'range': (0.1, 1.0),
                'default': 0.3,
                'description': 'Body pattern density'
            },
            
            # Head Genetics
            'head_size_modifier': {
                'type': 'continuous',
                'range': (0.7, 1.3),
                'default': 1.0,
                'description': 'Head size scaling'
            },
            'head_color': {
                'type': 'rgb',
                'range': [(0, 255), (0, 255), (0, 255)],
                'default': (139, 90, 43),  # Brown
                'description': 'Head color'
            },
            
            # Leg Genetics
            'leg_length': {  # Updated key to match renderer
                'type': 'continuous',
                'range': (0.5, 1.5),  # Updated range to match renderer
                'default': 1.0,
                'description': 'Leg length scaling'
            },
            'limb_shape': {  # New gene for limb shape
                'type': 'discrete',
                'range': ['flippers', 'feet', 'fins'],  # Match renderer expectations
                'default': 'flippers',
                'description': 'Limb shape type'
            },
            'leg_thickness_modifier': {
                'type': 'continuous',
                'range': (0.7, 1.3),
                'default': 1.0,
                'description': 'Leg thickness'
            },
            'leg_color': {
                'type': 'rgb',
                'range': [(0, 255), (0, 255), (0, 255)],
                'default': (101, 67, 33),  # Dark brown
                'description': 'Leg color'
            },
            
            # Eye Genetics
            'eye_color': {
                'type': 'rgb',
                'range': [(0, 255), (0, 255), (0, 255)],
                'default': (0, 0, 0),  # Black
                'description': 'Eye color'
            },
            'eye_size_modifier': {
                'type': 'continuous',
                'range': (0.8, 1.2),
                'default': 1.0,
                'description': 'Eye size scaling'
            }
        }
    
    def generate_random_genetics(self) -> Dict[str, Union[Tuple, str, float]]:
        """
        Generate completely random visual genetics
        Returns a dictionary of all genetic traits with random values
        """
        genetics = {}
        for gene_name, gene_def in self.gene_definitions.items():
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
    
    def inherit_genetics(self, parent1_genetics: Dict, parent2_genetics: Dict) -> Dict[str, Union[Tuple, str, float]]:
        """
        Inherit genetics from two parents with mutation
        Implements Mendelian inheritance with random mutations
        """
        child_genetics = {}
        
        for gene_name in self.gene_definitions:
            # Random inheritance from either parent (50/50 chance)
            if random.random() < 0.5:
                inherited_value = parent1_genetics.get(gene_name, self.gene_definitions[gene_name]['default'])
            else:
                inherited_value = parent2_genetics.get(gene_name, self.gene_definitions[gene_name]['default'])
            
            # Apply mutation
            mutated_value = self.mutate_gene(gene_name, inherited_value)
            child_genetics[gene_name] = mutated_value
        
        return child_genetics
    
    def mutate_gene(self, gene_name: str, value: Union[Tuple, str, float]) -> Union[Tuple, str, float]:
        """
        Apply mutation to a gene value
        10% chance of mutation with varying effects based on gene type
        """
        mutation_rate = 0.1  # 10% chance of mutation
        
        if random.random() < mutation_rate:
            gene_def = self.gene_definitions[gene_name]
            gene_type = gene_def['type']
            
            if gene_type == 'rgb':
                # Slight color shift
                mutated = list(value)
                for i in range(3):
                    shift = random.randint(-20, 20)
                    mutated[i] = max(0, min(255, mutated[i] + shift))
                return tuple(mutated)
            elif gene_type == 'discrete':
                # Chance to change to different pattern
                if random.random() < 0.3:
                    available_patterns = [p for p in gene_def['range'] if p != value]
                    return random.choice(available_patterns) if available_patterns else value
                return value
            elif gene_type == 'continuous':
                # Small continuous change
                change = random.uniform(-0.1, 0.1)
                new_value = value + change
                value_range = gene_def['range']
                return max(value_range[0], min(value_range[1], new_value))
        
        return value
    
    def validate_genetics(self, genetics: Dict) -> Dict[str, bool]:
        """
        Validate that all genetic values are within acceptable ranges
        Returns a dictionary of validation results for each gene
        """
        validation_results = {}
        
        for gene_name, gene_def in self.gene_definitions.items():
            if gene_name not in genetics:
                validation_results[gene_name] = False
                continue
            
            value = genetics[gene_name]
            gene_type = gene_def['type']
            value_range = gene_def['range']
            
            if gene_type == 'rgb':
                is_valid = (
                    isinstance(value, tuple) and len(value) == 3 and
                    all(isinstance(v, int) and 0 <= v <= 255 for v in value) and
                    all(value_range[i][0] <= value[i] <= value_range[i][1] for i in range(3))
                )
            elif gene_type == 'discrete':
                is_valid = value in value_range
            elif gene_type == 'continuous':
                is_valid = isinstance(value, (int, float)) and value_range[0] <= value <= value_range[1]
            else:
                is_valid = False
            
            validation_results[gene_name] = is_valid
        
        return validation_results
    
    def get_gene_summary(self, genetics: Dict) -> Dict[str, str]:
        """
        Get human-readable summary of genetic traits
        """
        summary = {}
        
        for gene_name, value in genetics.items():
            if gene_name not in self.gene_definitions:
                continue
            
            gene_def = self.gene_definitions[gene_name]
            gene_type = gene_def['type']
            
            if gene_type == 'rgb':
                summary[gene_name] = f"RGB({value[0]}, {value[1]}, {value[2]})"
            elif gene_type == 'discrete':
                summary[gene_name] = value.title()
            elif gene_type == 'continuous':
                summary[gene_name] = f"{value:.2f}"
            else:
                summary[gene_name] = str(value)
        
        return summary
    
    def get_rarity_score(self, genetics: Dict) -> float:
        """
        Calculate rarity score based on genetic combinations
        Higher score = more rare combination
        """
        rarity_score = 0.0
        
        # Pattern combinations (rare patterns get higher score)
        shell_pattern = genetics.get('shell_pattern_type', 'stripes')
        body_pattern = genetics.get('body_pattern_type', 'solid')
        
        pattern_rarity = {
            'stripes': 1.0, 'spots': 1.2, 'spiral': 1.5, 'geometric': 1.8, 'complex': 2.0,
            'solid': 1.0, 'mottled': 1.3, 'speckled': 1.5, 'marbled': 1.8
        }
        
        rarity_score += pattern_rarity.get(shell_pattern, 1.0)
        rarity_score += pattern_rarity.get(body_pattern, 1.0)
        
        # Color harmony bonus (unusual color combinations)
        shell_color = genetics.get('shell_base_color', (34, 139, 34))
        pattern_color = genetics.get('shell_pattern_color', (255, 255, 255))
        
        # Calculate color contrast
        contrast = sum(abs(shell_color[i] - pattern_color[i]) for i in range(3)) / (255 * 3)
        rarity_score += contrast * 2.0
        
        # Size modifier extremes (very small or very large are rarer)
        shell_size = genetics.get('shell_size_modifier', 1.0)
        size_rarity = abs(shell_size - 1.0) * 2.0
        rarity_score += size_rarity
        
        # Pattern density extremes
        pattern_density = genetics.get('shell_pattern_density', 0.5)
        density_rarity = abs(pattern_density - 0.5) * 1.5
        rarity_score += density_rarity
        
        return rarity_score
    
    def get_trait_categories(self) -> Dict[str, List[str]]:
        """
        Get genes grouped by categories for UI organization
        """
        categories = {
            'shell': [
                'shell_base_color', 'shell_pattern_type', 'shell_pattern_color',
                'shell_pattern_density', 'shell_pattern_opacity', 'shell_size_modifier'
            ],
            'body': [
                'body_base_color', 'body_pattern_type', 'body_pattern_color', 'body_pattern_density'
            ],
            'head': [
                'head_size_modifier', 'head_color'
            ],
            'legs': [
                'leg_length_modifier', 'leg_thickness_modifier', 'leg_color'
            ],
            'eyes': [
                'eye_color', 'eye_size_modifier'
            ]
        }
        
        return categories
    
    def get_influenced_genetics(self, pool_weights: Dict, base_genetics: Dict = None) -> Dict[str, Union[Tuple, str, float]]:
        """
        Generate genetics influenced by genetic pool weights
        Used for creating turtles that reflect player voting preferences
        """
        if base_genetics is None:
            base_genetics = self.generate_random_genetics()
        
        influenced_genetics = base_genetics.copy()
        
        for gene_name, pool_data in pool_weights.items():
            if gene_name not in self.gene_definitions:
                continue
            
            weight = pool_data.get('weight', 0.5)
            
            # Use pool-influenced value based on weight probability
            if random.random() < weight:
                gene_def = self.gene_definitions[gene_name]
                influenced_value = self.generate_pool_influenced_value(gene_name, gene_def, pool_data)
                influenced_genetics[gene_name] = influenced_value
        
        return influenced_genetics
    
    def generate_pool_influenced_value(self, gene_name: str, gene_def: Dict, pool_data: Dict) -> Union[Tuple, str, float]:
        """
        Generate value influenced by genetic pool data
        """
        gene_type = gene_def['type']
        
        if gene_type == 'rgb' and all(key in pool_data for key in ['r_value', 'g_value', 'b_value']):
            # Use pool RGB values with some variation
            r = int(pool_data['r_value'] + random.uniform(-30, 30))
            g = int(pool_data['g_value'] + random.uniform(-30, 30))
            b = int(pool_data['b_value'] + random.uniform(-30, 30))
            return (
                max(0, min(255, r)),
                max(0, min(255, g)),
                max(0, min(255, b))
            )
        elif gene_type == 'discrete' and 'pattern_distribution' in pool_data:
            # Use weighted pattern selection
            distribution = pool_data['pattern_distribution']
            patterns = list(distribution.keys())
            weights = list(distribution.values())
            return random.choices(patterns, weights=weights)[0]
        elif gene_type == 'continuous' and 'target_value' in pool_data:
            # Use target value with variation
            target = pool_data['target_value']
            variation = target * 0.2  # 20% variation
            value_range = gene_def['range']
            new_value = target + random.uniform(-variation, variation)
            return max(value_range[0], min(value_range[1], new_value))
        else:
            # Fallback to random value
            return self.generate_random_gene_value(gene_def)


# Factory function for easy instantiation
def create_visual_genetics() -> VisualGenetics:
    """Create a VisualGenetics instance"""
    return VisualGenetics()


# Utility functions
def generate_random_turtle_genetics() -> Dict[str, Union[Tuple, str, float]]:
    """Generate random turtle genetics using default VisualGenetics instance"""
    vg = VisualGenetics()
    return vg.generate_random_genetics()


def inherit_turtle_genetics(parent1: Dict, parent2: Dict) -> Dict[str, Union[Tuple, str, float]]:
    """Inherit genetics from two parent turtles"""
    vg = VisualGenetics()
    return vg.inherit_genetics(parent1, parent2)


def calculate_genetics_rarity(genetics: Dict) -> float:
    """Calculate rarity score for turtle genetics"""
    vg = VisualGenetics()
    return vg.get_rarity_score(genetics)
