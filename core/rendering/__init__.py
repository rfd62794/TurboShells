"""
Rendering System for TurboShells
Modular rendering system following Single Responsibility Principle
"""

from .direct_turtle_renderer import DirectTurtleRenderer, get_direct_renderer

__all__ = ['DirectTurtleRenderer', 'get_direct_renderer']
