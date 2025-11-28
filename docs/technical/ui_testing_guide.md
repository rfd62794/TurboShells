# UI Testing Guide

## Overview

This guide provides comprehensive information about testing the pygame_gui-based UI system in TurboShells. The test suite ensures 95%+ coverage of all UI functionality with robust integration testing and performance validation.

## Test Structure

### Directory Organization

```
tests/ui/
├── panels/                    # Individual panel test suites
│   ├── test_settings_panel.py
│   ├── test_shop_panel.py
│   ├── test_breeding_panel.py
│   ├── test_voting_panel.py
│   └── test_main_menu_refactored.py
├── integration/              # System integration tests
│   └── test_ui_system_integration.py
├── components/               # Reusable component tests
│   ├── test_reusable_components.py
│   └── test_settings_view_refactored.py
├── debug/                    # Diagnostic and debugging tools
│   ├── debug_buttons.py
│   └── debug_container.py
├── fixtures/                 # Test data and utilities
│   └── ui.py
└── README.md                 # This file
```

### Test Categories

#### Unit Tests
- **Panel Initialization**: Verify proper setup and configuration
- **Component Functionality**: Test individual UI components
- **Event Handling**: Validate event processing and responses
- **State Management**: Test game state integration and data binding

#### Integration Tests
- **Cross-Panel Communication**: Test event bus and navigation
- **State Synchronization**: Verify data binding consistency
- **System Performance**: Test memory management and resource cleanup
- **Error Propagation**: Validate error handling across the system

#### Performance Tests
- **Memory Management**: Detect leaks and verify cleanup
- **Concurrent Access**: Test thread safety and race conditions
- **Load Testing**: Performance with large datasets
- **Resource Usage**: Monitor pygame_gui resource consumption

## Running Tests

### Quick Start

```bash
# Run all UI tests
python -m pytest tests/ui/ -v

# Run with coverage
python -m pytest tests/ui/ --cov=ui --cov-report=html

# Run specific panel tests
python -m pytest tests/ui/panels/test_settings_panel.py -v

# Run integration tests only
python -m pytest tests/ui/integration/ -v
```

### Test Markers

Use pytest markers to run specific test categories:

```bash
# Run only unit tests
python -m pytest tests/ui/ -m "not integration"

# Run only integration tests
python -m pytest tests/ui/ -m integration

# Run performance tests
python -m pytest tests/ui/ -m performance

# Run smoke tests (quick validation)
python -m pytest tests/ui/ -m smoke
```

## Test Fixtures

### Common Fixtures

#### `pygame_setup`
Initializes pygame and creates a UI manager for testing:

```python
@pytest.fixture
def pygame_setup(self):
    """Setup pygame for testing."""
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    manager = pygame_gui.UIManager((1024, 768))
    yield screen, manager
    pygame.quit()
```

#### `mock_game_state`
Creates a realistic mock game state:

```python
@pytest.fixture
def mock_game_state(self):
    """Create mock game state for testing."""
    class MockGame:
        def __init__(self):
            self.money = 1000
            self.resolution = (1024, 768)
            self.master_volume = 0.8
            # ... other game state properties
    return MockGame()
```

#### `panel_setup`
Creates a fully configured panel:

```python
@pytest.fixture
def settings_panel(self, pygame_setup, mock_game_state):
    """Create settings panel for testing."""
    screen, manager = pygame_setup
    game_state_interface = TurboShellsGameStateInterface(mock_game_state)
    data_binding = DataBindingManager()
    
    panel = SettingsPanel(game_state_interface, data_binding)
    panel.initialize(manager)
    
    return panel, manager, mock_game_state
```

## Writing Tests

### Test Structure Template

