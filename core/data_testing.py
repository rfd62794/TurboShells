"""
Data Testing Framework for TurboShells

This module contains only testing and validation logic,
following Single Responsibility Principle.
"""

import datetime
import time
from typing import Dict, List, Any

from core.data_structures import (
    GameData, TurtleData, PlayerPreferences,
    TransactionData, EconomicData, SessionStats, GameStateData, RosterData, LastSession,
    GeneTrait, ParentContribution, MutationDetails, BaseStats, GeneticModifiers,
    TurtleStats, TerrainPerformance, RaceResult, TurtlePerformance, TurtleParents,
    VotingRecord, TraitWeights, ColorPreferences, PatternPreferences,
    RatingBehavior, PreferenceProfile, TraitInfluence, InfluenceDecay,
    GeneticInfluence
)
from core.data_validation import DataValidator


class TestDataGenerator:
    """Generate test data for validation and testing"""
    
    @staticmethod
    def create_test_game_data(player_id: str = "test_player") -> GameData:
        """Create test game data"""
        return GameData(
            version="2.2.0",
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
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
                        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
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
                    timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
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
            created_timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
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
                        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
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
            last_updated=datetime.datetime.now(datetime.timezone.utc).isoformat(),
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
# GLOBAL TESTING INSTANCES
# ============================================================================

test_generator = TestDataGenerator()
validator_tester = DataValidatorTester()
