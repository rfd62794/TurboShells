"""
Data Formats and Validation Schemas for TurboShells

This module defines the data structures and validation schemas for Game Data,
Gene Data, and Gene Preference data as specified in the technical design.
"""

import json
import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import jsonschema


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class TransactionData:
    """Individual transaction record"""
    id: str
    timestamp: str
    type: str  # earnings, purchase, breeding_cost
    amount: int
    source: str  # race, shop, voting, breeding
    details: Dict[str, Any]


@dataclass
class EconomicData:
    """Economic state and transaction history"""
    total_earned: int
    total_spent: int
    transaction_history: List[TransactionData]


@dataclass
class SessionStats:
    """Player session statistics"""
    total_playtime_minutes: int
    races_completed: int
    turtles_bred: int
    votes_cast: int


@dataclass
class GameStateData:
    """Core game state information"""
    money: int
    current_phase: str
    unlocked_features: List[str]
    tutorial_progress: Dict[str, bool]
    session_stats: SessionStats


@dataclass
class RosterData:
    """Roster management data"""
    active_slots: int
    active_turtles: List[str]
    retired_turtles: List[str]
    max_retired: int


@dataclass
class LastSession:
    """Information about last game session"""
    timestamp: str
    duration_minutes: int
    activities: List[str]


@dataclass
class GameData:
    """Complete game data structure"""
    version: str
    timestamp: str
    player_id: str
    game_state: GameStateData
    economy: EconomicData
    roster: RosterData
    last_sessions: List[LastSession]


@dataclass
class ParentContribution:
    """Parent contribution to genetic traits"""
    mother: float
    father: float


@dataclass
class MutationDetails:
    """Details about mutations"""
    type: str
    similarity_to_parents: Optional[float] = None


@dataclass
class GeneTrait:
    """Individual genetic trait"""
    value: Union[str, float]
    dominance: float
    mutation_source: str  # inherited, mutation, random
    parent_contribution: Optional[ParentContribution] = None
    mutation_details: Optional[MutationDetails] = None


@dataclass
class BaseStats:
    """Base stats before genetic modifiers"""
    speed: float
    energy: float
    recovery: float
    swim: float
    climb: float


@dataclass
class GeneticModifiers:
    """Stat modifiers from genetics"""
    speed: float
    energy: float
    recovery: float
    swim: float
    climb: float


@dataclass
class TurtleStats:
    """Complete turtle statistics"""
    speed: float
    energy: float
    recovery: float
    swim: float
    climb: float
    base_stats: BaseStats
    genetic_modifiers: GeneticModifiers


@dataclass
class TerrainPerformance:
    """Performance on different terrain types"""
    grass: float
    water: float
    rock: float


@dataclass
class RaceResult:
    """Individual race result"""
    race_id: str
    timestamp: str
    position: int
    earnings: int
    terrain_performance: TerrainPerformance


@dataclass
class TurtlePerformance:
    """Turtle performance history"""
    race_history: List[RaceResult]
    total_races: int
    wins: int
    average_position: float
    total_earnings: int


@dataclass
class TurtleParents:
    """Parent information for breeding"""
    mother_id: str
    father_id: str


@dataclass
class TurtleData:
    """Complete turtle data structure"""
    turtle_id: str
    name: str
    generation: int
    created_timestamp: str
    parents: Optional[TurtleParents]
    genetics: Dict[str, GeneTrait]
    stats: TurtleStats
    performance: TurtlePerformance


@dataclass
class TraitFrequencies:
    """Frequency distribution for genetic traits"""
    hex: float
    spots: float
    stripes: float
    rings: float


@dataclass
class DominantTraits:
    """Currently dominant traits in gene pool"""
    shell_pattern: str
    limb_shape: str
    pattern_color: str


@dataclass
class MutationRates:
    """Current mutation rates"""
    point_mutation: float
    adaptive_mutation: float
    pattern_mutation: float


@dataclass
class GenePoolData:
    """Gene pool state and statistics"""
    version: str
    last_updated: str
    trait_frequencies: Dict[str, Union[TraitFrequencies, Dict[str, Any]]]
    dominant_traits: DominantTraits
    mutation_rates: MutationRates


@dataclass
class VotingRecord:
    """Individual voting record"""
    date: str
    design_id: str
    ratings: Dict[str, int]
    rewards_earned: int
    time_spent_minutes: int


@dataclass
class TraitWeights:
    """Player preference weights for traits"""
    shell_pattern: float
    shell_color: float
    pattern_color: float
    limb_shape: float
    limb_length: float
    head_size: float
    eye_color: float
    skin_texture: float


