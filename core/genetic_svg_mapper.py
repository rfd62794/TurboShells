"""
Genetic to SVG Parameter Mapping System
Complete mapping from genetic values to SVG rendering parameters
"""

from typing import Dict, Any, Union, Tuple
from .visual_genetics import VisualGenetics


class GeneticToSVGMapper:
    """
    Complete mapping from genetic values to SVG rendering parameters
    Each genetic trait directly controls specific SVG properties
    """
    
    def __init__(self):
        self.visual_genetics = VisualGenetics()
        self.gene_svg_mapping = {
            # Shell Genetics
            'shell_base_color': {
                'svg_property': 'fill',
                'target_element': 'shell',
                'value_type': 'rgb_to_hex',
                'control_range': {'r': (0, 255), 'g': (0, 255), 'b': (0, 255)},
                'default_value': (34, 139, 34),  # Forest green
                'description': 'Primary shell color'
            },
            'shell_pattern_type': {
                'svg_property': 'pattern_generator',
                'target_element': 'shell_pattern',
                'value_type': 'discrete',
                'control_range': ['stripes', 'spots', 'spiral', 'geometric', 'complex'],
                'default_value': 'stripes',
                'description': 'Shell pattern type'
            },
            'shell_pattern_color': {
                'svg_property': 'stroke',
                'target_element': 'shell_pattern',
                'value_type': 'rgb_to_hex',
                'control_range': {'r': (0, 255), 'g': (0, 255), 'b': (0, 255)},
                'default_value': (255, 255, 255),  # White
                'description': 'Shell pattern color'
            },
            'shell_pattern_density': {
                'svg_property': 'density_factor',
                'target_element': 'shell_pattern',
                'value_type': 'continuous',
                'control_range': (0.1, 1.0),
                'default_value': 0.5,
                'description': 'Pattern density/intensity'
            },
            'shell_pattern_opacity': {
                'svg_property': 'opacity',
                'target_element': 'shell_pattern',
                'value_type': 'continuous',
                'control_range': (0.3, 1.0),
                'default_value': 0.8,
                'description': 'Pattern transparency'
            },
            'shell_size_modifier': {
                'svg_property': 'transform',
                'target_element': 'shell',
                'value_type': 'scale',
                'control_range': (0.5, 1.5),
                'default_value': 1.0,
                'description': 'Shell size scaling'
            },
            
            # Body Genetics
            'body_base_color': {
                'svg_property': 'fill',
                'target_element': 'body',
                'value_type': 'rgb_to_hex',
                'control_range': {'r': (0, 255), 'g': (0, 255), 'b': (0, 255)},
                'default_value': (107, 142, 35),  # Olive green
                'description': 'Primary body color'
            },
            'body_pattern_type': {
                'svg_property': 'pattern_generator',
                'target_element': 'body_pattern',
                'value_type': 'discrete',
                'control_range': ['solid', 'mottled', 'speckled', 'marbled'],
                'default_value': 'solid',
                'description': 'Body pattern type'
            },
            'body_pattern_color': {
                'svg_property': 'fill',
                'target_element': 'body_pattern',
                'value_type': 'rgb_to_hex',
                'control_range': {'r': (0, 255), 'g': (0, 255), 'b': (0, 255)},
                'default_value': (85, 107, 47),  # Dark olive green
                'description': 'Body pattern color'
            },
            'body_pattern_density': {
                'svg_property': 'density_factor',
                'target_element': 'body_pattern',
                'value_type': 'continuous',
                'control_range': (0.1, 1.0),
                'default_value': 0.3,
                'description': 'Body pattern density'
            },
            
            # Head Genetics
            'head_size_modifier': {
                'svg_property': 'transform',
                'target_element': 'head',
                'value_type': 'scale',
                'control_range': (0.7, 1.3),
                'default_value': 1.0,
                'description': 'Head size scaling'
            },
            'head_color': {
                'svg_property': 'fill',
                'target_element': 'head',
                'value_type': 'rgb_to_hex',
                'control_range': {'r': (0, 255), 'g': (0, 255), 'b': (0, 255)},
                'default_value': (139, 90, 43),  # Brown
                'description': 'Head color'
            },
            
            # Leg Genetics
            'leg_length_modifier': {
                'svg_property': 'length_factor',
                'target_element': 'legs',
                'value_type': 'continuous',
                'control_range': (0.8, 1.2),
                'default_value': 1.0,
                'description': 'Leg length scaling'
            },
            'leg_thickness_modifier': {
                'svg_property': 'stroke_width',
                'target_element': 'legs',
                'value_type': 'continuous',
                'control_range': (0.7, 1.3),
                'default_value': 1.0,
                'description': 'Leg thickness'
            },
            'leg_color': {
                'svg_property': 'stroke',
                'target_element': 'legs',
                'value_type': 'rgb_to_hex',
                'control_range': {'r': (0, 255), 'g': (0, 255), 'b': (0, 255)},
                'default_value': (101, 67, 33),  # Dark brown
                'description': 'Leg color'
            },
            
            # Eye Genetics
            'eye_color': {
                'svg_property': 'fill',
                'target_element': 'eyes',
                'value_type': 'rgb_to_hex',
                'control_range': {'r': (0, 255), 'g': (0, 255), 'b': (0, 255)},
                'default_value': (0, 0, 0),  # Black
                'description': 'Eye color'
            },
            'eye_size_modifier': {
                'svg_property': 'transform',
                'target_element': 'eyes',
                'value_type': 'scale',
                'control_range': (0.8, 1.2),
                'default_value': 1.0,
                'description': 'Eye size scaling'
            }
        }
    
    def map_genetics_to_svg_params(self, visual_genetics: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Convert genetic values to SVG rendering parameters
        Returns a dictionary organized by target elements
        """
        svg_params = {}
        
        for gene_name, gene_value in visual_genetics.items():
            if gene_name in self.gene_svg_mapping:
                mapping = self.gene_svg_mapping[gene_name]
                svg_value = self.convert_gene_to_svg_value(gene_value, mapping)
                
                target_element = mapping['target_element']
                if target_element not in svg_params:
                    svg_params[target_element] = {}
                
                svg_params[target_element][mapping['svg_property']] = svg_value
        
        return svg_params
    
    def convert_gene_to_svg_value(self, gene_value: Union[Tuple, str, float], mapping: Dict[str, Any]) -> Any:
        """
        Convert genetic value to SVG-compatible value
        """
        value_type = mapping['value_type']
        
        if value_type == 'rgb_to_hex':
            return self.rgb_to_hex(gene_value)
        elif value_type == 'discrete':
            return gene_value
        elif value_type == 'continuous':
            return gene_value
        elif value_type == 'scale':
            return f"scale({gene_value})"
        elif value_type == 'pattern_generator':
            return gene_value  # Pattern generator function name
        else:
            return gene_value
    
    def rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """
        Convert RGB tuple to hex color string
        """
        if len(rgb) != 3 or not all(isinstance(c, int) and 0 <= c <= 255 for c in rgb):
            # Return default color if invalid RGB
            return "#228B22"  # Forest green
        
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """
        Convert hex color string to RGB tuple
        """
        try:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except (ValueError, IndexError):
            return (34, 139, 34)  # Default forest green
    
    def get_element_defaults(self) -> Dict[str, Dict[str, Any]]:
        """
        Get default SVG parameters for all elements
        """
        defaults = {}
        
        for gene_name, mapping in self.gene_svg_mapping.items():
            target_element = mapping['target_element']
            svg_property = mapping['svg_property']
            default_value = mapping['default_value']
            
            if target_element not in defaults:
                defaults[target_element] = {}
            
            # Convert default value to SVG format
            if mapping['value_type'] == 'rgb_to_hex':
                defaults[target_element][svg_property] = self.rgb_to_hex(default_value)
            elif mapping['value_type'] == 'scale':
                defaults[target_element][svg_property] = f"scale({default_value})"
            else:
                defaults[target_element][svg_property] = default_value
        
        return defaults
    
    def validate_svg_params(self, svg_params: Dict[str, Dict[str, Any]]) -> Dict[str, bool]:
        """
        Validate SVG parameters against expected ranges and types
        """
        validation_results = {}
        
        for element_name, element_params in svg_params.items():
            for param_name, param_value in element_params.items():
                key = f"{element_name}.{param_name}"
                
                # Find the corresponding gene mapping
                gene_mapping = None
                for gene_name, mapping in self.gene_svg_mapping.items():
                    if (mapping['target_element'] == element_name and 
                        mapping['svg_property'] == param_name):
                        gene_mapping = mapping
                        break
                
                if gene_mapping:
                    validation_results[key] = self.validate_svg_parameter(
                        param_value, gene_mapping
                    )
                else:
                    validation_results[key] = False  # Unknown parameter
        
        return validation_results
    
    def validate_svg_parameter(self, value: Any, mapping: Dict[str, Any]) -> bool:
        """
        Validate individual SVG parameter
        """
        value_type = mapping['value_type']
        
        if value_type == 'rgb_to_hex':
            if isinstance(value, str) and value.startswith('#'):
                try:
                    hex_color = value.lstrip('#')
                    return len(hex_color) == 6 and all(c in '0123456789ABCDEFabcdef' for c in hex_color)
                except:
                    return False
            return False
        elif value_type == 'discrete':
            return value in mapping['control_range']
        elif value_type == 'continuous':
            control_range = mapping['control_range']
            return isinstance(value, (int, float)) and control_range[0] <= value <= control_range[1]
        elif value_type == 'scale':
            if isinstance(value, str) and value.startswith('scale(') and value.endswith(')'):
                try:
                    scale_value = float(value[6:-1])
                    control_range = mapping['control_range']
                    return control_range[0] <= scale_value <= control_range[1]
                except:
                    return False
            return False
        elif value_type == 'pattern_generator':
            return value in mapping['control_range']
        
        return False
    
    def get_gene_control_summary(self) -> Dict[str, Dict[str, str]]:
        """
        Get human-readable summary of gene control
        """
        summary = {}
        
        for gene_name, mapping in self.gene_svg_mapping.items():
            summary[gene_name] = {
                'element': mapping['target_element'],
                'property': mapping['svg_property'],
                'type': mapping['value_type'],
                'description': mapping['description'],
                'default': str(mapping['default_value'])
            }
        
        return summary
    
    def get_element_gene_mapping(self) -> Dict[str, List[str]]:
        """
        Get mapping of SVG elements to controlling genes
        """
        element_mapping = {}
        
        for gene_name, mapping in self.gene_svg_mapping.items():
            element = mapping['target_element']
            if element not in element_mapping:
                element_mapping[element] = []
            element_mapping[element].append(gene_name)
        
        return element_mapping
    
    def get_controlled_elements(self) -> List[str]:
        """
        Get list of all SVG elements that can be controlled genetically
        """
        return list(set(mapping['target_element'] for mapping in self.gene_svg_mapping.values()))
    
    def get_controlled_properties(self, element: str) -> List[str]:
        """
        Get list of SVG properties that can be controlled for a specific element
        """
        properties = []
        for mapping in self.gene_svg_mapping.values():
            if mapping['target_element'] == element:
                properties.append(mapping['svg_property'])
        return properties
    
    def get_gene_for_property(self, element: str, property: str) -> str:
        """
        Get the gene that controls a specific SVG property
        """
        for gene_name, mapping in self.gene_svg_mapping.items():
            if (mapping['target_element'] == element and 
                mapping['svg_property'] == property):
                return gene_name
        return None
    
    def create_svg_style_string(self, svg_params: Dict[str, Dict[str, Any]]) -> str:
        """
        Create CSS style string from SVG parameters
        """
        styles = []
        
        for element_name, element_params in svg_params.items():
            element_styles = []
            for param_name, param_value in element_params.items():
                if param_name == 'fill':
                    element_styles.append(f"fill: {param_value}")
                elif param_name == 'stroke':
                    element_styles.append(f"stroke: {param_value}")
                elif param_name == 'stroke_width':
                    element_styles.append(f"stroke-width: {param_value}")
                elif param_name == 'opacity':
                    element_styles.append(f"opacity: {param_value}")
            
            if element_styles:
                styles.append(f".{element_name} {{ {' ; '.join(element_styles)} ; }}")
        
        return '\n'.join(styles)
    
    def apply_genetic_constraints(self, svg_params: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Apply genetic constraints to SVG parameters
        Ensures values stay within genetically defined ranges
        """
        constrained_params = {}
        
        for element_name, element_params in svg_params.items():
            constrained_params[element_name] = {}
            
            for param_name, param_value in element_params.items():
                # Find the corresponding gene mapping
                gene_mapping = None
                for gene_name, mapping in self.gene_svg_mapping.items():
                    if (mapping['target_element'] == element_name and 
                        mapping['svg_property'] == param_name):
                        gene_mapping = mapping
                        break
                
                if gene_mapping:
                    constrained_value = self.apply_constraint(param_value, gene_mapping)
                    constrained_params[element_name][param_name] = constrained_value
                else:
                    # Keep original value if no mapping found
                    constrained_params[element_name][param_name] = param_value
        
        return constrained_params
    
    def apply_constraint(self, value: Any, mapping: Dict[str, Any]) -> Any:
        """
        Apply genetic constraint to a single parameter value
        """
        value_type = mapping['value_type']
        
        if value_type == 'continuous':
            control_range = mapping['control_range']
            if isinstance(value, (int, float)):
                return max(control_range[0], min(control_range[1], value))
        elif value_type == 'scale':
            if isinstance(value, str) and value.startswith('scale(') and value.endswith(')'):
                try:
                    scale_value = float(value[6:-1])
                    control_range = mapping['control_range']
                    constrained_scale = max(control_range[0], min(control_range[1], scale_value))
                    return f"scale({constrained_scale})"
                except:
                    pass
        elif value_type == 'discrete':
            if value not in mapping['control_range']:
                return mapping['default_value']
        elif value_type == 'rgb_to_hex':
            # For hex colors, validate and fix if needed
            if isinstance(value, str) and value.startswith('#'):
                try:
                    hex_color = value.lstrip('#')
                    if len(hex_color) == 6 and all(c in '0123456789ABCDEFabcdef' for c in hex_color):
                        return value
                except:
                    pass
            # Return default hex color if invalid
            return self.rgb_to_hex(mapping['default_value'])
        
        return value


# Factory function for easy instantiation
def create_genetic_svg_mapper() -> GeneticToSVGMapper:
    """Create a GeneticToSVGMapper instance"""
    return GeneticToSVGMapper()


# Utility functions
def map_genetics_to_svg(genetics: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Map genetics to SVG parameters using default mapper"""
    mapper = GeneticToSVGMapper()
    return mapper.map_genetics_to_svg_params(genetics)


def create_svg_defaults() -> Dict[str, Dict[str, Any]]:
    """Create default SVG parameters for all elements"""
    mapper = GeneticToSVGMapper()
    return mapper.get_element_defaults()
