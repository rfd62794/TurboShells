# Diagnostic Tools

This directory contains diagnostic and verification tools for TurboShells development and debugging.

## 📁 Directory Structure

```text
tools/diagnostics/
├── README.md                    # This file
├── diagnose_race_system.py     # Race system testing
├── diagnose_rendering.py       # Rendering pipeline testing
├── diagnose_state_constants.py # State constants validation
├── verify_ui_panels.py         # UI panel verification
├── test_pygame_gui_integration.py # pygame_gui integration testing
└── ui_verification/             # UI verification screenshots
    ├── screenshot_MENU.png
    ├── screenshot_RACE.png
    ├── screenshot_RACE_RESULT.png
    ├── screenshot_ROSTER.png
    └── screenshot_SHOP.png
```

## 🚀 Usage

### Race System Diagnostics

```bash
cd tools/diagnostics
python diagnose_race_system.py
```

### Rendering Diagnostics

```bash
cd tools/diagnostics
python diagnose_rendering.py
```

### State Constants Validation

```bash
cd tools/diagnostics
python diagnose_state_constants.py
```

### UI Panel Verification

```bash
cd tools/diagnostics
python verify_ui_panels.py
```

### pygame_gui Integration Testing

```bash
cd tools/diagnostics
python test_pygame_gui_integration.py
```

## 📋 Purpose

These tools are designed to help developers:

- **Diagnose issues** with specific game systems
- **Verify functionality** of UI components
- **Test integrations** between different parts of the system
- **Generate screenshots** for visual verification
- **Debug problems** in isolation from the main game

## 🔧 Maintenance

- Keep tools focused on specific diagnostic tasks
- Update tools when corresponding game systems change
- Add new diagnostic tools as needed for new features
- Remove outdated tools when they're no longer useful

## 📝 Notes

- These are development tools, not part of the test suite
- They can be run independently of the main game
- Some tools may require specific dependencies (pygame, etc.)
- Screenshot verification requires a display environment
