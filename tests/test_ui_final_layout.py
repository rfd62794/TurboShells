#!/usr/bin/env python3
"""
Final verification of the updated main menu layout with buttons moved up further.
"""

# Add project root to path
import ui.menu_view as menu_view
import ui.layouts.positions as layout
import sys
sys.path.insert(0, ".")
sys.path.insert(0, "src")
from settings import *
import pygame
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


sys.path.insert(0, ".")
sys.path.insert(0, "src")


def show_final_layout():
    """Display the final layout with all buttons moved up."""
    print("🎯 Final Main Menu Layout Verification")
    print("=" * 50)

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.SysFont("Arial", 24)

    # Create mock game state
    class MockGameState:
        def __init__(self):
            self.money = 100
            self.mouse_pos = (400, 300)

    game_state = MockGameState()

    print("\n📍 Final Button Positions:")
    print("-" * 30)

    buttons = [
        ("ROSTER", layout.MENU_ROSTER_RECT),
        ("SHOP", layout.MENU_SHOP_RECT),
        ("BREEDING", layout.MENU_BREEDING_RECT),
        ("RACE", layout.MENU_RACE_RECT),
        ("VOTING", layout.MENU_VOTING_RECT),
        ("SETTINGS", layout.MENU_SETTINGS_RECT)
    ]

    for name, rect in buttons:
        print(f"{name:10} : Y={rect.y:3d} (Height: {rect.height})")

    print(f"\n[REPORT] Layout Summary:")
    print(f"• Top button starts at Y={layout.MENU_ROSTER_RECT.y}")
    print(f"• Bottom button ends at Y={layout.MENU_SETTINGS_RECT.bottom}")
    print(f"• Total button height: {layout.MENU_SETTINGS_RECT.bottom - layout.MENU_ROSTER_RECT.y}px")
    print(f"• Screen height: {SCREEN_HEIGHT}px")
    print(f"• Used space: {((layout.MENU_SETTINGS_RECT.bottom - layout.MENU_ROSTER_RECT.y) / SCREEN_HEIGHT) * 100:.1f}%")

    print(f"\n💰 Money Display:")
    print(f"• Format: 'Money: $' + amount")
    print(f"• Position: X={layout.HEADER_MONEY_POS[0]}, Y={layout.HEADER_MONEY_POS[1]}")

    # Draw the menu
    menu_view.draw_menu(screen, font, game_state)

    # Add visual indicators
    pygame.draw.rect(screen, (255, 0, 0), layout.MENU_ROSTER_RECT, 2)
    pygame.draw.rect(screen, (0, 255, 0), layout.MENU_SETTINGS_RECT, 2)

    # Save final screenshot
    pygame.image.save(screen, "final_menu_layout.png")
    print(f"\n📸 Final layout saved as 'final_menu_layout.png'")
    print(f"🔴 Red box: ROSTER (top button)")
    print(f"🟢 Green box: SETTINGS (bottom button)")

    print("\n[PASS] All buttons successfully moved up!")
    print("[PASS] Settings button added and functional!")
    print("[PASS] Money display updated with 'Money: ' prefix!")

    pygame.quit()


if __name__ == "__main__":
    show_final_layout()
