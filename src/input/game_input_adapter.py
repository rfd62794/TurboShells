"""Game Input Adapter for TurboShells

Converts ImGui UI interactions to game actions, implementing the Adapter pattern.
Provides clean separation between UI layer and game logic.
"""

import pygame
from typing import Dict, Callable, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class ActionType(Enum):
    """Types of game actions that can be triggered by UI."""
    NAVIGATION = "navigation"
    GAME_STATE = "game_state"
    TURTLE_ACTION = "turtle_action"
    SHOP_ACTION = "shop_action"
    RACE_ACTION = "race_action"
    BREEDING_ACTION = "breeding_action"
    SETTINGS_ACTION = "settings_action"
    SYSTEM_ACTION = "system_action"


@dataclass
class GameAction:
    """Represents a game action triggered by UI interaction."""
    action_type: ActionType
    action_name: str
    parameters: Dict[str, Any]
    source: str  # Which UI element triggered this action


class GameInputAdapter:
    """Adapter to convert ImGui events to game actions.
    
    Responsibilities:
    - Map ImGui UI interactions to game actions
    - Validate action parameters
    - Execute game actions through proper interfaces
    - Maintain action history for debugging
    
    This class implements the Adapter pattern to bridge the UI layer
    with the game logic layer without creating direct dependencies.
    """
    
    def __init__(self, game_state):
        """Initialize the game input adapter.
        
        Args:
            game_state: Reference to the main game state object
        """
        self.game_state = game_state
        self.action_mappings: Dict[str, Callable] = {}
        self.action_history: List[GameAction] = []
        self.max_history = 50
        self._register_default_actions()
        
    def _register_default_actions(self) -> None:
        """Register default game actions."""
        # Navigation actions
        self.register_action("navigate_to_menu", self._navigate_to_menu)
        self.register_action("navigate_to_roster", self._navigate_to_roster)
        self.register_action("navigate_to_shop", self._navigate_to_shop)
        self.register_action("navigate_to_breeding", self._navigate_to_breeding)
        self.register_action("navigate_to_race", self._navigate_to_race)
        self.register_action("navigate_to_profile", self._navigate_to_profile)
        self.register_action("navigate_to_voting", self._navigate_to_voting)
        
        # Turtle actions
        self.register_action("train_turtle", self._train_turtle)
        self.register_action("rest_turtle", self._rest_turtle)
        self.register_action("retire_turtle", self._retire_turtle)
        self.register_action("select_turtle", self._select_turtle)
        
        # Shop actions
        self.register_action("buy_turtle", self._buy_turtle)
        self.register_action("refresh_shop", self._refresh_shop)
        
        # Race actions
        self.register_action("start_race", self._start_race)
        self.register_action("set_race_speed", self._set_race_speed)
        self.register_action("select_racer", self._select_racer)
        
        # Breeding actions
        self.register_action("select_breeding_parent", self._select_breeding_parent)
        self.register_action("attempt_breeding", self._attempt_breeding)
        self.register_action("clear_breeding_selection", self._clear_breeding_selection)
        
        # Settings actions
        self.register_action("toggle_settings", self._toggle_settings)
        self.register_action("update_setting", self._update_setting)
        self.register_action("reset_settings", self._reset_settings)
        
        # System actions
        self.register_action("save_game", self._save_game)
        self.register_action("load_game", self._load_game)
        self.register_action("exit_game", self._exit_game)
        self.register_action("toggle_ui", self._toggle_ui)
    
    def register_action(self, action_name: str, callback: Callable) -> None:
        """Register a game action callback.
        
        Args:
            action_name: Name of the action
            callback: Function to execute when action is triggered
        """
        self.action_mappings[action_name] = callback
    
    def unregister_action(self, action_name: str) -> bool:
        """Unregister a game action.
        
        Args:
            action_name: Name of action to remove
            
        Returns:
            True if action was found and removed, False otherwise
        """
        if action_name in self.action_mappings:
            del self.action_mappings[action_name]
            return True
        return False
    
    def handle_action(self, action_name: str, parameters: Optional[Dict[str, Any]] = None, 
                     source: str = "unknown") -> bool:
        """Execute a game action from UI interaction.
        
        Args:
            action_name: Name of the action to execute
            parameters: Optional parameters for the action
            source: UI element that triggered the action
            
        Returns:
            True if action was executed successfully, False otherwise
        """
        if parameters is None:
            parameters = {}
            
        # Find the action mapping
        callback = self.action_mappings.get(action_name)
        if not callback:
            print(f"Warning: Unknown action '{action_name}' from {source}")
            return False
        
        # Create action object for history
        action = GameAction(
            action_type=self._determine_action_type(action_name),
            action_name=action_name,
            parameters=parameters,
            source=source
        )
        
        try:
            # Execute the action
            result = callback(parameters)
            
            # Add to history if successful
            if result:
                self._add_to_history(action)
            
            return result
            
        except Exception as e:
            print(f"Error executing action '{action_name}': {e}")
            return False
    
    def _determine_action_type(self, action_name: str) -> ActionType:
        """Determine the type of action based on its name.
        
        Args:
            action_name: Name of the action
            
        Returns:
            ActionType enum value
        """
        if action_name.startswith("navigate"):
            return ActionType.NAVIGATION
        elif action_name.startswith("train") or action_name.startswith("rest") or action_name.startswith("retire") or action_name.startswith("select"):
            return ActionType.TURTLE_ACTION
        elif action_name.startswith("buy") or action_name.startswith("shop") or action_name.startswith("refresh"):
            return ActionType.SHOP_ACTION
        elif action_name.startswith("race"):
            return ActionType.RACE_ACTION
        elif action_name.startswith("breeding"):
            return ActionType.BREEDING_ACTION
        elif action_name.startswith("setting"):
            return ActionType.SETTINGS_ACTION
        elif action_name.startswith("save") or action_name.startswith("load") or action_name.startswith("exit") or action_name.startswith("toggle"):
            return ActionType.SYSTEM_ACTION
        else:
            return ActionType.GAME_STATE
    
    def _add_to_history(self, action: GameAction) -> None:
        """Add action to history buffer.
        
        Args:
            action: Action to add to history
        """
        self.action_history.append(action)
        
        # Maintain history size
        if len(self.action_history) > self.max_history:
            self.action_history.pop(0)
    
    def get_action_history(self, limit: Optional[int] = None) -> List[GameAction]:
        """Get action history.
        
        Args:
            limit: Maximum number of actions to return
            
        Returns:
            List of recent actions
        """
        if limit is not None:
            return self.action_history[-limit:]
        return self.action_history.copy()
    
    def clear_history(self) -> None:
        """Clear action history."""
        self.action_history.clear()
    
    # Navigation action implementations
    def _navigate_to_menu(self, parameters: Dict[str, Any]) -> bool:
        """Navigate to main menu."""
        self.game_state.state = "menu"
        self.game_state._clear_temporary_opponents()
        return True
    
    def _navigate_to_roster(self, parameters: Dict[str, Any]) -> bool:
        """Navigate to roster screen."""
        self.game_state.state_handler.transition_to_roster()
        return True
    
    def _navigate_to_shop(self, parameters: Dict[str, Any]) -> bool:
        """Navigate to shop screen."""
        self.game_state.state_handler.transition_to_shop()
        return True
    
    def _navigate_to_breeding(self, parameters: Dict[str, Any]) -> bool:
        """Navigate to breeding screen."""
        self.game_state.state_handler.transition_to_breeding()
        return True
    
    def _navigate_to_race(self, parameters: Dict[str, Any]) -> bool:
        """Navigate to race screen."""
        self.game_state.state_handler.transition_to_race()
        return True
    
    def _navigate_to_profile(self, parameters: Dict[str, Any]) -> bool:
        """Navigate to profile screen."""
        self.game_state.state = "profile"
        return True
    
    def _navigate_to_voting(self, parameters: Dict[str, Any]) -> bool:
        """Navigate to voting screen."""
        self.game_state.state = "voting"
        return True
    
    # Turtle action implementations
    def _train_turtle(self, parameters: Dict[str, Any]) -> bool:
        """Train a turtle."""
        turtle_index = parameters.get("turtle_index", 0)
        self.game_state.roster_manager.train_turtle(turtle_index)
        return True
    
    def _rest_turtle(self, parameters: Dict[str, Any]) -> bool:
        """Rest a turtle."""
        turtle_index = parameters.get("turtle_index", 0)
        self.game_state.roster_manager.rest_turtle(turtle_index)
        return True
    
    def _retire_turtle(self, parameters: Dict[str, Any]) -> bool:
        """Retire a turtle."""
        turtle_index = parameters.get("turtle_index", 0)
        self.game_state.roster_manager.retire_turtle(turtle_index)
        return True
    
    def _select_turtle(self, parameters: Dict[str, Any]) -> bool:
        """Select a turtle."""
        turtle_index = parameters.get("turtle_index", 0)
        self.game_state.active_racer_index = turtle_index
        return True
    
    # Shop action implementations
    def _buy_turtle(self, parameters: Dict[str, Any]) -> bool:
        """Buy a turtle from shop."""
        turtle_index = parameters.get("turtle_index", 0)
        self.game_state.shop_manager.buy_turtle(turtle_index)
        return True
    
    def _refresh_shop(self, parameters: Dict[str, Any]) -> bool:
        """Refresh shop inventory."""
        self.game_state.shop_manager.refresh_stock()
        return True
    
    # Race action implementations
    def _start_race(self, parameters: Dict[str, Any]) -> bool:
        """Start a race."""
        # This would trigger the race manager to start a race
        return True
    
    def _set_race_speed(self, parameters: Dict[str, Any]) -> bool:
        """Set race speed multiplier."""
        speed = parameters.get("speed", 1)
        self.game_state.race_speed_multiplier = speed
        return True
    
    def _select_racer(self, parameters: Dict[str, Any]) -> bool:
        """Select a turtle for racing."""
        turtle_index = parameters.get("turtle_index", 0)
        self.game_state.active_racer_index = turtle_index
        return True
    
    # Breeding action implementations
    def _select_breeding_parent(self, parameters: Dict[str, Any]) -> bool:
        """Select a turtle for breeding."""
        turtle = parameters.get("turtle")
        if turtle:
            self.game_state.breeding_manager._toggle_parent_by_turtle(turtle)
        return True
    
    def _attempt_breeding(self, parameters: Dict[str, Any]) -> bool:
        """Attempt breeding between selected parents."""
        if self.game_state.breeding_manager.breed():
            self.game_state.state = "menu"
        return True
    
    def _clear_breeding_selection(self, parameters: Dict[str, Any]) -> bool:
        """Clear breeding parent selection."""
        self.game_state.breeding_parents = []
        return True
    
    # Settings action implementations
    def _toggle_settings(self, parameters: Dict[str, Any]) -> bool:
        """Toggle settings panel."""
        self.game_state.settings_manager.toggle_settings()
        return True
    
    def _update_setting(self, parameters: Dict[str, Any]) -> bool:
        """Update a setting value."""
        key = parameters.get("key")
        value = parameters.get("value")
        if key is not None and value is not None:
            self.game_state.settings_manager.set_setting(key, value)
        return True
    
    def _reset_settings(self, parameters: Dict[str, Any]) -> bool:
        """Reset settings to defaults."""
        self.game_state.settings_manager.reset_to_defaults()
        return True
    
    # System action implementations
    def _save_game(self, parameters: Dict[str, Any]) -> bool:
        """Save the game."""
        self.game_state.auto_save("manual")
        return True
    
    def _load_game(self, parameters: Dict[str, Any]) -> bool:
        """Load the game."""
        # This would trigger the game state manager to load
        return True
    
    def _exit_game(self, parameters: Dict[str, Any]) -> bool:
        """Exit the game."""
        self.game_state.save_on_exit()
        pygame.quit()
        exit()
    
    def _toggle_ui(self, parameters: Dict[str, Any]) -> bool:
        """Toggle UI visibility."""
        if hasattr(self.game_state, 'ui_manager'):
            self.game_state.ui_manager.toggle_visibility()
        return True
    
    def get_registered_actions(self) -> List[str]:
        """Get list of registered action names.
        
        Returns:
            List of action names
        """
        return list(self.action_mappings.keys())
    
    def print_action_info(self) -> None:
        """Print debugging information about registered actions."""
        print("=== Game Input Adapter Actions ===")
        print(f"Registered actions: {len(self.action_mappings)}")
        for action_name in sorted(self.action_mappings.keys()):
            action_type = self._determine_action_type(action_name)
            print(f"  - {action_name} (Type: {action_type.value})")
        print("=" * 40)
