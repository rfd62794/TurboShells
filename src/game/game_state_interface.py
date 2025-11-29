"""Game State Interface for TurboShells

Clean interface between UI and game state following the Interface Segregation Principle.
Provides controlled access to game data without exposing internal implementation.
"""

from typing import Dict, List, Callable, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod


class AccessLevel(Enum):
    """Access levels for game state data."""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    WRITE_ONLY = "write_only"
    HIDDEN = "hidden"


class DataType(Enum):
    """Types of data available through the interface."""
    SCALAR = "scalar"      # Simple values (int, float, str, bool)
    COLLECTION = "collection"  # Lists, dictionaries
    OBJECT = "object"      # Complex objects
    COMPUTED = "computed"  # Computed properties


@dataclass
class GameStateProperty:
    """Definition of a game state property."""
    key: str
    data_type: DataType
    access_level: AccessLevel
    description: str = ""
    validator: Optional[Callable] = None
    converter: Optional[Callable] = None
    default_value: Any = None


class GameStateInterface(ABC):
    """Clean interface between UI and game state.
    
    Responsibilities:
    - Provide controlled access to game state data
    - Validate and sanitize data access
    - Support computed properties
    - Maintain access control and permissions
    - Enable reactive updates through observers
    
    This interface implements the Interface Segregation Principle
    by providing only the necessary access methods without exposing
    the internal game state implementation.
    """
    
    def __init__(self, game):
        """Initialize the game state interface.
        
        Args:
            game: Reference to the main game state object
        """
        self.game = game
        self.read_accessors: Dict[str, Callable] = {}
        self.write_accessors: Dict[str, Callable] = {}
        self.computed_properties: Dict[str, Callable] = {}
        self.property_definitions: Dict[str, GameStateProperty] = {}
        self.observers: Dict[str, List[Callable]] = {}
        
        # Initialize standard game state properties
        self._register_standard_properties()
    
    @abstractmethod
    def _register_standard_properties(self) -> None:
        """Register standard game state properties.
        
        This method should be implemented by concrete interfaces
        to register the specific properties available for that game.
        """
        pass
    
    def register_reader(self, key: str, accessor_func: Callable, 
                       data_type: DataType = DataType.SCALAR,
                       description: str = "", validator: Optional[Callable] = None) -> None:
        """Register read access to game data.
        
        Args:
            key: Property key identifier
            accessor_func: Function to get the value (game) -> value
            data_type: Type of data
            description: Human-readable description
            validator: Optional validation function
        """
        self.read_accessors[key] = accessor_func
        
        # Create property definition
        property_def = GameStateProperty(
            key=key,
            data_type=data_type,
            access_level=AccessLevel.READ_ONLY,
            description=description,
            validator=validator
        )
        self.property_definitions[key] = property_def
    
    def register_writer(self, key: str, writer_func: Callable,
                       data_type: DataType = DataType.SCALAR,
                       description: str = "", validator: Optional[Callable] = None,
                       converter: Optional[Callable] = None) -> None:
        """Register write access to game data.
        
        Args:
            key: Property key identifier
            writer_func: Function to set the value (game, value) -> bool
            data_type: Type of data
            description: Human-readable description
            validator: Optional validation function
            converter: Optional data converter
        """
        self.write_accessors[key] = writer_func
        
        # Create or update property definition
        if key in self.property_definitions:
            property_def = self.property_definitions[key]
            property_def.access_level = AccessLevel.READ_WRITE
        else:
            property_def = GameStateProperty(
                key=key,
                data_type=data_type,
                access_level=AccessLevel.WRITE_ONLY,
                description=description,
                validator=validator,
                converter=converter
            )
            self.property_definitions[key] = property_def
    
    def register_computed_property(self, key: str, compute_func: Callable,
                                 data_type: DataType = DataType.COMPUTED,
                                 description: str = "") -> None:
        """Register a computed property.
        
        Args:
            key: Property key identifier
            compute_func: Function to compute value (game) -> value
            data_type: Type of data
            description: Human-readable description
        """
        self.computed_properties[key] = compute_func
        
        # Create property definition
        property_def = GameStateProperty(
            key=key,
            data_type=data_type,
            access_level=AccessLevel.READ_ONLY,
            description=description
        )
        self.property_definitions[key] = property_def
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get game state value.
        
        Args:
            key: Property key
            default: Default value if not found
            
        Returns:
            Game state value or default
        """
        try:
            # Check computed properties first
            if key in self.computed_properties:
                return self.computed_properties[key](self.game)
            
            # Check read accessors
            accessor = self.read_accessors.get(key)
            if accessor:
                value = accessor(self.game)
                
                # Validate value if validator exists
                property_def = self.property_definitions.get(key)
                if property_def and property_def.validator:
                    if not property_def.validator(value):
                        return default
                
                return value
            
            # Direct game property access (fallback)
            if hasattr(self.game, key):
                return getattr(self.game, key)
            
            return default
            
        except Exception as e:
            print(f"Error getting game state property '{key}': {e}")
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """Set game state value.
        
        Args:
            key: Property key
            value: New value to set
            
        Returns:
            True if set was successful, False otherwise
        """
        try:
            # Check write accessors
            writer = self.write_accessors.get(key)
            if writer:
                # Validate value
                property_def = self.property_definitions.get(key)
                if property_def:
                    if property_def.validator and not property_def.validator(value):
                        print(f"Validation failed for property '{key}'")
                        return False
                    
                    # Convert value if converter exists
                    if property_def.converter:
                        value = property_def.converter(value)
                
                # Set value and trigger observers
                old_value = self.get(key)
                success = writer(self.game, value)
                
                if success:
                    self._notify_observers(key, old_value, value)
                
                return success
            
            # Direct game property access (fallback)
            if hasattr(self.game, key):
                old_value = getattr(self.game, key)
                setattr(self.game, key, value)
                self._notify_observers(key, old_value, value)
                return True
            
            print(f"Warning: Property '{key}' not found for writing")
            return False
            
        except Exception as e:
            print(f"Error setting game state property '{key}': {e}")
            return False
    
    def has_property(self, key: str) -> bool:
        """Check if property exists.
        
        Args:
            key: Property key
            
        Returns:
            True if property exists, False otherwise
        """
        return (key in self.read_accessors or 
                key in self.write_accessors or 
                key in self.computed_properties or
                hasattr(self.game, key))
    
    def get_property_info(self, key: str) -> Optional[GameStateProperty]:
        """Get information about a property.
        
        Args:
            key: Property key
            
        Returns:
            Property definition or None if not found
        """
        return self.property_definitions.get(key)
    
    def get_all_properties(self) -> Dict[str, GameStateProperty]:
        """Get all available properties.
        
        Returns:
            Dictionary of all property definitions
        """
        return self.property_definitions.copy()
    
    def get_properties_by_type(self, data_type: DataType) -> Dict[str, GameStateProperty]:
        """Get properties filtered by data type.
        
        Args:
            data_type: Type of data to filter by
            
        Returns:
            Dictionary of matching properties
        """
        return {k: v for k, v in self.property_definitions.items() 
                if v.data_type == data_type}
    
    def get_readable_properties(self) -> Dict[str, GameStateProperty]:
        """Get all readable properties.
        
        Returns:
            Dictionary of readable property definitions
        """
        return {k: v for k, v in self.property_definitions.items() 
                if v.access_level in [AccessLevel.READ_ONLY, AccessLevel.READ_WRITE]}
    
    def get_writable_properties(self) -> Dict[str, GameStateProperty]:
        """Get all writable properties.
        
        Returns:
            Dictionary of writable property definitions
        """
        return {k: v for k, v in self.property_definitions.items() 
                if v.access_level in [AccessLevel.WRITE_ONLY, AccessLevel.READ_WRITE]}
    
    # Observer pattern methods
    def observe(self, key: str, callback: Callable[[str, Any, Any], None]) -> None:
        """Observe changes to a property.
        
        Args:
            key: Property key to observe
            callback: Callback function (key, old_value, new_value) -> None
        """
        if key not in self.observers:
            self.observers[key] = []
        self.observers[key].append(callback)
    
    def unobserve(self, key: str, callback: Callable[[str, Any, Any], None]) -> bool:
        """Stop observing changes to a property.
        
        Args:
            key: Property key to stop observing
            callback: Callback function to remove
            
        Returns:
            True if callback was found and removed, False otherwise
        """
        if key in self.observers:
            try:
                self.observers[key].remove(callback)
                return True
            except ValueError:
                pass
        return False
    
    def _notify_observers(self, key: str, old_value: Any, new_value: Any) -> None:
        """Notify observers of property changes.
        
        Args:
            key: Property key that changed
            old_value: Previous value
            new_value: New value
        """
        if key in self.observers:
            for callback in self.observers[key]:
                try:
                    callback(key, old_value, new_value)
                except Exception as e:
                    print(f"Error in property observer callback: {e}")
    
    # Batch operations
    def get_multiple(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple property values.
        
        Args:
            keys: List of property keys
            
        Returns:
            Dictionary of key-value pairs
        """
        return {key: self.get(key) for key in keys}
    
    def set_multiple(self, updates: Dict[str, Any]) -> Dict[str, bool]:
        """Set multiple property values.
        
        Args:
            updates: Dictionary of key-value pairs to set
            
        Returns:
            Dictionary of key-success pairs
        """
        results = {}
        for key, value in updates.items():
            results[key] = self.set(key, value)
        return results
    
    # Validation and utilities
    def validate_property(self, key: str, value: Any) -> bool:
        """Validate a value for a property.
        
        Args:
            key: Property key
            value: Value to validate
            
        Returns:
            True if value is valid, False otherwise
        """
        property_def = self.property_definitions.get(key)
        if property_def and property_def.validator:
            return property_def.validator(value)
        return True
    
    def get_property_schema(self) -> Dict[str, Any]:
        """Get schema of all available properties.
        
        Returns:
            Dictionary representing the property schema
        """
        schema = {
            'properties': {},
            'computed_properties': list(self.computed_properties.keys()),
            'readable_keys': list(self.get_readable_properties().keys()),
            'writable_keys': list(self.get_writable_properties().keys())
        }
        
        for key, prop_def in self.property_definitions.items():
            schema['properties'][key] = {
                'type': prop_def.data_type.value,
                'access': prop_def.access_level.value,
                'description': prop_def.description,
                'has_validator': prop_def.validator is not None,
                'has_converter': prop_def.converter is not None,
                'default_value': prop_def.default_value
            }
        
        return schema
    
    def print_property_info(self) -> None:
        """Print debugging information about available properties."""
        print("=== Game State Interface Properties ===")
        print(f"Total properties: {len(self.property_definitions)}")
        print(f"Readable: {len(self.get_readable_properties())}")
        print(f"Writable: {len(self.get_writable_properties())}")
        print(f"Computed: {len(self.computed_properties)}")
        print()
        
        for key, prop_def in self.property_definitions.items():
            access_symbol = {
                AccessLevel.READ_ONLY: "R",
                AccessLevel.WRITE_ONLY: "W",
                AccessLevel.READ_WRITE: "RW",
                AccessLevel.HIDDEN: "H"
            }.get(prop_def.access_level, "?")
            
            type_symbol = prop_def.data_type.value[0].upper()
            
            print(f"  {key}: {access_symbol}/{type_symbol} - {prop_def.description}")
        
        print("=" * 45)


