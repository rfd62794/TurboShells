# 🐢 TurboShells Python Style Guide

This guide establishes coding standards for the TurboShells project to ensure consistency, readability, and maintainability across all code.

## 📋 Table of Contents

1. [Core Principles](#core-principles)
2. [Code Formatting](#code-formatting)
3. [Naming Conventions](#naming-conventions)
4. [Documentation Standards](#documentation-standards)
5. [Import Organization](#import-organization)
6. [Error Handling](#error-handling)
7. [Testing Guidelines](#testing-guidelines)
8. [Game Development Specifics](#game-development-specifics)
9. [Code Review Checklist](#code-review-checklist)

---

## 🎯 Core Principles

### **Readability First**
- Code should be self-documenting where possible
- Use clear, descriptive names for variables, functions, and classes
- Prefer explicit over implicit

### **Consistency**
- Follow established patterns in the codebase
- Use the same style throughout all modules
- Maintain consistent structure across similar files

### **Game Development Focus**
- Performance-critical code may deviate from strict standards when necessary
- Game logic should be clear and maintainable
- UI code should be modular and reusable

---

## 🎨 Code Formatting

### **Black Formatter**
All code must be formatted with **Black** using the project configuration:

```bash
python -m black src/ tests/
```

**Configuration:**
- Line length: 88 characters
- Target Python versions: 3.8+
- Double quotes for strings

### **Manual Style Guidelines**

#### **Indentation**
- Use 4 spaces for indentation (no tabs)
- Align continuation lines with opening delimiters

```python
# ✅ Good
def long_function_name(
    parameter_one: str,
    parameter_two: int,
    parameter_three: bool,
) -> Dict[str, Any]:
    return {"result": parameter_one + str(parameter_two)}

# ❌ Bad
def long_function_name(parameter_one: str, parameter_two: int, parameter_three: bool) -> Dict[str, Any]:
    return {"result": parameter_one + str(parameter_two)}
```

#### **Blank Lines**
- Use 2 blank lines before top-level function and class definitions
- Use 1 blank line before method definitions inside classes
- Use blank lines to separate logical sections within functions

#### **Line Length**
- Maximum 88 characters (enforced by Black)
- Break long lines at natural points
- Use parentheses for multi-line expressions

---

## 🏷️ Naming Conventions

### **Variables and Functions**
- Use `snake_case` for variables and functions
- Use descriptive names that explain purpose
- Avoid single-letter variables except in loops

```python
# ✅ Good
player_money = 1000
turtle_speed = calculate_base_speed(genetics)

# ❌ Bad
pm = 1000
ts = calc_speed(g)
```

### **Classes**
- Use `PascalCase` for class names
- Use descriptive names that indicate purpose

```python
# ✅ Good
class TurboShellsGame:
class TurtleRenderer:
class GeneticsCalculator:

# ❌ Bad
class game:
class tr:
class gc:
```

### **Constants**
- Use `UPPER_SNAKE_CASE` for module-level constants
- Group related constants together

```python
# ✅ Good
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
TURTLE_BASE_SPEED = 5.0

# ❌ Bad
screen_width = 1024
ScreenHeight = 768
turtleBaseSpeed = 5.0
```

### **Private Members**
- Use single underscore prefix for protected members
- Use double underscore prefix for private members (rare)

```python
# ✅ Good
class Turtle:
    def __init__(self):
        self._energy = 100  # Protected
        self.__internal_state = {}  # Private (rare)

# ❌ Bad
class Turtle:
    def __init__(self):
        self.energy = 100  # Should be protected
        self.internal_state = {}  # Should be private
```

---

## 📚 Documentation Standards

### **Docstring Format**
Use Google-style docstrings for all public functions and classes:

```python
def calculate_race_time(
    turtle: Turtle, 
    track: RaceTrack, 
    weather_conditions: Weather
) -> float:
    """Calculate the estimated race time for a turtle.
    
    Args:
        turtle: The turtle participating in the race
        track: The race track with terrain information
        weather_conditions: Current weather affecting performance
        
    Returns:
        Estimated race time in seconds
        
    Raises:
        ValueError: If turtle has insufficient energy
        TrackError: If track configuration is invalid
    """
    # Implementation here
```

### **Class Documentation**
Every class should have a clear docstring explaining its purpose:

```python
class TurtleManager:
    """Manages all turtle-related operations in the game.
    
    Handles turtle creation, training, racing, and breeding operations.
    Maintains the active roster and breeding pool.
    
    Attributes:
        active_turtles: List of currently active racing turtles
        breeding_pool: List of retired turtles available for breeding
        max_active_turtles: Maximum number of active turtles allowed
    """
```

### **Inline Comments**
- Use comments to explain complex logic or business rules
- Don't comment obvious code
- Keep comments concise and up-to-date

```python
# ✅ Good
# Energy recovery rate is 20% per second when turtle is exhausted
recovery_rate = base_energy * 0.2 * delta_time

# ❌ Bad
# Add 1 to counter
counter += 1
```

---

## 📦 Import Organization

### **Import Order**
Imports are automatically organized by `isort`. Manual order should be:

1. Standard library imports
2. Third-party imports
3. Local application imports
4. Relative imports

```python
# ✅ Good
import os
import sys
from typing import Dict, List, Optional

import pygame
import pytest

from src.core.entities import Turtle
from src.managers.race_manager import RaceManager
from .ui_components import Button

# ❌ Bad
import pygame
from src.core.entities import Turtle
import os
from .ui_components import Button
import sys
```

### **Import Style**
- Use explicit imports instead of wildcards (except in specific cases)
- Group related imports
- Remove unused imports

```python
# ✅ Good
from typing import Dict, List, Optional

# ❌ Bad (avoid wildcards)
from typing import *
```

---

## ⚠️ Error Handling

### **Exception Hierarchy**
Create specific exceptions for different error types:

```python
# ✅ Good
class TurboShellsError(Exception):
    """Base exception for TurboShells game."""
    pass

class InsufficientFundsError(TurboShellsError):
    """Raised when player doesn't have enough money."""
    pass

class InvalidTurtleError(TurboShellsError):
    """Raised when turtle operation is invalid."""
    pass

# ❌ Bad (too generic)
try:
    process_turtle_action()
except Exception:
    print("Something went wrong")
```

### **Error Handling Patterns**
- Handle specific exceptions
- Provide meaningful error messages
- Log errors when appropriate
- Use context managers for resource management

```python
# ✅ Good
def save_game_state(game_data: Dict) -> bool:
    """Save the current game state to file."""
    try:
        with open("save.json", "w") as save_file:
            json.dump(game_data, save_file)
        logger.info("Game state saved successfully")
        return True
    except (IOError, PermissionError) as e:
        logger.error(f"Failed to save game: {e}")
        return False
    except json.JSONEncodeError as e:
        logger.error(f"Failed to encode game data: {e}")
        return False

# ❌ Bad
def save_game_state(game_data: Dict) -> bool:
    try:
        with open("save.json", "w") as save_file:
            json.dump(game_data, save_file)
        return True
    except:
        return False
```

---

## 🧪 Testing Guidelines

### **Test Structure**
- Use descriptive test names that explain what is being tested
- Follow Arrange-Act-Assert pattern
- Test both success and failure cases

```python
# ✅ Good
def test_turtle_energy_decreases_during_race():
    """Test that turtle energy decreases proportionally to distance covered."""
    # Arrange
    turtle = Turtle(speed=10, energy=100)
    race_distance = 50
    
    # Act
    initial_energy = turtle.energy
    turtle.simulate_movement(race_distance)
    
    # Assert
    assert turtle.energy < initial_energy
    assert turtle.energy >= 0

# ❌ Bad
def test_energy():
    turtle = Turtle(10, 100)
    turtle.move(50)
    assert turtle.energy < 100
```

### **Test Coverage**
- Aim for 70%+ coverage on core game logic
- 95%+ coverage on critical systems (save/load, genetics)
- Focus on testing business logic, not implementation details

### **Mock Usage**
- Use mocks to isolate units under test
- Mock external dependencies (file I/O, network)
- Don't mock the system under test

---

## 🎮 Game Development Specifics

### **Performance Considerations**
- Profile before optimizing
- Cache expensive calculations
- Use appropriate data structures
- Avoid premature optimization

```python
# ✅ Good (cached calculation)
@functools.lru_cache(maxsize=128)
def calculate_genetic_combination(parent1_id: str, parent2_id: str) -> Genetics:
    """Calculate genetic combination with caching."""
    # Expensive calculation here
    pass

# ❌ Bad (uncached repeated calculation)
def calculate_genetic_combination(parent1_id: str, parent2_id: str) -> Genetics:
    # Expensive calculation repeated every call
    pass
```

### **Game Loop Patterns**
- Keep game loop functions focused and fast
- Separate rendering from game logic
- Use delta time for frame-independent movement

```python
# ✅ Good
def update_game_state(delta_time: float) -> None:
    """Update game logic independent of frame rate."""
    for turtle in active_turtles:
        turtle.update_position(delta_time)
        turtle.update_energy(delta_time)

def render_game(screen: pygame.Surface) -> None:
    """Render current game state."""
    for turtle in active_turtles:
        turtle_renderer.draw(screen, turtle)

# ❌ Bad (mixed logic and rendering)
def game_loop():
    for turtle in active_turtles:
        turtle.move()
        turtle.draw(screen)
```

### **UI Component Design**
- Keep UI components modular and reusable
- Separate layout from rendering logic
- Use consistent coordinate systems

```python
# ✅ Good
class Button:
    """Reusable button component."""
    
    def __init__(self, rect: pygame.Rect, text: str):
        self.rect = rect
        self.text = text
        self.is_hovered = False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events."""
        # Event handling logic
        pass
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the button."""
        # Rendering logic
        pass

# ❌ Bad (mixed responsibilities)
class GameUI:
    def handle_button_click(self):
        # Event handling + rendering mixed
        if self.mouse_over_button():
            self.draw_button_highlighted()
```

---

## ✅ Code Review Checklist

### **Before Submitting Code**
- [ ] Code is formatted with Black
- [ ] All imports are organized with isort
- [ ] Pylint score is 8.0+ (or exceptions are justified)
- [ ] All public functions have docstrings
- [ ] Tests are included for new functionality
- [ ] No debug print statements remain
- [ ] Error handling is appropriate
- [ ] Performance considerations are documented

### **Review Focus Areas**
- **Readability**: Is the code easy to understand?
- **Maintainability**: Can this be easily modified later?
- **Performance**: Are there obvious performance issues?
- **Testing**: Are edge cases covered?
- **Documentation**: Is the purpose clear?

### **Game-Specific Checks**
- [ ] Game logic is frame-independent (uses delta time)
- [ ] UI components are modular and reusable
- [ ] Resource management (memory, file handles) is proper
- [ ] State management is consistent
- [ ] User input handling is robust

---

## 🔧 Development Tools Integration

### **Pre-commit Hooks**
The project uses pre-commit hooks to enforce quality standards:

```bash
# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### **IDE Configuration**
Configure your IDE with these settings:
- **Formatter**: Black (88 character line length)
- **Linter**: Pylint with project configuration
- **Test Runner**: PyTest with test discovery
- **Type Checker**: mypy (optional)

### **Continuous Integration**
All code changes must pass:
- Black formatting check
- Pylint quality check
- Test suite with coverage
- Security scan (bandit)

---

## 📝 Examples and Patterns

### **Good Function Example**
```python
def calculate_race_winnings(
    bet_amount: int, 
    placement: int, 
    turtle_performance: float
) -> int:
    """Calculate race winnings based on bet and performance.
    
    Args:
        bet_amount: Amount of money bet on the race
        placement: Finishing position (1=first, 2=second, etc.)
        turtle_performance: Performance multiplier (0.5-2.0)
        
    Returns:
        Total winnings including original bet
        
    Raises:
        ValueError: If bet_amount is negative or placement is invalid
    """
    if bet_amount <= 0:
        raise ValueError("Bet amount must be positive")
    if placement < 1:
        raise ValueError("Placement must be positive")
    
    base_multipliers = {1: 3.0, 2: 1.5, 3: 1.0}
    multiplier = base_multipliers.get(placement, 0.0)
    
    winnings = int(bet_amount * multiplier * turtle_performance)
    return max(0, winnings)
```

### **Good Class Example**
```python
class Turtle:
    """Represents a racing turtle with genetics and performance stats.
    
    Attributes:
        name: Unique identifier for the turtle
        genetics: Genetic traits affecting performance
        current_energy: Current energy level (0-100)
        position: Current position on the track
    """
    
    def __init__(self, name: str, genetics: Genetics) -> None:
        """Initialize a new turtle.
        
        Args:
            name: Unique identifier for the turtle
            genetics: Genetic traits determining base stats
        """
        self.name = name
        self.genetics = genetics
        self.current_energy = 100.0
        self.position = Vector2(0, 0)
        self._base_speed = self._calculate_base_speed()
    
    def update_position(self, delta_time: float, terrain: Terrain) -> None:
        """Update turtle position based on current energy and terrain.
        
        Args:
            delta_time: Time elapsed since last update (seconds)
            terrain: Current terrain type affecting movement speed
        """
        if self.current_energy <= 0:
            return
        
        speed_modifier = terrain.get_speed_modifier(self.genetics)
        movement_distance = self._base_speed * speed_modifier * delta_time
        
        self.position.x += movement_distance
        self.current_energy -= movement_distance * 0.1
        self.current_energy = max(0, self.current_energy)
    
    def _calculate_base_speed(self) -> float:
        """Calculate base speed from genetic traits."""
        speed_gene = self.genetics.get_trait("speed")
        return 5.0 + (speed_gene * 0.5)
```

---

This style guide serves as the foundation for maintaining high-quality code in the TurboShells project. All contributors should follow these guidelines to ensure consistency and maintainability.
