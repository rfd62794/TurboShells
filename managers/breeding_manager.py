from game_state import breed_turtles
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

        # Check Breed button (mouse equivalent of pressing Enter)
        if layout.BREED_BTN_RECT.collidepoint(pos):
            if len(self.parents) == 2:
                if self.breed():
                    return "GOTO_MENU"
            return None

        # Otherwise, treat clicks as parent selection rows from the combined pool
        candidates = self._get_breeding_candidates()

        for i, turtle in enumerate(candidates):
            y_pos = layout.BREEDING_LIST_START_Y + (i * layout.BREEDING_SLOT_HEIGHT)
            row_rect = pygame.Rect(
                layout.BREEDING_ROW_X,
                y_pos,
                layout.BREEDING_ROW_WIDTH,
                layout.BREEDING_SLOT_HEIGHT,
            )
            if row_rect.collidepoint(pos):
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
