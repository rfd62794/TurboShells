# Game Design Document: Turbo Shells - Technical Implementation

**Version:** 1.1 (Enhanced MVP)  
**Date:** November 22, 2025  
**Focus:** Technical architecture and implementation details

---

## 1. Technical Stack

### 1.1 Core Technologies

- **Language**: Python 3.10+
- **Graphics Library**: pygame-ce 2.5.6
- **Architecture**: Component-based design pattern
- **State Management**: Centralized game state system
- **Event Handling**: PyGame event loop with custom state handlers

### 1.2 Development Environment

- **IDE**: Any Python IDE (VS Code, PyCharm, etc.)
- **Version Control**: Git
- **Package Management**: pip
- **Testing**: Manual testing (unit tests planned)
- **Documentation**: Markdown-based documentation system

---

## 2. Architecture Overview

### 2.1 High-Level Architecture

```
TurboShells/
├── main.py                 # Game entry point and main loop
├── settings.py             # Global constants and configuration
├── core/                   # Domain layer (entities, logic)
│   ├── entities.py         # Turtle class and physics
│   ├── game_state.py       # Generation and breeding helpers
│   ├── race_track.py       # Terrain generation
│   └── state_handler.py    # Input handling and state transitions
├── managers/               # Business logic layer
│   ├── roster_manager.py   # Roster management
│   ├── race_manager.py     # Race coordination
│   ├── shop_manager.py     # Shop operations
│   └── breeding_manager.py # Breeding logic
├── ui/                     # Presentation layer
│   ├── layouts/            # UI positioning data
│   │   └── positions.py    # Screen layout constants
│   ├── components/         # Reusable UI elements
│   │   ├── button.py       # Button component
│   │   └── turtle_card.py  # Turtle display component
│   ├── views/              # Screen renderers
│   │   ├── menu_view.py    # Main menu
│   │   ├── roster_view.py  # Roster management
│   │   ├── race_view.py    # Race visualization
│   │   ├── shop_view.py    # Shop interface
│   │   ├── breeding_view.py # Breeding center
│   │   └── profile_view.py # Turtle profiles
│   └── renderer.py         # Central rendering coordinator
└── docs/                   # Documentation
    ├── GDD*.md            # Game design documents
    ├── TODO.md            # Development roadmap
    └── CHANGELOG.md        # Version history
```

### 2.2 Design Patterns

#### **Component-Based Design**
- **Reusable Components**: Button, TurtleCard classes
- **Separation of Concerns**: UI, logic, and data separated
- **Modular Architecture**: Each screen has dedicated view and manager
- **Centralized Layout**: All positioning in one location

#### **Manager Pattern**
- **Specialized Managers**: Each game system has dedicated manager
- **Business Logic**: Complex operations encapsulated in managers
- **State Coordination**: Managers handle specific domain logic
- **Interface Segregation**: Clear manager responsibilities

#### **State Machine Pattern**
- **Game States**: String-based state identifiers
- **State Transitions**: Centralized state management
- **Input Routing**: Different handlers per state
- **Clean Transitions**: Predictable state changes

---

## 3. Core Systems

### 3.1 Entity System

**File**: `core/entities.py`

#### **Turtle Class**
```python
class Turtle:
    def __init__(self, name, speed, energy, recovery, swim, climb):
        # Identity
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.age = 0
        self.is_active = True
        
        # Stats
        self.stats = {
            "speed": speed,
            "max_energy": energy,
            "recovery": recovery,
            "swim": swim,
            "climb": climb
        }
        
        # Race State
        self.current_energy = energy
        self.race_distance = 0
        self.is_resting = False
        self.finished = False
        self.rank = None
        
        # Race History
        self.race_history = []
        self.total_races = 0
        self.total_earnings = 0
        
        # Visual Genetics (future)
        self.visual_genetics = {...}
        self.parent_ids = []
        self.generation = 0
```

#### **Physics System**
```python
def update_physics(self, terrain_type):
    if self.is_resting:
        # Energy recovery
        self.current_energy += self.stats["recovery"] * RECOVERY_RATE
        if self.current_energy >= RECOVERY_THRESHOLD * self.stats["max_energy"]:
            self.is_resting = False
        return 0
    
    # Calculate movement speed
    speed = self.stats["speed"]
    if terrain_type == "water":
        speed *= self.stats["swim"] / 10.0
    elif terrain_type == "rock":
        speed *= self.stats["climb"] / 10.0
    
    # Energy drain
    self.current_energy -= 0.5 * TERRAIN_DIFFICULTY
    if self.current_energy <= 0:
        self.current_energy = 0
        self.is_resting = True
    
    return speed
```

### 3.2 State Management

**File**: `core/state_handler.py`

