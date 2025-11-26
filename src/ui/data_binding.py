"""Data Binding Framework for TurboShells

Provides two-way data binding between UI components and game state.
Implements Observer pattern for reactive UI updates.
"""

import pygame
from typing import Dict, List, Callable, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import weakref


class BindingDirection(Enum):
    """Direction of data binding."""
    ONE_WAY_TO_UI = "to_ui"      # Game state → UI only
    ONE_WAY_TO_GAME = "to_game"  # UI → Game state only
    TWO_WAY = "two_way"          # Both directions


class ValidationType(Enum):
    """Types of data validation."""
    NONE = "none"
    RANGE = "range"
    LENGTH = "length"
    PATTERN = "pattern"
    CUSTOM = "custom"


@dataclass
class ValidationRule:
    """Validation rule for data binding."""
    type: ValidationType
    parameters: Dict[str, Any] = field(default_factory=dict)
    error_message: str = "Invalid input"


@dataclass
class DataBinding:
    """Represents a UI-to-Game data connection."""
    binding_id: str
    source: Any  # Game state object
    property_name: str
    ui_element: str  # UI element identifier
    direction: BindingDirection = BindingDirection.TWO_WAY
    converter: Optional[Callable] = None
    validator: Optional[ValidationRule] = None
    enabled: bool = True
    
    # Change tracking
    last_source_value: Any = None
    last_ui_value: Any = None
    
    # Callbacks
    on_source_changed: List[Callable] = field(default_factory=list)
    on_ui_changed: List[Callable] = field(default_factory=list)
    on_validation_error: List[Callable] = field(default_factory=list)


