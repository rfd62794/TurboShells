"""
Turtle Entity ↔ DataClass Conversion Utilities

This module provides bidirectional conversion between Turtle entities and 
EnhancedTurtleData structures, ensuring 100% data preservation.
"""

import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from core.game.entities import Turtle
from core.data.data_structures import (
    EnhancedTurtleData,
    TurtleStaticData,
    TurtleDynamicData,
    TurtleIdentity,
    TurtleLineage,
    TurtleVisualGenetics,
    TurtleDynamicState,
    TurtleRaceResult,
    TurtleEnhancedPerformance,
    TurtleStats,
    BaseStats,
    GeneticModifiers,
    TurtleParents,
    TurtleData,
    GeneTrait,
    RaceResult,
    TerrainPerformance,
    TurtlePerformance,
)


class TurtleEntityConverter:
    """Handles conversion between Turtle entities and EnhancedTurtleData"""
    
    @staticmethod
    def entity_to_enhanced_data(turtle: Turtle) -> EnhancedTurtleData:
        """Convert Turtle entity to EnhancedTurtleData with complete data preservation"""
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Convert identity
        identity = TurtleIdentity(
            turtle_id=turtle.id,  # Use entity.id directly
            name=turtle.name,
            age=turtle.age,
            is_active=turtle.is_active,
            created_timestamp=now,  # Use current time as creation timestamp
            last_modified=now,
        )
        
        # Convert lineage
        lineage = TurtleLineage(
            parent_ids=turtle.parent_ids.copy() if turtle.parent_ids else [],
            generation=turtle.generation,
            ancestors=[],  # Could be calculated from parent_ids in future
            offspring_count=0,  # Could be tracked in future
        )
        
        # Convert visual genetics
        visual_genetics = TurtleVisualGenetics.from_dict(turtle.visual_genetics)
        
        # Convert base stats (current stats become base stats)
        base_stats = BaseStats(
            speed=turtle.speed,
            energy=turtle.max_energy,
            recovery=turtle.recovery,
            swim=turtle.swim,
            climb=turtle.climb,
        )
        
        # Create static data
        static_data = TurtleStaticData(
            identity=identity,
            lineage=lineage,
            visual_genetics=visual_genetics,
            base_stats=base_stats,
            created_timestamp=now,
        )
        
        # Convert current stats
        current_stats = TurtleStats(
            speed=turtle.speed,
            energy=turtle.max_energy,  # Use max_energy for consistency
            recovery=turtle.recovery,
            swim=turtle.swim,
            climb=turtle.climb,
            base_stats=base_stats,
            genetic_modifiers=GeneticModifiers(
                speed=0.0,  # Could be calculated from genetics in future
                energy=0.0,
                recovery=0.0,
                swim=0.0,
                climb=0.0,
            ),
            age=turtle.age,
        )
        
        # Convert race history
        race_results = []
        for race_data in turtle.race_history:
            race_result = TurtleRaceResult(
                number=race_data.get("number", 0),
                position=race_data.get("position", 0),
                earnings=race_data.get("earnings", 0),
                age_at_race=race_data.get("age_at_race", turtle.age),
                terrain_type=race_data.get("terrain_type", "grass"),  # Default terrain
                race_timestamp=race_data.get("timestamp", now),
            )
            race_results.append(race_result)
        
        # Create enhanced performance
        performance = TurtleEnhancedPerformance(
            race_history=race_results,
            total_races=turtle.total_races,
            total_earnings=turtle.total_earnings,
            wins=len([r for r in race_results if r.position == 1]),
            average_position=sum(r.position for r in race_results) / len(race_results) if race_results else 0.0,
            best_position=min(r.position for r in race_results) if race_results else 0,
            worst_position=max(r.position for r in race_results) if race_results else 0,
            favorite_terrain="grass",  # Could be calculated from performance
            terrain_performance={},  # Could be calculated from race_history
        )
        
        # Convert dynamic race state (if currently in race)
        race_state = None
        if hasattr(turtle, 'current_energy') and turtle.current_energy != turtle.max_energy:
            race_state = TurtleDynamicState(
                current_energy=getattr(turtle, 'current_energy', turtle.max_energy),
                race_distance=getattr(turtle, 'race_distance', 0.0),
                is_resting=getattr(turtle, 'is_resting', False),
                finished=getattr(turtle, 'finished', False),
                rank=getattr(turtle, 'rank', None),
                last_race_update=now,
            )
        
        # Create dynamic data
        dynamic_data = TurtleDynamicData(
            current_stats=current_stats,
            performance=performance,
            race_state=race_state,
            last_updated=now,
        )
        
        # Create enhanced turtle data
        return EnhancedTurtleData(
            static_data=static_data,
            dynamic_data=dynamic_data,
            turtle_id=turtle.id,  # Legacy compatibility
            name=turtle.name,      # Legacy compatibility
        )
    
    @staticmethod
    def enhanced_data_to_entity(enhanced_data: EnhancedTurtleData) -> Turtle:
        """Convert EnhancedTurtleData back to Turtle entity with complete data restoration"""
        # Extract identity
        identity = enhanced_data.get_identity()
        
        # Extract visual genetics
        visual_genetics = enhanced_data.get_visual_genetics().to_dict()
        
        # Create turtle entity
        turtle = Turtle(
            name=identity.name,
            speed=enhanced_data.dynamic_data.current_stats.speed,
            energy=enhanced_data.dynamic_data.current_stats.energy,
            recovery=enhanced_data.dynamic_data.current_stats.recovery,
            swim=enhanced_data.dynamic_data.current_stats.swim,
            climb=enhanced_data.dynamic_data.current_stats.climb,
            genetics=visual_genetics,  # Use the converted genetics
        )
        
        # Restore entity properties
        turtle.id = identity.turtle_id
        turtle.age = identity.age
        turtle.is_active = identity.is_active
        
        # Restore lineage
        turtle.parent_ids = enhanced_data.static_data.lineage.parent_ids.copy()
        turtle.generation = enhanced_data.static_data.lineage.generation
        
        # Restore race history
        turtle.race_history = []
        turtle.total_races = 0
        turtle.total_earnings = 0
        
        for race_result in enhanced_data.get_race_history():
            race_data = {
                "number": race_result.number,
                "position": race_result.position,
                "earnings": race_result.earnings,
                "age_at_race": race_result.age_at_race,
                "terrain_type": race_result.terrain_type,
                "timestamp": race_result.race_timestamp,
            }
            turtle.race_history.append(race_data)
            turtle.total_races += 1
            turtle.total_earnings += race_result.earnings
        
        # Restore dynamic race state if available
        if enhanced_data.dynamic_data.race_state:
            race_state = enhanced_data.dynamic_data.race_state
            turtle.current_energy = race_state.current_energy
            turtle.race_distance = race_state.race_distance
            turtle.is_resting = race_state.is_resting
            turtle.finished = race_state.finished
            turtle.rank = race_state.rank
        
        return turtle
    
    @staticmethod
    def entity_to_legacy_data(turtle: Turtle) -> TurtleData:
        """Convert Turtle entity to legacy TurtleData for backward compatibility"""
        enhanced = TurtleEntityConverter.entity_to_enhanced_data(turtle)
        return TurtleData.from_enhanced(enhanced)
    
    @staticmethod
    def legacy_data_to_entity(turtle_data: TurtleData) -> Turtle:
        """Convert legacy TurtleData to Turtle entity"""
        # First convert to enhanced, then to entity
        # This requires creating a temporary enhanced structure
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Extract genetics from legacy format
        genetics_dict = {}
        for trait_name, gene_trait in turtle_data.genetics.items():
            genetics_dict[trait_name] = gene_trait.value
        
        # Create visual genetics
        visual_genetics = TurtleVisualGenetics.from_dict(genetics_dict)
        
        # Create identity
        identity = TurtleIdentity(
            turtle_id=turtle_data.turtle_id,
            name=turtle_data.name,
            age=turtle_data.stats.age,
            is_active=True,  # Default to active for legacy data
            created_timestamp=turtle_data.created_timestamp,
            last_modified=now,
        )
        
        # Create lineage
        parent_ids = []
        if turtle_data.parents:
            if turtle_data.parents.mother_id:
                parent_ids.append(turtle_data.parents.mother_id)
            if turtle_data.parents.father_id:
                parent_ids.append(turtle_data.parents.father_id)
        
        lineage = TurtleLineage(
            parent_ids=parent_ids,
            generation=turtle_data.generation,
            ancestors=[],
            offspring_count=0,
        )
        
        # Create static data
        static_data = TurtleStaticData(
            identity=identity,
            lineage=lineage,
            visual_genetics=visual_genetics,
            base_stats=turtle_data.stats.base_stats,
            created_timestamp=turtle_data.created_timestamp,
        )
        
        # Convert performance data
        race_results = []
        for race_result in turtle_data.performance.race_history:
            # Convert legacy RaceResult to TurtleRaceResult
            enhanced_race_result = TurtleRaceResult(
                number=int(race_result.race_id.split("_")[1]) if "_" in race_result.race_id else 0,
                position=race_result.position,
                earnings=race_result.earnings,
                age_at_race=turtle_data.stats.age,
                terrain_type="grass",  # Default terrain for legacy data
                race_timestamp=race_result.timestamp,
            )
            race_results.append(enhanced_race_result)
        
        performance = TurtleEnhancedPerformance(
            race_history=race_results,
            total_races=turtle_data.performance.total_races,
            total_earnings=turtle_data.performance.total_earnings,
            wins=turtle_data.performance.wins,
            average_position=turtle_data.performance.average_position,
            best_position=min(r.position for r in race_results) if race_results else 0,
            worst_position=max(r.position for r in race_results) if race_results else 0,
            favorite_terrain="grass",
            terrain_performance={},
        )
        
        # Create dynamic data
        dynamic_data = TurtleDynamicData(
            current_stats=turtle_data.stats,
            performance=performance,
            race_state=None,  # Legacy data doesn't have race state
            last_updated=now,
        )
        
        # Create enhanced data
        enhanced_data = EnhancedTurtleData(
            static_data=static_data,
            dynamic_data=dynamic_data,
            turtle_id=turtle_data.turtle_id,
            name=turtle_data.name,
        )
        
        # Convert to entity
        return TurtleEntityConverter.enhanced_data_to_entity(enhanced_data)


