from game_state import generate_random_turtle
from settings import *

class RaceManager:
    def __init__(self, game_state):
        self.game_state = game_state
        self.results = []

    def start_race(self):
        self.results = []
        self.game_state.race_results = []
        
        # Fill empty slots with opponents
        if self.game_state.roster[1] is None:
            t = generate_random_turtle(level=1)
            t.is_temp = True
            self.game_state.roster[1] = t
        if self.game_state.roster[2] is None:
            t = generate_random_turtle(level=1)
            t.is_temp = True
            self.game_state.roster[2] = t

        for t in self.game_state.roster:
            if t:
                t.reset_for_race()

    def update(self):
        active_turtles = [t for t in self.game_state.roster if t is not None]
        
        for _ in range(self.game_state.race_speed_multiplier):
            for t in active_turtles:
                # 1. Determine Terrain (Placeholder for Track Logic)
                terrain = "grass"
                if 500 < t.race_distance < 700:
                    terrain = "water"
                
                # 2. UPDATE PHYSICS (Using the Shared Class)
                move_amt = t.update_physics(terrain)
                t.race_distance += move_amt
                
                # 3. Check Finish
                if t.race_distance >= TRACK_LENGTH_LOGIC and not t.finished:
                    t.finished = True
                    t.rank = len(self.results) + 1
                    self.results.append(t)
        
        # Sync results
        self.game_state.race_results = self.results

        # Check if Race Over (All finished)
        if len(self.results) == len(active_turtles):
            self.process_rewards()
            return True # Race Finished
        return False

    def process_rewards(self):
        # Find player rank
        player_turtle = self.game_state.roster[0]
        if player_turtle in self.results:
            rank = player_turtle.rank
            reward = 0
            if rank == 1: reward = REWARD_1ST
            elif rank == 2: reward = REWARD_2ND
            elif rank == 3: reward = REWARD_3RD
            
            self.game_state.money += reward
            print(f"Player finished {rank}. Reward: ${reward}")