```python
class TestPanelName:
    """Test suite for PanelName with pygame_gui."""
    
    @pytest.fixture
    def panel_setup(self, pygame_setup, mock_game_state):
        """Create panel for testing."""
        # Panel setup code
        return panel, manager, game_state
    
    def test_initialization(self, panel_setup):
        """Test panel initialization."""
        panel, manager, game_state = panel_setup
        
        # Verify panel creation
        assert panel is not None
        assert hasattr(panel, 'window')
        
        # Verify game state integration
        assert panel.game_state_interface is not None
        
        # Verify UI manager integration
        assert panel.ui_manager == manager
    
    def test_functionality(self, panel_setup):
        """Test main functionality."""
        panel, manager, game_state = panel_setup
        
        # Test core functionality
        # ... test code
    
    def test_error_handling(self, panel_setup):
        """Test error handling."""
        panel, manager, game_state = panel_setup
        
        # Test error conditions
        # ... error handling tests
```

### Best Practices

#### 1. Use Descriptive Test Names
```python
def test_settings_panel_tab_navigation(self, panel_setup):
    """Test tab navigation functionality."""
    # Good: Specific and descriptive

def test_panel_works(self, panel_setup):
    """Test panel."""
    # Bad: Too generic
```

#### 2. Test Both Positive and Negative Cases
```python
def test_purchase_with_sufficient_funds(self, panel_setup):
    """Test successful purchase with enough money."""
    # Set up sufficient funds
    # Verify purchase succeeds

def test_purchase_with_insufficient_funds(self, panel_setup):
    """Test purchase failure with insufficient funds."""
    # Set up insufficient funds
    # Verify purchase fails gracefully
```

#### 3. Use Parameterized Testing
```python
@pytest.mark.parametrize("money_amount", [0, 50, 500, 1000, 5000])
def test_different_money_amounts(self, panel_setup, money_amount):
    """Test shop behavior with different money amounts."""
    # Test with various money amounts
```

#### 4. Verify State Changes
```python
def test_settings_persistence(self, panel_setup):
    """Test that settings persist to game state."""
    panel, manager, game_state = panel_setup
    
    # Modify UI settings
    # Verify game state updated
    assert game_state.resolution == expected_value
```

#### 5. Test Event Handling
```python
def test_event_handling(self, panel_setup):
    """Test event handling integration."""
    panel, manager, game_state = panel_setup
    
    # Create test events
    mouse_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (100, 100)})
    key_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE})
    
    # Test event processing
    result1 = panel.handle_event(mouse_event)
    result2 = panel.handle_event(key_event)
    
    # Verify results
    assert isinstance(result1, bool)
    assert isinstance(result2, bool)
```

## Specific Panel Testing

### Settings Panel Tests

#### Key Test Areas
- **Tab Navigation**: Switching between Graphics, Audio, Controls, Gameplay, System tabs
- **Settings Controls**: Sliders, dropdowns, checkboxes functionality
- **Data Binding**: Two-way synchronization with game state
- **Persistence**: Settings saved and loaded correctly

#### Example Test
```python
def test_graphics_settings_controls(self, panel_setup):
    """Test graphics settings controls."""
    panel, manager, game_state = panel_setup
    
    # Switch to graphics tab
    panel.tab_container.set_current_tab(0)
    graphics_panel = panel.content_panels[0]
    
    # Test resolution dropdown
    resolution_dropdown = graphics_panel.resolution_dropdown
    assert resolution_dropdown.selected_option == str(game_state.resolution)
    
    # Change resolution
    resolution_dropdown.selected_option = "1920x1080"
    resolution_dropdown.on_changed()
    
    # Verify game state updated
    assert game_state.resolution == (1920, 1080)
```

### Shop Panel Tests

#### Key Test Areas
- **Inventory Display**: Turtle cards with correct information
- **Purchase Validation**: Money checking and roster space validation
- **Money Handling**: Deduction and display updates
- **Error Messages**: Clear feedback for failed purchases

#### Example Test
```python
def test_purchase_interaction(self, panel_setup):
    """Test turtle purchase interaction."""
    panel, manager, game_state, turtles = panel_setup
    
    # Get first turtle and its card
    turtle = turtles[0]
    card = panel.turtle_cards[0]
    
    # Verify initial state
    initial_money = game_state.money
    turtle_price = turtle.calculate_price()
    
    # Simulate purchase
    card.buy_button.on_clicked()
    
    # Verify purchase processed
    assert game_state.money == initial_money - turtle_price
    assert turtle in game_state.roster
```

