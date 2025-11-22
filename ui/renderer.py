import pygame
from settings import *
import ui.layout as layout
from ui.menu_view import draw_menu as draw_menu_view
from ui.race_view import draw_race as draw_race_view, draw_race_result as draw_race_result_view

class Renderer:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font

    def draw_menu(self, game_state):
        draw_menu_view(self.screen, self.font, game_state)

    def draw_race(self, game_state):
        draw_race_view(self.screen, self.font, game_state)

    def draw_race_result(self, game_state):
        draw_race_result_view(self.screen, self.font, game_state)

    def draw_shop(self, game_state):
        # Header
        pygame.draw.rect(self.screen, DARK_GREY, layout.HEADER_RECT)
        title = self.font.render(f"TURTLE SHOP", True, WHITE)
        self.screen.blit(title, layout.HEADER_TITLE_POS)

        money_txt = self.font.render(f"$ {game_state.money}", True, WHITE)
        self.screen.blit(money_txt, layout.HEADER_MONEY_POS)

        # Small debug hint for keyboard shortcuts
        msg = self.font.render("[DBG] 1-3: Buy | R: Refresh | M: Menu", True, GRAY)
        self.screen.blit(msg, (layout.PADDING, layout.HEADER_RECT.bottom + 5))
        
        # Feedback Message
        if game_state.shop_message:
            feedback = self.font.render(game_state.shop_message, True, (255, 255, 0))
            self.screen.blit(feedback, (layout.PADDING, layout.HEADER_RECT.bottom + 30))

        for i, turtle in enumerate(game_state.shop_inventory):
            x_pos = 50 + (i * 250)
            y_pos = 120

            card_rect = pygame.Rect(x_pos, y_pos, 220, 300)

            # Draw Card
            pygame.draw.rect(self.screen, GRAY, card_rect, 2)

            name_txt = self.font.render(turtle.name, True, WHITE)
            stats_txt = self.font.render(f"Spd: {turtle.stats['speed']}", True, WHITE)
            cost_txt = self.font.render("$50", True, GREEN)

            self.screen.blit(name_txt, (x_pos + 20, y_pos + 20))
            self.screen.blit(stats_txt, (x_pos + 20, y_pos + 60))
            self.screen.blit(cost_txt, (x_pos + 20, y_pos + 250))

            # BUY button (visual) using layout.SHOP_BTN_BUY_RECT (relative to card)
            buy_rel = layout.SHOP_BTN_BUY_RECT
            buy_rect = pygame.Rect(
                card_rect.x + buy_rel.x,
                card_rect.y + buy_rel.y,
                buy_rel.width,
                buy_rel.height,
            )
            pygame.draw.rect(self.screen, GREEN, buy_rect, 2)

            buy_txt = self.font.render("BUY", True, WHITE)
            self.screen.blit(buy_txt, (buy_rect.x + 40, buy_rect.y + 8))

        # Shop controls: Refresh and Back to Menu buttons
        pygame.draw.rect(self.screen, BLUE, layout.SHOP_BTN_REFRESH_RECT, 2)
        pygame.draw.rect(self.screen, GREEN, layout.SHOP_BTN_BACK_RECT, 2)

        refresh_txt = self.font.render("REFRESH ($5)", True, WHITE)
        back_txt = self.font.render("MENU", True, WHITE)

        self.screen.blit(refresh_txt, (layout.SHOP_BTN_REFRESH_RECT.x + 15, layout.SHOP_BTN_REFRESH_RECT.y + 15))
        self.screen.blit(back_txt, (layout.SHOP_BTN_BACK_RECT.x + 70, layout.SHOP_BTN_BACK_RECT.y + 15))

    def draw_breeding(self, game_state):
        title = self.font.render("BREEDING CENTER (Press M for Menu)", True, WHITE)
        self.screen.blit(title, layout.HEADER_TITLE_POS)
        
        msg = self.font.render("Select 2 Parents (Press 1, 2, 3...) then ENTER to Breed", True, GREEN)
        self.screen.blit(msg, (50, 60))
        
        # Combined breeding pool: active + retired
        candidates = [t for t in game_state.roster if t is not None] + list(game_state.retired_roster)

        for i, turtle in enumerate(candidates):
            y_pos = layout.BREEDING_LIST_START_Y + (i * layout.BREEDING_SLOT_HEIGHT)

            is_retired = not getattr(turtle, "is_active", True)
            base_color = RED if is_retired else GRAY

            # Selected parents stand out in green (active) or red (retired)
            if turtle in game_state.breeding_parents:
                color = GREEN if not is_retired else RED
            else:
                color = base_color

            row_rect = pygame.Rect(
                layout.BREEDING_ROW_X,
                y_pos,
                layout.BREEDING_ROW_WIDTH,
                layout.BREEDING_SLOT_HEIGHT,
            )
            pygame.draw.rect(self.screen, color, row_rect, 2)

            status_tag = "[RET]" if is_retired else "[ACT]"
            label = f"{i+1}. {turtle.name} {status_tag} (Spd:{turtle.stats['speed']})"
            txt = self.font.render(label, True, WHITE)
            self.screen.blit(txt, (row_rect.x + 20, row_rect.y + 15))

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
