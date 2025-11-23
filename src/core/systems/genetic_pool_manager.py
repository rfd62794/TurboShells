"""
Genetic Pool Manager for TurboShells
Complete genetic pool system for player vote impact on future turtle generations
"""

import random
import math
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Import genetics with fallback
try:
    from genetics import VisualGenetics
except ImportError:
    try:
        from src.genetics import VisualGenetics
    except ImportError:
        VisualGenetics = None


class GeneticPool:
    """
    Individual genetic pool for a specific trait
    Tracks weight, target values, and distribution patterns
    """

    def __init__(self, gene_name: str, gene_type: str, default_value: Any):
        self.gene_name = gene_name
        self.gene_type = gene_type
        self.default_value = default_value
        self.weight = 0.5  # Influence strength (0.0 to 1.0)
        self.influence_count = 0
        self.last_influence = None

        # Type-specific data
        if gene_type == "rgb":
            self.target_rgb = {"r": 128, "g": 128, "b": 128}
        elif gene_type == "discrete":
            self.distribution = {}
            self._initialize_discrete_distribution(default_value)
        elif gene_type == "continuous":
            self.target_value = 0.5
            self.value_range = (0.0, 1.0)

    def _initialize_discrete_distribution(self, default_value: str):
        """Initialize discrete value distribution"""
        # Common discrete values and their initial probabilities
        common_values = {
            "shell_pattern_type": [
                "stripes",
                "spots",
                "spiral",
                "geometric",
                "complex",
            ],
            "body_pattern_type": ["solid", "mottled", "speckled", "marbled"],
        }

        if self.gene_name in common_values:
            values = common_values[self.gene_name]
            self.distribution = {value: 1.0 / len(values) for value in values}
        else:
            self.distribution = {default_value: 1.0}

    def apply_influence(self, value: Any, influence_strength: float) -> float:
        """Apply influence to this genetic pool"""
        self.influence_count += 1
        self.last_influence = datetime.now()

        if self.gene_type == "rgb":
            return self._apply_rgb_influence(value, influence_strength)
        elif self.gene_type == "discrete":
            return self._apply_discrete_influence(value, influence_strength)
        elif self.gene_type == "continuous":
            return self._apply_continuous_influence(value, influence_strength)
        else:
            return influence_strength

    def _apply_rgb_influence(
        self, rgb_value: Tuple[int, int, int], influence_strength: float
    ) -> float:
        """Apply influence to RGB genetic pool"""
        # Update target RGB values
        for i, component in enumerate(["r", "g", "b"]):
            current_value = self.target_rgb[component]
            target_value = rgb_value[i]

            # Move target value toward rated color
            new_value = (current_value * 0.9) + (
                target_value * 0.1 * influence_strength
            )
            self.target_rgb[component] = int(new_value)

        # Update weight
        self.weight = (self.weight * 0.9) + (influence_strength * 0.1)

        return influence_strength

    def _apply_discrete_influence(
        self, discrete_value: str, influence_strength: float
    ) -> float:
        """Apply influence to discrete genetic pool"""
        if discrete_value in self.distribution:
            # Boost the rated value
            boost = influence_strength * 0.1
            current_prob = self.distribution[discrete_value]
            new_prob = min(1.0, current_prob + boost)
            self.distribution[discrete_value] = new_prob

            # Normalize distribution
            total = sum(self.distribution.values())
            for value in self.distribution:
                self.distribution[value] /= total

        # Update weight
        self.weight = (self.weight * 0.9) + (influence_strength * 0.1)

        return influence_strength

    def _apply_continuous_influence(
        self, continuous_value: float, influence_strength: float
    ) -> float:
        """Apply influence to continuous genetic pool"""
        # Move target value toward rated value
        current_target = self.target_value
        new_target = (current_target * 0.9) + (
            continuous_value * 0.1 * influence_strength
        )
        self.target_value = new_target

        # Update weight
        self.weight = (self.weight * 0.9) + (influence_strength * 0.1)

        return influence_strength

    def generate_influenced_value(self, visual_genetics: VisualGenetics) -> Any:
        """Generate value influenced by this genetic pool"""
        if random.random() < self.weight:
            # Use pool-influenced value
            if self.gene_type == "rgb":
                return self._generate_rgb_value()
            elif self.gene_type == "discrete":
                return self._generate_discrete_value()
            elif self.gene_type == "continuous":
                return self._generate_continuous_value(visual_genetics)

        # Use random value
        gene_def = visual_genetics.gene_definitions.get_gene_definition(self.gene_name)
        if gene_def is None:
            gene_def = {}
        return visual_genetics.generate_random_gene_value(gene_def)

    def _generate_rgb_value(self) -> Tuple[int, int, int]:
        """Generate RGB value influenced by pool"""
        r = int(self.target_rgb["r"] + random.uniform(-30, 30))
        g = int(self.target_rgb["g"] + random.uniform(-30, 30))
        b = int(self.target_rgb["b"] + random.uniform(-30, 30))

        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

    def _generate_discrete_value(self) -> str:
        """Generate discrete value influenced by pool"""
        if not self.distribution:
            return self.default_value

        values = list(self.distribution.keys())
        weights = list(self.distribution.values())
        return random.choices(values, weights=weights)[0]

    def _generate_continuous_value(self, visual_genetics: VisualGenetics) -> float:
        """Generate continuous value influenced by pool"""
        gene_def = visual_genetics.gene_definitions.get_gene_definition(self.gene_name)
        if gene_def is None:
            return 0.5
        value_range = gene_def.get("range", (0.0, 1.0))

        # Use target value with variation
        target = self.target_value
        variation = target * 0.2  # 20% variation
        new_value = target + random.uniform(-variation, variation)

        return max(value_range[0], min(value_range[1], new_value))

    def get_pool_status(self) -> Dict[str, Any]:
        """Get status of this genetic pool"""
        status = {
            "gene_name": self.gene_name,
            "gene_type": self.gene_type,
            "weight": self.weight,
            "influence_count": self.influence_count,
            "last_influence": (
                self.last_influence.isoformat() if self.last_influence else None
            ),
        }

        if self.gene_type == "rgb":
            status["target_rgb"] = self.target_rgb
        elif self.gene_type == "discrete":
            status["distribution"] = self.distribution
        elif self.gene_type == "continuous":
            status["target_value"] = self.target_value

        return status


