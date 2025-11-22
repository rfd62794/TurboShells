import pygame
from settings import *
import ui.layout as layout
from ui.menu_view import draw_menu as draw_main_menu_view
from ui.roster_view import draw_roster as draw_menu_view
from ui.race_view import draw_race as draw_race_view, draw_race_result as draw_race_result_view
from ui.shop_view import draw_shop as draw_shop_view
from ui.breeding_view import draw_breeding as draw_breeding_view

class Renderer:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font

    def draw_main_menu(self, game_state):
        draw_main_menu_view(self.screen, self.font, game_state)

    def draw_menu(self, game_state):
        draw_menu_view(self.screen, self.font, game_state)

    def draw_race(self, game_state):
        draw_race_view(self.screen, self.font, game_state)

    def draw_race_result(self, game_state):
        draw_race_result_view(self.screen, self.font, game_state)

    def draw_shop(self, game_state):
        draw_shop_view(self.screen, self.font, game_state)

    def draw_breeding(self, game_state):
        draw_breeding_view(self.screen, self.font, game_state)

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
