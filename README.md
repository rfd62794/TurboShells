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

This project includes several development tools to maintain code quality:

- **Black**: Code formatter for consistent style
- **Pylint**: Code quality and error checking
- **PyTest**: Testing framework with coverage
- **Pre-commit**: Automatic code quality checks before commits

#### Running Development Tools

```bash
# Format code
black .

# Lint code
pylint .

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=. --cov-report=html
```

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