import pygame
from settings import *
import ui.layouts.positions as layout
from ui.components.button import Button

def draw_profile(screen, font, game_state):
    """Draw the profile view for a single turtle with navigation"""
    
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
    
    # Main turtle card
    pygame.draw.rect(screen, GRAY, layout.PROFILE_TURTLE_CARD_RECT, 2)
    
    # Turtle name
    name_txt = font.render(turtle.name, True, WHITE)
    screen.blit(name_txt, layout.PROFILE_TURTLE_NAME_POS)
    
    # Status and age
    status = "ACTIVE" if turtle.is_active else "RETIRED"
    status_color = GREEN if turtle.is_active else YELLOW
    status_txt = font.render(f"[{status}]", True, status_color)
    screen.blit(status_txt, layout.PROFILE_TURTLE_STATUS_POS)
    
    age_txt = font.render(f"Age: {turtle.age}", True, WHITE)
    screen.blit(age_txt, layout.PROFILE_TURTLE_AGE_POS)
    
    # Energy bar (for active turtles)
    if turtle.is_active:
        energy_pct = turtle.current_energy / turtle.max_energy
        pygame.draw.rect(screen, DARK_GREY, layout.PROFILE_TURTLE_ENERGY_BG_RECT)
        energy_width = int(400 * energy_pct)
        energy_rect = pygame.Rect(70, 190, energy_width, 20)
        pygame.draw.rect(screen, GREEN, energy_rect)
        energy_txt = font.render(f"Energy: {turtle.current_energy}/{turtle.max_energy}", True, WHITE)
        screen.blit(energy_txt, (480, 190))
    
    # Stats section
    stats_header = font.render("DETAILED STATS", True, WHITE)
    screen.blit(stats_header, layout.PROFILE_STATS_HEADER_POS)
    
    # Detailed stat breakdown
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
        stat_txt = font.render(f"{stat_name}: {stat_value}", True, WHITE)
        screen.blit(stat_txt, (70, y_pos))
        
        # Description (smaller font if available, otherwise same)
        desc_font = pygame.font.Font(None, 18) if pygame.font.get_fonts() else font
        desc_txt = desc_font.render(description, True, GRAY)
        screen.blit(desc_txt, (250, y_pos + 3))
        
        # Visual bar for stat value
        bar_width = min(stat_value * 3, 200)  # Scale stat to visual bar
        bar_rect = pygame.Rect(550, y_pos, bar_width, 15)
        pygame.draw.rect(screen, BLUE, bar_rect)
        
        y_pos += layout.PROFILE_STATS_HEIGHT
    
    # Race history section
    history_header = font.render("RACE HISTORY", True, WHITE)
    screen.blit(history_header, layout.PROFILE_HISTORY_HEADER_POS)
    
    # Display race history (placeholder for now)
    race_history = getattr(turtle, 'race_history', [])
    if race_history:
        y_pos = layout.PROFILE_HISTORY_START_Y
        for i, race in enumerate(race_history[-5:]):  # Show last 5 races
            race_txt = font.render(f"Race {race.get('number', '?')}: Position {race.get('position', '?')} - ${race.get('earnings', 0)}", True, WHITE)
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
