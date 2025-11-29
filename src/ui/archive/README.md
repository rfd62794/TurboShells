# UI Archive - Original Implementations

This directory contains archived original UI implementations that have been replaced with refactored versions.

## Purpose

- **Reference**: Preserve original implementations for comparison and reference
- **Rollback**: Enable quick rollback if issues arise with refactored versions
- **Documentation**: Show the evolution of the UI architecture
- **Testing**: Use as baseline for testing refactored implementations

## Structure

```
archive/
├── panels/          # Archived panel implementations
│   ├── main_menu_panel.py
│   ├── roster_panel.py
│   ├── profile_panel.py
│   └── settings_panel.py
├── views/           # Archived view implementations
│   ├── settings_view.py
│   ├── voting_view.py
│   └── migration_adapter.py
└── components/      # Archived component implementations
    ├── settings_view_refactored.py
    └── legacy_components.py
```

## Archive Policy

1. **Original files are moved here** when replaced by refactored versions
2. **Files are prefixed with date** of archiving: `YYYYMMDD_`
3. **Class names remain unchanged** to maintain reference clarity
4. **Dependencies are preserved** - no modifications to archived code
5. **Documentation added** explaining why the file was archived

## Migration Log

See `MIGRATION_LOG.md` for detailed history of what was replaced and when.

## Usage

- **Reference**: Look here to understand original implementation patterns
- **Comparison**: Compare with new implementations to verify functionality
- **Rollback**: Copy files back to original locations if needed
- **Learning**: Study the evolution of the codebase architecture

## Notes

- Archived files are **read-only** reference copies
- Do not modify archived files - create new versions instead
- When copying back for rollback, ensure dependencies are still compatible
- Consider the impact on the current codebase before rolling back
