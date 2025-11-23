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
# PERFORMANCE OPTIMIZATION
# ============================================================================

import gzip
import hashlib
from functools import lru_cache
from typing import Dict, Any, Optional
import time


class DataCache:
    """LRU cache for frequently accessed data"""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._cache = {}
        self._access_times = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        if key in self._cache:
            self._access_times[key] = time.time()
            return self._cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set item in cache"""
        if len(self._cache) >= self.max_size:
            self._evict_oldest()
        
        self._cache[key] = value
        self._access_times[key] = time.time()
    
    def _evict_oldest(self) -> None:
        """Remove oldest item from cache"""
        if not self._access_times:
            return
        
        oldest_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        del self._cache[oldest_key]
        del self._access_times[oldest_key]
    
    def clear(self) -> None:
        """Clear cache"""
        self._cache.clear()
        self._access_times.clear()


class PerformanceOptimizer:
    """Performance optimization utilities for data operations"""
    
    def __init__(self):
        self.turtle_cache = DataCache(max_size=100)
        self.game_cache = DataCache(max_size=10)
        self.preference_cache = DataCache(max_size=50)
        
        # Compression settings
        self.compression_enabled = True
        self.compression_level = 6
        self.compression_threshold = 1024  # Only compress data larger than 1KB
    
    @lru_cache(maxsize=1000)
    def cached_validate_game_data(self, data_hash: str, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Cached game data validation"""
        validator = DataValidator()
        return validator.validate_game_data(data)
    
    @lru_cache(maxsize=1000)
    def cached_validate_turtle_data(self, data_hash: str, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Cached turtle data validation"""
        validator = DataValidator()
        return validator.validate_turtle_data(data)
    
    @lru_cache(maxsize=1000)
    def cached_validate_preference_data(self, data_hash: str, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Cached preference data validation"""
        validator = DataValidator()
        return validator.validate_preference_data(data)
    
    def calculate_data_hash(self, data: Dict[str, Any]) -> str:
        """Calculate hash for data caching"""
        data_string = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(data_string.encode('utf-8')).hexdigest()
    
    def compress_data_optimized(self, data: str) -> bytes:
        """Optimized compression with threshold"""
        if not self.compression_enabled:
            return data.encode('utf-8')
        
        data_bytes = data.encode('utf-8')
        
        # Only compress if data is larger than threshold
        if len(data_bytes) < self.compression_threshold:
            return data_bytes
        
        return gzip.compress(data_bytes, compresslevel=self.compression_level)
    
    def decompress_data_optimized(self, compressed_data: bytes) -> str:
        """Optimized decompression with fallback"""
        try:
            # Try to decompress
            return gzip.decompress(compressed_data).decode('utf-8')
        except (gzip.BadGzipFile, OSError):
            # Fallback to uncompressed data
            return compressed_data.decode('utf-8')
    
    def get_cached_turtle(self, turtle_id: str, turtle_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get turtle data from cache or cache it"""
        cached = self.turtle_cache.get(turtle_id)
        if cached:
            return cached
        
        # Cache the data
        self.turtle_cache.set(turtle_id, turtle_data)
        return turtle_data
    
    def get_cached_game_data(self, player_id: str, game_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get game data from cache or cache it"""
        cached = self.game_cache.get(player_id)
        if cached:
            return cached
        
        # Cache the data
        self.game_cache.set(player_id, game_data)
        return game_data
    
    def get_cached_preferences(self, player_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Get preference data from cache or cache it"""
        cached = self.preference_cache.get(player_id)
        if cached:
            return cached
        
        # Cache the data
        self.preference_cache.set(player_id, preferences)
        return preferences
    
    def invalidate_cache(self, cache_type: str = "all") -> None:
        """Invalidate specified cache"""
        if cache_type == "all" or cache_type == "turtle":
            self.turtle_cache.clear()
        if cache_type == "all" or cache_type == "game":
            self.game_cache.clear()
        if cache_type == "all" or cache_type == "preference":
            self.preference_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "turtle_cache_size": len(self.turtle_cache._cache),
            "game_cache_size": len(self.game_cache._cache),
            "preference_cache_size": len(self.preference_cache._cache),
            "compression_enabled": self.compression_enabled,
            "compression_level": self.compression_level,
            "compression_threshold": self.compression_threshold
        }


# ============================================================================
# SECURITY FEATURES
# ============================================================================

import hmac
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class SecurityManager:
    """Security features for data protection"""
    
    def __init__(self, encryption_key: Optional[bytes] = None):
        self.encryption_enabled = True
        self.checksum_enabled = True
        
        # Generate or use provided encryption key
        if encryption_key:
            self.encryption_key = encryption_key
        else:
            self.encryption_key = self._generate_encryption_key()
        
        self.fernet = Fernet(self.encryption_key)
    
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key from password"""
        password = b"turbo_shells_save_key_2025"  # In production, use user-specific key
        salt = b"turbo_shells_salt_2025"  # In production, use random salt
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate SHA-256 checksum for data"""
        if not self.checksum_enabled:
            return ""
        
        data_string = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_string.encode('utf-8')).hexdigest()
    
    def verify_checksum(self, data: Dict[str, Any], expected_checksum: str) -> bool:
        """Verify data integrity with checksum"""
        if not self.checksum_enabled or not expected_checksum:
            return True
        
        actual_checksum = self.calculate_checksum(data)
        return hmac.compare_digest(actual_checksum, expected_checksum)
    
    def encrypt_data(self, data: str) -> bytes:
        """Encrypt data with Fernet symmetric encryption"""
        if not self.encryption_enabled:
            return data.encode('utf-8')
        
        return self.fernet.encrypt(data.encode('utf-8'))
    
    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt data with Fernet symmetric encryption"""
        if not self.encryption_enabled:
            return encrypted_data.decode('utf-8')
        
        try:
            return self.fernet.decrypt(encrypted_data).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")
    
    def sign_data(self, data: Dict[str, Any]) -> str:
        """Create HMAC signature for data"""
        data_string = json.dumps(data, sort_keys=True, default=str)
        signature = hmac.new(
            self.encryption_key,
            data_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def verify_signature(self, data: Dict[str, Any], signature: str) -> bool:
        """Verify HMAC signature for data"""
        data_string = json.dumps(data, sort_keys=True, default=str)
        expected_signature = hmac.new(
            self.encryption_key,
            data_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize data for privacy protection"""
        # Remove or mask sensitive fields
        sensitive_fields = ["player_id", "session_stats", "transaction_history"]
        
        sanitized = data.copy()
        for field in sensitive_fields:
            if field in sanitized:
                if isinstance(sanitized[field], str):
                    # Mask string fields
                    sanitized[field] = "*" * len(sanitized[field])
                elif isinstance(sanitized[field], dict):
                    # Remove dict fields
                    sanitized[field] = {}
                elif isinstance(sanitized[field], list):
                    # Clear list fields
                    sanitized[field] = []
        
        return sanitized


# ============================================================================
# ENHANCED SERIALIZATION WITH OPTIMIZATION
# ============================================================================

class EnhancedDataSerializer(DataSerializer):
    """Enhanced serializer with performance and security features"""
    
    def __init__(self):
        super().__init__()
        self.optimizer = PerformanceOptimizer()
        self.security = SecurityManager()
    
    def serialize_optimized(self, data: Any, compress: bool = True, encrypt: bool = False) -> bytes:
        """Serialize data with optimization and security options"""
        # Convert to JSON
        json_data = json.dumps(data, indent=2, default=str)
        
        # Apply compression
        if compress:
            json_data = self.optimizer.compress_data_optimized(json_data).decode('utf-8')
        
        # Apply encryption
        if encrypt:
            return self.security.encrypt_data(json_data)
        
        return json_data.encode('utf-8')
    
    def deserialize_optimized(self, data: bytes, compressed: bool = True, encrypted: bool = False) -> Any:
        """Deserialize data with optimization and security options"""
        # Apply decryption
        if encrypted:
            data = self.security.decrypt_data(data).encode('utf-8')
        
        # Apply decompression
        if compressed:
            json_data = self.optimizer.decompress_data_optimized(data)
        else:
            json_data = data.decode('utf-8')
        
        # Parse JSON
        return json.loads(json_data)
    
    def serialize_with_metadata(self, data: Any, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Serialize data with metadata"""
        serialized_data = {
            "version": "2.2.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
            "checksum": self.security.calculate_checksum(data),
            "compression": self.optimizer.compression_enabled,
            "encryption": self.security.encryption_enabled
        }
        
        if metadata:
            serialized_data["metadata"] = metadata
        
        return serialized_data
    
    def deserialize_with_metadata(self, serialized_data: Dict[str, Any]) -> tuple[Any, Dict[str, Any]]:
        """Deserialize data with metadata validation"""
        # Verify checksum
        if "checksum" in serialized_data:
            if not self.security.verify_checksum(serialized_data["data"], serialized_data["checksum"]):
                raise ValueError("Data integrity check failed")
        
        # Extract metadata
        metadata = {
            "version": serialized_data.get("version", "2.2.0"),
            "timestamp": serialized_data.get("timestamp"),
            "compression": serialized_data.get("compression", False),
            "encryption": serialized_data.get("encryption", False)
        }
        
        if "metadata" in serialized_data:
            metadata.update(serialized_data["metadata"])
        
        return serialized_data["data"], metadata


# ============================================================================
# TESTING FRAMEWORK
# ============================================================================

class TestDataGenerator:
    """Generate test data for validation and testing"""
    
    @staticmethod
    def create_test_game_data(player_id: str = "test_player") -> GameData:
        """Create test game data"""
        return GameData(
            version="2.2.0",
            timestamp=datetime.now(timezone.utc).isoformat(),
            player_id=player_id,
            game_state=GameStateData(
                money=1500,
                current_phase="ROSTER",
                unlocked_features=["roster", "racing", "voting"],
                tutorial_progress={
                    "roster_intro": True,
                    "racing_basics": True,
                    "breeding_intro": False,
                    "voting_system": True
                },
                session_stats=SessionStats(
                    total_playtime_minutes=120,
                    races_completed=5,
                    turtles_bred=2,
                    votes_cast=8
                )
            ),
            economy=EconomicData(
                total_earned=500,
                total_spent=200,
                transaction_history=[
                    TransactionData(
                        id="txn_test_001",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        type="earnings",
                        amount=10,
                        source="race",
                        details={"position": 1, "race_id": "race_test_001"}
                    )
                ]
            ),
            roster=RosterData(
                active_slots=3,
                active_turtles=["turtle_001", "turtle_002"],
                retired_turtles=["turtle_003"],
                max_retired=20
            ),
            last_sessions=[
                LastSession(
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    duration_minutes=45,
                    activities=["racing", "voting"]
                )
            ]
        )
    
    @staticmethod
    def create_test_turtle_data(turtle_id: str = "turtle_test", name: str = "Test Turtle") -> TurtleData:
        """Create test turtle data"""
        return TurtleData(
            turtle_id=turtle_id,
            name=name,
            generation=2,
            created_timestamp=datetime.now(timezone.utc).isoformat(),
            parents=TurtleParents(mother_id="turtle_mother", father_id="turtle_father"),
            genetics={
                "shell_pattern": GeneTrait(
                    value="hex",
                    dominance=0.85,
                    mutation_source="inherited",
                    parent_contribution=ParentContribution(mother=0.6, father=0.4)
                ),
                "shell_color": GeneTrait(
                    value="#4A90E2",
                    dominance=0.92,
                    mutation_source="inherited",
                    parent_contribution=ParentContribution(mother=0.7, father=0.3)
                ),
                "pattern_color": GeneTrait(
                    value="#E74C3C",
                    dominance=0.78,
                    mutation_source="mutation",
                    mutation_details=MutationDetails(type="adaptive", similarity_to_parents=0.3)
                ),
                "limb_shape": GeneTrait(
                    value="flippers",
                    dominance=0.88,
                    mutation_source="inherited",
                    parent_contribution=ParentContribution(mother=0.5, father=0.5)
                ),
                "limb_length": GeneTrait(
                    value=1.2,
                    dominance=0.75,
                    mutation_source="inherited",
                    parent_contribution=ParentContribution(mother=0.4, father=0.6)
                ),
                "head_size": GeneTrait(
                    value=0.9,
                    dominance=0.82,
                    mutation_source="inherited",
                    parent_contribution=ParentContribution(mother=0.55, father=0.45)
                ),
                "eye_color": GeneTrait(
                    value="#2ECC71",
                    dominance=0.90,
                    mutation_source="inherited",
                    parent_contribution=ParentContribution(mother=0.65, father=0.35)
                ),
                "skin_texture": GeneTrait(
                    value="smooth",
                    dominance=0.79,
                    mutation_source="inherited",
                    parent_contribution=ParentContribution(mother=0.5, father=0.5)
                )
            },
            stats=TurtleStats(
                speed=8.5,
                energy=7.2,
                recovery=6.8,
                swim=9.1,
                climb=5.4,
                base_stats=BaseStats(7.0, 7.0, 7.0, 7.0, 7.0),
                genetic_modifiers=GeneticModifiers(1.5, 0.2, -0.2, 2.1, -1.6)
            ),
            performance=TurtlePerformance(
                race_history=[
                    RaceResult(
                        race_id="race_test_001",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        position=1,
                        earnings=10,
                        terrain_performance=TerrainPerformance(grass=9.2, water=8.8, rock=6.1)
                    )
                ],
                total_races=5,
                wins=3,
                average_position=2.1,
                total_earnings=125
            )
        )
    
    @staticmethod
    def create_test_preference_data(player_id: str = "test_player") -> PlayerPreferences:
        """Create test preference data"""
        return PlayerPreferences(
            version="2.2.0",
            player_id=player_id,
            last_updated=datetime.now(timezone.utc).isoformat(),
            voting_history=[
                VotingRecord(
                    date="2025-11-22",
                    design_id="design_test_001",
                    ratings={
                        "shell_pattern": 5,
                        "shell_color": 4,
                        "pattern_color": 5,
                        "limb_shape": 3,
                        "limb_length": 4,
                        "head_size": 3,
                        "eye_color": 4,
                        "skin_texture": 3
                    },
                    rewards_earned=8,
                    time_spent_minutes=5
                )
            ],
            preference_profile=PreferenceProfile(
                trait_weights=TraitWeights(
                    shell_pattern=0.25,
                    shell_color=0.20,
                    pattern_color=0.25,
                    limb_shape=0.10,
                    limb_length=0.10,
                    head_size=0.05,
                    eye_color=0.03,
                    skin_texture=0.02
                ),
                color_preferences=ColorPreferences(
                    favorite_colors=["#4A90E2", "#E74C3C", "#2ECC71"],
                    avoided_colors=["#95A5A6", "#34495E"],
                    color_harmony_score=0.78
                ),
                pattern_preferences=PatternPreferences(
                    favorite_patterns=["hex", "spots"],
                    avoided_patterns=["rings"],
                    complexity_preference=0.6
                ),
                rating_behavior=RatingBehavior(
                    average_rating=4.2,
                    rating_variance=0.8,
                    tendency_to_extreme=0.15,
                    consistent_rater=True
                )
            ),
            genetic_influence=GeneticInfluence(
                total_influence_points=45,
                trait_influence=TraitInfluence(
                    shell_pattern=12.5,
                    shell_color=8.3,
                    pattern_color=11.2,
                    limb_shape=4.1,
                    limb_length=4.8,
                    head_size=2.0,
                    eye_color=1.6,
                    skin_texture=0.5
                ),
                influence_decay=InfluenceDecay(
                    daily_decay_rate=0.05,
                    last_decay_date="2025-11-22",
                    total_decayed=2.3
                )
            )
        )


class DataValidatorTester:
    """Testing utilities for data validation"""
    
    def __init__(self):
        self.validator = DataValidator()
        self.test_generator = TestDataGenerator()
    
    def test_all_valid_data(self) -> Dict[str, bool]:
        """Test validation of all valid data types"""
        results = {}
        
        # Test game data
        game_data = self.test_generator.create_test_game_data()
        game_dict = game_data.__dict__
        results["game_data"] = self.validator.validate_game_data(game_dict)[0]
        
        # Test turtle data
        turtle_data = self.test_generator.create_test_turtle_data()
        turtle_dict = turtle_data.__dict__
        results["turtle_data"] = self.validator.validate_turtle_data(turtle_dict)[0]
        
        # Test preference data
        pref_data = self.test_generator.create_test_preference_data()
        pref_dict = pref_data.__dict__
        results["preference_data"] = self.validator.validate_preference_data(pref_dict)[0]
        
        return results
    
    def test_invalid_data(self) -> Dict[str, List[str]]:
        """Test validation of invalid data"""
        errors = {}
        
        # Test invalid game data
        invalid_game = {"invalid": "data"}
        valid, error = self.validator.validate_game_data(invalid_game)
        if not valid:
            errors["game_data"] = [error]
        
        # Test invalid turtle data
        invalid_turtle = {"turtle_id": "invalid_id", "genetics": "invalid"}
        valid, error = self.validator.validate_turtle_data(invalid_turtle)
        if not valid:
            errors["turtle_data"] = [error]
        
        # Test invalid preference data
        invalid_pref = {"player_id": "invalid", "voting_history": "invalid"}
        valid, error = self.validator.validate_preference_data(invalid_pref)
        if not valid:
            errors["preference_data"] = [error]
        
        return errors
    
    def run_performance_test(self, iterations: int = 1000) -> Dict[str, float]:
        """Run performance tests"""
        import time
        
        # Generate test data
        game_data = self.test_generator.create_test_game_data()
        turtle_data = self.test_generator.create_test_turtle_data()
        pref_data = self.test_generator.create_test_preference_data()
        
        results = {}
        
        # Test game data validation performance
        start_time = time.time()
        for _ in range(iterations):
            self.validator.validate_game_data(game_data.__dict__)
        results["game_validation_time"] = time.time() - start_time
        
        # Test turtle data validation performance
        start_time = time.time()
        for _ in range(iterations):
            self.validator.validate_turtle_data(turtle_data.__dict__)
        results["turtle_validation_time"] = time.time() - start_time
        
        # Test preference data validation performance
        start_time = time.time()
        for _ in range(iterations):
            self.validator.validate_preference_data(pref_data.__dict__)
        results["preference_validation_time"] = time.time() - start_time
        
        return results


# ============================================================================
# GLOBAL INSTANCES
# ============================================================================

performance_optimizer = PerformanceOptimizer()
security_manager = SecurityManager()
enhanced_serializer = EnhancedDataSerializer()
test_generator = TestDataGenerator()
validator_tester = DataValidatorTester()
