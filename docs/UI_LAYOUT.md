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

## 2. Main Menu (The Stable)
*Vertical layout for 3 turtle slots.*

### Roster Slots (Container)
* **Slot 1:** `Rect(50, 80, 700, 120)`
* **Slot 2:** `Rect(50, 220, 700, 120)`
* **Slot 3:** `Rect(50, 360, 700, 120)`

### Inside a Slot (Relative to Container)
* **Turtle Name:** `(20, 10)`
* **Stats Block:** `(20, 40)` (Multiline text)
* **Energy Bar Background:** `Rect(250, 20, 300, 20)`
* **Energy Bar Fill:** `Rect(252, 22, <Variable>, 16)`
* **Action Buttons:**
    * [TRAIN]: `Rect(580, 15, 100, 30)`
    * [REST]:  `Rect(580, 50, 100, 30)`
    * [RETIRE]: `Rect(580, 85, 100, 30)`

### Bottom Navigation
* **[GO TO RACE]:** `Rect(50, 500, 200, 60)` (Green)
* **[BREEDING]:** `Rect(300, 500, 200, 60)` (Pink)
* **[SHOP]:** `Rect(550, 500, 200, 60)` (Blue)

---

## 3. The Race Screen
*Horizontal layout for side-scrolling lanes.*

### The Lanes
* **Lane 1 (Player):** `Rect(0, 100, 800, 100)`
* **Lane 2 (CPU):** `Rect(0, 220, 800, 100)`
* **Lane 3 (CPU):** `Rect(0, 340, 800, 100)`

### Race HUD (Bottom Panel)
* **Area:** `Rect(0, 480, 800, 120)`
* **Color:** Black `(0, 0, 0)`
* **Speed Controls:**
    * [1x]: `Rect(300, 520, 50, 40)`
    * [2x]: `Rect(360, 520, 50, 40)`
    * [4x]: `Rect(420, 520, 50, 40)`
* **Progress Bar:** `Rect(50, 570, 700, 10)`

---

## 4. The Shop Screen
*Grid layout for purchasing.*

### Shop Slots
* **Slot 1:** `Rect(50, 100, 200, 300)`
* **Slot 2:** `Rect(300, 100, 200, 300)`
* **Slot 3:** `Rect(550, 100, 200, 300)`

### Inside Shop Slot
* **Turtle Art/Icon:** Center `(100, 50)` relative to slot.
* **Stats Text:** `(20, 150)` relative to slot.
* **[BUY] Button:** `Rect(20, 240, 160, 40)` relative to slot.

### Shop Controls
* **[REFRESH STOCK ($5)]:** `Rect(300, 450, 200, 50)`
* **[BACK TO MENU]:** `Rect(300, 520, 200, 50)`