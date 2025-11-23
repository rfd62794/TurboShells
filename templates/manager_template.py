"""
Template for creating new manager classes in TurboShells.

This template provides a standard structure for manager classes
that handle specific game systems.
"""

from typing import Dict, List, Optional, Any
from core.logging_config import get_logger


class TemplateManager:
    """
    Template manager class following TurboShells patterns.

    This class demonstrates the standard structure for manager classes
    including initialization, state management, and logging.
    """

    def __init__(self, game_state=None):
        """
        Initialize the template manager.

        Args:
            game_state: Reference to the main game state
        """
        self.game_state = game_state
        self.logger = get_logger(__name__)
        self._data: Dict[str, Any] = {}
        self._is_initialized = False

        self.logger.info("TemplateManager initialized")

    def initialize(self) -> bool:
        """
        Initialize the manager's internal state.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # TODO: Add initialization logic here
            self._is_initialized = True
            self.logger.info("TemplateManager initialization completed")
            return True
        except Exception as e:
            self.logger.error(f"TemplateManager initialization failed: {e}")
            return False

    def update(self, dt: float) -> None:
        """
        Update the manager's state.

        Args:
            dt: Time delta since last update in seconds
        """
        if not self._is_initialized:
            self.logger.warning("TemplateManager not initialized, skipping update")
            return

        # TODO: Add update logic here
        pass

    def get_data(self, key: str) -> Optional[Any]:
        """
        Get data from the manager.

        Args:
            key: Data key

        Returns:
            Data value or None if not found
        """
        return self._data.get(key)

    def set_data(self, key: str, value: Any) -> None:
        """
        Set data in the manager.

        Args:
            key: Data key
            value: Data value
        """
        self._data[key] = value
        self.logger.debug(f"Set data: {key} = {value}")

    def reset(self) -> None:
        """Reset the manager to initial state."""
        self._data.clear()
        self._is_initialized = False
        self.logger.info("TemplateManager reset")

    def cleanup(self) -> None:
        """Clean up resources before shutdown."""
        self._data.clear()
        self._is_initialized = False
        self.logger.info("TemplateManager cleanup completed")

    def get_status(self) -> Dict[str, Any]:
        """
        Get current manager status.

        Returns:
            Dictionary with status information
        """
        return {
            'initialized': self._is_initialized,
            'data_count': len(self._data),
            'data_keys': list(self._data.keys())
        }


# Example usage pattern:
if __name__ == "__main__":
    # Create manager instance
    manager = TemplateManager()

    # Initialize
    if manager.initialize():
        # Use manager
        manager.set_data('example_key', 'example_value')
        value = manager.get_data('example_key')
        print(f"Retrieved value: {value}")

        # Get status
        status = manager.get_status()
        print(f"Manager status: {status}")

        # Cleanup when done
        manager.cleanup()
    else:
        print("Failed to initialize manager")