### Breeding Panel Tests

#### Key Test Areas
- **Parent Selection**: Validation and duplicate prevention
- **Genetics Inheritance**: Trait calculation and mutation
- **Offspring Generation**: Creation and display
- **Cost Validation**: Money checking and deduction

#### Example Test
```python
def test_genetics_inheritance(self, panel_setup):
    """Test genetics inheritance patterns."""
    panel, manager, game_state, parents, offspring = panel_setup
    
    # Select parents with distinct traits
    # ... selection code
    
    # Perform breeding
    panel.breed_button.on_clicked()
    
    # Verify offspring inherits traits
    child = panel.offspring_display.offspring[0]
    
    # Traits should be between parents (with mutation)
    parent1_speed = parents[0].speed
    parent2_speed = parents[1].speed
    min_expected = min(parent1_speed, parent2_speed) - 2
    max_expected = max(parent1_speed, parent2_speed) + 2
    
    assert min_expected <= child.speed <= max_expected
```

### Voting Panel Tests

#### Key Test Areas
- **Vote Selection**: Radio button functionality and mutual exclusion
- **Vote Submission**: Validation and cost checking
- **Results Display**: Vote counting and percentage calculation
- **History Tracking**: Previous votes and influence calculation

#### Example Test
```python
def test_vote_submission(self, panel_setup):
    """Test vote submission process."""
    panel, manager, game_state, vote_data = panel_setup
    
    # Select an option
    option_display = panel.vote_options[0]
    option_display.radio_button.selected = True
    option_display.radio_button.on_changed()
    
    # Verify initial state
    initial_money = game_state.money
    vote_cost = vote_data['cost']
    
    # Submit vote
    panel.vote_button.on_clicked()
    
    # Verify money deducted and vote recorded
    assert game_state.money == initial_money - vote_cost
    assert len(game_state.voting_results) > 0
```

## Integration Testing

### System Integration Tests

#### Key Test Areas
- **Cross-Panel Communication**: Event bus functionality
- **State Synchronization**: Data binding across panels
- **Navigation**: Scene controller and panel switching
- **Performance**: Memory management and resource cleanup

#### Example Test
```python
def test_scene_navigation(self, ui_system):
    """Test scene navigation between panels."""
    scene_controller = ui_system['scene_controller']
    panels = ui_system['panels']
    
    # Test navigation to each scene
    scenes = ['main_menu', 'settings', 'shop', 'breeding', 'voting']
    
    for scene in scenes:
        # Navigate to scene
        scene_controller.goto_state(scene)
        
        # Verify scene active
        assert scene_controller.current_state == scene
        
        # Verify corresponding panel visible
        panel = panels[scene]
        assert panel.visible
        
        # Verify other panels hidden
        for other_scene, other_panel in panels.items():
            if other_scene != scene:
                assert not other_panel.visible
```

### Performance Testing

#### Memory Management
```python
def test_memory_management(self, ui_system):
    """Test memory management across panels."""
    import gc
    
    # Get initial memory usage
    gc.collect()
    initial_objects = len(gc.get_objects())
    
    # Create and destroy panels
    for _ in range(10):
        temp_panel = SettingsPanel(ui_system['game_state_interface'], ui_system['data_binding'])
        temp_panel.initialize(ui_system['ui_manager'].manager)
        temp_panel.hide()
        del temp_panel
    
    # Check for memory leaks
    gc.collect()
    final_objects = len(gc.get_objects())
    object_growth = final_objects - initial_objects
    assert object_growth < 1000  # Allow some growth but not excessive
```

