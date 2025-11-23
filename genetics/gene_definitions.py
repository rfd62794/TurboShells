"""
Gene Definitions for TurboShells
Central registry of all genetic traits and their properties
"""

from typing import Dict, List, Tuple, Union


class GeneDefinitions:
    """
    Central registry of gene definitions with their types, ranges, and defaults.
    Single responsibility: Define and manage gene schemas.
    """
    
    def __init__(self):
        self.definitions = self._get_base_definitions()
    
    def _get_base_definitions(self) -> Dict[str, Dict]:
        """
        Define all available genes with their properties
        """
        return {
            # Shell Genetics
            'shell_base_color': {
                'type': 'rgb',
                'range': [(0, 255), (0, 255), (0, 255)],
                'default': (34, 139, 34),  # Forest green
                'description': 'Primary shell color'
            },
            'shell_pattern_type': {
                'type': 'discrete',
                'range': ['hex', 'spots', 'stripes', 'rings'],
                'default': 'hex',
                'description': 'Shell pattern type'
            },
            'shell_pattern_color': {
                'type': 'rgb',
                'range': [(0, 255), (0, 255), (0, 255)],
                'default': (255, 255, 255),  # White
                'description': 'Shell pattern color'
            },
            'pattern_color': {  # Alias for renderer compatibility
                'type': 'rgb',
                'range': [(0, 255), (0, 255), (0, 255)],
                'default': (255, 255, 255),  # White
                'description': 'Pattern color (used by renderer)'
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
            'leg_length': {
                'type': 'continuous',
                'range': (0.5, 1.5),
                'default': 1.0,
                'description': 'Leg length scaling'
            },
            'limb_shape': {
                'type': 'discrete',
                'range': ['flippers', 'feet', 'fins'],
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
    
    def get_gene_definition(self, gene_name: str) -> Dict:
        """Get definition for a specific gene"""
        return self.definitions.get(gene_name, {})
    
    def get_all_gene_names(self) -> List[str]:
        """Get list of all defined gene names"""
        return list(self.definitions.keys())
    
    def get_genes_by_type(self, gene_type: str) -> Dict[str, Dict]:
        """Get all genes of a specific type"""
        return {
            name: definition for name, definition in self.definitions.items()
            if definition.get('type') == gene_type
        }
    
    def get_default_genetics(self) -> Dict[str, Union[Tuple, str, float]]:
        """Get default values for all genes"""
        return {
            name: definition['default']
            for name, definition in self.definitions.items()
        }
    
    def validate_gene_value(self, gene_name: str, value: Union[Tuple, str, float]) -> bool:
        """Validate if a value is valid for a gene"""
        definition = self.get_gene_definition(gene_name)
        if not definition:
            return False
        
        gene_type = definition['type']
        value_range = definition['range']
        
        if gene_type == 'rgb':
            if not isinstance(value, tuple) or len(value) != 3:
                return False
            return all(
                isinstance(v, int) and value_range[i][0] <= v <= value_range[i][1]
                for i, v in enumerate(value)
            )
        elif gene_type == 'discrete':
            return value in value_range
        elif gene_type == 'continuous':
            return isinstance(value, (int, float)) and value_range[0] <= value <= value_range[1]
        
        return False
