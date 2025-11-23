"""
Pattern Generation System for TurboShells
Complete pattern generation library with genetic control
"""

import math
import random
from typing import Optional, Dict, Any

try:
    import drawsvg as draw
except ImportError:
    draw = None


class PatternGenerators:
    """
    Complete pattern generation system with genetic control
    Each pattern type is fully controllable by genetic parameters
    """

    def __init__(self):
        self.pattern_cache = {}
        self.max_cache_size = 100

    def generate_pattern(
        self, pattern_type: str, size: int, color: str, density: float, opacity: float
    ) -> Optional[object]:
        """
        Generate pattern based on type and parameters
        Returns drawsvg Pattern object or None if drawsvg not available
        """
        if draw is None:
            return None

        cache_key = f"{pattern_type}_{size}_{color}_{density}_{opacity}"

        if cache_key in self.pattern_cache:
            return self.pattern_cache[cache_key]

        if pattern_type == "stripes":
            pattern = self.generate_stripes(size, color, density, opacity)
        elif pattern_type == "spots":
            pattern = self.generate_spots(size, color, density, opacity)
        elif pattern_type == "spiral":
            pattern = self.generate_spiral(size, color, density, opacity)
        elif pattern_type == "geometric":
            pattern = self.generate_geometric(size, color, density, opacity)
        elif pattern_type == "complex":
            pattern = self.generate_complex(size, color, density, opacity)
        else:
            pattern = None

        if pattern:
            self.cache_pattern(cache_key, pattern)

        return pattern

    def generate_stripes(
        self, size: int, color: str, density: float, opacity: float
    ) -> object:
        """
        Generate radial stripes pattern
        """
        pattern_id = f"stripes_{id(self)}"
        pattern = draw.Pattern(
            pattern_id, 0, 0, size, size, patternUnits="userSpaceOnUse"
        )

        stripe_count = int(density * 12) + 3  # 3-15 stripes
        stripe_width = max(1, size // (stripe_count * 2))

        for i in range(stripe_count):
            angle = (i / stripe_count) * 360

            # Create radial stripe
            stripe = draw.Line(
                size / 2,
                size / 2,
                size / 2 + size * 0.4 * math.cos(math.radians(angle)),
                size / 2 + size * 0.4 * math.sin(math.radians(angle)),
                stroke=color,
                stroke_width=stripe_width,
                opacity=opacity,
            )
            pattern.append(stripe)

        return pattern

    def generate_spots(
        self, size: int, color: str, density: float, opacity: float
    ) -> object:
        """
        Generate random spots pattern
        """
        pattern_id = f"spots_{id(self)}"
        pattern = draw.Pattern(
            pattern_id, 0, 0, size, size, patternUnits="userSpaceOnUse"
        )

        spot_count = int(density * 20) + 5  # 5-25 spots
        min_spot_size = size * 0.02
        max_spot_size = size * 0.08

        # Use seeded random for consistency
        random.seed(hash(f"spots_{size}_{density}"))

        for i in range(spot_count):
            # Random position within pattern bounds
            x = random.uniform(size * 0.1, size * 0.9)
            y = random.uniform(size * 0.1, size * 0.9)
            spot_size = random.uniform(min_spot_size, max_spot_size)

            spot = draw.Circle(x, y, spot_size, fill=color, opacity=opacity)
            pattern.append(spot)

        random.seed()  # Reset random seed
        return pattern

    def generate_spiral(
        self, size: int, color: str, density: float, opacity: float
    ) -> object:
        """
        Generate spiral pattern
        """
        pattern_id = f"spiral_{id(self)}"
        pattern = draw.Pattern(
            pattern_id, 0, 0, size, size, patternUnits="userSpaceOnUse"
        )

        # Generate spiral path
        spiral = draw.Path(
            stroke=color, stroke_width=max(1, size * 0.02), fill="none", opacity=opacity
        )

        # Spiral parameters
        rotations = 3  # Number of rotations
        points_per_rotation = 20
        max_radius = size * 0.4

        points = []
        for i in range(rotations * points_per_rotation):
            angle = (i / points_per_rotation) * (2 * math.pi)
            radius = (i / (rotations * points_per_rotation)) * max_radius

            x = size / 2 + radius * math.cos(angle)
            y = size / 2 + radius * math.sin(angle)
            points.append((x, y))

        # Draw spiral
        if points:
            spiral.M(*points[0])
            for point in points[1:]:
                spiral.L(*point)

        pattern.append(spiral)
        return pattern

    def generate_geometric(
        self, size: int, color: str, density: float, opacity: float
    ) -> object:
        """
        Generate geometric pattern
        """
        pattern_id = f"geometric_{id(self)}"
        pattern = draw.Pattern(
            pattern_id, 0, 0, size, size, patternUnits="userSpaceOnUse"
        )

        # Create geometric shapes based on density
        shape_count = int(density * 8) + 2  # 2-10 shapes
        shape_size = size * 0.1

        for i in range(shape_count):
            # Position shapes in a grid
            row = i // 3
            col = i % 3

            x = size * 0.2 + col * size * 0.3
            y = size * 0.2 + row * size * 0.3

            # Alternate between squares and triangles
            if i % 2 == 0:
                shape = draw.Rect(
                    x - shape_size / 2,
                    y - shape_size / 2,
                    shape_size,
                    shape_size,
                    fill=color,
                    opacity=opacity,
                )
            else:
                shape = draw.Path(fill=color, opacity=opacity)
                shape.M(x, y - shape_size / 2)
                shape.L(x - shape_size / 2, y + shape_size / 2)
                shape.L(x + shape_size / 2, y + shape_size / 2)
                shape.Z()

            pattern.append(shape)

        return pattern

    def generate_complex(
        self, size: int, color: str, density: float, opacity: float
    ) -> object:
        """
        Generate complex pattern combining multiple elements
        """
        pattern_id = f"complex_{id(self)}"
        pattern = draw.Pattern(
            pattern_id, 0, 0, size, size, patternUnits="userSpaceOnUse"
        )

        # Combine multiple pattern types
        # Base layer: radial lines
        line_count = int(density * 8) + 4
        for i in range(line_count):
            angle = (i / line_count) * 360
            x1, y1 = size / 2, size / 2
            x2 = size / 2 + size * 0.4 * math.cos(math.radians(angle))
            y2 = size / 2 + size * 0.4 * math.sin(math.radians(angle))

            line = draw.Line(
                x1, y1, x2, y2, stroke=color, stroke_width=1, opacity=opacity * 0.5
            )
            pattern.append(line)

        # Second layer: small circles
        circle_count = int(density * 6) + 3
        random.seed(hash(f"complex_{size}_{density}"))

        for i in range(circle_count):
            x = random.uniform(size * 0.2, size * 0.8)
            y = random.uniform(size * 0.2, size * 0.8)
            radius = random.uniform(size * 0.01, size * 0.03)

            circle = draw.Circle(x, y, radius, fill=color, opacity=opacity * 0.7)
            pattern.append(circle)

        random.seed()  # Reset random seed
        return pattern

    def generate_body_pattern(
        self, pattern_type: str, size: int, color: str, density: float
    ) -> Optional[object]:
        """
        Generate body-specific patterns
        """
        if draw is None:
            return None

        if pattern_type == "solid":
            return None  # No pattern for solid
        elif pattern_type == "mottled":
            return self.generate_mottled(size, color, density)
        elif pattern_type == "speckled":
            return self.generate_speckled(size, color, density)
        elif pattern_type == "marbled":
            return self.generate_marbled(size, color, density)
        else:
            return None

    def generate_mottled(self, size: int, color: str, density: float) -> object:
        """
        Generate mottled body pattern
        """
        pattern_id = f"mottled_{id(self)}"
        pattern = draw.Pattern(
            pattern_id, 0, 0, size, size, patternUnits="userSpaceOnUse"
        )

        blot_count = int(density * 10) + 5
        random.seed(hash(f"mottled_{size}_{density}"))

        for i in range(blot_count):
            x = random.uniform(size * 0.1, size * 0.9)
            y = random.uniform(size * 0.1, size * 0.9)
            blot_size = random.uniform(size * 0.05, size * 0.15)

            blot = draw.Circle(x, y, blot_size, fill=color, opacity=0.6)
            pattern.append(blot)

        random.seed()
        return pattern

    def generate_speckled(self, size: int, color: str, density: float) -> object:
        """
        Generate speckled body pattern
        """
        pattern_id = f"speckled_{id(self)}"
        pattern = draw.Pattern(
            pattern_id, 0, 0, size, size, patternUnits="userSpaceOnUse"
        )

        speck_count = int(density * 30) + 10
        speck_size = max(1, size * 0.02)
        random.seed(hash(f"speckled_{size}_{density}"))

        for i in range(speck_count):
            x = random.uniform(size * 0.1, size * 0.9)
            y = random.uniform(size * 0.1, size * 0.9)

            speck = draw.Circle(x, y, speck_size, fill=color, opacity=0.8)
            pattern.append(speck)

        random.seed()
        return pattern

    def generate_marbled(self, size: int, color: str, density: float) -> object:
        """
        Generate marbled body pattern
        """
        pattern_id = f"marbled_{id(self)}"
        pattern = draw.Pattern(
            pattern_id, 0, 0, size, size, patternUnits="userSpaceOnUse"
        )

        # Create flowing marble lines
        line_count = int(density * 5) + 3
        random.seed(hash(f"marbled_{size}_{density}"))

        for i in range(line_count):
            # Create flowing curves
            path = draw.Path(
                stroke=color,
                stroke_width=max(1, size * 0.015),
                fill="none",
                opacity=0.7,
            )

            points = []
            for j in range(4):
                x = random.uniform(size * 0.1, size * 0.9)
                y = random.uniform(size * 0.1, size * 0.9)
                points.append((x, y))

            if len(points) >= 2:
                path.M(*points[0])
                for point in points[1:]:
                    path.L(*point)
                pattern.append(path)

        random.seed()
        return pattern

    def cache_pattern(self, cache_key: str, pattern: object) -> None:
        """
        Cache pattern with size management
        """
        if len(self.pattern_cache) >= self.max_cache_size:
            # Remove oldest entry (simple LRU)
            oldest_key = next(iter(self.pattern_cache))
            del self.pattern_cache[oldest_key]

        self.pattern_cache[cache_key] = pattern

    def clear_cache(self) -> None:
        """
        Clear the pattern cache
        """
        self.pattern_cache.clear()

    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics
        """
        return {
            "size": len(self.pattern_cache),
            "max_size": self.max_cache_size,
            "usage_percentage": (len(self.pattern_cache) / self.max_cache_size) * 100,
        }

    def get_available_patterns(self) -> list:
        """
        Get list of available pattern types
        """
        return ["stripes", "spots", "spiral", "geometric", "complex"]

    def get_available_body_patterns(self) -> list:
        """
        Get list of available body pattern types
        """
        return ["solid", "mottled", "speckled", "marbled"]

    def validate_pattern_parameters(
        self, pattern_type: str, size: int, color: str, density: float, opacity: float
    ) -> Dict[str, bool]:
        """
        Validate pattern parameters
        """
        validation_results = {
            "pattern_type": pattern_type in self.get_available_patterns(),
            "size": isinstance(size, int) and size > 0,
            "color": isinstance(color, str) and color.startswith("#"),
            "density": isinstance(density, (int, float)) and 0.0 <= density <= 1.0,
            "opacity": isinstance(opacity, (int, float)) and 0.0 <= opacity <= 1.0,
        }

        return validation_results

    def create_pattern_preview(
        self, pattern_type: str, size: int = 100
    ) -> Optional[object]:
        """
        Create a preview of a pattern with default parameters
        """
        if draw is None:
            return None

        # Default parameters for preview
        default_color = "#FF0000"  # Red for visibility
        default_density = 0.5
        default_opacity = 0.8

        return self.generate_pattern(
            pattern_type, size, default_color, default_density, default_opacity
        )

    def get_pattern_description(self, pattern_type: str) -> str:
        """
        Get human-readable description of pattern type
        """
        descriptions = {
            "stripes": "Radial stripes emanating from center",
            "spots": "Random circular spots distributed across surface",
            "spiral": "Mathematical spiral pattern with multiple rotations",
            "geometric": "Grid-based geometric shapes (squares and triangles)",
            "complex": "Combination of radial lines and circular elements",
            "solid": "No pattern, solid color only",
            "mottled": "Irregular blotches with soft edges",
            "speckled": "Small dots distributed across surface",
            "marbled": "Flowing curved lines mimicking marble texture",
        }

        return descriptions.get(pattern_type, "Unknown pattern type")

    def get_pattern_complexity(self, pattern_type: str) -> int:
        """
        Get complexity rating for pattern type (1-5 scale)
        """
        complexity = {
            "solid": 1,
            "stripes": 2,
            "spots": 2,
            "speckled": 3,
            "mottled": 3,
            "spiral": 4,
            "geometric": 4,
            "marbled": 4,
            "complex": 5,
        }

        return complexity.get(pattern_type, 1)


# Factory function for easy instantiation
def create_pattern_generators() -> PatternGenerators:
    """Create a PatternGenerators instance"""
    return PatternGenerators()


# Utility functions
def generate_shell_pattern(
    pattern_type: str, size: int, color: str, density: float, opacity: float
) -> Optional[object]:
    """Generate shell pattern using default PatternGenerators instance"""
    generators = PatternGenerators()
    return generators.generate_pattern(pattern_type, size, color, density, opacity)


def generate_body_pattern(
    pattern_type: str, size: int, color: str, density: float
) -> Optional[object]:
    """Generate body pattern using default PatternGenerators instance"""
    generators = PatternGenerators()
    return generators.generate_body_pattern(pattern_type, size, color, density)


def get_all_pattern_types() -> Dict[str, list]:
    """Get all available pattern types organized by category"""
    generators = PatternGenerators()
    return {
        "shell": generators.get_available_patterns(),
        "body": generators.get_available_body_patterns(),
    }
