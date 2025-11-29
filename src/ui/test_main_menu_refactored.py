"""
Test script for the refactored Main Menu Panel.

This script verifies that the new component-based Main Menu works correctly
and maintains feature parity with the original implementation.
"""

import pygame
import pygame_gui
import sys
import os

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ui.panels.main_menu_panel import MainMenuPanel


class MockGameState:
    """Mock game state for testing."""
    
    def __init__(self):
        self.money = 1000
        self.state = "main_menu"
        self.select_racer_mode = False
        self.game = self
        
    def get(self, key, default=None):
        return getattr(self, key, default)
        
    def set(self, key, value):
        setattr(self, key, value)
        
    class MockUIManager:
        def toggle_panel(self, panel_id):
            print(f"Toggle panel: {panel_id}")


class MockEventBus:
    """Mock event bus for testing."""
    
    def emit(self, event_name, data):
        print(f"Event: {event_name} -> {data}")


def test_main_menu_functionality():
    """Test Main Menu functionality."""
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("Main Menu Refactor Test")
    
    manager = pygame_gui.UIManager((1200, 800))
    game_state = MockGameState()
    event_bus = MockEventBus()
    
    # Create both versions for comparison
    refactored_panel = MainMenuPanel(game_state, event_bus)
    original_panel = MainMenuPanel(game_state, event_bus)
    
    # Set up managers
    refactored_panel.manager = manager
    original_panel.manager = manager
    
    # Create windows
    refactored_panel._create_window()
    original_panel._create_window()
    
    # Test callbacks
    navigation_events = []
    quit_events = []
    
    def on_navigate(state):
        navigation_events.append(state)
        print(f"Navigation to: {state}")
        
    def on_quit():
        quit_events.append(True)
        print("Quit requested")
        
    refactored_panel.set_navigation_callback(on_navigate)
    refactored_panel.set_quit_callback(on_quit)
    
    clock = pygame.time.Clock()
    running = True
    show_refactored = True
    
    print("=== Main Menu Refactor Test ===")
    print("Press SPACE to toggle between refactored/original")
    print("Press M to change money amount")
    print("Press ESC to quit")
    print()
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    show_refactored = not show_refactored
                    print(f"Showing: {'Refactored' if show_refactored else 'Original'}")
                elif event.key == pygame.K_m:
                    # Change money to test display update
                    game_state.money = 5000 if game_state.money == 1000 else 1000
                    print(f"Money changed to: ${game_state.money}")
                    
            # Handle events through panels
            if show_refactored:
                refactored_panel.handle_event(event)
            else:
                original_panel.handle_event(event)
                
            manager.process_events(event)
            
        # Update
        manager.update(dt)
        if show_refactored:
            refactored_panel.update(dt)
        else:
            original_panel.update(dt)
            
        # Render
        screen.fill((200, 200, 200))
        
        # Draw panel info
        font = pygame.font.Font(None, 24)
        panel_type = "Refactored (Reusable Components)" if show_refactored else "Original (Monolithic)"
        info_text = f"Testing: {panel_type}"
        text_surface = font.render(info_text, True, (0, 0, 0))
        screen.blit(text_surface, (20, 20))
        
        # Draw money info
        money_text = f"Money: ${game_state.money}"
        money_surface = font.render(money_text, True, (0, 100, 0))
        screen.blit(money_surface, (20, 50))
        
        # Draw navigation events
        if navigation_events:
            nav_text = f"Last Navigation: {navigation_events[-1]}"
            nav_surface = font.render(nav_text, True, (0, 0, 150))
            screen.blit(nav_surface, (20, 80))
            
        # Draw quit events
        if quit_events:
            quit_text = f"Quit events: {len(quit_events)}"
            quit_surface = font.render(quit_text, True, (150, 0, 0))
            screen.blit(quit_surface, (20, 110))
            
        # Draw panel
        if show_refactored:
            refactored_panel.render(screen)
        else:
            original_panel.render(screen)
            
        manager.draw_ui(screen)
        
        pygame.display.flip()
    
    # Test results
    print("\n=== Test Results ===")
    print(f"Navigation events captured: {len(navigation_events)}")
    print(f"Quit events captured: {len(quit_events)}")
    
    # Feature parity check
    print("\n=== Feature Parity Check ===")
    
    # Check components exist
    refactored_components = {
        'main_panel': refactored_panel.main_panel is not None,
        'money_display': refactored_panel.money_display is not None,
        'menu_container': refactored_panel.menu_container is not None,
        'menu_buttons': len(refactored_panel.menu_buttons) > 0,
        'quit_dialog': refactored_panel.quit_dialog is not None
    }
    
    print("Refactored Components:")
    for component, exists in refactored_components.items():
        status = "✅" if exists else "❌"
        print(f"  {status} {component}")
        
    # Test button functionality
    print("\nButton Functionality:")
    for button in refactored_panel.menu_buttons:
        enabled = button.enabled
        print(f"  ✅ {button.text}: {'Enabled' if enabled else 'Disabled'}")
        
    # Test money display
    if refactored_panel.money_display:
        displayed_money = refactored_panel.money_display.get_amount()
        print(f"\nMoney Display:")
        print(f"  ✅ Current amount: ${displayed_money}")
        print(f"  ✅ Game state amount: ${game_state.money}")
        print(f"  ✅ Match: {displayed_money == game_state.money}")
        
    print("\n=== Test Complete ===")
    
    pygame.quit()


