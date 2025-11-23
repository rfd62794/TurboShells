import pygame
from settings import *
import ui.layouts.positions as layout
from ui.turtle_card import format_turtle_label_basic


def draw_shop(screen, font, game_state):
    # Header with back button (like voting view)
    pygame.draw.rect(screen, DARK_GREY, layout.HEADER_RECT)
    title = font.render("TURTLE SHOP", True, WHITE)
    screen.blit(title, layout.HEADER_TITLE_POS)

    money_txt = font.render(f"$ {game_state.money}", True, WHITE)
    screen.blit(money_txt, layout.HEADER_MONEY_POS)
    
    # Back button in header (like voting view)
    back_rect = pygame.Rect(700, 5, 80, 30)
    mouse_pos = getattr(game_state, 'mouse_pos', None)
    back_color = (150, 50, 50) if mouse_pos and back_rect.collidepoint(mouse_pos) else (100, 100, 100)
    
    pygame.draw.rect(screen, back_color, back_rect)
    pygame.draw.rect(screen, (200, 200, 200), back_rect, 2)
    
    back_text = font.render("BACK", True, WHITE)
    text_x = back_rect.x + (back_rect.width - back_text.get_width()) // 2
    text_y = back_rect.y + (back_rect.height - back_text.get_height()) // 2
    screen.blit(back_text, (text_x, text_y))
    
    # Store back rect for click handling
    game_state.shop_back_rect = back_rect

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

        # Draw larger turtle image at top using universal renderer
        try:
            from core.rendering.pygame_turtle_renderer import render_turtle_pygame
            # Generate larger turtle image (80x80) for bigger boxes
            turtle_img = render_turtle_pygame(turtle, size=80)
            img_x = card_rect.x + (card_rect.width - 80) // 2
            img_y = card_rect.y + 15
            screen.blit(turtle_img, (img_x, img_y))
        except:
            # Fallback: draw a simple colored square
            pygame.draw.rect(screen, (100, 150, 200), 
                           (card_rect.x + (card_rect.width - 80) // 2, card_rect.y + 15, 80, 80))

        # Name below image (moved down)
        name_txt = font.render(turtle.name, True, WHITE)
        name_x = card_rect.x + (card_rect.width - name_txt.get_width()) // 2
        screen.blit(name_txt, (name_x, card_rect.y + 110))

        # Vertical stats layout (moved down further)
        stats_lines = [
            f"Speed: {turtle.stats['speed']}",
            f"Energy: {turtle.stats['max_energy']}",
            f"Recovery: {turtle.stats['recovery']}",
            f"Swim: {turtle.stats['swim']}",
            f"Climb: {turtle.stats['climb']}"
        ]
        
        y_offset = card_rect.y + 150  # Moved down for larger images
        for line in stats_lines:
            stat_txt = font.render(line, True, WHITE)
            stat_x = card_rect.x + (card_rect.width - stat_txt.get_width()) // 2
            screen.blit(stat_txt, (stat_x, y_offset))
            y_offset += 25

        # Energy bar (moved down)
        energy_bg = pygame.Rect(card_rect.x + 20, card_rect.y + 280, 180, 15)
        pygame.draw.rect(screen, (50, 50, 50), energy_bg)
        
        energy_fill_width = int((turtle.energy / turtle.max_energy) * 176)
        if energy_fill_width > 0:
            energy_fill = pygame.Rect(card_rect.x + 22, card_rect.y + 282, energy_fill_width, 11)
            pygame.draw.rect(screen, GREEN, energy_fill)

        # Cost at bottom - better alignment (moved down)
        cost_val = getattr(turtle, "shop_cost", 50)
        cost_txt = font.render(f"${cost_val}", True, GREEN)
        cost_x = card_rect.x + (card_rect.width - cost_txt.get_width()) // 2
        # Position cost just above the BUY button (moved down)
        cost_y = card_rect.y + 310
        screen.blit(cost_txt, (cost_x, cost_y))

        # BUY button (moved down)
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

    # Refresh button at bottom only (back button is now in header)
    pygame.draw.rect(screen, BLUE, layout.SHOP_BTN_REFRESH_RECT, 2)
    refresh_txt = font.render("REFRESH ($5)", True, WHITE)
    screen.blit(refresh_txt, (layout.SHOP_BTN_REFRESH_RECT.x + 15, layout.SHOP_BTN_REFRESH_RECT.y + 15))
