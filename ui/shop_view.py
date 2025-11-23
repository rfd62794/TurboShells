import pygame
from settings import *
import ui.layouts.positions as layout
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

        # Draw tiny turtle image at top using universal renderer
        try:
            from core.rendering.pygame_turtle_renderer import render_turtle_pygame
            # Generate tiny turtle image (40x40) using universal renderer
            turtle_img = render_turtle_pygame(turtle, size=40)
            img_x = card_rect.x + (card_rect.width - 40) // 2
            img_y = card_rect.y + 10
            screen.blit(turtle_img, (img_x, img_y))
        except:
            # Fallback: draw a simple colored square
            pygame.draw.rect(screen, (100, 150, 200), 
                           (card_rect.x + (card_rect.width - 40) // 2, card_rect.y + 10, 40, 40))

        # Name below image
        name_txt = font.render(turtle.name, True, WHITE)
        name_x = card_rect.x + (card_rect.width - name_txt.get_width()) // 2
        screen.blit(name_txt, (name_x, card_rect.y + 60))

        # Vertical stats layout
        stats_lines = [
            f"Speed: {turtle.stats['speed']}",
            f"Energy: {turtle.stats['max_energy']}",
            f"Recovery: {turtle.stats['recovery']}",
            f"Swim: {turtle.stats['swim']}",
            f"Climb: {turtle.stats['climb']}"
        ]
        
        y_offset = card_rect.y + 90
        for line in stats_lines:
            stat_txt = font.render(line, True, WHITE)
            stat_x = card_rect.x + (card_rect.width - stat_txt.get_width()) // 2
            screen.blit(stat_txt, (stat_x, y_offset))
            y_offset += 25

        # Cost at bottom - better alignment
        cost_val = getattr(turtle, "shop_cost", 50)
        cost_txt = font.render(f"${cost_val}", True, GREEN)
        cost_x = card_rect.x + (card_rect.width - cost_txt.get_width()) // 2
        # Position cost just above the BUY button
        cost_y = card_rect.y + card_rect.height - 35
        screen.blit(cost_txt, (cost_x, cost_y))

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
