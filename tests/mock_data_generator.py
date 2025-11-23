#!/usr/bin/env python3
"""
Mock Data Generators for TurboShells Testing
Provides realistic test data for all game entities and scenarios.
"""

import random
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import json
from datetime import datetime, timedelta

# Add project root to path for imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class MockTurtleData:
    """Mock turtle data structure for testing"""
    name: str
    speed: float
    energy: float
    recovery: float
    swim: float
    climb: float
    age: int
    is_active: bool
    shop_cost: int = None
    current_energy: float = None
    race_distance: float = 0.0
    is_resting: bool = False
    finished: bool = False
    rank: int = 0


@dataclass
class MockRaceData:
    """Mock race data structure for testing"""
    track_length: int
    terrain_distribution: Dict[str, int]
    participants: List[MockTurtleData]
    weather_condition: str
    race_type: str


class MockDataGenerator:
    """Generates realistic mock data for testing purposes"""

    # Realistic turtle name pools
    FIRST_NAMES = [
        "Speedy", "Shelly", "Turbo", "Dash", "Flash", "Zoom", "Rocket", "Bolt",
        "Swift", "Rapid", "Quick", "Ace", "Jet", "Lightning", "Comet", "Star",
        "Nimbus", "Storm", "Blaze", "Phoenix", "Shadow", "Ghost", "Stealth",
        "Ninja", "Samurai", "Warrior", "Champion", "Legend", "Mythic"
    ]

    LAST_NAMES = [
        "Shell", "Tortoise", "Slider", "Crawler", "Walker", "Runner", "Racer",
        "Sprinter", "Marathon", "Dash", "Zoom", "Flash", "Blaze", "Storm",
        "Thunder", "Lightning", "Comet", "Meteor", "Star", "Nova", "Eclipse",
        "Shadow", "Ghost", "Spirit", "Phantom", "Mystic", "Ancient", "Elder"
    ]

    # Realistic stat ranges based on game balance
    STAT_RANGES = {
        'speed': (1.0, 10.0),
        'energy': (50.0, 150.0),
        'recovery': (0.5, 5.0),
        'swim': (0.5, 3.0),
        'climb': (0.5, 3.0)
    }

    # Cost calculation based on stats
    BASE_COST = 20
    STAT_MULTIPLIER = 2

    def __init__(self, seed: int = None):
        """Initialize with optional seed for reproducible tests"""
        if seed:
            random.seed(seed)
        self.turtle_counter = 0

    def generate_turtle(self,
                        name_prefix: str = None,
                        stat_ranges: Dict[str, Tuple[float, float]] = None,
                        age_range: Tuple[int, int] = (1, 10),
                        is_active: bool = True) -> MockTurtleData:
        """Generate a single realistic turtle"""

        # Generate name
        if name_prefix:
            name = f"{name_prefix} {self.turtle_counter}"
        else:
            first = random.choice(self.FIRST_NAMES)
            last = random.choice(self.LAST_NAMES)
            name = f"{first} {last}"

        # Use custom stat ranges if provided
        ranges = stat_ranges or self.STAT_RANGES

        # Generate stats with realistic distribution
        speed = self._realistic_stat('speed', ranges['speed'])
        energy = self._realistic_stat('energy', ranges['energy'])
        recovery = self._realistic_stat('recovery', ranges['recovery'])
        swim = self._realistic_stat('swim', ranges['swim'])
        climb = self._realistic_stat('climb', ranges['climb'])

        # Calculate shop cost based on stats
        shop_cost = self.calculate_shop_cost(speed, energy, recovery, swim, climb)

        # Generate age
        age = random.randint(*age_range)

        # Create turtle data
        turtle = MockTurtleData(
            name=name,
            speed=speed,
            energy=energy,
            recovery=recovery,
            swim=swim,
            climb=climb,
            age=age,
            is_active=is_active,
            shop_cost=shop_cost,
            current_energy=energy  # Start with full energy
        )

        self.turtle_counter += 1
        return turtle

    def _realistic_stat(self, stat_name: str, range_tuple: Tuple[float, float]) -> float:
        """Generate realistic stat values with proper distribution"""
        min_val, max_val = range_tuple

        # Use different distributions for different stats
        if stat_name == 'speed':
            # Speed tends toward higher values (competitive advantage)
            return round(random.triangular(min_val, max_val, (min_val + max_val) * 0.7), 2)
        elif stat_name == 'energy':
            # Energy is normally distributed
            return round(random.normalvariate((min_val + max_val) / 2, (max_val - min_val) / 6), 1)
        elif stat_name in ['swim', 'climb']:
            # Swim and climb tend toward lower values (specialized stats)
            return round(random.triangular(min_val, max_val, (min_val + max_val) * 0.3), 2)
        else:
            # Recovery is uniform
            return round(random.uniform(min_val, max_val), 2)

    def calculate_shop_cost(self, speed: float, energy: float, recovery: float,
                            swim: float, climb: float) -> int:
        """Calculate realistic shop cost based on turtle stats"""
        total_stats = speed + (energy / 10) + recovery + swim + climb
        cost = int(self.BASE_COST + (total_stats * self.STAT_MULTIPLIER))
        return max(cost, 10)  # Minimum cost of 10

    def generate_turtle_batch(self, count: int, **kwargs) -> List[MockTurtleData]:
        """Generate a batch of turtles"""
        return [self.generate_turtle(**kwargs) for _ in range(count)]

    def generate_roster(self, active_count: int = 3, retired_count: int = 5) -> Dict[str, List[MockTurtleData]]:
        """Generate a complete roster with active and retired turtles"""

        # Generate active turtles (generally better stats)
        active_turtles = self.generate_turtle_batch(
            active_count,
            stat_ranges={
                'speed': (5.0, 9.0),
                'energy': (80.0, 140.0),
                'recovery': (2.0, 4.5),
                'swim': (1.0, 2.5),
                'climb': (1.0, 2.5)
            },
            age_range=(1, 5),
            is_active=True
        )

        # Generate retired turtles (mixed stats)
        retired_turtles = self.generate_turtle_batch(
            retired_count,
            stat_ranges={
                'speed': (3.0, 8.0),
                'energy': (60.0, 120.0),
                'recovery': (1.5, 4.0),
                'swim': (0.8, 2.2),
                'climb': (0.8, 2.2)
            },
            age_range=(3, 12),
            is_active=False
        )

        return {
            'active': active_turtles,
            'retired': retired_turtles
        }

    def generate_shop_inventory(self, count: int = 3, quality: str = 'mixed') -> List[MockTurtleData]:
        """Generate shop inventory with specified quality"""

        if quality == 'high':
            stat_ranges = {
                'speed': (6.0, 9.5),
                'energy': (90.0, 150.0),
                'recovery': (2.5, 5.0),
                'swim': (1.5, 3.0),
                'climb': (1.5, 3.0)
            }
        elif quality == 'low':
            stat_ranges = {
                'speed': (2.0, 5.5),
                'energy': (50.0, 90.0),
                'recovery': (1.0, 2.5),
                'swim': (0.5, 1.5),
                'climb': (0.5, 1.5)
            }
        else:  # mixed
            stat_ranges = self.STAT_RANGES

        return self.generate_turtle_batch(count, stat_ranges=stat_ranges, is_active=True)

    def generate_race_data(self, participant_count: int = 6) -> MockRaceData:
        """Generate realistic race data"""

        # Generate track
        track_length = random.randint(800, 1200)

        # Generate terrain distribution
        terrain_types = ['grass', 'water', 'rock']
        terrain_distribution = {}
        remaining = track_length

        for terrain in terrain_types[:-1]:
            amount = random.randint(int(track_length * 0.2), int(track_length * 0.4))
            terrain_distribution[terrain] = amount
            remaining -= amount

        terrain_distribution[terrain_types[-1]] = remaining

        # Generate participants
        participants = self.generate_turtle_batch(participant_count)

        # Generate weather and race type
        weather_conditions = ['sunny', 'cloudy', 'rainy', 'windy']
        race_types = ['sprint', 'endurance', 'mixed']

        return MockRaceData(
            track_length=track_length,
            terrain_distribution=terrain_distribution,
            participants=participants,
            weather_condition=random.choice(weather_conditions),
            race_type=random.choice(race_types)
        )

    def generate_breeding_parents(self) -> Tuple[MockTurtleData, MockTurtleData]:
        """Generate two suitable breeding parents"""

        # Generate retired turtles with good stats for breeding
        parent1 = self.generate_turtle(
            stat_ranges={
                'speed': (6.0, 9.0),
                'energy': (80.0, 140.0),
                'recovery': (2.5, 4.5),
                'swim': (1.2, 2.8),
                'climb': (1.2, 2.8)
            },
            age_range=(4, 8),
            is_active=False
        )

        parent2 = self.generate_turtle(
            stat_ranges={
                'speed': (6.0, 9.0),
                'energy': (80.0, 140.0),
                'recovery': (2.5, 4.5),
                'swim': (1.2, 2.8),
                'climb': (1.2, 2.8)
            },
            age_range=(4, 8),
            is_active=False
        )

        return parent1, parent2

    def generate_test_scenarios(self) -> Dict[str, Any]:
        """Generate comprehensive test scenarios"""

        return {
            'new_game': {
                'money': 50,
                'roster': self.generate_roster(active_count=1, retired_count=0),
                'shop_inventory': self.generate_shop_inventory(3, 'mixed')
            },
            'mid_game': {
                'money': random.randint(200, 800),
                'roster': self.generate_roster(active_count=3, retired_count=3),
                'shop_inventory': self.generate_shop_inventory(3, 'high')
            },
            'late_game': {
                'money': random.randint(1000, 5000),
                'roster': self.generate_roster(active_count=3, retired_count=8),
                'shop_inventory': self.generate_shop_inventory(3, 'high')
            },
            'breeding_scenario': {
                'parents': self.generate_breeding_parents(),
                'roster_space': True
            },
            'race_scenario': self.generate_race_data(6)
        }

    def export_test_data(self, filename: str = 'test_data.json') -> None:
        """Export generated test data to JSON file"""
        test_data = self.generate_test_scenarios()

        # Convert dataclasses to dicts for JSON serialization
        json_data = {}
        for key, value in test_data.items():
            if isinstance(value, dict):
                json_data[key] = {}
                for sub_key, sub_value in value.items():
                    if hasattr(sub_value, '__dict__'):
                        json_data[key][sub_key] = sub_value.__dict__
                    elif isinstance(sub_value, list):
                        json_data[key][sub_key] = [item.__dict__ if hasattr(
                            item, '__dict__') else item for item in sub_value]
                    else:
                        json_data[key][sub_key] = sub_value
            else:
                json_data[key] = value.__dict__ if hasattr(value, '__dict__') else value

        with open(filename, 'w') as f:
            json.dump(json_data, f, indent=2)

        print(f"Test data exported to {filename}")


# Example usage and testing
if __name__ == "__main__":
    # Test the mock data generator
    generator = MockDataGenerator(seed=42)  # Reproducible tests

    print("[TEST] Testing Mock Data Generator")
    print("=" * 50)

    # Generate test turtle
    turtle = generator.generate_turtle()
    print(f"Generated turtle: {turtle.name}")
    print(f"Stats: Speed={turtle.speed}, Energy={turtle.energy}, Cost=${turtle.shop_cost}")

    # Generate roster
    roster = generator.generate_roster()
    print(f"\nGenerated roster: {len(roster['active'])} active, {len(roster['retired'])} retired")

    # Generate race data
    race = generator.generate_race_data()
    print(f"\nGenerated race: {race.track_length}m track, {len(race.participants)} participants")

    # Generate test scenarios
    scenarios = generator.generate_test_scenarios()
    print(f"\nGenerated {len(scenarios)} test scenarios")

    # Export test data
    generator.export_test_data('tests/mock_test_data.json')
    print("\n[PASS] Mock data generator test complete!")
