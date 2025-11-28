"""
Rating components for voting interfaces.
"""

import pygame
import pygame_gui
from typing import Optional, Callable, Dict, Any
from .base_component import BaseComponent


class StarRating(BaseComponent):
    """Star rating component."""
    
    def __init__(self, rect: pygame.Rect, max_stars: int = 5, manager=None):
        """Initialize star rating.
        
        Args:
            rect: Component position and size
            max_stars: Maximum number of stars
            manager: pygame_gui UIManager
        """
        super().__init__(rect, manager)
        self.max_stars = max_stars
        self.current_rating = 0
        self.star_color = (255, 215, 0)  # Gold
        self.star_empty_color = (200, 200, 200)  # Light gray
        self.star_hover_color = (255, 255, 100)  # Light yellow
        self.star_size = 20
        self.star_spacing = 5
        self.hover_star = -1
        self.on_rating_changed: Optional[Callable[[int], None]] = None
        
    def render(self, surface: pygame.Surface) -> None:
        """Render star rating."""
        if not self.visible:
            return
            
        abs_rect = self.get_absolute_rect()
        mouse_pos = pygame.mouse.get_pos()
        
        # Check hover position
        self.hover_star = -1
        if self.enabled and abs_rect.collidepoint(mouse_pos):
            for i in range(self.max_stars):
                star_x = abs_rect.x + i * (self.star_size + self.star_spacing)
                star_rect = pygame.Rect(star_x, abs_rect.y, self.star_size, self.star_size)
                if star_rect.collidepoint(mouse_pos):
                    self.hover_star = i
                    break
                    
        # Draw stars
        for i in range(self.max_stars):
            star_x = abs_rect.x + i * (self.star_size + self.star_spacing)
            star_y = abs_rect.y
            
            # Determine star color
            if i < self.current_rating:
                color = self.star_color
            elif self.hover_star >= 0 and i <= self.hover_star:
                color = self.star_hover_color
            else:
                color = self.star_empty_color
                
            self._draw_star(surface, star_x, star_y, color)
            
    def _draw_star(self, surface: pygame.Surface, x: int, y: int, color: Tuple[int, int, int]) -> None:
        """Draw a star shape."""
        points = []
        for i in range(10):
            angle = 3.14159 * i / 5
            if i % 2 == 0:
                radius = self.star_size
            else:
                radius = self.star_size * 0.5
                
            px = x + self.star_size + radius * pygame.math.Vector2(1, 0).rotate(angle - 90).x
            py = y + self.star_size + radius * pygame.math.Vector2(1, 0).rotate(angle - 90).y
            points.append((px, py))
            
        pygame.draw.polygon(surface, color, points)
        
    def _handle_component_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            abs_rect = self.get_absolute_rect()
            mouse_pos = event.pos
            
            if abs_rect.collidepoint(mouse_pos):
                # Calculate which star was clicked
                for i in range(self.max_stars):
                    star_x = abs_rect.x + i * (self.star_size + self.star_spacing)
                    star_rect = pygame.Rect(star_x, abs_rect.y, self.star_size, self.star_size)
                    if star_rect.collidepoint(mouse_pos):
                        # Toggle rating (click same star to unrate)
                        if self.current_rating == i + 1:
                            self.current_rating = 0
                        else:
                            self.current_rating = i + 1
                            
                        if self.on_rating_changed:
                            self.on_rating_changed(self.current_rating)
                        return True
        return False
        
    def set_rating(self, rating: int) -> None:
        """Set the rating value."""
        self.current_rating = max(0, min(rating, self.max_stars))
        
    def get_rating(self) -> int:
        """Get the current rating."""
        return self.current_rating


class DropdownRating(BaseComponent):
    """Dropdown rating component using pygame_gui."""
    
    def __init__(self, rect: pygame.Rect, max_rating: int = 5, manager=None):
        """Initialize dropdown rating.
        
        Args:
            rect: Component position and size
            max_rating: Maximum rating value
            manager: pygame_gui UIManager
        """
        super().__init__(rect, manager)
        self.max_rating = max_rating
        self.current_rating = 0
        self.dropdown: Optional[pygame_gui.elements.UIDropDownMenu] = None
        self.on_rating_changed: Optional[Callable[[int], None]] = None
        
        if self.manager:
            self._create_dropdown()
            
    def _create_dropdown(self) -> None:
        """Create the dropdown menu."""
        options = ['No Rating'] + [f'{i} Stars' for i in range(1, self.max_rating + 1)]
        self.dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=options,
            starting_option='No Rating',
            relative_rect=pygame.Rect(0, 0, self.rect.width, self.rect.height),
            manager=self.manager
        )
        
    def render(self, surface: pygame.Surface) -> None:
        """Render dropdown (handled by pygame_gui)."""
        # Dropdown is rendered by pygame_gui automatically
        pass
        
    def _handle_component_event(self, event: pygame.event.Event) -> bool:
        """Handle dropdown events."""
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.dropdown:
                selected_text = event.text
                
                # Parse rating from selection
                if selected_text == 'No Rating':
                    self.current_rating = 0
                else:
                    # Extract number from "X Stars"
                    rating = int(selected_text.split(' ')[0])
                    self.current_rating = rating
                    
                if self.on_rating_changed:
                    self.on_rating_changed(self.current_rating)
                return True
        return False
        
    def set_rating(self, rating: int) -> None:
        """Set the rating value."""
        self.current_rating = max(0, min(rating, self.max_rating))
        
        # Update dropdown selection
        if self.dropdown:
            if self.current_rating == 0:
                self.dropdown.selected_option = 'No Rating'
            else:
                self.dropdown.selected_option = f'{self.current_rating} Stars'
                
    def get_rating(self) -> int:
        """Get the current rating."""
        return self.current_rating


class RatingCategory(BaseComponent):
    """Complete rating category with label, description, and rating component."""
    
    def __init__(self, rect: pygame.Rect, name: str, description: str, 
                 rating_type: str = 'stars', manager=None):
        """Initialize rating category.
        
        Args:
            rect: Component position and size
            name: Category name
            description: Category description
            rating_type: 'stars' or 'dropdown'
            manager: pygame_gui UIManager
        """
        super().__init__(rect, manager)
        self.name = name
        self.description = description
        self.rating_type = rating_type
        self.font = pygame.font.Font(None, 18)
        self.small_font = pygame.font.Font(None, 14)
        
        # Create rating component
        rating_rect = pygame.Rect(0, 50, rect.width, 30)
        if rating_type == 'stars':
            self.rating_component = StarRating(rating_rect, manager=manager)
        else:
            self.rating_component = DropdownRating(rating_rect, manager=manager)
            
        self.add_child(self.rating_component)
        
    def render(self, surface: pygame.Surface) -> None:
        """Render rating category."""
        if not self.visible:
            return
            
        abs_rect = self.get_absolute_rect()
        
        # Draw name
        name_surface = self.font.render(self.name, True, (0, 0, 0))
        surface.blit(name_surface, (abs_rect.x, abs_rect.y))
        
        # Draw description
        desc_surface = self.small_font.render(self.description, True, (100, 100, 100))
        surface.blit(desc_surface, (abs_rect.x, abs_rect.y + 25))
        
        # Render rating component
        self.rating_component.render(surface)
        
    def get_rating(self) -> int:
        """Get the rating value."""
        return self.rating_component.get_rating()
        
    def set_rating(self, rating: int) -> None:
        """Set the rating value."""
        self.rating_component.set_rating(rating)
        
    def set_rating_changed_callback(self, callback: Callable[[int], None]) -> None:
        """Set callback for rating changes."""
        self.rating_component.on_rating_changed = callback
