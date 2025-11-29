"""Event type constants for consistent event handling."""

from enum import Enum
from typing import Any, Dict, Optional


class UIEvents(str, Enum):
    """UI event type constants."""
    
    # Navigation events
    NAVIGATE = "ui:navigate"
    PANEL_CLOSED = "ui:panel_closed"
    
    # Component events
    UPDATE_UI = "update_ui"
    VIEW_CHANGED = "view_changed"
    
    # Turtle action events
    TURTLE_TRAIN = "turtle:train"
    TURTLE_VIEW = "turtle:view"
    TURTLE_RETIRE = "turtle:retire"
    TURTLE_SELECT = "turtle:select"
    
    # Menu events
    MENU_ACTION = "menu:action"
    MENU_BACK = "menu:back"
    
    # Input events
    BUTTON_PRESS = "input:button_press"
    TOGGLE = "input:toggle"
    SELECTION_CHANGED = "input:selection_changed"
    VALUE_CHANGED = "input:value_changed"
    TEXT_CHANGED = "input:text_changed"


class EventData:
    """Standardized event data structures."""
    
    @staticmethod
    def navigate(state: str) -> Dict[str, Any]:
        """Create navigation event data."""
        return {"state": state}
    
    @staticmethod
    def panel_closed(panel_id: str) -> Dict[str, Any]:
        """Create panel closed event data."""
        return {"panel_id": panel_id}
    
    @staticmethod
    def turtle_action(action: str, turtle_index: int) -> Dict[str, Any]:
        """Create turtle action event data."""
        return {"action": action, "turtle_index": turtle_index}
    
    @staticmethod
    def menu_action(action: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create menu action event data."""
        result = {"action": action}
        if data:
            result.update(data)
        return result
