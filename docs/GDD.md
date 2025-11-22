## Game Design Document: Turbo Shells

**Version:** 1.0 (MVP)  
**Date:** November 22, 2025  
**Engine:** Python / PyGame (or pygame-ce)  
**Genre:** Management Simulation / Auto‑Racer

---

## 1. Executive Summary

Turbo Shells is a management simulation where the player acts as a trainer and breeder for a stable of racing turtles. The player does **not** directly control movement during races. Instead, they manage:

- Genetics (breeding, lineage, long‑term planning)
- Training (improving stats over time)
- Energy and fatigue (when to push, when to rest)
- Economy (shopping, betting, roster composition)

The core hook is the **Sacrificial Breeding** loop: to create the next generation of champions, you must eventually retire and give up your current turtles, using them as parents for offspring that (usually) inherit or exceed their strengths.

High‑level fantasy:  
> “Tamagotchi meets Horse Racing” – you don’t drive the turtle; you coach it.

---

## 2. Core Gameplay Loop

The main loop is a 4‑stage cycle:

1. **Manage (Stable / Roster)**
   - Inspect the **Active Roster** (up to 3 turtles).
   - Train turtles to improve stats (costs **time/age**, not money).
   - Rest turtles to refill energy.
   - Retire aging champions to the **Retired Roster** for breeding.

2. **Race**
   - Select your **active racer** from the Stable.
   - Optionally place a small **bet** on the race outcome.
   - Enter a race on a procedurally generated track (Grass / Water / Rock).
   - Watch the race unfold at varying speeds (1x, 2x, 4x).

3. **Profit**
   - Earn prize money based on finish position.
   - Resolve any bets (win more, or lose the bet amount).
   - Use money to buy new genetic stock from the **Shop**.

4. **Evolve (Breeding)**
   - Retire turtles into a **Breeding Pool**.
   - Choose any two turtles (active or retired) as parents.
   - Sacrifice them (they are removed from the game) to create one **Child** turtle.
   - Child inherits the **best** stats of both parents plus a small chance of positive mutation.

Repeat: as turtles age (from races and training), they naturally move toward retirement, breeding, and replacement.

---

## 3. Game Systems

### 3.1 Roster System

The player’s stable is intentionally small to force tough choices.

- **Active Roster**
  - Max 3 turtles.
  - These turtles can **Train** and **Race**.
  - Age increases by **1** for each race and for each successful training session.
  - When a turtle reaches **Age 100**, it is automatically **retired**:
    - Removed from Active Roster.
    - Marked as inactive (`is_active=False`).
    - Moved into **Retired Roster**.

- **Retired Roster**
  - Stores turtles that are no longer racing or training.
  - Used primarily as **breeding material**.
  - Retired turtles can still be chosen as breeding parents but cannot race or be trained.

- **Inventory Constraint**
  - The player cannot acquire a new turtle (via Shop or Breeding) if all 3 active slots are full.
  - This forces the player to retire or sacrifice turtles to make space.

### 3.2 Turtle Stats (The DNA)

Every turtle is defined by a core set of stats stored in `entities.Turtle`:

| Stat       | Description                         | Gameplay Impact                                           |
|-----------|-------------------------------------|-----------------------------------------------------------|
| Speed     | Base velocity on flat ground        | Higher = more distance per tick on Grass                 |
| MaxEnergy | Total stamina pool                  | Drains while moving; when empty, turtle must rest        |
| Recovery  | Energy regeneration rate            | Higher = faster energy recovery while resting            |
| Swim      | Water terrain skill                 | Multiplier applied on Water segments                     |
| Climb     | Rock terrain skill                  | Multiplier applied on Rock segments                      |
| Age       | Days of use (races/train sessions)  | At 100, turtle is forced into Retirement                 |

Additional identity fields:

- `name`: Chosen from a predefined list (e.g., Speedy, Tank, Nitro).
- `id`: Short unique identifier for internal tracking.
- `is_active`: Boolean flag (Active vs Retired).

#### 3.2.1 Movement & Energy

Movement and energy are governed by shared physics in `entities.update_physics(terrain_type)`:

- If turtle is **resting**:
  - Energy regenerates based on `Recovery` and a global `RECOVERY_RATE`.
  - Once energy ≥ threshold (`RECOVERY_THRESHOLD * MaxEnergy`), turtle resumes running.

