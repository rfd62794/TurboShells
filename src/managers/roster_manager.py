import pygame
from settings import *
import ui.layouts.positions as layout


class RosterManager:
    def __init__(self, game_state):
        self.game_state = game_state

    def handle_click(self, pos):
        # View toggle buttons: Active vs Retired
        if layout.VIEW_ACTIVE_RECT.collidepoint(pos):
            self.game_state.show_retired_view = False
        elif layout.VIEW_RETIRED_RECT.collidepoint(pos):
            self.game_state.show_retired_view = True

        # Betting Buttons (set current bet amount) - only in select racer mode
        select_racer_mode = getattr(self.game_state, "select_racer_mode", False)
        if select_racer_mode:
            if layout.BET_BTN_NONE_RECT.collidepoint(pos):
                self.game_state.current_bet = 0
            elif layout.BET_BTN_5_RECT.collidepoint(pos):
                self.game_state.current_bet = 5
            elif layout.BET_BTN_10_RECT.collidepoint(pos):
                self.game_state.current_bet = 10

        # Check Roster Slots (only actionable in Active view)
        for i, slot_rect in enumerate(layout.SLOT_RECTS):
            # We need absolute positions for buttons which are defined relative in layout.py?
            # Wait, layout.py defines them as absolute Rects if I recall correctly?
            # Let's check layout.py content.
            # Actually, looking at layout.py, the buttons are defined relative to the slot or absolute?
            # SLOT_BTN_TRAIN_RECT = pygame.Rect(580, 15, 100, 30) -> This looks like relative Y?
            # No, Y is 15. That's definitely relative to the slot.

            # We need to calculate absolute rects for buttons
            slot_x = slot_rect.x
            slot_y = slot_rect.y

            train_rect = pygame.Rect(
                slot_x + layout.SLOT_BTN_TRAIN_RECT.x,
                slot_y + layout.SLOT_BTN_TRAIN_RECT.y,
                layout.SLOT_BTN_TRAIN_RECT.width,
                layout.SLOT_BTN_TRAIN_RECT.height,
            )

            retire_rect = pygame.Rect(
                slot_x + layout.SLOT_BTN_RETIRE_RECT.x,
                slot_y + layout.SLOT_BTN_RETIRE_RECT.y,
                layout.SLOT_BTN_RETIRE_RECT.width,
                layout.SLOT_BTN_RETIRE_RECT.height,
            )

            # Check if this slot is the active racer
            is_active_racer = i == getattr(self.game_state, "active_racer_index", 0)

            if not getattr(self.game_state, "show_retired_view", False):
                # First check for action buttons (for any turtle with a train button)
                if self.game_state.roster[i]:
                    if train_rect.collidepoint(pos):
                        self.train_turtle(i)
                        return  # Don't continue to slot check
                    elif retire_rect.collidepoint(pos):
                        self.retire_turtle(i)
                        return  # Don't continue to slot check

                # Then check for slot selection (profile view or select turtle)
                if slot_rect.collidepoint(pos):
                    # Check for turtle card click (profile view access)
                    if self.game_state.roster[i]:
                        return "PROFILE"
                    self.game_state.active_racer_index = i
            else:
                # In retired view, check for profile view access
                if slot_rect.collidepoint(pos):
                    retired_index = i
                    if retired_index < len(self.game_state.retired_roster):
                        return "PROFILE"

        return None

    def train_turtle(self, index):
        if self.game_state.roster[index]:
            t = self.game_state.roster[index]
            # Train Speed for now (could be random stat in future)
            if t.train("speed"):
                print(f"Trained {t.name}! Speed is now {t.stats['speed']}")
                # Auto-retire turtles that reach max age via training
                if t.age >= MAX_AGE:
                    self.retire_turtle(index)
                # Auto-save after training
                self.game_state.auto_save("training")
            else:
                print(f"{t.name} is too tired to train!")

    def rest_turtle(self, index):
        if self.game_state.roster[index]:
            t = self.game_state.roster[index]
            t.current_energy = t.stats["max_energy"]
            print(f"{t.name} rested and recovered full energy.")

    def retire_turtle(self, index):
        if self.game_state.roster[index] is not None:
            t = self.game_state.roster[index]
            t.is_active = False
            self.game_state.roster[index] = None
            self.game_state.retired_roster.append(t)
            print(f"Retired {t.name}")
            
    def release_turtle(self, index):
        """Permanently release a turtle from the roster (frees up space)"""
        show_retired = getattr(self.game_state, 'show_retired_view', False)
        
        if show_retired:
            # Release from retired roster
            retired_roster = self.game_state.retired_roster
            if 0 <= index < len(retired_roster):
                t = retired_roster.pop(index)
                print(f"Released {t.name} from retired roster")
                self.game_state.auto_save("release")
        else:
            # Release from active roster
            if 0 <= index < len(self.game_state.roster) and self.game_state.roster[index] is not None:
                t = self.game_state.roster[index]
                self.game_state.roster[index] = None
                print(f"Released {t.name} from active roster")
                self.game_state.auto_save("release")
