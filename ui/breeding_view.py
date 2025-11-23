import pygame
from settings import *
import ui.layouts.positions as layout
from ui.turtle_card import draw_stable_turtle_slot


def draw_breeding(screen, font, game_state):
    # Header bar
    pygame.draw.rect(screen, DARK_GREY, layout.HEADER_RECT)
    title = font.render("BREEDING CENTER", True, WHITE)
    screen.blit(title, layout.HEADER_TITLE_POS)

    money_txt = font.render(f"$ {game_state.money}", True, WHITE)
    screen.blit(money_txt, layout.HEADER_MONEY_POS)

    mouse_pos = getattr(game_state, "mouse_pos", None)

    # Instructions
    msg = font.render("Select 2 Parents (Press 1, 2, 3...) then ENTER to Breed", True, GREEN)
    screen.blit(msg, (50, 60))

    # Combined breeding pool: active + retired
    candidates = [t for t in game_state.roster if t is not None] + list(game_state.retired_roster)

    # Draw turtle cards for breeding candidates
    for i, turtle in enumerate(candidates):
        if i >= 6:  # Limit to 6 candidates for display
            break
            
        # Create a card position
        card_x = 50 + (i % 3) * 230  # Further reduced spacing
        card_y = 120 + (i // 3) * 150
        card_rect = pygame.Rect(card_x, card_y, 200, 120)  # Slightly narrower cards

        # Determine if this turtle is selected
        is_selected = turtle in game_state.breeding_parents
        is_retired = turtle in game_state.retired_roster

        # Draw the turtle card
        draw_stable_turtle_slot(screen, font, game_state, turtle, card_rect, is_selected, mouse_pos)

        # Add selection indicator
        if is_selected:
            pygame.draw.rect(screen, GREEN, card_rect, 4)
            select_txt = font.render("SELECTED", True, GREEN)
            screen.blit(select_txt, (card_rect.x + 5, card_rect.y + 5))

    # Menu button
    menu_color = GREEN
    if mouse_pos and layout.BREED_BACK_BTN_RECT.collidepoint(mouse_pos):
        menu_color = WHITE
    pygame.draw.rect(screen, menu_color, layout.BREED_BACK_BTN_RECT, 2)
    menu_txt = font.render("MENU", True, WHITE)
    menu_x = layout.BREED_BACK_BTN_RECT.x + (layout.BREED_BACK_BTN_RECT.width - menu_txt.get_width()) // 2
    screen.blit(menu_txt, (menu_x, layout.BREED_BACK_BTN_RECT.y + 15))

    # Breed button (only if 2 parents selected)
    if len(game_state.breeding_parents) == 2:
        breed_color = GREEN
        if mouse_pos and layout.BREED_BTN_RECT.collidepoint(mouse_pos):
            breed_color = WHITE
        pygame.draw.rect(screen, breed_color, layout.BREED_BTN_RECT, 2)
        breed_txt = font.render("BREED", True, WHITE)
        breed_x = layout.BREED_BTN_RECT.x + (layout.BREED_BTN_RECT.width - breed_txt.get_width()) // 2
        screen.blit(breed_txt, (breed_x, layout.BREED_BTN_RECT.y + 15))
