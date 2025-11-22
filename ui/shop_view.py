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

    # Feedback Message
    if game_state.shop_message:
        feedback = font.render(game_state.shop_message, True, (255, 255, 0))
        screen.blit(feedback, (layout.PADDING, layout.HEADER_RECT.bottom + 30))

    for i, turtle in enumerate(game_state.shop_inventory):
        if i >= len(layout.SHOP_SLOT_RECTS):
            break
            
        slot_rect = layout.SHOP_SLOT_RECTS[i]
        card_rect = slot_rect

        # Draw Card
        pygame.draw.rect(screen, GRAY, card_rect, 2)

        name_txt = font.render(turtle.name, True, WHITE)
        stats_txt = font.render(format_turtle_label_basic(turtle), True, WHITE)
        # Expect cost to be computed in ShopManager when needed; fall back to 50.
        cost_val = getattr(turtle, "shop_cost", 50)
        cost_txt = font.render(f"${cost_val}", True, GREEN)

        screen.blit(name_txt, (card_rect.x + 20, card_rect.y + 20))
        screen.blit(stats_txt, (card_rect.x + 20, card_rect.y + 60))
        screen.blit(cost_txt, (card_rect.x + 20, card_rect.y + 250))

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
        # Move Buy text to right side of button
        buy_x = buy_rect.x + buy_rect.width - buy_txt.get_width() - 10
        screen.blit(buy_txt, (buy_x, buy_rect.y + 8))

    # Shop controls: Refresh and Back to Menu buttons
    pygame.draw.rect(screen, BLUE, layout.SHOP_BTN_REFRESH_RECT, 2)
    pygame.draw.rect(screen, GREEN, layout.SHOP_BTN_BACK_RECT, 2)

    refresh_txt = font.render("REFRESH ($5)", True, WHITE)
    back_txt = font.render("MENU", True, WHITE)

    screen.blit(refresh_txt, (layout.SHOP_BTN_REFRESH_RECT.x + 15, layout.SHOP_BTN_REFRESH_RECT.y + 15))
    screen.blit(back_txt, (layout.SHOP_BTN_BACK_RECT.x + 70, layout.SHOP_BTN_BACK_RECT.y + 15))
