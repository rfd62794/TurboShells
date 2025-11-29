"""Turtle action buttons component for individual turtle actions."""

import pygame
import pygame_gui
from pygame_gui import UIManager
from typing import Optional, Dict, Any
from ..base_component import BaseComponent


class TurtleActionButtons(BaseComponent):
    """Component for turtle action buttons (Train, View, Retire, Select).
    
    Single Responsibility: Handle individual turtle action buttons and their visibility.
    """
    
    def __init__(self, rect: pygame.Rect, turtle_index: int, manager: Optional[UIManager] = None,
                 game_state=None, container=None, event_bus=None):
        """Initialize turtle action buttons.
        
        Args:
            rect: Component position and size
            turtle_index: Index of this turtle in the roster
            manager: pygame_gui UIManager instance
            game_state: Game state interface for actions
            container: pygame_gui container for buttons
            event_bus: Event bus for publishing events
        """
        super().__init__(rect, manager, container)
        self.turtle_index = turtle_index
        self.game_state = game_state
        self.event_bus = event_bus  # Store event bus reference
        self.container = container
        
        # UI elements
        self.btn_train = None
        self.btn_view = None
        self.btn_retire = None
        self.btn_select = None
        
        # Current mode state
        self._is_retired_turtle = False
        self._is_select_mode = False
        self._is_active_racer = False
        
        self._create_ui_elements()
        
    def _create_ui_elements(self) -> None:
        """Create the action buttons."""
        if not self.manager or not self.container:
            return
            
        # Train Button (middle)
        self.btn_train = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.rect.x + 60, self.rect.y + 270), (100, 30)),
            text="Train",
            manager=self.manager,
            container=self.container
        )
        
        # View Button (bottom left)
        self.btn_view = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.rect.x, self.rect.y + 310), (50, 30)),
            text="View",
            manager=self.manager,
            container=self.container
        )
        
        # Retire Button (bottom right)
        self.btn_retire = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.rect.x + 180, self.rect.y + 310), (50, 30)),
            text="Retire",
            manager=self.manager,
            container=self.container
        )
        
        # Select Button (bottom center)
        self.btn_select = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.rect.x + 60, self.rect.y + 310), (100, 30)),
            text="Select",
            manager=self.manager,
            container=self.container
        )
        
        # Set initial visibility
        self._update_visibility()
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for this component."""
        return self._handle_component_event(event)
        
    def _handle_component_event(self, event: pygame.event.Event) -> bool:
        """Handle button click events."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_train:
                self._handle_train()
                return True
            elif event.ui_element == self.btn_view:
                self._handle_view()
                return True
            elif event.ui_element == self.btn_retire:
                self._handle_retire()
                return True
            elif event.ui_element == self.btn_select:
                self._handle_select()
                return True
        return False
        
    def _handle_train(self) -> None:
        """Handle train button click."""
        if self.game_state:
            self.game_state.set('train_turtle', self.turtle_index)
        self._emit_event("train_clicked", self.turtle_index)
        
    def _handle_view(self) -> None:
        """Handle view button click."""
        if self.game_state:
            self.game_state.set('view_profile', self.turtle_index)
        self._emit_event("view_clicked", self.turtle_index)
        
    def _handle_retire(self) -> None:
        """Handle retire button click."""
        if self.game_state:
            self.game_state.set('retire_turtle', self.turtle_index)
        self._emit_event("retire_clicked", self.turtle_index)
        
    def _handle_select(self) -> None:
        """Handle select button click."""
        if self.game_state:
            # Follow original pattern exactly
            self.game_state.set('set_active_racer', self.turtle_index)
            # Emit to global event bus if available
            if hasattr(self, 'event_bus') and self.event_bus:
                self.event_bus.emit('update_ui', None)
            else:
                # Fallback to local emission
                self._emit_event("update_ui", None)
        
    def update_mode(self, is_retired_turtle: bool, is_select_mode: bool, 
                   is_active_racer: bool = False) -> None:
        """Update button visibility based on mode.
        
        Args:
            is_retired_turtle: True if this turtle is retired
            is_select_mode: True if in racer selection mode
            is_active_racer: True if this turtle is the currently selected racer
        """
        self._is_retired_turtle = is_retired_turtle
        self._is_select_mode = is_select_mode
        self._is_active_racer = is_active_racer
        self._update_visibility()
        
    def _update_visibility(self) -> None:
        """Update button visibility based on current mode."""
        if not all([self.btn_train, self.btn_view, self.btn_retire, self.btn_select]):
            return
            
        if self._is_retired_turtle:
            # Retired turtles: no action buttons
            self.btn_train.hide()
            self.btn_view.hide()
            self.btn_retire.hide()
            self.btn_select.hide()
        else:
            # Active turtles
            if self._is_select_mode:
                self.btn_train.hide()
                self.btn_view.hide()
                # Keep retire button visible even in select mode
                self.btn_retire.show()
                self.btn_select.show()
                
                # Update select button text
                if self._is_active_racer:
                    self.btn_select.set_text("[Selected]")
                else:
                    self.btn_select.set_text("Select")
            else:
                self.btn_train.show()
                self.btn_view.show()
                self.btn_retire.show()
                self.btn_select.hide()
                
    def update_select_button_text(self, text: str) -> None:
        """Update only the select button text."""
        if self.btn_select:
            self.btn_select.set_text(text)
                
    def get_buttons(self) -> Dict[str, Any]:
        """Get button references for external access."""
        return {
            'train': self.btn_train,
            'view': self.btn_view,
            'retire': self.btn_retire,
            'select': self.btn_select
        }
        
    def render(self, surface: pygame.Surface) -> None:
        """Render the component. pygame_gui handles rendering."""
        pass
        
    def destroy(self) -> None:
        """Clean up UI elements."""
        for button in [self.btn_train, self.btn_view, self.btn_retire, self.btn_select]:
            if button:
                button.kill()
        super().destroy()
