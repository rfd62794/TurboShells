# Phase 27: ImGui Hybrid Architecture Migration

## **Phase Overview**

Transform TurboShells from a pure PyGame monolithic architecture to a hybrid PyGame + pyimgui system following Clean Architecture principles. This migration provides strict separation between the game engine (PyGame) and user interface (ImGui), enabling data-driven design patterns and maintainable UI components.

## **Current State Analysis**

### Existing Architecture
- **Monolithic Design**: Single `TurboShellsGame` class handling everything
- **Direct Event Handling**: PyGame events processed through `StateHandler` and `KeyboardHandler`
- **Immediate Mode Rendering**: PyGame drawing functions mixed with game logic
- **Tight Coupling**: UI rendering directly accesses game state without abstraction

### Critical Issues
- No separation between UI and game logic
- Event handling mixed with game state management
- UI rendering tightly coupled to game state
- No data binding system for UI components
- Difficult to test UI components in isolation

## **Target Architecture**

### Clean Architecture Pipeline
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   ImGui UI      │───▶│   Data Pipeline  │───▶│  PyGame Engine  │
│ (Interface)     │    │   (Pure Data)    │    │   (World)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Key Principles
- **Single Responsibility**: Each component has one clear purpose
- **Data-Driven**: UI manipulates data, engine renders data
- **Separation of Concerns**: UI logic separate from game logic
- **Testability**: Each layer can be unit tested independently

## **Implementation Phases**

### Phase 1: Dependency & Boilerplate Setup

#### 1.1 Dependency Integration
```python
# requirements.txt additions
pygame-ce>=2.5
imgui[pygame]>=2.0.0  # OpenGL backend for PyGame
PyOpenGL>=3.1.0       # OpenGL context provider
```

#### 1.2 ImGui Context Manager
```python
# src/ui/imgui_context.py
import pygame
import imgui
import OpenGL.GL as gl
from imgui.integrations.pygame import PygameRenderer

class ImGuiContext:
    """Manages ImGui initialization, context, and rendering"""
    
    def __init__(self, pygame_surface):
        self.screen = pygame_surface
        self.context = None
        self.impl = None
        
    def initialize(self):
        """Initialize ImGui context and PyGame integration"""
        imgui.create_context()
        self.impl = PygameRenderer()
        
    def begin_frame(self):
        """Start new ImGui frame"""
        self.impl.process_event(pygame.event.Event(pygame.USEREVENT, {}))
        imgui.new_frame()
        
    def end_frame(self):
        """End ImGui frame and render"""
        imgui.render()
        self.impl.render(imgui.get_draw_data())
        
    def shutdown(self):
        """Clean up ImGui resources"""
        if self.impl:
            self.impl.shutdown()
```

#### 1.3 UI Layer Foundation
```python
# src/ui/ui_manager.py
class UIManager:
    """Central UI coordinator following SRP"""
    
    def __init__(self, screen_rect):
        self.screen_rect = screen_rect
        self.imgui_context = None
        self.ui_panels = {}
        self.data_bindings = {}
        
    def initialize(self, pygame_surface):
        """Initialize ImGui and UI system"""
        self.imgui_context = ImGuiContext(pygame_surface)
        self.imgui_context.initialize()
        
    def handle_event(self, event):
        """Route events to ImGui first, then game if not consumed"""
        if self.imgui_context and self.imgui_context.impl:
            return self.imgui_context.impl.process_event(event)
        return False
```

### Phase 2: Input Hijack

#### 2.1 Event Flow Redesign
```python
# src/main.py (modified handle_input)
def handle_input(self):
    for event in pygame.event.get():
        # 1. ImGui gets first priority
        if self.ui_manager.handle_event(event):
            continue  # Event consumed by ImGui
            
        # 2. Game-specific events (only if ImGui didn't handle)
        if event.type == pygame.QUIT:
            self.save_on_exit()
            pygame.quit()
            sys.exit()
            
        # 3. Game state handling (reduced scope)
        self.state_handler.handle_game_events(event)
```