@dataclass
class ColorPreferences:
    """Player color preferences"""
    favorite_colors: List[str]
    avoided_colors: List[str]
    color_harmony_score: float


@dataclass
class PatternPreferences:
    """Player pattern preferences"""
    favorite_patterns: List[str]
    avoided_patterns: List[str]
    complexity_preference: float


@dataclass
class RatingBehavior:
    """Player rating behavior analysis"""
    average_rating: float
    rating_variance: float
    tendency_to_extreme: float
    consistent_rater: bool


@dataclass
class PreferenceProfile:
    """Complete player preference profile"""
    trait_weights: TraitWeights
    color_preferences: ColorPreferences
    pattern_preferences: PatternPreferences
    rating_behavior: RatingBehavior


@dataclass
class TraitInfluence:
    """Genetic influence by trait"""
    shell_pattern: float
    shell_color: float
    pattern_color: float
    limb_shape: float
    limb_length: float
    head_size: float
    eye_color: float
    skin_texture: float


@dataclass
class InfluenceDecay:
    """Influence decay tracking"""
    daily_decay_rate: float
    last_decay_date: str
    total_decayed: float


@dataclass
class GeneticInfluence:
    """Player's genetic influence on gene pool"""
    total_influence_points: int
    trait_influence: TraitInfluence
    influence_decay: InfluenceDecay


@dataclass
class PlayerPreferences:
    """Complete player preference data"""
    version: str
    player_id: str
    last_updated: str
    voting_history: List[VotingRecord]
    preference_profile: PreferenceProfile
    genetic_influence: GeneticInfluence


@dataclass
class TraitAverages:
    """Community average ratings for traits"""
    shell_pattern: float
    shell_color: float
    pattern_color: float
    limb_shape: float
    limb_length: float
    head_size: float
    eye_color: float
    skin_texture: float


@dataclass
class TraitCombination:
    """Popular trait combination"""
    combination: Dict[str, Any]
    popularity_score: float
    frequency: float


@dataclass
class TrendingTraits:
    """Trending trait information"""
    rising: List[str]
    declining: List[str]
    stable: List[str]


