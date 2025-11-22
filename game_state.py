import random
from entities import Turtle

# --- DATA ---
TURTLE_NAMES = [
    "Speedy", "Flash", "Tank", "Rocky", "Splash", "Bolt", "Zoom", "Crush",
    "Snap", "Drift", "Turbo", "Nitro", "Apex", "Vortex", "Titan", "Goliath",
    "Dash", "Sprint", "Marathon", "Iron"
]

def generate_random_turtle(level=1):
    """
    Generates a random turtle based on a level budget.
    Level 1 Budget ~ 20-30 points distributed.
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
            
    return Turtle(name, speed, energy, recovery, swim, climb)

def breed_turtles(parent_a, parent_b):
    """
    Breeds two turtles to create a child.
    Stats are averaged + mutation.
    """
    # Name combination (First half of A + Last half of B)
    name_a_part = parent_a.name[:len(parent_a.name)//2]
    name_b_part = parent_b.name[len(parent_b.name)//2:]
    child_name = name_a_part + name_b_part
    
    # Mutation factor: -2 to +2
    def mutate(val):
        return max(1, int(val + random.randint(-2, 2)))
    
    # Stat Inheritance
    child_speed = mutate((parent_a.stats["speed"] + parent_b.stats["speed"]) / 2)
    child_energy = mutate((parent_a.stats["max_energy"] + parent_b.stats["max_energy"]) / 2)
    child_recovery = mutate((parent_a.stats["recovery"] + parent_b.stats["recovery"]) / 2)
    child_swim = mutate((parent_a.stats["swim"] + parent_b.stats["swim"]) / 2)
    child_climb = mutate((parent_a.stats["climb"] + parent_b.stats["climb"]) / 2)
    
    return Turtle(child_name, child_speed, child_energy, child_recovery, child_swim, child_climb)
