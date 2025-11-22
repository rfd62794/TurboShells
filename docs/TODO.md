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