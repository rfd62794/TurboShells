import pygame
from settings import *
import ui.layout as layout

class Renderer:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font

    def draw_menu(self, game_state):
        title = self.font.render(f"STABLE MENU (R=Race, S=Shop, B=Breed) | Money: ${game_state.money}", True, WHITE)
        self.screen.blit(title, layout.HEADER_TITLE_POS)
        
        msg = self.font.render("Press 4-6 to Retire | Q-E to Train | Z-C to Rest", True, GRAY)
        self.screen.blit(msg, (50, 60))
        
        for i, turtle in enumerate(game_state.roster):
            y_pos = 100 + (i * 120)
            pygame.draw.rect(self.screen, GRAY, (50, y_pos, 200, 100), 2)
            
            if turtle:
                name_txt = self.font.render(f"{turtle.name}", True, WHITE)
                # Accessing the stats dictionary from the shared class
                stats_str = f"Spd:{turtle.stats['speed']} Nrg:{turtle.stats['max_energy']} Rec:{turtle.stats['recovery']}"
                stats_txt = self.font.render(stats_str, True, WHITE)
                
                # Draw Energy Bar (Static View)
                pygame.draw.rect(self.screen, RED, (300, y_pos + 40, 100, 10))
                # Calculate width based on current energy
                pct = turtle.current_energy / turtle.stats['max_energy']
                pygame.draw.rect(self.screen, GREEN, (300, y_pos + 40, int(100 * pct), 10))
                
                self.screen.blit(name_txt, (60, y_pos + 10))
                self.screen.blit(stats_txt, (60, y_pos + 70))
                
                # Controls Hint
                controls_txt = self.font.render(f"[Q: Train] [Z: Rest] [{4+i}: Retire]", True, GRAY)
                self.screen.blit(controls_txt, (450, y_pos + 40))
            else:
                empty_txt = self.font.render("[ EMPTY SLOT ]", True, GRAY)
                self.screen.blit(empty_txt, (60, y_pos + 40))

    def draw_race(self, game_state):
        header = self.font.render(f"RACE (Speed: {game_state.race_speed_multiplier}x)", True, WHITE)
        self.screen.blit(header, layout.HEADER_TITLE_POS)

        # Draw Finish Line
        pygame.draw.line(self.screen, WHITE, (TRACK_LENGTH_PIXELS + 40, 50), (TRACK_LENGTH_PIXELS + 40, 500), 5)

        # Draw lanes and turtles
        for i, turtle in enumerate(game_state.roster):
            lane_y = 150 + (i * 100)
            pygame.draw.rect(self.screen, (30, 30, 30), (0, lane_y - 20, SCREEN_WIDTH, 80))

            if turtle:
                self.draw_turtle_sprite(turtle, lane_y)

        # Draw Race HUD panel
        pygame.draw.rect(self.screen, (0, 0, 0), layout.RACE_HUD_RECT)

        # Speed buttons
        pygame.draw.rect(self.screen, GRAY, layout.SPEED_1X_RECT, 2)
        pygame.draw.rect(self.screen, GRAY, layout.SPEED_2X_RECT, 2)
        pygame.draw.rect(self.screen, GRAY, layout.SPEED_4X_RECT, 2)

        one_txt = self.font.render("1x", True, WHITE)
        two_txt = self.font.render("2x", True, WHITE)
        four_txt = self.font.render("4x", True, WHITE)

        self.screen.blit(one_txt, (layout.SPEED_1X_RECT.x + 10, layout.SPEED_1X_RECT.y + 10))
        self.screen.blit(two_txt, (layout.SPEED_2X_RECT.x + 10, layout.SPEED_2X_RECT.y + 10))
        self.screen.blit(four_txt, (layout.SPEED_4X_RECT.x + 10, layout.SPEED_4X_RECT.y + 10))

        # Progress bar (simple overall race progress for player turtle)
        player = game_state.roster[0]
        pygame.draw.rect(self.screen, GRAY, layout.PROGRESS_BAR_RECT, 1)
        if player:
            pct = min(1.0, player.race_distance / TRACK_LENGTH_LOGIC)
            fill_width = int(layout.PROGRESS_BAR_RECT.width * pct)
            fill_rect = pygame.Rect(
                layout.PROGRESS_BAR_RECT.x,
                layout.PROGRESS_BAR_RECT.y,
                fill_width,
                layout.PROGRESS_BAR_RECT.height,
            )
            pygame.draw.rect(self.screen, GREEN, fill_rect)

    def draw_race_result(self, game_state):
        title = self.font.render("RACE RESULTS (Press M for Menu)", True, WHITE)
        self.screen.blit(title, layout.HEADER_TITLE_POS)
        
        for i, turtle in enumerate(game_state.race_results):
            y_pos = 100 + (i * 60)
            color = WHITE
            if turtle == game_state.roster[0]: color = GREEN # Highlight Player
            
            txt = self.font.render(f"{i+1}. {turtle.name}", True, color)
            self.screen.blit(txt, (100, y_pos))
            
        # Show Reward info if player finished
        player = game_state.roster[0]
        if player and player.rank:
            reward_txt = self.font.render(f"You finished #{player.rank}!", True, GREEN)
            self.screen.blit(reward_txt, (100, 350))

    def draw_shop(self, game_state):
        title = self.font.render(f"TURTLE SHOP (Press M for Menu) | Money: ${game_state.money}", True, WHITE)
        self.screen.blit(title, layout.HEADER_TITLE_POS)
        
        msg = self.font.render("Press 1, 2, 3 to Buy ($50) | Press R to Refresh ($5)", True, GREEN)
        self.screen.blit(msg, (50, 60))
        
        # Feedback Message
        if game_state.shop_message:
            feedback = self.font.render(game_state.shop_message, True, (255, 255, 0))
            self.screen.blit(feedback, (400, 60))

        for i, turtle in enumerate(game_state.shop_inventory):
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

    def draw_breeding(self, game_state):
        title = self.font.render("BREEDING CENTER (Press M for Menu)", True, WHITE)
        self.screen.blit(title, layout.HEADER_TITLE_POS)
        
        msg = self.font.render("Select 2 Parents (Press 1, 2, 3...) then ENTER to Breed", True, GREEN)
        self.screen.blit(msg, (50, 60))
        
        # Draw Retired Roster
        for i, turtle in enumerate(game_state.retired_roster):
            y_pos = 120 + (i * 80)
            color = GRAY
            if turtle in game_state.breeding_parents: color = GREEN # Highlight Selected
            
            pygame.draw.rect(self.screen, color, (50, y_pos, 600, 60), 2)
            txt = self.font.render(f"{i+1}. {turtle.name} (Spd:{turtle.stats['speed']})", True, WHITE)
            self.screen.blit(txt, (70, y_pos + 15))

    # --- HELPER: Draw the shared entity using PyGame ---
    def draw_turtle_sprite(self, turtle, y_pos):
        # Convert Logical Distance (1500) to Screen Pixels (700)
        screen_x = (turtle.race_distance / TRACK_LENGTH_LOGIC) * TRACK_LENGTH_PIXELS
        
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
