"""
Comprehensive Turtle Render Engine
Centralized turtle rendering system for all UI components
"""

import pygame
from typing import Optional, Tuple, Dict, Any
from core.rendering.pygame_turtle_renderer import PygameTurtleRenderer

class TurtleRenderEngine:
    """Centralized turtle rendering system with caching and optimization"""
    
    def __init__(self):
        self.pygame_renderer = PygameTurtleRenderer()
        self._sprite_cache: Dict[str, pygame.Surface] = {}
        self._cache_hits = 0
        self._cache_misses = 0
        
    def render_turtle_sprite(self, 
                           screen: pygame.Surface,
                           turtle: Any,
                           position: Tuple[int, int],
                           size: Tuple[int, int] = (40, 30),
                           force_regenerate: bool = False) -> bool:
        """
        Render a turtle sprite at the specified position
        
        Args:
            screen: Target pygame surface
            turtle: Turtle object with required attributes
            position: (x, y) screen coordinates
            size: (width, height) of the sprite
            force_regenerate: Force regeneration of cached sprite
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate cache key based on turtle attributes
            cache_key = self._generate_cache_key(turtle, size)
            
            # Check cache first
            if not force_regenerate and cache_key in self._sprite_cache:
                sprite = self._sprite_cache[cache_key]
                self._cache_hits += 1
            else:
                # Generate new sprite
                sprite = self._generate_turtle_sprite(turtle, size)
                if sprite:
                    self._sprite_cache[cache_key] = sprite
                    self._cache_misses += 1
                else:
                    return False
            
            # Blit sprite to screen
            screen.blit(sprite, position)
            return True
            
        except Exception as e:
            print(f"[DEBUG] TurtleRenderEngine: Failed to render {getattr(turtle, 'name', 'Unknown')}: {e}")
            return False
    
    def _generate_cache_key(self, turtle: Any, size: Tuple[int, int]) -> str:
        """Generate unique cache key for turtle sprite"""
        try:
            # Include all visual attributes that affect rendering
            attrs = [
                getattr(turtle, 'name', 'Unknown'),
                getattr(turtle, 'color', (0, 0, 0)),
                getattr(turtle, 'age', 1),
                f"{size[0]}x{size[1]}"
            ]
            
            # Include stats if available (for visual variations)
            if hasattr(turtle, 'stats'):
                stats = turtle.stats
                attrs.extend([
                    f"speed_{stats.get('speed', 1)}",
                    f"energy_{stats.get('max_energy', 50)}"
                ])
            
            return "|".join(str(attr) for attr in attrs)
            
        except Exception:
            return f"fallback_{id(turtle)}_{size[0]}x{size[1]}"
    
    def _generate_turtle_sprite(self, turtle: Any, size: Tuple[int, int]) -> Optional[pygame.Surface]:
        """Generate turtle sprite using the pygame renderer"""
        try:
            # Use the existing pygame turtle renderer
            font = pygame.font.Font(None, 12)
            
            # The PygameTurtleRenderer.render_turtle() takes (turtle, size) parameters
            # size should be an integer (square dimensions)
            sprite_size = max(size)  # Use the larger dimension for square sprite
            sprite = self.pygame_renderer.render_turtle(turtle, sprite_size)
            
            if sprite:
                # Resize to the exact dimensions requested
                if sprite.get_size() != size:
                    sprite = pygame.transform.scale(sprite, size)
                print(f"[DEBUG] TurtleRenderEngine: Generated sprite for {getattr(turtle, 'name', 'Unknown')}")
                return sprite
            else:
                # Fallback to simple rectangle
                return self._generate_fallback_sprite(turtle, size)
                
        except Exception as e:
            print(f"[DEBUG] TurtleRenderEngine: Fallback rendering for {getattr(turtle, 'name', 'Unknown')}: {e}")
            return self._generate_fallback_sprite(turtle, size)
    
    def _generate_fallback_sprite(self, turtle: Any, size: Tuple[int, int]) -> pygame.Surface:
        """Generate simple fallback sprite when main renderer fails"""
        width, height = size
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Get turtle color or use default
        color = getattr(turtle, 'color', (100, 150, 100))
        if isinstance(color, str):
            # Convert color name to RGB
            color_map = {
                'green': (50, 200, 50),
                'blue': (50, 50, 200),
                'red': (200, 50, 50),
                'yellow': (200, 200, 50),
                'purple': (150, 50, 200)
            }
            color = color_map.get(color.lower(), (100, 150, 100))
        
        # Draw simple turtle shape
        pygame.draw.ellipse(surface, color, (0, 0, width, height))
        pygame.draw.ellipse(surface, (0, 0, 0), (0, 0, width, height), 1)
        
        # Add turtle name
        font = pygame.font.Font(None, 10)
        name = getattr(turtle, 'name', '?')[:3]  # First 3 characters
        text = font.render(name, True, (255, 255, 255))
        text_rect = text.get_rect(center=(width//2, height//2))
        surface.blit(text, text_rect)
        
        return surface
    
    def render_turtle_card(self,
                          screen: pygame.Surface,
                          turtle: Any,
                          rect: pygame.Rect,
                          show_stats: bool = True,
                          selected: bool = False) -> bool:
        """
        Render a turtle card (for roster, shop, etc.)
        
        Args:
            screen: Target pygame surface
            turtle: Turtle object
            rect: Rectangle area for the card
            show_stats: Whether to show turtle stats
            selected: Whether this turtle is selected
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Card background
            bg_color = (80, 80, 100) if selected else (60, 60, 80)
            pygame.draw.rect(screen, bg_color, rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 2)
            
            # Turtle sprite
            sprite_size = (60, 45)
            sprite_pos = (rect.x + 10, rect.y + 10)
            self.render_turtle_sprite(screen, turtle, sprite_pos, sprite_size)
            
            # Turtle info
            font = pygame.font.Font(None, 20)
            name_text = font.render(getattr(turtle, 'name', 'Unknown'), True, (255, 255, 255))
            screen.blit(name_text, (rect.x + 80, rect.y + 10))
            
            if show_stats and hasattr(turtle, 'stats'):
                stats_font = pygame.font.Font(None, 16)
                stats = turtle.stats
                
                # Display key stats
                stat_lines = [
                    f"Speed: {stats.get('speed', 1)}",
                    f"Energy: {stats.get('max_energy', 50)}",
                    f"Age: {getattr(turtle, 'age', 1)}"
                ]
                
                y_offset = rect.y + 35
                for line in stat_lines:
                    stat_text = stats_font.render(line, True, (200, 200, 200))
                    screen.blit(stat_text, (rect.x + 80, y_offset))
                    y_offset += 18
            
            return True
            
        except Exception as e:
            print(f"[DEBUG] TurtleRenderEngine: Failed to render card for {getattr(turtle, 'name', 'Unknown')}: {e}")
            return False
    
    def clear_cache(self):
        """Clear the sprite cache"""
        self._sprite_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        print("[DEBUG] TurtleRenderEngine: Cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache performance statistics"""
        return {
            'cache_size': len(self._sprite_cache),
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses
        }
    
    def preload_common_sprites(self, turtles: list):
        """Preload sprites for common turtles to improve performance"""
        print(f"[DEBUG] TurtleRenderEngine: Preloading sprites for {len(turtles)} turtles")
        
        for turtle in turtles:
            # Preload common sizes
            for size in [(40, 30), (60, 45), (80, 60)]:
                try:
                    self.render_turtle_sprite(pygame.Surface((1, 1)), turtle, (0, 0), size)
                except:
                    pass  # Ignore errors during preload
        
        print(f"[DEBUG] TurtleRenderEngine: Preloading complete. Cache size: {len(self._sprite_cache)}")


# Global instance for shared use
turtle_render_engine = TurtleRenderEngine()
