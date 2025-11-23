"""
Data Performance Optimization for TurboShells

This module contains only performance optimization logic,
following Single Responsibility Principle.
"""

import gzip
import hashlib
from functools import lru_cache
from typing import Dict, Any, Optional
import time
import json


class DataCache:
    """LRU cache for frequently accessed data"""

    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._cache = {}
        self._access_times = {}

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        if key in self._cache:
            self._access_times[key] = time.time()
            return self._cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Set item in cache"""
        if len(self._cache) >= self.max_size:
            self._evict_oldest()

        self._cache[key] = value
        self._access_times[key] = time.time()

    def _evict_oldest(self) -> None:
        """Remove oldest item from cache"""
        if not self._access_times:
            return

        oldest_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        del self._cache[oldest_key]
        del self._access_times[oldest_key]

    def clear(self) -> None:
        """Clear cache"""
        self._cache.clear()
        self._access_times.clear()


class PerformanceOptimizer:
    """Performance optimization utilities for data operations"""

    def __init__(self):
        self.turtle_cache = DataCache(max_size=100)
        self.game_cache = DataCache(max_size=10)
        self.preference_cache = DataCache(max_size=50)

        # Compression settings
        self.compression_enabled = True
        self.compression_level = 6
        self.compression_threshold = 1024  # Only compress data larger than 1KB

    def cached_validate_game_data(self, data_hash: str, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Cached game data validation"""
        from .data_validation import DataValidator
        validator = DataValidator()
        return validator.validate_game_data(data)

    @lru_cache(maxsize=1000)
    def cached_validate_turtle_data(self, data_hash: str, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Cached turtle data validation"""
        from .data_validation import DataValidator
        validator = DataValidator()
        return validator.validate_turtle_data(data)

    @lru_cache(maxsize=1000)
    def cached_validate_preference_data(self, data_hash: str, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Cached preference data validation"""
        from .data_validation import DataValidator
        validator = DataValidator()
        return validator.validate_preference_data(data)

    def calculate_data_hash(self, data: Dict[str, Any]) -> str:
        """Calculate hash for data caching"""
        data_string = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(data_string.encode('utf-8')).hexdigest()

    def compress_data_optimized(self, data: str) -> bytes:
        """Optimized compression with threshold"""
        if not self.compression_enabled:
            return data.encode('utf-8')

        data_bytes = data.encode('utf-8')

        # Only compress if data is larger than threshold
        if len(data_bytes) < self.compression_threshold:
            return data_bytes

        return gzip.compress(data_bytes, compresslevel=self.compression_level)

    def decompress_data_optimized(self, compressed_data: bytes) -> str:
        """Optimized decompression with fallback"""
        try:
            # Try to decompress
            return gzip.decompress(compressed_data).decode('utf-8')
        except (gzip.BadGzipFile, OSError):
            # Fallback to uncompressed data
            return compressed_data.decode('utf-8')

    def get_cached_turtle(self, turtle_id: str, turtle_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get turtle data from cache or cache it"""
        cached = self.turtle_cache.get(turtle_id)
        if cached:
            return cached

        # Cache the data
        self.turtle_cache.set(turtle_id, turtle_data)
        return turtle_data

    def get_cached_game_data(self, player_id: str, game_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get game data from cache or cache it"""
        cached = self.game_cache.get(player_id)
        if cached:
            return cached

        # Cache the data
        self.game_cache.set(player_id, game_data)
        return game_data

    def get_cached_preferences(self, player_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Get preference data from cache or cache it"""
        cached = self.preference_cache.get(player_id)
        if cached:
            return cached

        # Cache the data
        self.preference_cache.set(player_id, preferences)
        return preferences

    def invalidate_cache(self, cache_type: str = "all") -> None:
        """Invalidate specified cache"""
        if cache_type == "all" or cache_type == "turtle":
            self.turtle_cache.clear()
        if cache_type == "all" or cache_type == "game":
            self.game_cache.clear()
        if cache_type == "all" or cache_type == "preference":
            self.preference_cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "turtle_cache_size": len(self.turtle_cache._cache),
            "game_cache_size": len(self.game_cache._cache),
            "preference_cache_size": len(self.preference_cache._cache),
            "compression_enabled": self.compression_enabled,
            "compression_level": self.compression_level,
            "compression_threshold": self.compression_threshold
        }


# ============================================================================
# GLOBAL OPTIMIZER INSTANCE
# ============================================================================

performance_optimizer = PerformanceOptimizer()
