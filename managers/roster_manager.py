import pygame
from settings import *
import ui.layout as layout

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
            slot_y = slot_rect.y
            
            train_rect = pygame.Rect(layout.SLOT_BTN_TRAIN_RECT.x, slot_y + layout.SLOT_BTN_TRAIN_RECT.y, 
                                     layout.SLOT_BTN_TRAIN_RECT.width, layout.SLOT_BTN_TRAIN_RECT.height)
            
            retire_rect = pygame.Rect(layout.SLOT_BTN_RETIRE_RECT.x, slot_y + layout.SLOT_BTN_RETIRE_RECT.y, 
                                      layout.SLOT_BTN_RETIRE_RECT.width, layout.SLOT_BTN_RETIRE_RECT.height)

            # Check if this slot is the active racer
            is_active_racer = i == getattr(self.game_state, "active_racer_index", 0)
            
            if not getattr(self.game_state, "show_retired_view", False):
                # First check for slot selection
                if slot_rect.collidepoint(pos):
                    self.game_state.active_racer_index = i
                # Then check for action buttons (only if this slot is selected and has a turtle)
                elif is_active_racer and self.game_state.roster[i]:
                    if train_rect.collidepoint(pos):
                        self.train_turtle(i)
                    elif retire_rect.collidepoint(pos):
                        self.retire_turtle(i)
                    # Check for individual race button
                    race_btn = pygame.Rect(slot_rect.x + 550, slot_rect.y + 15, 80, 28)
                    if race_btn.collidepoint(pos):
                        return "GOTO_RACE"
        
        return None

    def train_turtle(self, index):
        if self.game_state.roster[index]:
            t = self.game_state.roster[index]
            # Train Speed for now
            if t.train("speed"):
                print(f"Trained {t.name}! Speed is now {t.stats['speed']}")
                # Auto-retire turtles that reach age 100 via training
                if t.age >= 100:
                    self.retire_turtle(index)
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
