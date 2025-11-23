"""
Turtle SVG Cache System for TurboShells
Advanced caching system with LRU eviction and performance optimization
"""

import time
import hashlib
import pickle
from typing import Dict, Any, Optional, Tuple, List
from collections import OrderedDict
import pygame

try:
    import drawsvg as draw
except ImportError:
    draw = None


class CacheEntry:
    """
    Individual cache entry with metadata
    """
    
    def __init__(self, data: Any, size: int = 0):
        self.data = data
        self.size = size
        self.access_count = 0
        self.last_access = time.time()
        self.created = time.time()
    
    def touch(self):
        """Update access statistics"""
        self.access_count += 1
        self.last_access = time.time()
    
    def get_age(self) -> float:
        """Get age in seconds"""
        return time.time() - self.created
    
    def get_time_since_access(self) -> float:
        """Get time since last access in seconds"""
        return time.time() - self.last_access


class TurtleSVGCache:
    """
    Advanced caching system for SVG and PyGame surfaces
    Implements LRU eviction with intelligent size management
    """
    
    def __init__(self, max_memory_mb: int = 50, max_entries: int = 1000):
        self.max_memory_mb = max_memory_mb
        self.max_entries = max_entries
        self.current_memory_mb = 0.0
        
        # Cache storage
        self.svg_cache = OrderedDict()  # SVG Drawing objects
        self.surface_cache = OrderedDict()  # PyGame surfaces
        self.genetics_cache = OrderedDict()  # Genetics data
        
        # Statistics
        self.stats = {
            'svg_hits': 0,
            'svg_misses': 0,
            'surface_hits': 0,
            'surface_misses': 0,
            'genetics_hits': 0,
            'genetics_misses': 0,
            'evictions': 0,
            'memory_evictions': 0,
            'age_evictions': 0
        }
        
        # Cache configuration
        self.max_age_seconds = 3600  # 1 hour
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
        
        # Size estimation
        self.avg_svg_size = 1024  # 1KB average
        self.avg_surface_size = 40000  # 40KB average (100x100 RGBA)
        self.avg_genetics_size = 512  # 512 bytes average
    
    def generate_cache_key(self, data: Any, prefix: str = "") -> str:
        """
        Generate consistent cache key from data
        """
        if isinstance(data, str):
            # For strings, use hash directly
            key_data = data
        elif isinstance(data, dict):
            # For dictionaries, sort keys and convert to string
            key_data = str(sorted(data.items()))
        elif isinstance(data, (list, tuple)):
            # For sequences, convert to string
            key_data = str(data)
        else:
            # For other objects, use pickle
            try:
                key_data = pickle.dumps(data)
            except:
                key_data = str(data)
        
        # Generate hash
        hash_obj = hashlib.md5(key_data.encode('utf-8'))
        cache_key = f"{prefix}_{hash_obj.hexdigest()}"
        
        return cache_key
    
    def cache_svg(self, genetics: Dict[str, Any], svg_drawing: object) -> str:
        """
        Cache SVG drawing object
        """
        cache_key = self.generate_cache_key(genetics, "svg")
        
        # Estimate size
        svg_size = self.estimate_svg_size(svg_drawing)
        
        # Check if we need to evict
        self._check_memory_limits(svg_size)
        
        # Create cache entry
        entry = CacheEntry(svg_drawing, svg_size)
        self.svg_cache[cache_key] = entry
        
        # Update memory usage
        self.current_memory_mb += svg_size / (1024 * 1024)
        
        return cache_key
    
    def get_cached_svg(self, genetics: Dict[str, Any]) -> Optional[object]:
        """
        Get cached SVG drawing
        """
        cache_key = self.generate_cache_key(genetics, "svg")
        
        if cache_key in self.svg_cache:
            entry = self.svg_cache[cache_key]
            entry.touch()
            self.stats['svg_hits'] += 1
            return entry.data
        
        self.stats['svg_misses'] += 1
        return None
    
    def cache_surface(self, genetics: Dict[str, Any], size: int, surface: pygame.Surface) -> str:
        """
        Cache PyGame surface
        """
        cache_key = self.generate_cache_key((genetics, size), "surface")
        
        # Estimate size
        surface_size = self.estimate_surface_size(surface)
        
        # Check if we need to evict
        self._check_memory_limits(surface_size)
        
        # Create cache entry
        entry = CacheEntry(surface, surface_size)
        self.surface_cache[cache_key] = entry
        
        # Update memory usage
        self.current_memory_mb += surface_size / (1024 * 1024)
        
        return cache_key
    
    def get_cached_surface(self, genetics: Dict[str, Any], size: int) -> Optional[pygame.Surface]:
        """
        Get cached PyGame surface
        """
        cache_key = self.generate_cache_key((genetics, size), "surface")
        
        if cache_key in self.surface_cache:
            entry = self.surface_cache[cache_key]
            entry.touch()
            self.stats['surface_hits'] += 1
            return entry.data
        
        self.stats['surface_misses'] += 1
        return None
    
    def cache_genetics(self, genetics_hash: str, genetics: Dict[str, Any]) -> str:
        """
        Cache genetics data
        """
        cache_key = self.generate_cache_key(genetics_hash, "genetics")
        
        # Estimate size
        genetics_size = self.estimate_genetics_size(genetics)
        
        # Check if we need to evict
        self._check_memory_limits(genetics_size)
        
        # Create cache entry
        entry = CacheEntry(genetics, genetics_size)
        self.genetics_cache[cache_key] = entry
        
        # Update memory usage
        self.current_memory_mb += genetics_size / (1024 * 1024)
        
        return cache_key
    
    def get_cached_genetics(self, genetics_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get cached genetics data
        """
        cache_key = self.generate_cache_key(genetics_hash, "genetics")
        
        if cache_key in self.genetics_cache:
            entry = self.genetics_cache[cache_key]
            entry.touch()
            self.stats['genetics_hits'] += 1
            return entry.data
        
        self.stats['genetics_misses'] += 1
        return None
    
    def _check_memory_limits(self, new_item_size: int) -> None:
        """
        Check and enforce memory limits
        """
        new_item_mb = new_item_size / (1024 * 1024)
        
        # Check memory limit
        while (self.current_memory_mb + new_item_mb > self.max_memory_mb or 
               len(self.svg_cache) + len(self.surface_cache) + len(self.genetics_cache) > self.max_entries):
            self._evict_lru()
    
    def _evict_lru(self) -> None:
        """
        Evict least recently used items
        """
        # Combine all caches with their access times
        all_items = []
        
        for cache_key, entry in self.svg_cache.items():
            all_items.append(('svg', cache_key, entry))
        
        for cache_key, entry in self.surface_cache.items():
            all_items.append(('surface', cache_key, entry))
        
        for cache_key, entry in self.genetics_cache.items():
            all_items.append(('genetics', cache_key, entry))
        
        # Sort by last access time
        all_items.sort(key=lambda x: x[2].last_access)
        
        # Evict the oldest item
        if all_items:
            cache_type, cache_key, entry = all_items[0]
            
            # Remove from appropriate cache
            if cache_type == 'svg':
                del self.svg_cache[cache_key]
            elif cache_type == 'surface':
                del self.surface_cache[cache_key]
            elif cache_type == 'genetics':
                del self.genetics_cache[cache_key]
            
            # Update memory usage
            self.current_memory_mb -= entry.size / (1024 * 1024)
            self.stats['evictions'] += 1
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired entries
        """
        current_time = time.time()
        expired_count = 0
        
        # Check if cleanup is needed
        if current_time - self.last_cleanup < self.cleanup_interval:
            return 0
        
        # Clean SVG cache
        expired_svg = [key for key, entry in self.svg_cache.items() 
                     if entry.get_age() > self.max_age_seconds]
        for key in expired_svg:
            entry = self.svg_cache[key]
            self.current_memory_mb -= entry.size / (1024 * 1024)
            del self.svg_cache[key]
            expired_count += 1
        
        # Clean surface cache
        expired_surfaces = [key for key, entry in self.surface_cache.items() 
                           if entry.get_age() > self.max_age_seconds]
        for key in expired_surfaces:
            entry = self.surface_cache[key]
            self.current_memory_mb -= entry.size / (1024 * 1024)
            del self.surface_cache[key]
            expired_count += 1
        
        # Clean genetics cache
        expired_genetics = [key for key, entry in self.genetics_cache.items() 
                           if entry.get_age() > self.max_age_seconds]
        for key in expired_genetics:
            entry = self.genetics_cache[key]
            self.current_memory_mb -= entry.size / (1024 * 1024)
            del self.genetics_cache[key]
            expired_count += 1
        
        self.last_cleanup = current_time
        self.stats['age_evictions'] += expired_count
        
        return expired_count
    
    def estimate_svg_size(self, svg_drawing: object) -> int:
        """
        Estimate SVG drawing size in bytes
        """
        if draw is None or svg_drawing is None:
            return self.avg_svg_size
        
        try:
            svg_string = svg_drawing.as_svg()
            return len(svg_string.encode('utf-8'))
        except:
            return self.avg_svg_size
    
    def estimate_surface_size(self, surface: pygame.Surface) -> int:
        """
        Estimate PyGame surface size in bytes
        """
        if surface is None:
            return self.avg_surface_size
        
        try:
            width, height = surface.get_size()
            return width * height * 4  # RGBA = 4 bytes per pixel
        except:
            return self.avg_surface_size
    
    def estimate_genetics_size(self, genetics: Dict[str, Any]) -> int:
        """
        Estimate genetics data size in bytes
        """
        try:
            return len(pickle.dumps(genetics))
        except:
            return self.avg_genetics_size
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics
        """
        total_requests = (self.stats['svg_hits'] + self.stats['svg_misses'] + 
                          self.stats['surface_hits'] + self.stats['surface_misses'] +
                          self.stats['genetics_hits'] + self.stats['genetics_misses'])
        
        total_hits = (self.stats['svg_hits'] + self.stats['surface_hits'] + 
                     self.stats['genetics_hits'])
        
        hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'memory_usage_mb': self.current_memory_mb,
            'memory_limit_mb': self.max_memory_mb,
            'memory_usage_percentage': (self.current_memory_mb / self.max_memory_mb) * 100,
            'total_entries': len(self.svg_cache) + len(self.surface_cache) + len(self.genetics_cache),
            'max_entries': self.max_entries,
            'svg_entries': len(self.svg_cache),
            'surface_entries': len(self.surface_cache),
            'genetics_entries': len(self.genetics_cache),
            'hit_rate_percentage': hit_rate,
            'total_requests': total_requests,
            'total_hits': total_hits,
            'total_misses': total_requests - total_hits,
            'evictions': self.stats['evictions'],
            'age_evictions': self.stats['age_evictions'],
            'memory_evictions': self.stats['memory_evictions'],
            'svg_hit_rate': (self.stats['svg_hits'] / (self.stats['svg_hits'] + self.stats['svg_misses']) * 100) if (self.stats['svg_hits'] + self.stats['svg_misses']) > 0 else 0,
            'surface_hit_rate': (self.stats['surface_hits'] / (self.stats['surface_hits'] + self.stats['surface_misses']) * 100) if (self.stats['surface_hits'] + self.stats['surface_misses']) > 0 else 0,
            'genetics_hit_rate': (self.stats['genetics_hits'] / (self.stats['genetics_hits'] + self.stats['genetics_misses']) * 100) if (self.stats['genetics_hits'] + self.stats['genetics_misses']) > 0 else 0
        }
    
    def get_top_accessed_items(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get most accessed cache items
        """
        all_items = []
        
        for cache_key, entry in self.svg_cache.items():
            all_items.append({
                'type': 'svg',
                'key': cache_key,
                'access_count': entry.access_count,
                'last_access': entry.last_access,
                'age': entry.get_age(),
                'size': entry.size
            })
        
        for cache_key, entry in self.surface_cache.items():
            all_items.append({
                'type': 'surface',
                'key': cache_key,
                'access_count': entry.access_count,
                'last_access': entry.last_access,
                'age': entry.get_age(),
                'size': entry.size
            })
        
        for cache_key, entry in self.genetics_cache.items():
            all_items.append({
                'type': 'genetics',
                'key': cache_key,
                'access_count': entry.access_count,
                'last_access': entry.last_access,
                'age': entry.get_age(),
                'size': entry.size
            })
        
        # Sort by access count
        all_items.sort(key=lambda x: x['access_count'], reverse=True)
        
        return all_items[:count]
    
    def clear_cache(self, cache_type: str = "all") -> int:
        """
        Clear cache entries
        """
        cleared_count = 0
        
        if cache_type in ("all", "svg"):
            cleared_count += len(self.svg_cache)
            self.current_memory_mb -= sum(entry.size for entry in self.svg_cache.values()) / (1024 * 1024)
            self.svg_cache.clear()
        
        if cache_type in ("all", "surface"):
            cleared_count += len(self.surface_cache)
            self.current_memory_mb -= sum(entry.size for entry in self.surface_cache.values()) / (1024 * 1024)
            self.surface_cache.clear()
        
        if cache_type in ("all", "genetics"):
            cleared_count += len(self.genetics_cache)
            self.current_memory_mb -= sum(entry.size for entry in self.genetics_cache.values()) / (1024 * 1024)
            self.genetics_cache.clear()
        
        return cleared_count
    
    def optimize_cache_size(self, target_memory_mb: int = None, target_entries: int = None) -> None:
        """
        Optimize cache size for better performance
        """
        if target_memory_mb is not None:
            self.max_memory_mb = target_memory_mb
        
        if target_entries is not None:
            self.max_entries = target_entries
        
        # Evict entries until within limits
        while self.current_memory_mb > self.max_memory_mb or len(self.svg_cache) + len(self.surface_cache) + len(self.genetics_cache) > self.max_entries:
            self._evict_lru()
    
    def prewarm_cache(self, genetics_list: List[Dict[str, Any]], 
                      svg_generator, surface_renderer) -> None:
        """
        Prewarm cache with common turtle variations
        """
        for genetics in genetics_list:
            # Generate and cache SVG
            svg_drawing = svg_generator.generate_turtle_svg(genetics)
            if svg_drawing:
                self.cache_svg(genetics, svg_drawing)
            
            # Generate and cache surface
            surface = surface_renderer.render_turtle_to_surface(genetics)
            if surface:
                self.cache_surface(genetics, 100, surface)
    
    def export_cache_stats(self) -> str:
        """
        Export cache statistics as formatted string
        """
        stats = self.get_cache_stats()
        
        stats_str = f"""
Turtle SVG Cache Statistics
==========================
Memory Usage: {stats['memory_usage_mb']:.2f} MB / {stats['memory_limit_mb']} MB ({stats['memory_usage_percentage']:.1f}%)
Total Entries: {stats['total_entries']} / {stats['max_entries']}
Hit Rate: {stats['hit_rate_percentage']:.1f}%

Cache Breakdown:
- SVG: {stats['svg_entries']} entries ({stats['svg_hit_rate']:.1f}% hit rate)
- Surface: {stats['surface_entries']} entries ({stats['surface_hit_rate']:.1f}% hit rate)
- Genetics: {stats['genetics_entries']} entries ({stats['genetics_hit_rate']:.1f}% hit rate)

Performance:
- Total Requests: {stats['total_requests']}
- Total Hits: {stats['total_hits']}
- Total Misses: {stats['total_misses']}
- Evictions: {stats['evictions']}
"""
        return stats_str.strip()


# Global cache instance
_cache_instance = None


def get_turtle_cache() -> TurtleSVGCache:
    """
    Get global turtle cache instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = TurtleSVGCache()
    return _cache_instance


# Utility functions
def cache_turtle_svg(genetics: Dict[str, Any], svg_drawing: object) -> str:
    """Cache turtle SVG using global cache"""
    cache = get_turtle_cache()
    return cache.cache_svg(genetics, svg_drawing)


def get_cached_turtle_svg(genetics: Dict[str, Any]) -> Optional[object]:
    """Get cached turtle SVG using global cache"""
    cache = get_turtle_cache()
    return cache.get_cached_svg(genetics)


def cache_turtle_surface(genetics: Dict[str, Any], size: int, surface: pygame.Surface) -> str:
    """Cache turtle surface using global cache"""
    cache = get_turtle_cache()
    return cache.cache_surface(genetics, size, surface)


def get_cached_turtle_surface(genetics: Dict[str, Any], size: int) -> Optional[pygame.Surface]:
    """Get cached turtle surface using global cache"""
    cache = get_turtle_cache()
    return cache.get_cached_surface(genetics, size)


def clear_turtle_cache(cache_type: str = "all") -> int:
    """Clear turtle cache using global cache"""
    cache = get_turtle_cache()
    return cache.clear_cache(cache_type)


def get_cache_statistics() -> Dict[str, Any]:
    """Get cache statistics using global cache"""
    cache = get_turtle_cache()
    return cache.get_cache_stats()
