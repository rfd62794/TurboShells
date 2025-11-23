import pygame
from settings import *
import ui.layouts.positions as layout
from ui.components.button import Button


def draw_profile(screen, font, game_state):
    """Draw the profile view for a single turtle with navigation (image-ready design)"""

    # Header
    pygame.draw.rect(screen, DARK_GREY, layout.PROFILE_HEADER_RECT)
    title = font.render("TURTLE PROFILE", True, WHITE)
    screen.blit(title, layout.PROFILE_TITLE_POS)

    # Back button
    back_btn = Button(layout.PROFILE_BACK_BTN_RECT, "MENU", GRAY, WHITE)
    back_btn.draw(screen, game_state.mouse_pos)

    # Get current turtle and all turtles list
    all_turtles = get_all_turtles(game_state)
    if not all_turtles:
        no_turtles_txt = font.render("No turtles available", True, WHITE)
        screen.blit(no_turtles_txt, (300, 250))
        return back_btn

    current_index = getattr(game_state, 'profile_turtle_index', 0)
    current_index = max(0, min(current_index, len(all_turtles) - 1))
    game_state.profile_turtle_index = current_index

    turtle = all_turtles[current_index]

    # LEFT PANEL - Turtle Visual (future image area)
    pygame.draw.rect(screen, GRAY, layout.PROFILE_VISUAL_PANEL_RECT, 2)

    # Draw actual turtle image using PIL-to-pygame port (preserves customizations)
    try:
        from core.rendering.pygame_turtle_renderer import render_turtle_pygame
        # Generate turtle image (120x120 for profile view) using existing renderer
        turtle_img = render_turtle_pygame(turtle, size=120)
        img_x = layout.PROFILE_TURTLE_IMAGE_POS[0] - 60  # Center the image
        img_y = layout.PROFILE_TURTLE_IMAGE_POS[1] - 60
        screen.blit(turtle_img, (img_x, img_y))
    except Exception as e:
        # Fallback: draw a simple colored circle with turtle info
        pygame.draw.circle(screen, (100, 150, 200), layout.PROFILE_TURTLE_IMAGE_POS, 80, 0)
        pygame.draw.circle(screen, GRAY, layout.PROFILE_TURTLE_IMAGE_POS, 80, 2)

        # Fallback text with turtle name
        placeholder_font = pygame.font.SysFont("Arial", 16)
        placeholder_txt = placeholder_font.render(turtle.name, True, WHITE)
        text_rect = placeholder_txt.get_rect(center=layout.PROFILE_TURTLE_IMAGE_POS)
        screen.blit(placeholder_txt, text_rect)

        # Show age below name
        age_txt = placeholder_font.render(f"Age {turtle.age}", True, GRAY)
        age_rect = age_txt.get_rect(
            center=(
                layout.PROFILE_TURTLE_IMAGE_POS[0],
                layout.PROFILE_TURTLE_IMAGE_POS[1] + 20))
        screen.blit(age_txt, age_rect)

    # RIGHT PANEL - Detailed Information
    pygame.draw.rect(screen, GRAY, layout.PROFILE_INFO_PANEL_RECT, 2)

    # Turtle name (larger font)
    name_font = pygame.font.SysFont("Arial", 28)
    name_txt = name_font.render(turtle.name, True, WHITE)
    screen.blit(name_txt, layout.PROFILE_TURTLE_NAME_POS)

    # Status and age
    status = "ACTIVE" if turtle.is_active else "RETIRED"
    status_color = GREEN if turtle.is_active else YELLOW
    status_txt = font.render(f"[{status}]", True, status_color)
    screen.blit(status_txt, layout.PROFILE_TURTLE_STATUS_POS)

    age_txt = font.render(f"Age: {turtle.age}", True, WHITE)
    screen.blit(age_txt, layout.PROFILE_TURTLE_AGE_POS)

    # Stats section
    stats_header = font.render("DETAILED STATS", True, WHITE)
    screen.blit(stats_header, layout.PROFILE_STATS_HEADER_POS)

    # Detailed stat breakdown with visual bars
    stats = [
        ("Speed", turtle.speed, "How fast the turtle runs on grass"),
        ("Max Energy", turtle.max_energy, "Total stamina for racing"),
        ("Recovery", turtle.recovery, "How quickly energy regenerates"),
        ("Swim", turtle.swim, "Performance in water terrain"),
        ("Climb", turtle.climb, "Performance on rock terrain")
    ]

    y_pos = layout.PROFILE_STATS_START_Y
    for stat_name, stat_value, description in stats:
        # Stat name and value
        stat_txt = font.render(f"{stat_name}:", True, WHITE)
        screen.blit(stat_txt, (390, y_pos))

        value_txt = font.render(str(stat_value), True, WHITE)
        screen.blit(value_txt, (480, y_pos))

        # Visual bar for stat value
        bar_width = min(stat_value * 2, layout.PROFILE_STATS_BAR_WIDTH)  # Scale to fit
        bar_rect = pygame.Rect(layout.PROFILE_STATS_BAR_X, y_pos, bar_width, 15)
        pygame.draw.rect(screen, BLUE, bar_rect)

        y_pos += layout.PROFILE_STATS_HEIGHT

    # Energy section (for active turtles)
    if turtle.is_active:
        energy_header = font.render("ENERGY STATUS", True, WHITE)
        screen.blit(energy_header, layout.PROFILE_ENERGY_HEADER_POS)

        energy_pct = turtle.current_energy / turtle.max_energy
        pygame.draw.rect(screen, DARK_GREY, layout.PROFILE_ENERGY_BG_RECT)
        energy_width = int(300 * energy_pct)
        energy_rect = pygame.Rect(390, 390, energy_width, 20)
        pygame.draw.rect(screen, GREEN, energy_rect)

        energy_txt = font.render(f"{turtle.current_energy}/{turtle.max_energy}", True, WHITE)
        screen.blit(energy_txt, (390, 415))

    # BOTTOM SECTION - Race History
    pygame.draw.rect(screen, GRAY, layout.PROFILE_HISTORY_PANEL_RECT, 2)

    history_header = font.render("RACE HISTORY (Last 5)", True, WHITE)
    screen.blit(history_header, layout.PROFILE_HISTORY_HEADER_POS)

    # Display race history
    race_history = getattr(turtle, 'race_history', [])
    if race_history:
        y_pos = layout.PROFILE_HISTORY_START_Y
        for i, race in enumerate(race_history[-5:]):  # Show last 5 races
            race_txt = font.render(
                f"Race {
                    race.get(
                        'number',
                        '?')}: Pos {
                    race.get(
                        'position',
                        '?')} - ${
                    race.get(
                        'earnings',
                        0)}",
                True,
                WHITE)
            screen.blit(race_txt, (70, y_pos))
            y_pos += layout.PROFILE_HISTORY_HEIGHT
    else:
        no_history_txt = font.render("No race history yet", True, GRAY)
        screen.blit(no_history_txt, (70, layout.PROFILE_HISTORY_START_Y))

    # Navigation controls
    prev_btn = Button(layout.PROFILE_PREV_BTN_RECT, "← PREV", GRAY, WHITE)
    next_btn = Button(layout.PROFILE_NEXT_BTN_RECT, "NEXT →", GRAY, WHITE)

    prev_btn.draw(screen, game_state.mouse_pos)
    next_btn.draw(screen, game_state.mouse_pos)

    # Navigation dots
    draw_navigation_dots(screen, font, current_index, len(all_turtles))

    return back_btn, prev_btn, next_btn


