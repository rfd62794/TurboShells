"""Core domain: Turtle stats and shared race physics.

This module is the single source of truth for turtle DNA and
movement/energy logic. It must not import or depend on any UI code.
"""

import random
import uuid

# Import the new modular genetics system
try:
    from genetics import VisualGenetics
except ImportError:
    try:
        from src.genetics import VisualGenetics
    except ImportError:
        VisualGenetics = None

# --- SHARED PHYSICS CONSTANTS ---
# These are the "Balanced" values found in your simulation
TERRAIN_DIFFICULTY = 0.8
RECOVERY_RATE = 0.1
RECOVERY_THRESHOLD = 0.5


class Turtle:
    def __init__(self, name, speed, energy, recovery, swim, climb, stamina=0, luck=0, genetics=None):
        # Identity
        self.id = str(uuid.uuid4())[:8]  # Unique ID for tracking
        self.name = name
        self.age = 0
        self.is_active = True  # True = Roster, False = Retired

        # Stats (The DNA)
        self.stats = {
            "speed": speed,
            "max_energy": energy,
            "recovery": recovery,
            "swim": swim,
            "climb": climb,
            "stamina": stamina,
            "luck": luck,
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

        # Visual Genetics - Use new modular system
        if VisualGenetics:
            self.genetics_system = VisualGenetics()
            # Use provided genetics or generate random ones
            if genetics is not None:
                self.visual_genetics = genetics.copy()
            else:
                self.visual_genetics = self.genetics_system.generate_random_genetics()
        else:
            self.genetics_system = None
            self.visual_genetics = genetics.copy() if genetics else {}

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

    def update_physics(self, terrain):
        """
        The Master Physics Logic.
        Returns: distance_moved (float)
        Used by BOTH the Simulation and the Visual Game.
        
        Args:
            terrain: Terrain dict with 'type', 'speed_modifier', 'energy_drain', 'color'
        """
        if self.finished:
            return 0

        # 1. RECOVERY LOGIC
        if self.is_resting:
            # Recover 10% of recovery stat per tick, boosted by stamina
            stamina_bonus = self.stats["stamina"] / 20.0  # Stamina adds 5% recovery per point
            recovery_rate = RECOVERY_RATE * (1 + stamina_bonus)
            self.current_energy += self.stats["recovery"] * recovery_rate

            # Check if ready to run again
            if self.current_energy >= (self.stats["max_energy"] * RECOVERY_THRESHOLD):
                self.is_resting = False
            return 0

        # 2. MOVEMENT LOGIC
        move_speed = self.stats["speed"]
        
        # Get terrain type and modifiers
        terrain_type = terrain.get('type', 'normal') if isinstance(terrain, dict) else terrain
        speed_modifier = terrain.get('speed_modifier', 1.0) if isinstance(terrain, dict) else 1.0
        energy_drain = terrain.get('energy_drain', 1.0) if isinstance(terrain, dict) else 1.0

        # Apply Terrain Modifiers
        if terrain_type == "water":
            # Swimming bonus
            swim_bonus = self.stats["swim"] / 10.0
            move_speed *= swim_bonus * speed_modifier
        elif terrain_type == "rocks":
            # Climbing bonus
            climb_bonus = self.stats["climb"] / 10.0
            move_speed *= climb_bonus * speed_modifier
        elif terrain_type == "sand":
            # Sand affects speed more, recovery helps
            recovery_bonus = self.stats["recovery"] / 15.0
            move_speed *= (1.0 + recovery_bonus) * speed_modifier
        elif terrain_type == "mud":
            # Mud is very difficult, high energy drain affects movement
            energy_factor = self.current_energy / self.stats["max_energy"]
            move_speed *= energy_factor * speed_modifier
        elif terrain_type == "boost":
            # Boost terrain gives extra speed
            move_speed *= speed_modifier * 1.2  # Extra 20% boost
        else:
            # Apply general terrain speed modifier
            move_speed *= speed_modifier

        # 3. ENERGY DRAIN LOGIC
        base_drain = 0.5 * TERRAIN_DIFFICULTY
        actual_drain = base_drain * energy_drain
        self.current_energy -= actual_drain

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
        
        return True

    def add_race_result(self, position, earnings, race_number=None):
        """
        Record race result in history
        """
        if race_number is None:
            race_number = self.total_races + 1

        result = {
            "number": race_number,
            "position": position,
            "earnings": earnings,
            "age_at_race": self.age,
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

    @property
    def stamina(self):
        return self.stats["stamina"]

    @property
    def luck(self):
        return self.stats["luck"]

    @property
    def wins(self):
        """Calculate wins from race history"""
        return sum(1 for race in self.race_history if race.get('position') == 1)

    # --- Genetics Methods ---

    def get_genetic_trait(self, trait_name: str):
        """Get a specific genetic trait value"""
        return self.visual_genetics.get(trait_name)

    def set_genetic_trait(self, trait_name: str, value):
        """Set a specific genetic trait value"""
        self.visual_genetics[trait_name] = value

    def get_all_genetics(self):
        """Get complete genetics dictionary"""
        return self.visual_genetics.copy()

    def inherit_from_parents(self, parent1_genetics, parent2_genetics):
        """Create child genetics from two parents"""
        if self.genetics_system:
            self.visual_genetics = self.genetics_system.inherit_genetics(
                parent1_genetics, parent2_genetics
            )
        else:
            # Fallback: just copy parent1
            self.visual_genetics = parent1_genetics.copy()
            
        self.parent_ids = [
            parent1_genetics.get("turtle_id"),
            parent2_genetics.get("turtle_id"),
        ]
        self.generation = (
            max(
                parent1_genetics.get("generation", 0),
                parent2_genetics.get("generation", 0),
            )
            + 1
        )

    def mutate_trait(self, trait_name: str = None):
        """Apply mutation to a specific trait or random trait"""
        if not self.genetics_system:
            return

        if trait_name is None:
            # Pick a random trait to mutate
            trait_name = random.choice(
                self.genetics_system.get_gene_definitions().get_all_gene_names()
            )

        current_value = self.visual_genetics.get(trait_name)
        if current_value is not None:
            mutated_value = self.genetics_system.mutate_gene(trait_name, current_value)
            self.visual_genetics[trait_name] = mutated_value

    def get_trait_summary(self) -> str:
        """Get human-readable summary of key genetic traits"""
        traits = []

        # Shell traits
        shell_pattern = self.get_genetic_trait("shell_pattern_type")
        shell_color = self.get_genetic_trait("shell_base_color")
        traits.append(f"{shell_pattern} shell")

        # Limb traits
        limb_shape = self.get_genetic_trait("limb_shape")
        leg_length = self.get_genetic_trait("leg_length")
        traits.append(f"{limb_shape} legs")

        # Body traits
        body_pattern = self.get_genetic_trait("body_pattern_type")
        traits.append(f"{body_pattern} body")

        return ", ".join(traits)

    def __repr__(self):
        return f"<{self.name} (Spd:{self.stats['speed']})>"
