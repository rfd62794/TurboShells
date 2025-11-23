"""Reusable turtle card component for UI."""

import pygame
from settings import WHITE, GRAY, GREEN, RED


class TurtleCard:
    """Reusable turtle card component."""
    
    def __init__(self, rect, turtle=None, show_train_button=True):
        self.rect = rect
        self.turtle = turtle
        self.show_train_button = show_train_button
        self.font = pygame.font.SysFont("Arial", 18)
        self.small_font = pygame.font.SysFont("Arial", 14)
        
    def draw(self, screen, game_state, mouse_pos=None, is_selected=False, is_active_racer=False):
        """Draw the turtle card."""
        # Draw card border
        border_color = GREEN if is_selected else (WHITE if is_active_racer else GRAY)
        pygame.draw.rect(screen, border_color, self.rect, 2)
        
        if self.turtle:
            # Draw turtle info
            name_text = self.font.render(self.turtle.name, True, WHITE)
            screen.blit(name_text, (self.rect.x + 20, self.rect.y + 15))
            
            # Draw stats
            stats_text = f"Spd:{self.turtle.stats['speed']} Eng:{self.turtle.current_energy}/{self.turtle.stats['max_energy']}"
            stats_surface = self.small_font.render(stats_text, True, WHITE)
            screen.blit(stats_surface, (self.rect.x + 20, self.rect.y + 45))
            
            # Draw energy bar
            energy_width = int((self.turtle.current_energy / self.turtle.stats['max_energy']) * 200)
            pygame.draw.rect(screen, GRAY, (self.rect.x + 20, self.rect.y + 70, 200, 10))
            pygame.draw.rect(screen, GREEN, (self.rect.x + 20, self.rect.y + 70, energy_width, 10))
            
            # Draw train button if enabled and turtle is active
            if self.show_train_button and is_active_racer and getattr(self.turtle, 'is_active', True):
                self._draw_train_button(screen, mouse_pos)
        else:
            # Empty slot
            empty_text = self.font.render("Empty", True, GRAY)
            text_x = self.rect.x + (self.rect.width - empty_text.get_width()) // 2
            text_y = self.rect.y + (self.rect.height - empty_text.get_height()) // 2
            screen.blit(empty_text, (text_x, text_y))
    
    def _draw_train_button(self, screen, mouse_pos=None):
        """Draw train button on the card."""
        train_rect = pygame.Rect(
            self.rect.x + 550, 
            self.rect.y + 15, 
            80, 
            28
        )
        
        color = WHITE if mouse_pos and train_rect.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(screen, color, train_rect, 2)
        
        train_text = self.small_font.render("TRAIN", True, WHITE)
        text_x = train_rect.x + (train_rect.width - train_text.get_width()) // 2
        text_y = train_rect.y + (train_rect.height - train_text.get_height()) // 2
        screen.blit(train_text, (text_x, text_y))
    
    def is_clicked(self, pos):
        """Check if card was clicked."""
        return self.rect.collidepoint(pos)
    
    def is_train_clicked(self, pos):
        """Check if train button was clicked."""
        if not self.turtle or not self.show_train_button:
            return False
            
        train_rect = pygame.Rect(
            self.rect.x + 550, 
            self.rect.y + 15, 
            80, 
            28
        )
        return train_rect.collidepoint(pos)
    
    def is_card_clicked(self, pos):
        """Check if the turtle card itself was clicked (for profile view)."""
        if not self.turtle:
            return False
        return self.rect.collidepoint(pos)
