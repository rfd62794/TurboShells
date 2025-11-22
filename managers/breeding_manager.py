from game_state import breed_turtles
from settings import *
import pygame # Needed for Rect
import ui.layout as layout

class BreedingManager:
    def __init__(self, game_state):
        self.game_state = game_state
        self.parents = []

    def handle_click(self, pos):
        # Check Navigation (Back to Menu is implicit or we need a button)
        # The UI Layout doesn't explicitly define a Back button for Breeding, 
        # but we should probably add one or check for a specific area.
        # For now, let's assume clicking outside or a specific key returns, 
        # but wait, the user wants MOUSE support.
        # Let's add a "Back" check if we had a button, but layout doesn't have one yet.
        # We'll rely on 'M' key for now unless we add a button to layout.
        # Actually, let's check if we can click the parents.
        
        for i, turtle in enumerate(self.game_state.retired_roster):
            y_pos = 120 + (i * 80)
            # We need a rect for the row
            row_rect = pygame.Rect(50, y_pos, 600, 60)
            if row_rect.collidepoint(pos):
                self.toggle_parent(i)
                return None
        
        # Check Breed Button (We need to add one to layout or hardcode it for now)
        # Let's assume a Breed button exists or we use the "Enter" key logic.
        # For MVP mouse support, let's add a virtual rect for "Breed" if 2 parents selected.
        # Or better, let's just support parent selection for now.
        
        return None

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
