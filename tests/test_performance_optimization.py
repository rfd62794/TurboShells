#!/usr/bin/env python3
"""
Comprehensive unit tests for performance optimization
Tests caching, lazy loading, and performance monitoring.
"""

import pytest
import time
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


class MockCache:
    """Mock cache for testing"""
    
    def __init__(self):
        self.cache = {}
        self.hits = 0
        self.misses = 0
    
    def get(self, key):
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        else:
            self.misses += 1
            return None
    
    def set(self, key, value):
        self.cache[key] = value
    
    def clear(self):
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_hit_ratio(self):
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0


class MockPerformanceMonitor:
    """Mock performance monitor"""
    
    def __init__(self):
        self.metrics = {}
        self.timers = {}
    
    def start_timer(self, name):
        self.timers[name] = time.time()
    
    def end_timer(self, name):
        if name in self.timers:
            duration = time.time() - self.timers[name]
            self.metrics[name] = duration
            return duration
        return 0
    
    def record_metric(self, name, value):
        self.metrics[name] = value
    
    def get_metric(self, name):
        return self.metrics.get(name, 0)


class TestCachingSystem:
    """Unit tests for caching functionality"""

    @pytest.fixture
    def cache(self):
        """Create a mock cache"""
        return MockCache()

    @pytest.mark.unit
    def test_cache_initialization(self, cache):
        """Test cache initialization"""
        assert cache is not None
        assert len(cache.cache) == 0
        assert cache.hits == 0
        assert cache.misses == 0

    @pytest.mark.unit
    def test_cache_set_and_get(self, cache):
        """Test cache set and get operations"""
        key = "test_key"
        value = "test_value"
        
        cache.set(key, value)
        result = cache.get(key)
        
        assert result == value
        assert cache.hits == 1
        assert cache.misses == 0

    @pytest.mark.unit
    def test_cache_miss(self, cache):
        """Test cache miss behavior"""
        result = cache.get("nonexistent_key")
        
        assert result is None
        assert cache.hits == 0
        assert cache.misses == 1

    @pytest.mark.unit
    def test_cache_hit_ratio(self, cache):
        """Test cache hit ratio calculation"""
        # Add some items
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        # Get some hits
        cache.get("key1")
        cache.get("key2")
        
        # Get some misses
        cache.get("nonexistent1")
        cache.get("nonexistent2")
        
        hit_ratio = cache.get_hit_ratio()
        assert hit_ratio == 0.5  # 2 hits out of 4 total accesses

    @pytest.mark.unit
    def test_cache_clear(self, cache):
        """Test cache clearing"""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        assert len(cache.cache) == 2
        
        cache.clear()
        
        assert len(cache.cache) == 0
        assert cache.hits == 0
        assert cache.misses == 0

    @pytest.mark.unit
    def test_cache_with_complex_objects(self, cache):
        """Test caching complex objects"""
        complex_value = {
            "numbers": [1, 2, 3],
            "nested": {"key": "value"},
            "tuple": (1, 2, 3)
        }
        
        cache.set("complex", complex_value)
        result = cache.get("complex")
        
        assert result == complex_value
        assert result["numbers"] == [1, 2, 3]
        assert result["nested"]["key"] == "value"


class TestLazyLoading:
    """Unit tests for lazy loading functionality"""

    @pytest.mark.unit
    def test_lazy_property_evaluation(self):
        """Test lazy property evaluation"""
        class LazyObject:
            def __init__(self):
                self._expensive_value = None
                self._computed = False
            
            @property
            def expensive_value(self):
                if not self._computed:
                    # Simulate expensive computation
                    time.sleep(0.01)
                    self._expensive_value = "computed_value"
                    self._computed = True
                return self._expensive_value
        
        obj = LazyObject()
        
        # Property should not be computed initially
        assert obj._computed == False
        
        # First access should compute the value
        start_time = time.time()
        value1 = obj.expensive_value
        first_access_time = time.time() - start_time
        
        assert value1 == "computed_value"
        assert obj._computed == True
        assert first_access_time >= 0.01
        
        # Second access should be instant (cached)
        start_time = time.time()
        value2 = obj.expensive_value
        second_access_time = time.time() - start_time
        
        assert value2 == value1
        assert second_access_time < 0.005  # Much faster

    @pytest.mark.unit
    def test_lazy_loading_with_factory(self):
        """Test lazy loading with factory function"""
        def expensive_factory():
            time.sleep(0.01)
            return {"data": "expensive_computation"}
        
        class LazyFactory:
            def __init__(self, factory_func):
                self._factory = factory_func
                self._value = None
                self._loaded = False
            
            def get_value(self):
                if not self._loaded:
                    self._value = self._factory()
                    self._loaded = True
                return self._value
        
        lazy_obj = LazyFactory(expensive_factory)
        
        # Should not be loaded initially
        assert lazy_obj._loaded == False
        
        # First call should trigger factory
        start_time = time.time()
        value1 = lazy_obj.get_value()
        first_time = time.time() - start_time
        
        assert value1["data"] == "expensive_computation"
        assert lazy_obj._loaded == True
        assert first_time >= 0.01
        
        # Second call should be instant
        start_time = time.time()
        value2 = lazy_obj.get_value()
        second_time = time.time() - start_time
        
        assert value2 == value1
        assert second_time < 0.005


