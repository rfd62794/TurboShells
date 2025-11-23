"""
Turtle SVG Generator for TurboShells
Complete SVG turtle generator with full genetic control
"""

import math
from typing import Dict, Any, Optional, Union
from .visual_genetics import VisualGenetics
from .genetic_svg_mapper import GeneticToSVGMapper
from .pattern_generators import PatternGenerators

try:
    import drawsvg as draw
except ImportError:
    draw = None


class TurtleSVGGenerator:
    """
    Complete SVG turtle generator with genetic control
    Every visual aspect is controlled by genetic parameters
    """
    
    def __init__(self):
        self.visual_genetics = VisualGenetics()
        self.mapper = GeneticToSVGMapper()
        self.pattern_generators = PatternGenerators()
        self.default_size = 100
    
    def generate_turtle_svg(self, visual_genetics: Dict[str, Any], size: Optional[int] = None) -> Optional[object]:
        """
        Generate complete turtle SVG from genetic parameters
        Returns drawsvg Drawing object or None if drawsvg not available
        """
        if draw is None:
            return None
            
        if size is None:
            size = self.default_size
        
        # Create SVG drawing
        svg_drawing = draw.Drawing(size * 2, size * 2, origin='center')
        
        # Map genetics to SVG parameters
        svg_params = self.mapper.map_genetics_to_svg_params(visual_genetics)
        
        # Generate turtle components in order (back to front)
        components = [
            ('shadow', self.create_shadow, size),
            ('tail', self.create_tail, size),
            ('legs', self.create_legs, size, svg_params.get('legs', {})),
            ('body', self.create_body, size, svg_params.get('body', {})),
            ('shell', self.create_shell, size, svg_params.get('shell', {})),
            ('head', self.create_head, size, svg_params.get('head', {})),
            ('eyes', self.create_eyes, size, svg_params.get('eyes', {}))
        ]
        
        for component_name, generator_func, *args in components:
            try:
                component = generator_func(*args)
                if component:
                    svg_drawing.append(component)
            except Exception as e:
                print(f"Error generating {component_name}: {e}")
                # Use default component if generation fails
                default_args = [size] if len(args) == 0 else [size, {}]
                component = generator_func(*default_args)
                if component:
                    svg_drawing.append(component)
        
        return svg_drawing
    
    def create_shell(self, shell_params: Dict[str, Any], size: int) -> object:
        """
        Generate turtle shell with genetic control
        """
        if draw is None:
            return None
        
        # Ensure shell_params is a dict
        if not isinstance(shell_params, dict):
            shell_params = {}
            
        # Get shell parameters with defaults
        shell_color = shell_params.get('fill', '#228B22')  # Forest green default
        shell_transform = shell_params.get('transform', 'scale(1.0)')
        
        # Parse scale from transform
        scale_factor = 1.0
        if isinstance(shell_transform, str) and shell_transform.startswith('scale('):
            try:
                scale_factor = float(shell_transform[6:-1])
            except:
                scale_factor = 1.0
        
        # Create shell base
        shell = draw.Ellipse(
            0, 0, 
            size * 0.8 * scale_factor, size * 0.6 * scale_factor,
            fill=shell_color,
            stroke='#1F5F1F',
            stroke_width=2
        )
        
        # Add pattern if specified
        if 'pattern_generator' in shell_params:
            pattern_type = shell_params['pattern_generator']
            pattern_color = shell_params.get('stroke', '#FFFFFF')
            pattern_density = shell_params.get('density_factor', 0.5)
            pattern_opacity = shell_params.get('opacity', 0.8)
            
            pattern = self.pattern_generators.generate_pattern(
                pattern_type, size, pattern_color, pattern_density, pattern_opacity
            )
            
            if pattern:
                shell_pattern = draw.Defs()
                shell_pattern.append(pattern)
                
                patterned_shell = draw.Ellipse(
                    0, 0,
                    size * 0.8 * scale_factor, size * 0.6 * scale_factor,
                    fill=f"url(#{pattern.id})",
                    stroke='#1F5F1F',
                    stroke_width=2
                )
                
                return draw.Group([shell_pattern, patterned_shell])
        
        return shell
    
    def create_body(self, body_params: Dict[str, Any], size: int) -> object:
        """
        Generate turtle body with genetic control
        """
        if draw is None:
            return None
        
        # Ensure body_params is a dict
        if not isinstance(body_params, dict):
            body_params = {}
            
        # Get body parameters with defaults
        body_color = body_params.get('fill', '#6B8E23')  # Olive green default
        
        # Create body ellipse (smaller than shell)
        body = draw.Ellipse(
            0, size * 0.1,
            size * 0.5, size * 0.4,
            fill=body_color,
            stroke='#4A5F23',
            stroke_width=1.5
        )
        
        # Add body pattern if specified
        if 'pattern_generator' in body_params:
            pattern_type = body_params['pattern_generator']
            pattern_color = body_params.get('fill', '#556B2F')
            pattern_density = body_params.get('density_factor', 0.3)
            
            pattern = self.pattern_generators.generate_body_pattern(
                pattern_type, size, pattern_color, pattern_density
            )
            
            if pattern:
                body_pattern = draw.Defs()
                body_pattern.append(pattern)
                
                patterned_body = draw.Ellipse(
                    0, size * 0.1,
                    size * 0.5, size * 0.4,
                    fill=f"url(#{pattern.id})",
                    stroke='#4A5F23',
                    stroke_width=1.5
                )
                
                return draw.Group([body_pattern, patterned_body])
        
        return body
    
    def create_head(self, head_params: Dict[str, Any], size: int) -> object:
        """
        Generate turtle head with genetic control
        """
        if draw is None:
            return None
        
        # Ensure head_params is a dict
        if not isinstance(head_params, dict):
            head_params = {}
            
        # Get head parameters with defaults
        head_color = head_params.get('fill', '#8B5A2B')  # Brown default
        head_transform = head_params.get('transform', 'scale(1.0)')
        
        # Parse scale from transform
        scale_factor = 1.0
        if isinstance(head_transform, str) and head_transform.startswith('scale('):
            try:
                scale_factor = float(head_transform[6:-1])
            except:
                scale_factor = 1.0
        
        # Create head circle
        head = draw.Circle(
            0, -size * 0.7,
            size * 0.2 * scale_factor,
            fill=head_color,
            stroke='#6B3A1B',
            stroke_width=1.5
        )
        
        return head
    
    def create_legs(self, leg_params: Dict[str, Any], size: int) -> object:
        """
        Generate turtle legs with genetic control
        """
        if draw is None:
            return None
        
        # Ensure leg_params is a dict
        if not isinstance(leg_params, dict):
            leg_params = {}
            
        # Get leg parameters with defaults
        leg_color = leg_params.get('stroke', '#654321')  # Dark brown default
        leg_thickness = leg_params.get('stroke_width', 3.0)
        leg_length_factor = leg_params.get('length_factor', 1.0)
        
        legs_group = draw.Group()
        
        # Leg positions (4 legs)
        leg_positions = [
            (-size * 0.4, size * 0.2),   # Front left
            (size * 0.4, size * 0.2),    # Front right
            (-size * 0.3, size * 0.5),   # Back left
            (size * 0.3, size * 0.5)     # Back right
        ]
        
        for i, (x, y) in enumerate(leg_positions):
            # Create leg as curved path
            leg = draw.Path(
                stroke=leg_color,
                stroke_width=leg_thickness,
                fill='none',
                stroke_linecap='round'
            )
            
            # Leg curve from body to ground
            leg_length = size * 0.3 * leg_length_factor
            leg.M(x, y).C(
                x + leg_length * 0.3, y + leg_length * 0.5,
                x + leg_length * 0.2, y + leg_length,
                x, y + leg_length
            )
            
            legs_group.append(leg)
        
        return legs_group
    
    def create_eyes(self, eye_params: Dict[str, Any], size: int) -> object:
        """
        Generate turtle eyes with genetic control
        """
        if draw is None:
            return None
        
        # Ensure eye_params is a dict
        if not isinstance(eye_params, dict):
            eye_params = {}
            
        # Get eye parameters with defaults
        eye_color = eye_params.get('fill', '#000000')  # Black default
        eye_transform = eye_params.get('transform', 'scale(1.0)')
        
        # Parse scale from transform
        scale_factor = 1.0
        if isinstance(eye_transform, str) and eye_transform.startswith('scale('):
            try:
                scale_factor = float(eye_transform[6:-1])
            except:
                scale_factor = 1.0
        
        eyes_group = draw.Group()
        
        # Eye positions
        eye_positions = [
            (-size * 0.08, -size * 0.72),  # Left eye
            (size * 0.08, -size * 0.72)    # Right eye
        ]
        
        for x, y in eye_positions:
            eye = draw.Circle(
                x, y,
                size * 0.03 * scale_factor,
                fill=eye_color
            )
            eyes_group.append(eye)
        
        return eyes_group
    
    def create_tail(self, size: int) -> object:
        """
        Generate turtle tail
        """
        if draw is None:
            return None
            
        tail = draw.Path(
            stroke='#654321',
            stroke_width=4,
            fill='none',
            stroke_linecap='round'
        )
        
        # Tail curve
        tail.M(0, size * 0.5).C(
            size * 0.1, size * 0.6,
            size * 0.15, size * 0.7,
            size * 0.1, size * 0.8
        )
        
        return tail
    
    def create_shadow(self, size: int) -> object:
        """
        Generate turtle shadow
        """
        if draw is None:
            return None
            
        shadow = draw.Ellipse(
            0, size * 0.9,
            size * 0.6, size * 0.2,
            fill='#000000',
            opacity=0.2
        )
        
        return shadow
    
    def generate_random_turtle(self, size: Optional[int] = None) -> Optional[object]:
        """
        Generate a turtle with random genetics
        """
        random_genetics = self.visual_genetics.generate_random_genetics()
        return self.generate_turtle_svg(random_genetics, size)
    
    def generate_turtle_from_parents(self, parent1_genetics: Dict[str, Any], 
                                   parent2_genetics: Dict[str, Any], 
                                   size: Optional[int] = None) -> Optional[object]:
        """
        Generate a turtle from two parents (inheritance)
        """
        child_genetics = self.visual_genetics.inherit_genetics(parent1_genetics, parent2_genetics)
        return self.generate_turtle_svg(child_genetics, size)
    
    def validate_svg_generation(self, visual_genetics: Dict[str, Any]) -> Dict[str, bool]:
        """
        Validate that genetics can be properly converted to SVG
        """
        validation_results = {}
        
        # Validate genetics
        genetics_validation = self.visual_genetics.validate_genetics(visual_genetics)
        validation_results['genetics'] = all(genetics_validation.values())
        
        # Validate SVG parameter mapping
        svg_params = self.mapper.map_genetics_to_svg_params(visual_genetics)
        svg_validation = self.mapper.validate_svg_params(svg_params)
        validation_results['svg_params'] = all(svg_validation.values())
        
        # Validate pattern parameters
        pattern_validation = True
        if 'shell_pattern_type' in visual_genetics:
            pattern_type = visual_genetics['shell_pattern_type']
            density = visual_genetics.get('shell_pattern_density', 0.5)
            opacity = visual_genetics.get('shell_pattern_opacity', 0.8)
            
            pattern_params_valid = self.pattern_generators.validate_pattern_parameters(
                pattern_type, 100, '#FFFFFF', density, opacity
            )
            pattern_validation = all(pattern_params_valid.values())
        
        validation_results['patterns'] = pattern_validation
        
        # Overall validation
        validation_results['overall'] = (
            validation_results['genetics'] and 
            validation_results['svg_params'] and 
            validation_results['patterns']
        )
        
        return validation_results
    
    def get_generation_stats(self, visual_genetics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get statistics about the turtle generation
        """
        stats = {
            'gene_count': len(visual_genetics),
            'pattern_complexity': 0,
            'color_count': 0,
            'size_modifiers': {}
        }
        
        # Count patterns and their complexity
        if 'shell_pattern_type' in visual_genetics:
            pattern_type = visual_genetics['shell_pattern_type']
            stats['pattern_complexity'] = self.pattern_generators.get_pattern_complexity(pattern_type)
        
        if 'body_pattern_type' in visual_genetics:
            pattern_type = visual_genetics['body_pattern_type']
            body_complexity = self.pattern_generators.get_pattern_complexity(pattern_type)
            stats['pattern_complexity'] = max(stats['pattern_complexity'], body_complexity)
        
        # Count unique colors
        colors = set()
        color_genes = ['shell_base_color', 'shell_pattern_color', 'body_base_color', 
                      'body_pattern_color', 'head_color', 'leg_color', 'eye_color']
        
        for gene in color_genes:
            if gene in visual_genetics:
                color = visual_genetics[gene]
                if isinstance(color, tuple) and len(color) == 3:
                    colors.add(color)
        
        stats['color_count'] = len(colors)
        
        # Get size modifiers
        size_genes = ['shell_size_modifier', 'head_size_modifier', 
                     'leg_length_modifier', 'leg_thickness_modifier', 'eye_size_modifier']
        
        for gene in size_genes:
            if gene in visual_genetics:
                stats['size_modifiers'][gene] = visual_genetics[gene]
        
        # Calculate rarity score
        stats['rarity_score'] = self.visual_genetics.get_rarity_score(visual_genetics)
        
        return stats
    
    def create_turtle_preview(self, visual_genetics: Dict[str, Any], 
                           preview_size: int = 50) -> Optional[object]:
        """
        Create a small preview of the turtle
        """
        return self.generate_turtle_svg(visual_genetics, preview_size)
    
    def get_supported_features(self) -> Dict[str, list]:
        """
        Get list of supported features for documentation
        """
        return {
            'shell_patterns': self.pattern_generators.get_available_patterns(),
            'body_patterns': self.pattern_generators.get_available_body_patterns(),
            'genetic_traits': list(self.visual_genetics.gene_definitions.keys()),
            'svg_elements': self.mapper.get_controlled_elements(),
            'color_genes': ['shell_base_color', 'shell_pattern_color', 'body_base_color', 
                          'body_pattern_color', 'head_color', 'leg_color', 'eye_color'],
            'size_genes': ['shell_size_modifier', 'head_size_modifier', 
                         'leg_length_modifier', 'leg_thickness_modifier', 'eye_size_modifier']
        }
    
    def export_svg_string(self, visual_genetics: Dict[str, Any], 
                         size: Optional[int] = None) -> Optional[str]:
        """
        Export SVG as string for saving or transmission
        """
        svg_drawing = self.generate_turtle_svg(visual_genetics, size)
        if svg_drawing:
            return svg_drawing.as_svg()
        return None
    
    def get_default_genetics(self) -> Dict[str, Any]:
        """
        Get default genetics for a standard turtle
        """
        return self.visual_genetics.generate_random_genetics()


# Factory function for easy instantiation
def create_turtle_svg_generator() -> TurtleSVGGenerator:
    """Create a TurtleSVGGenerator instance"""
    return TurtleSVGGenerator()


# Utility functions
def generate_random_turtle_svg(size: Optional[int] = None) -> Optional[object]:
    """Generate random turtle SVG using default generator"""
    generator = TurtleSVGGenerator()
    return generator.generate_random_turtle(size)


def generate_turtle_svg_from_genetics(genetics: Dict[str, Any], 
                                    size: Optional[int] = None) -> Optional[object]:
    """Generate turtle SVG from genetics using default generator"""
    generator = TurtleSVGGenerator()
    return generator.generate_turtle_svg(genetics, size)


def create_turtle_preview_svg(genetics: Dict[str, Any], preview_size: int = 50) -> Optional[str]:
    """Create turtle preview SVG string"""
    generator = TurtleSVGGenerator()
    return generator.export_svg_string(genetics, preview_size)
