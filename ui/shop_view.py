import pygame
from settings import *
import ui.layout as layout
from ui.turtle_card import format_turtle_label_basic


def draw_shop(screen, font, game_state):
    # Header
    pygame.draw.rect(screen, DARK_GREY, layout.HEADER_RECT)
    title = font.render("TURTLE SHOP", True, WHITE)
    screen.blit(title, layout.HEADER_TITLE_POS)

    money_txt = font.render(f"$ {game_state.money}", True, WHITE)
    screen.blit(money_txt, layout.HEADER_MONEY_POS)

    # Small debug hint for keyboard shortcuts
    msg = font.render("[DBG] 1-3: Buy | R: Refresh | M: Menu", True, GRAY)
    screen.blit(msg, (layout.PADDING, layout.HEADER_RECT.bottom + 5))

    # Feedback Message
    if game_state.shop_message:
        feedback = font.render(game_state.shop_message, True, (255, 255, 0))
        screen.blit(feedback, (layout.PADDING, layout.HEADER_RECT.bottom + 30))

    for i, turtle in enumerate(game_state.shop_inventory):
        x_pos = 50 + (i * 250)
        y_pos = 120

        card_rect = pygame.Rect(x_pos, y_pos, 220, 300)

        # Draw Card
        pygame.draw.rect(screen, GRAY, card_rect, 2)

        name_txt = font.render(turtle.name, True, WHITE)
        stats_txt = font.render(format_turtle_label_basic(turtle), True, WHITE)
        # Expect cost to be computed in ShopManager when needed; fall back to 50.
        cost_val = getattr(turtle, "shop_cost", 50)
        cost_txt = font.render(f"${cost_val}", True, GREEN)

        screen.blit(name_txt, (x_pos + 20, y_pos + 20))
        screen.blit(stats_txt, (x_pos + 20, y_pos + 60))
        screen.blit(cost_txt, (x_pos + 20, y_pos + 250))

        # BUY button (visual) using layout.SHOP_BTN_BUY_RECT (relative to card)
        buy_rel = layout.SHOP_BTN_BUY_RECT
        buy_rect = pygame.Rect(
            card_rect.x + buy_rel.x,
            card_rect.y + buy_rel.y,
            buy_rel.width,
            buy_rel.height,
        )
        pygame.draw.rect(screen, GREEN, buy_rect, 2)

        buy_txt = font.render("BUY", True, WHITE)
        screen.blit(buy_txt, (buy_rect.x + 40, buy_rect.y + 8))

    # Shop controls: Refresh and Back to Menu buttons
    pygame.draw.rect(screen, BLUE, layout.SHOP_BTN_REFRESH_RECT, 2)
    pygame.draw.rect(screen, GREEN, layout.SHOP_BTN_BACK_RECT, 2)

    refresh_txt = font.render("REFRESH ($5)", True, WHITE)
    back_txt = font.render("MENU", True, WHITE)

    screen.blit(refresh_txt, (layout.SHOP_BTN_REFRESH_RECT.x + 15, layout.SHOP_BTN_REFRESH_RECT.y + 15))
    screen.blit(back_txt, (layout.SHOP_BTN_BACK_RECT.x + 70, layout.SHOP_BTN_BACK_RECT.y + 15))
