"""Roster view toggle component for switching between Active and Retired turtles."""

import pygame
from pygame_gui import UIManager
from typing import Optional, Callable
from .base_component import BaseComponent


class RosterViewToggle(BaseComponent):
    """Component for toggling between Active and Retired roster views.
    
    Single Responsibility: Handle view switching UI and state management.
    """
    
    def __init__(self, rect: pygame.Rect, manager: Optional[UIManager] = None, 
                 game_state=None, container=None):
        """Initialize roster view toggle.
        
        Args:
            rect: Component position and size
            manager: pygame_gui UIManager instance
            game_state: Game state interface for view state
            container: pygame_gui container for buttons
        """
        super().__init__(rect, manager)
        self.game_state = game_state
        self.container = container
        self.on_view_changed: Optional[Callable[[bool], None]] = None
        
        # UI elements
        self.btn_active = None
        self.btn_retired = None
        self._current_view = "active"  # "active" or "retired"
        
        self._create_ui_elements()
        
    def _create_ui_elements(self) -> None:
        """Create the Active and Retired toggle buttons."""
        if not self.manager or not self.container:
            return
            
        # Active Button
        self.btn_active = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.rect.x, self.rect.y), (100, 30)),
            text="Active",
            manager=self.manager,
            container=self.container
        )
        
        # Retired Button  
        self.btn_retired = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.rect.x + 110, self.rect.y), (100, 30)),
            text="Retired",
            manager=self.manager,
            container=self.container
        )
        
        # Set initial state
        self._update_button_states()
        
    def _update_button_states(self) -> None:
        """Update button visual states based on current view."""
        if not self.btn_active or not self.btn_retired:
            return
            
        # Update visual states (could be enhanced with different styling)
        if self._current_view == "active":
            self.btn_active.set_text("[Active]")
            self.btn_retired.set_text("Retired")
        else:
            self.btn_active.set_text("Active")
            self.btn_retired.set_text("[Retired]")
            
    def _handle_component_event(self, event: pygame.event.Event) -> bool:
        """Handle button click events."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_active:
                self.set_active_view(False)  # Show active
                return True
            elif event.ui_element == self.btn_retired:
                self.set_active_view(True)   # Show retired
                return True
        return False
        
    def set_active_view(self, show_retired: bool) -> None:
        """Set the current view.
        
        Args:
            show_retired: True to show retired roster, False for active
        """
        self._current_view = "retired" if show_retired else "active"
        self._update_button_states()
        
        # Update game state
        if self.game_state:
            self.game_state.set('toggle_view', show_retired)
            
        # Notify listeners
        if self.on_view_changed:
            self.on_view_changed(show_retired)
            
        self._emit_event("view_changed", show_retired)
        
    def get_current_view(self) -> str:
        """Get current view mode."""
        return self._current_view
        
    def is_showing_retired(self) -> bool:
        """Check if currently showing retired roster."""
        return self._current_view == "retired"
        
    def render(self, surface: pygame.Surface) -> None:
        """Render the component. pygame_gui handles rendering."""
        pass
        
    def destroy(self) -> None:
        """Clean up UI elements."""
        if self.btn_active:
            self.btn_active.kill()
        if self.btn_retired:
            self.btn_retired.kill()
        super().destroy()
