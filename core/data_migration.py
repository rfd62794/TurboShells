"""
Data Migration Utilities for TurboShells

Handles version compatibility and data transformation between save file versions.
Implements the migration strategies from the technical design.
"""

import json
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime, timezone
import logging

from core.data_structures import GameData, TurtleData, PlayerPreferences


class DataMigrator:
    """Handles data migration between different versions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Define migration rules
        self.migration_rules = {
            "2.1.0_to_2.2.0": self._migrate_2_1_0_to_2_2_0,
            "2.0.0_to_2.1.0": self._migrate_2_0_0_to_2_1_0,
            "1.0.0_to_2.0.0": self._migrate_1_0_0_to_2_0_0,
        }
        
        # Compatibility matrix
        self.compatibility_matrix = {
            "2.2.0": {
                "can_load": ["2.1.0", "2.0.0", "1.0.0"],
                "migration_required": ["2.1.0", "2.0.0", "1.0.0"],
                "deprecated_fields": {
                    "turtle.stats.speed_rating": "Replaced with turtle.stats.speed",
                    "game_state.current_screen": "Replaced with game_state.current_phase"
                }
            },
            "2.1.0": {
                "can_load": ["2.0.0", "1.0.0"],
                "migration_required": ["2.0.0", "1.0.0"],
                "deprecated_fields": {
                    "turtle.stats.speed_rating": "Replaced with turtle.stats.speed"
                }
            },
            "2.0.0": {
                "can_load": ["1.0.0"],
                "migration_required": ["1.0.0"],
                "deprecated_fields": {}
            }
        }
    
    def get_migration_path(self, from_version: str, to_version: str) -> List[Callable]:
        """Get the migration path from one version to another"""
        if from_version == to_version:
            return []
        
        # Direct migration available
        migration_key = f"{from_version}_to_{to_version}"
        if migration_key in self.migration_rules:
            return [self.migration_rules[migration_key]]
        
        # Build migration path step by step
        path = []
        current_version = from_version
        
        while current_version != to_version:
            next_migration = self._find_next_migration(current_version, to_version)
            if not next_migration:
                raise ValueError(f"No migration path from {from_version} to {to_version}")
            
            migration_key = f"{current_version}_to_{next_migration}"
            path.append(self.migration_rules[migration_key])
            current_version = next_migration
        
        return path
    
    def _find_next_migration(self, from_version: str, to_version: str) -> Optional[str]:
        """Find the next version in migration path"""
        # Simple version comparison logic
        from_parts = [int(x) for x in from_version.split('.')]
        to_parts = [int(x) for x in to_version.split('.')]
        
        # Try to increment version components
        for i in range(len(from_parts)):
            if from_parts[i] < to_parts[i]:
                # Increment this component and zero out the rest
                next_parts = from_parts.copy()
                next_parts[i] += 1
                for j in range(i + 1, len(next_parts)):
                    next_parts[j] = 0
                
                next_version = '.'.join(str(x) for x in next_parts)
                if f"{from_version}_to_{next_version}" in self.migration_rules:
                    return next_version
        
        return None
    
    def migrate_data(self, save_data: Dict[str, Any], target_version: str) -> Dict[str, Any]:
        """Migrate save data to target version"""
        current_version = save_data.get("version", "1.0.0")
        
        if current_version == target_version:
            return save_data
        
        self.logger.info(f"Migrating data from {current_version} to {target_version}")
        
        try:
            migration_path = self.get_migration_path(current_version, target_version)
            
            for migration_func in migration_path:
                save_data = migration_func(save_data)
            
            # Update version
            save_data["version"] = target_version
            save_data["migration_timestamp"] = datetime.now(timezone.utc).isoformat()
            
            self.logger.info(f"Successfully migrated to {target_version}")
            return save_data
            
        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            raise
    
    def _migrate_2_1_0_to_2_2_0(self, save_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from version 2.1.0 to 2.2.0"""
        self.logger.info("Applying 2.1.0 to 2.2.0 migration")
        
        # Add skin_texture trait to all turtles
        turtles = save_data.get("turtles", [])
        for turtle in turtles:
            genetics = turtle.get("genetics", {})
            
            if "skin_texture" not in genetics:
                genetics["skin_texture"] = {
                    "value": "smooth",
                    "dominance": 0.5,
                    "mutation_source": "random"
                }
                turtle["genetics"] = genetics
        
        # Update game state structure
        game_state = save_data.get("game_data", {}).get("game_state", {})
        
        # Add new fields if missing
        if "unlocked_features" not in game_state:
            game_state["unlocked_features"] = ["roster", "racing"]
        
        if "session_stats" not in game_state:
            game_state["session_stats"] = {
                "total_playtime_minutes": 0,
                "races_completed": 0,
                "turtles_bred": 0,
                "votes_cast": 0
            }
        
        # Update preference data structure
        preferences = save_data.get("preferences", {})
        
        if "preference_profile" not in preferences:
            # Create default preference profile
            preferences["preference_profile"] = {
                "trait_weights": {
                    "shell_pattern": 0.125,
                    "shell_color": 0.125,
                    "pattern_color": 0.125,
                    "limb_shape": 0.125,
                    "limb_length": 0.125,
                    "head_size": 0.125,
                    "eye_color": 0.125,
                    "skin_texture": 0.125
                },
                "color_preferences": {
                    "favorite_colors": ["#4A90E2", "#E74C3C", "#2ECC71"],
                    "avoided_colors": [],
                    "color_harmony_score": 0.5
                },
                "pattern_preferences": {
                    "favorite_patterns": [],
                    "avoided_patterns": [],
                    "complexity_preference": 0.5
                },
                "rating_behavior": {
                    "average_rating": 3.0,
                    "rating_variance": 1.0,
                    "tendency_to_extreme": 0.1,
                    "consistent_rater": False
                }
            }
        
        # Add genetic influence if missing
        if "genetic_influence" not in preferences:
            preferences["genetic_influence"] = {
                "total_influence_points": 0,
                "trait_influence": {
                    "shell_pattern": 0.0,
                    "shell_color": 0.0,
                    "pattern_color": 0.0,
                    "limb_shape": 0.0,
                    "limb_length": 0.0,
                    "head_size": 0.0,
                    "eye_color": 0.0,
                    "skin_texture": 0.0
                },
                "influence_decay": {
                    "daily_decay_rate": 0.05,
                    "last_decay_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    "total_decayed": 0.0
                }
            }
        
        return save_data
    
    def _migrate_2_0_0_to_2_1_0(self, save_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from version 2.0.0 to 2.1.0"""
        self.logger.info("Applying 2.0.0 to 2.1.0 migration")
        
        # Rename speed_rating to speed in turtle stats
        turtles = save_data.get("turtles", [])
        for turtle in turtles:
            stats = turtle.get("stats", {})
            
            if "speed_rating" in stats:
                stats["speed"] = stats.pop("speed_rating")
            
            # Ensure base_stats and genetic_modifiers exist
            if "base_stats" not in stats:
                stats["base_stats"] = {
                    "speed": 7.0,
                    "energy": 7.0,
                    "recovery": 7.0,
                    "swim": 7.0,
                    "climb": 7.0
                }
            
            if "genetic_modifiers" not in stats:
                stats["genetic_modifiers"] = {
                    "speed": 0.0,
                    "energy": 0.0,
                    "recovery": 0.0,
                    "swim": 0.0,
                    "climb": 0.0
                }
        
        # Update game state structure
        game_state = save_data.get("game_data", {}).get("game_state", {})
        
        # Rename current_screen to current_phase
        if "current_screen" in game_state:
            game_state["current_phase"] = game_state.pop("current_screen")
        
        # Add tutorial progress if missing
        if "tutorial_progress" not in game_state:
            game_state["tutorial_progress"] = {
                "roster_intro": False,
                "racing_basics": False,
                "breeding_intro": False,
                "voting_system": False
            }
        
        return save_data
    
    def _migrate_1_0_0_to_2_0_0(self, save_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from version 1.0.0 to 2.0.0"""
        self.logger.info("Applying 1.0.0 to 2.0.0 migration")
        
        # This is a major version migration, restructure the data
        
        # Extract old data structure
        old_game_state = save_data.get("game_state", {})
        turtles = save_data.get("turtles", [])
        
        # Create new game_data structure
        new_game_data = {
            "version": "2.0.0",
            "timestamp": save_data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            "player_id": f"player_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "game_state": {
                "money": old_game_state.get("money", 1000),
                "current_phase": old_game_state.get("current_screen", "MENU"),
                "unlocked_features": ["roster", "racing"],
                "tutorial_progress": {
                    "roster_intro": False,
                    "racing_basics": False,
                    "breeding_intro": False,
                    "voting_system": False
                },
                "session_stats": {
                    "total_playtime_minutes": 0,
                    "races_completed": 0,
                    "turtles_bred": 0,
                    "votes_cast": 0
                }
            },
            "economy": {
                "total_earned": 0,
                "total_spent": 0,
                "transaction_history": []
            },
            "roster": {
                "active_slots": 3,
                "active_turtles": [t.get("id", f"turtle_{i:03d}") for i, t in enumerate(turtles[:3])],
                "retired_turtles": [t.get("id", f"turtle_{i:03d}") for i, t in enumerate(turtles[3:])],
                "max_retired": 20
            },
            "last_sessions": []
        }
        
        # Migrate turtles to new structure
        new_turtles = []
        for i, old_turtle in enumerate(turtles):
            new_turtle = {
                "turtle_id": old_turtle.get("id", f"turtle_{i:03d}"),
                "name": old_turtle.get("name", f"Turtle {i+1}"),
                "generation": old_turtle.get("generation", 0),
                "created_timestamp": datetime.now(timezone.utc).isoformat(),
                "parents": None,
                "genetics": {
                    "shell_pattern": {
                        "value": old_turtle.get("shell_pattern", "hex"),
                        "dominance": 1.0,
                        "mutation_source": "random"
                    },
                    "shell_color": {
                        "value": old_turtle.get("shell_color", "#4A90E2"),
                        "dominance": 1.0,
                        "mutation_source": "random"
                    },
                    "pattern_color": {
                        "value": old_turtle.get("pattern_color", "#E74C3C"),
                        "dominance": 1.0,
                        "mutation_source": "random"
                    },
                    "limb_shape": {
                        "value": old_turtle.get("limb_shape", "flippers"),
                        "dominance": 1.0,
                        "mutation_source": "random"
                    },
                    "limb_length": {
                        "value": old_turtle.get("limb_length", 1.0),
                        "dominance": 1.0,
                        "mutation_source": "random"
                    },
                    "head_size": {
                        "value": old_turtle.get("head_size", 1.0),
                        "dominance": 1.0,
                        "mutation_source": "random"
                    },
                    "eye_color": {
                        "value": old_turtle.get("eye_color", "#2ECC71"),
                        "dominance": 1.0,
                        "mutation_source": "random"
                    },
                    "skin_texture": {
                        "value": "smooth",
                        "dominance": 0.5,
                        "mutation_source": "random"
                    }
                },
                "stats": {
                    "speed": old_turtle.get("speed", 7.0),
                    "energy": old_turtle.get("energy", 7.0),
                    "recovery": old_turtle.get("recovery", 7.0),
                    "swim": old_turtle.get("swim", 7.0),
                    "climb": old_turtle.get("climb", 7.0),
                    "base_stats": {
                        "speed": 7.0,
                        "energy": 7.0,
                        "recovery": 7.0,
                        "swim": 7.0,
                        "climb": 7.0
                    },
                    "genetic_modifiers": {
                        "speed": old_turtle.get("speed", 7.0) - 7.0,
                        "energy": old_turtle.get("energy", 7.0) - 7.0,
                        "recovery": old_turtle.get("recovery", 7.0) - 7.0,
                        "swim": old_turtle.get("swim", 7.0) - 7.0,
                        "climb": old_turtle.get("climb", 7.0) - 7.0
                    }
                },
                "performance": {
                    "race_history": [],
                    "total_races": 0,
                    "wins": 0,
                    "average_position": 0.0,
                    "total_earnings": 0
                }
            }
            new_turtles.append(new_turtle)
        
        # Create default preferences
        new_preferences = {
            "version": "2.0.0",
            "player_id": new_game_data["player_id"],
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "voting_history": [],
            "preference_profile": {
                "trait_weights": {
                    "shell_pattern": 0.125,
                    "shell_color": 0.125,
                    "pattern_color": 0.125,
                    "limb_shape": 0.125,
                    "limb_length": 0.125,
                    "head_size": 0.125,
                    "eye_color": 0.125,
                    "skin_texture": 0.125
                },
                "color_preferences": {
                    "favorite_colors": ["#4A90E2", "#E74C3C", "#2ECC71"],
                    "avoided_colors": [],
                    "color_harmony_score": 0.5
                },
                "pattern_preferences": {
                    "favorite_patterns": [],
                    "avoided_patterns": [],
                    "complexity_preference": 0.5
                },
                "rating_behavior": {
                    "average_rating": 3.0,
                    "rating_variance": 1.0,
                    "tendency_to_extreme": 0.1,
                    "consistent_rater": False
                }
            },
            "genetic_influence": {
                "total_influence_points": 0,
                "trait_influence": {
                    "shell_pattern": 0.0,
                    "shell_color": 0.0,
                    "pattern_color": 0.0,
                    "limb_shape": 0.0,
                    "limb_length": 0.0,
                    "head_size": 0.0,
                    "eye_color": 0.0,
                    "skin_texture": 0.0
                },
                "influence_decay": {
                    "daily_decay_rate": 0.05,
                    "last_decay_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    "total_decayed": 0.0
                }
            }
        }
        
        # Return new structure
        return {
            "version": "2.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "game_data": new_game_data,
            "turtles": new_turtles,
            "preferences": new_preferences
        }
    
    def is_version_compatible(self, save_version: str, target_version: str) -> bool:
        """Check if save version is compatible with target version"""
        compatibility_info = self.compatibility_matrix.get(target_version, {})
        compatible_versions = compatibility_info.get("can_load", [])
        
        return save_version in compatible_versions
    
    def get_deprecated_fields(self, version: str) -> Dict[str, str]:
        """Get deprecated fields for a version"""
        compatibility_info = self.compatibility_matrix.get(version, {})
        return compatibility_info.get("deprecated_fields", {})
    
    def needs_migration(self, save_version: str, target_version: str) -> bool:
        """Check if save data needs migration"""
        if save_version == target_version:
            return False
        
        return self.is_version_compatible(save_version, target_version)


# ============================================================================
# GLOBAL MIGRATOR INSTANCE
# ============================================================================

data_migrator = DataMigrator()
