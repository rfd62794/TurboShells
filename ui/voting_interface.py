"""
Voting interface for TurboShells main game integration
Provides a simple interface between the main game and VotingView
"""

import pygame
from settings import *

def draw_voting(screen, font, game_state):
    """Draw the voting interface for main game integration"""
    # Initialize voting view if not exists
    if not hasattr(game_state, 'voting_view'):
        from ui.voting_view import VotingView
        game_state.voting_view = VotingView(screen, game_state)
    
    # Update mouse position for hover effects
    game_state.voting_view.mouse_pos = game_state.mouse_pos
    
    # Draw header
    pygame.draw.rect(screen, (30, 30, 30), (0, 0, SCREEN_WIDTH, 40))
    
    # Title
    title_font = pygame.font.SysFont("Arial", 28)
    title = title_font.render("DESIGN VOTING", True, (255, 255, 255))
    screen.blit(title, (20, 8))
    
    # Money display
    money_text = font.render(f"$ {game_state.money}", True, (255, 255, 255))
    screen.blit(money_text, (650, 10))
    
    # Back button with better styling
    back_rect = pygame.Rect(700, 5, 80, 30)
    
    # Hover effect
    mouse_pos = getattr(game_state, 'mouse_pos', None)
    back_color = (150, 50, 50) if mouse_pos and back_rect.collidepoint(mouse_pos) else (100, 100, 100)
    
    pygame.draw.rect(screen, back_color, back_rect)
    pygame.draw.rect(screen, (200, 200, 200), back_rect, 2)  # Border
    
    back_text = font.render("BACK", True, (255, 255, 255))
    text_x = back_rect.x + (back_rect.width - back_text.get_width()) // 2
    text_y = back_rect.y + (back_rect.height - back_text.get_height()) // 2
    screen.blit(back_text, (text_x, text_y))
    
    # Draw voting content
    game_state.voting_view.draw()
    
    # Store back rect for click handling
    game_state.voting_back_rect = back_rect

def handle_voting_click(game_state, pos):
    """Handle clicks in voting interface"""
    # Check back button
    if hasattr(game_state, 'voting_back_rect') and game_state.voting_back_rect.collidepoint(pos):
        return "back_to_menu"
    
    # Handle voting view clicks
    if hasattr(game_state, 'voting_view'):
        return game_state.voting_view.handle_click(pos)
    
    return None
