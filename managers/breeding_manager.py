from game_state import breed_turtles
from settings import *

class BreedingManager:
    def __init__(self, game_state):
        self.game_state = game_state
        self.parents = []

    def toggle_parent(self, index):
        if index < len(self.game_state.retired_roster):
            t = self.game_state.retired_roster[index]
            if t in self.parents:
                self.parents.remove(t)
            else:
                if len(self.parents) < 2:
                    self.parents.append(t)
        
        # Sync with game state for UI
        self.game_state.breeding_parents = self.parents

    def breed(self):
        if len(self.parents) == 2:
            # Check for empty slot
            slot_idx = -1
            for i in range(len(self.game_state.roster)):
                if self.game_state.roster[i] is None:
                    slot_idx = i
                    break
            
            if slot_idx != -1:
                parent_a = self.parents[0]
                parent_b = self.parents[1]
                
                child = breed_turtles(parent_a, parent_b)
                self.game_state.roster[slot_idx] = child
                
                # Remove parents from retired roster
                self.game_state.retired_roster.remove(parent_a)
                self.game_state.retired_roster.remove(parent_b)
                self.parents = []
                self.game_state.breeding_parents = []
                
                print(f"Bred {child.name}!")
                return True # Success
            else:
                print("No Roster Space!")
        return False
