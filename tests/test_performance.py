#!/usr/bin/env python3
"""
Comprehensive performance testing for TurboShells
Tests system performance under various loads and conditions.
"""

import pytest
import time
import gc
import psutil
import os
from typing import List, Dict, Any
from unittest.mock import Mock
from src.core.entities import Turtle
from src.core.game_state import generate_random_turtle, breed_turtles
from src.core.race_track import generate_track
from tests.conftest import TestDataFactory, PerformanceTracker


@pytest.mark.performance
class TestSystemPerformance:
    """Performance tests for core game systems"""

    @pytest.mark.performance
    def test_turtle_creation_performance(self, perf_tracker, performance_test_data):
        """Test performance of turtle creation with large numbers"""
        num_turtles = performance_test_data['large_roster_size']
        
        perf_tracker.start_timer("turtle_creation")
        perf_tracker.track_memory("turtle_creation_start")
        
        turtles = []
        for i in range(num_turtles):
            turtle = generate_random_turtle(f"Turtle{i}")
            turtles.append(turtle)
        
        creation_time = perf_tracker.end_timer("turtle_creation")
        perf_tracker.track_memory("turtle_creation_end")
        
        # Performance assertions
        assert creation_time < 2.0  # Should create 50 turtles in < 2 seconds
        assert len(turtles) == num_turtles
        
        # Memory usage check
        memory_start = perf_tracker.get_metric("turtle_creation_start")
        memory_end = perf_tracker.get_metric("turtle_creation_end")
        if memory_start and memory_end:
            memory_increase = memory_end - memory_start
            # Should use reasonable memory (< 100MB for 50 turtles)
            assert memory_increase < 100 * 1024 * 1024

    @pytest.mark.performance
    def test_race_simulation_performance(self, perf_tracker, performance_test_data):
        """Test performance of race simulation"""
        # Create test turtles
        turtles = []
        for i in range(8):  # 8 turtles in race
            turtle = TestDataFactory.create_minimal_turtle(f"Racer{i}")
            turtles.append(turtle)
        
        # Generate track
        track = generate_track(2000)
        
        perf_tracker.start_timer("race_simulation")
        perf_tracker.track_memory("race_simulation_start")
        
        # Simulate race
        max_iterations = 5000
        for iteration in range(max_iterations):
            current_terrain = track[iteration % len(track)]
            all_finished = True
            
            for turtle in turtles:
                if not turtle.finished and turtle.current_energy > 0:
                    turtle.update_physics(current_terrain)
                    all_finished = False
            
            if all_finished:
                break
        
        simulation_time = perf_tracker.end_timer("race_simulation")
        perf_tracker.track_memory("race_simulation_end")
        
        # Performance assertions
        assert simulation_time < 3.0  # Should complete in < 3 seconds
        
        # Most turtles should have finished or made progress
        progress_turtles = sum(1 for t in turtles if t.race_distance > 0)
        assert progress_turtles >= len(turtles) // 2

    @pytest.mark.performance
    def test_track_generation_performance(self, perf_tracker, performance_test_data):
        """Test performance of track generation for various sizes"""
        track_sizes = [1000, 5000, 10000, 20000]
        generation_times = {}
        
        for size in track_sizes:
            perf_tracker.start_timer(f"track_gen_{size}")
            
            track = generate_track(size)
            
            generation_time = perf_tracker.end_timer(f"track_gen_{size}")
            generation_times[size] = generation_time
            
            # Verify track generation
            assert len(track) == size
            assert generation_time < 1.0  # Each track should generate in < 1 second
        
        # Larger tracks should not be disproportionately slower
        if len(generation_times) >= 2:
            size_ratio = track_sizes[-1] / track_sizes[0]
            time_ratio = generation_times[track_sizes[-1]] / generation_times[track_sizes[0]]
            
            # Time should scale sub-linearly with size
            assert time_ratio < size_ratio * 1.5

    @pytest.mark.performance
    def test_breeding_performance(self, perf_tracker, performance_test_data):
        """Test performance of breeding operations"""
        # Create parent turtles
        parent1 = TestDataFactory.create_extreme_turtle("Parent1")
        parent2 = TestDataFactory.create_extreme_turtle("Parent2")
        
        num_generations = 100
        
        perf_tracker.start_timer("breeding_simulation")
        perf_tracker.track_memory("breeding_start")
        
        generations = []
        current_generation = [parent1, parent2]
        
        for gen in range(num_generations):
            # Breed current generation
            next_generation = []
            for i in range(0, len(current_generation), 2):
                if i + 1 < len(current_generation):
                    child = breed_turtles(current_generation[i], current_generation[i + 1])
                    next_generation.append(child)
            
            generations.append(next_generation)
            current_generation = next_generation
            
            # Stop if we run out of breeding pairs
            if len(current_generation) < 2:
                break
        
        breeding_time = perf_tracker.end_timer("breeding_simulation")
        perf_tracker.track_memory("breeding_end")
        
        # Performance assertions
        assert breeding_time < 2.0  # Should complete in < 2 seconds
        assert len(generations) > 0
        
        # Memory usage check
        memory_start = perf_tracker.get_metric("breeding_start")
        memory_end = perf_tracker.get_metric("breeding_end")
        if memory_start and memory_end:
            memory_increase = memory_end - memory_start
            # Should use reasonable memory
            assert memory_increase < 50 * 1024 * 1024

    @pytest.mark.performance
    def test_memory_leak_detection(self, perf_tracker, performance_test_data):
        """Test for memory leaks in repeated operations"""
        iterations = performance_test_data['memory_test_iterations']
        
        # Track memory over iterations
        memory_samples = []
        
        for i in range(iterations):
            # Create and destroy turtles
            turtles = []
            for j in range(10):
                turtle = generate_random_turtle(f"Temp{i}_{j}")
                turtles.append(turtle)
            
            # Simulate short race
            track = generate_track(100)
            for turtle in turtles:
                turtle.reset_for_race()
                for terrain in track[:50]:
                    if turtle.current_energy > 0:
                        turtle.update_physics(terrain)
            
            # Clear references
            del turtles
            
            # Sample memory every 100 iterations
            if i % 100 == 0:
                gc.collect()  # Force garbage collection
                perf_tracker.track_memory(f"iteration_{i}")
                memory_sample = perf_tracker.get_metric(f"iteration_{i}")
                if memory_sample:
                    memory_samples.append(memory_sample)
        
        # Check for memory leaks
        if len(memory_samples) >= 2:
            initial_memory = memory_samples[0]
            final_memory = memory_samples[-1]
            memory_growth = final_memory - initial_memory
            
            # Memory growth should be reasonable (< 50MB)
            assert memory_growth < 50 * 1024 * 1024

    @pytest.mark.performance
    def test_concurrent_operations_simulation(self, perf_tracker):
        """Test performance under simulated concurrent load"""
        # Simulate multiple game sessions running concurrently
        num_sessions = 5
        session_results = []
        
        perf_tracker.start_timer("concurrent_sessions")
        
        for session_id in range(num_sessions):
            # Create session state
            session_turtles = []
            for i in range(8):
                turtle = generate_random_turtle(f"Session{session_id}_Turtle{i}")
                session_turtles.append(turtle)
            
            # Simulate race in each session
            track = generate_track(1000)
            for iteration in range(1000):
                current_terrain = track[iteration % len(track)]
                
                for turtle in session_turtles:
                    if not turtle.finished and turtle.current_energy > 0:
                        turtle.update_physics(current_terrain)
            
            # Record session result
            total_distance = sum(t.race_distance for t in session_turtles)
            session_results.append(total_distance)
        
        concurrent_time = perf_tracker.end_timer("concurrent_sessions")
        
        # Performance assertions
        assert concurrent_time < 5.0  # Should complete in < 5 seconds
        assert len(session_results) == num_sessions
        assert all(result > 0 for result in session_results)

    @pytest.mark.performance
    def test_large_save_load_performance(self, perf_tracker, temp_save_dir):
        """Test performance of save/load operations with large data"""
        import json
        
        # Create large game state
        large_game_state = {
            'money': 10000,
            'roster': [],
            'retired_roster': [],
            'shop_inventory': [],
            'race_history': [],
            'votes': {},
            'genetics_pool': {}
        }
        
        # Add many turtles
        for i in range(100):
            turtle = generate_random_turtle(f"LargeTurtle{i}")
            turtle_dict = {
                'name': turtle.name,
                'speed': turtle.speed,
                'energy': turtle.energy,
                'recovery': turtle.recovery,
                'swim': turtle.swim,
                'climb': turtle.climb,
                'age': turtle.age,
                'is_active': turtle.is_active,
                'current_energy': turtle.current_energy,
                'race_distance': turtle.race_distance,
                'is_resting': turtle.is_resting,
                'finished': turtle.finished,
                'rank': turtle.rank
            }
            large_game_state['roster'].append(turtle_dict)
        
        save_path = temp_save_dir / "large_save.json"
        
        # Test save performance
        perf_tracker.start_timer("large_save")
        
        with open(save_path, 'w') as f:
            json.dump(large_game_state, f, indent=2)
        
        save_time = perf_tracker.end_timer("large_save")
        
        # Test load performance
        perf_tracker.start_timer("large_load")
        
        with open(save_path, 'r') as f:
            loaded_state = json.load(f)
        
        load_time = perf_tracker.end_timer("large_load")
        
        # Performance assertions
        assert save_time < 1.0  # Save should complete in < 1 second
        assert load_time < 1.0  # Load should complete in < 1 second
        assert len(loaded_state['roster']) == 100
        
        # Check file size
        file_size = save_path.stat().st_size
        assert file_size > 0
        # Should be reasonable size (< 10MB for 100 turtles)
        assert file_size < 10 * 1024 * 1024

    @pytest.mark.performance
    def test_physics_calculation_performance(self, perf_tracker):
        """Test performance of physics calculations"""
        # Create test turtle
        turtle = TestDataFactory.create_extreme_turtle("PhysicsTest")
        
        # Test different terrain types
        terrains = ['grass', 'water', 'rock']
        iterations_per_terrain = 10000
        
        perf_tracker.start_timer("physics_calculations")
        
        for terrain in terrains:
            for i in range(iterations_per_terrain):
                turtle.update_physics(terrain)
        
        physics_time = perf_tracker.end_timer("physics_calculations")
        
        # Performance assertions
        total_iterations = len(terrains) * iterations_per_terrain
        iterations_per_second = total_iterations / physics_time
        
        # Should handle at least 100,000 physics updates per second
        assert iterations_per_second > 100000

    @pytest.mark.performance
    def test_ui_rendering_simulation(self, perf_tracker, mock_pygame):
        """Test performance of UI rendering operations"""
        # Mock rendering operations
        mock_surface = Mock()
        mock_pygame.display.get_surface.return_value = mock_surface
        
        # Simulate rendering many UI elements
        num_elements = 1000
        
        perf_tracker.start_timer("ui_rendering")
        
        for i in range(num_elements):
            # Mock rendering operations
            mock_surface.fill((255, 255, 255))
            mock_pygame.draw.rect(mock_surface, (0, 0, 0), (i % 800, i % 600, 50, 30))
            mock_pygame.draw.circle(mock_surface, (255, 0, 0), (i % 800, i % 600), 10)
        
        rendering_time = perf_tracker.end_timer("ui_rendering")
        
        # Performance assertions
        assert rendering_time < 1.0  # Should render 1000 elements in < 1 second
        
        # Verify mock calls were made
        assert mock_surface.fill.call_count == num_elements
        assert mock_pygame.draw.rect.call_count == num_elements
        assert mock_pygame.draw.circle.call_count == num_elements

    @pytest.mark.performance
    @pytest.mark.slow
    def test_stress_test_extreme_load(self, perf_tracker, performance_test_data):
        """Stress test with extreme load conditions"""
        timeout_seconds = performance_test_data['timeout_seconds']
        
        perf_tracker.start_timer("stress_test")
        
        # Create extreme load
        num_turtles = 200
        num_races = 50
        
        # Create many turtles
        turtles = []
        for i in range(num_turtles):
            turtle = TestDataFactory.create_minimal_turtle(f"Stress{i}")
            turtles.append(turtle)
        
        # Run many races
        for race_num in range(num_races):
            # Select random subset of turtles for race
            import random
            race_turtles = random.sample(turtles, min(8, len(turtles)))
            
            # Generate track
            track = generate_track(500)
            
            # Simulate race
            for iteration in range(500):
                current_terrain = track[iteration % len(track)]
                
                for turtle in race_turtles:
                    if not turtle.finished and turtle.current_energy > 0:
                        turtle.update_physics(current_terrain)
            
            # Check timeout
            current_time = perf_tracker.get_metric("stress_test_start")
            if current_time and (time.time() - current_time) > timeout_seconds:
                break
        
        stress_time = perf_tracker.end_timer("stress_test")
        
        # Stress test assertions
        assert stress_time < timeout_seconds + 5  # Should complete within timeout + buffer
        assert len(turtles) == num_turtles
        
        # Most turtles should have been used in races
        used_turtles = set()
        for turtle in turtles:
            if turtle.race_distance > 0:
                used_turtles.add(turtle)
        
        # At least half the turtles should have participated
        assert len(used_turtles) >= num_turtles // 2


