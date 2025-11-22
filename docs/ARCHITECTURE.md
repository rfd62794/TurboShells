# Technical Architecture: Turbo Shells

## 1. Project Structure
The project follows a flat structure for the MVP to minimize import complexity.

```text
/TurboShells
├── main.py             # Entry point. Handles the Game Loop and State Machine.
├── settings.py         # Global constants (screen dims, colors, game settings).
├── entities.py         # Shared Turtle class and physics logic.
├── game_state.py       # Generation and breeding helpers (no PyGame).
├── managers/           # State/feature managers (roster, race, shop, breeding).
│   ├── roster_manager.py
│   ├── race_manager.py
│   ├── shop_manager.py
│   └── breeding_manager.py
├── ui/
│   ├── layout.py       # All UI rects and positions (from UI_LAYOUT spec).
│   ├── menu_view.py    # Stable/Main Menu rendering.
│   ├── race_view.py    # Race and Race Results rendering.
│   ├── shop_view.py    # Shop rendering.
│   ├── breeding_view.py# Breeding rendering.
│   └── renderer.py     # Thin delegator that calls per-screen views.
├── simulation.py       # Headless race simulator using entities.Turtle.
├── docs/
│   ├── ARCHITECTURE.md # This file.
│   ├── GDD.md          # Full Game Design Document.
│   ├── GDD_Lite.md     # Condensed design doc.
│   ├── TODO.md         # Roadmap & checklist.
│   └── UI_LAYOUT.md    # UI layout coordinates and design notes.
└── README.md           # Setup and high-level overview.

2. Global Constants (settings.py)
Centralized variables to avoid "Magic Numbers" in the code.

SCREEN_WIDTH, SCREEN_HEIGHT, FPS

COLOR_PALETTE (Dictionary of RGB tuples)

GAME_SPEEDS = [1, 2, 4]

TURTLE_LIMIT = 3

COST_REFRESH_SHOP = 5

3. Class Definitions
3.1 Class: Turtle
Responsibility: Represents a single entity with stats and state.

Properties:

id: UUID or Unique Int.

name: String.

stats: Dict {speed, energy, recovery, swim, climb}.

state: Enum (IDLE, RUNNING, RESTING, RETIRED).

rect: PyGame Rect (for rendering).

Methods:

update_race(dt, terrain_type): Calculates movement and energy drain.

train(stat_name): Decrements energy, increments specific stat.

rest(): Sets energy to max.

3.2 Class: GameManager (in main.py)
Responsibility: The "God Object" that controls the flow.

Properties:

screen: The PyGame display surface.

clock: The PyGame clock.

current_state: Enum (MENU, RACE, SHOP).

roster: List [Turtle, Turtle, None].

money: Int.

Methods:

change_state(new_state): Handles transition logic (e.g., generating a new track when entering Race state).

game_loop(): The while True loop calling update() and draw().

3.3 Class: RaceTrack
Responsibility: Procedural generation of the level.

Properties:

segments: List of dicts [{type: 'GRASS', length: 100}, {type: 'WATER', length: 50}].

total_length: Int.

Methods:

generate(): Randomly appends segments until total length is reached.

get_terrain_at(x_pos): Returns the terrain type for a specific pixel coordinate.

4. Data Flow
The Race Loop
Input: User selects Speed Multiplier.

Logic:

GameManager loops through active_turtles.

Calls RaceTrack.get_terrain_at(turtle.x).

Passes terrain to turtle.update_race().

Turtle calculates new X position and Energy.

Render:

GameManager draws background segments.

GameManager draws Turtle sprites at new X positions.

The Breeding Loop
Input: User selects Parent A and Parent B from retired_roster.

Logic:

Verify active_roster has space.

Calculate new_stats = (A.stats + B.stats) / 2 + mutation.

Instantiate new Turtle(new_stats).

Append to active_roster.

Remove A and B from retired_roster (Delete objects).

Save: (Future) Serialize rosters to JSON.

5. Development Roadmap (Phases)
Phase 1 (The Skeleton): Get a square moving across the screen with Energy logic.

Phase 2 (The Manager): Implement the Menu, Roster list, and basic "Click to Train" button.

Phase 3 (The Economy): Implement Money, Shop generation, and Betting math.

Phase 4 (The Cycle): Implement Breeding and Retirement logic.