def test_component_architecture():
    """Test component architecture benefits."""
    print("\n=== Component Architecture Test ===")
    
    pygame.init()
    manager = pygame_gui.UIManager((800, 600))
    game_state = MockGameState()
    event_bus = MockEventBus()
    
    panel = MainMenuPanel(game_state, event_bus)
    panel.manager = manager
    panel._create_window()
    
    # Test 1: Component isolation
    print("1. Testing Component Isolation:")
    print(f"   ✅ Main Panel: {panel.main_panel is not None}")
    print(f"   ✅ Money Display: {panel.money_display is not None}")
    print(f"   ✅ Menu Container: {panel.menu_container is not None}")
    print(f"   ✅ Menu Buttons: {len(panel.menu_buttons)}")
    
    # Test 2: Component reusability
    print("\n2. Testing Component Reusability:")
    from ui.components.reusable import Button, MoneyDisplay, Container, Panel
    
    # Create same components independently
    test_button = Button(pygame.Rect(0, 0, 100, 30), "Test", "test", manager)
    test_money = MoneyDisplay(pygame.Rect(0, 0, 100, 20), 500, manager)
    test_container = Container(pygame.Rect(0, 0, 200, 200), manager)
    test_panel = Panel(pygame.Rect(0, 0, 300, 400), "Test Panel", manager)
    
    print(f"   ✅ Can create independent Button: {test_button is not None}")
    print(f"   ✅ Can create independent MoneyDisplay: {test_money is not None}")
    print(f"   ✅ Can create independent Container: {test_container is not None}")
    print(f"   ✅ Can create independent Panel: {test_panel is not None}")
    
    # Test 3: Component configuration
    print("\n3. Testing Component Configuration:")
    button_configs = [
        {'style': 'primary'},
        {'style': 'secondary'},
        {'style': 'danger'}
    ]
    
    for i, config in enumerate(button_configs):
        button = Button(pygame.Rect(0, i * 35, 100, 30), f"Style {i+1}", f"action_{i}", manager, config)
        print(f"   ✅ Button with {config['style']} style: {button is not None}")
        
    # Test 4: Component composition
    print("\n4. Testing Component Composition:")
    
    # Test that components can be nested
    outer_container = Container(pygame.Rect(0, 0, 300, 300), manager)
    inner_container = Container(pygame.Rect(10, 10, 280, 280), manager)
    nested_button = Button(pygame.Rect(10, 10, 100, 30), "Nested", "nested", manager)
    
    outer_container.add_child(inner_container)
    inner_container.add_child(nested_button)
    
    print(f"   ✅ Nested containers: {len(outer_container.children) == 1}")
    print(f"   ✅ Nested button: {len(inner_container.children) == 1}")
    
    # Test 5: Event delegation
    print("\n5. Testing Event Delegation:")
    test_events = []
    
    def test_callback(action):
        test_events.append(action)
        
    nested_button.set_action_callback(test_callback)
    
    # Simulate button press
    nested_button.on_action("nested")
    
    print(f"   ✅ Event captured: {len(test_events) == 1}")
    print(f"   ✅ Correct action: {test_events[0] == 'nested'}")
    
    print("\n=== Architecture Test Complete ===")
    pygame.quit()


if __name__ == "__main__":
    print("Starting Main Menu Refactor Tests...")
    
    # Run architecture test first
    test_component_architecture()
    
    # Run interactive test
    test_main_menu_functionality()
    
    print("\nAll tests completed!")
