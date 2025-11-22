# UI Layout Guide: Turbo Shells
**Resolution:** 800 x 600 px
**Padding:** Standard padding is 20px.

## 1. Global Header (Top Bar)
*Used on every screen.*
* **Area:** `Rect(0, 0, 800, 60)`
* **Color:** Dark Grey `(30, 30, 30)`
* **Title Text:** `(20, 15)`
* **Money Display:** `(650, 15)` (Top Right)

---

## 2. Stable Screen (Roster / Management)
*Vertical layout for 3 turtle slots, plus view toggles and betting controls.*

### 2.1 Roster Slots (Container)
* **Slot 1:** `Rect(50, 80, 700, 120)`
* **Slot 2:** `Rect(50, 220, 700, 120)`
* **Slot 3:** `Rect(50, 360, 700, 120)`

These slots show either the **Active Roster** or **Retired Roster** depending on the view toggle.

### 2.2 Inside a Slot (Relative to Container)
* **Turtle Name:** `(20, 10)`
* **Stats Block:** `(20, 40)` (Multiline text)
  * Current implementation: `[ACT]/[RET] Age:X Spd: Nrg: Rec: Swm: Clm:`
* **Energy Bar Background:** `Rect(250, 20, 300, 20)`
* **Energy Bar Fill:** `Rect(252, 22, <Variable>, 16)`
* **Action Buttons (Active view only):**
    * [TRAIN]: `Rect(580, 15, 100, 30)`
    * [REST]:  `Rect(580, 50, 100, 30)`
    * [RETIRE]: `Rect(580, 85, 100, 30)`

In **Retired view**, these buttons are visually present but clicks are ignored (read‑only view).

### 2.3 View Toggles (Active vs Retired)
* Located above the bottom navigation bar.
* **[ACTIVE]:** `Rect(50, 450, 120, 40)`
* **[RETIRED]:** `Rect(190, 450, 120, 40)`

Current behavior:

- ACTIVE selected (green border): slots show the **Active Roster**.
- RETIRED selected: slots show up to the first 3 turtles in **Retired Roster**.

Planned: Visually upgrade these to proper tabbed UI (`[ACTIVE] [RETIRED]`).

### 2.4 Betting Controls (MVP)
* Located to the right of the view toggles.
* **[BET: $0]:** `Rect(350, 450, 120, 40)`
* **[BET: $5]:** `Rect(490, 450, 120, 40)`
* **[BET: $10]:** `Rect(630, 450, 120, 40)`

Current behavior:

- Clicking a button sets the current bet amount before a race.
- Selected bet is highlighted; buttons also respond to hover.

### 2.5 Bottom Navigation
* **[GO TO RACE]:** `Rect(50, 500, 200, 60)` (Green)
* **[BREEDING]:** `Rect(300, 500, 200, 60)` (Pink)
* **[SHOP]:** `Rect(550, 500, 200, 60)` (Blue)

---

## 3. The Race Screen
*Horizontal layout for side-scrolling lanes.*

### 3.1 The Lanes
* **Lane 1 (Player):** `Rect(0, 100, 800, 100)`
* **Lane 2 (CPU):** `Rect(0, 220, 800, 100)`
* **Lane 3 (CPU):** `Rect(0, 340, 800, 100)`

### 3.2 Race HUD (Bottom Panel)
* **Area:** `Rect(0, 480, 800, 120)`
* **Color:** Black `(0, 0, 0)`
* **Speed Controls:**
    * [1x]: `Rect(300, 520, 50, 40)`
    * [2x]: `Rect(360, 520, 50, 40)`
    * [4x]: `Rect(420, 520, 50, 40)`
* **Progress Bar:** `Rect(50, 570, 700, 10)`

Current condition:

- Lanes are visually uniform; terrain is logical only (via physics).
- Header displays current speed and bet amount.

Desired condition (future):

- Draw track segments along each lane with different colors:
  - Grass: Green strips.
  - Water: Blue strips.
  - Rock: Grey strips.
- Optionally show a mini‑map or track preview.

---

## 4. The Shop Screen
*Grid layout for purchasing.*

### 4.1 Shop Slots
* **Slot 1:** `Rect(50, 100, 200, 300)`
* **Slot 2:** `Rect(300, 100, 200, 300)`
* **Slot 3:** `Rect(550, 100, 200, 300)`

### 4.2 Inside Shop Slot (Relative)
* **Turtle Art/Icon:** Center `(100, 50)` relative to slot. *(Currently placeholder rectangle only.)*
* **Stats Text:** `(20, 150)` relative to slot.
  * Uses the same label format as Stable (status, age, stats).
* **Price Text:** `(20, 250)` relative to slot.
* **[BUY] Button:** `Rect(20, 240, 160, 40)` relative to slot.

### 4.3 Shop Controls
* **[REFRESH STOCK ($5)]:** `Rect(300, 450, 200, 50)`
* **[BACK TO MENU]:** `Rect(300, 520, 200, 50)`

---

## 5. Breeding Screen (Current)

*List layout for selecting breeding parents.*

### 5.1 List Area
* Rows start at `y = 120`, spaced by `+80` per turtle.
* Row rect (per turtle): `Rect(50, y, 600, 60)`

Each row shows:

- Index + shared stats label (`[ACT]/[RET] Age:X ...`).
- Border color:
  - Grey for unselected.
  - Green if selected and active.
  - Red if selected and retired.

### 5.2 Controls
* **[BREED]:** `Rect(300, 450, 200, 50)` *(currently drawn in code, planned to be added here explicitly once finalized)*
* **[BACK TO MENU]:** `Rect(300, 520, 200, 50)`

Desired refinements:

- Dedicated BREED button rect in this document with exact coordinates.
- Optional visual indicator showing Parent A vs Parent B.

---

## 6. Future Screens (Planned)

### 6.1 Main Menu (Front Door)

* Separate screen from Stable.
* Likely layout:
  - Centered vertical stack of buttons:
    - [CONTINUE]/[NEW GAME]
    - [STABLE]
    - [RACES]
    - [SHOP]
    - [BREEDING]
    - [POND]
* Reuses **Global Header** for title + money summary (if appropriate).

### 6.2 Pond / Glade Screen

* Visual "overworld" showing all turtles wandering.
* Likely layout:
  - Large central area (similar to lanes) for turtle movement.
  - Minimal HUD: back button, maybe filter toggles.
* Interactions:
  - Hover or click on a turtle pops a small tooltip near it with name + key stats.
  - Clicking the tooltip opens full Profile view (Stable).