- If turtle is **running**:
  - Base move speed starts from `Speed`.
  - Terrain modifiers:
    - Grass: neutral (Speed only).
    - Water: `Speed * (Swim / 10.0)`.
    - Rock:  `Speed * (Climb / 10.0)`.
  - Energy drains per tick, scaled by `TERRAIN_DIFFICULTY`.
  - When energy hits 0, turtle enters **resting** state.

#### 3.2.2 Training

- Training currently improves **Speed** (MVP behavior) and increments **Age**.
- Training does **not** consume Energy (by design) but advances the turtle’s lifecycle.
- If training pushes `Age >= 100`, the turtle is **auto‑retired**.

### 3.3 Breeding System

Breeding is the long‑term progression system.

- **Eligibility**
  - Any turtle (Active or Retired) can be used as a parent.
  - After **breeding**, both parents are **removed** from the game (sacrificial).

- **Child Generation**
  - Child’s name is a simple splice of parents’ names (first half of A + last half of B).
  - For each stat:
    - Base = `max(parent_a.stat, parent_b.stat)`.
    - Apply small **non‑negative mutation**:
      - 0–20% chance +1 or +2.
      - Never below the better parent.

- **Placement**
  - Child enters the first empty Active slot.
  - If no slot is available, breeding fails (MVP) and should be surfaced to the player.

### 3.4 Economy & Betting

- **Currency:** Money ($)
- **Income:**
  - Race prizes for 1st/2nd/3rd place.
  - Optional betting payouts when enabled.

- **Shop Pricing:**
  - Each Shop turtle’s cost is derived from its stats using a simple formula:
    - Cost = `base_cost + scale * (Speed + normalized(MaxEnergy) + Recovery + Swim + Climb)`.
  - This ensures high‑stat turtles are more expensive.

- **Betting (MVP Implementation):**
  - Fixed bet options in Stable: `$0`, `$5`, `$10`.
  - Bet is deducted when the race starts (if affordable).
  - If the player finishes **1st**, a simple payout is granted (e.g., `bet * 2`).
  - If not, the bet is lost; race prizes still apply.

### 3.5 Race Track & Terrain

- Track is generated by a shared `race_track` helper:
  - A list of segments (`"grass"`, `"water"`, `"rock"`).
  - Probabilities tuned for ~60% Grass, ~20% Water, ~20% Rock.
- Both the **headless simulation** and the **visual game** use this helper to decide the current terrain at a turtle’s position.

---

## 4. User Interface (UI) Architecture

The UI is divided into several screens. For MVP, each screen is rendered by a dedicated view module under `ui/`.

### Screen 1: Main Menu (Future)

**Status:** Planned for a post‑MVP UX pass.

- Purpose: a true front door separate from the Stable.
- Buttons (planned):
  - Start / Continue
  - Stable (Roster)
  - Races
  - Shop
  - Breeding Center
  - Pond / Glade (future)

### Screen 2: Stable (Roster / Management)

**View:** `ui/menu_view.py`  
**Managers:** `RosterManager`, `ShopManager`, `RaceManager`, `BreedingManager` (for navigation)

- Layout: 3 vertical slots.
- Each slot shows (via shared turtle card component):
  - Name
  - Status tag (`[ACT]`/`[RET]`)
  - Age
  - Stats summary (Speed, MaxEnergy, Recovery, Swim, Climb)
  - Energy bar.
- Buttons per Active slot:
  - [TRAIN], [REST], [RETIRE]
- Global controls:
  - Buttons to switch to **RACE**, **BREEDING**, **SHOP**.
  - Toggle between **Active** and **Retired** views.
  - Betting buttons to set bet amount before a race.

Planned extensions:

- Tabbed roster interface `[ACTIVE] [RETIRED]` with richer styling.
- Side‑panel **Profile View** for the selected turtle, including lineage and history.

### Screen 3: Race View

**View:** `ui/race_view.py`  
**Manager:** `RaceManager`

- Visuals:
  - 3 horizontal lanes (player + 2 opponents).
  - Finish line.
  - (Future) Visible terrain segments colored by type (Grass, Water, Rock).