#### 2.2 Input Event Bus
```python
# src/ui/input_bus.py
class InputBus:
    """Decoupled input event distribution"""
    
    def __init__(self):
        self.subscribers = defaultdict(list)
        
    def subscribe(self, event_type, callback):
        """Subscribe to specific input events"""
        self.subscribers[event_type].append(callback)
        
    def publish(self, event):
        """Publish event to subscribers"""
        event_type = event.type if hasattr(event, 'type') else type(event)
        for callback in self.subscribers.get(event_type, []):
            if callback(event):
                return True  # Event consumed
        return False
```

#### 2.3 Game Input Adapter
```python
# src/input/game_input_adapter.py
class GameInputAdapter:
    """Adapter to convert ImGui events to game actions"""
    
    def __init__(self, game_state):
        self.game_state = game_state
        self.action_mappings = {}
        
    def register_action(self, imgui_element, game_action):
        """Map ImGui interactions to game actions"""
        self.action_mappings[imgui_element] = game_action
        
    def handle_action(self, action_name, *args):
        """Execute game action from UI interaction"""
        if action_name in self.action_mappings:
            self.action_mappings[action_name](*args)
```

### Phase 3: Overlay Implementation

#### 3.1 Rendering Pipeline
```python
# src/graphics/rendering_pipeline.py
class RenderingPipeline:
    """Manages layered rendering: Game World → ImGui Overlay"""
    
    def __init__(self, screen):
        self.screen = screen
        self.game_renderer = None
        self.ui_manager = None
        
    def render_frame(self, game_state):
        """Render complete frame with proper layering"""
        # 1. Clear screen (PyGame)
        self.screen.fill(BLACK)
        
        # 2. Render game world (PyGame - sprites, entities)
        self.game_renderer.render_game_world(game_state)
        
        # 3. Begin ImGui frame
        self.ui_manager.imgui_context.begin_frame()
        
        # 4. Render UI overlay (ImGui)
        self.ui_manager.render_ui_panels(game_state)
        
        # 5. End ImGui frame and composite
        self.ui_manager.imgui_context.end_frame()
        
        # 6. Final PyGame display flip
        pygame.display.flip()
```

#### 3.2 Panel System Architecture
```python
# src/ui/panels/base_panel.py
class BasePanel:
    """Base class for all UI panels with SRP"""
    
    def __init__(self, panel_id, title=""):
        self.panel_id = panel_id
        self.title = title
        self.visible = True
        self.position = (0, 0)
        self.size = (300, 200)
        self.data_bindings = {}
        
    def render(self, game_state):
        """Render panel content - to be overridden"""
        raise NotImplementedError
        
    def bind_data(self, key, data_source):
        """Bind UI element to game data"""
        self.data_bindings[key] = data_source

# src/ui/panels/main_menu_panel.py
class MainMenuPanel(BasePanel):
    """Main menu panel using ImGui"""
    
    def render(self, game_state):
        imgui.set_next_window_size(400, 500)
        imgui.set_next_window_position(100, 100)
        
        expanded, opened = imgui.begin("Turbo Shells", True)
        
        if expanded:
            # Menu buttons with data binding
            if imgui.button("Roster"):
                self._navigate_to_state("roster")
                
            imgui.same_line()
            if imgui.button("Shop"):
                self._navigate_to_state("shop")
                
            # Money display (data-bound)
            money = self.data_bindings.get("money", 0)
            imgui.text(f"Money: ${money}")
            
        imgui.end()
```

#### 3.3 View Migration Strategy
```python
# src/ui/views/migration_adapter.py
class MigrationAdapter:
    """Gradual migration adapter for existing views"""
    
    def __init__(self):
        self.legacy_views = {}
        self.imgui_panels = {}
        self.migration_flags = {}
        
    def register_legacy_view(self, view_name, view_function):
        """Register existing PyGame view for gradual migration"""
        self.legacy_views[view_name] = view_function
        
    def migrate_view(self, view_name, imgui_panel):
        """Mark view as migrated to ImGui"""
        self.migration_flags[view_name] = True
        self.imgui_panels[view_name] = imgui_panel
        
    def render_view(self, view_name, screen, font, game_state):
        """Render using appropriate system"""
        if self.migration_flags.get(view_name, False):
            # Use ImGui panel
            panel = self.imgui_panels.get(view_name)
            if panel:
                panel.render(game_state)
        else:
            # Use legacy PyGame view
            legacy_func = self.legacy_views.get(view_name)
            if legacy_func:
                legacy_func(screen, font, game_state)
```

