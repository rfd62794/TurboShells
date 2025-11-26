"""ImGui Context Management for TurboShells

Handles ImGui initialization, OpenGL context, and PyGame integration.
Follows Single Responsibility Principle by managing only ImGui lifecycle.
"""

import pygame
import imgui_bundle as imgui
import imgui_bundle.integrations.pygame as pygame_integration
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
        self.context: Optional[imgui.Context] = None
        self.impl: Optional[pygame_integration.PygameRenderer] = None
        self._initialized = False
        
    def initialize(self) -> bool:
        """Initialize ImGui context and PyGame integration.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Create ImGui context
            self.context = imgui.create_context()
            
            # Initialize PyGame renderer
            self.impl = pygame_integration.PygameRenderer()
            
            # Set up initial ImGui style for game UI
            self._setup_game_style()
            
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"Failed to initialize ImGui context: {e}")
            return False
    
    def _setup_game_style(self) -> None:
        """Configure ImGui style for game aesthetic."""
        style = imgui.get_style()
        
        # Dark theme suitable for games
        style.colors[imgui.COLOR_WINDOW_BACKGROUND] = (0.1, 0.1, 0.15, 0.9)
        style.colors[imgui.COLOR_TITLE_BACKGROUND] = (0.2, 0.2, 0.3, 1.0)
        style.colors[imgui.COLOR_TITLE_BACKGROUND_ACTIVE] = (0.3, 0.3, 0.4, 1.0)
        style.colors[imgui.COLOR_BUTTON] = (0.2, 0.3, 0.4, 1.0)
        style.colors[imgui.COLOR_BUTTON_HOVERED] = (0.3, 0.4, 0.5, 1.0)
        style.colors[imgui.COLOR_BUTTON_ACTIVE] = (0.4, 0.5, 0.6, 1.0)
        
        # Rounded corners for modern look
        style.window_rounding = 5.0
        style.frame_rounding = 3.0
        style.popup_rounding = 3.0
        
        # Padding for better spacing
        style.window_padding = (10, 10)
        style.frame_padding = (8, 4)
        style.item_spacing = (8, 4)
    
    def begin_frame(self) -> None:
        """Start new ImGui frame.
        
        Must be called before any ImGui UI code.
        """
        if not self._initialized or not self.impl:
            return
            
        # Process PyGame events for ImGui
        self.impl.process_event(pygame.event.Event(pygame.USEREVENT, {}))
        
        # Start new ImGui frame
        imgui.new_frame()
    
    def end_frame(self) -> None:
        """End ImGui frame and render to screen.
        
        Must be called after all ImGui UI code.
        """
        if not self._initialized or not self.impl:
            return
            
        # Render ImGui draw data
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
        return self._initialized and self.context is not None and self.impl is not None
    
    def shutdown(self) -> None:
        """Clean up ImGui resources."""
        if self.impl:
            self.impl.shutdown()
            self.impl = None
            
        if self.context:
            imgui.destroy_context(self.context)
            self.context = None
            
        self._initialized = False
    
    def get_screen_size(self) -> tuple[int, int]:
        """Get current screen size from PyGame surface."""
        return self.screen.get_size()
    
    def set_display_size(self, width: int, height: int) -> None:
        """Update ImGui display size for window resizing."""
        if self._initialized:
            imgui.get_io().display_size = (width, height)
