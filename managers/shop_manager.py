from core.game.game_state import generate_random_turtle, compute_turtle_cost
from settings import *
import pygame
import ui.layouts.positions as layout

class ShopManager:
    def __init__(self, game_state):
        self.game_state = game_state
        self.inventory = []
        self.message = ""
        self.message_timer = 0

    def handle_click(self, pos):
        # Check Navigation
        if layout.SHOP_BTN_BACK_RECT.collidepoint(pos):
            return "GOTO_MENU"
        
        if layout.SHOP_BTN_REFRESH_RECT.collidepoint(pos):
            self.refresh_stock()
            return None

        # Check Shop Slots
        for i, slot_rect in enumerate(layout.SHOP_SLOT_RECTS):
            # Calculate absolute button position
            # SHOP_BTN_BUY_RECT is relative to slot
            buy_rect = pygame.Rect(slot_rect.x + layout.SHOP_BTN_BUY_RECT.x, 
                                   slot_rect.y + layout.SHOP_BTN_BUY_RECT.y,
                                   layout.SHOP_BTN_BUY_RECT.width, layout.SHOP_BTN_BUY_RECT.height)
            
            if buy_rect.collidepoint(pos):
                self.buy_turtle(i)
        
        return None

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

            # Precompute and attach shop_cost for UI display
            for t in self.inventory:
                try:
                    t.shop_cost = compute_turtle_cost(t)
                except Exception:
                    t.shop_cost = COST_TURTLE
            self.message = "Shop Refreshed!"
            self.message_timer = 60
        else:
            self.message = "Not enough money!"
            self.message_timer = 60

    def buy_turtle(self, index):
        if index < len(self.inventory):
            turtle = self.inventory[index]
            cost = compute_turtle_cost(turtle)
            if self.game_state.money >= cost:
                # Find empty slot in roster
                for i in range(len(self.game_state.roster)):
                    if self.game_state.roster[i] is None:
                        self.game_state.roster[i] = self.inventory.pop(index)
                        self.game_state.money -= cost
                        self.message = f"Bought turtle for ${cost}!"
                        self.message_timer = 60
                        
                        # Auto-save after purchase
                        self.game_state.auto_save("purchase")
                        return
                self.message = "Roster Full!"
                self.message_timer = 60
            else:
                self.message = "Not enough money!"
                self.message_timer = 60
