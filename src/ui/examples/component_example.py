"""
Example demonstrating the new component-based UI architecture.
"""

import pygame
import pygame_gui
from ui.components import (
    BaseComponent, 
    Container, 
    ScrollableContainer,
    StarRating, 
    RatingCategory,
    DesignDisplay,
    VotingPanelComponent
)


class SimpleComponentExample:
    """Example of using the new component system."""
    
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager
        self.components = []
        
        # Create example components
        self._create_example_components()
        
    def _create_example_components(self):
        """Create example components to demonstrate the system."""
        
        # Example 1: Simple star rating
        star_rating = StarRating(
            rect=pygame.Rect(50, 50, 150, 30),
            manager=self.manager
        )
        star_rating.on_rating_changed = lambda rating: print(f"Star rating: {rating}")
        self.components.append(star_rating)
        
        # Example 2: Rating category with description
        rating_category = RatingCategory(
            rect=pygame.Rect(50, 100, 300, 80),
            name="Visual Appeal",
            description="How good does it look?",
            rating_type="stars",
            manager=self.manager
        )
        rating_category.set_rating_changed_callback(
            lambda rating, name="Visual Appeal": print(f"{name}: {rating}")
        )
        self.components.append(rating_category)
        
        # Example 3: Scrollable container with multiple items
        scroll_container = ScrollableContainer(
            rect=pygame.Rect(400, 50, 300, 400),
            manager=self.manager
        )
        
        # Add multiple rating categories to the container
        categories = [
            ("Shell Design", "Color and pattern quality"),
            ("Body Shape", "Overall form and proportions"),
            ("Head Features", "Facial characteristics"),
            ("Limb Structure", "Leg and fin design"),
            ("Eye Quality", "Size and color"),
            ("Overall Balance", "Harmony of all elements"),
            ("Creativity", "Originality of design"),
            ("Functionality", "Practical aspects"),
        ]
        
        for i, (name, description) in enumerate(categories):
            category = RatingCategory(
                rect=pygame.Rect(10, i * 90, 280, 80),
                name=name,
                description=description,
                rating_type="dropdown" if i % 2 == 0 else "stars",
                manager=self.manager
            )
            scroll_container.add_child(category)
            
        self.components.append(scroll_container)
        
        # Example 4: Design display
        design_display = DesignDisplay(
            rect=pygame.Rect(50, 500, 300, 200),
            manager=self.manager
        )
        
        # Mock design data
        mock_design = {
            'id': 1,
            'name': 'Example Design',
            'voting_status': 'pending',
            'rating_categories': {}
        }
        
        design_display.set_design(mock_design)
        self.components.append(design_display)
        
    def handle_event(self, event):
        """Handle events for all components."""
        for component in self.components:
            if component.handle_event(event):
                return True
        return False
        
    def update(self, dt):
        """Update all components."""
        for component in self.components:
            component.update(dt)
            
    def render(self):
        """Render all components."""
        for component in self.components:
            component.render(self.screen)


class VotingPanelExample:
    """Example using the complete VotingPanelComponent."""
    
    def __init__(self, screen, manager, game_state):
        self.screen = screen
        self.manager = manager
        self.game_state = game_state
        
        # Create voting panel component
        self.voting_panel = VotingPanelComponent(
            rect=pygame.Rect(100, 50, 900, 700),
            manager=manager,
            game_state=game_state
        )
        
        # Create the window and initialize components
        self.voting_panel.create_window(manager)
        
        # Set up event handlers
        self.voting_panel.add_event_handler('back', self._on_back)
        
    def _on_back(self, data):
        """Handle back navigation."""
        print("Back to main menu")
        
    def handle_event(self, event):
        """Handle events."""
        return self.voting_panel.handle_event(event)
        
    def update(self, dt):
        """Update voting panel."""
        self.voting_panel.update(dt)
        
    def render(self):
        """Render voting panel (handled by pygame_gui)."""
        pass


def main():
    """Run the component examples."""
    pygame.init()
    
    # Setup display
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("Component Architecture Examples")
    
    # Setup UI manager
    manager = pygame_gui.UIManager((1200, 800))
    
    # Mock game state
    class MockGameState:
        def get(self, key, default=None):
            return getattr(self, key, default)
        def set(self, key, value):
            setattr(self, key, value)
    
    game_state = MockGameState()
    game_state.money = 1000
    
    # Create examples
    simple_example = SimpleComponentExample(screen, manager)
    voting_example = VotingPanelExample(screen, manager, game_state)
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Handle events
            simple_example.handle_event(event)
            voting_example.handle_event(event)
            
            manager.process_events(event)
            
        # Update
        manager.update(dt)
        simple_example.update(dt)
        voting_example.update(dt)
        
        # Render
        screen.fill((240, 240, 240))
        simple_example.render(screen)
        
        # Draw UI manager (handles pygame_gui elements)
        manager.draw_ui(screen)
        
        # Draw info text
        font = pygame.font.Font(None, 24)
        info_text = [
            "Component Architecture Examples",
            "Left: Simple components (Star Rating, Categories, Scrollable Container)",
            "Right: Complete Voting Panel Component",
            "ESC to exit"
        ]
        
        for i, text in enumerate(info_text):
            text_surface = font.render(text, True, (0, 0, 0))
            screen.blit(text_surface, (10, 10 + i * 25))
        
        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    main()
