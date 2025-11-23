"""
Data Serialization for TurboShells

This module contains only serialization and deserialization logic,
following Single Responsibility Principle. Enhanced for Phase 4 with complete
turtle data preservation support.
"""

from core.data.data_structures import (
    GameStateData,
    EconomicData,
    SessionStats,
    RosterData,
    LastSession,
    GeneTrait,
    BaseStats,
    GeneticModifiers,
    TurtleStats,
    TerrainPerformance,
    RaceResult,
    TurtlePerformance,
    TurtleParents,
    TraitWeights,
    ColorPreferences,
    PatternPreferences,
    RatingBehavior,
    PreferenceProfile,
    TraitInfluence,
    InfluenceDecay,
    GeneticInfluence,
    VotingRecord,
    # Enhanced structures for Phase 4
    EnhancedTurtleData,
    TurtleStaticData,
    TurtleDynamicData,
    TurtleIdentity,
    TurtleLineage,
    TurtleVisualGenetics,
    TurtleDynamicState,
    TurtleRaceResult,
    TurtleEnhancedPerformance,
)
from typing import Optional, Dict, Any, List
import datetime
import json

from .data_structures import GameData, TurtleData, PlayerPreferences


class EnhancedDataSerializer:
    """Enhanced serialization with complete turtle data support"""
    
    @staticmethod
    def serialize_enhanced_turtle_data(enhanced_data: EnhancedTurtleData) -> str:
        """Serialize EnhancedTurtleData to JSON with complete data preservation"""
        # Convert to dictionary recursively
        data_dict = EnhancedDataSerializer._convert_to_dict(enhanced_data)
        return json.dumps(data_dict, indent=2, default=str)
    
    @staticmethod
    def deserialize_enhanced_turtle_data(json_str: str) -> EnhancedTurtleData:
        """Deserialize EnhancedTurtleData from JSON"""
        data_dict = json.loads(json_str)
        return EnhancedDataSerializer._dict_to_enhanced_turtle_data(data_dict)
    
    @staticmethod
    def serialize_turtle_visual_genetics(genetics: TurtleVisualGenetics) -> str:
        """Serialize TurtleVisualGenetics to JSON"""
        return json.dumps(genetics.to_dict(), indent=2)
    
    @staticmethod
    def deserialize_turtle_visual_genetics(json_str: str) -> TurtleVisualGenetics:
        """Deserialize TurtleVisualGenetics from JSON"""
        data_dict = json.loads(json_str)
        return TurtleVisualGenetics.from_dict(data_dict)
    
    @staticmethod
    def serialize_turtle_race_result(result: TurtleRaceResult) -> str:
        """Serialize TurtleRaceResult to JSON"""
        data_dict = {
            "number": result.number,
            "position": result.position,
            "earnings": result.earnings,
            "age_at_race": result.age_at_race,
            "terrain_type": result.terrain_type,
            "race_timestamp": result.race_timestamp,
        }
        return json.dumps(data_dict, indent=2)
    
    @staticmethod
    def deserialize_turtle_race_result(json_str: str) -> TurtleRaceResult:
        """Deserialize TurtleRaceResult from JSON"""
        data_dict = json.loads(json_str)
        return TurtleRaceResult(**data_dict)
    
    @staticmethod
    def _convert_to_dict(obj) -> Dict[str, Any]:
        """Recursively convert dataclass objects to dictionaries"""
        if hasattr(obj, '__dict__'):
            # It's a dataclass or object with __dict__
            result = {}
            for key, value in obj.__dict__.items():
                if hasattr(value, '__dict__'):
                    # Recursively convert nested dataclass
                    result[key] = EnhancedDataSerializer._convert_to_dict(value)
                elif isinstance(value, dict):
                    # Handle nested dictionaries
                    result[key] = {
                        k: EnhancedDataSerializer._convert_to_dict(v) if hasattr(v, '__dict__') else v
                        for k, v in value.items()
                    }
                elif isinstance(value, list):
                    # Handle lists of objects
                    result[key] = [
                        (
                            EnhancedDataSerializer._convert_to_dict(item)
                            if hasattr(item, '__dict__')
                            else item
                        )
                        for item in value
                    ]
                elif isinstance(value, (datetime.datetime, datetime.date)):
                    # Handle datetime objects
                    result[key] = value.isoformat()
                else:
                    result[key] = value
            return result
        else:
            # It's already a primitive value
            return obj
    
    @staticmethod
    def _dict_to_enhanced_turtle_data(data_dict: Dict[str, Any]) -> EnhancedTurtleData:
        """Convert dictionary back to EnhancedTurtleData"""
        # Reconstruct static data
        static_data_dict = data_dict.get('static_data', {})
        static_data = TurtleStaticData(
            identity=TurtleIdentity(**static_data_dict.get('identity', {})),
            lineage=TurtleLineage(**static_data_dict.get('lineage', {})),
            visual_genetics=TurtleVisualGenetics.from_dict(
                static_data_dict.get('visual_genetics', {})
            ),
            base_stats=BaseStats(**static_data_dict.get('base_stats', {})),
            created_timestamp=static_data_dict.get('created_timestamp', ''),
        )
        
        # Reconstruct dynamic data
        dynamic_data_dict = data_dict.get('dynamic_data', {})
        
        # Reconstruct race history
        race_history = []
        for race_dict in dynamic_data_dict.get('performance', {}).get('race_history', []):
            race_history.append(TurtleRaceResult(**race_dict))
        
        # Reconstruct performance
        performance_dict = dynamic_data_dict.get('performance', {})
        performance = TurtleEnhancedPerformance(
            race_history=race_history,
            total_races=performance_dict.get('total_races', 0),
            total_earnings=performance_dict.get('total_earnings', 0),
            wins=performance_dict.get('wins', 0),
            average_position=performance_dict.get('average_position', 0.0),
            best_position=performance_dict.get('best_position', 0),
            worst_position=performance_dict.get('worst_position', 0),
            favorite_terrain=performance_dict.get('favorite_terrain', 'grass'),
            terrain_performance=performance_dict.get('terrain_performance', {}),
        )
        
        # Reconstruct race state (optional)
        race_state_dict = dynamic_data_dict.get('race_state')
        race_state = TurtleDynamicState(**race_state_dict) if race_state_dict else None
        
        dynamic_data = TurtleDynamicData(
            current_stats=TurtleStats(**dynamic_data_dict.get('current_stats', {})),
            performance=performance,
            race_state=race_state,
            last_updated=dynamic_data_dict.get('last_updated', ''),
        )
        
        # Reconstruct enhanced turtle data
        return EnhancedTurtleData(
            static_data=static_data,
            dynamic_data=dynamic_data,
            turtle_id=data_dict.get('turtle_id', ''),
            name=data_dict.get('name', ''),
        )


