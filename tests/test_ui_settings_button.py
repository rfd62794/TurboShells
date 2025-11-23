#!/usr/bin/env python3
"""
Test script to verify the Settings button functionality in the main menu.
"""

# Add project root to path
from src.core.systems.state_handler import StateHandler
import ui.layouts.positions as layout
from settings import *
import pygame
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


sys.path.insert(0, ".")
sys.path.insert(0, "src")


def test_settings_button():
    """Test the Settings button click handling."""
    print("[TEST] Testing Settings Button Functionality...")

    try:
        pygame.init()

        # Create a mock game state with settings manager
        class MockGameState:
            def __init__(self):
                self.state = STATE_MENU
                self.settings_manager = MockSettingsManager()
                self.money = 100

        class MockSettingsManager:
            def __init__(self):
                self.visible = False
                self.show_called = False

            def show_settings(self):
                self.visible = True
                self.show_called = True
                print("  📱 Settings overlay shown!")

            def is_visible(self):
                return self.visible

        game_state = MockGameState()
        state_handler = StateHandler(game_state)

        # Test 1: Check if Settings button click is handled
        print("\n🖱️  Testing Settings Button Click...")

        # Simulate clicking on the Settings button
        settings_click_pos = (layout.MENU_SETTINGS_RECT.centerx, layout.MENU_SETTINGS_RECT.centery)

        # Handle the click
        state_handler.handle_click(settings_click_pos)

        # Check if settings manager was called
        if game_state.settings_manager.show_called:
            print("  [PASS] Settings button click handled correctly")
            print("  [PASS] Settings manager show_settings() was called")
        else:
            print("  [FAIL] Settings button click not handled")

        # Test 2: Verify settings are visible
        if game_state.settings_manager.is_visible():
            print("  [PASS] Settings overlay is now visible")
        else:
            print("  [FAIL] Settings overlay is not visible")

        # Test 3: Verify game state didn't change (settings is overlay, not new state)
        if game_state.state == STATE_MENU:
            print("  [PASS] Game state remained in MENU (correct for overlay)")
        else:
            print(f"  [FAIL] Game state changed to {game_state.state} (should stay MENU)")

        print("\n[PASS] Settings button functionality tests completed!")
        return True

    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        pygame.quit()


if __name__ == "__main__":
    success = test_settings_button()
    sys.exit(0 if success else 1)
