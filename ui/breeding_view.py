import pygame
from settings import *
import ui.layout as layout
from ui.turtle_card import format_turtle_label_basic


def draw_breeding(screen, font, game_state):
    title = font.render("BREEDING CENTER (Press M for Menu)", True, WHITE)
    screen.blit(title, layout.HEADER_TITLE_POS)

    msg = font.render("Select 2 Parents (Press 1, 2, 3...) then ENTER to Breed", True, GREEN)
    screen.blit(msg, (50, 60))

    # Combined breeding pool: active + retired
    candidates = [t for t in game_state.roster if t is not None] + list(game_state.retired_roster)

    for i, turtle in enumerate(candidates):
        y_pos = layout.BREEDING_LIST_START_Y + (i * layout.BREEDING_SLOT_HEIGHT)

        is_retired = not getattr(turtle, "is_active", True)
        base_color = RED if is_retired else GRAY

        # Selected parents stand out in green (active) or red (retired)
        if turtle in game_state.breeding_parents:
            color = GREEN if not is_retired else RED
        else:
            color = base_color

        row_rect = pygame.Rect(
            layout.BREEDING_ROW_X,
            y_pos,
            layout.BREEDING_ROW_WIDTH,
            layout.BREEDING_SLOT_HEIGHT,
        )
        pygame.draw.rect(screen, color, row_rect, 2)

        label = f"{i+1}. " + format_turtle_label_basic(turtle)
        txt = font.render(label, True, WHITE)
        screen.blit(txt, (row_rect.x + 20, row_rect.y + 15))
