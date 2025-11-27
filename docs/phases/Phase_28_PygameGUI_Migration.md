# Phase 28: Pygame GUI Architecture Migration

## **Phase Overview**

Transform TurboShells from a pure PyGame monolithic architecture to a hybrid PyGame + `pygame_gui` system. This migration provides a robust, native Python UI solution that integrates seamlessly with Pygame's event loop, replacing the previous attempts with `pyimgui` and `thorpy`.

## **Current State Analysis**

### Recent Changes
- **Library Switch**: Moved from `pyimgui`/`thorpy` to `pygame_gui` due to compatibility and installation issues.
- **Foundation Implemented**:
    - `UIManager`: Wraps `pygame_gui.UIManager` and handles event delegation.
    - `BasePanel`: Abstract base class using `pygame_gui.elements.UIWindow`.
    - `SettingsPanel`: Fully implemented using `pygame_gui` widgets (sliders, buttons) with data binding.
    - `main.py`: Integrated `UIManager` and `SettingsPanel`, replacing legacy `SettingsManager`.
    - `test_pygame_gui_integration.py`: Verified successful integration.

### Remaining Work
- **Legacy UI Replacement**: The main menu, shop, roster, and other views are still using the old `Renderer` class with direct Pygame drawing.
- **Panel Migration**: Need to convert these legacy views into `pygame_gui` panels.

## **Target Architecture**

### UI Pipeline
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   pygame_gui    │───▶│   Data Binding   │───▶│  PyGame Engine  │
│   (UI Layer)    │    │   (Interface)    │    │   (World)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Key Components
1.  **UIManager**: Central coordinator, manages `pygame_gui.UIManager` instance.
2.  **BasePanel**: Wraps `UIWindow`, provides common interface for visibility and data binding.
3.  **DataBindingManager**: Connects UI widgets to Game State properties bi-directionally.
4.  **GameStateInterface**: Controlled access point for UI to read/write game data.

## **Implementation Phases**

### Phase 1: Foundation (Completed)
- [x] Install `pygame_gui`.
- [x] Implement `UIManager`.
- [x] Implement `BasePanel`.
- [x] Implement `SettingsPanel` as proof of concept.
- [x] Integrate into `main.py` loop.

### Phase 2: Core Views Migration (Next Steps)
- [ ] **Main Menu**: Convert `draw_main_menu` to `MainMenuPanel`.
- [ ] **Shop**: Convert `draw_shop` to `ShopPanel` using `UIScrollingContainer` for inventory.
- [ ] **Roster**: Convert `draw_menu` (roster view) to `RosterPanel`.
- [ ] **Race Interface**: Overlay race UI (speed, progress) using `pygame_gui` or keep lightweight custom drawing if performance demands it.

### Phase 3: Advanced Features
- [ ] **Breeding**: Convert `draw_breeding` to `BreedingPanel`.
- [ ] **Profile**: Convert `draw_profile` to `ProfilePanel`.
- [ ] **Voting**: Convert `draw_voting` to `VotingPanel`.
- [ ] **Styling**: Create a custom `theme.json` for `pygame_gui` to match TurboShells aesthetic.

## **File Structure**

```
src/
├── ui/
│   ├── ui_manager.py             # Manages pygame_gui.UIManager
│   ├── data_binding.py           # Data binding system
│   ├── panels/
│   │   ├── base_panel.py         # Base class wrapping UIWindow
│   │   ├── settings_panel.py     # Settings (Implemented)
│   │   ├── main_menu_panel.py    # To be implemented
│   │   ├── shop_panel.py         # To be implemented
│   │   └── ...
│   └── themes/
│       └── theme.json            # Custom styling
```

## **Benefits**
- **Stability**: `pygame_gui` is pure Python and highly compatible with Pygame.
- **Maintainability**: Clear separation of UI logic from game rendering.
- **Features**: Built-in support for windows, scrolling, text entry, and rich text.
- **Accessibility**: Better support for keyboard navigation and screen readers (potential).

## **Success Criteria**
- [ ] All legacy `Renderer` UI methods replaced by `pygame_gui` panels.
- [ ] Game playable entirely through new UI.
- [ ] Consistent visual theme applied.
- [ ] No performance regression in main game loop.