#### **State Machine**
```python
class StateHandler:
    def __init__(self, game):
        self.game = game
        self.state_transitions = {
            STATE_MENU: self._handle_menu_clicks,
            STATE_ROSTER: self._handle_roster_clicks,
            STATE_SHOP: self._handle_shop_clicks,
            STATE_BREEDING: self._handle_breeding_clicks,
            STATE_RACE: self._handle_race_clicks,
            STATE_RACE_RESULT: self._handle_race_result_clicks,
            STATE_PROFILE: self._handle_profile_clicks,
        }
    
    def handle_click(self, pos):
        handler = self.state_transitions.get(self.game.state)
        if handler:
            handler(pos)
```

#### **Input Handling**
- **Mouse Events**: Primary input method
- **State-Specific Handlers**: Different logic per game state
- **Click Validation**: Ensure clicks are valid for current state
- **State Transitions**: Centralized state change management

### 3.3 Game State

**File**: `main.py`

#### **TurboShellsGame Class**
```python
class TurboShellsGame:
    def __init__(self):
        # Game state
        self.state = STATE_MENU
        self.money = 100
        self.roster = [None, None, None]
        self.retired_roster = []
        self.shop_inventory = []
        
        # Managers
        self.roster_manager = RosterManager(self)
        self.race_manager = RaceManager(self)
        self.shop_manager = ShopManager(self)
        self.breeding_manager = BreedingManager(self)
        
        # UI
        self.renderer = Renderer()
        self.state_handler = StateHandler(self)
        self.mouse_pos = None
        
        # Profile system
        self.profile_turtle_index = 0
```

---

## 4. Manager System

### 4.1 Roster Manager

**File**: `managers/roster_manager.py`

#### **Responsibilities**
- **Roster Management**: Add, remove, organize turtles
- **Training System**: Improve turtle stats
- **Retirement System**: Move turtles to retired roster
- **Profile Access**: Handle profile view transitions

#### **Key Methods**
```python
def handle_click(self, pos):
    # View toggle buttons
    if layout.VIEW_ACTIVE_RECT.collidepoint(pos):
        self.game_state.show_retired_view = False
    elif layout.VIEW_RETIRED_RECT.collidepoint(pos):
        self.game_state.show_retired_view = True
    
    # Check roster slots
    for i, slot_rect in enumerate(layout.SLOT_RECTS):
        if slot_rect.collidepoint(pos):
            if self.game_state.roster[i]:
                return "PROFILE"  # Transition to profile view
```

### 4.2 Race Manager

**File**: `managers/race_manager.py`

#### **Responsibilities**
- **Race Setup**: Initialize race participants
- **Race Logic**: Update turtle positions and physics
- **Race Completion**: Determine winners and distribute rewards
- **Race History**: Record race results

#### **Race Physics**
```python
def update_race(self):
    active_turtles = [t for t in self.game_state.roster if t]
    
    for turtle in active_turtles:
        # Get current terrain
        terrain = self.track.get_terrain_at(turtle.race_distance)
        
        # Update physics
        speed = turtle.update_physics(terrain)
        turtle.race_distance += speed
        
        # Check finish
        if turtle.race_distance >= TRACK_LENGTH_LOGIC and not turtle.finished:
            turtle.finished = True
            turtle.rank = len(self.results) + 1
            self.results.append(turtle)
```

### 4.3 Shop Manager

**File**: `managers/shop_manager.py`

#### **Responsibilities**
- **Inventory Management**: Generate and maintain shop stock
- **Purchase Processing**: Handle turtle purchases
- **Pricing Logic**: Calculate turtle costs based on stats
- **Stock Refresh**: Regenerate shop inventory

#### **Pricing Algorithm**
```python
def compute_turtle_cost(turtle):
    stats = turtle.stats
    normalized_energy = stats["max_energy"] / 10.0
    total = (
        stats["speed"] + normalized_energy + 
        stats["recovery"] + stats["swim"] + stats["climb"]
    )
    return BASE_COST + COST_SCALE * total
```

### 4.4 Breeding Manager

**File**: `managers/breeding_manager.py`

#### **Responsibilities**
- **Parent Selection**: Handle parent turtle selection
- **Breeding Logic**: Generate offspring from parents
- **Stat Inheritance**: Calculate child stats from parents
- **Lineage Tracking**: Record parent-child relationships

#### **Breeding Algorithm**
```python
def create_offspring(self, parent_a, parent_b):
    child_name = parent_a.name[:len(parent_a.name)//2] + parent_b.name[len(parent_b.name)//2:]
    
    # Inherit stats
    child_stats = {}
    for stat in ["speed", "max_energy", "recovery", "swim", "climb"]:
        base = max(parent_a.stats[stat], parent_b.stats[stat])
        # Mutation chance
        if random.random() < 0.2:
            base += random.randint(1, 2)
        child_stats[stat] = base
    
    return Turtle(child_name, **child_stats)
```