class GeneticPoolManager:
    """
    Complete genetic pool management system
    Handles player vote impact and genetic evolution
    """

    def __init__(self):
        self.visual_genetics = VisualGenetics()
        self.genetic_pools = self._initialize_genetic_pools()
        self.influence_history = []
        self.total_influences = 0

        # System configuration
        self.max_influence_history = 1000
        self.decay_rate = 0.99  # Weight decay per day
        self.min_weight = 0.1
        self.max_weight = 1.0

    def _initialize_genetic_pools(self) -> Dict[str, GeneticPool]:
        """Initialize genetic pools for all genes"""
        pools = {}

        for (
            gene_name,
            gene_def,
        ) in self.visual_genetics.gene_definitions.definitions.items():
            gene_type = gene_def["type"]
            default_value = gene_def["default"]

            pools[gene_name] = GeneticPool(gene_name, gene_type, default_value)

        return pools

    def apply_ratings_to_pool(
        self, design_genetics: Dict[str, Any], ratings: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Apply player ratings to genetic pool
        Returns impact summary
        """
        impact_summary = {
            "design_genetics": design_genetics,
            "ratings": ratings,
            "timestamp": datetime.now(),
            "trait_changes": [],
            "overall_impact": 0.0,
        }

        # Process each rating category
        for category, rating in ratings.items():
            if category == "overall":
                impact = self._apply_overall_impact(
                    design_genetics, rating, impact_summary
                )
            else:
                impact = self._apply_category_impact(
                    design_genetics, category, rating, impact_summary
                )

            impact_summary["overall_impact"] += impact

        # Store influence history
        self.influence_history.append(impact_summary)
        self.total_influences += 1

        # Trim history if necessary
        if len(self.influence_history) > self.max_influence_history:
            self.influence_history.pop(0)

        return impact_summary

    def _apply_overall_impact(
        self, genetics: Dict[str, Any], rating: float, impact_summary: Dict[str, Any]
    ) -> float:
        """Apply overall rating to all genetic traits"""
        influence_strength = rating / 5.0  # Normalize to 0-1
        base_influence = influence_strength * 0.1  # 10% max influence

        total_impact = 0.0

        for trait_name, trait_value in genetics.items():
            if trait_name in self.genetic_pools:
                pool = self.genetic_pools[trait_name]
                trait_influence = self._calculate_trait_influence(
                    trait_name, trait_value, base_influence
                )

                # Apply influence to pool
                impact = pool.apply_influence(trait_value, trait_influence)
                total_impact += impact

                # Track change
                impact_summary["trait_changes"].append(
                    {
                        "trait": trait_name,
                        "category": "overall",
                        "old_weight": pool.weight - (trait_influence * 0.1),
                        "new_weight": pool.weight,
                        "change": trait_influence * 0.1,
                        "rating": rating,
                    }
                )

        return total_impact / len(genetics) if genetics else 0.0

    def _apply_category_impact(
        self,
        genetics: Dict[str, Any],
        category: str,
        rating: float,
        impact_summary: Dict[str, Any],
    ) -> float:
        """Apply specific category rating to relevant traits"""
        category_traits = self._get_traits_for_category(category)
        influence_strength = rating / 5.0
        category_influence = influence_strength * 0.15  # 15% max influence

        total_impact = 0.0

        for trait_name in category_traits:
            if trait_name in genetics and trait_name in self.genetic_pools:
                trait_value = genetics[trait_name]
                pool = self.genetic_pools[trait_name]
                trait_influence = self._calculate_trait_influence(
                    trait_name, trait_value, category_influence
                )

                # Apply influence to pool
                impact = pool.apply_influence(trait_value, trait_influence)
                total_impact += impact

                # Track change
                impact_summary["trait_changes"].append(
                    {
                        "trait": trait_name,
                        "category": category,
                        "old_weight": pool.weight - (trait_influence * 0.15),
                        "new_weight": pool.weight,
                        "change": trait_influence * 0.15,
                        "rating": rating,
                    }
                )

        return total_impact / len(category_traits) if category_traits else 0.0

    def _get_traits_for_category(self, category: str) -> List[str]:
        """Map rating categories to genetic traits"""
        category_mapping = {
            "shell_appearance": [
                "shell_base_color",
                "shell_pattern_type",
                "shell_pattern_color",
                "shell_pattern_density",
                "shell_size_modifier",
            ],
            "color_harmony": [
                "shell_base_color",
                "shell_pattern_color",
                "body_base_color",
            ],
            "pattern_quality": [
                "shell_pattern_type",
                "shell_pattern_density",
                "body_pattern_type",
            ],
            "proportions": [
                "shell_size_modifier",
                "head_size_modifier",
                "leg_length_modifier",
            ],
        }
        return category_mapping.get(category, [])

    def _calculate_trait_influence(
        self, trait_name: str, trait_value: Any, influence_strength: float
    ) -> float:
        """Calculate how a specific trait value influences the genetic pool"""
        gene_def = self.visual_genetics.gene_definitions.get_gene_definition(trait_name)
        gene_type = gene_def.get("type", "continuous")

        if gene_type == "discrete":
            # Discrete values (patterns, types)
            return self._calculate_discrete_influence(
                trait_name, trait_value, influence_strength
            )
        elif gene_type == "rgb":
            # RGB color values
            return self._calculate_color_influence(
                trait_name, trait_value, influence_strength
            )
        elif gene_type == "continuous":
            # Continuous values
            return self._calculate_continuous_influence(
                trait_name, trait_value, influence_strength
            )
        else:
            return influence_strength

    def _calculate_discrete_influence(
        self, trait_name: str, discrete_value: str, influence_strength: float
    ) -> float:
        """Calculate influence for discrete genetic values"""
        pool = self.genetic_pools.get(trait_name)
        if not pool or pool.gene_type != "discrete":
            return influence_strength

        # Check if this is a rare or common value
        distribution = pool.distribution
        current_prob = distribution.get(discrete_value, 0.0)

        # Higher influence for rare values being rated highly
        rarity_factor = 1.0 - current_prob  # Higher for rarer values
        return influence_strength * (1.0 + rarity_factor * 0.5)

    def _calculate_color_influence(
        self,
        trait_name: str,
        rgb_color: Tuple[int, int, int],
        influence_strength: float,
    ) -> float:
        """Calculate influence for RGB color values"""
        pool = self.genetic_pools.get(trait_name)
        if not pool or pool.gene_type != "rgb":
            return influence_strength

        # Calculate color distance from target
        target_rgb = pool.target_rgb
        color_distance = sum(
            abs(rgb_color[i] - target_rgb[component])
            for i, component in enumerate(["r", "g", "b"])
        )
        max_distance = 255 * 3  # Maximum possible distance

        # Higher influence for colors far from current target
        distance_factor = color_distance / max_distance
        return influence_strength * (1.0 + distance_factor * 0.3)

    def _calculate_continuous_influence(
        self, trait_name: str, continuous_value: float, influence_strength: float
    ) -> float:
        """Calculate influence for continuous genetic values"""
        pool = self.genetic_pools.get(trait_name)
        if not pool or pool.gene_type != "continuous":
            return influence_strength

        # Calculate distance from target
        target_value = pool.target_value
        value_range = pool.value_range
        max_distance = value_range[1] - value_range[0]

        if max_distance > 0:
            distance_factor = abs(continuous_value - target_value) / max_distance
            return influence_strength * (1.0 + distance_factor * 0.3)

        return influence_strength

    def generate_influenced_genetics(self) -> Dict[str, Any]:
        """Generate genetics influenced by the current pool"""
        influenced_genetics = {}

        for (
            gene_name,
            gene_def,
        ) in self.visual_genetics.gene_definitions.definitions.items():
            if gene_name in self.genetic_pools:
                pool = self.genetic_pools[gene_name]
                influenced_value = pool.generate_influenced_value(self.visual_genetics)
                influenced_genetics[gene_name] = influenced_value
            else:
                # Use random value for genes not in pool
                influenced_genetics[gene_name] = (
                    self.visual_genetics.generate_random_gene_value(gene_def)
                )

        return influenced_genetics

    def get_genetic_pool_status(self) -> Dict[str, Any]:
        """Get current genetic pool status"""
        return {
            "pool_weights": {
                name: pool.get_pool_status()
                for name, pool in self.genetic_pools.items()
            },
            "influence_count": self.total_influences,
            "last_influence": (
                self.influence_history[-1] if self.influence_history else None
            ),
            "average_weight": self._calculate_average_weight(),
            "most_influenced_traits": self._get_most_influenced_traits(),
            "pool_diversity": self._calculate_pool_diversity(),
        }

    def _calculate_average_weight(self) -> float:
        """Calculate average weight across all pools"""
        if not self.genetic_pools:
            return 0.0

        total_weight = sum(pool.weight for pool in self.genetic_pools.values())
        return total_weight / len(self.genetic_pools)

    def _get_most_influenced_traits(self, count: int = 5) -> List[Tuple[str, float]]:
        """Get most influenced traits"""
        trait_weights = [
            (name, pool.weight) for name, pool in self.genetic_pools.items()
        ]
        trait_weights.sort(key=lambda x: x[1], reverse=True)
        return trait_weights[:count]

    def _calculate_pool_diversity(self) -> float:
        """Calculate diversity measure of genetic pools"""
        diversity_scores = []

        for pool in self.genetic_pools.values():
            if pool.gene_type == "discrete" and pool.distribution:
                # Use entropy as diversity measure
                probs = list(pool.distribution.values())
                entropy = -sum(p * math.log2(p) for p in probs if p > 0)
                max_entropy = math.log2(len(pool.distribution))
                diversity_scores.append(
                    entropy / max_entropy if max_entropy > 0 else 0.0
                )
            elif pool.gene_type == "continuous":
                # Use weight as inverse diversity measure
                diversity_scores.append(1.0 - pool.weight)
            else:
                diversity_scores.append(pool.weight)

        return (
            sum(diversity_scores) / len(diversity_scores) if diversity_scores else 0.0
        )

    def apply_daily_decay(self) -> int:
        """Apply daily decay to pool weights"""
        decayed_count = 0

        for pool in self.genetic_pools.values():
            old_weight = pool.weight
            pool.weight = max(self.min_weight, pool.weight * self.decay_rate)

            if pool.weight != old_weight:
                decayed_count += 1

        return decayed_count

    def reset_genetic_pools(self) -> None:
        """Reset all genetic pools to default state"""
        self.genetic_pools = self._initialize_genetic_pools()
        self.influence_history.clear()
        self.total_influences = 0

    def export_pool_data(self) -> Dict[str, Any]:
        """Export genetic pool data for backup"""
        return {
            "genetic_pools": {
                name: pool.get_pool_status()
                for name, pool in self.genetic_pools.items()
            },
            "influence_history": [
                {
                    "design_genetics": record["design_genetics"],
                    "ratings": record["ratings"],
                    "timestamp": record["timestamp"].isoformat(),
                    "overall_impact": record["overall_impact"],
                }
                for record in self.influence_history
            ],
            "total_influences": self.total_influences,
            "system_config": {
                "max_influence_history": self.max_influence_history,
                "decay_rate": self.decay_rate,
                "min_weight": self.min_weight,
                "max_weight": self.max_weight,
            },
        }

    def import_pool_data(self, data: Dict[str, Any]) -> bool:
        """Import genetic pool data from backup"""
        try:
            # Import genetic pools
            for pool_name, pool_data in data.get("genetic_pools", {}).items():
                if pool_name in self.genetic_pools:
                    pool = self.genetic_pools[pool_name]
                    pool.weight = pool_data.get("weight", 0.5)
                    pool.influence_count = pool_data.get("influence_count", 0)

                    if pool_data.get("last_influence"):
                        pool.last_influence = datetime.fromisoformat(
                            pool_data["last_influence"]
                        )

                    # Type-specific data
                    if pool.gene_type == "rgb":
                        pool.target_rgb = pool_data.get(
                            "target_rgb", {"r": 128, "g": 128, "b": 128}
                        )
                    elif pool.gene_type == "discrete":
                        pool.distribution = pool_data.get("distribution", {})
                    elif pool.gene_type == "continuous":
                        pool.target_value = pool_data.get("target_value", 0.5)

            # Import influence history
            self.influence_history = []
            for record in data.get("influence_history", []):
                record["timestamp"] = datetime.fromisoformat(record["timestamp"])
                self.influence_history.append(record)

            # Import system config
            config = data.get("system_config", {})
            self.max_influence_history = config.get("max_influence_history", 1000)
            self.decay_rate = config.get("decay_rate", 0.99)
            self.min_weight = config.get("min_weight", 0.1)
            self.max_weight = config.get("max_weight", 1.0)

            self.total_influences = data.get("total_influences", 0)

            return True

        except Exception as e:
            print(f"Error importing pool data: {e}")
            return False

    def get_influence_statistics(self) -> Dict[str, Any]:
        """Get detailed influence statistics"""
        if not self.influence_history:
            return {}

        # Calculate statistics
        overall_ratings = [
            record["ratings"].get("overall", 3.0)
            for record in self.influence_history
            if "overall" in record["ratings"]
        ]
        category_impacts = {}

        for record in self.influence_history:
            for change in record.get("trait_changes", []):
                category = change["category"]
                if category not in category_impacts:
                    category_impacts[category] = []
                category_impacts[category].append(abs(change["change"]))

        return {
            "total_influences": len(self.influence_history),
            "average_overall_rating": (
                sum(overall_ratings) / len(overall_ratings) if overall_ratings else 0.0
            ),
            "average_impact_per_vote": sum(
                record.get("overall_impact", 0.0) for record in self.influence_history
            )
            / len(self.influence_history),
            "category_impacts": {
                category: sum(impacts) / len(impacts)
                for category, impacts in category_impacts.items()
                if impacts
            },
            "most_active_categories": sorted(
                [
                    (category, len(impacts))
                    for category, impacts in category_impacts.items()
                ],
                key=lambda x: x[1],
                reverse=True,
            ),
        }


# Factory function for easy instantiation
def create_genetic_pool_manager() -> GeneticPoolManager:
    """Create a GeneticPoolManager instance"""
    return GeneticPoolManager()


# Utility functions
def apply_player_ratings(
    design_genetics: Dict[str, Any], ratings: Dict[str, float]
) -> Dict[str, Any]:
    """Apply player ratings using default genetic pool manager"""
    manager = GeneticPoolManager()
    return manager.apply_ratings_to_pool(design_genetics, ratings)


def generate_influenced_turtle() -> Dict[str, Any]:
    """Generate turtle genetics influenced by player voting"""
    manager = GeneticPoolManager()
    return manager.generate_influenced_genetics()


def get_genetic_pool_status() -> Dict[str, Any]:
    """Get genetic pool status using default manager"""
    manager = GeneticPoolManager()
    return manager.get_genetic_pool_status()
