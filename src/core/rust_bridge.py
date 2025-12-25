"""Rust Bridge Module for TurboShells.

This module provides a bridge to the Rust turboshells_core library,
falling back to Python implementations if Rust is not available.

Usage:
    from core.rust_bridge import RustGenetics, RustTurtle, RustRace
    
    # These will use Rust if available, Python otherwise
    genetics = RustGenetics()
    turtle = RustTurtle("Name", speed=5, energy=100, ...)
"""

import logging

logger = logging.getLogger(__name__)

# Try to import Rust bindings
try:
    import turboshells_core
    RUST_AVAILABLE = True
    RUST_VERSION = turboshells_core.__version__
    logger.info(f"Rust turboshells_core v{RUST_VERSION} loaded successfully")
except ImportError:
    RUST_AVAILABLE = False
    RUST_VERSION = None
    logger.warning("Rust turboshells_core not available, using Python fallback")


class RustGenetics:
    """Wrapper for genetics system - uses Rust if available."""
    
    def __init__(self):
        if RUST_AVAILABLE:
            self._rust = turboshells_core.PyGenetics()
            self._use_rust = True
        else:
            from genetics import VisualGenetics
            self._python = VisualGenetics()
            self._use_rust = False
    
    def generate_random(self) -> dict:
        """Generate random genetics."""
        if self._use_rust:
            return self._rust.generate_random()
        else:
            return self._python.generate_random_genetics()
    
    def get_defaults(self) -> dict:
        """Get default genetics values."""
        if self._use_rust:
            return self._rust.get_defaults()
        else:
            return self._python.get_defaults()
    
    def inherit(self, parent1: dict, parent2: dict) -> dict:
        """Inherit genetics from two parents (Mendelian 50/50)."""
        if self._use_rust:
            return self._rust.inherit(parent1, parent2)
        else:
            return self._python.inherit_genetics(parent1, parent2)
    
    def inherit_blended(self, parent1: dict, parent2: dict) -> dict:
        """Inherit with blending for continuous traits."""
        if self._use_rust:
            return self._rust.inherit_blended(parent1, parent2)
        else:
            # Python fallback uses same method
            return self._python.inherit_genetics(parent1, parent2)
    
    def mutate(self, genetics: dict, rate: float = 0.1) -> dict:
        """Apply mutations with specified rate."""
        if self._use_rust:
            return self._rust.mutate(genetics, rate)
        else:
            return self._python.mutate_genetics(genetics, rate)
    
    def similarity(self, genetics1: dict, genetics2: dict) -> float:
        """Calculate genetic similarity (0.0 to 1.0)."""
        if self._use_rust:
            return self._rust.similarity(genetics1, genetics2)
        else:
            return self._python.calculate_genetic_similarity(genetics1, genetics2)


