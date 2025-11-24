"""
Event handling component for settings interface.

Handles all user input events following SRP principles.
"""

from typing import Dict, List, Tuple, Optional, Callable, Any
import pygame

from core.logging_config import get_logger
from ui.components.tab_manager import TabManager, SettingsTab
from ui.components.ui_renderer import UIElement


class EventHandler:
    """
    Handles all user input events for the settings interface.
    
    Single responsibility: Process user interactions only.
    """
    
    def __init__(self, tab_manager: TabManager):
        """
        Initialize event handler.
        
        Args:
            tab_manager: Tab manager for tab navigation
        """
        self.tab_manager = tab_manager
        self.logger = get_logger(__name__)
        
        # Event state
        self.mouse_pos = (0, 0)
        self.mouse_pressed = False
        self.hovered_element = None
        self.tooltip_text = ""
        self.tooltip_position = (0, 0)
        
        # UI elements to handle
        self.ui_elements: Dict[SettingsTab, List[UIElement]] = {}
        self.action_buttons: List[UIElement] = []
        
        # Event callbacks
        self.tab_change_callbacks: List[Callable[[SettingsTab], None]] = []
        self.element_callbacks: Dict[str, Callable] = {}
        
        self.logger.debug("EventHandler initialized")
    
    def set_ui_elements(self, tab_id: SettingsTab, elements: List[UIElement]) -> None:
        """
        Set UI elements for a specific tab.
        
        Args:
            tab_id: Tab identifier
            elements: List of UI elements for the tab
        """
        self.ui_elements[tab_id] = elements
        self.logger.debug(f"Set {len(elements)} UI elements for tab {tab_id.value}")
    
    def set_action_buttons(self, buttons: List[UIElement]) -> None:
        """
        Set action buttons.
        
        Args:
            buttons: List of action button elements
        """
        self.action_buttons = buttons
        self.logger.debug(f"Set {len(buttons)} action buttons")
    
    def add_tab_change_callback(self, callback: Callable[[SettingsTab], None]) -> None:
        """
        Add callback for tab changes.
        
        Args:
            callback: Function to call when tab changes
        """
        self.tab_change_callbacks.append(callback)
    
    def add_element_callback(self, element_id: str, callback: Callable) -> None:
        """
        Add callback for specific UI element.
        
        Args:
            element_id: Unique element identifier
            callback: Function to call when element is activated
        """
        self.element_callbacks[element_id] = callback
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle a pygame event.
        
        Args:
            event: Pygame event to handle
            
        Returns:
            True if event was handled, False otherwise
        """
        if event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event)
            return True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return self._handle_mouse_button_down(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            return self._handle_mouse_button_up(event)
        elif event.type == pygame.KEYDOWN:
            return self._handle_key_down(event)
        elif event.type == pygame.KEYUP:
            return self._handle_key_up(event)
        
        return False
    
    def _handle_mouse_motion(self, event: pygame.event.Event) -> bool:
        """Handle mouse motion events."""
        self.mouse_pos = event.pos
        self._update_hover_state()
        self._update_tooltip()
        return True
    
    def _handle_mouse_button_down(self, event: pygame.event.Event) -> bool:
        """Handle mouse button down events."""
        if event.button != 1:  # Only handle left click
            return False
        
        self.mouse_pressed = True
        
        # Check tab clicks
        clicked_tab = self.tab_manager.handle_click(self.mouse_pos)
        if clicked_tab:
            if self.tab_manager.switch_to_tab(clicked_tab):
                self._notify_tab_change(clicked_tab)
            return True
        
        # Check action button clicks
        for button in self.action_buttons:
            if button.rect.collidepoint(self.mouse_pos):
                self._activate_element(button)
                return True
        
        # Check content element clicks
        current_tab = self.tab_manager.get_active_tab()
        content_elements = self.ui_elements.get(current_tab, [])
        
        for element in content_elements:
            if element.rect.collidepoint(self.mouse_pos) and element.enabled:
                self._activate_element(element)
                return True
        
        return False
    
    def _handle_mouse_button_up(self, event: pygame.event.Event) -> bool:
        """Handle mouse button up events."""
        if event.button != 1:  # Only handle left click
            return False
        
        self.mouse_pressed = False
        return True
    
    def _handle_key_down(self, event: pygame.event.Event) -> bool:
        """Handle key down events."""
        # Handle tab navigation with arrow keys
        if event.key == pygame.K_LEFT:
            self._navigate_to_previous_tab()
            return True
        elif event.key == pygame.K_RIGHT:
            self._navigate_to_next_tab()
            return True
        elif event.key == pygame.K_TAB:
            if event.mod & pygame.KMOD_SHIFT:
                self._navigate_to_previous_tab()
            else:
                self._navigate_to_next_tab()
            return True
        elif event.key == pygame.K_ESCAPE:
            # Handle escape key (close settings)
            self._activate_escape()
            return True
        
        return False
    
    def _handle_key_up(self, event: pygame.event.Event) -> bool:
        """Handle key up events."""
        return False
    
    def _update_hover_state(self) -> None:
        """Update hover state for UI elements."""
        self.hovered_element = None
        
        # Check action buttons
        for button in self.action_buttons:
            if button.rect.collidepoint(self.mouse_pos):
                self.hovered_element = button
                return
        
        # Check content elements
        current_tab = self.tab_manager.get_active_tab()
        content_elements = self.ui_elements.get(current_tab, [])
        
        for element in content_elements:
            if element.rect.collidepoint(self.mouse_pos):
                self.hovered_element = element
                return
    
    def _update_tooltip(self) -> None:
        """Update tooltip text and position."""
        self.tooltip_text = ""
        self.tooltip_position = self.mouse_pos
        
        # Check tab tooltips
        tab_at_pos = self.tab_manager.get_tab_at_position(self.mouse_pos)
        if tab_at_pos:
            tab_element = self.tab_manager.get_tab_element(tab_at_pos)
            if tab_element and tab_element.config.tooltip:
                self.tooltip_text = tab_element.config.tooltip
            return
        
        # Check element tooltips
        if self.hovered_element and self.hovered_element.tooltip:
            self.tooltip_text = self.hovered_element.tooltip
            return
    
    def _activate_element(self, element: UIElement) -> None:
        """
        Activate a UI element (click, select, etc.).
        
        Args:
            element: Element to activate
        """
        # Call element-specific callback if available
        element_id = f"{element.element_type}_{element.label}"
        if element_id in self.element_callbacks:
            try:
                self.element_callbacks[element_id]()
                self.logger.debug(f"Activated element: {element_id}")
            except Exception as e:
                self.logger.error(f"Error activating element {element_id}: {e}")
        
        # Call element's own callback if available
        elif hasattr(element, 'callback') and element.callback:
            try:
                element.callback()
                self.logger.debug(f"Called element callback: {element.label}")
            except Exception as e:
                self.logger.error(f"Error calling element callback {element.label}: {e}")
        
        else:
            self.logger.warning(f"No callback found for element: {element.label}")
    
    def _notify_tab_change(self, new_tab: SettingsTab) -> None:
        """
        Notify all callbacks about tab change.
        
        Args:
            new_tab: New active tab
        """
        for callback in self.tab_change_callbacks:
            try:
                callback(new_tab)
            except Exception as e:
                self.logger.error(f"Error in tab change callback: {e}")
    
    def _navigate_to_previous_tab(self) -> None:
        """Navigate to the previous tab."""
        current_tab = self.tab_manager.get_active_tab()
        tab_configs = [tc.tab_id for tc in self.tab_manager.tab_configs if tc.tab_id in self.tab_manager.tabs]
        
        current_index = tab_configs.index(current_tab) if current_tab in tab_configs else 0
        previous_index = (current_index - 1) % len(tab_configs)
        previous_tab = tab_configs[previous_index]
        
        if self.tab_manager.switch_to_tab(previous_tab):
            self._notify_tab_change(previous_tab)
    
    def _navigate_to_next_tab(self) -> None:
        """Navigate to the next tab."""
        current_tab = self.tab_manager.get_active_tab()
        tab_configs = [tc.tab_id for tc in self.tab_manager.tab_configs if tc.tab_id in self.tab_manager.tabs]
        
        current_index = tab_configs.index(current_tab) if current_tab in tab_configs else 0
        next_index = (current_index + 1) % len(tab_configs)
        next_tab = tab_configs[next_index]
        
        if self.tab_manager.switch_to_tab(next_tab):
            self._notify_tab_change(next_tab)
    
    def _activate_escape(self) -> None:
        """Handle escape key activation."""
        # Call escape callback if available
        if "escape" in self.element_callbacks:
            try:
                self.element_callbacks["escape"]()
                self.logger.debug("Activated escape callback")
            except Exception as e:
                self.logger.error(f"Error in escape callback: {e}")
    
    def get_hovered_element(self) -> Optional[UIElement]:
        """Get currently hovered element."""
        return self.hovered_element
    
    def get_tooltip_info(self) -> Tuple[str, Tuple[int, int]]:
        """Get current tooltip text and position."""
        return self.tooltip_text, self.tooltip_position
    
    def is_mouse_over_ui(self) -> bool:
        """Check if mouse is over any UI element."""
        # Check tabs
        if self.tab_manager.get_tab_at_position(self.mouse_pos):
            return True
        
        # Check action buttons
        for button in self.action_buttons:
            if button.rect.collidepoint(self.mouse_pos):
                return True
        
        # Check content elements
        current_tab = self.tab_manager.get_active_tab()
        content_elements = self.ui_elements.get(current_tab, [])
        
        for element in content_elements:
            if element.rect.collidepoint(self.mouse_pos):
                return True
        
        return False
    
    def clear_callbacks(self) -> None:
        """Clear all callbacks."""
        self.tab_change_callbacks.clear()
        self.element_callbacks.clear()
        self.logger.debug("All callbacks cleared")
    
    def update_layout(self) -> None:
        """Update event handler after layout changes."""
        self._update_hover_state()
        self._update_tooltip()
        self.logger.debug("EventHandler layout updated")
