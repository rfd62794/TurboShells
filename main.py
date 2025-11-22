import pygame
import sys
from entities import Turtle  # <--- IMPORT THE SHARED CLASS
from game_state import generate_random_turtle, breed_turtles # <--- IMPORT HELPER

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
STATE_RACE_RESULT = "RACE_RESULT"
STATE_SHOP = "SHOP"
STATE_BREEDING = "BREEDING"

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
        self.retired_roster = [] # Turtles moved here for breeding
        
        # Breeding State Variables
        self.breeding_parents = [] # List of 2 turtles selected for breeding
        
        # Race Variables
        self.track_length_logic = 1500 # The logical distance (matches simulation)
        self.track_length_pixels = 700 # The visual distance on screen
        self.race_speed_multiplier = 1
        
        self.race_results = [] # List of turtles in finish order

        # Economy & Shop
        self.money = 100
        self.shop_inventory = []
        self.shop_message = "" # Feedback message
        self.shop_message_timer = 0

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
                    if self.state == STATE_SHOP:
                        self.refresh_shop()
                    elif self.state == STATE_MENU:
                        self.reset_race()
                        self.state = STATE_RACE
                if event.key == pygame.K_s: self.state = STATE_SHOP
                if event.key == pygame.K_b: self.state = STATE_BREEDING # B for Breeding

                if self.state == STATE_MENU:
                    # Simple Retire Logic (4, 5, 6 keys for slots 1, 2, 3)
                    if event.key == pygame.K_4: self.retire_turtle(0)
                    if event.key == pygame.K_5: self.retire_turtle(1)
                    if event.key == pygame.K_6: self.retire_turtle(2)
                
                if self.state == STATE_SHOP:
                    # Simple Shop Buying Logic (1, 2, 3 keys)
                    if event.key == pygame.K_1: self.buy_turtle(0)
                    if event.key == pygame.K_2: self.buy_turtle(1)
                    if event.key == pygame.K_3: self.buy_turtle(2)
                
                if self.state == STATE_RACE:
                    if event.key == pygame.K_1: self.race_speed_multiplier = 1
                    if event.key == pygame.K_2: self.race_speed_multiplier = 2
                    if event.key == pygame.K_3: self.race_speed_multiplier = 4
                    
                if self.state == STATE_RACE_RESULT:
                    if event.key == pygame.K_m:
                        self.state = STATE_MENU
                        # Clear opponents
                        self.roster[1] = None
                        self.roster[2] = None

                if self.state == STATE_BREEDING:
                    if event.key == pygame.K_m: self.state = STATE_MENU
                    # Select Parents (1, 2, 3... based on retired list)
                    # For MVP, just press 1, 2 to select first two retired
                    if event.key == pygame.K_1: self.toggle_breeding_parent(0)
                    if event.key == pygame.K_2: self.toggle_breeding_parent(1)
                    if event.key == pygame.K_3: self.toggle_breeding_parent(2)
                    if event.key == pygame.K_RETURN: self.breed()

    def reset_race(self):
        """Prepares shared entities for a new race"""
        self.race_results = []
        
        # Fill empty slots with opponents
        if self.roster[1] is None:
            self.roster[1] = generate_random_turtle(level=1)
        if self.roster[2] is None:
            self.roster[2] = generate_random_turtle(level=1)

        for t in self.roster:
            if t:
                t.reset_for_race()

    def update(self):
        if self.state == STATE_SHOP:
            # Refill Shop if empty
            if not self.shop_inventory:
                self.refresh_shop(free=True)
            
            # Message Timer
            if self.shop_message_timer > 0:
                self.shop_message_timer -= 1
                if self.shop_message_timer <= 0:
                    self.shop_message = ""

        if self.state == STATE_RACE:
            active_turtles = [t for t in self.roster if t is not None]
            
            for _ in range(self.race_speed_multiplier):
                for t in active_turtles:
                    # 1. Determine Terrain (Placeholder for Track Logic)
                    # Example: Water patch between 500 and 700 units
                    terrain = "grass"
                    if 500 < t.race_distance < 700:
                        terrain = "water"
                    
                    # 2. UPDATE PHYSICS (Using the Shared Class)
                    move_amt = t.update_physics(terrain)
                    t.race_distance += move_amt
                    
                    # 3. Check Finish
                    if t.race_distance >= self.track_length_logic and not t.finished:
                        t.finished = True
                        t.rank = len(self.race_results) + 1
                        self.race_results.append(t)
            
            # Check if Race Over (All finished)
            if len(self.race_results) == len(active_turtles):
                self.process_race_rewards()
                self.state = STATE_RACE_RESULT

    def process_race_rewards(self):
        # Find player rank
        player_turtle = self.roster[0]
        if player_turtle in self.race_results:
            rank = player_turtle.rank
            reward = 0
            if rank == 1: reward = 50
            elif rank == 2: reward = 25
            elif rank == 3: reward = 10
            
            self.money += reward
            print(f"Player finished {rank}. Reward: ${reward}")

    def draw(self):
        self.screen.fill(BLACK)
        
        if self.state == STATE_MENU:
            self.draw_menu()
        elif self.state == STATE_RACE:
            self.draw_race()
        elif self.state == STATE_RACE_RESULT:
            self.draw_race_result()
        elif self.state == STATE_SHOP:
            self.draw_shop()
        elif self.state == STATE_BREEDING:
            self.draw_breeding()
            
        pygame.display.flip()

    def draw_menu(self):
        title = self.font.render(f"STABLE MENU (R=Race, S=Shop, B=Breed) | Money: ${self.money}", True, WHITE)
        self.screen.blit(title, (20, 20))
        
        msg = self.font.render("Press 4, 5, 6 to Retire a Turtle (Permanent!)", True, RED)
        self.screen.blit(msg, (50, 60))
        
        for i, turtle in enumerate(self.roster):
            y_pos = 100 + (i * 120)
            pygame.draw.rect(self.screen, GRAY, (50, y_pos, 200, 100), 2)
            
            if turtle:
                name_txt = self.font.render(f"{turtle.name}", True, WHITE)
                # Accessing the stats dictionary from the shared class
                stats_str = f"Spd:{turtle.stats['speed']} Nrg:{turtle.stats['max_energy']} Rec:{turtle.stats['recovery']}"
                stats_txt = self.font.render(stats_str, True, WHITE)
                
                # Draw Energy Bar (Static View)
                pygame.draw.rect(self.screen, RED, (300, y_pos + 40, 100, 10))
                pygame.draw.rect(self.screen, GREEN, (300, y_pos + 40, 100, 10)) # Full in menu
                
                self.screen.blit(name_txt, (60, y_pos + 10))
                self.screen.blit(stats_txt, (60, y_pos + 70))
                
                # Retire Hint
                retire_txt = self.font.render(f"[Press {4+i} to Retire]", True, GRAY)
                self.screen.blit(retire_txt, (580, y_pos + 40))
            else:
                empty_txt = self.font.render("[ EMPTY SLOT ]", True, GRAY)
                self.screen.blit(empty_txt, (60, y_pos + 40))

    def draw_race(self):
        header = self.font.render(f"RACE (Speed: {self.race_speed_multiplier}x)", True, WHITE)
        self.screen.blit(header, (20, 20))
        
        # Draw Finish Line
        pygame.draw.line(self.screen, WHITE, (self.track_length_pixels + 40, 50), (self.track_length_pixels + 40, 500), 5)
        
        for i, turtle in enumerate(self.roster):
            lane_y = 150 + (i * 100)
            pygame.draw.rect(self.screen, (30, 30, 30), (0, lane_y - 20, SCREEN_WIDTH, 80))
            
            if turtle:
                self.draw_turtle_sprite(turtle, lane_y)

    def draw_race_result(self):
        title = self.font.render("RACE RESULTS (Press M for Menu)", True, WHITE)
        self.screen.blit(title, (20, 20))
        
        for i, turtle in enumerate(self.race_results):
            y_pos = 100 + (i * 60)
            color = WHITE
            if turtle == self.roster[0]: color = GREEN # Highlight Player
            
            txt = self.font.render(f"{i+1}. {turtle.name}", True, color)
            self.screen.blit(txt, (100, y_pos))
            
        # Show Reward info if player finished
        player = self.roster[0]
        if player and player.rank:
            reward_txt = self.font.render(f"You finished #{player.rank}!", True, GREEN)
            self.screen.blit(reward_txt, (100, 350))

    def draw_shop(self):
        title = self.font.render(f"TURTLE SHOP (Press M for Menu) | Money: ${self.money}", True, WHITE)
        self.screen.blit(title, (20, 20))
        
        msg = self.font.render("Press 1, 2, 3 to Buy ($50) | Press R to Refresh ($5)", True, GREEN)
        self.screen.blit(msg, (50, 60))
        
        # Feedback Message
        if self.shop_message:
            feedback = self.font.render(self.shop_message, True, (255, 255, 0))
            self.screen.blit(feedback, (400, 60))

        for i, turtle in enumerate(self.shop_inventory):
            x_pos = 50 + (i * 250)
            y_pos = 120
            
            # Draw Card
            pygame.draw.rect(self.screen, GRAY, (x_pos, y_pos, 220, 300), 2)
            
            name_txt = self.font.render(turtle.name, True, WHITE)
            stats_txt = self.font.render(f"Spd: {turtle.stats['speed']}", True, WHITE)
            cost_txt = self.font.render("$50", True, GREEN)
            
            self.screen.blit(name_txt, (x_pos + 20, y_pos + 20))
            self.screen.blit(stats_txt, (x_pos + 20, y_pos + 60))
            self.screen.blit(cost_txt, (x_pos + 20, y_pos + 250))

    def refresh_shop(self, free=False):
        cost = 5
        if free or self.money >= cost:
            if not free: self.money -= cost
            self.shop_inventory = [
                generate_random_turtle(level=1),
                generate_random_turtle(level=2),
                generate_random_turtle(level=3)
            ]
            self.shop_message = "Shop Refreshed!"
            self.shop_message_timer = 60
        else:
            self.shop_message = "Not enough money!"
            self.shop_message_timer = 60

    def buy_turtle(self, index):
        if index < len(self.shop_inventory):
            cost = 50
            if self.money >= cost:
                # Find empty slot in roster
                for i in range(len(self.roster)):
                    if self.roster[i] is None:
                        self.roster[i] = self.shop_inventory.pop(index)
                        self.money -= cost
                        self.shop_message = "Bought turtle!"
                        self.shop_message_timer = 60
                        return
                self.shop_message = "Roster Full!"
                self.shop_message_timer = 60
            else:
                self.shop_message = "Not enough money!"
                self.shop_message_timer = 60

    def retire_turtle(self, index):
        if self.roster[index] is not None:
            t = self.roster[index]
            self.roster[index] = None
            self.retired_roster.append(t)
            print(f"Retired {t.name}")

    def draw_breeding(self):
        title = self.font.render("BREEDING CENTER (Press M for Menu)", True, WHITE)
        self.screen.blit(title, (20, 20))
        
        msg = self.font.render("Select 2 Parents (Press 1, 2, 3...) then ENTER to Breed", True, GREEN)
        self.screen.blit(msg, (50, 60))
        
        # Draw Retired Roster
        for i, turtle in enumerate(self.retired_roster):
            y_pos = 120 + (i * 80)
            color = GRAY
            if turtle in self.breeding_parents: color = GREEN # Highlight Selected
            
            pygame.draw.rect(self.screen, color, (50, y_pos, 600, 60), 2)
            txt = self.font.render(f"{i+1}. {turtle.name} (Spd:{turtle.stats['speed']})", True, WHITE)
            self.screen.blit(txt, (70, y_pos + 15))

    def toggle_breeding_parent(self, index):
        if index < len(self.retired_roster):
            t = self.retired_roster[index]
            if t in self.breeding_parents:
                self.breeding_parents.remove(t)
            else:
                if len(self.breeding_parents) < 2:
                    self.breeding_parents.append(t)

    def breed(self):
        if len(self.breeding_parents) == 2:
            # Check for empty slot
            slot_idx = -1
            for i in range(len(self.roster)):
                if self.roster[i] is None:
                    slot_idx = i
                    break
            
            if slot_idx != -1:
                parent_a = self.breeding_parents[0]
                parent_b = self.breeding_parents[1]
                
                child = breed_turtles(parent_a, parent_b)
                self.roster[slot_idx] = child
                
                # Remove parents from retired roster
                self.retired_roster.remove(parent_a)
                self.retired_roster.remove(parent_b)
                self.breeding_parents = []
                
                print(f"Bred {child.name}!")
                self.state = STATE_MENU
            else:
                print("No Roster Space!")

    # --- HELPER: Draw the shared entity using PyGame ---
    def draw_turtle_sprite(self, turtle, y_pos):
        # Convert Logical Distance (1500) to Screen Pixels (700)
        screen_x = (turtle.race_distance / self.track_length_logic) * self.track_length_pixels
        
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