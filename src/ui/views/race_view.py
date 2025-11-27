import pygame
from settings import *
import ui.layout as layout
import math


def draw_race(screen, font, game_state):
    print(f"[DEBUG] Drawing race screen")
    
    # Draw Finish Line
    pygame.draw.line(
        screen,
        WHITE,
        (TRACK_LENGTH_PIXELS + 40, 50),
        (TRACK_LENGTH_PIXELS + 40, 500),
        5,
    )

    # Get race turtles with fallback
    race_turtles = None
    if hasattr(game_state, 'race_manager') and hasattr(game_state.race_manager, 'race_roster'):
        race_turtles = game_state.race_manager.race_roster
        print(f"[DEBUG] Found {len(race_turtles)} race turtles from race_manager")
    elif hasattr(game_state, 'roster'):
        race_turtles = game_state.roster
        print(f"[DEBUG] Fallback: Using main roster with {len(race_turtles)} turtles")
    else:
        print(f"[ERROR] No turtles found for race rendering!")
        # Draw error message
        error_text = font.render("Race Error: No turtles found", True, RED)
        screen.blit(error_text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2))
        return
    
    # Draw lanes and turtles
    for i, turtle in enumerate(race_turtles):
        lane_y = 150 + (i * 100)
        pygame.draw.rect(screen, (30, 30, 30), (0, lane_y - 20, SCREEN_WIDTH, 80))

        if turtle:
            print(f"[DEBUG] Drawing turtle {i}: {turtle.name} at distance {turtle.race_distance}")
            draw_turtle_sprite(screen, font, turtle, lane_y)
        else:
            print(f"[DEBUG] Empty turtle slot at index {i}")


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
    print(f"[DEBUG] Drawing turtle sprite for {turtle.name} at distance {turtle.race_distance}")
    
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

    print(f"[DEBUG] Screen position: ({screen_x}, {screen_y})")
    
    try:
        # Use universal pygame renderer
        from core.rendering.pygame_turtle_renderer import render_turtle_pygame

        # Generate small turtle image (60x60) for race
        turtle_surface = render_turtle_pygame(turtle, size=60)
        print(f"[DEBUG] Turtle surface generated successfully")

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
        print(f"[DEBUG] Turtle blitted successfully")
        return

    except Exception as e:
        print(f"[ERROR] Error rendering race turtle {turtle.name}: {e}")
        # Fallback: draw simple colored rectangle
        turtle_color = (100, 150, 200)  # Blue fallback
        turtle_rect = pygame.Rect(screen_x, screen_y, 40, 30)
        pygame.draw.rect(screen, turtle_color, turtle_rect)
        print(f"[DEBUG] Using fallback rectangle for {turtle.name}")

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