class DataSerializer:
    """Serialization and deserialization utilities"""

    @staticmethod
    def serialize_game_data(game_data: GameData) -> str:
        """Serialize game data to JSON"""
        return json.dumps(game_data.__dict__, indent=2, default=str)

    @staticmethod
    def deserialize_game_data(json_str: str) -> GameData:
        """Deserialize game data from JSON"""
        data = json.loads(json_str)
        return GameData(**data)

    @staticmethod
    def serialize_turtle_data(turtle_data: TurtleData) -> str:
        """Serialize turtle data to JSON"""
        return json.dumps(turtle_data.__dict__, indent=2, default=str)

    @staticmethod
    def deserialize_turtle_data(json_str: str) -> TurtleData:
        """Deserialize turtle data from JSON"""
        data = json.loads(json_str)
        return TurtleData(**data)

    @staticmethod
    def serialize_preference_data(pref_data: PlayerPreferences) -> str:
        """Serialize preference data to JSON"""
        return json.dumps(pref_data.__dict__, indent=2, default=str)

    @staticmethod
    def deserialize_preference_data(json_str: str) -> PlayerPreferences:
        """Deserialize preference data from JSON"""
        data = json.loads(json_str)
        return PlayerPreferences(**data)
    
    @staticmethod
    def serialize_enhanced_turtle_list(enhanced_turtles: List[EnhancedTurtleData]) -> str:
        """Serialize list of EnhancedTurtleData objects"""
        turtle_dicts = [EnhancedDataSerializer._convert_to_dict(turtle) for turtle in enhanced_turtles]
        return json.dumps(turtle_dicts, indent=2, default=str)
    
    @staticmethod
    def deserialize_enhanced_turtle_list(json_str: str) -> List[EnhancedTurtleData]:
        """Deserialize list of EnhancedTurtleData objects"""
        turtle_dicts = json.loads(json_str)
        return [EnhancedDataSerializer._dict_to_enhanced_turtle_data(turtle_dict) for turtle_dict in turtle_dicts]
    
    @staticmethod
    def convert_legacy_to_enhanced_list(legacy_turtles: List[TurtleData]) -> List[EnhancedTurtleData]:
        """Convert list of legacy TurtleData to EnhancedTurtleData"""
        enhanced_turtles = []
        for legacy_turtle in legacy_turtles:
            # This is a simplified conversion - in practice you'd use the conversion utilities
            # For now, create a basic enhanced structure
            enhanced_turtles.append(EnhancedDataSerializer._dict_to_enhanced_turtle_data(
                EnhancedDataSerializer._convert_to_dict(legacy_turtle)
            ))
        return enhanced_turtles
    
    @staticmethod
    def convert_enhanced_to_legacy_list(enhanced_turtles: List[EnhancedTurtleData]) -> List[TurtleData]:
        """Convert list of EnhancedTurtleData to legacy TurtleData"""
        legacy_turtles = []
        for enhanced_turtle in enhanced_turtles:
            legacy_turtles.append(TurtleData.from_enhanced(enhanced_turtle))
        return legacy_turtles


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
                "voting_system": False,
            },
            session_stats=SessionStats(
                total_playtime_minutes=0,
                races_completed=0,
                turtles_bred=0,
                votes_cast=0,
            ),
        ),
        economy=EconomicData(total_earned=0, total_spent=0, transaction_history=[]),
        roster=RosterData(
            active_slots=3, active_turtles=[], retired_turtles=[], max_retired=20
        ),
        last_sessions=[],
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
            "skin_texture": GeneTrait("smooth", 1.0, "random"),
        },
        stats=TurtleStats(
            speed=7.0,
            energy=7.0,
            recovery=7.0,
            swim=7.0,
            climb=7.0,
            base_stats=BaseStats(7.0, 7.0, 7.0, 7.0, 7.0),
            genetic_modifiers=GeneticModifiers(0.0, 0.0, 0.0, 0.0, 0.0),
            age=0,  # Start at age 0
        ),
        performance=TurtlePerformance(
            race_history=[],
            total_races=0,
            wins=0,
            average_position=0.0,
            total_earnings=0,
        ),
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
                skin_texture=0.125,
            ),
            color_preferences=ColorPreferences(
                favorite_colors=["#4A90E2", "#E74C3C", "#2ECC71"],
                avoided_colors=[],
                color_harmony_score=0.5,
            ),
            pattern_preferences=PatternPreferences(
                favorite_patterns=[], avoided_patterns=[], complexity_preference=0.5
            ),
            rating_behavior=RatingBehavior(
                average_rating=3.0,
                rating_variance=1.0,
                tendency_to_extreme=0.1,
                consistent_rater=False,
            ),
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
                skin_texture=0.0,
            ),
            influence_decay=InfluenceDecay(
                daily_decay_rate=0.05,
                last_decay_date=now.split("T")[0],
                total_decayed=0.0,
            ),
        ),
    )
