from game_state import generate_random_turtle
from settings import *

class ShopManager:
    def __init__(self, game_state):
        self.game_state = game_state
        self.inventory = []
        self.message = ""
        self.message_timer = 0

    def update(self):
        # Refill Shop if empty
        if not self.inventory:
            self.refresh_stock(free=True)
        
        # Message Timer
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.message = ""
        
        # Sync with game state for rendering
        self.game_state.shop_inventory = self.inventory
        self.game_state.shop_message = self.message

    def refresh_stock(self, free=False):
        if free or self.game_state.money >= COST_REFRESH:
            if not free: 
                self.game_state.money -= COST_REFRESH
            
            self.inventory = [
                generate_random_turtle(level=1),
                generate_random_turtle(level=2),
                generate_random_turtle(level=3)
            ]
            self.message = "Shop Refreshed!"
            self.message_timer = 60
        else:
            self.message = "Not enough money!"
            self.message_timer = 60

    def buy_turtle(self, index):
        if index < len(self.inventory):
            if self.game_state.money >= COST_TURTLE:
                # Find empty slot in roster
                for i in range(len(self.game_state.roster)):
                    if self.game_state.roster[i] is None:
                        self.game_state.roster[i] = self.inventory.pop(index)
                        self.game_state.money -= COST_TURTLE
                        self.message = "Bought turtle!"
                        self.message_timer = 60
                        return
                self.message = "Roster Full!"
                self.message_timer = 60
            else:
                self.message = "Not enough money!"
                self.message_timer = 60
