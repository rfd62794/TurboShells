"""Core domain helpers: turtle generation, breeding, and pricing.

This module encapsulates high-level game math that operates on
`entities.Turtle` instances (generation, breeding, shop cost).
It must remain UI-agnostic (no PyGame imports).
"""

import random
from .entities import Turtle

# --- DATA ---
TURTLE_NAMES = [
    "Speedy",
    "Flash",
    "Tank",
    "Rocky",
    "Splash",
    "Bolt",
    "Zoom",
    "Crush",
    "Snap",
    "Drift",
    "Turbo",
    "Nitro",
    "Apex",
    "Vortex",
    "Titan",
    "Goliath",
    "Dash",
    "Sprint",
    "Marathon",
    "Iron",
]


def compute_turtle_cost(turtle: Turtle) -> int:
    """Compute a simple cost for a turtle based on its stats.

    Currently: base cost + a small factor times the sum of core stats.
    This is intentionally simple and easy to tune.
    """
    stats = turtle.stats
    # Normalize energy down so it doesn't dominate cost
    normalized_energy = stats["max_energy"] / 10.0
    total = (
        stats["speed"]
        + normalized_energy
        + stats["recovery"]
        + stats["swim"]
        + stats["climb"]
    )
    base_cost = 20
    scale = 2.0
    return int(base_cost + total * scale)


def generate_balanced_opponent(player_turtle):
    """
    Generates a random opponent with equal total stat points to the player's turtle.
    Points are randomly distributed across all stats.
    """
    name = random.choice(TURTLE_NAMES)

    # Calculate player's total stat points (excluding energy which uses different scaling)
    player_points = (
        player_turtle.stats["speed"]
        + player_turtle.stats["recovery"]
        + player_turtle.stats["swim"]
        + player_turtle.stats["climb"]
        + (player_turtle.stats["max_energy"] // 10)  # Energy: 10 energy = 1 point
    )

    print(f"[DEBUG] Player {player_turtle.name} stats: speed={player_turtle.stats['speed']}, energy={player_turtle.stats['max_energy']}, recovery={player_turtle.stats['recovery']}, swim={player_turtle.stats['swim']}, climb={player_turtle.stats['climb']}")
    print(f"[DEBUG] Player total points: {player_points}")

    # Start with base stats
    speed = 1
    energy = 50
    recovery = 1
    swim = 1
    climb = 1

    # Use player's total points as budget (subtract base points since we start with them)
    budget = player_points - 9  # Subtract base points (1+1+1+1+5=9)
    print(f"[DEBUG] Opponent generation budget: {budget}")

    # Randomly distribute points with reduced bias toward speed
    while budget > 0:
        # 15% chance to boost speed (reduced from 34%), 85% for other stats
        if random.random() < 0.15:
            speed += 1
            budget -= 1
        else:
            choice = random.randint(1, 4)  # Skip speed (0)
            if choice == 1:  # Energy
                energy += 10
                budget -= 1
            elif choice == 2:  # Recovery
                recovery += 1
                budget -= 1
            elif choice == 3:  # Swim
                swim += 1
                budget -= 1
            elif choice == 4:  # Climb
                climb += 1
                budget -= 1

    # Calculate opponent's total points for verification
    opponent_points = speed + recovery + swim + climb + (energy // 10)
    
    print(f"[DEBUG] Generated opponent {name}: speed={speed}, energy={energy}, recovery={recovery}, swim={swim}, climb={climb}")
    print(f"[DEBUG] Opponent total points: {opponent_points}")

    return Turtle(name, speed, energy, recovery, swim, climb)


def generate_random_turtle(level=1, use_influenced_genetics=False):
    """
    Generates a random turtle based on a level budget.
    Level 1 Budget ~ 20-30 points distributed.
    Now uses the new modular genetics system.

    Args:
        level: Turtle level (affects stat budget)
        use_influenced_genetics: If True, uses voting-influenced genetics
    """
    name = random.choice(TURTLE_NAMES)

    # Base stats
    speed = 1
    energy = 50
    recovery = 1
    swim = 1
    climb = 1

    # Budget Logic
    # Each level gives roughly 10 points to distribute
    # Energy costs 0.1 per point (so 10 energy = 1 point)
    budget = 15 + (level * 10)

    while budget > 0:
        choice = random.randint(0, 4)
        if choice == 0:  # Speed
            speed += 1
            budget -= 1
        elif choice == 1:  # Energy
            energy += 10
            budget -= 1
        elif choice == 2:  # Recovery
            recovery += 1
            budget -= 1
        elif choice == 3:  # Swim
            swim += 1
            budget -= 1
        elif choice == 4:  # Climb
            climb += 1
            budget -= 1

    # Create turtle with genetics system
    turtle = Turtle(name, speed, energy, recovery, swim, climb)

    # Apply influenced genetics if requested
    if use_influenced_genetics:
        try:
            from core.systems import GeneticPoolManager

            pool_manager = GeneticPoolManager()
            influenced_genetics = pool_manager.generate_influenced_genetics()
            # Apply the influenced genetics to the turtle
            for trait_name, trait_value in influenced_genetics.items():
                turtle.set_genetic_trait(trait_name, trait_value)
        except Exception as e:
            print(f"Warning: Could not apply influenced genetics: {e}")
            # Fall back to random genetics (already generated by Turtle constructor)

    return turtle


def breed_turtles(parent_a, parent_b, use_influenced_genetics=False):
    """
    Breeds two turtles to create a child.
    Uses the new modular genetics system for inheritance.

    Args:
        parent_a: First parent turtle
        parent_b: Second parent turtle
        use_influenced_genetics: If True, applies voting influence to child
    """
    # Name combination (First half of A + Last half of B)
    name_a_part = parent_a.name[: len(parent_a.name) // 2]
    name_b_part = parent_b.name[len(parent_b.name) // 2]
    child_name = name_a_part + name_b_part

    # Mutation: small non-negative boost, so children never get worse
    mutation = random.randint(0, 3)

    # Inherit stats from parents, with mutation
    speed = max(1, (parent_a.speed + parent_b.speed) // 2 + mutation)
    energy = max(50, (parent_a.max_energy + parent_b.max_energy) // 2 + (mutation * 10))
    recovery = max(
        1, (parent_a.stats["recovery"] + parent_b.stats["recovery"]) // 2 + mutation
    )
    swim = max(1, (parent_a.stats["swim"] + parent_b.stats["swim"]) // 2 + mutation)
    climb = max(1, (parent_a.stats["climb"] + parent_b.stats["climb"]) // 2 + mutation)

    # Create child with inheritance
    child = Turtle(child_name, speed, energy, recovery, swim, climb)

    # Apply influenced genetics if requested
    if use_influenced_genetics:
        try:
            from core.systems import GeneticPoolManager

            pool_manager = GeneticPoolManager()
            influenced_genetics = pool_manager.generate_influenced_genetics()
            # Apply the influenced genetics to the child (blend with inherited)
            for trait_name, trait_value in influenced_genetics.items():
                # 30% chance to use influenced value instead of inherited
                if random.random() < 0.3:
                    child.set_genetic_trait(trait_name, trait_value)
        except Exception as e:
            print(f"Warning: Could not apply influenced genetics to child: {e}")
            # Fall back to inherited genetics (already generated by Turtle constructor)

    return child
