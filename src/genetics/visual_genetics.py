"""
Visual Genetics System for TurboShells
Main interface for the modular genetics system
"""

from typing import Dict, List, Tuple, Union
from .gene_definitions import GeneDefinitions
from .gene_generator import GeneGenerator
from .inheritance import Inheritance
from .mutation import Mutation


class VisualGenetics:
    """
    Main interface for the visual genetics system.
    Coordinates between gene definitions, generation, inheritance, and mutation.
    Single responsibility: Provide unified interface for genetics operations.
    """

    def __init__(self):
        self.gene_definitions = GeneDefinitions()
        self.gene_generator = GeneGenerator(self.gene_definitions)
        self.inheritance = Inheritance(self.gene_definitions)
        self.mutation = Mutation(self.gene_definitions)

    # --- Legacy Interface Methods (for backward compatibility) ---

    def generate_random_genetics(self) -> Dict[str, Union[Tuple, str, float]]:
        """Generate completely random visual genetics"""
        return self.gene_generator.generate_random_genetics()

    def generate_random_gene_value(self, gene_def: Dict) -> Union[Tuple, str, float]:
        """Generate random value for a specific gene"""
        return self.gene_generator.generate_random_gene_value(gene_def)

    def inherit_genetics(
        self, parent1_genetics: Dict, parent2_genetics: Dict
    ) -> Dict[str, Union[Tuple, str, float]]:
        """Inherit genetics from two parents with mutation"""
        child_genetics = self.inheritance.inherit_genetics(
            parent1_genetics, parent2_genetics
        )
        return self.mutation.mutate_genetics(child_genetics)

    def mutate_gene(
        self, gene_name: str, value: Union[Tuple, str, float]
    ) -> Union[Tuple, str, float]:
        """Apply mutation to a gene value"""
        return self.mutation.mutate_gene(gene_name, value)

    # --- Enhanced Interface Methods ---

    def get_gene_definitions(self) -> GeneDefinitions:
        """Get access to gene definitions"""
        return self.gene_definitions

    def create_offspring(
        self,
        parent1_genetics: Dict,
        parent2_genetics: Dict,
        inheritance_type: str = "standard",
        mutation_intensity: str = "moderate",
    ) -> Dict[str, Union[Tuple, str, float]]:
        """
        Create offspring with specified inheritance and mutation types
        """
        # Choose inheritance method
        if inheritance_type == "standard":
            child_genetics = self.inheritance.inherit_genetics(
                parent1_genetics, parent2_genetics
            )
        elif inheritance_type == "blended":
            blend_genes = ["shell_size_modifier", "head_size_modifier", "leg_length"]
            child_genetics = self.inheritance.inherit_blended(
                parent1_genetics, parent2_genetics, blend_genes
            )
        elif inheritance_type == "color_patterns":
            child_genetics = self.inheritance.inherit_color_patterns(
                parent1_genetics, parent2_genetics
            )
        else:
            child_genetics = self.inheritance.inherit_genetics(
                parent1_genetics, parent2_genetics
            )

        # Apply mutations
        if mutation_intensity == "pattern":
            child_genetics = self.mutation.pattern_mutation(child_genetics)
        else:
            child_genetics = self.mutation.mutate_with_intensity(
                child_genetics, mutation_intensity
            )

        return child_genetics

    def generate_variations(
        self, base_genetics: Dict, count: int = 5, variation_type: str = "mutation"
    ) -> List[Dict[str, Union[Tuple, str, float]]]:
        """
        Generate variations of base genetics
        """
        variations = []

        if variation_type == "mutation":
            for _ in range(count):
                variation = self.mutation.mutate_with_intensity(
                    base_genetics, "moderate"
                )
                variations.append(variation)

        elif variation_type == "color":
            # Generate color variations
            base_color = base_genetics.get("shell_base_color", (34, 139, 34))
            color_variations = self.gene_generator.generate_color_variations(base_color)

            for color in color_variations[:count]:
                variation = base_genetics.copy()
                variation["shell_base_color"] = color
                variations.append(variation)

        elif variation_type == "pattern":
            # Generate pattern variations
            base_pattern = base_genetics.get("shell_pattern_type", "hex")
            pattern_variations = self.gene_generator.generate_pattern_variations(
                base_pattern
            )

            for pattern in pattern_variations[:count]:
                variation = base_genetics.copy()
                variation["shell_pattern_type"] = pattern
                variations.append(variation)

        elif variation_type == "size":
            # Generate size variations
            base_size = base_genetics.get("shell_size_modifier", 1.0)
            size_variations = self.gene_generator.generate_size_variations(base_size)

            for size in size_variations[:count]:
                variation = base_genetics.copy()
                variation["shell_size_modifier"] = size
                variations.append(variation)

        return variations

    def analyze_genetics(self, genetics: Dict) -> Dict[str, Union[str, float, List]]:
        """
        Analyze genetic profile and return insights
        """
        analysis = {
            "total_genes": len(genetics),
            "color_genes": len(self.gene_definitions.get_genes_by_type("rgb")),
            "pattern_genes": len(self.gene_definitions.get_genes_by_type("discrete")),
            "size_genes": len(self.gene_definitions.get_genes_by_type("continuous")),
            "dominant_colors": self._get_dominant_colors(genetics),
            "pattern_profile": self._get_pattern_profile(genetics),
            "size_profile": self._get_size_profile(genetics),
        }

        return analysis

    def _get_dominant_colors(self, genetics: Dict) -> List[str]:
        """Extract dominant color themes from genetics"""
        colors = []
        color_genes = [
            "shell_base_color",
            "head_color",
            "leg_color",
            "eye_color",
            "pattern_color",
        ]

        for gene in color_genes:
            if gene in genetics:
                rgb = genetics[gene]
                # Simple color categorization
                if rgb[0] > 200 and rgb[1] > 200 and rgb[2] > 200:
                    colors.append("light")
                elif rgb[0] < 55 and rgb[1] < 55 and rgb[2] < 55:
                    colors.append("dark")
                elif rgb[0] > rgb[1] and rgb[0] > rgb[2]:
                    colors.append("red")
                elif rgb[1] > rgb[0] and rgb[1] > rgb[2]:
                    colors.append("green")
                elif rgb[2] > rgb[0] and rgb[2] > rgb[1]:
                    colors.append("blue")
                else:
                    colors.append("neutral")

        return colors

    def _get_pattern_profile(self, genetics: Dict) -> Dict[str, str]:
        """Get pattern information from genetics"""
        profile = {}

        pattern_genes = ["shell_pattern_type", "body_pattern_type"]
        for gene in pattern_genes:
            if gene in genetics:
                profile[gene] = str(genetics[gene])

        return profile

    def _get_size_profile(self, genetics: Dict) -> Dict[str, float]:
        """Get size information from genetics"""
        profile = {}

        size_genes = [
            "shell_size_modifier",
            "head_size_modifier",
            "leg_length",
            "eye_size_modifier",
        ]
        for gene in size_genes:
            if gene in genetics:
                profile[gene] = float(genetics[gene])

        return profile

    def validate_genetics(self, genetics: Dict) -> Dict[str, bool]:
        """
        Validate genetics against gene definitions
        """
        validation_results = {}

        for gene_name, value in genetics.items():
            validation_results[gene_name] = self.gene_definitions.validate_gene_value(
                gene_name, value
            )

        return validation_results

    def get_default_genetics(self) -> Dict[str, Union[Tuple, str, float]]:
        """Get default genetic values"""
        return self.gene_definitions.get_default_genetics()

    # --- Legacy property for backward compatibility ---
    @property
    def gene_definitions_dict(self) -> Dict:
        """Legacy access to gene definitions dictionary"""
        return self.gene_definitions.definitions
