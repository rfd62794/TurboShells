"""Simple UI event bus for decoupling panel actions from game logic."""

from collections import defaultdict
from typing import Any, Callable, DefaultDict, Dict, List, Optional


class UIEventBus:
    """Lightweight publish/subscribe system for UI events."""

    def __init__(self) -> None:
        self._subscribers: DefaultDict[str, List[Callable[[Dict[str, Any]], None]]] = defaultdict(list)

    def subscribe(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register a callback for an event type."""
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Remove a callback for an event type."""
        if callback in self._subscribers.get(event_type, []):
            self._subscribers[event_type].remove(callback)

    def emit(self, event_type: str, payload: Optional[Dict[str, Any]] = None) -> None:
        """Emit an event to all subscribers."""
        payload = payload or {}
        for callback in list(self._subscribers.get(event_type, [])):
            try:
                callback(payload)
            except Exception as exc:  # pragma: no cover - defensive logging hook
                print(f"[UIEventBus] Error in subscriber for '{event_type}': {exc}")