class RustTurtle:
    """Wrapper for Turtle - uses Rust physics if available."""
    
    def __init__(self, name: str, speed: float, energy: float, recovery: float,
                 swim: float, climb: float, stamina: float = 3.0, luck: float = 3.0):
        self.name = name
        self._stats = {
            'speed': speed,
            'max_energy': energy,
            'recovery': recovery,
            'swim': swim,
            'climb': climb,
            'stamina': stamina,
            'luck': luck,
        }
        
        if RUST_AVAILABLE:
            self._rust = turboshells_core.PyTurtle(
                name, speed, energy, recovery, swim, climb, stamina, luck
            )
            self._use_rust = True
        else:
            self._use_rust = False
            # Python state
            self.current_energy = energy
            self.race_distance = 0.0
            self.is_resting = False
            self.finished = False
    
    @property
    def id(self) -> str:
        if self._use_rust:
            return self._rust.id
        return ""
    
    @property
    def current_energy(self) -> float:
        if self._use_rust:
            return self._rust.current_energy
        return self._current_energy
    
    @current_energy.setter
    def current_energy(self, value: float):
        self._current_energy = value
    
    @property
    def race_distance(self) -> float:
        if self._use_rust:
            return self._rust.race_distance
        return self._race_distance
    
    @race_distance.setter
    def race_distance(self, value: float):
        self._race_distance = value
    
    @property
    def is_resting(self) -> bool:
        if self._use_rust:
            return self._rust.is_resting
        return self._is_resting
    
    @is_resting.setter
    def is_resting(self, value: bool):
        self._is_resting = value
    
    @property
    def finished(self) -> bool:
        if self._use_rust:
            return self._rust.finished
        return self._finished
    
    @finished.setter
    def finished(self, value: bool):
        self._finished = value
    
    def reset_for_race(self):
        """Reset turtle for a new race."""
        if self._use_rust:
            self._rust.reset_for_race()
        else:
            self._current_energy = self._stats['max_energy']
            self._race_distance = 0.0
            self._is_resting = False
            self._finished = False
    
    def update_physics(self, terrain_type: str, speed_mod: float = 1.0, 
                       energy_drain: float = 1.0) -> float:
        """Update physics for one tick. Returns distance moved."""
        if self._use_rust:
            return self._rust.update_physics(terrain_type, speed_mod, energy_drain)
        else:
            # Simplified Python fallback
            if self._is_resting:
                self._current_energy += self._stats['recovery'] * 0.1
                if self._current_energy >= self._stats['max_energy'] * 0.5:
                    self._is_resting = False
                return 0.0
            
            move_speed = self._stats['speed'] * speed_mod
            self._current_energy -= 0.5 * 0.8 * energy_drain
            
            if self._current_energy <= 0:
                self._current_energy = 0
                self._is_resting = True
            
            return move_speed
    
    def get_stats(self) -> dict:
        """Get turtle stats."""
        if self._use_rust:
            return self._rust.get_stats()
        return self._stats.copy()


class RustRace:
    """Wrapper for Race simulation - uses Rust if available."""
    
    def __init__(self, track_length: float = 1500.0):
        self.track_length = track_length
        self._turtles = []
        
        if RUST_AVAILABLE:
            self._rust = turboshells_core.PyRace(track_length)
            self._use_rust = True
        else:
            self._use_rust = False
    
    def add_turtle(self, turtle: RustTurtle):
        """Add a turtle to the race."""
        self._turtles.append(turtle)
        if self._use_rust and turtle._use_rust:
            self._rust.add_turtle(turtle._rust)
    
    def run(self) -> str:
        """Run the full race. Returns winner name."""
        if self._use_rust:
            return self._rust.run()
        else:
            # Python fallback
            for t in self._turtles:
                t.reset_for_race()
            
            for _ in range(5000):
                for t in self._turtles:
                    if not t.finished:
                        dist = t.update_physics('normal')
                        t._race_distance += dist
                        if t._race_distance >= self.track_length:
                            t._finished = True
                            return t.name
            
            # Find furthest
            return max(self._turtles, key=lambda t: t.race_distance).name
    
    def tick(self) -> bool:
        """Run a single tick. Returns True if race finished."""
        if self._use_rust:
            return self._rust.tick()
        else:
            for t in self._turtles:
                if not t._finished:
                    dist = t.update_physics('normal')
                    t._race_distance += dist
                    if t._race_distance >= self.track_length:
                        t._finished = True
            return any(t._finished for t in self._turtles)
    
    def get_positions(self) -> list:
        """Get current positions as list of (name, distance)."""
        if self._use_rust:
            return self._rust.get_positions()
        else:
            positions = [(t.name, t.race_distance) for t in self._turtles]
            return sorted(positions, key=lambda x: -x[1])


# Convenience function to check Rust status
def is_rust_available() -> bool:
    """Check if Rust turboshells_core is available."""
    return RUST_AVAILABLE


def get_rust_version() -> str:
    """Get Rust library version or 'N/A' if not available."""
    return RUST_VERSION or "N/A"
