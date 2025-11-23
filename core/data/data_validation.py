"""
Data Validation for TurboShells

This module contains only validation logic for data structures,
following Single Responsibility Principle.
"""

import json
from typing import Dict, List, Any, Optional, Tuple

from .data_structures import GameData, TurtleData, PlayerPreferences


# ============================================================================
# SIMPLE JSON-BASED VALIDATION
# ============================================================================

class DataValidator:
    """Validates data structures using JSON serialization and basic checks"""
    
    def __init__(self):
        pass
    
    def validate_game_data(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate game data structure"""
        try:
            # Try to serialize to JSON to ensure it's valid
            json.dumps(data)
            
            # Check required fields
            required_fields = ["version", "timestamp", "player_id", "game_state", "economy", "roster"]
            for field in required_fields:
                if field not in data:
                    return False, f"Missing required field: {field}"
            
            # Basic type checks
            if not isinstance(data.get("version"), str):
                return False, "version must be a string"
            if not isinstance(data.get("player_id"), str):
                return False, "player_id must be a string"
            if not isinstance(data.get("game_state"), dict):
                return False, "game_state must be a dictionary"
            if not isinstance(data.get("economy"), dict):
                return False, "economy must be a dictionary"
            if not isinstance(data.get("roster"), dict):
                return False, "roster must be a dictionary"
            
            return True, None
            
        except (TypeError, ValueError) as e:
            return False, f"Invalid JSON data: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def validate_turtle_data(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate turtle data structure"""
        try:
            # Try to serialize to JSON to ensure it's valid
            json.dumps(data)
            
            # Check required fields
            required_fields = ["turtle_id", "name", "generation", "created_timestamp", "genetics", "stats", "performance"]
            for field in required_fields:
                if field not in data:
                    return False, f"Missing required field: {field}"
            
            # Basic type checks
            if not isinstance(data.get("turtle_id"), str):
                return False, "turtle_id must be a string"
            if not isinstance(data.get("name"), str):
                return False, "name must be a string"
            if not isinstance(data.get("generation"), int):
                return False, "generation must be an integer"
            if not isinstance(data.get("genetics"), dict):
                return False, "genetics must be a dictionary"
            if not isinstance(data.get("stats"), dict):
                return False, "stats must be a dictionary"
            if not isinstance(data.get("performance"), dict):
                return False, "performance must be a dictionary"
            
            return True, None
            
        except (TypeError, ValueError) as e:
            return False, f"Invalid JSON data: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def validate_preference_data(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate preference data structure"""
        try:
            # Try to serialize to JSON to ensure it's valid
            json.dumps(data)
            
            # Check required fields
            required_fields = ["version", "player_id", "last_updated", "voting_history", "preference_profile", "genetic_influence"]
            for field in required_fields:
                if field not in data:
                    return False, f"Missing required field: {field}"
            
            # Basic type checks
            if not isinstance(data.get("version"), str):
                return False, "version must be a string"
            if not isinstance(data.get("player_id"), str):
                return False, "player_id must be a string"
            if not isinstance(data.get("voting_history"), list):
                return False, "voting_history must be a list"
            if not isinstance(data.get("preference_profile"), dict):
                return False, "preference_profile must be a dictionary"
            if not isinstance(data.get("genetic_influence"), dict):
                return False, "genetic_influence must be a dictionary"
            
            return True, None
            
        except (TypeError, ValueError) as e:
            return False, f"Invalid JSON data: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def validate_all(self, game_data: Dict[str, Any], turtles: List[Dict[str, Any]], 
                    preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Validate all data types"""
        results = {}
        results['game'] = self.validate_game_data(game_data)
        results['turtles'] = [(self.validate_turtle_data(turtle), turtle.get('turtle_id', 'unknown')) for turtle in turtles]
        results['preferences'] = self.validate_preference_data(preferences)
        return results


# ============================================================================
# GLOBAL VALIDATOR INSTANCE
# ============================================================================

validator = DataValidator()
