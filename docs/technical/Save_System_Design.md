# Save System Design Document

**Version:** 1.0  
**Date:** November 22, 2025  
**Status:** Design Phase  

## 1. Overview

This document outlines the technical design for TurboShells' save system, enabling persistent game state between sessions. The save system will handle automatic saving, loading, and data integrity validation.

### 1.1 Goals
- **Persistence**: Save and restore complete game state
- **Automation**: Automatic saves on critical events
- **Reliability**: Robust error handling and data validation
- **Performance**: Fast save/load operations
- **User Experience**: Seamless save/load with minimal disruption

### 1.2 Scope
- Game state persistence (money, phase, unlocked features)
- Roster data (all turtles with genetics and stats)
- Race history and statistics
- Voting history and reward tracking
- System state (voting pool, genetic influence, timestamps)

---

## 2. Architecture

### 2.1 Core Components

#### 2.1.1 SaveManager Class
```python
class SaveManager:
    def __init__(self, save_directory: str)
    def save_game(self, game_state: GameState) -> bool
    def load_game(self) -> Optional[GameState]
    def auto_save(self, game_state: GameState) -> bool
    def validate_save_file(self, file_path: str) -> bool
    def create_backup(self, file_path: str) -> bool
    def cleanup_old_saves(self) -> None
```

#### 2.1.2 SaveData Structure
```python
@dataclass
class SaveData:
    version: str
    timestamp: datetime
    game_state: GameStateData
    roster_data: List[TurtleData]
    race_history: List[RaceData]
    voting_history: List[VotingData]
    system_state: SystemStateData
```

### 2.2 File Structure
```
saves/
├── turbo_shells_save.json      # Primary save file
├── turbo_shells_backup.json    # Automatic backup
└── turbo_shells_old.json       # Previous save (auto-cleanup)
```

---

## 3. Data Models

### 3.1 GameStateData
```python
@dataclass
class GameStateData:
    money: int
    current_phase: str
    unlocked_features: List[str]
    current_design_index: int
    daily_voting_status: Dict[str, Any]
    tutorial_progress: Dict[str, bool]
    statistics: Dict[str, Any]
```

### 3.2 TurtleData
```python
@dataclass
class TurtleData:
    id: str
    name: str
    genetics: Dict[str, Any]
    stats: Dict[str, float]
    race_history: List[RaceResultData]
    breeding_info: Optional[BreedingData]
    is_active: bool
    retirement_date: Optional[datetime]
```

### 3.3 RaceData
```python
@dataclass
class RaceData:
    race_id: str
    timestamp: datetime
    participants: List[str]  # Turtle IDs
    results: Dict[str, int]  # Turtle ID -> position
    terrain_data: List[str]
    earnings: Dict[str, int]
```

### 3.4 VotingData
```python
@dataclass
class VotingData:
    date: str
    design_id: str
    ratings: Dict[str, int]  # Category -> rating
    rewards_earned: int
    genetic_influence: Dict[str, float]
```

### 3.5 SystemStateData
```python
@dataclass
class SystemStateData:
    voting_pool: List[DesignData]
    genetic_pool_influence: Dict[str, float]
    last_daily_reset: datetime
    version_specific_data: Dict[str, Any]
```

---

## 4. Save/Load Logic

### 4.1 Auto-Save Triggers
- **Voting Completion**: After each category vote is submitted
- **Race Completion**: After race results are calculated
- **Breeding Completion**: After new turtle is created
- **Shop Purchase**: After turtle is bought
- **Game Exit**: Before application closes
- **Periodic**: Every 5 minutes of gameplay

### 4.2 Save Process
1. **Data Collection**: Gather current game state from all managers
2. **Data Validation**: Verify data integrity and completeness
3. **Backup Creation**: Create backup of existing save file
4. **Serialization**: Convert to JSON format
5. **File Write**: Atomically write to save file
6. **Verification**: Confirm file was written successfully
7. **Cleanup**: Remove old backup files

### 4.3 Load Process
1. **File Detection**: Check for save file existence
2. **Validation**: Verify file integrity and version compatibility
3. **Deserialization**: Parse JSON into data structures
4. **Data Validation**: Check data completeness and consistency
5. **State Restoration**: Apply data to game managers
6. **Fallback**: Handle corrupted or missing files

---

## 5. Error Handling

### 5.1 Save Failures
- **Disk Full**: Show user notification, retry with cleanup
- **Permission Denied**: Check write permissions, suggest alternative location
- **Data Corruption**: Use backup file, notify user
- **Network Issues** (cloud saves): Queue for later retry

