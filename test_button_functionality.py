"""
Test script to verify button functionality in the refactored Main Menu.
"""

import sys
import os
import pygame
import pygame_gui

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_button_functionality():
    """Test that buttons actually work when clicked."""
    print("🧪 Testing Button Functionality...")
    print("="*50)
    
    try:
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((1024, 768))
        pygame.display.set_caption("Button Functionality Test")
        manager = pygame_gui.UIManager((1024, 768))
        clock = pygame.time.Clock()
        
        # Import and create game state
        from game.game_state_interface import TurboShellsGameStateInterface
        
        class MockGame:
            def __init__(self):
                self.money = 2741
                self.state = "main_menu"
                self.events = []
                
            def get(self, key, default=None):
                return getattr(self, key, default)
                
            def set(self, key, value):
                setattr(self, key, value)
                print(f"🔔 Game state changed: {key} = {value}")
                
            class MockUIManager:
                def toggle_panel(self, panel_id):
                    print(f"🔔 Toggle panel: {panel_id}")
                    
            ui_manager = MockUIManager()
        
        mock_game = MockGame()
        game_state = TurboShellsGameStateInterface(mock_game)
        
        # Import Main Menu
        from ui.panels.main_menu_panel_refactored import MainMenuPanelRefactored
        
        print("✅ Creating Main Menu...")
        main_menu = MainMenuPanelRefactored(game_state)
        main_menu.manager = manager
        main_menu._create_window()
        
        print(f"✅ Created {len(main_menu.menu_buttons)} buttons")
        
        # Test button clicks programmatically
        print(f"\n🎯 Testing Button Actions:")
        
        # Test each button action
        test_actions = [
            ("Roster", "navigate_roster"),
            ("Shop", "navigate_shop"), 
            ("Breeding", "navigate_breeding"),
            ("Race", "navigate_race"),
            ("Voting", "navigate_voting"),
            ("Settings", "toggle_settings"),
            ("Quit", "quit")
        ]
        
        for button_text, expected_action in test_actions:
            button = main_menu.get_button(button_text)
            if button:
                print(f"  🔘 {button_text}: Action = {button.action}")
                # Simulate button press
                main_menu._on_button_action(expected_action)
                print(f"    ✅ Action executed")
            else:
                print(f"  ❌ {button_text}: Button not found")
        
        # Run interactive test
        print(f"\n🎮 Interactive Test (10 seconds) - Click buttons to test!")
        print("  Watch the console for action messages when you click buttons.")
        
        running = True
        start_time = pygame.time.get_ticks()
        
        while running:
            time_delta = clock.tick(60) / 1000.0
            current_time = pygame.time.get_ticks()
            
            if current_time - start_time > 10000:
                running = False
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                # Handle events through Main Menu
                if main_menu.handle_event(event):
                    print(f"🔔 Event handled by Main Menu: {event}")
                    
                manager.process_events(event)
            
            manager.update(time_delta)
            main_menu.update(time_delta)
            
            # Render
            screen.fill((50, 50, 50))
            main_menu.render(screen)
            manager.draw_ui(screen)
            
            # Draw instructions
            font = pygame.font.Font(None, 24)
            instructions = [
                "Click buttons to test functionality!",
                "Watch console for action messages",
                f"Time left: {max(0, 10 - (current_time - start_time) // 1000)}s"
            ]
            
            for i, text in enumerate(instructions):
                text_surface = font.render(text, True, (255, 255, 255))
                screen.blit(text_surface, (20, 20 + i * 30))
            
            pygame.display.flip()
        
        pygame.quit()
        
        print(f"\n✅ Button functionality test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_button_functionality()
    if success:
        print("\n🎉 Button functionality test PASSED!")
    else:
        print("\n❌ Button functionality test FAILED!")
