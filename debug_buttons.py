"""
Debug script to check why only the Quit button is showing.
"""

import sys
import os
import pygame
import pygame_gui

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_button_creation():
    """Debug button creation process."""
    print("🔍 Debugging Button Creation...")
    print("="*50)
    
    try:
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((1024, 768))
        pygame.display.set_caption("Button Debug")
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
        
        print(f"✅ Window created: {main_menu.window is not None}")
        print(f"✅ Container: {main_menu.container is not None}")
        print(f"✅ Money display: {main_menu.money_display is not None}")
        print(f"✅ Button count: {len(main_menu.menu_buttons)}")
        
        # Check each button
        for i, button in enumerate(main_menu.menu_buttons):
            print(f"  Button {i}: '{button.text}' at {button.rect}")
            
        # Check window size
        if main_menu.window:
            window_rect = main_menu.window.rect
            print(f"Window rect: {window_rect}")
            
        # Check container size
        if main_menu.container:
            container_rect = main_menu.container.rect
            print(f"Container rect: {container_rect}")
        
        # Run a short test to see what's actually rendered
        print(f"\n🎯 Running visual test (3 seconds)...")
        
        running = True
        start_time = pygame.time.get_ticks()
        
        while running:
            time_delta = clock.tick(60) / 1000.0
            current_time = pygame.time.get_ticks()
            
            if current_time - start_time > 3000:
                running = False
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                main_menu.handle_event(event)
                manager.process_events(event)
            
            manager.update(time_delta)
            main_menu.update(time_delta)
            
            # Render
            screen.fill((100, 100, 100))
            main_menu.render(screen)
            manager.draw_ui(screen)
            
            # Draw debug info
            font = pygame.font.Font(None, 24)
            debug_text = f"Buttons: {len(main_menu.menu_buttons)} - Window: {'Yes' if main_menu.window else 'No'}"
            text_surface = font.render(debug_text, True, (255, 255, 255))
            screen.blit(text_surface, (20, 20))
            
            pygame.display.flip()
        
        pygame.quit()
        
        # Check button visibility
        print(f"\n📊 Button Analysis:")
        for i, button in enumerate(main_menu.menu_buttons):
            button_visible = button.button is not None
            button_enabled = button.enabled
            print(f"  {i}. '{button.text}' - Visible: {button_visible}, Enabled: {button_enabled}")
            
        return len(main_menu.menu_buttons) == 7
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_button_creation()
    if success:
        print("\n✅ All buttons created successfully!")
    else:
        print("\n❌ Button creation issues detected!")
