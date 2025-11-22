import pygame
from settings import *
import ui.layout as layout

class Renderer:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font

    def draw_menu(self, game_state):
        # Header bar
        pygame.draw.rect(self.screen, DARK_GREY, layout.HEADER_RECT)
        title = self.font.render("STABLE MENU", True, WHITE)
        self.screen.blit(title, layout.HEADER_TITLE_POS)

        money_txt = self.font.render(f"$ {game_state.money}", True, WHITE)
        self.screen.blit(money_txt, layout.HEADER_MONEY_POS)

        # Keyboard hint (kept for now, but UI is primary)
        msg = self.font.render("Q/W/E: Train | Z/X/C: Rest | 4/5/6: Retire", True, GRAY)
        self.screen.blit(msg, (layout.PADDING, layout.HEADER_RECT.bottom + 5))

        # Roster slots
        for idx, slot_rect in enumerate(layout.SLOT_RECTS):
            border_color = GREEN if idx == getattr(game_state, "active_racer_index", 0) else GRAY
            pygame.draw.rect(self.screen, border_color, slot_rect, 2)

            turtle = game_state.roster[idx]

            if turtle:
                # Name
                name_pos = (slot_rect.x + layout.SLOT_NAME_POS[0], slot_rect.y + layout.SLOT_NAME_POS[1])
                name_txt = self.font.render(turtle.name, True, WHITE)
                self.screen.blit(name_txt, name_pos)

                # Stats text
                stats_pos = (slot_rect.x + layout.SLOT_STATS_POS[0], slot_rect.y + layout.SLOT_STATS_POS[1])
                stats_str = (
                    f"Spd:{turtle.stats['speed']} "
                    f"Nrg:{turtle.stats['max_energy']} "
                    f"Rec:{turtle.stats['recovery']} "
                    f"Swm:{turtle.stats['swim']} "
                    f"Clm:{turtle.stats['climb']}"
                )
                stats_txt = self.font.render(stats_str, True, WHITE)
                self.screen.blit(stats_txt, stats_pos)

                # Energy bar
                energy_bg = layout.SLOT_ENERGY_BG_RECT
                energy_bg_rect = pygame.Rect(
                    slot_rect.x + energy_bg.x,
                    slot_rect.y + energy_bg.y,
                    energy_bg.width,
                    energy_bg.height,
                )
                pygame.draw.rect(self.screen, RED, energy_bg_rect)

                pct = turtle.current_energy / turtle.stats["max_energy"] if turtle.stats["max_energy"] > 0 else 0
                fill_width = int(energy_bg.width * max(0.0, min(1.0, pct)))
                energy_fill_rect = pygame.Rect(
                    energy_bg_rect.x + 2,
                    energy_bg_rect.y + 2,
                    max(0, fill_width - 4),
                    energy_bg.height - 4,
                )
                pygame.draw.rect(self.screen, GREEN, energy_fill_rect)
            else:
                empty_txt = self.font.render("[ EMPTY SLOT ]", True, GRAY)
                self.screen.blit(empty_txt, (slot_rect.x + 20, slot_rect.y + 40))

            # Action buttons (visual only; click handling is in RosterManager)
            train_btn = layout.SLOT_BTN_TRAIN_RECT
            rest_btn = layout.SLOT_BTN_REST_RECT
            retire_btn = layout.SLOT_BTN_RETIRE_RECT

            train_rect = pygame.Rect(slot_rect.x + train_btn.x, slot_rect.y + train_btn.y, train_btn.width, train_btn.height)
            rest_rect = pygame.Rect(slot_rect.x + rest_btn.x, slot_rect.y + rest_btn.y, rest_btn.width, rest_btn.height)
            retire_rect = pygame.Rect(slot_rect.x + retire_btn.x, slot_rect.y + retire_btn.y, retire_btn.width, retire_btn.height)

            pygame.draw.rect(self.screen, GRAY, train_rect, 2)
            pygame.draw.rect(self.screen, GRAY, rest_rect, 2)
            pygame.draw.rect(self.screen, GRAY, retire_rect, 2)

            train_txt = self.font.render("TRAIN", True, WHITE)
            rest_txt = self.font.render("REST", True, WHITE)
            retire_txt = self.font.render("RETIRE", True, WHITE)

            self.screen.blit(train_txt, (train_rect.x + 10, train_rect.y + 5))
            self.screen.blit(rest_txt, (rest_rect.x + 10, rest_rect.y + 5))
            self.screen.blit(retire_txt, (retire_rect.x + 10, retire_rect.y + 5))

        # Bottom navigation buttons
        pygame.draw.rect(self.screen, GREEN, layout.NAV_RACE_RECT, 2)
        pygame.draw.rect(self.screen, (200, 100, 200), layout.NAV_BREED_RECT, 2)
        pygame.draw.rect(self.screen, BLUE, layout.NAV_SHOP_RECT, 2)

        race_txt = self.font.render("RACE", True, WHITE)
        breed_txt = self.font.render("BREEDING", True, WHITE)
        shop_txt = self.font.render("SHOP", True, WHITE)

        self.screen.blit(race_txt, (layout.NAV_RACE_RECT.x + 40, layout.NAV_RACE_RECT.y + 15))
        self.screen.blit(breed_txt, (layout.NAV_BREED_RECT.x + 20, layout.NAV_BREED_RECT.y + 15))
        self.screen.blit(shop_txt, (layout.NAV_SHOP_RECT.x + 50, layout.NAV_SHOP_RECT.y + 15))

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
        title = self.font.render("RACE RESULTS", True, WHITE)
        self.screen.blit(title, layout.HEADER_TITLE_POS)
        
        active_idx = getattr(game_state, "active_racer_index", 0)
        player_turtle = None
        if 0 <= active_idx < len(game_state.roster):
            player_turtle = game_state.roster[active_idx]

        for i, turtle in enumerate(game_state.race_results):
            y_pos = 100 + (i * 60)
            color = WHITE
            if turtle == player_turtle: color = GREEN
            
            txt = self.font.render(f"{i+1}. {turtle.name}", True, color)
            self.screen.blit(txt, (100, y_pos))
            
        # Show Reward info if player finished
        if player_turtle and player_turtle.rank:
            reward_txt = self.font.render(f"You finished #{player_turtle.rank}!", True, GREEN)
            self.screen.blit(reward_txt, (100, 350))

        # Buttons: Menu and Race Again
        pygame.draw.rect(self.screen, GREEN, layout.RACE_RESULT_MENU_BTN_RECT, 2)
        pygame.draw.rect(self.screen, BLUE, layout.RACE_RESULT_RERUN_BTN_RECT, 2)

        menu_txt = self.font.render("MENU", True, WHITE)
        rerun_txt = self.font.render("RACE AGAIN", True, WHITE)

        self.screen.blit(menu_txt, (layout.RACE_RESULT_MENU_BTN_RECT.x + 60, layout.RACE_RESULT_MENU_BTN_RECT.y + 15))
        self.screen.blit(rerun_txt, (layout.RACE_RESULT_RERUN_BTN_RECT.x + 25, layout.RACE_RESULT_RERUN_BTN_RECT.y + 15))

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