class DataBindingManager:
    """Manages all UI-to-game data connections.
    
    Responsibilities:
    - Create and manage data bindings
    - Synchronize data between UI and game state
    - Validate data changes
    - Handle change notifications
    - Provide reactive updates
    
    This class implements the Observer pattern to enable reactive UI
    that automatically updates when game state changes.
    """
    
    def __init__(self):
        """Initialize the data binding manager."""
        self.bindings: Dict[str, DataBinding] = {}
        self.ui_element_bindings: Dict[str, List[str]] = defaultdict(list)  # ui_element -> binding_ids
        self.source_bindings: Dict[int, List[str]] = defaultdict(list)  # source_id -> binding_ids
        self.global_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        
        # Performance tracking
        self.sync_stats = {
            'total_syncs': 0,
            'ui_to_game_syncs': 0,
            'game_to_ui_syncs': 0,
            'validation_errors': 0,
            'binding_errors': 0
        }
        
        # Change tracking
        self._pending_changes: List[Dict[str, Any]] = []
        self._batch_mode = False
    
    def bind_property(self, binding_id: str, source_object: Any, property_name: str, 
                     ui_element: str, direction: BindingDirection = BindingDirection.TWO_WAY,
                     converter: Optional[Callable] = None, validator: Optional[ValidationRule] = None) -> bool:
        """Create two-way data binding.
        
        Args:
            binding_id: Unique identifier for the binding
            source_object: Game state object
            property_name: Property name to bind
            ui_element: UI element identifier
            direction: Binding direction
            converter: Optional data conversion function
            validator: Optional validation rule
            
        Returns:
            True if binding was created successfully, False otherwise
        """
        try:
            # Validate source object has the property
            if not hasattr(source_object, property_name):
                print(f"Error: Source object does not have property '{property_name}'")
                return False
            
            # Create binding
            binding = DataBinding(
                binding_id=binding_id,
                source=source_object,
                property_name=property_name,
                ui_element=ui_element,
                direction=direction,
                converter=converter,
                validator=validator
            )
            
            # Store initial values
            binding.last_source_value = getattr(source_object, property_name, None)
            binding.last_ui_value = None
            
            # Register binding
            self.bindings[binding_id] = binding
            self.ui_element_bindings[ui_element].append(binding_id)
            self.source_bindings[id(source_object)].append(binding_id)
            
            return True
            
        except Exception as e:
            print(f"Error creating data binding '{binding_id}': {e}")
            return False
    
    def unbind(self, binding_id: str) -> bool:
        """Remove a data binding.
        
        Args:
            binding_id: ID of binding to remove
            
        Returns:
            True if binding was found and removed, False otherwise
        """
        binding = self.bindings.get(binding_id)
        if not binding:
            return False
        
        # Remove from indexes
        self.ui_element_bindings[binding.ui_element].remove(binding_id)
        self.source_bindings[id(binding.source)].remove(binding_id)
        
        # Remove binding
        del self.bindings[binding_id]
        
        return True
    
    def sync_to_ui(self, binding_id: Optional[str] = None) -> int:
        """Update UI elements from game state.
        
        Args:
            binding_id: Specific binding to sync, or None for all
            
        Returns:
            Number of bindings synchronized
        """
        sync_count = 0
        bindings_to_sync = [binding_id] if binding_id else list(self.bindings.keys())
        
        for bid in bindings_to_sync:
            if self._sync_binding_to_ui(bid):
                sync_count += 1
        
        self.sync_stats['game_to_ui_syncs'] += sync_count
        self.sync_stats['total_syncs'] += sync_count
        
        return sync_count
    
    def sync_to_game(self, binding_id: str, new_ui_value: Any) -> bool:
        """Update game state from UI input.
        
        Args:
            binding_id: ID of binding to update
            new_ui_value: New value from UI
            
        Returns:
            True if update was successful, False otherwise
        """
        if binding_id not in self.bindings:
            print(f"Warning: Binding '{binding_id}' not found")
            return False
        
        binding = self.bindings[binding_id]
        
        # Check if binding supports UI-to-game sync
        if binding.direction == BindingDirection.ONE_WAY_TO_UI:
            return False
        
        try:
            # Validate new value
            if binding.validator and not self._validate_value(binding, new_ui_value):
                return False
            
            # Convert value if converter provided
            processed_value = new_ui_value
            if binding.converter:
                try:
                    processed_value = binding.converter(new_ui_value, reverse=True)
                except Exception as e:
                    print(f"Error in value converter: {e}")
                    return False
            
            # Update game state
            setattr(binding.source, binding.property_name, processed_value)
            
            # Update tracking
            binding.last_ui_value = new_ui_value
            binding.last_source_value = processed_value
            
            # Trigger change callbacks
            for callback in binding.on_ui_changed:
                try:
                    callback(binding.last_source_value, processed_value)
                except Exception as e:
                    print(f"Error in UI change callback: {e}")
            
            # Trigger global callbacks
            for callback in self.global_callbacks['ui_changed']:
                try:
                    callback(binding_id, binding.last_source_value, processed_value)
                except Exception as e:
                    print(f"Error in global UI change callback: {e}")
            
            self.sync_stats['ui_to_game_syncs'] += 1
            self.sync_stats['total_syncs'] += 1
            
            return True
            
        except Exception as e:
            print(f"Error syncing to game for binding '{binding_id}': {e}")
            self.sync_stats['binding_errors'] += 1
            return False
    
    def _sync_binding_to_ui(self, binding_id: str) -> bool:
        """Sync a specific binding to UI.
        
        Args:
            binding_id: ID of binding to sync
            
        Returns:
            True if sync was needed and successful, False otherwise
        """
        binding = self.bindings[binding_id]
        
        # Check if binding supports game-to-UI sync
        if binding.direction == BindingDirection.ONE_WAY_TO_GAME:
            return False
        
        try:
            # Get current source value
            current_value = getattr(binding.source, binding.property_name, None)
            
            # Check if value changed
            if current_value == binding.last_source_value:
                return False
            
            # Convert value if converter provided
            ui_value = current_value
            if binding.converter:
                try:
                    ui_value = binding.converter(current_value)
                except Exception as e:
                    print(f"Error in value converter: {e}")
                    return False
            
            # Update tracking
            old_value = binding.last_source_value
            binding.last_source_value = current_value
            binding.last_ui_value = ui_value
            
            # Trigger change callbacks
            for callback in binding.on_source_changed:
                try:
                    callback(old_value, current_value)
                except Exception as e:
                    print(f"Error in source change callback: {e}")
            
            # Trigger global callbacks
            for callback in self.global_callbacks['source_changed']:
                try:
                    callback(binding_id, old_value, current_value)
                except Exception as e:
                    print(f"Error in global source change callback: {e}")
            
            return True
            
        except Exception as e:
            print(f"Error syncing to UI for binding '{binding_id}': {e}")
            self.sync_stats['binding_errors'] += 1
            return False
    
    def _validate_value(self, binding: DataBinding, value: Any) -> bool:
        """Validate a value against the binding's validation rules.
        
        Args:
            binding: Data binding with validation rules
            value: Value to validate
            
        Returns:
            True if value is valid, False otherwise
        """
        if not binding.validator:
            return True
        
        rule = binding.validator
        
        try:
            if rule.type == ValidationType.NONE:
                return True
            
            elif rule.type == ValidationType.RANGE:
                min_val = rule.parameters.get('min')
                max_val = rule.parameters.get('max')
                if min_val is not None and value < min_val:
                    return False
                if max_val is not None and value > max_val:
                    return False
            
            elif rule.type == ValidationType.LENGTH:
                min_len = rule.parameters.get('min_length')
                max_len = rule.parameters.get('max_length')
                if min_len is not None and len(value) < min_len:
                    return False
                if max_len is not None and len(value) > max_len:
                    return False
            
            elif rule.type == ValidationType.PATTERN:
                import re
                pattern = rule.parameters.get('pattern')
                if pattern and not re.match(pattern, str(value)):
                    return False
            
            elif rule.type == ValidationType.CUSTOM:
                validator_func = rule.parameters.get('validator')
                if validator_func and not validator_func(value):
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error during validation: {e}")
            return False
    
    def add_change_callback(self, binding_id: str, callback: Callable, 
                           source_changed: bool = True, ui_changed: bool = True) -> None:
        """Add callback for data changes.
        
        Args:
            binding_id: ID of binding
            callback: Callback function
            source_changed: Listen for source changes
            ui_changed: Listen for UI changes
        """
        if binding_id not in self.bindings:
            return
        
        binding = self.bindings[binding_id]
        
        if source_changed:
            binding.on_source_changed.append(callback)
        
        if ui_changed:
            binding.on_ui_changed.append(callback)
    
    def add_global_callback(self, event_type: str, callback: Callable) -> None:
        """Add global callback for binding events.
        
        Args:
            event_type: Type of event ('source_changed', 'ui_changed', 'validation_error')
            callback: Callback function
        """
        self.global_callbacks[event_type].append(callback)
    
    def get_binding(self, binding_id: str) -> Optional[DataBinding]:
        """Get a data binding by ID.
        
        Args:
            binding_id: ID of binding
            
        Returns:
            Data binding or None if not found
        """
        return self.bindings.get(binding_id)
    
    def get_bindings_for_ui_element(self, ui_element: str) -> List[DataBinding]:
        """Get all bindings for a UI element.
        
        Args:
            ui_element: UI element identifier
            
        Returns:
            List of data bindings
        """
        binding_ids = self.ui_element_bindings.get(ui_element, [])
        return [self.bindings[bid] for bid in binding_ids if bid in self.bindings]
    
    def get_bindings_for_source(self, source_object: Any) -> List[DataBinding]:
        """Get all bindings for a source object.
        
        Args:
            source_object: Source game object
            
        Returns:
            List of data bindings
        """
        binding_ids = self.source_bindings.get(id(source_object), [])
        return [self.bindings[bid] for bid in binding_ids if bid in self.bindings]
    
    def enable_binding(self, binding_id: str, enabled: bool = True) -> bool:
        """Enable or disable a binding.
        
        Args:
            binding_id: ID of binding
            enabled: Whether to enable the binding
            
        Returns:
            True if binding was found and updated, False otherwise
        """
        binding = self.bindings.get(binding_id)
        if binding:
            binding.enabled = enabled
            return True
        return False
    
    def start_batch_mode(self) -> None:
        """Start batch mode for deferred updates."""
        self._batch_mode = True
        self._pending_changes.clear()
    
    def end_batch_mode(self) -> int:
        """End batch mode and process all pending changes.
        
        Returns:
            Number of changes processed
        """
        self._batch_mode = False
        
        # Process all pending changes
        change_count = len(self._pending_changes)
        for change in self._pending_changes:
            if change['type'] == 'to_ui':
                self.sync_to_ui(change['binding_id'])
            elif change['type'] == 'to_game':
                self.sync_to_game(change['binding_id'], change['value'])
        
        self._pending_changes.clear()
        return change_count
    
    def get_sync_statistics(self) -> Dict[str, int]:
        """Get synchronization statistics.
        
        Returns:
            Dictionary with sync statistics
        """
        return self.sync_stats.copy()
    
    def reset_statistics(self) -> None:
        """Reset synchronization statistics."""
        self.sync_stats = {
            'total_syncs': 0,
            'ui_to_game_syncs': 0,
            'game_to_ui_syncs': 0,
            'validation_errors': 0,
            'binding_errors': 0
        }
    
    def validate_all_bindings(self) -> Dict[str, List[str]]:
        """Validate all bindings and return issues.
        
        Returns:
            Dictionary of binding issues by binding ID
        """
        issues = {}
        
        for binding_id, binding in self.bindings.items():
            binding_issues = []
            
            # Check if source object still has the property
            if not hasattr(binding.source, binding.property_name):
                binding_issues.append(f"Source object missing property '{binding.property_name}'")
            
            # Check if binding is still valid
            if binding.validator:
                current_value = getattr(binding.source, binding.property_name, None)
                if not self._validate_value(binding, current_value):
                    binding_issues.append("Current value fails validation")
            
            if binding_issues:
                issues[binding_id] = binding_issues
        
        return issues
    
    def print_binding_info(self) -> None:
        """Print debugging information about data bindings."""
        print("=== Data Binding Manager Info ===")
        print(f"Total bindings: {len(self.bindings)}")
        print(f"Enabled bindings: {len([b for b in self.bindings.values() if b.enabled])}")
        
        print("\nBindings by direction:")
        direction_counts = {}
        for binding in self.bindings.values():
            direction = binding.direction.value
            direction_counts[direction] = direction_counts.get(direction, 0) + 1
        
        for direction, count in direction_counts.items():
            print(f"  {direction}: {count}")
        
        print(f"\nSync statistics: {self.sync_stats}")
        
        print("\nBinding details:")
        for binding_id, binding in self.bindings.items():
            status = "ENABLED" if binding.enabled else "DISABLED"
            print(f"  {binding_id}: {binding.source.__class__.__name__}.{binding.property_name} -> {binding.ui_element} ({status})")
        
        print("=" * 40)
