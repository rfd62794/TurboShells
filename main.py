import pygame
import sys
from entities import Turtle  # <--- IMPORT THE SHARED CLASS
from game_state import generate_random_turtle # <--- IMPORT HELPER

# --- CONSTANTS ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
BLUE = (50, 50, 200)
GRAY = (100, 100, 100)

# Game States
STATE_MENU = "MENU"
STATE_RACE = "RACE"
STATE_SHOP = "SHOP"

# --- MAIN GAME CLASS ---
class TurboShellsGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Turbo Shells MVP")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        
        self.state = STATE_MENU
        
        # Initialize Roster with Shared Entities
        self.roster = [
            Turtle("Starter", speed=5, energy=100, recovery=5, swim=5, climb=5),
            None, 
            None 
        ]
        
        # Race Variables
        self.track_length_logic = 1500 # The logical distance (matches simulation)
        self.track_length_pixels = 700 # The visual distance on screen
        self.race_speed_multiplier = 1

        # Economy & Shop
        self.money = 100
        self.shop_inventory = []

        self.shop_inventory = []

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m: 
                    self.state = STATE_MENU
                    # Clear opponents when returning to stable
                    self.roster[1] = None
                    self.roster[2] = None
                if event.key == pygame.K_r: 
                    self.reset_race()
                    self.state = STATE_RACE
                if event.key == pygame.K_s: self.state = STATE_SHOP
                
                if self.state == STATE_SHOP:
                    # Simple Shop Buying Logic (1, 2, 3 keys)
                    if event.key == pygame.K_1: self.buy_turtle(0)
                    if event.key == pygame.K_2: self.buy_turtle(1)
        # Draw Body
        color = GREEN
        if turtle.is_resting: color = BLUE # Visual feedback for resting
        
        pygame.draw.rect(self.screen, color, (screen_x, y_pos, 40, 30))
        
        # Draw Energy Bar above head
        bar_width = 40
        pct = turtle.current_energy / turtle.stats['max_energy']
        fill_width = int(pct * bar_width)
        
        pygame.draw.rect(self.screen, RED, (screen_x, y_pos - 10, bar_width, 5))
        pygame.draw.rect(self.screen, color, (screen_x, y_pos - 10, fill_width, 5))

# --- ENTRY POINT ---
if __name__ == "__main__":
    game = TurboShellsGame()
    while True:
        game.handle_input()
        game.update()
        game.draw()
        game.clock.tick(FPS)