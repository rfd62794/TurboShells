"""NPC Manager: Manages a pool of persistent bot racers.

Maintains a cache of NPC turtles that persist across multiple races
to provide continuity (racing the same "ShellShock" twice) while
cycling them out periodically to ensure variety.
"""

import random
import uuid
from typing import List, Dict, Any

from src.game.entities import Turtle
from src.engine.logging_config import get_logger

logger = get_logger(__name__)

class NPCManager:
    def __init__(self, cache_size: int = 100):
        self.cache_size = cache_size
        # Pool structure: {turtle_id: {'turtle': Turtle, 'uses_left': int}}
        self._pool: Dict[str, Dict[str, Any]] = {}
        self._npc_names = [
            "SpeedyBot", "ShellShock", "TurboNPC", "SlowPoke", 
            "MechaTurtle", "DriftKing", "RoboRacer", "ByteShell",
            "Glitch", "Vector", "Ping", "Packet", "Socket"
        ]
        
        # Initial population
        self._replenish_pool()
        
    def _create_npc(self) -> Turtle:
        """Generate a single fresh NPC."""
        name = f"{random.choice(self._npc_names)} {random.randint(1, 99)}"
        
        # Randomize stats around a balanced baseline
        # Speed: 8-12 (Avg 10)
        # Energy: 80-120 (Avg 100)
        # Recovery: 3-7 (Avg 5)
        npc = Turtle(
            name=name,
            speed=random.uniform(8.0, 12.0),
            energy=random.uniform(80.0, 120.0),
            recovery=random.uniform(3.0, 7.0),
            swim=5.0,
            climb=5.0
        )
        
        # Format ID specifically for NPCs
        npc.id = f"npc-{str(uuid.uuid4())[:8]}" 
        npc.is_npc = True
        
        return npc

    def _replenish_pool(self):
        """Fill the pool up to cache_size."""
        current_count = len(self._pool)
        needed = self.cache_size - current_count
        
        if needed > 0:
            for _ in range(needed):
                npc = self._create_npc()
                # Random usage limit between 3 and 10 races
                limit = random.randint(3, 10)
                self._pool[npc.id] = {
                    'turtle': npc,
                    'uses_left': limit
                }
            
            if logger:
                logger.info(f"Replenished NPC pool (+{needed})")

    def get_racers(self, count: int) -> List[Turtle]:
        """Get a list of unique NPCs for a race.
        
        Selects random turtles from the pool, decrements their life,
        and retires them if expired.
        """
        # Ensure we have enough
        if len(self._pool) < count:
            self._replenish_pool()
            
        # Select random IDs
        available_ids = list(self._pool.keys())
        # If requested count > available, fallback (shouldn't happen with cache=100)
        count = min(count, len(available_ids))
        
        selected_ids = random.sample(available_ids, count)
        selected_turtles = []
        
        for tid in selected_ids:
            entry = self._pool[tid]
            turtle = entry['turtle']
            
            # Reset state for the new race
            turtle.reset_for_race()
            selected_turtles.append(turtle)
            
            # Decrement life
            entry['uses_left'] -= 1
            
            # Retire if expired
            if entry['uses_left'] <= 0:
                del self._pool[tid]
        
        # Top up pool for next time
        if len(self._pool) < self.cache_size:
            self._replenish_pool()
            
        return selected_turtles
