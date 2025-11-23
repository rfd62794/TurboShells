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

    # Combined breeding pool: active + retired turtles
    candidates = [t for t in game_state.roster if t is not None] + list(game_state.retired_roster)
    
    # Create breeding slots in a grid layout (2 rows of 3) - taller cards
    breeding_slots = [
        pygame.Rect(50, 120, 220, 180),   # Top row - increased height from 140 to 180
        pygame.Rect(290, 120, 220, 180),
        pygame.Rect(530, 120, 220, 180),
        pygame.Rect(50, 320, 220, 180),   # Bottom row - adjusted Y position
        pygame.Rect(290, 320, 220, 180),
        pygame.Rect(530, 320, 220, 180),
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
            
            # Draw selection indicator
            if is_selected:
                pygame.draw.rect(screen, GREEN, slot_rect, 4)
                select_txt = font.render("SELECTED", True, GREEN)
                screen.blit(select_txt, (slot_rect.x + 5, slot_rect.y + 5))
            
            # Draw turtle info
            draw_breeding_turtle_card(screen, font, turtle, slot_rect, is_retired)
            
            # Draw selection number (1, 2, 3...)
            num_txt = font.render(str(idx + 1), True, WHITE)
            screen.blit(num_txt, (slot_rect.x + 5, slot_rect.y + slot_rect.height - 25))
        else:
            # Empty slot
            pygame.draw.rect(screen, GRAY, slot_rect, 1)
            empty_txt = font.render("EMPTY", True, GRAY)
            screen.blit(empty_txt, (slot_rect.centerx - empty_txt.get_width()//2, slot_rect.centery))

    # Breed button (only if 2 parents selected)
    if len(game_state.breeding_parents) == 2:
        breed_color = GREEN
        if mouse_pos and layout.BREED_BTN_RECT.collidepoint(mouse_pos):
            breed_color = WHITE
        pygame.draw.rect(screen, breed_color, layout.BREED_BTN_RECT, 2)
        breed_txt = font.render("BREED", True, WHITE)
        breed_x = layout.BREED_BTN_RECT.x + (layout.BREED_BTN_RECT.width - breed_txt.get_width()) // 2
        screen.blit(breed_txt, (breed_x, layout.BREED_BTN_RECT.y + 15))
        
        # Show breeding info
        parent1, parent2 = game_state.breeding_parents
        info_txt = font.render(f"Breeding: {parent1.name} + {parent2.name}", True, WHITE)
        screen.blit(info_txt, (50, 480))


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
        pygame.draw.ellipse(screen, (34, 139, 34), 
                           (center_x - 25, center_y - 20, 50, 40))
        pygame.draw.ellipse(screen, (0, 100, 0), 
                           (center_x - 25, center_y - 20, 50, 40), 2)
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
        f"Climb: {turtle.climb}"
    ]
    
    # Start position with more space for retired indicator
    y_offset = rect.y + 35 if not is_retired else rect.y + 55
    line_spacing = 22  # Increased from 18 for more spacing
    
    for stat in stats:
        stat_txt = font.render(stat, True, WHITE)
        screen.blit(stat_txt, (rect.x + 80, y_offset))
        y_offset += line_spacing
