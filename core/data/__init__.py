"""
Data Module for TurboShells

This module provides a clean interface for all data-related functionality,
including structures, validation, serialization, performance, security, migration, and testing.
"""

# Core data structures
from .data_structures import (
    # Game data structures
    GameData, GameStateData, EconomicData, SessionStats, RosterData, LastSession, TransactionData,
    
    # Turtle data structures  
    TurtleData, TurtleParents, GeneTrait, ParentContribution, MutationDetails,
    BaseStats, GeneticModifiers, TurtleStats, TerrainPerformance, RaceResult, TurtlePerformance,
    
    # Preference data structures
    PlayerPreferences, VotingRecord, TraitWeights, ColorPreferences, PatternPreferences,
    RatingBehavior, PreferenceProfile, TraitInfluence, InfluenceDecay, GeneticInfluence,
    
    # Gene pool and community data structures
    GenePoolData, TraitFrequencies, DominantTraits, MutationRates,
    CommunityPreferences, TraitAverages, TraitCombination, TrendingTraits
)

# Validation
from .data_validation import DataValidator, validator

# Serialization
from .data_serialization import (
    DataSerializer, 
    create_default_game_data, 
    create_default_turtle_data, 
    create_default_preference_data
)

# Performance optimization
from .data_performance import PerformanceOptimizer, performance_optimizer

# Security
from .data_security import SecurityManager, security_manager

# Migration
from .data_migration import DataMigrator, data_migrator

# Testing
from .data_testing import TestDataGenerator, DataValidatorTester, test_generator, validator_tester

# Export main classes for convenience
__all__ = [
    # Data structures
    'GameData', 'GameStateData', 'EconomicData', 'SessionStats', 'RosterData', 'LastSession', 'TransactionData',
    'TurtleData', 'TurtleParents', 'GeneTrait', 'ParentContribution', 'MutationDetails',
    'BaseStats', 'GeneticModifiers', 'TurtleStats', 'TerrainPerformance', 'RaceResult', 'TurtlePerformance',
    'PlayerPreferences', 'VotingRecord', 'TraitWeights', 'ColorPreferences', 'PatternPreferences',
    'RatingBehavior', 'PreferenceProfile', 'TraitInfluence', 'InfluenceDecay', 'GeneticInfluence',
    'GenePoolData', 'TraitFrequencies', 'DominantTraits', 'MutationRates',
    'CommunityPreferences', 'TraitAverages', 'TraitCombination', 'TrendingTraits',
    
    # Validation
    'DataValidator', 'validator',
    
    # Serialization
    'DataSerializer', 'create_default_game_data', 'create_default_turtle_data', 'create_default_preference_data',
    
    # Performance
    'PerformanceOptimizer', 'performance_optimizer',
    
    # Security
    'SecurityManager', 'security_manager',
    
    # Migration
    'DataMigrator', 'data_migrator',
    
    # Testing
    'TestDataGenerator', 'DataValidatorTester', 'test_generator', 'validator_tester'
]
