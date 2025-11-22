# Software Design Document (SDD): Turbo Shells

## 1. Overview

This SDD describes the technical design of **Turbo Shells**, complementing the Game Design Document (GDD).

Goals:

- Capture the current architecture and module responsibilities.
- Describe key data models and state flows.
- Provide a stable reference for future features (Main Menu, Pond, Profile view, etc.).

The guiding principles are:

- **Single Source of Truth for Simulation Logic** (entities + race_track).
- **Separation of Concerns** between domain logic, orchestration (managers), and presentation (UI views).
- **Small, composable modules** that can evolve independently.

---

## 2. High-Level Architecture

Top-level layers:

- **Domain / Core Logic**
  - `entities.py` – Turtle stats and physics.
  - `race_track.py` – Procedural race track generation and terrain lookup.
  - `game_state.py` – High-level helpers: turtle generation, breeding, pricing.

- **Orchestration / Managers**
  - `main.py` – Owns the main loop (`handle_input`, `update`, `draw`) and global state object `TurboShellsGame`.
  - `managers/` – Feature-specific controllers:
    - `roster_manager.py` – Stable actions and navigation.
    - `race_manager.py` – Race loop, rewards, betting resolution.
    - `shop_manager.py` – Shop inventory and buying.
    - `breeding_manager.py` – Parent selection and breeding.

- **Presentation / UI**
  - `ui/layout.py` – All UI coordinates and rectangles.
  - `ui/*_view.py` – Per-screen rendering:
    - `menu_view.py` – Stable/Roster screen.
    - `race_view.py` – Race and Race Results.
    - `shop_view.py` – Shop.
    - `breeding_view.py` – Breeding Center.
  - `ui/renderer.py` – Thin delegator that calls the appropriate view.
  - `ui/turtle_card.py` – Shared turtle UI helpers (labels/cards).

- **Support**
  - `simulation.py` – Headless race simulator for balancing.
  - `docs/` – Design documents (GDD, SDD, TODO, etc.).

The runtime core is the `TurboShellsGame` object in `main.py`, which is passed by reference into all managers and views.

---

## 3. Module Responsibilities & Interfaces

### 3.1 `entities.py`

- **Contains:**
  - `Turtle` class.
  - Physics constants (e.g., `TERRAIN_DIFFICULTY`, `RECOVERY_RATE`).

- **Responsibilities:**
  - Source of truth for turtle stats and race state.
  - Implement energy/movement logic in `update_physics(terrain_type)`.

- **Used by:**
  - `simulation.py`, `race_manager.py`, `game_state.py`.

- **Key interface:**
  - `Turtle(name, speed, energy, recovery, swim, climb)`.
  - `t.reset_for_race()`, `t.update_physics(terrain_type)`, `t.train(stat_name)`.

### 3.2 `race_track.py`

- **Contains:**
  - `generate_track(length: int | None)` – builds a list of terrain segments.
  - `get_terrain_at(track, distance: float)` – returns terrain at a logical distance.

- **Responsibilities:**
  - Provide a shared notion of track layout for both the headless simulation and the visual game.

- **Used by:**
  - `simulation.py` and `race_manager.py`.

### 3.3 `game_state.py`

- **Contains:**
  - `TURTLE_NAMES` list.
  - `generate_random_turtle(level=1)`.
  - `breed_turtles(parent_a, parent_b)`.
  - `compute_turtle_cost(turtle)`.

- **Responsibilities:**
  - Encapsulate turtle generation and breeding math.
  - Provide a simple, centralized cost function for Shop pricing.

- **Constraints:**
  - Must remain UI-agnostic (no PyGame imports or Rect usage).

### 3.4 `main.py` (`TurboShellsGame`)

- **Contains:**
  - `TurboShellsGame` class.
  - Game loop entry point.

- **Responsibilities:**
  - Initialize PyGame, window, fonts.
  - Own global game state:
    - Roster and Retired lists.
    - Money, Shop inventory and messages.
    - Race results, speed multiplier, active racer index.
    - Breeding parents.
    - Betting (`current_bet`).
    - Stable view mode (`show_retired_view`).
    - Mouse position (`mouse_pos`).
  - Route input events to the appropriate manager.
  - Call managers in `update()` and UI views in `draw()`.

- **Key interfaces:**
  - `handle_input()` → uses PyGame event queue.
  - `update()` → calls manager `update()` where needed.
  - `draw()` → delegates to `Renderer` based on `state`.

### 3.5 Managers (`managers/`)

Managers coordinate domain logic but do **not** draw.

- **`RosterManager`**
  - Handles clicks on Stable UI (nav buttons, TRAIN/REST/RETIRE, view toggles, bet buttons).
  - Calls `t.train("speed")`, `rest_turtle`, `retire_turtle`.
  - Sets flags such as `show_retired_view` and `active_racer_index`.

- **`RaceManager`**
  - `start_race()`:
    - Initializes `results`.
    - Generates a new track (`race_track.generate_track`).
    - Fills CPU slots with temporary turtles if empty.
    - Applies betting deduction from `current_bet`.
    - Resets turtles for race.
  - `update()`:
    - Steps race using `t.update_physics(terrain)`.
    - Assigns ranks and finishes.
  - `process_rewards()`:
    - Awards prize money.
    - Applies betting payouts.
    - Handles post-race aging and auto-retirement.

- **`ShopManager`**
  - Maintains `inventory` list.
  - `refresh_stock()`:
    - Deducts refresh cost if not free.
    - Fills inventory with `generate_random_turtle`.
    - Computes and stores `t.shop_cost` using `compute_turtle_cost`.
  - `buy_turtle(index)`:
    - Checks money vs computed cost.
    - Inserts the turtle into the first empty roster slot.

