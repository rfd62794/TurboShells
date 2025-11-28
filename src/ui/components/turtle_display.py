"""
Turtle display component for showing rendered turtles.
"""

import pygame
from typing import Optional, Any
from .base_component import BaseComponent


class TurtleDisplay(BaseComponent):
    """Component for displaying rendered turtle images."""
    
    def __init__(self, rect: pygame.Rect, manager=None):
        """Initialize turtle display.
        
        Args:
            rect: Component position and size
            manager: pygame_gui UIManager
        """
        super().__init__(rect, manager)
        self.turtle: Optional[Any] = None
        self.turtle_surface: Optional[pygame.Surface] = None
        self.render_engine = None
        self.font = pygame.font.Font(None, 16)
        self.info_lines = []
        
    def set_turtle(self, turtle: Any, render_engine=None) -> None:
        """Set the turtle to display.
        
        Args:
            turtle: Turtle object with required attributes
            render_engine: Turtle rendering engine
        """
        self.turtle = turtle
        self.render_engine = render_engine
        self._update_turtle_surface()
        self._update_info_lines()
        
    def _update_turtle_surface(self) -> None:
        """Update the turtle surface using render engine."""
        if not self.turtle or not self.render_engine:
            self.turtle_surface = None
            return
            
        try:
            # Get turtle sprite surface from render engine
            size = (min(self.rect.width - 20, 200), min(self.rect.height - 100, 200))
            self.turtle_surface = self.render_engine.get_turtle_sprite_surface(self.turtle, size)
        except Exception as e:
            print(f"Error rendering turtle: {e}")
            self.turtle_surface = None
            
    def _update_info_lines(self) -> None:
        """Update turtle information lines."""
        self.info_lines = []
        
        if not self.turtle:
            self.info_lines = ["No turtle selected"]
            return
            
        # Add basic turtle info
        self.info_lines.append(f"Name: {getattr(self.turtle, 'name', 'Unknown')}")
        self.info_lines.append(f"ID: {getattr(self.turtle, 'id', 'Unknown')}")
        
        # Add stats if available
        if hasattr(self.turtle, 'stats'):
            stats = self.turtle.stats
            self.info_lines.append(f"Speed: {stats.get('speed', 'N/A')}")
            self.info_lines.append(f"Energy: {stats.get('max_energy', 'N/A')}")
            
        # Add genetics info if available
        if hasattr(self.turtle, 'shell_base_color'):
            self.info_lines.append(f"Shell: RGB{self.turtle.shell_base_color}")
            
    def render(self, surface: pygame.Surface) -> None:
        """Render turtle display."""
        if not self.visible:
            return
            
        abs_rect = self.get_absolute_rect()
        
        # Draw border
        pygame.draw.rect(surface, (200, 200, 200), abs_rect, 2)
        
        # Draw turtle surface if available
        if self.turtle_surface:
            # Center the turtle image
            turtle_rect = self.turtle_surface.get_rect()
            turtle_rect.centerx = abs_rect.centerx
            turtle_rect.y = abs_rect.y + 10
            surface.blit(self.turtle_surface, turtle_rect)
        else:
            # Draw placeholder
            placeholder_text = self.font.render("No Turtle", True, (150, 150, 150))
            placeholder_rect = placeholder_text.get_rect()
            placeholder_rect.centerx = abs_rect.centerx
            placeholder_rect.y = abs_rect.y + 50
            surface.blit(placeholder_text, placeholder_rect)
            
        # Draw info lines
        y_offset = abs_rect.bottom - 80
        for line in self.info_lines:
            text_surface = self.font.render(line, True, (0, 0, 0))
            surface.blit(text_surface, (abs_rect.x + 10, y_offset))
            y_offset += 18
            
    def set_info_lines(self, lines: list) -> None:
        """Set custom info lines."""
        self.info_lines = lines
        
    def add_info_line(self, line: str) -> None:
        """Add an info line."""
        self.info_lines.append(line)


class DesignDisplay(TurtleDisplay):
    """Specialized turtle display for voting designs."""
    
    def __init__(self, rect: pygame.Rect, manager=None):
        super().__init__(rect, manager)
        self.design_name = ""
        self.design_status = ""
        self.design_categories = 0
        
    def set_design(self, design: dict, render_engine=None) -> None:
        """Set the design to display.
        
        Args:
            design: Design dictionary with turtle data
            render_engine: Turtle rendering engine
        """
        self.design_name = design.get('name', 'Unknown Design')
        self.design_status = design.get('voting_status', 'unknown')
        self.design_categories = len(design.get('rating_categories', {}))
        
        # Extract turtle data if available
        turtle = design.get('turtle')
        if not turtle and 'id' in design:
            # Create mock turtle from design data
            turtle = self._create_mock_turtle(design)
            
        self.set_turtle(turtle, render_engine)
        
    def _create_mock_turtle(self, design: dict) -> Any:
        """Create a mock turtle from design data."""
        class MockTurtle:
            def __init__(self, design_data):
                self.name = design_data.get('name', f"Design #{design_data.get('id', '?')}")
                self.id = design_data.get('id', 0)
                # Add mock genetics based on design ID
                import random
                random.seed(self.id * 12345)
                self.shell_base_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
                self.shell_pattern_type = random.choice(['solid', 'stripes', 'spots', 'marbled'])
                self.stats = {'speed': random.randint(15, 25), 'max_energy': random.randint(200, 300)}
                
        return MockTurtle(design)
        
    def _update_info_lines(self) -> None:
        """Update design-specific info lines."""
        self.info_lines = []
        
        # Design info
        self.info_lines.append(f"Design: {self.design_name}")
        self.info_lines.append(f"Status: {self.design_status.upper()}")
        self.info_lines.append(f"Categories: {self.design_categories}")
        
        # Add turtle info if available
        if self.turtle:
            if hasattr(self.turtle, 'stats'):
                stats = self.turtle.stats
                self.info_lines.append(f"Speed: {stats.get('speed', 'N/A')}")
                self.info_lines.append(f"Energy: {stats.get('max_energy', 'N/A')}")
                
        # Add genetics info if available
        if hasattr(self.turtle, 'shell_base_color'):
            self.info_lines.append(f"Shell: RGB{self.turtle.shell_base_color}")