@dataclass
class CommunityPreferences:
    """Community preference aggregates"""
    version: str
    date: str
    total_voters: int
    total_votes_cast: int
    trait_averages: TraitAverages
    popular_combinations: List[TraitCombination]
    trending_traits: TrendingTraits


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
    
    def validate_game_data(self, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate game data against schema"""
        try:
            jsonschema.validate(data, self.game_schema)
            return True, None
        except jsonschema.ValidationError as e:
            return False, str(e)
    
    def validate_turtle_data(self, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate turtle data against schema"""
        try:
            jsonschema.validate(data, self.turtle_schema)
            return True, None
        except jsonschema.ValidationError as e:
            return False, str(e)
    
    def validate_preference_data(self, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate preference data against schema"""
        try:
            jsonschema.validate(data, self.preference_schema)
            return True, None
        except jsonschema.ValidationError as e:
            return False, str(e)
    
    def validate_all(self, game_data: Dict[str, Any], turtles: List[Dict[str, Any]], 
                    preferences: Dict[str, Any]) -> Dict[str, tuple[bool, Optional[str]]]:
        """Validate all data types"""
        results = {}
        results['game'] = self.validate_game_data(game_data)
        results['turtles'] = [(self.validate_turtle_data(turtle), turtle.get('turtle_id', 'unknown')) for turtle in turtles]
        results['preferences'] = self.validate_preference_data(preferences)
        return results


# ============================================================================
# SERIALIZATION UTILITIES
# ============================================================================

class DataSerializer:
    """Serialization and deserialization utilities"""
    
    @staticmethod
    def serialize_game_data(game_data: GameData) -> str:
        """Serialize game data to JSON"""
        return json.dumps(asdict(game_data), indent=2, default=str)
    
    @staticmethod
    def deserialize_game_data(json_str: str) -> GameData:
        """Deserialize game data from JSON"""
        data = json.loads(json_str)
        return GameData(**data)
    
    @staticmethod
    def serialize_turtle_data(turtle_data: TurtleData) -> str:
        """Serialize turtle data to JSON"""
        return json.dumps(asdict(turtle_data), indent=2, default=str)
    
    @staticmethod
    def deserialize_turtle_data(json_str: str) -> TurtleData:
        """Deserialize turtle data from JSON"""
        data = json.loads(json_str)
        return TurtleData(**data)
    
    @staticmethod
    def serialize_preference_data(pref_data: PlayerPreferences) -> str:
        """Serialize preference data to JSON"""
        return json.dumps(asdict(pref_data), indent=2, default=str)
    
    @staticmethod
    def deserialize_preference_data(json_str: str) -> PlayerPreferences:
        """Deserialize preference data from JSON"""
        data = json.loads(json_str)
        return PlayerPreferences(**data)


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_default_game_data(player_id: str) -> GameData:
    """Create default game data structure"""
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    return GameData(
        version="2.2.0",
        timestamp=now,
        player_id=player_id,
        game_state=GameStateData(
            money=1000,
            current_phase="MENU",
            unlocked_features=["roster", "racing"],
            tutorial_progress={
                "roster_intro": False,
                "racing_basics": False,
                "breeding_intro": False,
                "voting_system": False
            },
            session_stats=SessionStats(
                total_playtime_minutes=0,
                races_completed=0,
                turtles_bred=0,
                votes_cast=0
            )
        ),
        economy=EconomicData(
            total_earned=0,
            total_spent=0,
            transaction_history=[]
        ),
        roster=RosterData(
            active_slots=3,
            active_turtles=[],
            retired_turtles=[],
            max_retired=20
        ),
        last_sessions=[]
    )


def create_default_turtle_data(turtle_id: str, name: str) -> TurtleData:
    """Create default turtle data structure"""
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    return TurtleData(
        turtle_id=turtle_id,
        name=name,
        generation=0,
        created_timestamp=now,
        parents=None,
        genetics={
            "shell_pattern": GeneTrait("hex", 1.0, "random"),
            "shell_color": GeneTrait("#4A90E2", 1.0, "random"),
            "pattern_color": GeneTrait("#E74C3C", 1.0, "random"),
            "limb_shape": GeneTrait("flippers", 1.0, "random"),
            "limb_length": GeneTrait(1.0, 1.0, "random"),
            "head_size": GeneTrait(1.0, 1.0, "random"),
            "eye_color": GeneTrait("#2ECC71", 1.0, "random"),
            "skin_texture": GeneTrait("smooth", 1.0, "random")
        },
        stats=TurtleStats(
            speed=7.0,
            energy=7.0,
            recovery=7.0,
            swim=7.0,
            climb=7.0,
            base_stats=BaseStats(7.0, 7.0, 7.0, 7.0, 7.0),
            genetic_modifiers=GeneticModifiers(0.0, 0.0, 0.0, 0.0, 0.0)
        ),
        performance=TurtlePerformance(
            race_history=[],
            total_races=0,
            wins=0,
            average_position=0.0,
            total_earnings=0
        )
    )


def create_default_preference_data(player_id: str) -> PlayerPreferences:
    """Create default preference data structure"""
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    return PlayerPreferences(
        version="2.2.0",
        player_id=player_id,
        last_updated=now,
        voting_history=[],
        preference_profile=PreferenceProfile(
            trait_weights=TraitWeights(
                shell_pattern=0.125,
                shell_color=0.125,
                pattern_color=0.125,
                limb_shape=0.125,
                limb_length=0.125,
                head_size=0.125,
                eye_color=0.125,
                skin_texture=0.125
            ),
            color_preferences=ColorPreferences(
                favorite_colors=["#4A90E2", "#E74C3C", "#2ECC71"],
                avoided_colors=[],
                color_harmony_score=0.5
            ),
            pattern_preferences=PatternPreferences(
                favorite_patterns=[],
                avoided_patterns=[],
                complexity_preference=0.5
            ),
            rating_behavior=RatingBehavior(
                average_rating=3.0,
                rating_variance=1.0,
                tendency_to_extreme=0.1,
                consistent_rater=False
            )
        ),
        genetic_influence=GeneticInfluence(
            total_influence_points=0,
            trait_influence=TraitInfluence(
                shell_pattern=0.0,
                shell_color=0.0,
                pattern_color=0.0,
                limb_shape=0.0,
                limb_length=0.0,
                head_size=0.0,
                eye_color=0.0,
                skin_texture=0.0
            ),
            influence_decay=InfluenceDecay(
                daily_decay_rate=0.05,
                last_decay_date=now.split('T')[0],
                total_decayed=0.0
            )
        )
    )


# ============================================================================
# MAIN VALIDATOR INSTANCE
# ============================================================================

validator = DataValidator()