class TestPerformanceMonitoring:
    """Unit tests for performance monitoring"""

    @pytest.fixture
    def monitor(self):
        """Create a mock performance monitor"""
        return MockPerformanceMonitor()

    @pytest.mark.unit
    def test_monitor_initialization(self, monitor):
        """Test monitor initialization"""
        assert monitor is not None
        assert len(monitor.metrics) == 0
        assert len(monitor.timers) == 0

    @pytest.mark.unit
    def test_timer_functionality(self, monitor):
        """Test timer functionality"""
        timer_name = "test_timer"
        
        monitor.start_timer(timer_name)
        time.sleep(0.01)  # Small delay
        duration = monitor.end_timer(timer_name)
        
        assert duration >= 0.01
        assert timer_name in monitor.metrics
        assert monitor.metrics[timer_name] == duration

    @pytest.mark.unit
    def test_multiple_timers(self, monitor):
        """Test multiple concurrent timers"""
        timer_names = ["timer1", "timer2", "timer3"]
        
        for name in timer_names:
            monitor.start_timer(name)
        
        time.sleep(0.01)
        
        durations = []
        for name in timer_names:
            duration = monitor.end_timer(name)
            durations.append(duration)
        
        assert len(durations) == 3
        assert all(d >= 0.01 for d in durations)
        assert all(name in monitor.metrics for name in timer_names)

    @pytest.mark.unit
    def test_metric_recording(self, monitor):
        """Test metric recording"""
        metrics = {
            "memory_usage": 1024,
            "cpu_usage": 75.5,
            "operations_per_second": 1000
        }
        
        for name, value in metrics.items():
            monitor.record_metric(name, value)
        
        for name, expected_value in metrics.items():
            assert monitor.get_metric(name) == expected_value

    @pytest.mark.unit
    def test_performance_thresholds(self, monitor):
        """Test performance threshold monitoring"""
        slow_threshold = 0.1  # 100ms
        
        monitor.start_timer("slow_operation")
        time.sleep(0.05)  # 50ms - under threshold
        duration = monitor.end_timer("slow_operation")
        
        assert duration < slow_threshold
        
        monitor.start_timer("very_slow_operation")
        time.sleep(0.15)  # 150ms - over threshold
        duration = monitor.end_timer("very_slow_operation")
        
        assert duration > slow_threshold


