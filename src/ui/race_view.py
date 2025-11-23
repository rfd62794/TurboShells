import pygame
from settings import *
import ui.layout as layout
import math


def draw_race(screen, font, game_state):
    header = font.render(
        f"RACE (Speed: {game_state.race_speed_multiplier}x | Bet: ${getattr(game_state, 'current_bet', 0)} )",
        True,
        WHITE,
    )
    screen.blit(header, layout.HEADER_TITLE_POS)

    # Draw Finish Line
    pygame.draw.line(
        screen,
        WHITE,
        (TRACK_LENGTH_PIXELS + 40, 50),
        (TRACK_LENGTH_PIXELS + 40, 500),
        5,
    )

    # Draw lanes and turtles
    race_turtles = (
        game_state.race_manager.race_roster
        if hasattr(game_state.race_manager, "race_roster")
        else game_state.roster
    )
    for i, turtle in enumerate(race_turtles):
        lane_y = 150 + (i * 100)
        pygame.draw.rect(screen, (30, 30, 30), (0, lane_y - 20, SCREEN_WIDTH, 80))

        if turtle:
            draw_turtle_sprite(screen, font, turtle, lane_y)

    # Draw Race HUD panel
    pygame.draw.rect(screen, (0, 0, 0), layout.RACE_HUD_RECT)

    # Speed buttons
    pygame.draw.rect(screen, GRAY, layout.SPEED_1X_RECT, 2)
    pygame.draw.rect(screen, GRAY, layout.SPEED_2X_RECT, 2)
    pygame.draw.rect(screen, GRAY, layout.SPEED_4X_RECT, 2)

    one_txt = font.render("1x", True, WHITE)
    two_txt = font.render("2x", True, WHITE)
    four_txt = font.render("4x", True, WHITE)

    screen.blit(one_txt, (layout.SPEED_1X_RECT.x + 10, layout.SPEED_1X_RECT.y + 10))
    screen.blit(two_txt, (layout.SPEED_2X_RECT.x + 10, layout.SPEED_2X_RECT.y + 10))
    screen.blit(four_txt, (layout.SPEED_4X_RECT.x + 10, layout.SPEED_4X_RECT.y + 10))

    # Progress bar (simple overall race progress for player turtle)
    player = race_turtles[0] if race_turtles else None
    pygame.draw.rect(screen, GRAY, layout.PROGRESS_BAR_RECT, 1)
    if player:
        pct = min(1.0, player.race_distance / TRACK_LENGTH_LOGIC)
        fill_width = int(layout.PROGRESS_BAR_RECT.width * pct)
        fill_rect = pygame.Rect(
            layout.PROGRESS_BAR_RECT.x,
            layout.PROGRESS_BAR_RECT.y,
            fill_width,
            layout.PROGRESS_BAR_RECT.height,
        )
        pygame.draw.rect(screen, GREEN, fill_rect)


def draw_race_result(screen, font, game_state):
    title = font.render("RACE RESULTS", True, WHITE)
    screen.blit(title, layout.HEADER_TITLE_POS)

    active_idx = getattr(game_state, "active_racer_index", 0)
    player_turtle = None
    if 0 <= active_idx < len(game_state.roster):
        player_turtle = game_state.roster[active_idx]

    for i, turtle in enumerate(game_state.race_results):
        y_pos = 100 + (i * 60)
        color = WHITE
        if turtle == player_turtle:
            color = GREEN

        status_tag = "[ACT]" if getattr(turtle, "is_active", True) else "[RET]"
        label = f"{i + 1}. {turtle.name} {status_tag} (Age:{turtle.age})"
        txt = font.render(label, True, color)
        screen.blit(txt, (100, y_pos))

    # Show Reward info if player finished
    if player_turtle and player_turtle.rank:
        reward_txt = font.render(f"You finished #{player_turtle.rank}!", True, GREEN)
        screen.blit(reward_txt, (100, 350))

    # Buttons: Menu and Race Again
    pygame.draw.rect(screen, GREEN, layout.RACE_RESULT_MENU_BTN_RECT, 2)
    pygame.draw.rect(screen, BLUE, layout.RACE_RESULT_RERUN_BTN_RECT, 2)

    menu_txt = font.render("MENU", True, WHITE)
    rerun_txt = font.render("RACE AGAIN", True, WHITE)

    screen.blit(
        menu_txt,
        (
            layout.RACE_RESULT_MENU_BTN_RECT.x + 60,
            layout.RACE_RESULT_MENU_BTN_RECT.y + 15,
        ),
    )
    screen.blit(
        rerun_txt,
        (
            layout.RACE_RESULT_RERUN_BTN_RECT.x + 25,
            layout.RACE_RESULT_RERUN_BTN_RECT.y + 15,
        ),
    )


