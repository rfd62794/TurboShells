import pygame
import sys
from settings import *
from entities import Turtle
from ui.renderer import Renderer
from managers.shop_manager import ShopManager
from managers.race_manager import RaceManager
from managers.breeding_manager import BreedingManager
from game_state import generate_random_turtle

# --- MAIN GAME CLASS ---
class TurboShellsGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Turbo Shells MVP")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        
        self.state = STATE_MENU
        
        # --- SHARED STATE ---
        # This object will be passed to renderers and managers
        # Using self as the container for simplicity in MVP
        self.roster = [
            Turtle("Starter", speed=5, energy=100, recovery=5, swim=5, climb=5),
            None, 
            None 
        ]
        self.retired_roster = []
        self.money = 100
        
        # State-specific data containers
        self.shop_inventory = []
        self.shop_message = ""
        
        self.race_results = []
        self.race_speed_multiplier = 1
        
        self.breeding_parents = []

        # --- MANAGERS ---
        self.renderer = Renderer(self.screen, self.font)
        self.shop_manager = ShopManager(self)
        self.race_manager = RaceManager(self)
        self.breeding_manager = BreedingManager(self)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                # Global Navigation
                if event.key == pygame.K_m: 
                    self.state = STATE_MENU
                    # Clear ONLY temporary opponents when returning to stable
                    if self.roster[1] and getattr(self.roster[1], 'is_temp', False):
                        self.roster[1] = None
                    if self.roster[2] and getattr(self.roster[2], 'is_temp', False):
                        self.roster[2] = None
                
                # State Specific Inputs
                if self.state == STATE_MENU:
                    if event.key == pygame.K_r: 
                        self.race_manager.start_race()
                        self.state = STATE_RACE
                    if event.key == pygame.K_s: self.state = STATE_SHOP
                    if event.key == pygame.K_b: self.state = STATE_BREEDING

                    # Retire Logic (4, 5, 6)
                    if event.key == pygame.K_4: self.retire_turtle(0)
                    if event.key == pygame.K_5: self.retire_turtle(1)
                    if event.key == pygame.K_6: self.retire_turtle(2)
                    
                    # Training Logic (Q, W, E)
                    if event.key == pygame.K_q: self.train_turtle(0)
                    if event.key == pygame.K_w: self.train_turtle(1)
                    if event.key == pygame.K_e: self.train_turtle(2)
                    
                    # Resting Logic (Z, X, C)
                    if event.key == pygame.K_z: self.rest_turtle(0)
                    if event.key == pygame.K_x: self.rest_turtle(1)
                    if event.key == pygame.K_c: self.rest_turtle(2)

                elif self.state == STATE_SHOP:
                    if event.key == pygame.K_r: self.shop_manager.refresh_stock()
                    if event.key == pygame.K_1: self.shop_manager.buy_turtle(0)
                    if event.key == pygame.K_2: self.shop_manager.buy_turtle(1)
                    if event.key == pygame.K_3: self.shop_manager.buy_turtle(2)
                
                elif self.state == STATE_RACE:
                    if event.key == pygame.K_1: self.race_speed_multiplier = 1
                    if event.key == pygame.K_2: self.race_speed_multiplier = 2
                    if event.key == pygame.K_3: self.race_speed_multiplier = 4
                    
                elif self.state == STATE_RACE_RESULT:
                    if event.key == pygame.K_m:
                        self.state = STATE_MENU
                        # Clear ONLY temporary opponents when returning to stable
                        if self.roster[1] and getattr(self.roster[1], 'is_temp', False):
                            self.roster[1] = None
                        if self.roster[2] and getattr(self.roster[2], 'is_temp', False):
                            self.roster[2] = None

                elif self.state == STATE_BREEDING:
                    if event.key == pygame.K_1: self.breeding_manager.toggle_parent(0)
                    if event.key == pygame.K_2: self.breeding_manager.toggle_parent(1)
                    if event.key == pygame.K_3: self.breeding_manager.toggle_parent(2)
                    if event.key == pygame.K_RETURN: 
                        if self.breeding_manager.breed():
                            self.state = STATE_MENU

    def update(self):
        if self.state == STATE_SHOP:
            self.shop_manager.update()

        if self.state == STATE_RACE:
            if self.race_manager.update():
                self.state = STATE_RACE_RESULT

    def draw(self):
        self.screen.fill(BLACK)
        
        if self.state == STATE_MENU:
            self.renderer.draw_menu(self)
        elif self.state == STATE_RACE:
            self.renderer.draw_race(self)
        elif self.state == STATE_RACE_RESULT:
            self.renderer.draw_race_result(self)
        elif self.state == STATE_SHOP:
            self.renderer.draw_shop(self)
        elif self.state == STATE_BREEDING:
            self.renderer.draw_breeding(self)
            
        pygame.display.flip()

    # --- DIRECT LOGIC (To be moved to RosterManager later) ---
    def retire_turtle(self, index):
        if self.roster[index] is not None:
            t = self.roster[index]
            self.roster[index] = None
            self.retired_roster.append(t)
            print(f"Retired {t.name}")

    def train_turtle(self, index):
        if self.roster[index]:
            t = self.roster[index]
            # Train Speed for now
            if t.train("speed"):
                print(f"Trained {t.name}! Speed is now {t.stats['speed']}")
            else:
                print(f"{t.name} is too tired to train!")

    def rest_turtle(self, index):
        if self.roster[index]:
            t = self.roster[index]
            t.current_energy = t.stats["max_energy"]
            print(f"{t.name} rested and recovered full energy.")

# --- ENTRY POINT ---
if __name__ == "__main__":
    game = TurboShellsGame()
    while True:
        game.handle_input()
        game.update()
        game.draw()
        game.clock.tick(FPS)