class TurboShellsGameStateInterface(GameStateInterface):
    """Concrete implementation of game state interface for TurboShells."""
    
    def _register_standard_properties(self) -> None:
        """Register standard TurboShells game state properties."""
        
        # Basic game state
        self.register_reader('state', lambda g: getattr(g, 'state', 'menu'), 
                           DataType.SCALAR, "Current game state")
        self.register_writer('state', lambda g, v: setattr(g, 'state', v),
                           DataType.SCALAR, "Current game state")
        
        # Player resources
        self.register_reader('money', lambda g: getattr(g, 'money', 0),
                           DataType.SCALAR, "Player's money")
        self.register_writer('money', lambda g, v: self._validate_money(g, v),
                           DataType.SCALAR, "Player's money",
                           validator=lambda x: isinstance(x, (int, float)) and x >= 0)
        
        # Roster management
        self.register_reader('roster', lambda g: getattr(g, 'roster', []),
                           DataType.COLLECTION, "Player's turtle roster")
        self.register_reader('retired_roster', lambda g: getattr(g, 'retired_roster', []),
                           DataType.COLLECTION, "Retired turtles")
        
        # Shop state
        self.register_reader('shop_inventory', lambda g: getattr(g, 'shop_inventory', []),
                           DataType.COLLECTION, "Current shop inventory")
        self.register_reader('shop_message', lambda g: getattr(g, 'shop_message', ''),
                           DataType.SCALAR, "Shop status message")
        
        # Race state
        self.register_reader('race_results', lambda g: getattr(g, 'race_results', []),
                           DataType.COLLECTION, "Recent race results")
        self.register_reader('race_speed_multiplier', lambda g: getattr(g, 'race_speed_multiplier', 1),
                           DataType.SCALAR, "Race speed multiplier")
        self.register_writer('race_speed_multiplier', lambda g, v: setattr(g, 'race_speed_multiplier', max(1, v)),
                           DataType.SCALAR, "Race speed multiplier",
                           validator=lambda x: isinstance(x, (int, float)) and x > 0)
        
        # Breeding state
        self.register_reader('breeding_parents', lambda g: getattr(g, 'breeding_parents', []),
                           DataType.COLLECTION, "Selected breeding parents")
        
        # Computed properties
        self.register_computed_property('active_turtle_count', 
                                     lambda g: len([t for t in getattr(g, 'roster', []) if t is not None]),
                                     DataType.SCALAR, "Number of active turtles")
        
        self.register_computed_property('total_turtle_count',
                                     lambda g: len([t for t in getattr(g, 'roster', []) if t is not None]) + 
                                              len(getattr(g, 'retired_roster', [])),
                                     DataType.SCALAR, "Total number of turtles")
        
        self.register_computed_property('can_afford_shop',
                                     lambda g: self._can_afford_shop(g),
                                     DataType.SCALAR, "Whether player can afford shop items")
                                     
        # Shop Actions
        self.register_writer('shop_buy', lambda g, index: g.shop_manager.buy_turtle(index),
                           DataType.SCALAR, "Buy turtle at index")
        self.register_writer('shop_refresh', lambda g, _: g.shop_manager.refresh_stock(free=False),
                           DataType.SCALAR, "Refresh shop inventory")
                           
        # Roster Properties
        self.register_reader('active_racer_index', lambda g: getattr(g, 'active_racer_index', 0), DataType.SCALAR, "Index of active racer")
        self.register_writer('active_racer_index', lambda g, v: setattr(g, 'active_racer_index', v), DataType.SCALAR, "Index of active racer")
        
        self.register_reader('show_retired_view', lambda g: getattr(g, 'show_retired_view', False), DataType.SCALAR, "Show retired turtles")
        self.register_writer('show_retired_view', lambda g, v: setattr(g, 'show_retired_view', v), DataType.SCALAR, "Show retired turtles")
        
        self.register_reader('current_bet', lambda g: getattr(g, 'current_bet', 0), DataType.SCALAR, "Current bet amount")
        self.register_writer('current_bet', lambda g, v: setattr(g, 'current_bet', v), DataType.SCALAR, "Current bet amount")
        
        self.register_reader('select_racer_mode', lambda g: getattr(g, 'select_racer_mode', False), DataType.SCALAR, "In racer selection mode")
        self.register_writer('select_racer_mode', lambda g, v: setattr(g, 'select_racer_mode', v), DataType.SCALAR, "In racer selection mode")
        
        # Roster Actions
        self.register_writer('train_turtle', lambda g, index: g.roster_manager.train_turtle(index),
                           DataType.SCALAR, "Train turtle at index")
        self.register_writer('retire_turtle', lambda g, index: g.roster_manager.retire_turtle(index),
                           DataType.SCALAR, "Retire turtle at index")
        self.register_writer('set_active_racer', lambda g, index: setattr(g, 'active_racer_index', index),
                           DataType.SCALAR, "Set active racer index")
        self.register_writer('toggle_view', lambda g, show_retired: setattr(g, 'show_retired_view', show_retired),
                           DataType.SCALAR, "Set retired view visibility")
        self.register_writer('set_bet', lambda g, amount: setattr(g, 'current_bet', amount),
                           DataType.SCALAR, "Set bet amount")
                           
        # Race Properties (Duplicates removed, kept computed)
        self.register_computed_property('race_roster', lambda g: getattr(g.race_manager, 'race_roster', []),
                                      DataType.COLLECTION, "Current race roster")
        
        # Race Actions
        self.register_writer('set_race_speed', lambda g, speed: setattr(g, 'race_speed_multiplier', speed),
                           DataType.SCALAR, "Set race speed multiplier")
        self.register_writer('race_again', lambda g, _: self._race_again(g),
                           DataType.SCALAR, "Restart race")
        self.register_writer('start_race', lambda g, _: self._start_race(g),
                           DataType.SCALAR, "Start new race")
        self.register_writer('goto_menu', lambda g, _: setattr(g, 'state', 'MENU'),
                           DataType.SCALAR, "Go to menu")
        
        # Profile Actions
        self.register_reader('profile_turtle_index', lambda g: getattr(g, 'profile_turtle_index', 0),
                           DataType.SCALAR, "Index of turtle being viewed in profile")
        self.register_writer('profile_turtle_index', lambda g, v: setattr(g, 'profile_turtle_index', v),
                           DataType.SCALAR, "Index of turtle being viewed in profile")
        self.register_writer('view_profile', lambda g, index: self._view_profile(g, index),
                           DataType.SCALAR, "View turtle profile")
        self.register_writer('release_turtle', lambda g, index: g.roster_manager.release_turtle(index),
                           DataType.SCALAR, "Release turtle from roster")

    def _race_again(self, game):
        """Restart the race."""
        game.race_manager.start_race()
        from settings import STATE_RACE
        game.state = STATE_RACE

    def _start_race(self, game):
        """Start a new race from roster selection."""
        print(f"[DEBUG] Starting race with active_racer_index: {getattr(game, 'active_racer_index', 0)}")
        
        # Ensure active racer is valid
        idx = getattr(game, 'active_racer_index', 0)
        roster = getattr(game, 'roster', [])
        
        print(f"[DEBUG] Roster length: {len(roster)}")
        print(f"[DEBUG] Roster contents: {[t.name if t else None for t in roster]}")
        
        if 0 <= idx < len(roster) and roster[idx]:
            print(f"[DEBUG] Valid racer found: {roster[idx].name}")
            # Start the race through race manager
            game.race_manager.start_race()
            
            # Verify race roster was created
            if hasattr(game.race_manager, 'race_roster') and game.race_manager.race_roster:
                print(f"[DEBUG] Race roster created with {len(game.race_manager.race_roster)} turtles")
                for i, turtle in enumerate(game.race_manager.race_roster):
                    print(f"[DEBUG]   Racer {i}: {turtle.name} at distance {turtle.race_distance}")
            else:
                print(f"[ERROR] Race roster not created properly!")
                return False
                
            # Transition to race state - use the correct constant
            from settings import STATE_RACE
            game.state = STATE_RACE
            game.select_racer_mode = False
            print(f"[DEBUG] Race started successfully, state set to: {game.state}")
            return True
        else:
            print(f"[ERROR] Invalid active racer index {idx} or no turtle found")
            return False
            
    def _view_profile(self, game, index):
        """View a turtle's profile."""
        game.profile_turtle_index = index
        from settings import STATE_PROFILE
        game.state = STATE_PROFILE
    
    def _validate_money(self, game, value) -> bool:
        """Validate and set money value."""
        if isinstance(value, (int, float)) and value >= 0:
            game.money = int(value)
            return True
        return False
    
    def _can_afford_shop(self, game) -> bool:
        """Check if player can afford any shop items."""
        shop_inventory = getattr(game, 'shop_inventory', [])
        money = getattr(game, 'money', 0)
        return any(item.price <= money for item in shop_inventory if hasattr(item, 'price'))