---

## 5. UI System

### 5.1 Rendering System

**File**: `ui/renderer.py`

#### **Centralized Rendering**
```python
class Renderer:
    def draw(self, screen, font, game_state):
        if game_state.state == STATE_MENU:
            self.draw_menu(screen, font, game_state)
        elif game_state.state == STATE_ROSTER:
            self.draw_roster(screen, font, game_state)
        elif game_state.state == STATE_SHOP:
            self.draw_shop(screen, font, game_state)
        elif game_state.state == STATE_BREEDING:
            self.draw_breeding(screen, font, game_state)
        elif game_state.state == STATE_RACE:
            self.draw_race(screen, font, game_state)
        elif game_state.state == STATE_RACE_RESULT:
            self.draw_race_result(screen, font, game_state)
        elif game_state.state == STATE_PROFILE:
            self.draw_profile(screen, font, game_state)
```

### 5.2 Component System

#### **Button Component**
**File**: `ui/components/button.py`

```python
class Button:
    def __init__(self, rect, text, color=GRAY, hover_color=WHITE):
        self.rect = rect
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = pygame.font.SysFont("Arial", 18)
    
    def draw(self, screen, mouse_pos=None):
        color = self.hover_color if mouse_pos and self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, color, self.rect, 2)
        
        text_surface = self.font.render(self.text, True, WHITE)
        text_x = self.rect.x + (self.rect.width - text_surface.get_width()) // 2
        text_y = self.rect.y + (self.rect.height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
```

#### **TurtleCard Component**
**File**: `ui/components/turtle_card.py`

```python
class TurtleCard:
    def __init__(self, rect, turtle, show_train_button=True):
        self.rect = rect
        self.turtle = turtle
        self.show_train_button = show_train_button
    
    def draw(self, screen, font, mouse_pos, is_selected=False):
        # Draw card background
        border_color = GREEN if is_selected else GRAY
        if mouse_pos and self.rect.collidepoint(mouse_pos):
            border_color = WHITE
        pygame.draw.rect(screen, border_color, self.rect, 2)
        
        # Draw turtle information
        if self.turtle:
            # Name, stats, energy bar, etc.
            # ... rendering logic
```

### 5.3 Layout System

**File**: `ui/layouts/positions.py`

#### **Centralized Positioning**
```python
# Main Menu Layout
MENU_ROSTER_RECT = pygame.Rect(200, 150, 400, 80)
MENU_SHOP_RECT = pygame.Rect(200, 250, 400, 80)
MENU_BREEDING_RECT = pygame.Rect(200, 350, 400, 80)
MENU_RACE_RECT = pygame.Rect(200, 450, 400, 80)

# Roster Layout
SLOT_RECTS = [
    pygame.Rect(50, 100, 200, 300),  # Slot 1
    pygame.Rect(300, 100, 200, 300), # Slot 2
    pygame.Rect(550, 100, 200, 300), # Slot 3
]

# Profile Layout (Image-Ready)
PROFILE_VISUAL_PANEL_RECT = pygame.Rect(50, 80, 300, 400)
PROFILE_INFO_PANEL_RECT = pygame.Rect(370, 80, 380, 400)
PROFILE_TURTLE_IMAGE_POS = (200, 230)
```

---

## 6. Data Management

### 6.1 Game State Persistence

#### **Current State**
- **No Persistence**: Game resets on close (MVP design)
- **In-Memory**: All data stored in Python objects
- **Session-Based**: Single play session focus

#### **Future Persistence Plan**
- **JSON Format**: Human-readable save files
- **Auto-Save**: Periodic state saving
- **Multiple Slots**: Multiple save game support
- **Validation**: Save file integrity checking

### 6.2 Data Flow

#### **Entity Lifecycle**
1. **Generation**: Created in shop or breeding
2. **Active Service**: Used in races and training
3. **Retirement**: Moved to retired roster
4. **Breeding**: Used as parent, then removed
5. **History**: Race results recorded

#### **State Transitions**
```
Shop → Roster → Race → Results → Roster
         ↓
     Breeding → Roster
         ↓
      Profile → Roster
```

---

## 7. Performance Considerations

### 7.1 Rendering Performance

#### **Optimization Strategies**
- **Static Layouts**: Pre-calculated positions
- **Component Reuse**: Shared rendering logic
- **Efficient Updates**: Only redraw when state changes
- **Memory Management**: Proper object lifecycle

#### **Rendering Pipeline**
1. **Clear Screen**: Background color
2. **Draw UI Elements**: Components and layouts
3. **Draw Game Elements**: Turtles, track, etc.
4. **Update Display**: Present to screen

### 7.2 Memory Management

