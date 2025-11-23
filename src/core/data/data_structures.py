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

    mother_id: Optional[str]
    father_id: Optional[str]


@dataclass
class TurtleLineage:
    """Extended lineage information"""

    parent_ids: List[str]  # From entity
    generation: int         # From entity
    ancestors: List[str]     # Traced ancestry
    offspring_count: int    # Number of children


@dataclass
class TurtleIdentity:
    """Core turtle identity information"""

    turtle_id: str          # Standardized from entity.id
    name: str
    age: int                # From entity.age
    is_active: bool         # From entity.is_active
    created_timestamp: str
    last_modified: str


@dataclass
class TurtleDynamicState:
    """Dynamic race state (for mid-race saves)"""

    current_energy: float
    race_distance: float
    is_resting: bool
    finished: bool
    rank: Optional[int]
    last_race_update: str


@dataclass
class TurtleRaceResult:
    """Individual race result matching entity format"""

    number: int
    position: int
    earnings: int
    age_at_race: int
    terrain_type: str
    race_timestamp: str


@dataclass
class TurtleVisualGenetics:
    """Visual genetics compatible with entity system"""

    shell_pattern: str
    shell_color: str
    pattern_color: str
    limb_shape: str
    limb_length: float
    head_size: float
    eye_color: str
    skin_texture: str
    
    # Additional visual traits for future expansion
    shell_size: float = 1.0
    pattern_density: float = 1.0
    color_saturation: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format compatible with entity"""
        return {
            "shell_pattern": self.shell_pattern,
            "shell_color": self.shell_color,
            "pattern_color": self.pattern_color,
            "limb_shape": self.limb_shape,
            "limb_length": self.limb_length,
            "head_size": self.head_size,
            "eye_color": self.eye_color,
            "skin_texture": self.skin_texture,
            "shell_size": self.shell_size,
            "pattern_density": self.pattern_density,
            "color_saturation": self.color_saturation,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TurtleVisualGenetics':
        """Create from dictionary format"""
        return cls(
            shell_pattern=data.get("shell_pattern", "hex"),
            shell_color=data.get("shell_color", "#4A90E2"),
            pattern_color=data.get("pattern_color", "#E74C3C"),
            limb_shape=data.get("limb_shape", "flippers"),
            limb_length=float(data.get("limb_length", 1.0)),
            head_size=float(data.get("head_size", 1.0)),
            eye_color=data.get("eye_color", "#2ECC71"),
            skin_texture=data.get("skin_texture", "smooth"),
            shell_size=float(data.get("shell_size", 1.0)),
            pattern_density=float(data.get("pattern_density", 1.0)),
            color_saturation=float(data.get("color_saturation", 1.0)),
        )


@dataclass
class TurtleEnhancedPerformance:
    """Complete performance tracking"""

    race_history: List[TurtleRaceResult]
    total_races: int
    total_earnings: int
    wins: int
    average_position: float
    best_position: int
    worst_position: int
    favorite_terrain: str
    terrain_performance: Dict[str, float]
    
    def add_race_result(self, result: TurtleRaceResult) -> None:
        """Add a new race result and update statistics"""
        self.race_history.append(result)
        self.total_races += 1
        self.total_earnings += result.earnings
        
        # Update wins
        if result.position == 1:
            self.wins += 1
        
        # Update position statistics
        if self.total_races == 1:
            self.best_position = result.position
            self.worst_position = result.position
            self.average_position = float(result.position)
        else:
            self.best_position = min(self.best_position, result.position)
            self.worst_position = max(self.worst_position, result.position)
            self.average_position = (
                (self.average_position * (self.total_races - 1) + result.position) / 
                self.total_races
            )
        
        # Update terrain performance
        if result.terrain_type not in self.terrain_performance:
            self.terrain_performance[result.terrain_type] = 0.0
        self.terrain_performance[result.terrain_type] += (1.0 / result.position)
        
        # Update favorite terrain
        if self.terrain_performance:
            self.favorite_terrain = max(self.terrain_performance, 
                                     key=self.terrain_performance.get)


@dataclass
class TurtleStaticData:
    """Static turtle data that doesn't change during gameplay"""

    identity: TurtleIdentity
    lineage: TurtleLineage
    visual_genetics: TurtleVisualGenetics
    base_stats: BaseStats
    created_timestamp: str


@dataclass
class TurtleDynamicData:
    """Dynamic turtle data that changes during gameplay"""

    current_stats: TurtleStats
    performance: TurtleEnhancedPerformance
    race_state: Optional[TurtleDynamicState]
    last_updated: str