- HUD:
  - Speed controls: [1x], [2x], [4x].
  - Progress bar showing player progress along the track.
  - Current bet amount.

### Screen 4: Race Results

**View:** `ui/race_view.py` (results section)

- List of finishers, with:
  - Rank, Name, Status, Age.
  - The player’s turtle highlighted.
- Text summary of finish position and rewards.
- Buttons:
  - [MENU] – return to Stable.
  - [RACE AGAIN] – rerun with new track/opponents.

### Screen 5: Shop

**View:** `ui/shop_view.py`  
**Manager:** `ShopManager`

- Inventory: 3 random turtles rendered as cards.
- Each card shows:
  - Name.
  - Shared stats label (status, age, stats).
  - Price based on stats.
  - [BUY] button.
- Global Shop controls:
  - [REFRESH] (costs money unless free on first load).
  - [MENU] to return to Stable.

### Screen 6: Breeding Center

**View:** `ui/breeding_view.py`  
**Manager:** `BreedingManager`

- Shows a **combined list** of:
  - All Active turtles.
  - All Retired turtles.
- Each entry:
  - Uses the shared stats label.
  - Indicates selection state for breeding parents.
- Interactions:
  - Click to toggle a turtle as Parent A/B (max 2).
  - [BREED] button to create a child if space is available.
  - [MENU] button to return to Stable.

### Screen 7: Pond / Glade (Planned)

**Status:** Planned; not implemented in the current MVP.

- A relaxed overview space where all turtles wander.
- Clicking a turtle shows a tooltip with stats and links to Profile view.

---

## 5. Controls (Inputs)

### Mouse

- Primary input for menus and selection.
- Used for:
  - Clicking roster actions (TRAIN, REST, RETIRE).
  - Navigating between screens (Stable, Race, Shop, Breeding).
  - Selecting breeding parents.
  - Choosing bet levels.

### Keyboard (Debug / Shortcuts in MVP)

- Global:
  - `M` – Return to Stable.
- Stable:
  - `R` – Go to Race.
  - `S` – Go to Shop.
  - `B` – Go to Breeding.
  - `4/5/6` – Retire slots 1–3.
  - `Q/W/E` – Train slots 1–3.
  - `Z/X/C` – Rest slots 1–3.
- Race:
  - `1` – Speed 1x.
  - `2` – Speed 2x.
  - `3` – Speed 4x.

Future UX passes are expected to reduce reliance on keyboard shortcuts in favor of explicit on‑screen buttons.

---

## 6. Technical Implementation Details (MVP)

- **Language:** Python 3.10+
- **Library:** PyGame or pygame‑ce
- **Architecture:**
  - `entities.py` – Turtle stats and physics.
  - `game_state.py` – Generation and breeding helpers.
  - `race_track.py` – Terrain generation and lookup.
  - `managers/` – Roster, Race, Shop, Breeding managers.
  - `ui/` – Layout and per‑screen renderers.
  - `simulation.py` – Headless racing simulator for balancing.
- **State Management:**
  - Simple string‑based state machine (`STATE_MENU`, `STATE_RACE`, etc.).
  - A single `TurboShellsGame` object holds shared game state.
- **Persistence:** None for MVP (state resets on close).

---

## 7. Future Expansion (Post‑MVP)

Potential directions beyond the current scope:

- **Triathlons:** Multi‑stage races requiring well‑rounded turtles across multiple terrains.
- **Visual Polish:** Animated sprites for running, swimming, climbing; better track visuals.
- **Gym Upgrades:** Spend money to improve stat gains per training session.
- **Weather & Conditions:** Environmental modifiers (rain, heat) that affect terrain or energy.
- **Equipment:** Hats or shells that boost specific stats or modify behavior.
- **Personalities:** Hidden traits (e.g., “Lazy” = recovers fast but drains energy fast).
- **Save System:** JSON or similar persistence for the player’s stable and progression.
    # Handles the main loop, input events, and state switching
    def run(self): ...
7. Future Expansion (Post-MVP)Triathlons: Multi-stage races that require a generalist turtle.Visual Polish: Animated sprites for running/swimming/climbing.Gym Upgrades: Spend money to increase the stat gain per training session.Save System: JSON or Pickle serialization to save the stable.