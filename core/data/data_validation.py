"""
Data Validation for TurboShells

This module contains only validation logic for data structures,
following Single Responsibility Principle.
"""

import json
from typing import Dict, List, Any, Optional, Tuple

from .data_structures import GameData, TurtleData, PlayerPreferences


# ============================================================================
# JSON SCHEMAS
# ============================================================================

GAME_DATA_SCHEMA = {
    "type": "object",
    "required": ["version", "timestamp", "player_id", "game_state", "economy", "roster"],
    "properties": {
        "version": {
            "type": "string",
            "pattern": r"^\d+\.\d+\.\d+$"
        },
        "timestamp": {
            "type": "string",
            "format": "date-time"
        },
        "player_id": {
            "type": "string",
            "pattern": r"^player_\d+$"
        },
        "game_state": {
            "type": "object",
            "required": ["money", "current_phase", "unlocked_features", "tutorial_progress", "session_stats"],
            "properties": {
                "money": {
                    "type": "integer",
                    "minimum": 0
                },
                "current_phase": {
                    "type": "string",
                    "enum": ["MENU", "ROSTER", "RACE", "SHOP", "BREEDING", "VOTING"]
                },
                "unlocked_features": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "tutorial_progress": {
                    "type": "object",
                    "patternProperties": {
                        ".*": {"type": "boolean"}
                    }
                },
                "session_stats": {
                    "type": "object",
                    "required": ["total_playtime_minutes", "races_completed", "turtles_bred", "votes_cast"],
                    "properties": {
                        "total_playtime_minutes": {"type": "integer", "minimum": 0},
                        "races_completed": {"type": "integer", "minimum": 0},
                        "turtles_bred": {"type": "integer", "minimum": 0},
                        "votes_cast": {"type": "integer", "minimum": 0}
                    }
                }
            }
        },
        "economy": {
            "type": "object",
            "required": ["total_earned", "total_spent", "transaction_history"],
            "properties": {
                "total_earned": {"type": "integer", "minimum": 0},
                "total_spent": {"type": "integer", "minimum": 0},
                "transaction_history": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["id", "timestamp", "type", "amount", "source"],
                        "properties": {
                            "id": {"type": "string"},
                            "timestamp": {"type": "string", "format": "date-time"},
                            "type": {"type": "string", "enum": ["earnings", "purchase", "breeding_cost"]},
                            "amount": {"type": "integer"},
                            "source": {"type": "string"},
                            "details": {"type": "object"}
                        }
                    }
                }
            }
        },
        "roster": {
            "type": "object",
            "required": ["active_slots", "active_turtles", "retired_turtles", "max_retired"],
            "properties": {
                "active_slots": {"type": "integer", "minimum": 1, "maximum": 3},
                "active_turtles": {
                    "type": "array",
                    "items": {"type": "string", "pattern": r"^turtle_\d+$"}
                },
                "retired_turtles": {
                    "type": "array",
                    "items": {"type": "string", "pattern": r"^turtle_\d+$"}
                },
                "max_retired": {"type": "integer", "minimum": 1}
            }
        },
        "last_sessions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["timestamp", "duration_minutes", "activities"],
                "properties": {
                    "timestamp": {"type": "string", "format": "date-time"},
                    "duration_minutes": {"type": "integer", "minimum": 0},
                    "activities": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        }
    }
}


