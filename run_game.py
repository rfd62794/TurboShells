#!/usr/bin/env python3
"""
TurboShells Game Entry Point
Launches the game from the organized source directory structure.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the main game
if __name__ == "__main__":
    from main import TurboShellsGame
    import pygame
    
    try:
        game = TurboShellsGame()
        while True:
            game.handle_input()
            game.update()
            game.draw()
            game.clock.tick(60)
    except KeyboardInterrupt:
        print("\nGame closed by user.")
        game.save_on_exit()
        pygame.quit()
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        game.save_on_exit()
        pygame.quit()
        sys.exit(1)