### Phase 4: State Connection

#### 4.1 Data Binding System
```python
# src/ui/data_binding.py
@dataclass
class DataBinding:
    """Represents a UI-to-Game data connection"""
    source: Any  # Game state object
    property_name: str
    ui_element: str
    converter: Optional[Callable] = None
    validator: Optional[Callable] = None

class DataBindingManager:
    """Manages all UI-to-game data connections"""
    
    def __init__(self):
        self.bindings = {}
        self.change_callbacks = defaultdict(list)
        
    def bind_property(self, binding_id, source_object, property_name, ui_element):
        """Create two-way data binding"""
        binding = DataBinding(source_object, property_name, ui_element)
        self.bindings[binding_id] = binding
        
    def sync_to_ui(self):
        """Update UI elements from game state"""
        for binding_id, binding in self.bindings.items():
            value = getattr(binding.source, binding.property_name)
            if binding.converter:
                value = binding.converter(value)
            # Update UI element with value
            
    def sync_to_game(self, binding_id, new_value):
        """Update game state from UI input"""
        binding = self.bindings.get(binding_id)
        if binding:
            if binding.validator and not binding.validator(new_value):
                return False
            if binding.converter:
                new_value = binding.converter(new_value, reverse=True)
            setattr(binding.source, binding.property_name, new_value)
            
            # Trigger change callbacks
            for callback in self.change_callbacks[binding_id]:
                callback(new_value)
            return True
```

#### 4.2 Game State Interface
```python
# src/game/game_state_interface.py
class GameStateInterface:
    """Clean interface between UI and game state"""
    
    def __init__(self, game):
        self.game = game
        self.read_accessors = {}
        self.write_accessors = {}
        
    def register_reader(self, key, accessor_func):
        """Register read access to game data"""
        self.read_accessors[key] = accessor_func
        
    def register_writer(self, key, writer_func):
        """Register write access to game data"""
        self.write_accessors[key] = writer_func
        
    def get(self, key, default=None):
        """Get game state value"""
        accessor = self.read_accessors.get(key)
        return accessor(self.game) if accessor else default
        
    def set(self, key, value):
        """Set game state value"""
        writer = self.write_accessors.get(key)
        if writer:
            writer(self.game, value)
            return True
        return False
```

#### 4.3 Component Integration Example
```python
# src/ui/panels/shop_panel.py
class ShopPanel(BasePanel):
    """Shop interface with proper data binding"""
    
    def __init__(self, game_state_interface):
        super().__init__("shop", "Turbo Shop")
        self.game_state = game_state_interface
        
        # Register data bindings
        self.game_state.register_reader("money", lambda g: g.money)
        self.game_state.register_reader("inventory", lambda g: g.shop_inventory)
        self.game_state.register_writer("purchase_item", self._handle_purchase)
        
    def render(self, game_state):
        imgui.set_next_window_size(600, 400)
        
        if imgui.begin("Shop", True)[1]:
            # Bound money display
            money = self.game_state.get("money", 0)
            imgui.text(f"Available Funds: ${money}")
            
            # Bound inventory display
            inventory = self.game_state.get("inventory", [])
            for item in inventory:
                if imgui.button(f"Buy {item.name} (${item.price})"):
                    self.game_state.set("purchase_item", item)
                    
        imgui.end()
        
    def _handle_purchase(self, game, item):
        """Handle purchase with validation"""
        if game.money >= item.price:
            game.money -= item.price
            # Add to roster, etc.
            return True
        return False
```

## **Migration Timeline**

### Week 1: Foundation
- [ ] Add dependencies and ImGui context
- [ ] Create base UI manager and panel system
- [ ] Set up rendering pipeline
- [ ] Test basic ImGui integration

### Week 2: Input Migration
- [ ] Implement input hijack system
- [ ] Create event bus architecture
- [ ] Migrate settings view as proof of concept
- [ ] Test event flow isolation

### Week 3: Core Views
- [ ] Migrate main menu interface
- [ ] Implement shop panel with data binding
- [ ] Create roster management interface
- [ ] Test state synchronization

