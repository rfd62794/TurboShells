"""Core domain helpers: turtle generation, breeding, and pricing.

This module encapsulates high-level game math that operates on
`entities.Turtle` instances (generation, breeding, shop cost).
It must remain UI-agnostic (no PyGame imports).
"""

import random
from .entities import Turtle

# --- DATA ---
TURTLE_NAMES = [
    "Speedy", "Flash", "Tank", "Rocky", "Splash", "Bolt", "Zoom", "Crush",
    "Snap", "Drift", "Turbo", "Nitro", "Apex", "Vortex", "Titan", "Goliath",
    "Dash", "Sprint", "Marathon", "Iron"
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
        player_turtle.stats['speed'] + 
        player_turtle.stats['recovery'] + 
        player_turtle.stats['swim'] + 
        player_turtle.stats['climb'] +
        (player_turtle.stats['max_energy'] // 10)  # Energy: 10 energy = 1 point
    )
    
    # Start with base stats
    speed = 1
    energy = 50
    recovery = 1
    swim = 1
    climb = 1
    
    # Use player's total points as budget (subtract base points since we start with them)
    budget = player_points - 9  # Subtract base points (1+1+1+1+5=9)
    
    # Randomly distribute points with slight bias toward speed
    while budget > 0:
        # 35% chance to boost speed, 65% for other stats (reduced from 45%)
        if random.random() < 0.35:
            speed += 1
            budget -= 1
        else:
            choice = random.randint(1, 4)  # Skip speed (0)
            if choice == 1: # Energy
                energy += 10
                budget -= 1
            elif choice == 2: # Recovery
                recovery += 1
                budget -= 1
            elif choice == 3: # Swim
                swim += 1
                budget -= 1
            elif choice == 4: # Climb
                climb += 1
                budget -= 1
    
    # Calculate opponent's total points for verification
    opponent_points = speed + recovery + swim + climb + (energy // 10)
    
    return Turtle(name, speed, energy, recovery, swim, climb)

def generate_random_turtle(level=1):
    """
    Generates a random turtle based on a level budget.
    Level 1 Budget ~ 20-30 points distributed.
    Now uses the new modular genetics system.
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
        if choice == 0: # Speed
            speed += 1
            budget -= 1
        elif choice == 1: # Energy
            energy += 10
            budget -= 1
        elif choice == 2: # Recovery
            recovery += 1
            budget -= 1
        elif choice == 3: # Swim
            swim += 1
            budget -= 1
        elif choice == 4: # Climb
            climb += 1
            budget -= 1
            
    # Create turtle with new genetics system (will auto-generate random genetics)
    return Turtle(name, speed, energy, recovery, swim, climb)

def breed_turtles(parent_a, parent_b):
    """
    Breeds two turtles to create a child.
    Uses the new modular genetics system for inheritance.
    """
    # Name combination (First half of A + Last half of B)
    name_a_part = parent_a.name[:len(parent_a.name)//2]
    name_b_part = parent_b.name[len(parent_b.name)//2:]
    child_name = name_a_part + name_b_part
    
    # Mutation: small non-negative boost, so children never get worse
    # Base stat is the best (max) of both parents; mutation can only add.
    def mutate(base_val):
        # Small chance of +1 or +2, otherwise no change
        roll = random.random()
        if roll < 0.1:
            delta = 2
        elif roll < 0.3:
            delta = 1
        else:
            delta = 0
        return max(1, int(base_val + delta))
    
    # Stat Inheritance: take the better of each stat from the parents
    base_speed = max(parent_a.stats["speed"], parent_b.stats["speed"])
    base_energy = max(parent_a.stats["max_energy"], parent_b.stats["max_energy"])
    base_recovery = max(parent_a.stats["recovery"], parent_b.stats["recovery"])
    base_swim = max(parent_a.stats["swim"], parent_b.stats["swim"])
    base_climb = max(parent_a.stats["climb"], parent_b.stats["climb"])

    child_speed = mutate(base_speed)
    child_energy = mutate(base_energy)
    child_recovery = mutate(base_recovery)
    child_swim = mutate(base_swim)
    child_climb = mutate(base_climb)
    
    # Create child with inherited genetics
    child = Turtle(child_name, child_speed, child_energy, child_recovery, child_swim, child_climb)
    
    # Use the new genetics inheritance system
    parent1_genetics = parent_a.get_all_genetics()
    parent2_genetics = parent_b.get_all_genetics()
    
    # Add parent IDs to genetics for lineage tracking
    parent1_genetics['turtle_id'] = parent_a.id
    parent2_genetics['turtle_id'] = parent_b.id
    parent1_genetics['generation'] = parent_a.generation
    parent2_genetics['generation'] = parent_b.generation
    
    # Inherit visual genetics using the new system
    child.inherit_from_parents(parent1_genetics, parent2_genetics)
    
    return child
