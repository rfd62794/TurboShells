#!/usr/bin/env python3
"""
ImGui Integration Test for TurboShells
Validates that ImGui context can be created and basic UI rendered
"""

import sys
import pygame
import imgui
import OpenGL.GL as gl
from imgui.integrations.pygame import PygameRenderer

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from ui.imgui_context import ImGuiContext
    from ui.ui_manager import UIManager
    from game.game_state_interface import TurboShellsGameStateInterface
except ImportError as e:
    print(f"❌ Failed to import TurboShells modules: {e}")
    sys.exit(1)


def test_imgui_basic():
    """Test basic ImGui functionality"""
    print("=== ImGui Basic Integration Test ===")
    
    # Initialize PyGame
    pygame.init()
    screen = pygame.display.set_mode((800, 600), pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption("ImGui Integration Test")
    clock = pygame.time.Clock()
    
    try:
        # Test ImGui context creation
        print("Creating ImGui context...")
        imgui_context = ImGuiContext(screen)
        
        if not imgui_context.initialize():
            print("❌ Failed to initialize ImGui context")
            return False
        
        print("✅ ImGui context initialized successfully")
        
        # Test UI Manager
        print("Creating UI Manager...")
        ui_manager = UIManager(screen.get_rect())
        
        if not ui_manager.initialize(screen):
            print("❌ Failed to initialize UI Manager")
            return False
        
        print("✅ UI Manager initialized successfully")
        
        # Test game state interface
        print("Creating Game State Interface...")
        
        # Mock game object
        class MockGame:
            def __init__(self):
                self.money = 1000
                self.roster = []
                self.state = "menu"
        
        mock_game = MockGame()
        game_state = TurboShellsGameStateInterface(mock_game)
        
        print("✅ Game State Interface created successfully")
        
        # Basic rendering test
        print("Testing basic rendering...")
        frame_count = 0
        running = True
        
        while running and frame_count < 60:  # Run for 60 frames (~1 second)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                
                # Test event handling
                ui_manager.handle_event(event)
            
            # Clear screen
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            
            # Begin ImGui frame
            imgui_context.begin_frame()
            
            # Simple test UI
            imgui.begin("ImGui Test Window", True)
            imgui.text("TurboShells ImGui Integration Test")
            imgui.text(f"Frame: {frame_count}")
            
            if imgui.button("Test Button"):
                print("✅ Button clicked!")
            
            money = game_state.get('money', 0)
            imgui.text(f"Game Money: ${money}")
            
            imgui.end()
            
            # End frame
            imgui_context.end_frame()
            
            pygame.display.flip()
            clock.tick(60)
            frame_count += 1
        
        print("✅ Basic rendering test successful")
        
        # Cleanup
        ui_manager.shutdown()
        pygame.quit()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_imgui_components():
    """Test ImGui components integration"""
    print("\n=== ImGui Components Test ===")
    
    try:
        # Import components
        from ui.panels.settings_panel import SettingsPanel
        from ui.data_binding import DataBindingManager
        
        print("✅ Component imports successful")
        
        # Mock game and interfaces
        class MockGame:
            def __init__(self):
                self.money = 500
                self.roster = []
                self.state = "menu"
        
        mock_game = MockGame()
        game_state = TurboShellsGameStateInterface(mock_game)
        data_binding = DataBindingManager()
        
        # Test settings panel creation
        settings_panel = SettingsPanel(game_state, data_binding)
        print("✅ Settings panel created successfully")
        
        # Test data binding
        data_binding.bind_property(
            "test_money", mock_game, "money", "test_display"
        )
        print("✅ Data binding created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Components test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all ImGui integration tests"""
    print("TurboShells ImGui Integration Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Basic ImGui functionality
    if test_imgui_basic():
        tests_passed += 1
    
    # Test 2: Component integration
    if test_imgui_components():
        tests_passed += 1
    
    # Results
    print(f"\n=== Test Results ===")
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All ImGui integration tests passed!")
        print("Your environment is ready for ImGui hybrid architecture.")
        return True
    else:
        print("❌ Some tests failed. Check the error messages above.")
        return False


if __name__ == "__main__":
    from pathlib import Path
    
    success = main()
    sys.exit(0 if success else 1)
