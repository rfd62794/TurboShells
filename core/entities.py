"""Core domain: Turtle stats and shared race physics.

This module is the single source of truth for turtle DNA and
movement/energy logic. It must not import or depend on any UI code.
"""

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
        Training Logic: Costs Time (Age), Gains Stat.
        Does NOT cost Energy.
        """
        self.age += 1
        self.stats[stat_name] += 1
        return True

    def __repr__(self):
        return f"<{self.name} (Spd:{self.stats['speed']})>"