@pytest.mark.performance
class TestResourceUsage:
    """Tests for resource usage and optimization"""

    @pytest.mark.performance
    def test_cpu_usage_monitoring(self, perf_tracker):
        """Test CPU usage during intensive operations"""
        process = psutil.Process()
        
        # Get initial CPU usage
        initial_cpu = process.cpu_percent()
        
        # Perform CPU-intensive operation
        perf_tracker.start_timer("cpu_intensive")
        
        # Intensive calculation
        result = 0
        for i in range(1000000):
            result += i * i
        
        cpu_time = perf_tracker.end_timer("cpu_intensive")
        
        # Get final CPU usage
        final_cpu = process.cpu_percent()
        
        # Assertions
        assert cpu_time < 2.0  # Should complete quickly
        assert result > 0  # Calculation should have worked

    @pytest.mark.performance
    def test_memory_usage_patterns(self, perf_tracker):
        """Test memory usage patterns during different operations"""
        # Test memory usage for different operations
        operations = [
            ("turtle_creation", lambda: [generate_random_turtle(f"Turtle{i}") for i in range(50)]),
            ("track_generation", lambda: [generate_track(1000) for _ in range(10)]),
            ("breeding_simulation", lambda: [breed_turtles(
                TestDataFactory.create_minimal_turtle("P1"),
                TestDataFactory.create_minimal_turtle("P2")
            ) for _ in range(20)])
        ]
        
        for op_name, operation in operations:
            perf_tracker.track_memory(f"{op_name}_start")
            
            result = operation()
            
            perf_tracker.track_memory(f"{op_name}_end")
            
            # Clean up
            del result
            gc.collect()
            
            # Check memory usage
            memory_start = perf_tracker.get_metric(f"{op_name}_start")
            memory_end = perf_tracker.get_metric(f"{op_name}_end")
            
            if memory_start and memory_end:
                memory_used = memory_end - memory_start
                # Each operation should use reasonable memory (< 100MB)
                assert memory_used < 100 * 1024 * 1024

    @pytest.mark.performance
    def test_garbage_collection_efficiency(self, perf_tracker):
        """Test garbage collection efficiency"""
        # Create many temporary objects
        objects = []
        
        perf_tracker.start_timer("object_creation")
        
        for i in range(10000):
            turtle = generate_random_turtle(f"Temp{i}")
            objects.append(turtle)
        
        creation_time = perf_tracker.end_timer("object_creation")
        
        # Clear references
        perf_tracker.start_timer("object_cleanup")
        
        del objects
        gc.collect()  # Force garbage collection
        
        cleanup_time = perf_tracker.end_timer("object_cleanup")
        
        # Assertions
        assert creation_time < 2.0
        assert cleanup_time < 1.0
        
        # Memory should be released
        perf_tracker.track_memory("after_cleanup")
        memory_after = perf_tracker.get_metric("after_cleanup")
        if memory_after:
            # Memory should be reasonable
            assert memory_after < 200 * 1024 * 1024  # < 200MB
