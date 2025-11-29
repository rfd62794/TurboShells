# TurboShells Documentation

**Version:** 3.0 (pygame_gui Transition Focus)  
**Date:** November 28, 2025  
**Status:** Phase 5 – Legacy Views honored, pygame_gui rollout in progress

---

## 📚 **Documentation Overview**

This documentation provides comprehensive coverage of the TurboShells project, from game design to technical implementation. The documentation is organized into focused folders for easy navigation and maintenance.

---

## 🎯 **Quick Navigation**

### 1. 📋 Project & Phase Tracking
- **[TODO.md](TODO.md)** – Live roadmap & Phase 5 objectives.
- **[CHANGELOG.md](CHANGELOG.md)** – Primary release + documentation log.
- **[phases/](phases/)** – Detailed phase briefs (refactor plans, migration notes).

### 2. 🎮 Legacy View Intent (UX Source of Truth)
- **[UI_LAYOUT.md](UI_LAYOUT.md)** – Canonical coordinates for each historic view.
- **[gdd/GDD_UI.md](gdd/GDD_UI.md)** – Narrative UX goals per screen.
- **[docs/ui/](ui/)** – Archived view renderers/specs; treat as blueprints for pygame_gui parity.

### 3. 🧩 PyGame GUI Implementation
- **[technical/SDD.md](technical/SDD.md)** – Current architecture (window manager, panels, managers).
- **[technical/ARCHITECTURE.md](technical/ARCHITECTURE.md)** – Module relationships.
- **[technical/README.md](technical/README.md)** – Entry point to component system references.

### 4. 🧠 Design & Systems References
- **[gdd/](gdd/)** – Full game design canon (overview, gameplay, economy, voting, vision).
- **[GDD.md](GDD.md)** – Quick gateway into the design set.
- **[technical/SVG_*.md](technical/)** – Rendering + asset notes.

### 5. 🛠️ Operational Guides
- **[KEYBOARD.md](KEYBOARD.md)** – Hotkeys.
- **[STYLE_GUIDE.md](STYLE_GUIDE.md)** / **[CODING_STANDARDS.md](CODING_STANDARDS.md)** – Code style policies.
- **[DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md)** – Commit/test conventions.
- **[ERRORS.md](ERRORS.md)** – Troubleshooting log.

---

## 🚀 **Project Status: Version 3.0 (Phase 5) In Progress**

### 🎯 Current Objectives
- **pygame_gui Migration:** Roster, Shop, Breeding, Race HUD mapped to panels using `UIManager` + `WindowManager`.
- **Terrain Upgrade:** Race track visuals receive segment-aware rendering without breaking original lane layout.
- **Pond/Glade Foundations:** Overworld exploration hooks prepared.
- **Data Preservation:** Phase 4 work complete; continue validating migrations as new UI surfaces emerge.

### ✅ Recent Milestones
- SRP-aligned module decomposition (+15 focused modules).
- 19-trait genetics + breeding lineage tracking shipped.
- Direct rendering pipeline and voting loops stabilized.
- Monitoring + profiling overlays active in main loop.

---

## 📊 **Documentation Statistics**

### **Legacy View Specs**
- `docs/UI_LAYOUT.md` + `docs/gdd/GDD_UI.md`
- Additional layout callouts inside `docs/ui/views/*`

### **pygame_gui Migration References**
- `src/core/ui/window_manager.py` – size + rect calculations
- `src/ui/ui_manager.py`, `src/ui/panels/*` – new panel implementations
- `docs/phases/Phase_26_*` – Refactor playbook for component system

---

## 🎯 **Documentation Usage**

### **For New Engineers**
1. Read `WINDSURF.md` (persona + workflow).
2. Review legacy layouts: `docs/UI_LAYOUT.md`, `docs/gdd/GDD_UI.md`.
3. Inspect current pygame_gui panels: `src/ui/panels/`, `docs/phases/Phase_26_*`.
4. Align with roadmap: `docs/TODO.md`.

### **For Systems / UI Designers**
1. Canonical UX: `docs/gdd/GDD_UI.md` + `docs/UI_LAYOUT.md`.
2. Visual intent: `docs/ui/views/*` (historic render narratives).
3. Migration notes: `docs/phases/Phase_26_UI_Architecture_Refactoring.md`.

### **For Architects & Tooling**
1. Architecture: `docs/technical/ARCHITECTURE.md`.
2. SDD + component descriptions: `docs/technical/SDD.md`.
3. Monitoring & overlays: `docs/technical/README.md`, `src/core/monitoring_*`.

---

## 🔄 **Documentation Maintenance**

### **Organization Principles**
- **Logical Grouping**: Related documents in dedicated folders
- **Clear Navigation**: README files provide comprehensive indexes
- **Version Control**: All documents include version and date information
- **Cross-References**: Documents reference related materials

### **Update Guidelines**
- **Version Alignment**: Keep document versions consistent with code releases
- **Status Updates**: Regularly update completion status and progress
- **Link Validation**: Ensure all internal links remain valid
- **Content Accuracy**: Verify technical details match current implementation

---

## 📋 **Document Relationships**

```
docs/
├── README.md              # Main documentation index (this file)
├── TODO.md                 # Development roadmap
├── CHANGELOG.md            # Version history
├── GDD.md                  # GDD main index
├── gdd/                    # Game Design Documentation
│   ├── README.md           # GDD folder index
│   ├── GDD.md              # Main GDD (relocated)
│   ├── GDD_Overview.md     # Executive summary
│   ├── GDD_Gameplay.md     # Gameplay mechanics
│   ├── GDD_UI.md           # UI specifications
│   ├── GDD_Technical.md    # Technical overview
│   ├── GDD_Vision.md       # Future roadmap
│   ├── Design_Voting_System.md        # Voting system spec
│   └── Design_Voting_Implementation.md # Voting implementation
├── technical/              # Technical Documentation
│   ├── README.md           # Technical docs index
│   ├── SDD.md              # Software Design Document
│   ├── ARCHITECTURE.md     # Technical architecture
│   ├── SVG_Technical_Specification.md # SVG specs
│   └── SVG_Analysis.md     # SVG library analysis
└── [reference docs...]     # UI_LAYOUT.md, KEYBOARD.md, ERRORS.md
```

---

## 🎯 **Quick Reference**

### **Current Development Status**
- Architecture baseline solid; UI layer mid-migration.
- Genetics/economy/breeding stacks stable.
- pygame_gui panel set expanding; component system rollout ongoing.

### **Current Priorities (Phase 5)**
1. **Legacy View Parity:** Each pygame_gui panel must match coordinates/behavior from `UI_LAYOUT.md` (except upgraded race terrain visuals).
2. **Race Terrain Upgrade:** Implement colored segments + overlays while keeping HUD geometry intact.
3. **Pond/Glade Prep:** Document layout + data needs for overworld screen.
4. **Documentation Hygiene:** Keep `docs/` synchronized with UI changes to avoid legacy drift.

---

*This documentation provides comprehensive coverage of the TurboShells project, from high-level game design to detailed technical implementation. The modular organization ensures easy navigation and maintenance for all team members.*
