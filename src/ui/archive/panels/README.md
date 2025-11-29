# Archived Panels

This directory contains archived panel implementations that have been replaced with refactored versions.

## Archived Files

### Main Menu Panel
- **File**: `20251128_main_menu_panel.py`
- **Original Location**: `src/ui/panels/main_menu_panel.py`
- **Replaced By**: `src/ui/panels/main_menu_panel_refactored.py`
- **Reason**: Component-based architecture implementation
- **Size**: 7,807 bytes
- **Lines**: ~200+ lines
- **Key Features**: Original monolithic main menu implementation

### Roster Panel
- **File**: `20251128_roster_panel.py`
- **Original Location**: `src/ui/panels/roster_panel.py`
- **Replaced By**: `src/ui/panels/roster_panel_refactored.py`
- **Reason**: SRP component separation
- **Size**: 22,115 bytes
- **Lines**: ~520 lines
- **Key Features**: Turtle roster management with betting controls

### Profile Panel
- **File**: `20251128_profile_panel.py`
- **Original Location**: `src/ui/panels/profile/profile_panel.py`
- **Replaced By**: `src/ui/panels/profile/profile_panel_refactored.py`
- **Reason**: Specialized component architecture
- **Size**: 9,607 bytes
- **Lines**: ~300+ lines
- **Key Features**: Turtle profile display and management

## Usage Notes

1. **Reference Only**: These files are preserved for reference purposes
2. **No Modifications**: Do not modify archived files
3. **Rollback**: Can be copied back to original locations if needed
4. **Dependencies**: Original dependencies are preserved

## Architecture Evolution

### Before Archiving
- Monolithic panel classes
- Mixed responsibilities (UI + business logic)
- Tight coupling with game state
- Limited reusability

### After Refactoring
- Component-based architecture
- Clear separation of concerns
- Event-driven communication
- Reusable components

## Migration Impact

### Benefits
- **Maintainability**: Easier to maintain and modify
- **Testability**: Components can be tested independently
- **Reusability**: Components can be used in multiple contexts
- **Extensibility**: New features easier to implement

### Considerations
- **Learning Curve**: Team needs to learn new architecture
- **File Structure**: More files to manage
- **Dependencies**: More complex dependency graph
- **Performance**: Slight overhead from component system
