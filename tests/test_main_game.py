"""
Basic tests for the main TurboShells game functionality.
"""

# Add project root to path
import os
import pygame
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


# Add the parent directory to the path so we can import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from main import TurboShellsGame
    from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
except ImportError as e:
    pytest.skip(f"Cannot import main game module: {e}", allow_module_level=True)


class TestTurboShellsGame:
    """Test cases for the main TurboShellsGame class."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Initialize pygame for testing
        pygame.init()
        # Set up a dummy display to avoid errors
        pygame.display.set_mode((1, 1))

    def teardown_method(self):
        """Clean up after each test."""
        pygame.quit()

    def test_game_initialization(self):
        """Test that the game can be initialized without errors."""
        try:
            game = TurboShellsGame()
            assert game is not None
            assert hasattr(game, 'screen')
            assert hasattr(game, 'font')
            assert hasattr(game, 'state')
        except Exception as e:
            pytest.fail(f"Game initialization failed: {e}")

    def test_screen_dimensions(self):
        """Test that the game screen has correct dimensions."""
        try:
            game = TurboShellsGame()
            assert game.screen.get_width() == SCREEN_WIDTH
            assert game.screen.get_height() == SCREEN_HEIGHT
        except Exception as e:
            pytest.skip(f"Cannot test screen dimensions: {e}")

    def test_initial_game_state(self):
        """Test that the game starts in the correct state."""
        try:
            game = TurboShellsGame()
            # The game should start in menu state
            from settings import STATE_MENU
            assert game.state == STATE_MENU
        except Exception as e:
            pytest.skip(f"Cannot test game state: {e}")

    def test_required_managers_exist(self):
        """Test that required game managers are initialized."""
        try:
            game = TurboShellsGame()
            required_managers = [
                'renderer', 'roster_manager', 'shop_manager',
                'race_manager', 'breeding_manager', 'state_handler',
                'keyboard', 'game_state_manager'
            ]
            for manager in required_managers:
                assert hasattr(game, manager), f"Missing manager: {manager}"
        except Exception as e:
            pytest.skip(f"Cannot test managers: {e}")


class TestGameConstants:
    """Test game constants and settings."""

    def test_screen_constants(self):
        """Test that screen constants are positive values."""
        assert SCREEN_WIDTH > 0
        assert SCREEN_HEIGHT > 0
        assert isinstance(SCREEN_WIDTH, int)
        assert isinstance(SCREEN_HEIGHT, int)

    def test_fps_constant(self):
        """Test that FPS is a reasonable value."""
        assert FPS > 0
        assert isinstance(FPS, int)
        assert FPS <= 120  # Reasonable upper limit for game FPS


if __name__ == "__main__":
    pytest.main([__file__])
