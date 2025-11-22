import pygame
from settings import *
import ui.layout as layout
from ui.turtle_card import draw_stable_turtle_slot


def draw_roster(screen, font, game_state):
    # Header bar
    pygame.draw.rect(screen, DARK_GREY, layout.HEADER_RECT)
    title = font.render("ROSTER", True, WHITE)
    screen.blit(title, layout.HEADER_TITLE_POS)

    money_txt = font.render(f"$ {game_state.money}", True, WHITE)
    screen.blit(money_txt, layout.HEADER_MONEY_POS)

    # Menu button in header
    mouse_pos = getattr(game_state, "mouse_pos", None)
    menu_color = GREEN
    if mouse_pos:
        menu_rect = pygame.Rect(700, 5, 80, 30)
        if menu_rect.collidepoint(mouse_pos):
            menu_color = WHITE
        pygame.draw.rect(screen, menu_color, menu_rect, 2)
        menu_txt = font.render("MENU", True, WHITE)
        menu_x = menu_rect.x + (menu_rect.width - menu_txt.get_width()) // 2
        screen.blit(menu_txt, (menu_x, menu_rect.y + 5))

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

        # Train button (only for active roster turtles)
        if turtle and is_active_racer and not show_retired:
            train_btn = layout.SLOT_BTN_TRAIN_RECT
            train_rect = pygame.Rect(slot_rect.x + train_btn.x, slot_rect.y + train_btn.y, train_btn.width, train_btn.height)

            # Hover highlight for train button
            train_color = GRAY
            if mouse_pos and train_rect.collidepoint(mouse_pos):
                train_color = WHITE

            pygame.draw.rect(screen, train_color, train_rect, 2)
            train_txt = font.render("TRAIN", True, WHITE)
            screen.blit(train_txt, (train_rect.x + 15, train_rect.y + 5))

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
