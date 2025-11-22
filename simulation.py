from entities import Turtle # <--- IMPORT THE SHARED CLASS
import random

TRACK_LENGTH = 1500

def run_race(turtle_a, turtle_b):
    # Reset them so they are fresh
    turtle_a.reset_for_race()
    turtle_b.reset_for_race()
    
    # Generate Track
    track = []
    for _ in range(int(TRACK_LENGTH / 10) + 100):
        r = random.random()
        if r < 0.6: track.append("grass")
        elif r < 0.8: track.append("water")
        else: track.append("rock")
        
    finished = False
    ticks = 0
    
    while not finished:
        ticks += 1
        
        # Get current terrain
        idx_a = min(int(turtle_a.race_distance / 10), len(track)-1)
        idx_b = min(int(turtle_b.race_distance / 10), len(track)-1)
        
        # Update Physics using the Shared Logic
        dist_a = turtle_a.update_physics(track[idx_a])
        dist_b = turtle_b.update_physics(track[idx_b])
        
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