# UI Test Suite

This directory contains the organized test suite for all UI-related components and functionality in TurboShells.

## 📁 Test Organization

```text
tests/ui/
├── components/          # Reusable component tests
│   ├── test_reusable_components.py
│   └── test_layout_manager.py
├── panels/              # UI Panel tests
│   ├── test_main_menu_refactored.py
│   ├── test_button_functionality.py
│   └── test_main_menu_legacy.py
├── integration/         # Integration tests
│   ├── test_main_menu_integration.py
│   ├── test_game_integration_legacy.py
│   └── verify_integration_legacy.py
├── debug/              # Debug and diagnostic scripts
│   ├── debug_buttons.py
│   ├── debug_container.py
│   └── ...
├── run_ui_tests.py     # Main test runner
└── README.md           # This file
```

## 🚀 Running Tests

### Quick Start
```bash
# Run all UI tests
python tests/ui/run_ui_tests.py

# Run with verbose output
python tests/ui/run_ui_tests.py -v

# Run with coverage
python tests/ui/run_ui_tests.py -c
```

### Specific Categories
```bash
# Component tests only
python tests/ui/run_ui_tests.py components

# Panel tests only
python tests/ui/run_ui_tests.py panels

# Integration tests only
python tests/ui/run_ui_tests.py integration
```

### Specific Test Files
```bash
# Run a specific test file
python tests/ui/run_ui_tests.py -t test_main_menu_refactored.py

# Run with coverage
python tests/ui/run_ui_tests.py -t test_main_menu_refactored.py -c
```

### Quick Tests
```bash
# Run quick subset of important tests
python tests/ui/run_ui_tests.py -q
```

### List Available Tests
```bash
# List all available test files
python tests/ui/run_ui_tests.py -l
```

## 🧪 Test Categories

### Components (`tests/ui/components/`)
Tests for reusable UI components:
- **Button Component**: Styling, events, callbacks, positioning
- **MoneyDisplay Component**: Formatting, updates, configuration
- **Container Component**: Layout, child management
- **Panel Component**: Window creation, headers, styling
- **Reusability**: Component usage across different contexts

### Panels (`tests/ui/panels/`)
Tests for complete UI panels:
- **Main Menu Refactored**: Full functionality, architecture, integration
- **Button Functionality**: Interactive testing of button actions
- **Legacy Tests**: Original tests for comparison

### Integration (`tests/ui/integration/`)
Tests for system integration:
- **Game State Integration**: Main Menu with game state interface
- **UI Manager Integration**: Main Menu with pygame_gui
- **Event Bus Integration**: Main Menu with event system
- **Navigation Integration**: Main Menu with navigation system
- **Performance Integration**: Performance testing in context

### Debug (`tests/ui/debug/`)
Diagnostic and debugging scripts:
- **Button Debug**: Visual debugging of button issues
- **Container Debug**: Layout and positioning verification
- **Component Debug**: Component-specific diagnostics

## 🎯 Test Coverage

### Main Menu Refactored Tests
- ✅ **Initialization**: Panel creation and setup
- ✅ **Component Creation**: All components created correctly
- ✅ **Button Positioning**: Proper layout and spacing
- ✅ **Money Display**: Positioning and formatting
- ✅ **Event Handling**: Proper event delegation
- ✅ **Navigation Actions**: All button actions work
- ✅ **Component Isolation**: SRP compliance
- ✅ **Visual Layout**: No overlapping elements
- ✅ **Integration Compatibility**: Works with game systems

### Component Tests
- ✅ **Button**: All styling options, callbacks, events
- ✅ **MoneyDisplay**: Formatting, updates, configuration
- ✅ **Container**: Layout management, child components
- ✅ **Panel**: Window creation, headers, styling
- ✅ **Reusability**: Cross-context usage

### Integration Tests
- ✅ **Game State**: Real game state interface
- ✅ **UI Manager**: pygame_gui integration
- ✅ **Event Bus**: Event system integration
- ✅ **Navigation**: Navigation system integration
- ✅ **Performance**: Creation, update, render performance

## 🔧 Test Configuration

### Pytest Configuration
The tests use pytest with configuration in `pytest.ini`:
- Test discovery patterns
- Markers for test categorization
- Coverage settings
- Output formatting

### Fixtures
Common test fixtures:
- `pygame_setup`: Initialize pygame and UI manager
- `mock_game_state`: Mock game state interface
- `main_menu`: Fully configured main menu instance
- `mock_event_bus`: Mock event bus for testing

## 📊 Test Results

### Current Status
- ✅ **Component Tests**: All passing
- ✅ **Panel Tests**: All passing
- ✅ **Integration Tests**: All passing
- ✅ **Performance Tests**: All passing

### Coverage
- **Components**: ~95% coverage
- **Panels**: ~90% coverage
- **Integration**: ~85% coverage

## 🐛 Debugging

### When Tests Fail
1. **Check pygame setup**: Ensure display is properly initialized
2. **Verify imports**: Check Python path and module imports
3. **Component state**: Verify components are created and configured
4. **Event handling**: Check event delegation and callbacks

### Debug Scripts
Use debug scripts in `tests/ui/debug/`:
- `debug_buttons.py`: Visual button debugging
- `debug_container.py`: Layout and positioning debugging

### Common Issues
- **pygame display not set**: Always initialize display before creating UI elements
- **Import errors**: Check sys.path and module structure
- **Container positioning**: Verify container and component coordinates
- **Event handling**: Ensure proper event delegation chain

## 🚀 Adding New Tests

### Component Tests
1. Add test class to `tests/ui/components/test_reusable_components.py`
2. Follow naming convention: `Test<ComponentName>`
3. Use common fixtures where possible
4. Test initialization, configuration, events, and edge cases

### Panel Tests
1. Add test class to `tests/ui/panels/`
2. Follow naming convention: `Test<PanelName>`
3. Test creation, components, events, and integration
4. Use mock game state for isolated testing

### Integration Tests
1. Add test class to `tests/ui/integration/`
2. Test with real game systems
3. Include performance tests where relevant
4. Test error handling and edge cases

## 📝 Test Standards

### Naming Conventions
- Test classes: `Test<ComponentName>` or `Test<PanelName>`
- Test methods: `test_<functionality>_description`
- Fixtures: `<component>_setup` or descriptive name

### Test Structure
```python
class TestComponent:
    def test_initialization(self, setup):
        # Test basic initialization

    def test_functionality(self, setup):
        # Test main functionality

    def test_edge_cases(self, setup):
        # Test edge cases and error handling
```

### Assertions
- Use descriptive assertion messages
- Test both positive and negative cases
- Verify component state and behavior
- Check integration points

## 🔄 Continuous Integration

### Automated Testing
- Tests run on every commit
- Coverage reports generated
- Performance benchmarks tracked
- Integration tests validated

### Quality Gates
- All tests must pass
- Coverage threshold: >80%
- Performance regression checks
- Integration validation

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pygame_gui Documentation](https://pygame-gui.readthedocs.io/)
- [Test-Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)
- [Component Testing Best Practices](https://martinfowler.com/articles/microservice-testing/)

---

For questions or issues with the UI test suite, please check the debug scripts or create an issue in the project repository.
