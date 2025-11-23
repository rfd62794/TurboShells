#!/usr/bin/env python3
"""
Test script for the settings UI system.
Tests all major components of the Phase 3 implementation.
"""

import sys
import os
import pygame

# Add the current directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_settings_view():
    """Test the settings view component."""
    print("[TEST] Testing Settings View...")

    try:
        from ui.settings_view import SettingsView, SettingsTab

        # Initialize pygame for testing
        pygame.init()
        screen = pygame.display.set_mode((1024, 768))
        screen_rect = screen.get_rect()

        # Create settings view
        settings_view = SettingsView(screen_rect)

        # Test basic properties
        assert settings_view.visible == False, "Settings should start hidden"
        assert settings_view.active_tab == SettingsTab.GRAPHICS, "Default tab should be graphics"

        # Test show/hide
        settings_view.show()
        assert settings_view.visible, "Settings should be visible after show()"

        settings_view.hide()
        assert settings_view.visible == False, "Settings should be hidden after hide()"

        # Test tab switching
        settings_view.show()
        settings_view._switch_tab(SettingsTab.AUDIO)
        assert settings_view.active_tab == SettingsTab.AUDIO, "Tab should have switched to audio"

        # Test tab content exists
        assert SettingsTab.GRAPHICS in settings_view.tab_content, "Graphics tab should have content"
        assert SettingsTab.AUDIO in settings_view.tab_content, "Audio tab should have content"

        print("[PASS] Settings View tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Settings View test failed: {e}")
        return False


def test_ui_components():
    """Test the UI components library."""
    print("[TEST] Testing UI Components...")

    try:
        from ui.ui_components import Button, Checkbox, Slider, Dropdown, Label, Panel, ComponentStyle

        # Initialize pygame for testing
        pygame.init()
        screen = pygame.display.set_mode((1024, 768))

        # Test component creation
        button_rect = pygame.Rect(100, 100, 100, 30)
        button = Button(button_rect, "Test Button")
        assert button.text == "Test Button", "Button text not set correctly"
        assert button.enabled, "Button should be enabled by default"

        # Test checkbox
        checkbox_rect = pygame.Rect(100, 150, 20, 20)
        checkbox = Checkbox(checkbox_rect, checked=False)
        assert checkbox.checked == False, "Checkbox should start unchecked"

        # Test slider
        slider_rect = pygame.Rect(100, 200, 200, 20)
        slider = Slider(slider_rect, min_value=0.0, max_value=1.0, initial_value=0.5)
        assert slider.value == 0.5, "Slider value not set correctly"
        assert slider.min_value == 0.0, "Slider min value incorrect"
        assert slider.max_value == 1.0, "Slider max value incorrect"

        # Test dropdown
        dropdown_rect = pygame.Rect(100, 250, 150, 25)
        dropdown = Dropdown(dropdown_rect, ["Option 1", "Option 2", "Option 3"], selected_index=1)
        assert dropdown.selected_index == 1, "Dropdown selection incorrect"
        assert len(dropdown.options) == 3, "Dropdown options count incorrect"

        # Test label
        label_rect = pygame.Rect(100, 300, 100, 20)
        label = Label(label_rect, "Test Label")
        assert label.text == "Test Label", "Label text not set correctly"

        # Test panel
        panel_rect = pygame.Rect(100, 350, 200, 150)
        panel = Panel(panel_rect)
        assert len(panel.children) == 0, "Panel should start with no children"

        # Test adding children to panel
        panel.add_child(button)
        assert len(panel.children) == 1, "Panel should have one child after adding"

        print("[PASS] UI Components tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] UI Components test failed: {e}")
        return False


