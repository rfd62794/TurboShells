"""Headless simulation harness for balancing Turtle physics.

Runs races between real `entities.Turtle` instances using the shared
`race_track` helper, without any PyGame window or UI.
"""

from core.entities import Turtle # <--- IMPORT THE SHARED CLASS
import random
from core.race_track import generate_track, get_terrain_at

TRACK_LENGTH = 1500

def run_race(turtle_a, turtle_b):
    # Reset them so they are fresh
    turtle_a.reset_for_race()
    turtle_b.reset_for_race()
    
    # Generate Track using shared helper
    track = generate_track(TRACK_LENGTH)
        
    finished = False
    ticks = 0
    
    while not finished:
        ticks += 1
        
        # Get current terrain
        terrain_a = get_terrain_at(track, turtle_a.race_distance)
        terrain_b = get_terrain_at(track, turtle_b.race_distance)

        # Update Physics using the Shared Logic
        dist_a = turtle_a.update_physics(terrain_a)
        dist_b = turtle_b.update_physics(terrain_b)
        
        turtle_a.race_distance += dist_a
        turtle_b.race_distance += dist_b
        
        if turtle_a.race_distance >= TRACK_LENGTH: return "A"
        if turtle_b.race_distance >= TRACK_LENGTH: return "B"
        if ticks > 5000: return "DRAW"

if __name__ == "__main__":
    # Create real Turtle objects
    t1 = Turtle("Speedster", speed=12, energy=60, recovery=2, swim=5, climb=5)
    t2 = Turtle("Tank", speed=8, energy=100, recovery=8, swim=5, climb=5)
    
    print("Running Simulation using Shared Entities...")
    wins = {"A": 0, "B": 0}
    for _ in range(1000):
        winner = run_race(t1, t2)
        if winner in wins: wins[winner] += 1
        
    print(f"Speedster Wins: {wins['A']}")
    print(f"Tank Wins: {wins['B']}")