#### **Object Lifecycle**
- **Turtle Objects**: Managed through roster systems
- **Temporary Objects**: Race opponents cleaned up
- **UI Components**: Reused across screens
- **Event Handling**: Efficient event processing

#### **Memory Optimization**
- **Object Pooling**: Reuse turtle objects
- **Lazy Loading**: Load resources when needed
- **Garbage Collection**: Python automatic management
- **Resource Cleanup**: Proper object disposal

---

## 8. Error Handling

### 8.1 Current Error Handling

#### **Input Validation**
- **Click Boundaries**: Validate click positions
- **State Validation**: Ensure actions valid for current state
- **Resource Checks**: Validate roster space, funds, etc.
- **Graceful Degradation**: Handle errors without crashes

#### **Common Error Cases**
- **Empty Roster**: Handle no available turtles
- **Insufficient Funds**: Prevent purchases when broke
- **Full Roster**: Prevent adding when no space
- **Invalid Selection**: Handle incorrect parent choices

### 8.2 Future Error Handling

#### **Comprehensive Validation**
- **Save File Validation**: Check save file integrity
- **Network Errors**: Handle future multiplayer features
- **Resource Loading**: Handle missing assets
- **Exception Logging**: Comprehensive error tracking

---

## 9. Testing Strategy

### 9.1 Current Testing

#### **Manual Testing**
- **Functional Testing**: All features manually verified
- **User Experience**: Interface usability tested
- **Edge Cases**: Boundary conditions verified
- **Integration Testing**: System interactions tested

#### **Test Coverage**
- **Game States**: All states functional
- **Manager Logic**: Business logic verified
- **UI Components**: Rendering and interaction tested
- **Data Flow**: End-to-end scenarios tested

### 9.2 Future Testing

#### **Automated Testing**
- **Unit Tests**: Individual function testing
- **Integration Tests**: System interaction testing
- **UI Tests**: Component rendering and interaction
- **Performance Tests**: Speed and memory testing

---

## 10. Development Tools

### 10.1 Development Environment

#### **Required Tools**
- **Python 3.10+**: Core language requirement
- **pygame-ce 2.5.6**: Graphics and input library
- **IDE**: Code editor with Python support
- **Git**: Version control system

#### **Recommended Tools**
- **VS Code**: Python development environment
- **PyCharm**: Advanced Python IDE
- **GitHub**: Code hosting and collaboration
- **Markdown**: Documentation format

### 10.2 Build and Deployment

#### **Development Build**
```bash
# Install dependencies
pip install pygame-ce

# Run game
python main.py
```

#### **Distribution准备**
- **Standalone Executable**: PyInstaller for distribution
- **Asset Management**: Resource packaging
- **Version Management**: Semantic versioning
- **Release Process**: Automated builds

---

## 11. Future Technical Enhancements

### 11.1 Architecture Improvements

#### **Advanced Patterns**
- **Event System**: Decoupled event handling
- **Plugin Architecture**: Extensible feature system
- **Service Layer**: Business logic abstraction
- **Data Access Layer**: Database integration

#### **Performance Enhancements**
- **Multithreading**: Parallel processing
- **Caching System**: Resource and data caching
- **Optimized Rendering**: Hardware acceleration
- **Memory Optimization**: Advanced memory management

### 11.2 Technology Upgrades

#### **Graphics Enhancement**
- **OpenGL Integration**: Hardware-accelerated graphics
- **Shader Support**: Advanced visual effects
- **Animation System**: Smooth transitions and effects
- **UI Framework**: Advanced UI components

#### **System Integration**
- **Database Integration**: SQLite or PostgreSQL
- **Network Support**: Multiplayer capabilities
- **File System**: Advanced save system
- **Audio Integration**: Sound and music system

---

## 12. Code Quality

### 12.1 Code Standards

#### **Python Standards**
- **PEP 8**: Style guide compliance
- **Type Hints**: Optional type annotations
- **Docstrings**: Comprehensive documentation
- **Code Organization**: Logical file structure

#### **Architecture Standards**
- **SOLID Principles**: Single responsibility, etc.
- **Design Patterns**: Appropriate pattern usage
- **Code Reuse**: Component-based design
- **Maintainability**: Clean, readable code

### 12.2 Documentation Standards

#### **Code Documentation**
- **Inline Comments**: Complex logic explanation
- **Function Documentation**: Purpose and parameters
- **Class Documentation**: Responsibility and usage
- **Module Documentation**: Overview and dependencies

#### **Design Documentation**
- **GDD**: Comprehensive game design
- **Technical Specs**: Implementation details
- **API Documentation**: Interface specifications
- **User Documentation**: Player guides

---

**This technical implementation document provides the complete architectural blueprint for Turbo Shells, ensuring maintainable, scalable, and robust code structure.** 🏗️
