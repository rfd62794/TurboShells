"""Integration Test for Pygame GUI System

Verifies that the pygame_gui-based UI Manager and Panels initialize and render correctly.
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import pygame
import pygame_gui
from src.ui.ui_manager import UIManager
from src.ui.panels.settings_panel import SettingsPanel
from src.game.game_state_interface import TurboShellsGameStateInterface
from src.ui.data_binding import DataBindingManager


def main():
    print("Initializing Pygame...")
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("Pygame GUI Integration Test")
    clock = pygame.time.Clock()

    print("Initializing UI Manager...")
    # Initialize Managers
    ui_manager = UIManager(screen.get_rect())
    if not ui_manager.initialize(screen):
        print("Failed to initialize UI Manager")
        return

    print("Creating Mock Game State...")
    # Mock Game State
    class MockGame:
        def __init__(self):
            self.money = 1000
            self.active_turtle_count = 5
            self.race_speed_multiplier = 1.0

    class MockGameState:
        def __init__(self):
            self.game = MockGame()

        def get(self, key, default=None):
            if key == "money":
                return self.game.money
            if key == "active_turtle_count":
                return self.game.active_turtle_count
            return default

        def set(self, key, value):
            if key == "race_speed_multiplier":
                self.game.race_speed_multiplier = value
                print(f"Game State Updated: {key} = {value}")

    game_state = MockGameState()
    data_binding = DataBindingManager()

    print("Creating Settings Panel...")
    # Create and Register Settings Panel
    settings_panel = SettingsPanel(game_state, data_binding)
    ui_manager.register_panel("settings", settings_panel)
    ui_manager.show_panel("settings")

    print("Starting Main Loop...")
    running = True
    frame = 0
    while running:
        time_delta = clock.tick(60) / 1000.0

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Pass events to UI Manager
            ui_manager.handle_event(event)

            # Pass events to active panels if they need custom handling
            # (SettingsPanel handles button clicks via handle_event)
            settings_panel.handle_event(event)

            # Toggle settings with ESC
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    ui_manager.toggle_panel("settings")

        # Update
        ui_manager.update(time_delta)

        # Rendering
        screen.fill((50, 50, 50))  # Dark gray background

        # Draw UI
        ui_manager.draw_ui(screen)

        pygame.display.flip()

        frame += 1
        if frame % 60 == 0:
            print(f"Frame {frame}")
            # Auto-exit after 3 seconds for automated testing
            if frame > 180:
                print("Test completed successfully (timeout)")
                running = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
