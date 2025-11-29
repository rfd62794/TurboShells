"""Standardized event bus interface."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional
from .event_types import UIEvents, EventData


class IEventBus(ABC):
    """Interface for event bus implementations."""
    
    @abstractmethod
    def subscribe(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Subscribe to an event type."""
        pass
    
    @abstractmethod
    def unsubscribe(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Unsubscribe from an event type."""
        pass
    
    @abstractmethod
    def emit(self, event_type: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Emit an event to all subscribers."""
        pass


class StandardEventBus(IEventBus):
    """Standardized event bus implementation."""
    
    def __init__(self, name: str = "EventBus"):
        self.name = name
        self._subscribers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}
    
    def subscribe(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Subscribe to an event type with validation."""
        if not callable(callback):
            raise ValueError(f"Callback must be callable for event '{event_type}'")
        
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)
            print(f"[{self.name}] Subscribed to '{event_type}'")
    
    def unsubscribe(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Unsubscribe from an event type."""
        if event_type in self._subscribers and callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
            print(f"[{self.name}] Unsubscribed from '{event_type}'")
    
    def emit(self, event_type: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Emit an event to all subscribers with error handling."""
        data = data or {}
        
        if event_type not in self._subscribers:
            return  # No subscribers, silently ignore
        
        for callback in self._subscribers[event_type]:
            try:
                callback(data)
            except Exception as exc:
                print(f"[{self.name}] Error in subscriber for '{event_type}': {exc}")
    
    def clear(self) -> None:
        """Clear all subscribers."""
        self._subscribers.clear()
        print(f"[{self.name}] All subscribers cleared")
    
    def get_subscriber_count(self, event_type: str) -> int:
        """Get number of subscribers for an event type."""
        return len(self._subscribers.get(event_type, []))
    
    def list_events(self) -> list:
        """List all event types with subscribers."""
        return list(self._subscribers.keys())