### 5.2 Load Failures
- **File Not Found**: Start new game, notify user
- **Corrupted Data**: Use backup file or start new game
- **Version Mismatch**: Attempt migration or notify user
- **Invalid Data**: Start new game, log error details

---

## 6. Performance Considerations

### 6.1 Optimization Strategies
- **Incremental Saves**: Save only changed data
- **Compression**: Use gzip for large save files
- **Background Operations**: Perform saves in separate thread
- **Caching**: Cache frequently accessed save data
- **Lazy Loading**: Load data only when needed

### 6.2 Performance Targets
- **Save Time**: < 100ms for typical save
- **Load Time**: < 200ms for typical load
- **File Size**: < 1MB for typical save file
- **Memory Usage**: < 10MB for save operations

---

## 7. Security & Privacy

### 7.1 Data Protection
- **Local Storage**: Saves stored in user directory only
- **No Personal Data**: No personal information collected
- **File Permissions**: Restrict access to save files
- **Basic Encryption**: Simple XOR encryption for save files

### 7.2 Privacy Considerations
- **User Consent**: Clear notification of save system usage
- **Data Minimization**: Only save necessary game data
- **Local Only**: No cloud storage or data transmission
- **User Control**: Ability to delete save files

---

## 8. Version Compatibility

### 8.1 Version Management
- **Version Field**: Include version number in save files
- **Migration System**: Automatic data migration between versions
- **Backward Compatibility**: Support loading older save formats
- **Forward Compatibility**: Graceful handling of newer save formats

### 8.2 Migration Strategy
```python
class SaveMigrator:
    def migrate_v1_to_v2(self, save_data: SaveData) -> SaveData
    def migrate_v2_to_v3(self, save_data: SaveData) -> SaveData
    def get_migration_path(self, from_version: str, to_version: str) -> List[Callable]
```

---

## 9. Testing Strategy

### 9.1 Unit Tests
- **SaveManager**: Test all save/load operations
- **Data Validation**: Test data integrity checks
- **Error Handling**: Test failure scenarios
- **Migration**: Test version compatibility

### 9.2 Integration Tests
- **Game Integration**: Test save/load with actual game state
- **Performance**: Test save/load with large datasets
- **Concurrent Access**: Test multiple save operations
- **File System**: Test with various file system conditions

### 9.3 Edge Cases
- **Corrupted Files**: Test handling of damaged save files
- **Full Disk**: Test behavior when disk space is limited
- **Permission Issues**: Test with restricted file permissions
- **Power Loss**: Test data integrity during interruption

---

## 10. Implementation Plan

### 10.1 Phase 1: Core Save/Load (Week 1)
- [ ] Implement SaveManager class
- [ ] Define data structures
- [ ] Basic save/load functionality
- [ ] File management utilities

### 10.2 Phase 2: Integration (Week 2)
- [ ] Integrate with game managers
- [ ] Implement auto-save triggers
- [ ] Add error handling
- [ ] Basic validation

### 10.3 Phase 3: Polish & Optimization (Week 3)
- [ ] Performance optimization
- [ ] Advanced error handling
- [ ] User notifications
- [ ] Backup system

### 10.4 Phase 4: Testing & Validation (Week 4)
- [ ] Comprehensive testing
- [ ] Edge case handling
- [ ] Documentation
- [ ] Final integration

---

## 11. Dependencies

### 11.1 External Libraries
- **json**: Built-in JSON serialization
- **pathlib**: Modern file path handling
- **datetime**: Timestamp management
- **gzip**: Optional file compression
- **threading**: Background save operations

### 11.2 Internal Dependencies
- **core/game_state.py**: Game state management
- **managers/**: All manager classes
- **core/entities.py**: Turtle data structures
- **ui/voting_view.py**: Voting system data

---

## 12. Future Enhancements

### 12.1 Advanced Features
- **Multiple Save Slots**: Support for multiple save files
- **Cloud Sync**: Optional cloud storage integration
- **Save Analytics**: Statistics about save/load patterns
- **Import/Export**: Save file sharing between players

### 12.2 Performance Improvements
- **Binary Format**: Custom binary save format for better performance
- **Delta Saves**: Save only changes from previous save
- **Compression**: Advanced compression algorithms
- **Database Storage**: SQLite for complex save data

---

## 13. Conclusion

The save system design provides a robust foundation for game state persistence in TurboShells. The modular architecture ensures maintainability while the comprehensive error handling guarantees reliability. The phased implementation approach allows for incremental development and testing.

**Next Steps:**
1. Review and approve design
2. Begin Phase 1 implementation
3. Set up testing infrastructure
4. Integrate with existing game systems

---

*This document will be updated as the implementation progresses and requirements evolve.*
