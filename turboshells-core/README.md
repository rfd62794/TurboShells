# turboshells-core 🦀

High-performance Rust library for TurboShells turtle racing game.

## Overview

This library provides the compute-intensive core systems with Python bindings via PyO3:

| Module | Description |
|--------|-------------|
| `genetics` | 20 gene definitions, Mendelian inheritance, mutation system |
| `simulation` | Turtle physics, terrain effects, race engine |

## Python API

```python
import turboshells_core as tc

# Genetics
genetics = tc.PyGenetics()
parent1 = genetics.generate_random()
parent2 = genetics.generate_random()
child = genetics.inherit(parent1, parent2)
mutated = genetics.mutate(child, rate=0.1)

# Simulation
turtle = tc.PyTurtle("Speedster", speed=10, energy=80, recovery=5, swim=5, climb=5)
race = tc.PyRace(track_length=1500.0)
race.add_turtle(turtle)
winner = race.run()
```

## Building

Requires Python 3.12 and Rust toolchain.

```bash
# Install maturin
pip install maturin

# Build wheel
maturin build --release

# Install
pip install target/wheels/turboshells_core-*.whl
```

## Architecture

```
src/
├── lib.rs              # PyO3 module entry
├── types.rs            # Rgb, TurtleStats, GeneValue
├── genetics/
│   ├── genes.rs        # 20 gene definitions
│   ├── mutation.rs     # RGB/discrete/continuous mutations
│   └── inheritance.rs  # Mendelian + blended inheritance
└── simulation/
    ├── turtle.rs       # Turtle struct + physics
    ├── terrain.rs      # 6 terrain types
    └── race.rs         # Race simulation loop
```

## Performance

The Rust implementation provides:
- **Zero-copy** genetics operations
- **Parallel-ready** architecture (rayon-compatible)
- **Memory-safe** physics simulation
- Typical 10-100x speedup over pure Python for batch operations

## License

MIT — same as the main TurboShells project.
