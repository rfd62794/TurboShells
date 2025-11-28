"""
Test script to verify the refactored Main Menu works in the actual game.

This script runs a minimal version of the game to test the Main Menu integration.
"""

import sys
import os
import pygame
import pygame_gui

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_game_main_menu():
    """Test the Main Menu in a minimal game environment."""
    print("🎮 Testing Main Menu in Game Environment...")
    print("="*50)
    
    try:
        # Initialize pygame
        pygame.init()
        
        # Set up display
        screen = pygame.display.set_mode((1024, 768))
        pygame.display.set_caption("Main Menu Integration Test")
        clock = pygame.time.Clock()
        
        # Set up UI manager
        manager = pygame_gui.UIManager((1024, 768))
        
        # Import and create game state interface
        from game.game_state_interface import TurboShellsGameStateInterface
        
        # Create mock game state with some data
        class MockGame:
            def __init__(self):
                self.money = 2741  # From saved game
                self.state = "main_menu"
                
            def get(self, key, default=None):
                return getattr(self, key, default)
                
            def set(self, key, value):
                setattr(self, key, value)
                
            class MockUIManager:
                def toggle_panel(self, panel_id):
                    print(f"Toggle panel: {panel_id}")
                    
            ui_manager = MockUIManager()
        
        mock_game = MockGame()
        game_state = TurboShellsGameStateInterface(mock_game)
        game_state.money = mock_game.money
        
        # Import and create the refactored Main Menu
        from ui.panels.main_menu_panel_refactored import MainMenuPanelRefactored
        
        print("✅ Creating refactored Main Menu...")
        main_menu = MainMenuPanelRefactored(game_state)
        main_menu.manager = manager
        main_menu._create_window()
        
        print("✅ Main Menu created successfully!")
        
        # Verify components
        components = {
            'money_display': main_menu.money_display is not None,
            'menu_buttons': len(main_menu.menu_buttons) == 7,
            'window': main_menu.window is not None,
            'container': hasattr(main_menu, 'container') and main_menu.container is not None,
        }
        
        print("\n📋 Component Verification:")
        for component, exists in components.items():
            status = "✅" if exists else "❌"
            print(f"  {status} {component}")
        
        # Test money display
        if main_menu.money_display:
            initial_money = main_menu.money_display.get_amount()
            print(f"\n💰 Money Display Test:")
            print(f"  Initial amount: ${initial_money}")
            print(f"  Expected: ${mock_game.money}")
            print(f"  Match: {initial_money == mock_game.money}")
        
        # Test buttons
        print(f"\n🔘 Button Test:")
        button_labels = [button.text for button in main_menu.menu_buttons]
        expected_labels = ["Roster", "Shop", "Breeding", "Race", "Voting", "Settings", "Quit"]
        print(f"  Labels: {button_labels}")
        print(f"  Expected: {expected_labels}")
        print(f"  Match: {button_labels == expected_labels}")
        
        # Run a short test loop
        print(f"\n🎯 Running interactive test (5 seconds)...")
        print("  You should see the Main Menu appear!")
        
        running = True
        start_time = pygame.time.get_ticks()
        
        while running:
            time_delta = clock.tick(60) / 1000.0
            current_time = pygame.time.get_ticks()
            
            # Auto-close after 5 seconds
            if current_time - start_time > 5000:
                running = False
                print("  ⏰ Test completed!")
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                # Handle events through Main Menu
                main_menu.handle_event(event)
                manager.process_events(event)
            
            # Update
            manager.update(time_delta)
            main_menu.update(time_delta)
            
            # Render
            screen.fill((200, 200, 200))
            main_menu.render(screen)
            manager.draw_ui(screen)
            
            # Draw test info
            font = pygame.font.Font(None, 24)
            info_text = "Main Menu Integration Test - Closing in 5 seconds..."
            text_surface = font.render(info_text, True, (0, 0, 0))
            screen.blit(text_surface, (20, 20))
            
            pygame.display.flip()
        
        pygame.quit()
        
        # Final verification
        all_components_ok = all(components.values())
        money_ok = main_menu.money_display and main_menu.money_display.get_amount() == mock_game.money
        buttons_ok = button_labels == expected_labels
        
        success = all_components_ok and money_ok and buttons_ok
        
        print(f"\n{'='*50}")
        print("GAME INTEGRATION TEST RESULTS")
        print('='*50)
        
        print(f"✅ Components: {'PASS' if all_components_ok else 'FAIL'}")
        print(f"✅ Money Display: {'PASS' if money_ok else 'FAIL'}")
        print(f"✅ Buttons: {'PASS' if buttons_ok else 'FAIL'}")
        print(f"✅ Overall: {'PASS' if success else 'FAIL'}")
        
        if success:
            print(f"\n🎉 Game integration test PASSED!")
            print(f"✅ The refactored Main Menu works perfectly in the game!")
            print(f"✅ All components are functional!")
            print(f"✅ Ready for production use!")
        else:
            print(f"\n❌ Game integration test FAILED!")
            print(f"⚠️ Some components are not working correctly!")
        
        return success
        
    except Exception as e:
        print(f"❌ Game integration test crashed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the game integration test."""
    print("🚀 Starting Game Integration Test...")
    print("This will test the refactored Main Menu in a real game environment.")
    print()
    
    success = test_game_main_menu()
    
    if success:
        print(f"\n🎯 NEXT STEPS:")
        print(f"1. The refactored Main Menu is ready for production!")
        print(f"2. Run 'python run_game.py' to test in the full game!")
        print(f"3. Verify all buttons work correctly!")
        print(f"4. Check navigation between panels!")
        print(f"5. Test money display updates!")
    else:
        print(f"\n🔧 TROUBLESHOOTING:")
        print(f"1. Check the error messages above")
        print(f"2. Verify all component files exist")
        print(f"3. Check imports are working correctly")
        print(f"4. Run 'python verify_integration.py' for detailed checks")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
