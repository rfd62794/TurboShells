# Test Organization Structure

## Overview
The TurboShells test suite has been reorganized to mirror the `src/` directory structure for better maintainability and clarity.

## Directory Structure

### SRC-MIRRORED Structure (Recommended)
```
tests/
├── src/                           # Tests mirroring src/ structure
│   ├── core/                      # Core system tests
│   │   ├── game/                  # Game-specific tests
│   │   │   ├── test_game_state.py # Turtle generation, breeding, cost
│   │   │   ├── test_race_track.py # Track generation, terrain, checkpoints
│   │   │   └── test_core_mechanics.py # Turtle physics, energy, movement
│   │   ├── test_data_structures.py # Data validation, serialization
│   │   └── test_error_handling.py # Error recovery, logging
│   ├── genetics/                  # Genetics system tests
│   │   └── test_genetics_system.py # Genetics, inheritance, mutation
│   ├── managers/                  # Manager tests (future)
│   └── ui/                        # UI tests (future)
├── integration/                   # Workflow and system interaction tests
│   └── test_game_logic.py        # Complete game workflows
├── performance/                   # Performance and optimization tests
│   └── test_performance_optimization.py  # Caching, lazy loading, monitoring
├── unit/                         # Legacy unit tests (deprecated)
├── conftest.py                   # Shared fixtures and utilities
├── run_src_mirrored_tests.py     # New SRC-mirrored test runner (recommended)
├── run_organized_tests.py       # Legacy organized test runner
└── run_tests.py                  # Legacy test runner
```

### Legacy Structure (Deprecated)
```
tests/
├── unit/                          # Individual component tests
├── integration/                   # Workflow and system interaction tests
├── performance/                   # Performance and optimization tests
└── run_organized_tests.py        # Legacy organized test runner
```

## Test Categories

### Core Game Tests (src/core/game/)
- **Purpose**: Test game-specific functionality
- **Files**: 
  - `test_game_state.py` - Turtle generation, breeding, economics
  - `test_race_track.py` - Track generation, terrain, checkpoints
  - `test_core_mechanics.py` - Turtle physics, energy, movement

### Core System Tests (src/core/)
- **Purpose**: Test core system functionality
- **Files**: 
  - `test_data_structures.py` - Data validation, serialization
  - `test_error_handling.py` - Error recovery, logging

### Genetics Tests (src/genetics/)
- **Purpose**: Test genetics system functionality
- **Files**: 
  - `test_genetics_system.py` - Genetics, inheritance, mutation

### Integration Tests (integration/)
- **Purpose**: Test complete workflows and system interactions
- **Focus**: Real-world usage scenarios
- **Coverage**: Game logic, breeding programs, economics simulation

### Performance Tests (performance/)
- **Purpose**: Test performance characteristics and optimizations
- **Focus**: Caching, memory management, algorithm efficiency
- **Coverage**: Lazy loading, object pooling, search algorithms

## Running Tests

### SRC-Mirrored Test Runner (Recommended)
```bash
python tests/run_src_mirrored_tests.py
```

### Individual Test Suites
```bash
# Core game tests with coverage
python -m pytest tests/src/core/game/ --cov=src

# Core system tests
python -m pytest tests/src/core/

# Genetics tests
python -m pytest tests/src/genetics/

# Integration tests
python -m pytest tests/integration/

# Performance tests
python -m pytest tests/performance/
```

### Legacy Test Runners
```bash
# Legacy organized runner
python tests/run_organized_tests.py

# Original runner
python tests/run_tests.py
```

## Test Statistics

- **Total Tests**: 154+
- **Pass Rate**: 100%
- **Coverage**: 17% (focused on core components)
- **Execution Time**: ~5 seconds

## Key Improvements

1. **SRC Structure Mirroring**: Tests follow the same structure as source code
2. **Better Organization**: Clear mapping between source and test files
3. **Maintainability**: Easy to find tests for specific modules
4. **Scalability**: Simple to add tests for new modules
5. **Logical Grouping**: Related tests are grouped together

## Migration Benefits

- **Developer Experience**: Developers can easily find tests for the code they're working on
- **Code Navigation**: IDE navigation between source and test files is intuitive
- **Test Discovery**: Easy to run tests for specific modules
- **Documentation**: Test structure serves as documentation of system architecture

## Future Enhancements

- Add tests for `src/managers/` modules
- Add tests for `src/ui/` components  
- Add tests for `src/core/data/` modules
- Add tests for `src/core/systems/` modules
- Add tests for `src/core/rendering/` modules
- Expand test coverage for all components