- **`BreedingManager`**
  - Tracks `parents` (2 max) and syncs `breeding_parents` for UI.
  - Uses a combined pool of active + retired turtles for selection.
  - `breed()`:
    - Validates there is space in the active roster.
    - Calls `breed_turtles` to create a child.
    - Removes parents from whichever collection they belong to (roster or retired).

---

## 4. UI Layer

### 4.1 Layout (`ui/layout.py`)

- Holds **all** PyGame `Rect` definitions and coordinates.
- Grouped by screen: header, Stable slots, Race HUD, Shop cards, Breeding list, etc.
- Used by all views and managers for drawing and click detection.

### 4.2 Views (`ui/*.py`)

- **`ui/renderer.py`**
  - Thin wrapper:
    - `draw_menu(game_state)` → `menu_view.draw_menu`.
    - `draw_race(game_state)` → `race_view.draw_race`.
    - `draw_race_result(game_state)` → `race_view.draw_race_result`.
    - `draw_shop(game_state)` → `shop_view.draw_shop`.
    - `draw_breeding(game_state)` → `breeding_view.draw_breeding`.

- **`ui/menu_view.py`**
  - Renders the Stable screen:
    - Uses `draw_stable_turtle_slot` for each of the three slots.
    - Draws TRAIN/REST/RETIRE buttons (visual only; logic in `RosterManager`).
    - Draws nav buttons (Race, Breeding, Shop).
    - Draws view toggle buttons (Active/Retired) and bet buttons.

- **`ui/race_view.py`**
  - `draw_race`:
    - Renders race lanes, finish line, HUD (speed & bet info).
  - `draw_race_result`:
    - Shows ordered results list and action buttons (Menu, Race Again).

- **`ui/shop_view.py`**
  - Renders 3 turtle cards with name, shared label, and price.
  - Draws BUY, REFRESH, and BACK buttons.

- **`ui/breeding_view.py`**
  - Renders the combined breeding pool of active + retired turtles.
  - Highlights selected parents.
  - Draws BREED and MENU buttons.

- **`ui/turtle_card.py`**
  - `format_turtle_label_basic(turtle)` – status/age/stats label.
  - `draw_stable_turtle_slot(...)` – full Stable slot card.

---

## 5. Game State & Data Model

### 5.1 `Turtle`

Key fields (simplified):

- Identity: `id`, `name`, `age`, `is_active`.
- Stats: `speed`, `max_energy`, `recovery`, `swim`, `climb`.
- Race state: `current_energy`, `race_distance`, `is_resting`, `finished`, `rank`.
- Optional: `shop_cost`, future lineage fields (e.g., parent IDs).

### 5.2 `TurboShellsGame` Shared State

- Roster & Retired:
  - `roster: list[Turtle|None]` (size 3).
  - `retired_roster: list[Turtle]`.
- Economy:
  - `money: int`.
  - Shop: `shop_inventory`, `shop_message`.
- Race:
  - `race_results: list[Turtle]`.
  - `race_speed_multiplier: int`.
  - `active_racer_index: int`.
  - `current_bet: int`.
- Breeding:
  - `breeding_parents: list[Turtle]`.
- UI flags:
  - `state: str` (e.g., `STATE_MENU`).
  - `show_retired_view: bool`.
  - `mouse_pos: tuple[int, int]`.

---

## 6. Key Flows

### 6.1 Race Flow (with Betting)

1. Player selects a **bet amount** in Stable.
2. Player navigates to Race (via button/shortcut).
3. `RaceManager.start_race()`:
   - Deducts bet from `money` if possible.
   - Generates track.
   - Fills CPU opponents.
   - Resets turtles.
4. `RaceManager.update()` (per frame):
   - For each active turtle:
     - Determine terrain from `race_track`.
     - Call `update_physics(terrain)` and advance distance.
     - Mark finished turtles and assign ranks.
5. Once all finish:
   - `process_rewards()`:
     - Compute prize.
     - Compute bet payout (if 1st).
     - Age turtles and auto‑retire where needed.
   - `TurboShellsGame.state` → `STATE_RACE_RESULT`.

### 6.2 Breeding Flow

1. Player enters Breeding Center.
2. Combined list of active + retired turtles is rendered.
3. Player selects 2 parents.
4. Player clicks BREED:
   - Validate there is an empty roster slot.
   - Call `breed_turtles` to create a child.
   - Remove parents from `roster` and/or `retired_roster`.
   - Insert child into first empty active slot.

### 6.3 Stable View Toggle Flow

1. Player clicks **ACTIVE** or **RETIRED** button.
2. `RosterManager` toggles `show_retired_view`.
3. `menu_view` chooses appropriate data source:
   - Active: `roster`.
   - Retired: `retired_roster` (first 3).
4. Slot actions (train/rest/retire/select) only enabled in Active view.

---

## 7. Planned Extensions (Design Hooks)

This section summarizes how future features should integrate into the existing architecture.

- **Main Menu (STATE_MAIN_MENU):**
  - New view (`ui/main_menu_view.py`) and optional `MainMenuManager`.
  - Introduce a new `STATE_MAIN_MENU` and transition into existing states via explicit buttons.

- **Profile View:**
  - Add `selected_turtle` to `TurboShellsGame`.
  - Render a side panel in Stable using a new `ui/profile_view.py` or an extension of `turtle_card`.
  - Optional lineage visualization reading from future parent/child fields on `Turtle`.

- **Pond / Glade:**
  - New state `STATE_POND` with its own view/manager.
  - Reuse `Turtle` data; maintain separate positional state for pond rendering.
  - Keep pond logic mostly visual with minimal interaction hooks.

This SDD should evolve alongside implementation changes and the roadmap in `docs/TODO.md`.
*** End Patch