class TestMemoryOptimization:
    """Unit tests for memory optimization techniques"""

    @pytest.mark.unit
    def test_object_pooling(self):
        """Test object pooling for memory efficiency"""
        class ObjectPool:
            def __init__(self, factory_func, max_size=10):
                self.factory = factory_func
                self.pool = []
                self.max_size = max_size
            
            def acquire(self):
                if self.pool:
                    return self.pool.pop()
                return self.factory()
            
            def release(self, obj):
                if len(self.pool) < self.max_size:
                    self.pool.append(obj)
        
        def create_expensive_object():
            return {"data": "expensive", "created": time.time()}
        
        pool = ObjectPool(create_expensive_object, max_size=5)
        
        # Acquire objects
        obj1 = pool.acquire()
        obj2 = pool.acquire()
        
        assert obj1 is not obj2
        assert "data" in obj1
        assert "data" in obj2
        
        # Release objects back to pool
        pool.release(obj1)
        pool.release(obj2)
        
        # Acquire again - should reuse from pool
        obj3 = pool.acquire()
        obj4 = pool.acquire()
        
        # Should reuse the same objects (order may vary)
        reused_objects = {obj1, obj2}
        acquired_objects = {obj3, obj4}
        assert reused_objects == acquired_objects

    @pytest.mark.unit
    def test_memory_cleanup(self):
        """Test memory cleanup strategies"""
        class MemoryManager:
            def __init__(self):
                self.resources = []
            
            def allocate_resource(self, size):
                resource = {"size": size, "data": [0] * size}
                self.resources.append(resource)
                return resource
            
            def cleanup_resources(self):
                self.resources.clear()
            
            def get_memory_usage(self):
                return sum(res["size"] for res in self.resources)
        
        manager = MemoryManager()
        
        # Allocate resources
        manager.allocate_resource(100)
        manager.allocate_resource(200)
        manager.allocate_resource(150)
        
        assert manager.get_memory_usage() == 450
        
        # Cleanup
        manager.cleanup_resources()
        
        assert manager.get_memory_usage() == 0
        assert len(manager.resources) == 0

    @pytest.mark.unit
    def test_generator_efficiency(self):
        """Test generator for memory efficiency"""
        def generate_numbers_list(count):
            """Inefficient: creates entire list in memory"""
            return [i for i in range(count)]
        
        def generate_numbers_generator(count):
            """Efficient: yields numbers one at a time"""
            for i in range(count):
                yield i
        
        count = 1000
        
        # List approach (uses more memory)
        start_time = time.time()
        numbers_list = generate_numbers_list(count)
        list_time = time.time() - start_time
        
        # Generator approach (uses less memory)
        start_time = time.time()
        numbers_gen = list(generate_numbers_generator(count))
        generator_time = time.time() - start_time
        
        # Both produce same results
        assert numbers_list == numbers_gen
        
        # Generator should be competitive in performance
        assert generator_time < list_time * 2  # Allow some overhead


class TestAlgorithmOptimization:
    """Unit tests for algorithm optimization"""

    @pytest.mark.unit
    def test_search_algorithms(self):
        """Test different search algorithms"""
        data = list(range(1000))  # Sorted data
        target = 500
        
        # Linear search (O(n))
        start_time = time.time()
        linear_result = None
        for item in data:
            if item == target:
                linear_result = item
                break
        linear_time = time.time() - start_time
        
        # Binary search (O(log n))
        start_time = time.time()
        left, right = 0, len(data) - 1
        binary_result = None
        while left <= right:
            mid = (left + right) // 2
            if data[mid] == target:
                binary_result = data[mid]
                break
            elif data[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        binary_time = time.time() - start_time
        
        assert linear_result == target
        assert binary_result == target
        assert binary_time < linear_time  # Binary should be faster

    @pytest.mark.unit
    def test_caching_memoization(self):
        """Test memoization for expensive computations"""
        class Memoizer:
            def __init__(self):
                self.cache = {}
            
            def fibonacci(self, n):
                if n in self.cache:
                    return self.cache[n]
                
                if n <= 1:
                    result = n
                else:
                    result = self.fibonacci(n - 1) + self.fibonacci(n - 2)
                
                self.cache[n] = result
                return result
        
        memoizer = Memoizer()
        
        # First computation (slower)
        start_time = time.time()
        result1 = memoizer.fibonacci(30)
        first_time = time.time() - start_time
        
        # Second computation (much faster due to caching)
        start_time = time.time()
        result2 = memoizer.fibonacci(30)
        second_time = time.time() - start_time
        
        assert result1 == result2
        assert second_time < first_time / 10  # Should be much faster

    @pytest.mark.unit
    def test_batch_processing(self):
        """Test batch processing efficiency"""
        def process_items_individually(items):
            """Process items one by one"""
            results = []
            for item in items:
                # Simulate processing overhead
                result = item * 2
                results.append(result)
            return results
        
        def process_items_in_batches(items, batch_size=10):
            """Process items in batches"""
            results = []
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                # Simulate batch processing (reduced overhead)
                batch_results = [item * 2 for item in batch]
                results.extend(batch_results)
            return results
        
        items = list(range(100))
        
        # Individual processing
        start_time = time.time()
        result1 = process_items_individually(items)
        individual_time = time.time() - start_time
        
        # Batch processing
        start_time = time.time()
        result2 = process_items_in_batches(items)
        batch_time = time.time() - start_time
        
        assert result1 == result2
        # Batch should be competitive or faster
        assert batch_time <= individual_time * 1.5
