"""Dialog System for TurboShells

Contains modal dialog classes that can be owned by panels
without interfering with the UIManager system.
"""

from .base_dialog import BaseDialog
from .quit_confirmation_dialog import QuitConfirmationDialog

__all__ = ['BaseDialog', 'QuitConfirmationDialog']
