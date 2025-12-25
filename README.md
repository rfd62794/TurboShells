# 🐢 Turbo Shells

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Rust](https://img.shields.io/badge/Rust-Core-orange.svg)](https://www.rust-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status: Portfolio Demo](https://img.shields.io/badge/Status-Portfolio%20Demo-purple.svg)]()

**Turbo Shells** is a turtle racing management simulation featuring **procedural genetics**, **automated racing physics**, and a **hybrid Python/Rust architecture**. Breed the ultimate racing turtle through strategic selection and Mendelian inheritance.

<!-- TODO: Add hero GIF when available -->
<!-- ![Race Simulation](assets/screenshots/race_simulation.gif) -->

---

## 🎯 Portfolio Highlights

### Procedural Generation — No Sprites Required
Every turtle is **generated on-the-fly** from its genetic code. Shell size, color, pattern, limb shape, and 19 other traits are computed procedurally — zero external sprite files needed.

### NEAT-Inspired Genetics
This project evolved from a **Self-Learning Pong simulation** using NEAT (NeuroEvolution of Augmenting Topologies). The genetic systems here apply similar evolutionary principles to visual trait inheritance:
- **Mendelian inheritance** (dominant/recessive traits)
- **Mutation rates** with configurable intensity
- **Genetic similarity** calculations for breeding optimization

### Hybrid Python/Rust Architecture
Performance-critical genetics and simulation logic are implemented in **Rust** via PyO3 bindings, while the UI remains in Python/pygame for rapid iteration:

```
┌─────────────────────────────────────┐
│  Python (UI, pygame-ce)             │
│    ↓                                │
│  turboshells-core (Rust, PyO3)      │
│    • 20 gene definitions            │
│    • Mutation system                │
│    • Mendelian inheritance          │
│    • Race physics simulation        │
└─────────────────────────────────────┘
```

---

## 🎮 Features

* **Strategic Roster Management:** Limited to **3 Active Turtles** — make hard choices about who to keep.
* **Sacrificial Breeding:** Combine two retired champions. Parents are gone forever; the offspring must be worth it.
* **Physics-Based Racing:** Turtles manage **Energy**. Sprint too hard → exhaustion → forced recovery.
* **Procedural Tracks:** Random terrain (Grass, Water, Rocks) with stat-specific modifiers.
* **19-Trait Genetic System:** Shell pattern, colors, limb shape, body markings — all heritable.
* **Betting Economy:** Risk your earnings on race outcomes.

<!-- TODO: Add feature screenshots when available -->
<!--
| Roster View | Shop | Breeding |
|-------------|------|----------|
| ![Roster](assets/screenshots/roster_view.png) | ![Shop](assets/screenshots/shop_view.png) | ![Breeding](assets/screenshots/breeding_view.png) |
-->

---

## 🛠️ Built With

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Core Logic** | Rust + PyO3 | Genetics, physics, race simulation |
| **Game Engine** | pygame-ce | Rendering, input, window management |
| **UI Framework** | pygame_gui | Panels, buttons, responsive layout |
| **Logging** | Rich + Loguru | Beautiful terminal output |
| **Data** | JSON + Cryptography | Save/load with optional encryption |

---

## 🚀 Quick Start

### Prerequisites
* **Python 3.12** (required for Rust core)
* `pip` (Python package manager)
* Rust toolchain (optional, for building from source)

### Installation

```bash
# Clone the repository
git clone https://github.com/YourUsername/TurboShells.git
cd TurboShells

# Install dependencies
pip install -r requirements.txt

# Run the game
python run_game.py
```

### Building the Rust Core (Optional)

```bash
cd turboshells-core
pip install maturin
maturin build --release
pip install target/wheels/*.whl
```

---

## 🕹️ How to Play

1. **Start** with one basic turtle and $50
2. **Train** your turtle's stats (Speed, Swim, Climb, Stamina)
3. **Race** to earn money through betting
4. **Expand** your roster from the Shop
5. **Breed** retired champions to create genetically superior offspring

### Controls
| Action | Key |
|--------|-----|
| Race Speed | `1` / `2` / `3` (1x / 2x / 4x) |
| Navigate | `M` Menu, `R` Race, `S` Shop, `B` Breeding |

---

## 📊 The Genetic System

Every turtle carries DNA controlling 19+ visual and performance traits:

| Category | Traits |
|----------|--------|
| **Shell** | Base color, pattern type, pattern color, density, opacity, size |
| **Body** | Base color, pattern type, markings |
| **Limbs** | Shape (flippers/feet/fins), length, color |
| **Head** | Size, color |
| **Eyes** | Color, size |

Breeding combines parent genetics with configurable mutation rates, producing unique offspring every time.

---

## 📂 Project Structure

```
TurboShells/
├── src/                    # Python source
│   ├── main.py             # Game entry point
│   ├── core/               # Core systems (monitoring, data, rust_bridge)
│   ├── game/               # Game logic (entities, simulation, race_track)
│   ├── genetics/           # Python genetics (fallback)
│   ├── managers/           # Game state managers
│   └── ui/                 # pygame_gui panels and views
├── turboshells-core/       # Rust library
│   └── src/
│       ├── genetics/       # Rust genetics implementation
│       └── simulation/     # Rust physics and race engine
├── docs/                   # 60+ documentation files
├── tests/                  # 80+ test files
└── tools/                  # Development utilities
```

---

## 🔮 Future Direction

The Rust core migration is the foundation for:
- **Advanced adaptation systems** — environmental fitness, natural selection
- **Population-scale simulations** — parallel evolution with `rayon`
- **Cross-platform builds** — native performance on all platforms

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **NEAT-Python** — Inspiration for the genetic architecture
- **pygame-ce** — Modern pygame fork with active development
- **PyO3** — Seamless Python/Rust interoperability