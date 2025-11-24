import pygame
from settings import *
import ui.layouts.positions as layout


def draw_training(screen, font, game_state):
    """Draw the training interface"""
    # Header
    pygame.draw.rect(screen, DARK_GREY, layout.HEADER_RECT)
    title = font.render("TURTLE TRAINING", True, WHITE)
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

    # Get the selected turtle
    active_racer_index = getattr(game_state, "active_racer_index", 0)
    turtle = game_state.roster[active_racer_index]

    if not turtle:
        # No turtle selected
        no_turtle_txt = font.render("No turtle selected for training", True, GRAY)
        screen.blit(
            no_turtle_txt, (SCREEN_WIDTH // 2 - no_turtle_txt.get_width() // 2, 200)
        )
        return

    # Draw turtle info
    info_y = 100

    # Turtle name
    name_txt = font.render(f"Training: {turtle.name}", True, WHITE)
    screen.blit(name_txt, (50, info_y))

    # Current stats
    stats_y = info_y + 50
    stats_lines = [
        f"Speed: {turtle.stats['speed']}",
        f"Energy: {turtle.stats['max_energy']}",
        f"Recovery: {turtle.stats['recovery']}",
        f"Swim: {turtle.stats['swim']}",
        f"Climb: {turtle.stats['climb']}",
        f"Age: {turtle.age}",
    ]

    for i, line in enumerate(stats_lines):
        stat_txt = font.render(line, True, WHITE)
        screen.blit(stat_txt, (50, stats_y + i * 30))

    # Training options
    training_y = stats_y + len(stats_lines) * 30 + 50

    training_title = font.render("Training Options:", True, WHITE)
    screen.blit(training_title, (50, training_y))

    # Training buttons
    button_y = training_y + 50
    training_buttons = [
        ("Train Speed (+1)", "speed", 50, button_y),
        ("Train Energy (+1)", "energy", 300, button_y),
        ("Train Recovery (+1)", "recovery", 50, button_y + 60),
        ("Train Swim (+1)", "swim", 300, button_y + 60),
        ("Train Climb (+1)", "climb", 50, button_y + 120),
    ]

    for text, stat, x, y in training_buttons:
        button_rect = pygame.Rect(x, y, 200, 40)

        # Hover effect
        color = GREEN
        if mouse_pos and button_rect.collidepoint(mouse_pos):
            color = WHITE

        pygame.draw.rect(screen, color, button_rect, 2)

        # Button text
        btn_txt = font.render(text, True, WHITE)
        btn_x = button_rect.x + (button_rect.width - btn_txt.get_width()) // 2
        btn_y = button_rect.y + (button_rect.height - btn_txt.get_height()) // 2
        screen.blit(btn_txt, (btn_x, btn_y))

    # Training info
    info_y = button_y + 180
    info_lines = [
        "• Each training session ages the turtle by 1",
        "• Primary stat always improves by +1",
        "• 20% chance for other stats to improve",
        f"• Turtles auto-retire at age {MAX_AGE}",
    ]

    for i, line in enumerate(info_lines):
        info_txt = font.render(line, True, GRAY)
        screen.blit(info_txt, (50, info_y + i * 25))
