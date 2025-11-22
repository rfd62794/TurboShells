import pygame
from settings import *
import ui.layout as layout


def draw_stable_turtle_slot(screen, font, game_state, turtle, slot_rect, is_active_racer, mouse_pos):
    """Draw the Stable/Main Menu turtle slot, without action buttons.

    Buttons and click handling remain in RosterManager; this is purely visual.
    """
    # Slot border color: active racer highlighted
    border_color = GREEN if is_active_racer else GRAY
    if mouse_pos and slot_rect.collidepoint(mouse_pos):
        border_color = WHITE
    pygame.draw.rect(screen, border_color, slot_rect, 2)

    if not turtle:
        empty_txt = font.render("[ EMPTY SLOT ]", True, GRAY)
        screen.blit(empty_txt, (slot_rect.x + 20, slot_rect.y + 40))
        return

    # Name
    name_pos = (slot_rect.x + layout.SLOT_NAME_POS[0], slot_rect.y + layout.SLOT_NAME_POS[1])
    name_txt = font.render(turtle.name, True, WHITE)
    screen.blit(name_txt, name_pos)

    # Stats line with status + age
    stats_pos = (slot_rect.x + layout.SLOT_STATS_POS[0], slot_rect.y + layout.SLOT_STATS_POS[1])
    status_tag = "[ACT]" if getattr(turtle, "is_active", True) else "[RET]"
    stats_str = (
        f"{status_tag} "
        f"Age:{turtle.age} "
        f"Spd:{turtle.stats['speed']} "
        f"Nrg:{turtle.stats['max_energy']} "
        f"Rec:{turtle.stats['recovery']} "
        f"Swm:{turtle.stats['swim']} "
        f"Clm:{turtle.stats['climb']}"
    )
    stats_txt = font.render(stats_str, True, WHITE)
    screen.blit(stats_txt, stats_pos)

    # Energy bar
    energy_bg = layout.SLOT_ENERGY_BG_RECT
    energy_bg_rect = pygame.Rect(
        slot_rect.x + energy_bg.x,
        slot_rect.y + energy_bg.y,
        energy_bg.width,
        energy_bg.height,
    )
    pygame.draw.rect(screen, RED, energy_bg_rect)

    pct = turtle.current_energy / turtle.stats["max_energy"] if turtle.stats["max_energy"] > 0 else 0
    fill_width = int(energy_bg.width * max(0.0, min(1.0, pct)))
    energy_fill_rect = pygame.Rect(
        energy_bg_rect.x + 2,
        energy_bg_rect.y + 2,
        max(0, fill_width - 4),
        energy_bg.height - 4,
    )
    pygame.draw.rect(screen, GREEN, energy_fill_rect)
