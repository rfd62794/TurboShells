import pygame
from settings import *
import ui.layouts.positions as layout
from ui.views.turtle_card import draw_stable_turtle_slot


def draw_breeding(screen, font, game_state):
    # Header bar
    pygame.draw.rect(screen, DARK_GREY, layout.HEADER_RECT)
    title = font.render("BREEDING CENTER", True, WHITE)
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

    # Instructions
    msg = font.render("Select 2 Parents", True, GREEN)
    screen.blit(msg, (50, 60))

    # Warning about parent loss
    warning = font.render(
        "Parent 2 will be lost.", True, (255, 200, 100)
    )  # Orange warning color
    screen.blit(warning, (50, 80))

    # Breed button (only if 2 parents selected) - positioned next to instructions
    if len(game_state.breeding_parents) == 2:
        breed_color = GREEN
        breed_rect = pygame.Rect(250, 65, 100, 35)  # Adjusted Y position
        if mouse_pos and breed_rect.collidepoint(mouse_pos):
            breed_color = WHITE

        pygame.draw.rect(screen, breed_color, breed_rect, 2)
        breed_txt = font.render("BREED", True, WHITE)
        breed_x = breed_rect.x + (breed_rect.width - breed_txt.get_width()) // 2
        screen.blit(breed_txt, (breed_x, breed_rect.y + 8))

        # Show breeding info
        parent1, parent2 = game_state.breeding_parents
        info_txt = font.render(
            f"Breeding: {parent1.name} + {parent2.name}", True, WHITE
        )
        screen.blit(info_txt, (50, 110))  # Moved down to make space

    # Combined breeding pool: active + retired turtles
    candidates = [t for t in game_state.roster if t is not None] + list(
        game_state.retired_roster
    )

    # Create breeding slots in a grid layout (2 rows of 3) - adjusted Y position and more space
    breeding_slots = [
        pygame.Rect(
            50, 140, 230, 190
        ),  # Top row - increased width from 220 to 230, height from 180 to 190
        pygame.Rect(280, 140, 230, 190),  # Adjusted X for more spacing
        pygame.Rect(530, 140, 230, 190),
        pygame.Rect(50, 350, 230, 190),  # Bottom row - adjusted Y for more spacing
        pygame.Rect(280, 350, 230, 190),
        pygame.Rect(530, 350, 230, 190),
    ]

    # Draw breeding candidates
    for idx, slot_rect in enumerate(breeding_slots):
        if idx < len(candidates):
            turtle = candidates[idx]
            is_selected = turtle in game_state.breeding_parents
            is_retired = turtle in game_state.retired_roster

            # Draw slot background
            slot_color = DARK_GREY if is_selected else GRAY
            if mouse_pos and slot_rect.collidepoint(mouse_pos):
                slot_color = WHITE
            pygame.draw.rect(screen, slot_color, slot_rect, 2)

            # Draw selection indicator with parent number (moved to bottom)
            if is_selected:
                pygame.draw.rect(screen, GREEN, slot_rect, 4)

                # Determine parent number (1 or 2)
                parent_num = "1" if game_state.breeding_parents[0] == turtle else "2"
                parent_color = (
                    (100, 255, 100) if parent_num == "1" else (255, 100, 100)
                )  # Green for P1, Red for P2

                # Draw colored background bar at bottom
                bar_rect = pygame.Rect(
                    slot_rect.x + 5,
                    slot_rect.y + slot_rect.height - 35,
                    slot_rect.width - 10,
                    30,
                )
                pygame.draw.rect(screen, parent_color, bar_rect)
                pygame.draw.rect(screen, WHITE, bar_rect, 1)

                # White text on colored background
                select_txt = font.render(f"PARENT {parent_num}", True, WHITE)
                text_x = bar_rect.x + (bar_rect.width - select_txt.get_width()) // 2
                text_y = bar_rect.y + (bar_rect.height - select_txt.get_height()) // 2
                screen.blit(select_txt, (text_x, text_y))

                # Add red X over the turtle image for Parent 2
                if parent_num == "2":
                    # Draw red X over the turtle image area
                    x_center = slot_rect.x + 70  # Center of turtle image area
                    y_center = slot_rect.y + 85  # Center of turtle image area
                    x_size = 50  # Size of the X

                    # Draw thick red X lines
                    pygame.draw.line(
                        screen,
                        (255, 0, 0),
                        (x_center - x_size, y_center - x_size),
                        (x_center + x_size, y_center + x_size),
                        5,
                    )
                    pygame.draw.line(
                        screen,
                        (255, 0, 0),
                        (x_center + x_size, y_center - x_size),
                        (x_center - x_size, y_center + x_size),
                        5,
                    )

            # Draw turtle info
            draw_breeding_turtle_card(screen, font, turtle, slot_rect, is_retired)

            # Draw selection number (1, 2, 3...) - moved to top right
            num_txt = font.render(str(idx + 1), True, WHITE)
            screen.blit(num_txt, (slot_rect.x + slot_rect.width - 25, slot_rect.y + 5))
        else:
            # Empty slot
            pygame.draw.rect(screen, GRAY, slot_rect, 1)
            empty_txt = font.render("EMPTY", True, GRAY)
            screen.blit(
                empty_txt,
                (slot_rect.centerx - empty_txt.get_width() // 2, slot_rect.centery),
            )


def draw_breeding_turtle_card(screen, font, turtle, rect, is_retired):
    """Draw a compact turtle card for breeding selection"""
    if not turtle:
        return

    # Draw turtle image using universal renderer
    try:
        from core.rendering.pygame_turtle_renderer import render_turtle_pygame

        # Generate small turtle image (60x60) using existing renderer
        turtle_img = render_turtle_pygame(turtle, size=60)
        img_x = rect.x + 10
        img_y = rect.y + 25
        screen.blit(turtle_img, (img_x, img_y))
    except Exception as e:
        # Fallback: draw placeholder turtle
        pic_rect = pygame.Rect(rect.x + 10, rect.y + 25, 60, 60)
        pygame.draw.rect(screen, BLUE, pic_rect)
        pygame.draw.rect(screen, WHITE, pic_rect, 1)

        # Simple turtle shape fallback
        center_x = pic_rect.centerx
        center_y = pic_rect.centery
        # Shell
        pygame.draw.ellipse(
            screen, (34, 139, 34), (center_x - 25, center_y - 20, 50, 40)
        )
        pygame.draw.ellipse(
            screen, (0, 100, 0), (center_x - 25, center_y - 20, 50, 40), 2
        )
        # Head
        pygame.draw.circle(screen, (139, 90, 43), (center_x, center_y - 35), 10)
        pygame.draw.circle(screen, (100, 60, 20), (center_x, center_y - 35), 10, 2)

    # Turtle name
    name_color = GRAY if is_retired else WHITE
    name_txt = font.render(turtle.name, True, name_color)
    screen.blit(name_txt, (rect.x + 80, rect.y + 10))

    if is_retired:
        retired_txt = font.render("(RETIRED)", True, GRAY)
        screen.blit(retired_txt, (rect.x + 80, rect.y + 30))

    # Vertical stats list with more spacing
    stats = [
        f"Speed: {turtle.speed}",
        f"Energy: {turtle.max_energy}",
        f"Recovery: {turtle.recovery}",
        f"Swim: {turtle.swim}",
        f"Climb: {turtle.climb}",
    ]

    # Start position with more space for retired indicator
    y_offset = rect.y + 35 if not is_retired else rect.y + 55
    line_spacing = 22  # Increased from 18 for more spacing

    for stat in stats:
        stat_txt = font.render(stat, True, WHITE)
        screen.blit(stat_txt, (rect.x + 80, y_offset))
        y_offset += line_spacing
