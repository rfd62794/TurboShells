"""
Debug script to check container and button visibility issues.
"""

import sys
import os
import pygame
import pygame_gui

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_container_setup():
    """Debug container and button setup in detail."""
    print("🔍 Debugging Container Setup...")
    print("="*50)
    
    try:
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((1024, 768))
        pygame.display.set_caption("Container Debug")
        manager = pygame_gui.UIManager((1024, 768))
        clock = pygame.time.Clock()
        
        # Import and create game state
        from game.game_state_interface import TurboShellsGameStateInterface
        
        class MockGame:
            def __init__(self):
                self.money = 2741
                self.state = "main_menu"
                
            def get(self, key, default=None):
                return getattr(self, key, default)
                
            class MockUIManager:
                def toggle_panel(self, panel_id):
                    print(f"Toggle panel: {panel_id}")
                    
            ui_manager = MockUIManager()
        
        mock_game = MockGame()
        game_state = TurboShellsGameStateInterface(mock_game)
        
        # Import Main Menu
        from ui.panels.main_menu_panel_refactored import MainMenuPanelRefactored
        
        print("✅ Creating Main Menu...")
        main_menu = MainMenuPanelRefactored(game_state)
        main_menu.manager = manager
        main_menu._create_window()
        
        print(f"✅ Window: {main_menu.window is not None}")
        print(f"✅ Container: {main_menu.container is not None}")
        
        # Get detailed window info
        if main_menu.window:
            window_rect = main_menu.window.rect
            print(f"Window rect: {window_rect}")
            print(f"Window position: ({window_rect.x}, {window_rect.y})")
            print(f"Window size: ({window_rect.width}, {window_rect.height})")
        
        # Get detailed container info
        if main_menu.container:
            container_rect = main_menu.container.rect
            print(f"Container rect: {container_rect}")
            print(f"Container position: ({container_rect.x}, {container_rect.y})")
            print(f"Container size: ({container_rect.width}, {container_rect.height})")
        
        # Check each button's pygame_gui element
        print(f"\n🔘 Button Details:")
        for i, button in enumerate(main_menu.menu_buttons):
            print(f"  Button {i}: '{button.text}'")
            print(f"    - Component rect: {button.rect}")
            print(f"    - pygame_gui element: {button.button}")
            if button.button:
                button_rect = button.button.rect
                print(f"    - pygame_gui rect: {button_rect}")
                print(f"    - pygame_gui visible: {button.button.visible}")
                # Check if button is enabled using is_enabled method
                try:
                    enabled = button.button.is_enabled()
                    print(f"    - pygame_gui enabled: {enabled}")
                except:
                    print(f"    - pygame_gui enabled: (method not available)")
            print()
        
        # Test with a simple direct button creation for comparison
        print("🧪 Testing Direct Button Creation...")
        if main_menu.container:
            test_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(10, 10, 200, 40),
                text="TEST BUTTON",
                manager=manager,
                container=main_menu.container
            )
            print(f"✅ Direct test button created: {test_button}")
            print(f"  - Test button rect: {test_button.rect}")
            print(f"  - Test button visible: {test_button.visible}")
        
        # Run a visual test
        print(f"\n🎯 Running visual test (5 seconds)...")
        
        running = True
        start_time = pygame.time.get_ticks()
        
        while running:
            time_delta = clock.tick(60) / 1000.0
            current_time = pygame.time.get_ticks()
            
            if current_time - start_time > 5000:
                running = False
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                main_menu.handle_event(event)
                manager.process_events(event)
            
            manager.update(time_delta)
            main_menu.update(time_delta)
            
            # Render
            screen.fill((50, 50, 50))
            main_menu.render(screen)
            manager.draw_ui(screen)
            
            # Draw debug info
            font = pygame.font.Font(None, 24)
            debug_texts = [
                f"Window: {'Yes' if main_menu.window else 'No'}",
                f"Container: {'Yes' if main_menu.container else 'No'}",
                f"Buttons: {len(main_menu.menu_buttons)}",
                f"Test Button: {'Yes' if 'test_button' in locals() else 'No'}"
            ]
            
            for i, text in enumerate(debug_texts):
                text_surface = font.render(text, True, (255, 255, 255))
                screen.blit(text_surface, (20, 20 + i * 30))
            
            pygame.display.flip()
        
        pygame.quit()
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_container_setup()