TURTLE_DATA_SCHEMA = {
    "type": "object",
    "required": ["turtle_id", "name", "generation", "created_timestamp", "genetics", "stats", "performance"],
    "properties": {
        "turtle_id": {
            "type": "string",
            "pattern": r"^turtle_\d{3}$"
        },
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 50
        },
        "generation": {
            "type": "integer",
            "minimum": 0
        },
        "created_timestamp": {
            "type": "string",
            "format": "date-time"
        },
        "parents": {
            "type": "object",
            "required": ["mother_id", "father_id"],
            "properties": {
                "mother_id": {"type": "string", "pattern": r"^turtle_\d+$"},
                "father_id": {"type": "string", "pattern": r"^turtle_\d+$"}
            }
        },
        "genetics": {
            "type": "object",
            "required": ["shell_pattern", "shell_color", "pattern_color", "limb_shape", "limb_length", "head_size", "eye_color", "skin_texture"],
            "patternProperties": {
                "^(shell_pattern|shell_color|pattern_color|limb_shape|limb_length|head_size|eye_color|skin_texture)$": {
                    "type": "object",
                    "required": ["value", "dominance", "mutation_source"],
                    "properties": {
                        "value": {},
                        "dominance": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0
                        },
                        "mutation_source": {
                            "type": "string",
                            "enum": ["inherited", "mutation", "random"]
                        },
                        "parent_contribution": {
                            "type": "object",
                            "required": ["mother", "father"],
                            "properties": {
                                "mother": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                "father": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                            }
                        },
                        "mutation_details": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "similarity_to_parents": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                            }
                        }
                    }
                }
            }
        },
        "stats": {
            "type": "object",
            "required": ["speed", "energy", "recovery", "swim", "climb", "base_stats", "genetic_modifiers"],
            "properties": {
                "speed": {"type": "number", "minimum": 0.0, "maximum": 20.0},
                "energy": {"type": "number", "minimum": 0.0, "maximum": 20.0},
                "recovery": {"type": "number", "minimum": 0.0, "maximum": 20.0},
                "swim": {"type": "number", "minimum": 0.0, "maximum": 20.0},
                "climb": {"type": "number", "minimum": 0.0, "maximum": 20.0},
                "base_stats": {
                    "type": "object",
                    "required": ["speed", "energy", "recovery", "swim", "climb"],
                    "patternProperties": {
                        ".*": {"type": "number", "minimum": 0.0, "maximum": 20.0}
                    }
                },
                "genetic_modifiers": {
                    "type": "object",
                    "required": ["speed", "energy", "recovery", "swim", "climb"],
                    "patternProperties": {
                        ".*": {"type": "number"}
                    }
                }
            }
        },
        "performance": {
            "type": "object",
            "required": ["race_history", "total_races", "wins", "average_position", "total_earnings"],
            "properties": {
                "race_history": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["race_id", "timestamp", "position", "earnings", "terrain_performance"],
                        "properties": {
                            "race_id": {"type": "string"},
                            "timestamp": {"type": "string", "format": "date-time"},
                            "position": {"type": "integer", "minimum": 1},
                            "earnings": {"type": "integer", "minimum": 0},
                            "terrain_performance": {
                                "type": "object",
                                "required": ["grass", "water", "rock"],
                                "properties": {
                                    "grass": {"type": "number", "minimum": 0.0, "maximum": 20.0},
                                    "water": {"type": "number", "minimum": 0.0, "maximum": 20.0},
                                    "rock": {"type": "number", "minimum": 0.0, "maximum": 20.0}
                                }
                            }
                        }
                    }
                },
                "total_races": {"type": "integer", "minimum": 0},
                "wins": {"type": "integer", "minimum": 0},
                "average_position": {"type": "number", "minimum": 1.0},
                "total_earnings": {"type": "integer", "minimum": 0}
            }
        }
    }
}


