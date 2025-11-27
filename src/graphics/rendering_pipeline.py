"""Rendering Pipeline for TurboShells Hybrid Architecture

Manages layered rendering: Game World (PyGame) → ImGui Overlay.
Implements proper separation between game rendering and UI rendering.
"""

import pygame
from typing import Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass


class RenderLayer(Enum):
    """Rendering layers in the pipeline."""
    BACKGROUND = 1
    GAME_WORLD = 2
    GAME_UI = 3
    IMGUI_OVERLAY = 4
    DEBUG_OVERLAY = 5
    FOREGROUND = 6


@dataclass
class RenderPass:
    """Represents a single rendering pass."""
    layer: RenderLayer
    render_func: Callable
    enabled: bool = True
    priority: int = 0


class RenderingPipeline:
    """Manages layered rendering: Game World → ImGui Overlay.
    
    Responsibilities:
    - Coordinate rendering layers in proper order
    - Manage PyGame and ImGui rendering contexts
    - Handle screen resizing and display updates
    - Provide performance monitoring for rendering
    
    This class implements the Pipeline pattern to ensure proper layering
    of game world rendering and UI overlay rendering.
    """
    
    def __init__(self, screen: pygame.Surface):
        """Initialize the rendering pipeline.
        
        Args:
            screen: PyGame surface for rendering
        """
        self.screen = screen
        self.game_renderer: Optional[Any] = None
        self.ui_manager: Optional[Any] = None
        self.render_passes: List[RenderPass] = []
        self.background_color = (0, 0, 0)  # Black
        self._fps_counter = 0
        self._frame_times = []
        self._max_frame_samples = 60
        
        # Initialize default render passes
        self._setup_default_passes()
    
    def _setup_default_passes(self) -> None:
        """Set up default rendering passes."""
        # Background pass
        self.add_render_pass(RenderLayer.BACKGROUND, self._render_background)
        
        # Game world pass (sprites, entities, track)
        self.add_render_pass(RenderLayer.GAME_WORLD, self._render_game_world)
        
        # Legacy game UI pass (for gradual migration)
        self.add_render_pass(RenderLayer.GAME_UI, self._render_game_ui)
        
        # ImGui overlay pass
        self.add_render_pass(RenderLayer.IMGUI_OVERLAY, self._render_imgui_overlay)
        
        # Debug overlay pass
        self.add_render_pass(RenderLayer.DEBUG_OVERLAY, self._render_debug_overlay)
    
    def set_game_renderer(self, renderer: Any) -> None:
        """Set the game renderer.
        
        Args:
            renderer: Game renderer instance
        """
        self.game_renderer = renderer
    
    def set_ui_manager(self, ui_manager: Any) -> None:
        """Set the UI manager.
        
        Args:
            ui_manager: UI manager instance
        """
        self.ui_manager = ui_manager
    
    def add_render_pass(self, layer: RenderLayer, render_func: Callable, 
                       priority: int = 0, enabled: bool = True) -> None:
        """Add a rendering pass to the pipeline.
        
        Args:
            layer: Rendering layer
            render_func: Function to call for this pass
            priority: Priority within the layer (higher = later)
            enabled: Whether this pass is enabled
        """
        render_pass = RenderPass(
            layer=layer,
            render_func=render_func,
            enabled=enabled,
            priority=priority
        )
        
        self.render_passes.append(render_pass)
        
        # Sort passes by layer order, then by priority
        self.render_passes.sort(key=lambda p: (p.layer.value, p.priority))
    
    def remove_render_pass(self, layer: RenderLayer, render_func: Callable) -> bool:
        """Remove a rendering pass from the pipeline.
        
        Args:
            layer: Layer to remove from
            render_func: Function to remove
            
        Returns:
            True if pass was found and removed, False otherwise
        """
        for i, pass_obj in enumerate(self.render_passes):
            if pass_obj.layer == layer and pass_obj.render_func == render_func:
                self.render_passes.pop(i)
                return True
        return False
    
    def enable_render_pass(self, layer: RenderLayer, enabled: bool = True) -> None:
        """Enable or disable all passes in a layer.
        
        Args:
            layer: Layer to modify
            enabled: Whether to enable the layer
        """
        for pass_obj in self.render_passes:
            if pass_obj.layer == layer:
                pass_obj.enabled = enabled
    
    def render_frame(self, game_state: Any) -> None:
        """Render complete frame with proper layering.
        
        Args:
            game_state: Current game state object
        """
        frame_start = pygame.time.get_ticks()
        
        # Execute all enabled render passes in order
        for render_pass in self.render_passes:
            if render_pass.enabled:
                try:
                    render_pass.render_func(game_state)
                except Exception as e:
                    print(f"Error in render pass {render_pass.layer.name}: {e}")
        
        # Final display flip
        pygame.display.flip()
        
        # Track performance
        frame_time = pygame.time.get_ticks() - frame_start
        self._track_frame_performance(frame_time)
    
    def _render_background(self, game_state: Any) -> None:
        """Render background layer."""
        self.screen.fill(self.background_color)
    
    def _render_game_world(self, game_state: Any) -> None:
        """Render game world layer (sprites, entities, track)."""
        if not self.game_renderer:
            return
            
        # Render based on current game state
        state = getattr(game_state, 'state', 'MENU')
        
        if state == 'MENU':
            self.game_renderer.draw_main_menu(game_state)
        elif state == 'ROSTER':
            self.game_renderer.draw_menu(game_state)
        elif state == 'RACE':
            self.game_renderer.draw_race(game_state)
        elif state == 'RACE_RESULT':
            self.game_renderer.draw_race_result(game_state)
        elif state == 'SHOP':
            self.game_renderer.draw_shop(game_state)
        elif state == 'BREEDING':
            self.game_renderer.draw_breeding(game_state)
        elif state == 'PROFILE':
            self.game_renderer.draw_profile(game_state)
        elif state == 'VOTING':
            self.game_renderer.draw_voting(game_state)
    
    def _render_game_ui(self, game_state: Any) -> None:
        """Render legacy game UI layer (for gradual migration)."""
        # This layer can be used for legacy UI during migration
        # Eventually will be phased out in favor of ImGui
        pass
    
    def _render_imgui_overlay(self, game_state: Any) -> None:
        """Render ImGui overlay layer."""
        if not self.ui_manager or not self.ui_manager.visible():
            return
            
        # Render all ImGui panels
        self.ui_manager.render_ui_panels(game_state)
    
    def _render_debug_overlay(self, game_state: Any) -> None:
        """Render debug overlay layer."""
        # This could show FPS, rendering stats, etc.
        # For now, we'll skip this to keep it simple
        pass
    
    def _track_frame_performance(self, frame_time: int) -> None:
        """Track frame rendering performance.
        
        Args:
            frame_time: Time taken to render frame in milliseconds
        """
        self._frame_times.append(frame_time)
        
        # Maintain rolling average
        if len(self._frame_times) > self._max_frame_samples:
            self._frame_times.pop(0)
        
        self._fps_counter += 1
    
    def get_performance_stats(self) -> dict:
        """Get rendering performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        if not self._frame_times:
            return {
                'avg_frame_time': 0,
                'min_frame_time': 0,
                'max_frame_time': 0,
                'estimated_fps': 0,
                'frames_rendered': 0
            }
        
        avg_time = sum(self._frame_times) / len(self._frame_times)
        min_time = min(self._frame_times)
        max_time = max(self._frame_times)
        estimated_fps = 1000 / avg_time if avg_time > 0 else 0
        
        return {
            'avg_frame_time': avg_time,
            'min_frame_time': min_time,
            'max_frame_time': max_time,
            'estimated_fps': estimated_fps,
            'frames_rendered': self._fps_counter,
            'render_passes': len([p for p in self.render_passes if p.enabled])
        }
    
    def set_background_color(self, color: tuple[int, int, int]) -> None:
        """Set the background color.
        
        Args:
            color: RGB color tuple
        """
        self.background_color = color
    
    def handle_screen_resize(self, new_rect: pygame.Rect) -> None:
        """Handle screen resize events.
        
        Args:
            new_rect: New screen rectangle
        """
        # Update screen reference if needed
        # This would be called when the window is resized
        pass
    
    def reset_performance_stats(self) -> None:
        """Reset performance statistics."""
        self._frame_times.clear()
        self._fps_counter = 0
    
    def get_render_pass_info(self) -> list:
        """Get information about current render passes.
        
        Returns:
            List of render pass information
        """
        return [
            {
                'layer': pass_obj.layer.name,
                'enabled': pass_obj.enabled,
                'priority': pass_obj.priority
            }
            for pass_obj in self.render_passes
        ]
    
    def print_render_info(self) -> None:
        """Print debugging information about rendering pipeline."""
        print("=== Rendering Pipeline Info ===")
        print(f"Screen size: {self.screen.get_size()}")
        print(f"Background color: {self.background_color}")
        print(f"Render passes: {len(self.render_passes)}")
        
        for pass_info in self.get_render_pass_info():
            status = "ENABLED" if pass_info['enabled'] else "DISABLED"
            print(f"  - {pass_info['layer']}: {status} (Priority: {pass_info['priority']})")
        
        stats = self.get_performance_stats()
        print(f"Performance: {stats['estimated_fps']:.1f} FPS (Avg: {stats['avg_frame_time']:.1f}ms)")
        print("=" * 35)