### Week 4: Advanced Features
- [ ] Migrate breeding interface
- [ ] Add genetic modification sliders
- [ ] Implement racing controls
- [ ] Create debug tools panel

### Week 5: Complex Systems
- [ ] Migrate voting interface
- [ ] Add profile management
- [ ] Implement tournament controls
- [ ] Performance optimization

### Week 6: Polish & Testing
- [ ] Complete migration of all views
- [ ] Performance profiling and optimization
- [ ] Comprehensive testing
- [ ] Documentation updates

## **File Structure Changes**

### New Files
```
src/
├── ui/
│   ├── imgui_context.py          # ImGui context management
│   ├── ui_manager.py             # Central UI coordinator
│   ├── input_bus.py              # Event distribution system
│   ├── data_binding.py           # Data binding framework
│   ├── panels/
│   │   ├── base_panel.py         # Base panel class
│   │   ├── main_menu_panel.py    # Main menu interface
│   │   ├── shop_panel.py         # Shop interface
│   │   ├── roster_panel.py       # Roster management
│   │   ├── breeding_panel.py     # Breeding interface
│   │   ├── race_panel.py         # Racing controls
│   │   └── settings_panel.py     # Settings interface
│   └── views/
│       └── migration_adapter.py  # Gradual migration helper
├── input/
│   └── game_input_adapter.py    # ImGui to game action adapter
├── game/
│   └── game_state_interface.py   # Clean game state interface
└── graphics/
    └── rendering_pipeline.py     # Layered rendering system
```

### Modified Files
```
src/
├── main.py                       # Updated main loop
├── requirements.txt              # Added ImGui dependencies
└── ui/views/renderer.py         # Updated for hybrid rendering
```

## **Testing Strategy**

### Unit Tests
- [ ] ImGui context initialization
- [ ] Data binding synchronization
- [ ] Event bus distribution
- [ ] Panel rendering logic
- [ ] Game state interface

### Integration Tests
- [ ] Input flow from ImGui to game
- [ ] Data binding round-trip
- [ ] Rendering pipeline layers
- [ ] State synchronization

### Performance Tests
- [ ] Frame rate impact
- [ ] Memory usage
- [ ] Event processing overhead
- [ ] UI rendering performance

## **Risk Mitigation**

### Technical Risks
- **OpenGL Context Issues**: Test on multiple systems early
- **Event Handling Conflicts**: Implement clear priority system
- **Performance Degradation**: Profile and optimize early
- **State Synchronization**: Implement robust error handling

### Migration Risks
- **Feature Regression**: Maintain feature parity during migration
- **User Experience**: Preserve existing UI behavior
- **Data Corruption**: Implement safe migration procedures
- **Development Disruption**: Use gradual migration approach

## **Success Criteria**

### Functional Requirements
- [ ] All existing UI functionality preserved
- [ ] Clean separation between UI and game logic
- [ ] Data binding system working correctly
- [ ] Performance comparable to current system

### Architectural Requirements
- [ ] Clean Architecture principles followed
- [ ] Testable UI components
- [ ] Maintainable code structure
- [ ] Extensible system for future features

### Quality Requirements
- [ ] Comprehensive test coverage
- [ ] Documentation updated
- [ ] Code review completed
- [ ] Performance benchmarks met

## **Benefits Achieved**

### Immediate Benefits
- **Separation of Concerns**: UI logic completely separate from game logic
- **Testability**: Each layer can be unit tested independently
- **Maintainability**: Clear boundaries and responsibilities
- **Extensibility**: Easy to add new UI components without touching game code

### Long-term Benefits
- **Professional Architecture**: Clean, maintainable codebase
- **Future-Proof**: Foundation for advanced UI features
- **Developer Experience**: Easier to develop and debug UI
- **Performance**: Optimized rendering pipeline

## **Next Steps**

After completing this migration:
1. **Phase 7: Pond/Glade Environment** - Visual immersion with new UI system
2. **Phase 8: Advanced Training System** - Enhanced UI for training management
3. **Phase 25: UI Component SRP** - Further refinement of UI architecture
4. **Future Graphics Enhancements** - Foundation for advanced rendering

---

*This migration transforms TurboShells into a modern, maintainable architecture while preserving all existing functionality and providing a solid foundation for future development.*