def test_settings_manager():
    """Test the settings manager integration."""
    print("[TEST] Testing Settings Manager...")

    try:
        from managers.settings_manager import SettingsManager, SettingsTab

        # Initialize pygame for testing
        pygame.init()
        screen = pygame.display.set_mode((1024, 768))
        screen_rect = screen.get_rect()

        # Create settings manager
        settings_manager = SettingsManager(screen_rect)

        # Test basic properties
        assert settings_manager.is_visible() == False, "Settings should start hidden"

        # Test show/hide
        settings_manager.show_settings()
        assert settings_manager.is_visible(), "Settings should be visible after show()"

        settings_manager.hide_settings()
        assert settings_manager.is_visible() == False, "Settings should be hidden after hide()"

        # Test toggle
        settings_manager.toggle_settings()
        assert settings_manager.is_visible(), "Settings should be visible after toggle"

        settings_manager.toggle_settings()
        assert settings_manager.is_visible() == False, "Settings should be hidden after second toggle"

        # Test pending changes
        settings_manager.show_settings()
        settings_manager.update_pending_setting('test_key', 'test_value')
        assert settings_manager.get_pending_setting('test_key') == 'test_value', "Pending setting not stored correctly"

        # Test settings summary
        summary = settings_manager.get_settings_summary()
        assert 'graphics' in summary, "Summary should contain graphics settings"
        assert 'audio' in summary, "Summary should contain audio settings"
        assert 'controls' in summary, "Summary should contain controls settings"

        print("[PASS] Settings Manager tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Settings Manager test failed: {e}")
        return False


def test_settings_integration():
    """Test integration between settings components."""
    print("[TEST] Testing Settings Integration...")

    try:
        from managers.settings_manager import SettingsManager
        from core.config import config_manager

        # Initialize pygame for testing
        pygame.init()
        screen = pygame.display.set_mode((1024, 768))
        screen_rect = screen.get_rect()

        # Create settings manager
        settings_manager = SettingsManager(screen_rect)

        # Show settings
        settings_manager.show_settings()

        # Test that current settings are loaded
        config = config_manager.get_config()
        pending_resolution = settings_manager.get_pending_setting('resolution')
        expected_resolution = f"{config.graphics.resolution_width}x{config.graphics.resolution_height}"
        assert pending_resolution == expected_resolution, "Current resolution not loaded correctly"

        # Test applying settings
        settings_manager.update_pending_setting('fullscreen', not config.graphics.fullscreen)
        success = settings_manager.apply_settings()
        assert success, "Settings application should succeed"

        # Test reset settings
        success = settings_manager.reset_settings()
        assert success, "Settings reset should succeed"

        print("[PASS] Settings Integration tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Settings Integration test failed: {e}")
        return False


def test_interactive_demo():
    """Test interactive demo of the settings interface."""
    print("[TEST] Testing Interactive Demo (press ESC to exit)...")

    try:
        from managers.settings_manager import SettingsManager

        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((1024, 768))
        pygame.display.set_caption("TurboShells Settings Demo")
        clock = pygame.time.Clock()

        # Create settings manager
        settings_manager = SettingsManager(screen.get_rect())

        # Show settings
        settings_manager.show_settings()

        # Run demo loop
        running = True
        demo_time = 0

        while running and demo_time < 5000:  # 5 second demo
            dt = clock.tick(60) / 1000.0
            demo_time += dt * 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_s:
                        settings_manager.toggle_settings()

                # Handle settings events
                settings_manager.handle_event(event)

            # Update
            settings_manager.update(dt)

            # Draw
            screen.fill((40, 40, 40))
            settings_manager.draw(screen)

            # Draw demo text
            font = pygame.font.Font(None, 24)
            text = font.render("Press 'S' to toggle settings, ESC to exit", True, (255, 255, 255))
            screen.blit(text, (10, 10))

            pygame.display.flip()

        pygame.quit()

        print("[PASS] Interactive Demo completed successfully")
        return True

    except Exception as e:
        print(f"[FAIL] Interactive Demo failed: {e}")
        return False


def main():
    """Run all tests."""
    print("[START] Starting Settings UI Tests")
    print("=" * 50)

    tests = [
        test_settings_view,
        test_ui_components,
        test_settings_manager,
        test_settings_integration,
        test_interactive_demo
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"[REPORT] Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("[SUCCESS] All tests passed! Phase 3 implementation is working correctly.")
        return True
    else:
        print("[FAIL] Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
