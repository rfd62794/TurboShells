"""Reusable Turtle Info Panel Component for displaying turtle image and basic info."""

import pygame
import pygame_gui
from typing import Optional, Any
from core.rich_logging import get_ui_rich_logger


class TurtleInfoPanel:
    """Reusable turtle info panel component for displaying turtle image and basic information.
    
    Can be reused in Profile, Roster, Breeding, and other panels.
    """
    
    def __init__(self, rect: pygame.Rect, manager, container=None, config=None):
        """Initialize turtle info panel.
        
        Args:
            rect: Panel position and size
            manager: pygame_gui UIManager
            container: pygame_gui container (optional)
            config: Configuration options
        """
        self.rect = rect
        self.manager = manager
        self.container = container
        self.config = config or {}
        self.logger = get_ui_rich_logger()
        
        # UI elements
        self.panel = None
        self.turtle_image = None
        self.name_label = None
        self.status_label = None
        self.age_label = None
        
        # Configuration
        self.image_size = self.config.get('image_size', (120, 120))
        self.show_status = self.config.get('show_status', True)
        self.show_age = self.config.get('show_age', True)
        
        # Create the panel
        self._create_panel()
        
    def _create_panel(self) -> None:
        """Create the turtle info panel UI."""
        # Main panel
        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=self.rect,
            manager=self.manager,
            container=self.container,
            object_id="#turtle_info_panel"
        )
        
        # Calculate positions
        panel_width = self.rect.width
        panel_height = self.rect.height
        
        # Center the image horizontally
        image_x = (panel_width - self.image_size[0]) // 2
        image_y = 20
        
        # Turtle Image
        self.turtle_image = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect((image_x, image_y), self.image_size),
            image_surface=pygame.Surface(self.image_size),
            manager=self.manager,
            container=self.panel
        )
        
        # Labels below image
        label_y = image_y + self.image_size[1] + 15
        label_height = 25
        label_spacing = 5
        
        # Turtle Name
        self.name_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, label_y), (panel_width - 20, label_height)),
            text="",
            manager=self.manager,
            container=self.panel
        )
        label_y += label_height + label_spacing
        
        # Status Label (optional)
        if self.show_status:
            self.status_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((10, label_y), (panel_width - 20, label_height)),
                text="",
                manager=self.manager,
                container=self.panel
            )
            label_y += label_height + label_spacing
        
        # Age Label (optional)
        if self.show_age:
            self.age_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((10, label_y), (panel_width - 20, label_height)),
                text="",
                manager=self.manager,
                container=self.panel
            )
            
    def update_turtle_info(self, turtle: Any, is_retired: bool = False) -> None:
        """Update the turtle info display.
        
        Args:
            turtle: Turtle entity
            is_retired: Whether this is a retired turtle
        """
        if not turtle:
            self._clear_info()
            return
            
        # Update turtle image
        if self.turtle_image:
            try:
                from core.rendering.pygame_turtle_renderer import render_turtle_pygame
                turtle_img = render_turtle_pygame(turtle, size=self.image_size[0])
                self.turtle_image.set_image(turtle_img)
            except Exception as e:
                self.logger.error(f"Error rendering turtle image: {e}")
                
        # Update name
        if self.name_label:
            self.name_label.set_text(f"{turtle.name}")
            
        # Update status
        if self.status_label:
            status = "ACTIVE" if not is_retired else "RETIRED"
            self.status_label.set_text(f"[{status}]")
            
        # Update age
        if self.age_label:
            self.age_label.set_text(f"Age: {turtle.age}")
            
    def _clear_info(self) -> None:
        """Clear all turtle info."""
        # Clear image
        if self.turtle_image:
            self.turtle_image.set_image(pygame.Surface(self.image_size))
            
        # Clear labels
        if self.name_label:
            self.name_label.set_text("")
        if self.status_label:
            self.status_label.set_text("")
        if self.age_label:
            self.age_label.set_text("")
            
    def set_image(self, image_surface: pygame.Surface) -> None:
        """Set the turtle image directly.
        
        Args:
            image_surface: Pygame surface for the turtle image
        """
        if self.turtle_image:
            # Resize if needed
            if image_surface.get_size() != self.image_size:
                image_surface = pygame.transform.scale(image_surface, self.image_size)
            self.turtle_image.set_image(image_surface)
            
    def set_name(self, name: str) -> None:
        """Set the turtle name.
        
        Args:
            name: Turtle name
        """
        if self.name_label:
            self.name_label.set_text(name)
            
    def set_status(self, status: str) -> None:
        """Set the turtle status.
        
        Args:
            status: Status text
        """
        if self.status_label:
            self.status_label.set_text(f"[{status}]")
            
    def set_age(self, age: int) -> None:
        """Set the turtle age.
        
        Args:
            age: Turtle age
        """
        if self.age_label:
            self.age_label.set_text(f"Age: {age}")
            
    def show(self) -> None:
        """Show the turtle info panel."""
        if self.panel and hasattr(self.panel, 'show'):
            self.panel.show()
            
    def hide(self) -> None:
        """Hide the turtle info panel."""
        if self.panel and hasattr(self.panel, 'hide'):
            self.panel.hide()
            
    def destroy(self) -> None:
        """Clean up the turtle info panel."""
        if self.panel:
            self.panel.kill() if hasattr(self.panel, 'kill') else None
