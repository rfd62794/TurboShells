"""Core domain: Turtle stats and shared race physics.

This module is the single source of truth for turtle DNA and
movement/energy logic. It must not import or depend on any UI code.
"""

import random
import uuid

# --- SHARED PHYSICS CONSTANTS ---
# These are the "Balanced" values found in your simulation
TERRAIN_DIFFICULTY = 0.8
RECOVERY_RATE = 0.1
RECOVERY_THRESHOLD = 0.5

class Turtle:
    def __init__(self, name, speed, energy, recovery, swim, climb):
        # Identity
        self.id = str(uuid.uuid4())[:8] # Unique ID for tracking
        self.name = name
        self.age = 0
        self.is_active = True # True = Roster, False = Retired
        
        # Stats (The DNA)
        self.stats = {
            "speed": speed,
            "max_energy": energy,
            "recovery": recovery,
            "swim": swim,
            "climb": climb
        }
        
        # Dynamic Race State (Reset before every race)
        self.current_energy = energy
        self.race_distance = 0
        self.is_resting = False
        self.finished = False
        self.rank = None
        
        # Race History (new feature)
        self.race_history = []
        self.total_races = 0
        self.total_earnings = 0
        
        # Visual Genetics (Foundation for future shell styles/colors)
        self.visual_genetics = {
            # Shell color genes (RGB values 0-255)
            "shell_base_color": [random.randint(50, 200), random.randint(50, 150), random.randint(50, 100)],
            "shell_pattern_color": [random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)],
            "shell_accent_color": [random.randint(150, 255), random.randint(150, 255), random.randint(150, 255)],
            
            # Pattern genes (0-10 scale)
            "shell_pattern_type": random.randint(0, 5),  # 0=plain, 1=stripes, 2=spots, 3=spiral, 4=geometric, 5=complex
            "shell_pattern_density": random.randint(1, 10),
            "shell_pattern_size": random.randint(1, 10),
            
            # Body genes
            "body_base_color": [random.randint(100, 200), random.randint(150, 200), random.randint(50, 150)],
            "body_pattern_type": random.randint(0, 3),  # 0=plain, 1=mottled, 2=gradient, 3=two-tone
            
            # Physical traits (affect future SVG generation)
            "shell_size_factor": random.uniform(0.8, 1.2),  # Size variation
            "shell_curvature": random.uniform(0.8, 1.2),  # Shell shape
            "head_size_factor": random.uniform(0.9, 1.1),
            "limb_length_factor": random.uniform(0.9, 1.1),
        }
        
        # Lineage tracking (for inheritance system)
        self.parent_ids = []  # Will store parent IDs when breeding is implemented
        self.generation = 0  # 0 = wild turtle, 1+ = bred turtles

    def reset_for_race(self):
        """Call this before a race starts."""
        self.current_energy = self.stats["max_energy"]
        self.race_distance = 0
        self.is_resting = False
        self.finished = False
        self.rank = None

    def update_physics(self, terrain_type):
        """
        The Master Physics Logic.
        Returns: distance_moved (float)
        Used by BOTH the Simulation and the Visual Game.
        """
        if self.finished:
            return 0

        # 1. RECOVERY LOGIC
        if self.is_resting:
            # Recover 10% of recovery stat per tick
            self.current_energy += (self.stats["recovery"] * RECOVERY_RATE)
            
            # Check if ready to run again
            if self.current_energy >= (self.stats["max_energy"] * RECOVERY_THRESHOLD):
                self.is_resting = False
            return 0

        # 2. MOVEMENT LOGIC
        move_speed = self.stats["speed"]
        
        # Apply Terrain Modifiers
        if terrain_type == "water":
            move_speed *= (self.stats["swim"] / 10.0)
        elif terrain_type == "rock":
            move_speed *= (self.stats["climb"] / 10.0)
        
        # 3. ENERGY DRAIN LOGIC
        drain = 0.5 * TERRAIN_DIFFICULTY
        self.current_energy -= drain
        
        # Check for Exhaustion
        if self.current_energy <= 0:
            self.current_energy = 0
            self.is_resting = True
            
        return move_speed

    def train(self, stat_name):
        """
        Training Logic: Costs Time (Age), Gains Stats.
        Primary stat always improves, other stats have small chance to improve.
        Does NOT cost Energy.
        """
        import random
        
        self.age += 1
        # Primary stat always improves
        self.stats[stat_name] += 1
        
        # Small chance (20%) to improve each other stat
        other_stats = [s for s in self.stats.keys() if s != stat_name]
        for stat in other_stats:
            if random.random() < 0.2:  # 20% chance
                self.stats[stat] += 1
    
    def add_race_result(self, position, earnings, race_number=None):
        """
        Record race result in history
        """
        if race_number is None:
            race_number = self.total_races + 1
        
        result = {
            'number': race_number,
            'position': position,
            'earnings': earnings,
            'age_at_race': self.age
        }
        
        self.race_history.append(result)
        self.total_races += 1
        self.total_earnings += earnings
        
        # Keep only last 20 races to prevent memory issues
        if len(self.race_history) > 20:
            self.race_history = self.race_history[-20:]
    
    @property
    def speed(self):
        return self.stats["speed"]
    
    @property
    def max_energy(self):
        return self.stats["max_energy"]
    
    @property
    def recovery(self):
        return self.stats["recovery"]
    
    @property
    def swim(self):
        return self.stats["swim"]
    
    @property
    def climb(self):
        return self.stats["climb"]
        
    def __repr__(self):
        return f"<{self.name} (Spd:{self.stats['speed']})>"
