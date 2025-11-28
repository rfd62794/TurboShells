# UI Migration Guide

## Main Menu Integration Instructions

This guide provides step-by-step instructions for integrating the refactored Main Menu into the existing game system.

## **Step 1: Integration Strategy**

### **Option A: Safe Parallel Integration (Recommended)**
Keep both versions running and switch between them for testing.

### **Option B: Direct Replacement**
Replace the old implementation immediately (higher risk).

## **Step 2: Find Integration Points**

### **Locate Current Usage**

Search for these patterns in your codebase:

```python
# Import statements to find:
from ui.panels.main_menu_panel import MainMenuPanel
from src.ui.panels.main_menu_panel import MainMenuPanel

# Instantiation patterns:
panel = MainMenuPanel(game_state, event_bus)
ui_manager.show_panel("main_menu")
```

### **Common Integration Locations**
- `run_game.py` - Main game loop
- `ui_manager.py` - UI management system
- `state_management.py` - Game state transitions
- `main.py` - Application entry point

## **Step 3: Integration Steps**

### **Step 3.1: Update Imports**

**Find:**
```python
from ui.panels.main_menu_panel import MainMenuPanel
```

**Replace with:**
```python
from ui.panels.main_menu_panel_refactored import MainMenuPanelRefactored as MainMenuPanel
```

### **Step 3.2: Test Integration**

Create a test script to verify integration:

```python
# test_integration.py
import pygame
from ui.panels.main_menu_panel_refactored import MainMenuPanelRefactored
from game.game_state_interface import TurboShellsGameStateInterface

def test_integration():
    pygame.init()
    manager = pygame_gui.UIManager((1024, 768))
    game_state = TurboShellsGameStateInterface()
    
    # Test creation
    panel = MainMenuPanelRefactored(game_state)
    panel.manager = manager
    panel._create_window()
    
    # Test components exist
    assert panel.main_panel is not None, "Main panel not created"
    assert panel.money_display is not None, "Money display not created"
    assert panel.menu_container is not None, "Menu container not created"
    assert len(panel.menu_buttons) > 0, "Menu buttons not created"
    
    print("✅ Integration test passed!")
    
if __name__ == "__main__":
    test_integration()
```

### **Step 3.3: Update Game Integration**

**In your main game file:**

```python
# Before:
from ui.panels.main_menu_panel import MainMenuPanel

# After:
from ui.panels.main_menu_panel_refactored import MainMenuPanelRefactored as MainMenuPanel

# The rest of your code should work unchanged:
def show_main_menu():
    panel = MainMenuPanel(game_state, event_bus)
    ui_manager.add_panel(panel)
    ui_manager.show_panel("main_menu")
```

## **Step 4: Verification Checklist**

### **Functionality Tests**
- [ ] Main menu appears correctly
- [ ] All buttons are visible and clickable
- [ ] Money display shows correct amount
- [ ] Navigation buttons work (Roster, Shop, etc.)
- [ ] Settings toggle works
- [ ] Quit confirmation dialog appears
- [ ] Window close button shows confirmation

### **Visual Tests**
- [ ] Layout matches original design
- [ ] Colors and styling are consistent
- [ ] Text is readable
- [ ] No visual artifacts or glitches

### **Integration Tests**
- [ ] No import errors
- [ ] No runtime exceptions
- [ ] Event system works correctly
- [ ] Game state transitions work
- [ ] Performance is acceptable

## **Step 5: Rollback Plan**

If issues occur, rollback steps:

### **Immediate Rollback**
```python
# Revert import:
from ui.panels.main_menu_panel import MainMenuPanel
```

### **Cleanup**
```bash
# Remove new files (if needed):
rm src/ui/panels/main_menu_panel_refactored.py
rm src/ui/test_main_menu_refactored.py
```

## **Step 6: Performance Monitoring**

### **Metrics to Watch**
- Frame rate during menu display
- Memory usage
- Event handling performance
- Component creation time

### **Performance Test Script**
```python
import time
import pygame
from ui.panels.main_menu_panel_refactored import MainMenuPanelRefactored

def performance_test():
    pygame.init()
    manager = pygame_gui.UIManager((1024, 768))
    game_state = TurboShellsGameStateInterface()
    
    # Measure creation time
    start_time = time.time()
    panel = MainMenuPanelRefactored(game_state)
    panel.manager = manager
    panel._create_window()
    creation_time = time.time() - start_time
    
    print(f"Panel creation time: {creation_time:.4f} seconds")
    
    # Measure update time
    start_time = time.time()
    for _ in range(1000):
        panel.update(0.016)  # 60 FPS
    update_time = time.time() - start_time
    
    print(f"1000 updates time: {update_time:.4f} seconds")
    print(f"Average update time: {update_time/1000:.6f} seconds")

if __name__ == "__main__":
    performance_test()
```

## **Step 7: Troubleshooting**

### **Common Issues and Solutions**

#### **Issue: Import Error**
```
ImportError: cannot import name 'MainMenuPanelRefactored'
```

**Solution:** Check file path and Python path
```python
import sys
sys.path.append('src')
from ui.panels.main_menu_panel_refactored import MainMenuPanelRefactored
```

#### **Issue: Component Not Found**
```
AttributeError: 'MainMenuPanelRefactored' object has no attribute 'main_panel'
```

**Solution:** Ensure `_create_window()` is called
```python
panel = MainMenuPanelRefactored(game_state)
panel.manager = manager
panel._create_window()  # This creates all components
```

#### **Issue: Buttons Not Working**
```
Button clicks not responding
```

**Solution:** Ensure event handling is set up
```python
# In your main loop:
for event in pygame.event.get():
    panel.handle_event(event)
    manager.process_events(event)
```

#### **Issue: Money Display Not Updating**
```
Money amount stays at initial value
```

**Solution:** Ensure update is called
```python
# In your main loop:
panel.update(dt)
```

## **Step 8: Success Criteria**

### **Migration Success Indicators**
- ✅ All functionality preserved
- ✅ No performance regression
- ✅ Code is cleaner and more maintainable
- ✅ Component architecture proven
- ✅ No runtime errors
- ✅ Positive user feedback

### **Code Quality Improvements**
- ✅ Reduced complexity (cyclomatic complexity)
- ✅ Better separation of concerns
- ✅ Improved testability
- ✅ Enhanced reusability
- ✅ Cleaner interfaces

## **Step 9: Next Steps**

### **After Successful Migration**
1. **Remove old implementation** - Clean up legacy code
2. **Document lessons learned** - Update documentation
3. **Plan next migration** - Apply lessons to other panels
4. **Extend component library** - Add missing components
5. **Create migration template** - Standardize process

### **Continuous Improvement**
1. **Monitor performance** - Track metrics over time
2. **Gather feedback** - User and developer feedback
3. **Refine components** - Improve based on usage
4. **Expand testing** - Add automated tests
5. **Share knowledge** - Team training and documentation

## **Step 10: Support**

### **Getting Help**
- Review this guide first
- Check test scripts for examples
- Examine component documentation
- Run integration tests
- Contact development team

### **Resources**
- `src/ui/ADAPTATION_PLAN.md` - Overall migration strategy
- `src/ui/REUSABLE_COMPONENTS_ANALYSIS.md` - Component analysis
- `src/ui/test_main_menu_refactored.py` - Comprehensive tests
- Component source files in `src/ui/components/reusable/`

---

**Remember:** This migration is the first step in a larger architectural improvement. Success here paves the way for migrating other panels and achieving a truly component-based UI architecture.
