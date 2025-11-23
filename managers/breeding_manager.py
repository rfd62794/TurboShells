from core.game.game_state import breed_turtles
from settings import *
import pygame # Needed for Rect
import ui.layout as layout

class BreedingManager:
    def __init__(self, game_state):
        self.game_state = game_state
        self.parents = []

    def handle_click(self, pos):
        # Check navigation buttons first
        if layout.BREED_BACK_BTN_RECT.collidepoint(pos):
            return "GOTO_MENU"

        # Check Breed button at new position (next to instructions)
        breed_rect = pygame.Rect(250, 55, 100, 35)
        if breed_rect.collidepoint(pos):
            if len(self.parents) == 2:
                if self.breed():
                    return "GOTO_MENU"
            return None

        # Otherwise, treat clicks as parent selection from the breeding grid
        candidates = self._get_breeding_candidates()
        
        # Check breeding slot clicks (2x3 grid) - updated positions
        breeding_slots = [
            pygame.Rect(50, 140, 220, 180),   # Top row
            pygame.Rect(290, 140, 220, 180),
            pygame.Rect(530, 140, 220, 180),
            pygame.Rect(50, 340, 220, 180),   # Bottom row
            pygame.Rect(290, 340, 220, 180),
            pygame.Rect(530, 340, 220, 180),
        ]
        
        for idx, slot_rect in enumerate(breeding_slots):
            if idx < len(candidates) and slot_rect.collidepoint(pos):
                turtle = candidates[idx]
                self._toggle_parent_by_turtle(turtle)
                return None
        
        return None

    def toggle_parent(self, index):
        """Keyboard-based toggle (debug): indexes into retired_roster only."""
        if index < len(self.game_state.retired_roster):
            t = self.game_state.retired_roster[index]
            if t in self.parents:
                self.parents.remove(t)
            else:
                if len(self.parents) < 2:
                    self.parents.append(t)
        self.game_state.breeding_parents = self.parents

    def _toggle_parent_by_turtle(self, turtle):
        if turtle in self.parents:
            self.parents.remove(turtle)
        else:
            if len(self.parents) < 2:
                self.parents.append(turtle)
        # Sync with game state for UI
        self.game_state.breeding_parents = self.parents

    def _get_breeding_candidates(self):
        """Return combined breeding pool: active roster + retired turtles."""
        active = [t for t in self.game_state.roster if t is not None]
        retired = list(self.game_state.retired_roster)
        return active + retired

    def breed(self):
        if len(self.parents) == 2:
            parent_a = self.parents[0]
            parent_b = self.parents[1]
            
            # Always remove parent_b to make space for the child
            # Find parent_b in the active roster and remove it
            slot_idx = -1
            for i, t in enumerate(self.game_state.roster):
                if t is parent_b:
                    self.game_state.roster[i] = None
                    slot_idx = i  # Use this slot for the child
                    break
            
            # If parent_b wasn't in active roster, try retired roster
            if slot_idx == -1:
                if parent_b in self.game_state.retired_roster:
                    self.game_state.retired_roster.remove(parent_b)
                    # Find first empty slot in active roster
                    for i, t in enumerate(self.game_state.roster):
                        if t is None:
                            slot_idx = i
                            break
                
                # If still no slot, remove parent_a instead to make space
                if slot_idx == -1:
                    for i, t in enumerate(self.game_state.roster):
                        if t is parent_a:
                            self.game_state.roster[i] = None
                            slot_idx = i
                            break
            
            # If we still don't have a slot (shouldn't happen), can't breed
            if slot_idx == -1:
                print("Error: Could not find space for breeding!")
                return False
            
            # Create the child and place it in the freed slot
            child = breed_turtles(parent_a, parent_b)
            self.game_state.roster[slot_idx] = child
            
            # Clear breeding selection
            self.parents = []
            self.game_state.breeding_parents = []
            
            print(f"Bred {child.name}!")
            
            # Auto-save after breeding
            self.game_state.auto_save("breeding")
            
            return True # Success
        return False
