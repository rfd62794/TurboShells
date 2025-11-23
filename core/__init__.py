"""
Core Module for TurboShells
Modular architecture following Single Responsibility Principle
"""

# Import genetics from root level
import genetics

# Import all sub-modules
from . import rendering
from . import voting
from . import game
from . import systems

# Convenience imports for backward compatibility
from genetics import VisualGenetics
from rendering import DirectTurtleRenderer, get_direct_renderer
from voting import VotingSystem, DesignPackage
from game import Turtle, GameState, KeyboardHandler, RaceTrack, Simulation
from systems import StateHandler, GeneticPoolManager, PatternGenerators

__all__ = [
    # Sub-modules
    'rendering', 'voting', 'game', 'systems',
    
    # Main classes
    'VisualGenetics', 'DirectTurtleRenderer', 'VotingSystem', 'DesignPackage',
    'Turtle', 'Race', 'GameState', 'KeyboardHandler', 'RaceTrack', 'Simulation',
    'StateHandler', 'GeneticPoolManager', 'PatternGenerators',
    
    # Convenience functions
    'get_direct_renderer'
]