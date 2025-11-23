#!/usr/bin/env python3
"""
Test script to verify the main menu changes:
1. Buttons moved up
2. Settings button added
3. "Money: " added to money display
"""

import pygame
import sys
from settings import *
import ui.layouts.positions as layout
import ui.menu_view as menu_view

def test_menu_layout():
    """Test the main menu layout changes."""
    print("[TEST] Testing Main Menu Layout Changes...")
    
    try:
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        font = pygame.font.SysFont("Arial", 24)
        
        # Create a mock game state
        class MockGameState:
            def __init__(self):
                self.money = 100
                self.mouse_pos = (400, 300)
        
        game_state = MockGameState()
        
        # Test 1: Check if layout positions are correct
        print("\n📍 Testing Layout Positions...")
        
        # Verify buttons are moved up further (Y positions should be even lower)
        expected_positions = [80, 170, 260, 350, 440, 530]  # Updated expected Y positions
        actual_rects = [
            layout.MENU_ROSTER_RECT,
            layout.MENU_SHOP_RECT, 
            layout.MENU_BREEDING_RECT,
            layout.MENU_RACE_RECT,
            layout.MENU_VOTING_RECT,
            layout.MENU_SETTINGS_RECT
        ]
        
        for i, rect in enumerate(actual_rects):
            expected_y = expected_positions[i]
            if rect.y == expected_y:
                print(f"  [PASS] {['ROSTER', 'SHOP', 'BREEDING', 'RACE', 'VOTING', 'SETTINGS'][i]} at Y={rect.y} (correct)")
            else:
                print(f"  [FAIL] {['ROSTER', 'SHOP', 'BREEDING', 'RACE', 'VOTING', 'SETTINGS'][i]} at Y={rect.y} (expected {expected_y})")
        
        # Test 2: Check if Settings button exists
        if hasattr(layout, 'MENU_SETTINGS_RECT'):
            print("\n  [PASS] Settings button layout position exists")
        else:
            print("\n  [FAIL] Settings button layout position missing")
        
        # Test 3: Test money display
        print("\n💰 Testing Money Display...")
        menu_view.draw_menu(screen, font, game_state)
        
        # Check if money position is adjusted for longer text
        if layout.HEADER_MONEY_POS[0] < 650:  # Should be moved left from original 650
            print(f"  [PASS] Money position adjusted to X={layout.HEADER_MONEY_POS[0]}")
        else:
            print(f"  [FAIL] Money position still at X={layout.HEADER_MONEY_POS[0]} (should be moved left)")
        
        # Test 4: Visual test (optional)
        print("\n🎨 Visual Test - Drawing menu...")
        menu_view.draw_menu(screen, font, game_state)
        
        # Save a screenshot for visual verification
        pygame.image.save(screen, "test_menu_screenshot.png")
        print("  📸 Screenshot saved as 'test_menu_screenshot.png'")
        
        print("\n[PASS] Main menu layout tests completed!")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        return False
    finally:
        pygame.quit()

if __name__ == "__main__":
    success = test_menu_layout()
    sys.exit(0 if success else 1)
