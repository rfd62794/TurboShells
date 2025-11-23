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
    
    # Draw voting content (back button is now inside voting view)
    game_state.voting_view.draw()

def handle_voting_click(game_state, pos):
    """Handle clicks in voting interface"""
    # Handle voting view clicks (back button is now handled inside voting view)
    if hasattr(game_state, 'voting_view'):
        return game_state.voting_view.handle_click(pos)
    
    return None
