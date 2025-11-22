import pygame
from settings import *
import ui.layout as layout
from ui.turtle_card import draw_stable_turtle_slot


def draw_roster(screen, font, game_state):
    # Header bar
    pygame.draw.rect(screen, DARK_GREY, layout.HEADER_RECT)
    title = font.render("STABLE MENU", True, WHITE)
    screen.blit(title, layout.HEADER_TITLE_POS)

    money_txt = font.render(f"$ {game_state.money}", True, WHITE)
    screen.blit(money_txt, layout.HEADER_MONEY_POS)

    mouse_pos = getattr(game_state, "mouse_pos", None)

    # Determine which turtles to show: Active roster or Retired pool
    show_retired = getattr(game_state, "show_retired_view", False)
    if show_retired:
        turtles_to_show = list(game_state.retired_roster[:3])
        # Pad to length 3 for consistent UI
        while len(turtles_to_show) < 3:
            turtles_to_show.append(None)
    else:
        turtles_to_show = list(game_state.roster)

    # Roster slots
    for idx, slot_rect in enumerate(layout.SLOT_RECTS):
        turtle = turtles_to_show[idx]
        is_active_racer = (not show_retired) and idx == getattr(game_state, "active_racer_index", 0)
        draw_stable_turtle_slot(screen, font, game_state, turtle, slot_rect, is_active_racer, mouse_pos)

    # Bottom navigation buttons with hover
    nav_menu_color = GREEN
    nav_shop_color = BLUE
    nav_breed_color = (200, 100, 200)
    if mouse_pos:
        if layout.NAV_MENU_RECT.collidepoint(mouse_pos):
            nav_menu_color = WHITE
        if layout.NAV_SHOP_RECT.collidepoint(mouse_pos):
            nav_shop_color = WHITE
        if layout.NAV_BREED_RECT.collidepoint(mouse_pos):
            nav_breed_color = WHITE

    pygame.draw.rect(screen, nav_menu_color, layout.NAV_MENU_RECT, 2)
    pygame.draw.rect(screen, nav_shop_color, layout.NAV_SHOP_RECT, 2)
    pygame.draw.rect(screen, nav_breed_color, layout.NAV_BREED_RECT, 2)

    menu_txt = font.render("MENU", True, WHITE)
    shop_txt = font.render("SHOP", True, WHITE)
    breed_txt = font.render("BREEDING", True, WHITE)

    screen.blit(menu_txt, (layout.NAV_MENU_RECT.x + 60, layout.NAV_MENU_RECT.y + 15))
    screen.blit(shop_txt, (layout.NAV_SHOP_RECT.x + 60, layout.NAV_SHOP_RECT.y + 15))
    screen.blit(breed_txt, (layout.NAV_BREED_RECT.x + 35, layout.NAV_BREED_RECT.y + 15))

    # View toggle buttons: Active vs Retired
    show_retired = getattr(game_state, "show_retired_view", False)

    def draw_view_button(rect, label, selected):
        base_color = GREEN if selected else GRAY
        if mouse_pos and rect.collidepoint(mouse_pos):
            base_color = WHITE
        pygame.draw.rect(screen, base_color, rect, 2)
        txt = font.render(label, True, WHITE)
        screen.blit(txt, (rect.x + 10, rect.y + 10))

    draw_view_button(layout.VIEW_ACTIVE_RECT, "ACTIVE", not show_retired)
    draw_view_button(layout.VIEW_RETIRED_RECT, "RETIRED", show_retired)

    # Betting buttons (MVP): None, $5, $10
    current_bet = getattr(game_state, "current_bet", 0)

    def draw_bet_button(rect, label, amount):
        base_color = GRAY
        if current_bet == amount:
            base_color = GREEN
        if mouse_pos and rect.collidepoint(mouse_pos):
            base_color = WHITE
        pygame.draw.rect(screen, base_color, rect, 2)
        txt = font.render(label, True, WHITE)
        screen.blit(txt, (rect.x + 10, rect.y + 10))

    draw_bet_button(layout.BET_BTN_NONE_RECT, "BET: $0", 0)
    draw_bet_button(layout.BET_BTN_5_RECT, "BET: $5", 5)
    draw_bet_button(layout.BET_BTN_10_RECT, "BET: $10", 10)