def draw_turtle_sprite(screen, font, turtle, y_pos, race_direction="horizontal"):
    """Draw turtle using universal pygame renderer with rotation support"""
    # Convert Logical Distance (1500) to Screen Pixels (700)
    if race_direction == "horizontal":
        screen_x = (turtle.race_distance / TRACK_LENGTH_LOGIC) * TRACK_LENGTH_PIXELS
        screen_y = y_pos
    else:  # vertical (bottom to top)
        screen_x = y_pos  # Use y_pos as x position for vertical layout
        # Invert Y for bottom-to-top racing
        screen_y = (
            SCREEN_HEIGHT
            - 50
            - (turtle.race_distance / TRACK_LENGTH_LOGIC) * (SCREEN_HEIGHT - 150)
        )

    try:
        # Use universal pygame renderer
        from core.rendering.pygame_turtle_renderer import render_turtle_pygame

        # Generate small turtle image (60x60) for race
        turtle_surface = render_turtle_pygame(turtle, size=60)

        # Rotate based on race direction
        if race_direction == "horizontal":
            turtle_surface = pygame.transform.rotate(turtle_surface, -90)  # Face right
        else:
            turtle_surface = pygame.transform.rotate(
                turtle_surface, 0
            )  # Face up (no rotation)

        # Add energy bar overlay
        bar_width = 60
        pct = turtle.current_energy / turtle.stats["max_energy"]
        fill_width = int(pct * bar_width)

        # Draw energy bar above/below turtle based on direction
        if race_direction == "horizontal":
            pygame.draw.rect(screen, RED, (screen_x, screen_y - 15, bar_width, 5))
            pygame.draw.rect(screen, GREEN, (screen_x, screen_y - 15, fill_width, 5))
        else:
            pygame.draw.rect(screen, RED, (screen_x - 30, screen_y - 10, bar_width, 5))
            pygame.draw.rect(
                screen, GREEN, (screen_x - 30, screen_y - 10, fill_width, 5)
            )

        # Draw turtle
        screen.blit(turtle_surface, (screen_x, screen_y))
        return

    except Exception as e:
        print(f"Error rendering race turtle: {e}")
        # Fallback: draw simple colored rectangle
        turtle_color = (100, 150, 200)  # Blue fallback
        turtle_rect = pygame.Rect(screen_x, screen_y, 40, 30)
        pygame.draw.rect(screen, turtle_color, turtle_rect)

        # Add energy bar for fallback
        bar_width = 40
        pct = turtle.current_energy / turtle.stats["max_energy"]
        fill_width = int(pct * bar_width)

        if race_direction == "horizontal":
            pygame.draw.rect(screen, RED, (screen_x, screen_y - 10, bar_width, 3))
            pygame.draw.rect(screen, GREEN, (screen_x, screen_y - 10, fill_width, 3))
        else:
            pygame.draw.rect(screen, RED, (screen_x - 20, screen_y - 8, bar_width, 3))
            pygame.draw.rect(
                screen, GREEN, (screen_x - 20, screen_y - 8, fill_width, 3)
            )

        # Draw turtle name on fallback
        name_font = pygame.font.SysFont("Arial", 10)
        name_txt = name_font.render(turtle.name[:8], True, WHITE)
        screen.blit(name_txt, (screen_x + 2, screen_y + 8))
