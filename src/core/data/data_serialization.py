"""
Data Serialization for TurboShells

This module contains only serialization and deserialization logic,
following Single Responsibility Principle.
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
)
from typing import Optional
import datetime
import json
from typing import Dict, Any

from .data_structures import GameData, TurtleData, PlayerPreferences


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
