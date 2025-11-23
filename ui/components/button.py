"""Reusable button component for UI."""

import pygame
from settings import WHITE, GRAY, GREEN


class Button:
    """Reusable button component."""

    def __init__(self, rect, text, color=GRAY, hover_color=WHITE):
        self.rect = rect
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = pygame.font.SysFont("Arial", 18)

    def draw(self, screen, mouse_pos=None):
        """Draw the button."""
        color = self.hover_color if mouse_pos and self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, color, self.rect, 2)

        text_surface = self.font.render(self.text, True, WHITE)
        text_x = self.rect.x + (self.rect.width - text_surface.get_width()) // 2
        text_y = self.rect.y + (self.rect.height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))

    def is_clicked(self, pos):
        """Check if button was clicked."""
        return self.rect.collidepoint(pos)


class ToggleButton(Button):
    """Toggle button component."""

    def __init__(self, rect, text, color=GRAY, active_color=GREEN, hover_color=WHITE):
        super().__init__(rect, text, color, hover_color)
        self.active_color = active_color
        self.is_active = False

    def draw(self, screen, mouse_pos=None):
        """Draw the toggle button."""
        if self.is_active:
            color = self.hover_color if mouse_pos and self.rect.collidepoint(mouse_pos) else self.active_color
        else:
            color = self.hover_color if mouse_pos and self.rect.collidepoint(mouse_pos) else self.color

        pygame.draw.rect(screen, color, self.rect, 2)

        text_surface = self.font.render(self.text, True, WHITE)
        text_x = self.rect.x + (self.rect.width - text_surface.get_width()) // 2
        text_y = self.rect.y + (self.rect.height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))

    def toggle(self):
        """Toggle the button state."""
        self.is_active = not self.is_active

    def set_active(self, active):
        """Set the button state."""
        self.is_active = active
