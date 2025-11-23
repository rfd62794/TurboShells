# 🐢 Turbo Shells

**Turbo Shells** is a minimal management simulation game built with Python and PyGame. The goal is simple: breed the ultimate racing turtle.

In this game, you don't control the racer—you manage the *racer*. Balance your economy, train your turtles to improve their stats, and make high-stakes decisions on when to retire a champion to breed the next generation.

## 🎮 Features

* **Strategic Roster Management:** You are limited to **3 Active Turtles**. You must make hard choices about who to keep and who to release.
* **Sacrificial Breeding:** Combine two retired champions to create a new offspring with inherited stats and mutations. The parents are gone forever, so the baby *must* be worth it.
* **Automated Racing Physics:** Turtles don't just run; they manage **Energy**. If they sprint too hard, they hit exhaustion and must stop to recover.
* **Procedural Tracks:** Races feature random combinations of Grass, Water (Swim check), and Rocks (Climb check).
* **Betting System:** Grind for cash by betting on your own turtles.
* **Responsive UI:** Dynamic layout system with perfect centering and window resizing support.
* **Settings Interface:** Professional settings menu with adaptive layout for all screen sizes.

## 🛠️ Installation & Setup

### Prerequisites
* Python 3.8+ installed.
* `pip` (Python package manager).

### Quick Setup (Recommended)

For the best development experience, use our automated setup script:

```bash
# Clone the repository
git clone <repository-url>
cd TurboShells

# Run the setup script
python setup_dev.py
```

This will automatically:
- Create a Python virtual environment
- Install all dependencies
- Set up development tools (Black, Pylint, PyTest)
- Configure pre-commit hooks
- Run initial tests

### Manual Setup

If you prefer manual setup:

1. **Clone or Download** this repository.
2. **Create Virtual Environment:**
    ```bash
    python -m venv venv
    
    # Activate (Windows)
    venv\Scripts\activate
    
    # Activate (macOS/Linux)
    source venv/bin/activate
    ```
3. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4. **Install Development Tools:**
    ```bash
    pip install -e .[dev]
    ```
5. **Set up Pre-commit Hooks:**
    ```bash
    pre-commit install
    ```
6. **Run the Game:**
    ```bash
    python main.py
    ```

### Development Tools

This project includes a comprehensive development setup with professional code quality tools:

#### 🎨 Code Quality Tools
- **Black**: Automatic code formatter for consistent style (88 character line length)
- **Pylint**: Code quality and error checking with game-development-friendly rules
- **isort**: Import statement organizer
- **mypy**: Static type checking (optional)

#### 🧪 Testing Framework
- **PyTest**: Testing framework with comprehensive test suite
- **pytest-cov**: Coverage reporting with HTML output
- **pytest-mock**: Mocking support for isolated testing
- **pytest-xdist**: Parallel testing for faster test runs

#### 📊 Code Analysis
- **Coverage**: Advanced coverage measurement and reporting
- **Bandit**: Security vulnerability scanning
- **Memory Profiler**: Memory usage analysis
- **Line Profiler**: Performance profiling

#### 📚 Documentation
- **Sphinx**: Documentation generation
- **ReadTheDocs Theme**: Professional documentation styling

#### 🔧 Development Workflow
- **Pre-commit**: Automatic quality checks before commits
- **Build Tools**: Package building and publishing utilities

#### Running Development Tools

```bash
# Code formatting
python -m black src/ tests/

# Import sorting
python -m isort src/ tests/

# Code linting
python -m pylint src/

# Type checking (optional)
python -mypy src/

# Run all tests
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

# Run tests in parallel
python -m pytest tests/ -n auto

# Security scanning
python -m bandit -r src/

# Performance profiling
python -m memory_profiler src/main.py
```

#### Quality Gates

The project enforces several quality standards:
- **Code Formatting**: All code must be Black-formatted
- **Linting**: Pylint score of 8.0+ for new code
- **Test Coverage**: Minimum 70% coverage for core modules
- **Documentation**: All public functions must have docstrings

#### IDE Configuration

For optimal development experience, configure your IDE with:
- **Python Interpreter**: Point to your virtual environment
- **Code Formatting**: Enable Black integration
- **Linting**: Enable Pylint integration
- **Testing**: Configure PyTest test discovery
- **Debugging**: Set breakpoints in `src/main.py`

## 🕹️ How to Play

### The Core Loop
1.  **Start:** You begin with one basic turtle and $50.
2.  **Train:** Use your turtle's **Energy** to train stats (Speed, Swim, Climb) in the menu.
3.  **Race:** Enter races to earn money. Betting allows you to increase profits.
4.  **Expand:** Use money to buy new stock from the **Shop**.
5.  **Breed:** Retire old turtles to the "Breeding Pool." Combine two retirees to create a generic superior baby.

### Controls
* **Mouse (Primary):** Navigate menus, select turtles, and interact with buttons (Stable, Shop, Breeding, Race HUD speed controls).
* **Keyboard (Shortcuts, current MVP):**
    * **Race Speed:** `1`, `2`, `3` to set 1x / 2x / 4x.
    * **Menu Navigation:** `M` (Menu), `R` (Race), `S` (Shop), `B` (Breeding).
    * **Stable Actions:** `Q/W/E` (Train slots 1–3), `Z/X/C` (Rest slots 1–3), `4/5/6` (Retire slots 1–3).
    * **Breeding:** Number keys select parents, `Enter` breeds (if 2 selected and space in roster).

## 📊 The Stats System

Every turtle has unique DNA that affects performance:

| Stat | Effect |
| :--- | :--- |
| **Speed** | Base movement speed on flat ground. |
| **Energy** | The gas tank. Drains while moving. |
| **Recovery** | How fast the turtle recovers when exhausted (stopped). |
| **Swim** | Speed multiplier in Water segments. |
| **Climb** | Speed multiplier in Rock segments. |

## 📂 Project Structure

```text
TurboShells/
├── main.py            # Entry point and game loop (TurboShellsGame)
├── settings.py        # Global constants (screen, colors, rewards, costs)
├── entities.py        # Shared Turtle class + physics/energy logic
├── game_state.py      # Turtle generation & breeding helpers (no PyGame)
├── managers/          # Game logic managers
│   ├── roster_manager.py    # Stable actions (train, rest, retire)
│   ├── race_manager.py      # Race loop, track terrain, rewards
│   ├── shop_manager.py      # Shop inventory, buying, refreshing
│   ├── breeding_manager.py  # Breeding selection and child creation
│   └── settings_manager.py  # Settings system with responsive UI
├── ui/
│   ├── layouts/       # UI positioning and layout data
│   │   └── positions.py     # All UI rects and positions
│   ├── components/    # Reusable UI components
│   │   ├── button.py        # Button and ToggleButton classes
│   │   └── turtle_card.py   # TurtleCard component
│   ├── views/         # Screen-specific rendering
│   │   ├── menu_view.py     # Stable/Main Menu rendering
│   │   ├── race_view.py     # Race and Race Results rendering
│   │   ├── shop_view.py     # Shop rendering
│   │   ├── breeding_view.py # Breeding rendering
│   │   └── settings_view.py # Settings interface with responsive layout
│   └── renderer.py    # Thin delegator that calls the views
├── simulation.py      # Headless race simulator using entities.Turtle
├── docs/
│   ├── ARCHITECTURE.md # Technical architecture
│   ├── GDD.md          # Full Game Design Document
│   ├── GDD_Lite.md     # Condensed GDD
│   ├── TODO.md         # Roadmap & checklist
│   └── UI_LAYOUT.md    # UI layout coordinates
└── README.md          # This file