def get_all_turtles(game_state):
    """Get all turtles (active + retired) in a single list"""
    all_turtles = []

    # Add active turtles
    for turtle in game_state.roster:
        if turtle is not None:
            all_turtles.append(turtle)

    # Add retired turtles
    all_turtles.extend(game_state.retired_roster)

    return all_turtles


def draw_navigation_dots(screen, font, current_index, total_count):
    """Draw navigation dots showing current position"""
    if total_count <= 1:
        return

    dot_spacing = 15
    start_x = layout.PROFILE_DOTS_START_X

    for i in range(total_count):
        x_pos = start_x + (i * dot_spacing)

        # Adjust position if too many dots
        if x_pos > 460:  # Prevent dots from going off screen
            break

        color = WHITE if i == current_index else GRAY
        pygame.draw.circle(screen, color, (x_pos, layout.PROFILE_DOTS_Y), 4)


def handle_profile_click(game_state, pos, back_btn, prev_btn, next_btn):
    """Handle clicks in profile view"""
    # This function is called from state handler, but buttons are created in draw_profile
    # So we need to recreate the button logic here or restructure
    # For now, let's check the basic positions

    # Check back button
    if layout.PROFILE_BACK_BTN_RECT.collidepoint(pos):
        return "back"

    # Check navigation buttons
    if layout.PROFILE_PREV_BTN_RECT.collidepoint(pos):
        return "navigate_prev"

    if layout.PROFILE_NEXT_BTN_RECT.collidepoint(pos):
        return "navigate_next"

    return None
