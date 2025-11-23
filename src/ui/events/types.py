"""
Event types and definitions for the UI event system.

This module defines the base event class and specific event types used
throughout the UI system for component communication.
"""

import pygame
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid


class EventPriority(Enum):
    """Event processing priority."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Event:
    """Base event class."""
    timestamp: float = field(default_factory=time.time)
    source: Optional[str] = None
    priority: EventPriority = EventPriority.NORMAL
    data: Dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    
    def __post_init__(self) -> None:
        """Validate event after initialization."""
        if self.source is None:
            self.source = "unknown"


# Component Events

@dataclass
class ComponentEvent(Event):
    """Base class for component-related events."""
    component_id: str = ""
    component_type: str = ""


@dataclass
class ComponentCreatedEvent(ComponentEvent):
    """Event fired when a component is created."""
    pass


@dataclass
class ComponentDestroyedEvent(ComponentEvent):
    """Event fired when a component is destroyed."""
    pass


@dataclass
class ComponentShownEvent(ComponentEvent):
    """Event fired when a component becomes visible."""
    pass


@dataclass
class ComponentHiddenEvent(ComponentEvent):
    """Event fired when a component becomes hidden."""
    pass


@dataclass
class ComponentEnabledEvent(ComponentEvent):
    """Event fired when a component becomes enabled."""
    pass


@dataclass
class ComponentDisabledEvent(ComponentEvent):
    """Event fired when a component becomes disabled."""
    pass


@dataclass
class ComponentFocusedEvent(ComponentEvent):
    """Event fired when a component gains focus."""
    pass


@dataclass
class ComponentUnfocusedEvent(ComponentEvent):
    """Event fired when a component loses focus."""
    pass


# Interaction Events

@dataclass
class InteractionEvent(ComponentEvent):
    """Base class for user interaction events."""
    mouse_position: tuple[int, int] = (0, 0)
    mouse_button: Optional[int] = None
    keyboard_key: Optional[int] = None
    modifiers: int = 0


@dataclass
class ButtonClickEvent(InteractionEvent):
    """Event fired when a button is clicked."""
    button_text: str = ""
    
    def __post_init__(self) -> None:
        if self.priority == EventPriority.NORMAL:
            self.priority = EventPriority.HIGH


@dataclass
class ButtonRightClickEvent(InteractionEvent):
    """Event fired when a button is right-clicked."""
    button_text: str = ""


@dataclass
class ButtonHoverEnterEvent(InteractionEvent):
    """Event fired when mouse enters button area."""
    button_text: str = ""


@dataclass
class ButtonHoverExitEvent(InteractionEvent):
    """Event fired when mouse leaves button area."""
    button_text: str = ""


@dataclass
class SliderChangeEvent(InteractionEvent):
    """Event fired when slider value changes."""
    old_value: float = 0.0
    new_value: float = 0.0
    min_value: float = 0.0
    max_value: float = 1.0
    
    def __post_init__(self) -> None:
        if self.priority == EventPriority.NORMAL:
            self.priority = EventPriority.HIGH


@dataclass
class SliderDragStartEvent(InteractionEvent):
    """Event fired when slider dragging starts."""
    initial_value: float = 0.0


@dataclass
class SliderDragEndEvent(InteractionEvent):
    """Event fired when slider dragging ends."""
    final_value: float = 0.0


@dataclass
class CheckboxToggleEvent(InteractionEvent):
    """Event fired when checkbox is toggled."""
    checked: bool = False
    label: str = ""
    
    def __post_init__(self) -> None:
        if self.priority == EventPriority.NORMAL:
            self.priority = EventPriority.HIGH


@dataclass
class DropdownChangeEvent(InteractionEvent):
    """Event fired when dropdown selection changes."""
    old_value: Any = None
    new_value: Any = None
    old_index: int = -1
    new_index: int = -1
    option_label: str = ""
    
    def __post_init__(self) -> None:
        if self.priority == EventPriority.NORMAL:
            self.priority = EventPriority.HIGH


@dataclass
class DropdownOpenEvent(InteractionEvent):
    """Event fired when dropdown is opened."""
    pass


@dataclass
class DropdownCloseEvent(InteractionEvent):
    """Event fired when dropdown is closed."""
    selected_value: Any = None


# Container Events

@dataclass
class ContainerEvent(ComponentEvent):
    """Base class for container-related events."""
    pass


@dataclass
class TabChangeEvent(ContainerEvent):
    """Event fired when tab selection changes."""
    old_tab_index: int = -1
    new_tab_index: int = -1
    old_tab_title: str = ""
    new_tab_title: str = ""
    
    def __post_init__(self) -> None:
        if self.priority == EventPriority.NORMAL:
            self.priority = EventPriority.HIGH


@dataclass
class ScrollEvent(ContainerEvent):
    """Event fired when container is scrolled."""
    old_offset: int = 0
    new_offset: int = 0
    content_height: int = 0
    viewport_height: int = 0
    scroll_percentage: float = 0.0


@dataclass
class ScrollToTopEvent(ContainerEvent):
    """Event fired when scrolled to top."""
    pass


@dataclass
class ScrollToBottomEvent(ContainerEvent):
    """Event fired when scrolled to bottom."""
    pass


# View Events

@dataclass
class ViewEvent(Event):
    """Base class for view-related events."""
    view_name: str = ""
    view_type: str = ""


@dataclass
class ViewShownEvent(ViewEvent):
    """Event fired when a view becomes visible."""
    pass


@dataclass
class ViewHiddenEvent(ViewEvent):
    """Event fired when a view becomes hidden."""
    pass


@dataclass
class ViewActivatedEvent(ViewEvent):
    """Event fired when a view becomes active."""
    pass


@dataclass
class ViewDeactivatedEvent(ViewEvent):
    """Event fired when a view becomes inactive."""
    pass


@dataclass
class ViewNavigationEvent(ViewEvent):
    """Event fired when navigating between views."""
    from_view: str = ""
    to_view: str = ""
    navigation_type: str = ""  # "forward", "backward", "direct"
    
    def __post_init__(self) -> None:
        if self.priority == EventPriority.NORMAL:
            self.priority = EventPriority.HIGH


# Settings Events

@dataclass
class SettingsEvent(Event):
    """Base class for settings-related events."""
    pass


@dataclass
class SettingsChangedEvent(SettingsEvent):
    """Event fired when a setting value changes."""
    setting_key: str = ""
    old_value: Any = None
    new_value: Any = None
    setting_category: str = ""
    
    def __post_init__(self) -> None:
        if self.priority == EventPriority.NORMAL:
            self.priority = EventPriority.HIGH


@dataclass
class SettingsAppliedEvent(SettingsEvent):
    """Event fired when settings are applied."""
    changed_settings: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        if self.priority == EventPriority.NORMAL:
            self.priority = EventPriority.CRITICAL


@dataclass
class SettingsResetEvent(SettingsEvent):
    """Event fired when settings are reset to defaults."""
    reset_category: Optional[str] = None
    
    def __post_init__(self) -> None:
        if self.priority == EventPriority.NORMAL:
            self.priority = EventPriority.CRITICAL


@dataclass
class SettingsLoadedEvent(SettingsEvent):
    """Event fired when settings are loaded from file."""
    file_path: str = ""
    success: bool = True
    error_message: str = ""


@dataclass
class SettingsSavedEvent(SettingsEvent):
    """Event fired when settings are saved to file."""
    file_path: str = ""
    success: bool = True
    error_message: str = ""


# System Events

@dataclass
class SystemEvent(Event):
    """Base class for system-related events."""
    pass


@dataclass
class ScreenResizeEvent(SystemEvent):
    """Event fired when screen is resized."""
    old_width: int = 0
    old_height: int = 0
    new_width: int = 0
    new_height: int = 0
    
    def __post_init__(self) -> None:
        if self.priority == EventPriority.NORMAL:
            self.priority = EventPriority.HIGH


@dataclass
class ThemeChangeEvent(SystemEvent):
    """Event fired when theme is changed."""
    old_theme: str = ""
    new_theme: str = ""
    
    def __post_init__(self) -> None:
        if self.priority == EventPriority.NORMAL:
            self.priority = EventPriority.HIGH


@dataclass
class FontChangeEvent(SystemEvent):
    """Event fired when font settings change."""
    font_type: str = ""
    old_size: int = 0
    new_size: int = 0


@dataclass
class LanguageChangeEvent(SystemEvent):
    """Event fired when language is changed."""
    old_language: str = ""
    new_language: str = ""
    
    def __post_init__(self) -> None:
        if self.priority == EventPriority.NORMAL:
            self.priority = EventPriority.HIGH


# Input Events

@dataclass
class InputEvent(Event):
    """Base class for input-related events."""
    pass


@dataclass
class KeyboardInputEvent(InputEvent):
    """Event fired for keyboard input."""
    key: int = 0
    modifiers: int = 0
    unicode_char: str = ""
    repeat: bool = False


@dataclass
class MouseInputEvent(InputEvent):
    """Event fired for mouse input."""
    position: tuple[int, int] = (0, 0)
    button: Optional[int] = None
    delta: tuple[int, int] = (0, 0)  # For wheel events


@dataclass
class GamepadInputEvent(InputEvent):
    """Event fired for gamepad input."""
    gamepad_id: int = 0
    button: Optional[int] = None
    axis: Optional[int] = None
    value: float = 0.0


# Application Events

@dataclass
class ApplicationEvent(Event):
    """Base class for application-related events."""
    pass


@dataclass
class ApplicationStartedEvent(ApplicationEvent):
    """Event fired when application starts."""
    pass


@dataclass
class ApplicationStoppingEvent(ApplicationEvent):
    """Event fired when application is stopping."""
    pass


@dataclass
class ApplicationPausedEvent(ApplicationEvent):
    """Event fired when application is paused."""
    pass


@dataclass
class ApplicationResumedEvent(ApplicationEvent):
    """Event fired when application is resumed."""
    pass


@dataclass
class ApplicationFocusGainedEvent(ApplicationEvent):
    """Event fired when application gains focus."""
    pass


@dataclass
class ApplicationFocusLostEvent(ApplicationEvent):
    """Event fired when application loses focus."""
    pass


# Error Events

@dataclass
class ErrorEvent(Event):
    """Base class for error-related events."""
    error_message: str = ""
    error_type: str = ""
    stack_trace: str = ""
    
    def __post_init__(self) -> None:
        if self.priority == EventPriority.NORMAL:
            self.priority = EventPriority.CRITICAL


@dataclass
class ComponentErrorEvent(ErrorEvent, ComponentEvent):
    """Event fired when a component encounters an error."""
    pass


@dataclass
class SystemErrorEvent(ErrorEvent, SystemEvent):
    """Event fired when system encounters an error."""
    pass


@dataclass
class UserErrorEvent(ErrorEvent):
    """Event fired for user-actionable errors."""
    user_message: str = ""  # User-friendly error message
    can_retry: bool = False
    recovery_action: Optional[str] = None


# Debug Events

@dataclass
class DebugEvent(Event):
    """Base class for debug-related events."""
    pass


@dataclass
class PerformanceEvent(DebugEvent):
    """Event fired for performance monitoring."""
    metric_name: str = ""
    metric_value: float = 0.0
    metric_unit: str = ""
    frame_time: float = 0.0


@dataclass
class MemoryEvent(DebugEvent):
    """Event fired for memory monitoring."""
    memory_usage: int = 0
    memory_peak: int = 0
    component_count: int = 0


@dataclass
class LogEvent(DebugEvent):
    """Event fired for logging."""
    log_level: str = "INFO"
    log_message: str = ""
    logger_name: str = ""


# Custom Event Factory

class EventFactory:
    """Factory for creating common events."""
    
    @staticmethod
    def create_button_click(component_id: str, button_text: str, mouse_pos: tuple[int, int]) -> ButtonClickEvent:
        """Create button click event."""
        return ButtonClickEvent(
            component_id=component_id,
            component_type="Button",
            button_text=button_text,
            mouse_position=mouse_pos,
            mouse_button=1
        )
    
    @staticmethod
    def create_slider_change(component_id: str, old_val: float, new_val: float, min_val: float, max_val: float) -> SliderChangeEvent:
        """Create slider change event."""
        return SliderChangeEvent(
            component_id=component_id,
            component_type="Slider",
            old_value=old_val,
            new_value=new_val,
            min_value=min_val,
            max_value=max_val
        )
    
    @staticmethod
    def create_settings_change(key: str, old_val: Any, new_val: Any, category: str = "") -> SettingsChangedEvent:
        """Create settings change event."""
        return SettingsChangedEvent(
            setting_key=key,
            old_value=old_val,
            new_value=new_val,
            setting_category=category
        )
    
    @staticmethod
    def create_tab_change(component_id: str, old_index: int, new_index: int, old_title: str, new_title: str) -> TabChangeEvent:
        """Create tab change event."""
        return TabChangeEvent(
            component_id=component_id,
            component_type="TabContainer",
            old_tab_index=old_index,
            new_tab_index=new_index,
            old_tab_title=old_title,
            new_tab_title=new_title
        )
    
    @staticmethod
    def create_screen_resize(old_w: int, old_h: int, new_w: int, new_h: int) -> ScreenResizeEvent:
        """Create screen resize event."""
        return ScreenResizeEvent(
            old_width=old_w,
            old_height=old_h,
            new_width=new_w,
            new_height=new_h
        )


# Event type registry for dynamic event creation

class EventTypeRegistry:
    """Registry for event types."""
    
    def __init__(self):
        self._event_types: Dict[str, type] = {}
        self._register_builtin_events()
    
    def register_event_type(self, name: str, event_class: type) -> None:
        """Register a custom event type."""
        if not issubclass(event_class, Event):
            raise ValueError(f"Event class {event_class} must inherit from Event")
        
        self._event_types[name] = event_class
    
    def get_event_type(self, name: str) -> Optional[type]:
        """Get event type by name."""
        return self._event_types.get(name)
    
    def create_event(self, name: str, **kwargs) -> Optional[Event]:
        """Create event instance by name."""
        event_class = self.get_event_type(name)
        if event_class:
            return event_class(**kwargs)
        return None
    
    def get_all_event_types(self) -> Dict[str, type]:
        """Get all registered event types."""
        return self._event_types.copy()
    
    def _register_builtin_events(self) -> None:
        """Register built-in event types."""
        # Component events
        self._event_types.update({
            "component_created": ComponentCreatedEvent,
            "component_destroyed": ComponentDestroyedEvent,
            "component_shown": ComponentShownEvent,
            "component_hidden": ComponentHiddenEvent,
            "component_enabled": ComponentEnabledEvent,
            "component_disabled": ComponentDisabledEvent,
            "component_focused": ComponentFocusedEvent,
            "component_unfocused": ComponentUnfocusedEvent,
        })
        
        # Interaction events
        self._event_types.update({
            "button_click": ButtonClickEvent,
            "button_right_click": ButtonRightClickEvent,
            "button_hover_enter": ButtonHoverEnterEvent,
            "button_hover_exit": ButtonHoverExitEvent,
            "slider_change": SliderChangeEvent,
            "slider_drag_start": SliderDragStartEvent,
            "slider_drag_end": SliderDragEndEvent,
            "checkbox_toggle": CheckboxToggleEvent,
            "dropdown_change": DropdownChangeEvent,
            "dropdown_open": DropdownOpenEvent,
            "dropdown_close": DropdownCloseEvent,
        })
        
        # Container events
        self._event_types.update({
            "tab_change": TabChangeEvent,
            "scroll": ScrollEvent,
            "scroll_to_top": ScrollToTopEvent,
            "scroll_to_bottom": ScrollToBottomEvent,
        })
        
        # View events
        self._event_types.update({
            "view_shown": ViewShownEvent,
            "view_hidden": ViewHiddenEvent,
            "view_activated": ViewActivatedEvent,
            "view_deactivated": ViewDeactivatedEvent,
            "view_navigation": ViewNavigationEvent,
        })
        
        # Settings events
        self._event_types.update({
            "settings_changed": SettingsChangedEvent,
            "settings_applied": SettingsAppliedEvent,
            "settings_reset": SettingsResetEvent,
            "settings_loaded": SettingsLoadedEvent,
            "settings_saved": SettingsSavedEvent,
        })
        
        # System events
        self._event_types.update({
            "screen_resize": ScreenResizeEvent,
            "theme_change": ThemeChangeEvent,
            "font_change": FontChangeEvent,
            "language_change": LanguageChangeEvent,
        })
        
        # Application events
        self._event_types.update({
            "application_started": ApplicationStartedEvent,
            "application_stopping": ApplicationStoppingEvent,
            "application_paused": ApplicationPausedEvent,
            "application_resumed": ApplicationResumedEvent,
            "application_focus_gained": ApplicationFocusGainedEvent,
            "application_focus_lost": ApplicationFocusLostEvent,
        })
        
        # Error events
        self._event_types.update({
            "component_error": ComponentErrorEvent,
            "system_error": SystemErrorEvent,
            "user_error": UserErrorEvent,
        })
        
        # Debug events
        self._event_types.update({
            "performance": PerformanceEvent,
            "memory": MemoryEvent,
            "log": LogEvent,
        })


# Global event type registry
_event_type_registry: Optional[EventTypeRegistry] = None


def get_event_type_registry() -> EventTypeRegistry:
    """Get global event type registry."""
    global _event_type_registry
    if _event_type_registry is None:
        _event_type_registry = EventTypeRegistry()
    return _event_type_registry


def register_event_type(name: str, event_class: type) -> None:
    """Register a custom event type."""
    get_event_type_registry().register_event_type(name, event_class)


def create_event(name: str, **kwargs) -> Optional[Event]:
    """Create event by name."""
    return get_event_type_registry().create_event(name, **kwargs)