PREFERENCE_DATA_SCHEMA = {
    "type": "object",
    "required": ["version", "player_id", "last_updated", "voting_history", "preference_profile", "genetic_influence"],
    "properties": {
        "version": {
            "type": "string",
            "pattern": r"^\d+\.\d+\.\d+$"
        },
        "player_id": {
            "type": "string",
            "pattern": r"^player_\d+$"
        },
        "last_updated": {
            "type": "string",
            "format": "date-time"
        },
        "voting_history": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["date", "design_id", "ratings", "rewards_earned", "time_spent_minutes"],
                "properties": {
                    "date": {"type": "string", "format": "date"},
                    "design_id": {"type": "string"},
                    "ratings": {
                        "type": "object",
                        "patternProperties": {
                            ".*": {"type": "integer", "minimum": 1, "maximum": 5}
                        }
                    },
                    "rewards_earned": {"type": "integer", "minimum": 0},
                    "time_spent_minutes": {"type": "integer", "minimum": 0}
                }
            }
        },
        "preference_profile": {
            "type": "object",
            "required": ["trait_weights", "color_preferences", "pattern_preferences", "rating_behavior"],
            "properties": {
                "trait_weights": {
                    "type": "object",
                    "required": ["shell_pattern", "shell_color", "pattern_color", "limb_shape", "limb_length", "head_size", "eye_color", "skin_texture"],
                    "patternProperties": {
                        ".*": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                    }
                },
                "color_preferences": {
                    "type": "object",
                    "required": ["favorite_colors", "avoided_colors", "color_harmony_score"],
                    "properties": {
                        "favorite_colors": {
                            "type": "array",
                            "items": {"type": "string", "pattern": r"^#[0-9A-Fa-f]{6}$"}
                        },
                        "avoided_colors": {
                            "type": "array",
                            "items": {"type": "string", "pattern": r"^#[0-9A-Fa-f]{6}$"}
                        },
                        "color_harmony_score": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                    }
                },
                "pattern_preferences": {
                    "type": "object",
                    "required": ["favorite_patterns", "avoided_patterns", "complexity_preference"],
                    "properties": {
                        "favorite_patterns": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["hex", "spots", "stripes", "rings"]}
                        },
                        "avoided_patterns": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["hex", "spots", "stripes", "rings"]}
                        },
                        "complexity_preference": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                    }
                },
                "rating_behavior": {
                    "type": "object",
                    "required": ["average_rating", "rating_variance", "tendency_to_extreme", "consistent_rater"],
                    "properties": {
                        "average_rating": {"type": "number", "minimum": 1.0, "maximum": 5.0},
                        "rating_variance": {"type": "number", "minimum": 0.0},
                        "tendency_to_extreme": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "consistent_rater": {"type": "boolean"}
                    }
                }
            }
        },
        "genetic_influence": {
            "type": "object",
            "required": ["total_influence_points", "trait_influence", "influence_decay"],
            "properties": {
                "total_influence_points": {"type": "integer", "minimum": 0},
                "trait_influence": {
                    "type": "object",
                    "required": ["shell_pattern", "shell_color", "pattern_color", "limb_shape", "limb_length", "head_size", "eye_color", "skin_texture"],
                    "patternProperties": {
                        ".*": {"type": "number", "minimum": 0.0}
                    }
                },
                "influence_decay": {
                    "type": "object",
                    "required": ["daily_decay_rate", "last_decay_date", "total_decayed"],
                    "properties": {
                        "daily_decay_rate": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "last_decay_date": {"type": "string", "format": "date"},
                        "total_decayed": {"type": "number", "minimum": 0.0}
                    }
                }
            }
        }
    }
}


# ============================================================================
# VALIDATION CLASSES
# ============================================================================

class DataValidator:
    """Validation utilities for all data types"""
    
    def __init__(self):
        self.game_schema = GAME_DATA_SCHEMA
        self.turtle_schema = TURTLE_DATA_SCHEMA
        self.preference_schema = PREFERENCE_DATA_SCHEMA
    
    def validate_game_data(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate game data against schema"""
        try:
            jsonschema.validate(data, self.game_schema)
            return True, None
        except jsonschema.ValidationError as e:
            return False, str(e)
    
    def validate_turtle_data(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate turtle data against schema"""
        try:
            jsonschema.validate(data, self.turtle_schema)
            return True, None
        except jsonschema.ValidationError as e:
            return False, str(e)
    
    def validate_preference_data(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate preference data against schema"""
        try:
            jsonschema.validate(data, self.preference_schema)
            return True, None
        except jsonschema.ValidationError as e:
            return False, str(e)
    
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
