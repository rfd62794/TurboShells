"""ImGui Context Management for TurboShells

Handles ImGui initialization, OpenGL context, and PyGame integration.
Follows Single Responsibility Principle by managing only ImGui lifecycle.
"""

import pygame
import imgui
from imgui.integrations.pygame import PygameRenderer
from typing import Optional


class ImGuiContext:
    """Manages ImGui context, initialization, and rendering pipeline.
    
    Responsibilities:
    - Initialize ImGui context and OpenGL integration
    - Manage frame lifecycle (begin/end)
    - Handle PyGame event processing
    - Clean up resources on shutdown
    
    This class isolates all ImGui-specific concerns from the rest of the application.
    """
    
    def __init__(self, pygame_surface: pygame.Surface):
        """Initialize ImGui context manager.
        
        Args:
            pygame_surface: The PyGame surface for rendering
        """
        self.screen = pygame_surface
        self._initialized = False
        self.impl: Optional[PygameRenderer] = None
        
    def initialize(self) -> bool:
        """Initialize ImGui context and PyGame integration.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Create ImGui context manually
            imgui.create_context()
            
            # Initialize PyGame Renderer
            self.impl = PygameRenderer()
            
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"Failed to initialize ImGui context: {e}")
            return False
    
    def begin_frame(self) -> None:
        """Start new ImGui frame.
        
        Must be called before any ImGui UI code.
        """
        if not self._initialized or not self.impl:
            return
            
        imgui.new_frame()
    
    def end_frame(self) -> None:
        """End ImGui frame and render to screen.
        
        Must be called after all ImGui UI code.
        """
        if not self._initialized or not self.impl:
            return
            
        imgui.render()
        self.impl.render(imgui.get_draw_data())
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Process PyGame event through ImGui.
        
        Args:
            event: PyGame event to process
            
        Returns:
            True if event was consumed by ImGui, False otherwise
        """
        if not self._initialized or not self.impl:
            return False
            
        return self.impl.process_event(event)
    
    def is_initialized(self) -> bool:
        """Check if ImGui context is properly initialized."""
        return self._initialized
    
    def shutdown(self) -> None:
        """Clean up ImGui resources."""
        if self.impl:
            self.impl.shutdown()
            self.impl = None
        self._initialized = False
    
    def get_screen_size(self) -> tuple[int, int]:
        """Get current screen size from PyGame surface."""
        return self.screen.get_size()
    
    def set_display_size(self, width: int, height: int) -> None:
        """Update ImGui display size for window resizing."""
        # PygameRenderer handles this automatically via io.display_size in process_event or new_frame
        # But we can explicitly set it if needed, though usually not required with the standard integration
        io = imgui.get_io()
        io.display_size = (width, height)


