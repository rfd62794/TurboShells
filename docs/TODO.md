# Project Roadmap

## Phase 1: The Skeleton 🦴
- [ ] **Setup:** Create `main.py`, `settings.py`, and `sprites.py`.
- [ ] **Window:** Initialize PyGame window (800x600) and Main Loop.
- [ ] **State Machine:** Create simple `STATE` variables (MENU, RACE, SHOP) and generic draw functions for each to verify switching works.

## Phase 2: The Turtle & Physics 🐢
- [ ] **Class:** Define `Turtle` class with `speed`, `energy`, `recovery`, `swim`, `climb`.
- [ ] **Logic:** Implement `update_race()` method:
    - [ ] Forward movement.
    - [ ] Energy drain logic.
    - [ ] Resting/Recovery logic.
- [ ] **Test:** Render a single white square moving across the screen that stops when energy dies and starts again after recovery.

## Phase 3: The Race Track 🏁
- [x] **Terrain:** Implement shared `race_track` helper that generates a list of segments (Grass, Water, Rock) used by both `simulation.py` and the in-game Race.
- [ ] **Visuals:** Draw different colors for terrain segments on the Race Screen (currently lanes are uniform; terrain is logical only).
- [x] **Interaction:** Connect Turtle physics to track terrain (e.g., Swim/Climb stats affect Water/Rock via `update_physics`).
- [x] **Controls:** Add keyboard inputs (1, 2, 3) to change game speed multiplier.

## Phase 4: The Manager (UI) 📋
- [ ] **Roster Data:** Create a global list to hold 3 Turtle objects.
- [ ] **Menu Display:** Draw the 3 slots using coordinates from `UI_LAYOUT.md`.
- [ ] **Buttons:** Create a clickable `Button` class or simple rect collision check.
- [ ] **Training:** clicking [TRAIN] should decrease Energy and increase a Stat.
- [ ] **Resting:** clicking [REST] should refill Energy.

## Phase 5: The Economy 💰
- [ ] **Shop:** Generate 3 random turtles. Clicking [BUY] adds them to Roster.
- [ ] **Money:** Track player cash. Deduct cost on buy.
- [ ] **Betting:** Add a simple Input Box or Slider before the race starts to wager money.
- [ ] **Payouts:** Calculate wins/losses after race finishes.

## Phase 6: Breeding (The MVP Goal) 🧬
- [ ] **Retirement:** Add button to move Active Turtle to `retired_list`.
- [ ] **Breeding Logic:** Function that takes 2 Retired parents, deletes them, and returns 1 Baby.
- [ ] **Integration:** Add "Breeding Center" screen to select parents.

## Phase 7: Module Organization & SRP 🧱
- [x] **Per-screen UI Views:** Split rendering into `ui/menu_view.py`, `ui/race_view.py`, `ui/shop_view.py`, `ui/breeding_view.py`, and keep `ui/renderer.py` as a thin delegator.
- [x] **Shared Components:** Introduce shared turtle UI helpers in `ui/turtle_card.py` (basic label + Stable card).
- [ ] **Further Decomposition:** Consider extracting small shared button/label helpers for consistent UI styling.
- [ ] **Filesystem Cleanup:** Revisit top-level layout (e.g., group gameplay modules vs. infrastructure) once MVP stabilizes.

## Phase 8: Main Menu & Navigation UX 🧭
- [ ] **Main Menu Screen:** Design a dedicated "Main Menu" separate from the Stable, with clear buttons to:
  - [ ] Start Game / Continue
  - [ ] Go to Stable (Roster)
  - [ ] Go to Races
  - [ ] Open Shop
  - [ ] Open Breeding Center
- [ ] **In-Game Navigation:** Simplify keyboard shortcuts and rely on visible buttons for all major state transitions.

## Phase 9: Roster Tabs & Profile View 📇
- [x] **View Toggle:** Add Active/Retired toggle in Stable to switch which turtles are shown.
- [ ] **Tabbed Roster UI:** Replace simple toggle with a proper tabbed interface (e.g., [ACTIVE], [RETIRED]) that looks and behaves like tabs.
- [ ] **Profile View:** Add a dedicated Profile panel for a selected turtle:
  - [ ] Full stat breakdown.
  - [ ] Age, status, race history summary.
  - [ ] Lineage view (parents / children) once ancestry data is tracked.
- [ ] **Lineage Data Model:** Extend `Turtle` or `game_state` to optionally track parent IDs and children for lineage visualization.

## Phase 10: Pond / Glade Screen 🌿
- [ ] **Pond Overview:** Add a "Glade" or "Pond" screen where all current (active + retired) turtles wander passively.
- [ ] **Ambient Behavior:** Simple idle movement/animation for turtles in the pond.
- [ ] **Clickable Turtles:** Allow clicking a turtle in the pond to bring up a tooltip-style overlay with key stats (name, age, status, core stats).
- [ ] **Profile Shortcut:** From the pond tooltip, provide a way to open the full Profile view for that turtle.