#### Concurrent Access
```python
def test_concurrent_access(self, ui_system):
    """Test concurrent access to UI system."""
    import threading
    
    results = []
    
    def access_panel(panel_name):
        try:
            panel = ui_system['panels'][panel_name]
            for _ in range(10):
                if hasattr(panel, 'update'):
                    panel.update(0.016)
            results.append(f"{panel_name} success")
        except Exception as e:
            results.append(f"{panel_name} error: {e}")
    
    # Create threads for each panel
    threads = []
    for panel_name in ui_system['panels'].keys():
        thread = threading.Thread(target=access_panel, args=(panel_name,))
        threads.append(thread)
        thread.start()
    
    # Wait for completion
    for thread in threads:
        thread.join()
    
    # Verify all threads completed successfully
    for result in results:
        assert "success" in result
```

## Debugging Tools

### Debug Scripts

The `tests/ui/debug/` directory contains diagnostic tools:

#### `debug_buttons.py`
Visual debugging of button issues:
- Button visibility and positioning
- Event handling verification
- State changes and callbacks

#### `debug_container.py`
Layout and positioning debugging:
- Container boundaries and positioning
- Child component layout
- Resize behavior verification

### Running Debug Tools

```bash
# Run button debug
python tests/ui/debug/debug_buttons.py

# Run container debug
python tests/ui/debug/debug_container.py
```

### Common Debugging Techniques

#### 1. Visual Inspection
```python
# Add visual markers for debugging
pygame.draw.rect(screen, (255, 0, 0), component.rect, 2)
```

#### 2. Event Logging
```python
def handle_event(self, event):
    print(f"[DEBUG] {self.__class__.__name__} handling: {event}")
    # ... event handling code
```

#### 3. State Verification
```python
# Print current state for debugging
print(f"[DEBUG] Game state: {self.game_state_interface.get_all()}")
```

## Continuous Integration

### Automated Testing

The test suite is designed for CI/CD integration:

```yaml
# Example GitHub Actions workflow
- name: Run UI Tests
  run: |
    python -m pytest tests/ui/ --cov=ui --cov-report=xml
    
- name: Upload Coverage
  uses: codecov/codecov-action@v1
  with:
    file: ./coverage.xml
```

### Quality Gates

- **Coverage Threshold**: 95% minimum coverage
- **Performance Limits**: Tests must complete within time limits
- **Memory Limits**: No memory leaks detected
- **Error Handling**: All error cases handled gracefully

## Troubleshooting

### Common Issues

#### 1. pygame Display Not Set
```python
# Error: pygame display not set
# Solution: Always initialize pygame in fixtures
@pytest.fixture
def pygame_setup(self):
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    # ... rest of setup
```

#### 2. Import Errors
```python
# Error: Import errors
# Solution: Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
```

#### 3. Component Not Found
```python
# Error: Component not found
# Solution: Verify component creation and naming
assert hasattr(panel, 'component_name')
```

### Performance Issues

#### 1. Slow Test Execution
- Use `@pytest.mark.skip` for expensive tests
- Implement test caching for repeated operations
- Use mock objects for expensive dependencies

#### 2. Memory Leaks
- Ensure proper cleanup in fixtures
- Use `gc.collect()` in memory tests
- Verify pygame_gui resource cleanup

### Test Failures

#### 1. Flaky Tests
- Avoid time-dependent assertions
- Use explicit waits instead of sleep
- Mock external dependencies

#### 2. Environment Issues
- Ensure consistent pygame initialization
- Use absolute paths for test data
- Verify Python path configuration

## Best Practices Summary

1. **Use Comprehensive Fixtures**: Reusable setup code for consistency
2. **Test Both Success and Failure**: Verify error handling
3. **Use Parameterized Tests**: Test multiple scenarios efficiently
4. **Verify State Changes**: Ensure game state updates correctly
5. **Test Event Handling**: Validate event processing
6. **Include Performance Tests**: Monitor memory and resource usage
7. **Document Test Intent**: Clear test names and docstrings
8. **Maintain Test Independence**: Tests should not depend on each other
9. **Use Mock Objects**: Isolate tests from external dependencies
10. **Regular CI Validation**: Ensure tests pass in automated environments

---

This guide provides a comprehensive foundation for testing the pygame_gui UI system in TurboShells. Follow these practices to maintain high test quality and ensure robust UI functionality.