@dataclass
class EnhancedTurtleData:
    """Complete enhanced turtle data structure with 100% property coverage"""

    # Core identity and static data
    static_data: TurtleStaticData
    
    # Dynamic data that changes during gameplay
    dynamic_data: TurtleDynamicData
    
    # Legacy compatibility fields
    turtle_id: str  # For backward compatibility
    name: str      # For backward compatibility
    
    def get_identity(self) -> TurtleIdentity:
        """Get turtle identity information"""
        return self.static_data.identity
    
    def get_current_age(self) -> int:
        """Get current age from dynamic data"""
        return self.dynamic_data.current_stats.age
    
    def set_age(self, age: int) -> None:
        """Update turtle age"""
        self.dynamic_data.current_stats.age = age
        self.dynamic_data.last_updated = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    def is_active(self) -> bool:
        """Check if turtle is active (in roster)"""
        return self.static_data.identity.is_active
    
    def set_active_status(self, is_active: bool) -> None:
        """Update turtle active status"""
        self.static_data.identity.is_active = is_active
        self.dynamic_data.last_updated = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    def get_visual_genetics(self) -> TurtleVisualGenetics:
        """Get visual genetics"""
        return self.static_data.visual_genetics
    
    def get_race_history(self) -> List[TurtleRaceResult]:
        """Get complete race history"""
        return self.dynamic_data.performance.race_history
    
    def get_total_earnings(self) -> int:
        """Get total career earnings"""
        return self.dynamic_data.performance.total_earnings
    
    def add_race_result(self, position: int, earnings: int, terrain_type: str, 
                       race_number: Optional[int] = None) -> None:
        """Add a new race result"""
        if race_number is None:
            race_number = self.dynamic_data.performance.total_races + 1
        
        result = TurtleRaceResult(
            number=race_number,
            position=position,
            earnings=earnings,
            age_at_race=self.get_current_age(),
            terrain_type=terrain_type,
            race_timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
        )
        
        self.dynamic_data.performance.add_race_result(result)
        self.dynamic_data.last_updated = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    def update_race_state(self, current_energy: float, race_distance: float, 
                         is_resting: bool, finished: bool, rank: Optional[int] = None) -> None:
        """Update dynamic race state"""
        self.dynamic_data.race_state = TurtleDynamicState(
            current_energy=current_energy,
            race_distance=race_distance,
            is_resting=is_resting,
            finished=finished,
            rank=rank,
            last_race_update=datetime.datetime.now(datetime.timezone.utc).isoformat()
        )
        self.dynamic_data.last_updated = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    def clear_race_state(self) -> None:
        """Clear race state (called when race ends)"""
        self.dynamic_data.race_state = None
        self.dynamic_data.last_updated = datetime.datetime.now(datetime.timezone.utc).isoformat()


# Maintain backward compatibility
@dataclass
class TurtleData:
    """Legacy turtle data structure for backward compatibility"""

    turtle_id: str
    name: str
    generation: int
    created_timestamp: str
    parents: Optional[TurtleParents]
    genetics: Dict[str, GeneTrait]
    stats: TurtleStats
    performance: TurtlePerformance
    
    @classmethod
    def from_enhanced(cls, enhanced: EnhancedTurtleData) -> 'TurtleData':
        """Create legacy TurtleData from EnhancedTurtleData"""
        # Convert visual genetics to gene traits
        genetics_dict = {}
        visual_genetics = enhanced.get_visual_genetics()
        genetics_dict["shell_pattern"] = GeneTrait(
            value=visual_genetics.shell_pattern, 
            dominance=1.0, 
            mutation_source="inheritance"
        )
        genetics_dict["shell_color"] = GeneTrait(
            value=visual_genetics.shell_color, 
            dominance=1.0, 
            mutation_source="inheritance"
        )
        genetics_dict["pattern_color"] = GeneTrait(
            value=visual_genetics.pattern_color, 
            dominance=1.0, 
            mutation_source="inheritance"
        )
        genetics_dict["limb_shape"] = GeneTrait(
            value=visual_genetics.limb_shape, 
            dominance=1.0, 
            mutation_source="inheritance"
        )
        genetics_dict["limb_length"] = GeneTrait(
            value=visual_genetics.limb_length, 
            dominance=1.0, 
            mutation_source="inheritance"
        )
        genetics_dict["head_size"] = GeneTrait(
            value=visual_genetics.head_size, 
            dominance=1.0, 
            mutation_source="inheritance"
        )
        genetics_dict["eye_color"] = GeneTrait(
            value=visual_genetics.eye_color, 
            dominance=1.0, 
            mutation_source="inheritance"
        )
        genetics_dict["skin_texture"] = GeneTrait(
            value=visual_genetics.skin_texture, 
            dominance=1.0, 
            mutation_source="inheritance"
        )
        
        # Convert performance data
        enhanced_perf = enhanced.dynamic_data.performance
        
        # Convert race history to legacy format
        legacy_race_history = []
        for race_result in enhanced_perf.race_history:
            legacy_race_history.append(RaceResult(
                race_id=f"race_{race_result.number}",
                timestamp=race_result.race_timestamp,
                position=race_result.position,
                earnings=race_result.earnings,
                terrain_performance=TerrainPerformance(
                    grass=1.0/race_result.position if race_result.terrain_type == "grass" else 0.5,
                    water=1.0/race_result.position if race_result.terrain_type == "water" else 0.5,
                    rock=1.0/race_result.position if race_result.terrain_type == "rock" else 0.5,
                )
            ))
        
        return cls(
            turtle_id=enhanced.turtle_id,
            name=enhanced.name,
            generation=enhanced.static_data.lineage.generation,
            created_timestamp=enhanced.static_data.created_timestamp,
            parents=TurtleParents(
                mother_id=enhanced.static_data.lineage.parent_ids[0] if len(enhanced.static_data.lineage.parent_ids) > 0 else None,
                father_id=enhanced.static_data.lineage.parent_ids[1] if len(enhanced.static_data.lineage.parent_ids) > 1 else None,
            ),
            genetics=genetics_dict,
            stats=enhanced.dynamic_data.current_stats,
            performance=TurtlePerformance(
                race_history=legacy_race_history,
                total_races=enhanced_perf.total_races,
                wins=enhanced_perf.wins,
                average_position=enhanced_perf.average_position,
                total_earnings=enhanced_perf.total_earnings,
            ),
        )


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