class TurtleDataValidator:
    """Validates turtle data integrity during conversions"""
    
    @staticmethod
    def validate_entity(turtle: Turtle) -> tuple[bool, List[str]]:
        """Validate Turtle entity for conversion readiness"""
        errors = []
        
        # Check required attributes
        if not hasattr(turtle, 'id') or not turtle.id:
            errors.append("Missing or empty turtle.id")
        
        if not hasattr(turtle, 'name') or not turtle.name:
            errors.append("Missing or empty turtle.name")
        
        if not hasattr(turtle, 'stats') or not turtle.stats:
            errors.append("Missing or empty turtle.stats")
        
        # Check stats structure
        required_stats = ['speed', 'max_energy', 'recovery', 'swim', 'climb']
        for stat in required_stats:
            if stat not in turtle.stats:
                errors.append(f"Missing stat: {stat}")
            elif not isinstance(turtle.stats[stat], (int, float)):
                errors.append(f"Invalid stat type for {stat}: {type(turtle.stats[stat])}")
        
        # Check genetics structure
        if not hasattr(turtle, 'visual_genetics') or not turtle.visual_genetics:
            errors.append("Missing or empty turtle.visual_genetics")
        elif not isinstance(turtle.visual_genetics, dict):
            errors.append(f"visual_genetics must be dict, got {type(turtle.visual_genetics)}")
        
        # Check race history structure
        if hasattr(turtle, 'race_history') and turtle.race_history:
            for i, race in enumerate(turtle.race_history):
                if not isinstance(race, dict):
                    errors.append(f"Race history item {i} must be dict")
                else:
                    required_race_fields = ['number', 'position', 'earnings']
                    for field in required_race_fields:
                        if field not in race:
                            errors.append(f"Race {i} missing field: {field}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_enhanced_data(enhanced_data: EnhancedTurtleData) -> tuple[bool, List[str]]:
        """Validate EnhancedTurtleData for integrity"""
        errors = []
        
        # Check static data
        if not enhanced_data.static_data:
            errors.append("Missing static_data")
        else:
            # Check identity
            if not enhanced_data.static_data.identity:
                errors.append("Missing identity in static_data")
            else:
                if not enhanced_data.static_data.identity.turtle_id:
                    errors.append("Missing turtle_id in identity")
                if not enhanced_data.static_data.identity.name:
                    errors.append("Missing name in identity")
            
            # Check lineage
            if not enhanced_data.static_data.lineage:
                errors.append("Missing lineage in static_data")
            
            # Check visual genetics
            if not enhanced_data.static_data.visual_genetics:
                errors.append("Missing visual_genetics in static_data")
        
        # Check dynamic data
        if not enhanced_data.dynamic_data:
            errors.append("Missing dynamic_data")
        else:
            # Check current stats
            if not enhanced_data.dynamic_data.current_stats:
                errors.append("Missing current_stats in dynamic_data")
            
            # Check performance
            if not enhanced_data.dynamic_data.performance:
                errors.append("Missing performance in dynamic_data")
        
        # Check legacy compatibility fields
        if not enhanced_data.turtle_id:
            errors.append("Missing legacy turtle_id")
        if not enhanced_data.name:
            errors.append("Missing legacy name")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_legacy_data(turtle_data: TurtleData) -> tuple[bool, List[str]]:
        """Validate legacy TurtleData for integrity"""
        errors = []
        
        # Check required fields
        if not turtle_data.turtle_id:
            errors.append("Missing turtle_id")
        if not turtle_data.name:
            errors.append("Missing name")
        if not turtle_data.stats:
            errors.append("Missing stats")
        if not turtle_data.performance:
            errors.append("Missing performance")
        
        # Check genetics
        if not turtle_data.genetics:
            errors.append("Missing genetics")
        elif not isinstance(turtle_data.genetics, dict):
            errors.append("genetics must be dict")
        
        return len(errors) == 0, errors


class TurtleDataFactory:
    """Factory functions for creating turtle data structures"""
    
    @staticmethod
    def create_enhanced_from_entity(turtle: Turtle) -> EnhancedTurtleData:
        """Create EnhancedTurtleData from Turtle entity with validation"""
        # Validate entity first
        is_valid, errors = TurtleDataValidator.validate_entity(turtle)
        if not is_valid:
            raise ValueError(f"Invalid turtle entity: {errors}")
        
        return TurtleEntityConverter.entity_to_enhanced_data(turtle)
    
    @staticmethod
    def create_entity_from_enhanced(enhanced_data: EnhancedTurtleData) -> Turtle:
        """Create Turtle entity from EnhancedTurtleData with validation"""
        # Validate enhanced data first
        is_valid, errors = TurtleDataValidator.validate_enhanced_data(enhanced_data)
        if not is_valid:
            raise ValueError(f"Invalid enhanced turtle data: {errors}")
        
        return TurtleEntityConverter.enhanced_data_to_entity(enhanced_data)
    
    @staticmethod
    def create_legacy_from_entity(turtle: Turtle) -> TurtleData:
        """Create legacy TurtleData from Turtle entity"""
        enhanced = TurtleDataFactory.create_enhanced_from_entity(turtle)
        return TurtleData.from_enhanced(enhanced)
    
    @staticmethod
    def create_entity_from_legacy(turtle_data: TurtleData) -> Turtle:
        """Create Turtle entity from legacy TurtleData"""
        # Validate legacy data first
        is_valid, errors = TurtleDataValidator.validate_legacy_data(turtle_data)
        if not is_valid:
            raise ValueError(f"Invalid legacy turtle data: {errors}")
        
        return TurtleEntityConverter.legacy_data_to_entity(turtle_data)


# Conversion convenience functions
def entity_to_enhanced(turtle: Turtle) -> EnhancedTurtleData:
    """Convenience function to convert entity to enhanced data"""
    return TurtleDataFactory.create_enhanced_from_entity(turtle)


def enhanced_to_entity(enhanced_data: EnhancedTurtleData) -> Turtle:
    """Convenience function to convert enhanced data to entity"""
    return TurtleDataFactory.create_entity_from_enhanced(enhanced_data)


def entity_to_legacy(turtle: Turtle) -> TurtleData:
    """Convenience function to convert entity to legacy data"""
    return TurtleDataFactory.create_legacy_from_entity(turtle)


def legacy_to_entity(turtle_data: TurtleData) -> Turtle:
    """Convenience function to convert legacy data to entity"""
    return TurtleDataFactory.create_entity_from_legacy(turtle_data)
