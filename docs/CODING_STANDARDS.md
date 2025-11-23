# TurboShells Coding Standards

This document outlines the coding standards and conventions for the TurboShells project.

## 🐍 Python Style Guide

### Code Formatting
- Use **Black** for automatic code formatting
- Line length: 88 characters
- Use f-strings for string formatting
- Follow PEP 8 guidelines

### Naming Conventions

#### Variables and Functions
```python
# Use snake_case for variables and functions
player_money = 100
def calculate_turtle_stats(turtle):
    pass

# Constants use UPPER_SNAKE_CASE
MAX_TURTLES = 3
BASE_REWARD = 10

# Private methods start with underscore
def _internal_helper():
    pass
```

#### Classes
```python
# Use PascalCase for classes
class TurtleManager:
    pass

class GameState(Enum):
    pass
```

#### Files and Modules
```python
# Use snake_case for file names
# turtle_manager.py
# game_state.py
# breeding_system.py
```

### Type Hints
Use type hints for function signatures and important variables:

```python
from typing import List, Dict, Optional, Union

def breed_turtles(parent1: Turtle, parent2: Turtle) -> Turtle:
    """Breed two turtles to create offspring."""
    pass

def get_turtle_stats(turtle_id: int) -> Optional[Dict[str, int]]:
    """Get turtle statistics by ID."""
    pass
```

## 📝 Documentation Standards

### Docstrings
Use Google-style docstrings:

```python
def calculate_race_time(turtle: Turtle, track: Track) -> float:
    """Calculate the estimated race time for a turtle.
    
    Args:
        turtle: The turtle racing
        track: The race track with terrain
    
    Returns:
        Estimated race time in seconds
    
    Raises:
        ValueError: If turtle stats are invalid
    """
    pass
```

### Module Documentation
Each module should start with a docstring:

```python
"""
Turtle breeding system for TurboShells.

This module handles the genetic inheritance and mutation logic
for breeding new turtles from parent turtles.
"""

import random
from typing import List, Tuple
```

### Comments
- Use comments to explain complex logic
- Don't over-comment obvious code
- Use TODO comments for future improvements:

```python
# TODO: Add terrain-specific bonuses
terrain_bonus = calculate_terrain_modifier(terrain_type)

# Complex calculation for genetic inheritance
# This uses weighted averaging with mutation chance
inherited_speed = (parent1.speed * 0.4 + parent2.speed * 0.4) + mutation_bonus
```

## 🏗️ Architecture Standards

### Single Responsibility Principle
Each class and function should have a single, clear responsibility:

```python
# Good: Single responsibility
class TurtleRenderer:
    """Handles only turtle visual rendering."""
    
    def render_turtle(self, turtle: Turtle, position: Tuple[int, int]):
        pass

class TurtlePhysics:
    """Handles only turtle physics calculations."""
    
    def calculate_movement(self, turtle: Turtle, dt: float):
        pass

# Bad: Multiple responsibilities
class TurtleManager:
    """Handles rendering, physics, and breeding - too much!"""
    pass
```

### Dependency Injection
Prefer dependency injection over hard-coded dependencies:

```python
# Good: Dependency injection
class RaceManager:
    def __init__(self, renderer: Renderer, physics: Physics):
        self.renderer = renderer
        self.physics = physics

# Bad: Hard-coded dependencies
class RaceManager:
    def __init__(self):
        self.renderer = Renderer()  # Hard-coded
        self.physics = Physics()    # Hard-coded
```

### Error Handling
Use specific exceptions and proper error handling:

```python
# Good: Specific exceptions
def validate_turtle_stats(turtle: Turtle) -> None:
    if turtle.speed < 0:
        raise ValueError("Speed cannot be negative")
    if turtle.energy > 100:
        raise ValueError("Energy cannot exceed 100")

# Good: Try-except with specific handling
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Invalid input: {e}")
    raise
except IOError as e:
    logger.error(f"File operation failed: {e}")
    raise
```

## 🎮 Game-Specific Standards

### State Management
Use enums for game states and constants:

```python
from enum import Enum

class GameState(Enum):
    MENU = "menu"
    RACING = "racing"
    BREEDING = "breeding"
    SHOP = "shop"

class TurtleStat(Enum):
    SPEED = "speed"
    ENERGY = "energy"
    RECOVERY = "recovery"
    SWIM = "swim"
    CLIMB = "climb"
```

### Event System
Use a consistent event system for game events:

```python
from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class GameEvent:
    """Base class for game events."""
    event_type: str
    data: Dict[str, Any]

@dataclass
class TurtleBredEvent(GameEvent):
    """Event fired when turtles are bred."""
    parent1_id: int
    parent2_id: int
    offspring_id: int
```

### Configuration
Keep configuration separate from logic:

```python
# settings.py - Configuration only
TURTLE_COUNT_LIMIT = 3
BASE_REWARD_AMOUNT = 10
MUTATION_CHANCE = 0.1

# game_logic.py - Logic only
def can_add_turtle(current_count: int) -> bool:
    return current_count < TURTLE_COUNT_LIMIT
```

## 🧪 Testing Standards

### Test Structure
Organize tests by module and functionality:

```python
# tests/test_turtle_manager.py
class TestTurtleManager:
    def test_add_turtle_success(self):
        """Test adding a turtle successfully."""
        pass
    
    def test_add_turtle_limit_exceeded(self):
        """Test adding turtle when limit is exceeded."""
        pass
    
    def test_breed_turtles_valid_parents(self):
        """Test breeding with valid parent turtles."""
        pass
```

### Test Naming
Use descriptive test names that explain what's being tested:

```python
# Good: Descriptive names
def test_breed_turtles_with_high_stats_creates_high_stat_offspring():
    pass

def test_race_with_water_terrain_uses_swim_stat():
    pass

# Bad: Vague names
def test_breed_1():
    pass

def test_race():
    pass
```

### Test Data
Use factories or fixtures for test data:

```python
# tests/fixtures.py
@pytest.fixture
def sample_turtle():
    """Create a sample turtle for testing."""
    return Turtle(
        name="Test Turtle",
        speed=50,
        energy=75,
        recovery=60,
        swim=40,
        climb=30
    )
```

## 📁 File Organization

### Directory Structure
```
TurboShells/
├── core/                  # Core game logic
│   ├── game_state.py      # Game state management
│   ├── genetics.py        # Genetics system
│   ├── physics.py         # Physics calculations
│   └── events.py          # Event system
├── managers/              # Game managers
│   ├── turtle_manager.py  # Turtle management
│   ├── race_manager.py    # Race management
│   └── shop_manager.py    # Shop management
├── ui/                    # User interface
│   ├── views/             # UI views
│   ├── components/        # UI components
│   └── layouts.py         # Layout definitions
├── tests/                 # Test files
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── fixtures.py        # Test fixtures
└── docs/                  # Documentation
```

### Import Organization
Organize imports in this order:
1. Standard library imports
2. Third-party imports
3. Local application imports

```python
# Standard library
import os
import sys
from typing import List, Dict

# Third-party
import pygame
import pytest

# Local imports
from core.game_state import GameState
from managers.turtle_manager import TurtleManager
```

## 🔧 Development Tools

### Pre-commit Hooks
Always use pre-commit hooks to ensure code quality:
```bash
pre-commit install
```

### Code Quality Checks
Run these before committing:
```bash
# Format code
black .

# Lint code
pylint .

# Run tests
pytest tests/ -v
```

### IDE Configuration
Configure your IDE to:
- Use 4-space indentation
- Show line endings
- Enable type checking
- Integrate with Black and Pylint

## 🚀 Performance Guidelines

### Game Loop Optimization
- Profile before optimizing
- Cache expensive calculations
- Use appropriate data structures
- Avoid allocations in hot paths

### Memory Management
- Reuse objects when possible
- Clear references when done
- Monitor memory usage
- Use generators for large sequences

### Rendering Optimization
- Batch similar operations
- Use dirty rectangle updating
- Cache rendered surfaces
- Minimize state changes

## 📋 Code Review Checklist

### Before Submitting Code
- [ ] Code follows formatting standards
- [ ] Tests pass and have good coverage
- [ ] Documentation is updated
- [ ] No TODO/FIXME comments left
- [ ] Error handling is appropriate
- [ ] Performance is acceptable
- [ ] Security considerations are addressed

### During Review
- [ ] Logic is correct and clear
- [ ] Naming is consistent and meaningful
- [ ] Dependencies are appropriate
- [ ] Tests are comprehensive
- [ ] Documentation is accurate
- [ ] Edge cases are handled

## 🎯 Best Practices Summary

### Do
- Write clear, readable code
- Use meaningful names
- Add appropriate documentation
- Test thoroughly
- Handle errors gracefully
- Follow the established patterns

### Don't
- Over-engineer simple problems
- Use magic numbers or strings
- Ignore error conditions
- Write overly complex code
- Skip documentation
- Break established conventions

Remember: The goal is to write maintainable, readable code that other developers (including future you) can understand and modify easily.
