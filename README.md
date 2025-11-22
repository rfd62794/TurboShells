# 🐢 Turbo Shells

**Turbo Shells** is a minimal management simulation game built with Python and PyGame. The goal is simple: breed the ultimate racing turtle.

In this game, you don't control the racer—you manage the *racer*. Balance your economy, train your turtles to improve their stats, and make high-stakes decisions on when to retire a champion to breed the next generation.

## 🎮 Features

* **Strategic Roster Management:** You are limited to **3 Active Turtles**. You must make hard choices about who to keep and who to release.
* **Sacrificial Breeding:** Combine two retired champions to create a new offspring with inherited stats and mutations. The parents are gone forever, so the baby *must* be worth it.
* **Automated Racing Physics:** Turtles don't just run; they manage **Energy**. If they sprint too hard, they hit exhaustion and must stop to recover.
* **Procedural Tracks:** Races feature random combinations of Grass, Water (Swim check), and Rocks (Climb check).
* **Betting System:** Grind for cash by betting on your own turtles.

## 🛠️ Installation & Setup

### Prerequisites
* Python 3.x installed.
* `pip` (Python package manager).

### Steps
1.  **Clone or Download** this repository.
2.  **Install Dependencies:**
    This project requires `pygame`.
    ```bash
    pip install pygame
    ```
3.  **Run the Game:**
    ```bash
    python main.py
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
├── main.py           # The entry point and game loop
├── README.md         # This file
├── GDD.md            # The Game Design Document
└── assets/           # (Future) Images and sounds