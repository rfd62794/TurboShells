"""
Data Structures for TurboShells

This module contains only the data structures (dataclasses) for Game Data,
Gene Data, and Gene Preference data, following Single Responsibility Principle.
"""

import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass


# ============================================================================
# GAME DATA STRUCTURES
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


# ============================================================================
# GENE DATA STRUCTURES
# ============================================================================


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
    age: int = 0  # Turtle age in days


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


# ============================================================================
# PREFERENCE DATA STRUCTURES
# ============================================================================


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


# ============================================================================
# GENE POOL DATA STRUCTURES
# ============================================================================


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


# ============================================================================
# COMMUNITY DATA STRUCTURES
# ============================================================================


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
