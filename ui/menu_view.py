import pygame
from settings import *
import ui.layouts.positions as layout


def draw_menu(screen, font, game_state):
    """Draw the main menu with game options"""
    # Header bar
    pygame.draw.rect(screen, DARK_GREY, layout.HEADER_RECT)
    title = font.render("TURBO SHELLS", True, WHITE)
    screen.blit(title, layout.HEADER_TITLE_POS)

    money_txt = font.render(f"Money: ${game_state.money}", True, WHITE)
    screen.blit(money_txt, layout.HEADER_MONEY_POS)

    mouse_pos = getattr(game_state, "mouse_pos", None)

    # Main menu options
    menu_options = [
        ("ROSTER", "Manage your turtles", layout.MENU_ROSTER_RECT),
        ("SHOP", "Buy new turtles", layout.MENU_SHOP_RECT),
        ("BREEDING", "Breed turtles", layout.MENU_BREEDING_RECT),
        ("RACE", "Start a race", layout.MENU_RACE_RECT),
        ("VOTING", "Design voting & rewards", layout.MENU_VOTING_RECT),
        ("SETTINGS", "Configure game settings", layout.MENU_SETTINGS_RECT),
    ]

    for i, (title, desc, rect) in enumerate(menu_options):
        menu_rect = rect

        # Hover effect
        color = GRAY
        if mouse_pos and menu_rect.collidepoint(mouse_pos):
            color = WHITE

        pygame.draw.rect(screen, color, menu_rect, 2)

        # Title
        title_txt = font.render(title, True, WHITE)
        title_x = menu_rect.x + (menu_rect.width - title_txt.get_width()) // 2
        screen.blit(title_txt, (title_x, menu_rect.y + 20))

        # Description
        desc_font = pygame.font.SysFont("Arial", 18)
        desc_txt = desc_font.render(desc, True, GRAY)
        desc_x = menu_rect.x + (menu_rect.width - desc_txt.get_width()) // 2
        screen.blit(desc_txt, (desc_x, menu_rect.y + 45))

    # Instructions
    inst_font = pygame.font.SysFont("Arial", 16)
    inst_txt = inst_font.render("Click an option or use keyboard shortcuts", True, GRAY)
    inst_x = (SCREEN_WIDTH - inst_txt.get_width()) // 2
    screen.blit(inst_txt, (inst_x, SCREEN_HEIGHT - 50))
