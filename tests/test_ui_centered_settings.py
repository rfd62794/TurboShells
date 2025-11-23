#!/usr/bin/env python3
"""
Test script to verify the centered settings menu and responsive layout.
"""

# Add project root to path
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


import pygame
import sys
import sys
sys.path.insert(0, ".")
sys.path.insert(0, "src")
from settings import *
from src.managers.settings_manager import SettingsManager


def test_centered_settings():
    """Test the centered settings menu with different window sizes."""
    print("[TEST] Testing Centered Settings Menu...")

    try:
        pygame.init()

        # Test different screen sizes
        test_sizes = [
            (800, 600),   # Small
            (1024, 768),  # Default
            (1280, 720),  # HD
            (1920, 1080),  # Full HD
        ]

        for width, height in test_sizes:
            print(f"\n📐 Testing {width}x{height}...")

            # Create screen
            screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            screen_rect = pygame.Rect(0, 0, width, height)

            # Create settings manager
            settings_manager = SettingsManager(screen_rect)

            # Check if panel is centered
            panel = settings_manager.settings_view.panel_rect
            expected_center_x = width // 2
            expected_center_y = height // 2
            actual_center_x = panel.centerx
            actual_center_y = panel.centery

            # Check centering (allow 1px tolerance)
            if abs(actual_center_x - expected_center_x) <= 1:
                print(f"  [PASS] Panel centered horizontally: {actual_center_x} ≈ {expected_center_x}")
            else:
                print(f"  [FAIL] Panel not centered: X={actual_center_x} (expected {expected_center_x})")

            if abs(actual_center_y - expected_center_y) <= 1:
                print(f"  [PASS] Panel centered vertically: {actual_center_y} ≈ {expected_center_y}")
            else:
                print(f"  [FAIL] Panel not centered: Y={actual_center_y} (expected {expected_center_y})")

            # Check responsive sizing
            max_width = min(width * 0.7, 800)
            max_height = min(height * 0.8, 600)

            if panel.width <= max_width + 1:  # Allow 1px tolerance
                print(f"  [PASS] Panel width responsive: {panel.width} ≤ {max_width}")
            else:
                print(f"  [FAIL] Panel width too large: {panel.width} > {max_width}")

            if panel.height <= max_height + 1:  # Allow 1px tolerance
                print(f"  [PASS] Panel height responsive: {panel.height} ≤ {max_height}")
            else:
                print(f"  [FAIL] Panel height too large: {panel.height} > {max_height}")

            # Test window resize simulation
            new_width, new_height = width + 100, height + 100
            new_screen_rect = pygame.Rect(0, 0, new_width, new_height)
            settings_manager.update_screen_rect(new_screen_rect)

            # Check if panel re-centered after resize
            resized_panel = settings_manager.settings_view.panel_rect
            new_center_x = new_width // 2
            new_center_y = new_height // 2

            if abs(resized_panel.centerx - new_center_x) <= 1:
                print(f"  [PASS] Panel re-centered after resize: {resized_panel.centerx} ≈ {new_center_x}")
            else:
                print(f"  [FAIL] Panel failed to re-center: X={resized_panel.centerx} (expected {new_center_x})")

        print("\n[PASS] Centered settings menu tests completed!")
        return True

    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        pygame.quit()


if __name__ == "__main__":
    success = test_centered_settings()
    sys.exit(0 if success else 1)
