"""ImGui Context Management for TurboShells

Handles ImGui initialization, OpenGL context, and PyGame integration.
Follows Single Responsibility Principle by managing only ImGui lifecycle.
"""

import pygame
import imgui_bundle as imgui
import imgui_bundle.imgui as imgui_core
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
        self.impl: Optional['CustomPygameRenderer'] = None
        self._initialized = False
        
    def initialize(self) -> bool:
        """Initialize ImGui context and PyGame integration.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Create ImGui context
            self.context = imgui.imgui.create_context()
            
            # Initialize PyGame renderer
            self.impl = CustomPygameRenderer(self.screen)
            
            # Set up initial ImGui style for game UI
            self._setup_game_style()
            
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"Failed to initialize ImGui context: {e}")
            return False
    
    def _setup_game_style(self) -> None:
        """Configure ImGui style for game aesthetic."""
        style = imgui.imgui.get_style()
        
        # Dark theme suitable for games
        style.colors[imgui.imgui.COLOR_WINDOW_BACKGROUND] = (0.1, 0.1, 0.15, 0.9)
        style.colors[imgui.imgui.COLOR_TITLE_BACKGROUND] = (0.2, 0.2, 0.3, 1.0)
        style.colors[imgui.imgui.COLOR_TITLE_BACKGROUND_ACTIVE] = (0.3, 0.3, 0.4, 1.0)
        style.colors[imgui.imgui.COLOR_BUTTON] = (0.2, 0.3, 0.4, 1.0)
        style.colors[imgui.imgui.COLOR_BUTTON_HOVERED] = (0.3, 0.4, 0.5, 1.0)
        style.colors[imgui.imgui.COLOR_BUTTON_ACTIVE] = (0.4, 0.5, 0.6, 1.0)
        
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
        imgui.imgui.new_frame()
    
    def end_frame(self) -> None:
        """End ImGui frame and render to screen.
        
        Must be called after all ImGui UI code.
        """
        if not self._initialized or not self.impl:
            return
            
        # Render ImGui draw data
        imgui.imgui.render()
        self.impl.render(imgui.imgui.get_draw_data())
    
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
            imgui.imgui.destroy_context(self.context)
            self.context = None
            
        self._initialized = False
    
    def get_screen_size(self) -> tuple[int, int]:
        """Get current screen size from PyGame surface."""
        return self.screen.get_size()
    
    def set_display_size(self, width: int, height: int) -> None:
        """Update ImGui display size for window resizing."""
        if self._initialized:
            imgui.imgui.get_io().display_size = (width, height)


class CustomPygameRenderer:
    """Custom PyGame renderer for imgui-bundle."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.io = imgui.imgui.get_io()
        self.io.display_size = screen.get_size()
        self.io.display_fb_scale = (1, 1)
        
    def process_event(self, event: pygame.event.Event) -> bool:
        """Process PyGame event for ImGui."""
        if event.type == pygame.MOUSEMOTION:
            self.io.mouse_pos = event.pos
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.io.mouse_down[0] = True
            elif event.button == 2:
                self.io.mouse_down[1] = True
            elif event.button == 3:
                self.io.mouse_down[2] = True
            return False
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.io.mouse_down[0] = False
            elif event.button == 2:
                self.io.mouse_down[1] = False
            elif event.button == 3:
                self.io.mouse_down[2] = False
            return False
        elif event.type == pygame.MOUSEWHEEL:
            self.io.mouse_wheel = event.y
            return False
        elif event.type == pygame.KEYDOWN:
            key = event.key
            if key < 512:
                self.io.keys_down[key] = True
            if key == pygame.K_BACKSPACE:
                self.io.add_input_character(chr(8))
            elif key == pygame.K_RETURN:
                self.io.add_input_character(chr(13))
            elif key == pygame.K_TAB:
                self.io.add_input_character(chr(9))
            return False
        elif event.type == pygame.KEYUP:
            key = event.key
            if key < 512:
                self.io.keys_down[key] = False
            return False
        elif event.type == pygame.TEXTINPUT:
            for char in event.text:
                self.io.add_input_character(char)
            return False
        return False
    
    def render(self, draw_data) -> None:
        """Render ImGui draw data to PyGame surface."""
        # This is a minimal implementation - full rendering would require
        # OpenGL integration which is complex. For now, this provides
        # the basic structure for event handling.
        pass
    
    def shutdown(self) -> None:
        """Clean up renderer resources."""
        pass
