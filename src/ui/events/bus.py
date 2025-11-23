"""
Event bus system for component decoupling.

This module provides a centralized event management system that allows components
to communicate without direct dependencies, following the Observer pattern.
"""

import pygame
from typing import Dict, List, Callable, Any, Optional, Type, Union
from dataclasses import dataclass
from enum import Enum
import time
import weakref
from collections import defaultdict

from .types import Event, EventPriority, EventFilter
from .handlers import EventHandler, AsyncEventHandler


class EventOrder(Enum):
    """Event processing order."""
    FIFO = "fifo"  # First In, First Out
    LIFO = "lifo"  # Last In, First Out
    PRIORITY = "priority"  # By priority value


@dataclass
class EventSubscription:
    """Event subscription information."""
    handler: Callable
    priority: EventPriority = EventPriority.NORMAL
    filter: Optional[EventFilter] = None
    once: bool = False  # Remove after first event
    weak_ref: bool = False  # Use weak reference to handler
    created_time: float = 0.0
    
    def __post_init__(self) -> None:
        if self.created_time == 0.0:
            self.created_time = time.time()


class EventBus:
    """
    Centralized event management system.
    
    Responsibility: Manage event subscription and publication between components.
    """
    
    def __init__(self, max_queue_size: int = 1000):
        """
        Initialize event bus.
        
        Args:
            max_queue_size: Maximum number of events in queue
        """
        # Event subscriptions
        self._subscriptions: Dict[Type[Event], List[EventSubscription]] = defaultdict(list)
        self._global_subscriptions: List[EventSubscription] = []
        
        # Event queue
        self._event_queue: List[Event] = []
        self._max_queue_size = max_queue_size
        
        # Processing configuration
        self._event_order = EventOrder.FIFO
        self._processing_enabled = True
        self._batch_size = 50  # Events to process per frame
        
        # Statistics
        self._events_published = 0
        self._events_processed = 0
        self._events_dropped = 0
        self._subscriptions_count = 0
        
        # Error handling
        self._error_handlers: List[Callable[[Exception, Event], None]] = []
        self._stop_on_error = False
        
        # Debugging
        self._debug_mode = False
        self._event_history: List[Dict[str, Any]] = []
        self._max_history_size = 100
    
    def subscribe(
        self, 
        event_type: Type[Event], 
        handler: Callable[[Event], None],
        priority: EventPriority = EventPriority.NORMAL,
        filter: Optional[EventFilter] = None,
        once: bool = False,
        weak_ref: bool = False
    ) -> str:
        """
        Subscribe to specific event type.
        
        Args:
            event_type: Event class to subscribe to
            handler: Event handler function
            priority: Event processing priority
            filter: Optional event filter
            once: Remove subscription after first event
            weak_ref: Use weak reference to handler
            
        Returns:
            Subscription ID for unsubscribing
        """
        subscription = EventSubscription(
            handler=handler,
            priority=priority,
            filter=filter,
            once=once,
            weak_ref=weak_ref
        )
        
        self._subscriptions[event_type].append(subscription)
        self._subscriptions_count += 1
        
        if self._debug_mode:
            self._log_event(f"SUBSCRIBED: {event_type.__name__} -> {handler}")
        
        return f"{event_type.__name__}_{id(subscription)}"
    
    def subscribe_all(
        self, 
        handler: Callable[[Event], None],
        priority: EventPriority = EventPriority.NORMAL,
        filter: Optional[EventFilter] = None,
        once: bool = False,
        weak_ref: bool = False
    ) -> str:
        """
        Subscribe to all events.
        
        Args:
            handler: Event handler function
            priority: Event processing priority
            filter: Optional event filter
            once: Remove subscription after first event
            weak_ref: Use weak reference to handler
            
        Returns:
            Subscription ID for unsubscribing
        """
        subscription = EventSubscription(
            handler=handler,
            priority=priority,
            filter=filter,
            once=once,
            weak_ref=weak_ref
        )
        
        self._global_subscriptions.append(subscription)
        self._subscriptions_count += 1
        
        if self._debug_mode:
            self._log_event(f"SUBSCRIBED_ALL: {handler}")
        
        return f"ALL_{id(subscription)}"
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from events.
        
        Args:
            subscription_id: Subscription ID returned by subscribe
            
        Returns:
            True if unsubscribed successfully, False otherwise
        """
        # Try to find in type-specific subscriptions
        for event_type, subscriptions in self._subscriptions.items():
            for i, subscription in enumerate(subscriptions):
                if f"{event_type.__name__}_{id(subscription)}" == subscription_id:
                    del subscriptions[i]
                    self._subscriptions_count -= 1
                    
                    if self._debug_mode:
                        self._log_event(f"UNSUBSCRIBED: {event_type.__name__} -> {subscription.handler}")
                    
                    return True
        
        # Try to find in global subscriptions
        for i, subscription in enumerate(self._global_subscriptions):
            if f"ALL_{id(subscription)}" == subscription_id:
                del self._global_subscriptions[i]
                self._subscriptions_count -= 1
                
                if self._debug_mode:
                    self._log_event(f"UNSUBSCRIBED_ALL: {subscription.handler}")
                
                return True
        
        return False
    
    def publish(self, event: Event, immediate: bool = False) -> None:
        """
        Publish event to subscribers.
        
        Args:
            event: Event to publish
            immediate: Process event immediately instead of queuing
        """
        if not self._processing_enabled:
            return
        
        self._events_published += 1
        
        if immediate:
            self._process_event(event)
        else:
            # Add to queue
            if len(self._event_queue) >= self._max_queue_size:
                # Drop oldest event if queue is full
                self._event_queue.pop(0)
                self._events_dropped += 1
                
                if self._debug_mode:
                    self._log_event(f"DROPPED_EVENT: {type(event).__name__}")
            
            self._event_queue.append(event)
            
            if self._debug_mode:
                self._log_event(f"PUBLISHED: {type(event).__name__}")
    
    def publish_batch(self, events: List[Event]) -> None:
        """
        Publish multiple events.
        
        Args:
            events: List of events to publish
        """
        for event in events:
            self.publish(event)
    
    def process_events(self, max_events: Optional[int] = None) -> int:
        """
        Process events in queue.
        
        Args:
            max_events: Maximum number of events to process
            
        Returns:
            Number of events processed
        """
        if not self._processing_enabled or not self._event_queue:
            return 0
        
        max_to_process = min(max_events or self._batch_size, len(self._event_queue))
        processed = 0
        
        # Sort events based on order setting
        if self._event_order == EventOrder.LIFO:
            events_to_process = self._event_queue[-max_to_process:]
            self._event_queue = self._event_queue[:-max_to_process]
        elif self._event_order == EventOrder.PRIORITY:
            # Sort by priority (higher priority first)
            self._event_queue.sort(key=lambda e: e.priority.value, reverse=True)
            events_to_process = self._event_queue[:max_to_process]
            self._event_queue = self._event_queue[max_to_process:]
        else:  # FIFO
            events_to_process = self._event_queue[:max_to_process]
            self._event_queue = self._event_queue[max_to_process:]
        
        # Process events
        for event in events_to_process:
            self._process_event(event)
            processed += 1
        
        return processed
    
    def _process_event(self, event: Event) -> None:
        """Process a single event."""
        try:
            # Get subscribers for this event type
            event_type = type(event)
            subscriptions = self._subscriptions.get(event_type, [])
            
            # Add global subscriptions
            all_subscriptions = subscriptions + self._global_subscriptions
            
            # Sort by priority
            all_subscriptions.sort(key=lambda s: s.priority.value, reverse=True)
            
            # Process subscriptions
            to_remove = []
            
            for subscription in all_subscriptions:
                try:
                    # Apply filter if present
                    if subscription.filter and not subscription.filter(event):
                        continue
                    
                    # Check weak reference
                    if subscription.weak_ref:
                        if hasattr(subscription.handler, '__self__'):
                            # Method reference
                            obj = subscription.handler.__self__
                            if obj is None:  # Object was garbage collected
                                to_remove.append(subscription)
                                continue
                        else:
                            # Function reference
                            if subscription.handler is None:
                                to_remove.append(subscription)
                                continue
                    
                    # Call handler
                    subscription.handler(event)
                    
                    # Remove if once-only subscription
                    if subscription.once:
                        to_remove.append(subscription)
                
                except Exception as e:
                    self._handle_error(e, event)
                    
                    if self._stop_on_error:
                        break
            
            # Clean up once-only subscriptions
            for subscription in to_remove:
                if subscription in self._subscriptions.get(event_type, []):
                    self._subscriptions[event_type].remove(subscription)
                    self._subscriptions_count -= 1
                elif subscription in self._global_subscriptions:
                    self._global_subscriptions.remove(subscription)
                    self._subscriptions_count -= 1
            
            self._events_processed += 1
            
            if self._debug_mode:
                self._log_event(f"PROCESSED: {type(event).__name__}")
        
        except Exception as e:
            self._handle_error(e, event)
    
    def _handle_error(self, error: Exception, event: Event) -> None:
        """Handle event processing error."""
        for error_handler in self._error_handlers:
            try:
                error_handler(error, event)
            except Exception:
                pass  # Don't let error handler errors cascade
        
        if self._debug_mode:
            self._log_event(f"ERROR: {type(error).__name__} processing {type(event).__name__}: {error}")
    
    def clear_queue(self) -> int:
        """
        Clear all events from queue.
        
        Returns:
            Number of events cleared
        """
        count = len(self._event_queue)
        self._event_queue.clear()
        return count
    
    def clear_subscriptions(self) -> int:
        """
        Clear all subscriptions.
        
        Returns:
            Number of subscriptions cleared
        """
        count = self._subscriptions_count
        self._subscriptions.clear()
        self._global_subscriptions.clear()
        self._subscriptions_count = 0
        return count
    
    def set_processing_enabled(self, enabled: bool) -> None:
        """Enable or disable event processing."""
        self._processing_enabled = enabled
    
    def set_event_order(self, order: EventOrder) -> None:
        """Set event processing order."""
        self._event_order = order
    
    def set_batch_size(self, size: int) -> None:
        """Set batch processing size."""
        self._batch_size = max(1, size)
    
    def add_error_handler(self, handler: Callable[[Exception, Event], None]) -> None:
        """Add error handler for event processing errors."""
        self._error_handlers.append(handler)
    
    def set_debug_mode(self, enabled: bool) -> None:
        """Enable or disable debug mode."""
        self._debug_mode = enabled
    
    def _log_event(self, message: str) -> None:
        """Log event for debugging."""
        if not self._debug_mode:
            return
        
        log_entry = {
            "timestamp": time.time(),
            "message": message,
            "queue_size": len(self._event_queue),
            "subscriptions": self._subscriptions_count
        }
        
        self._event_history.append(log_entry)
        
        # Limit history size
        if len(self._event_history) > self._max_history_size:
            self._event_history.pop(0)
        
        # Also print to console
        print(f"[EventBus] {message}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get event bus statistics."""
        return {
            "events_published": self._events_published,
            "events_processed": self._events_processed,
            "events_dropped": self._events_dropped,
            "events_queued": len(self._event_queue),
            "subscriptions_count": self._subscriptions_count,
            "processing_enabled": self._processing_enabled,
            "debug_mode": self._debug_mode,
            "event_order": self._event_order.value,
            "batch_size": self._batch_size
        }
    
    def get_subscription_info(self) -> Dict[str, Any]:
        """Get detailed subscription information."""
        info = {}
        
        for event_type, subscriptions in self._subscriptions.items():
            info[event_type.__name__] = [
                {
                    "handler": str(subscription.handler),
                    "priority": subscription.priority.value,
                    "once": subscription.once,
                    "weak_ref": subscription.weak_ref,
                    "created_time": subscription.created_time
                }
                for subscription in subscriptions
            ]
        
        info["ALL_EVENTS"] = [
            {
                "handler": str(subscription.handler),
                "priority": subscription.priority.value,
                "once": subscription.once,
                "weak_ref": subscription.weak_ref,
                "created_time": subscription.created_time
            }
            for subscription in self._global_subscriptions
        ]
        
        return info
    
    def get_event_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get event history."""
        if limit:
            return self._event_history[-limit:]
        return self._event_history.copy()
    
    def validate_subscriptions(self) -> List[str]:
        """
        Validate subscriptions and return issues.
        
        Returns:
            List of validation issues
        """
        issues = []
        
        for event_type, subscriptions in self._subscriptions.items():
            for i, subscription in enumerate(subscriptions):
                # Check for dead weak references
                if subscription.weak_ref:
                    if hasattr(subscription.handler, '__self__'):
                        obj = subscription.handler.__self__
                        if obj is None:
                            issues.append(f"Dead weak reference in {event_type.__name__} subscription {i}")
                
                # Check for invalid handlers
                if not callable(subscription.handler):
                    issues.append(f"Non-callable handler in {event_type.__name__} subscription {i}")
        
        return issues
    
    def cleanup_dead_references(self) -> int:
        """
        Clean up dead weak references.
        
        Returns:
            Number of dead references removed
        """
        removed = 0
        
        for event_type, subscriptions in self._subscriptions.items():
            to_remove = []
            
            for subscription in subscriptions:
                if subscription.weak_ref:
                    if hasattr(subscription.handler, '__self__'):
                        obj = subscription.handler.__self__
                        if obj is None:  # Object was garbage collected
                            to_remove.append(subscription)
                    else:
                        if subscription.handler is None:
                            to_remove.append(subscription)
            
            for subscription in to_remove:
                subscriptions.remove(subscription)
                removed += 1
                self._subscriptions_count -= 1
        
        # Clean up global subscriptions
        to_remove = []
        for subscription in self._global_subscriptions:
            if subscription.weak_ref:
                if hasattr(subscription.handler, '__self__'):
                    obj = subscription.handler.__self__
                    if obj is None:
                        to_remove.append(subscription)
                else:
                    if subscription.handler is None:
                        to_remove.append(subscription)
        
        for subscription in to_remove:
            self._global_subscriptions.remove(subscription)
            removed += 1
            self._subscriptions_count -= 1
        
        return removed


# Global event bus instance
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """
    Get global event bus instance.
    
    Returns:
        Event bus instance
    """
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


def publish_event(event: Event, immediate: bool = False) -> None:
    """
    Publish event to global event bus.
    
    Args:
        event: Event to publish
        immediate: Process event immediately
    """
    get_event_bus().publish(event, immediate)


def subscribe_to_event(
    event_type: Type[Event], 
    handler: Callable[[Event], None],
    priority: EventPriority = EventPriority.NORMAL,
    filter: Optional[EventFilter] = None,
    once: bool = False,
    weak_ref: bool = False
) -> str:
    """
    Subscribe to event on global event bus.
    
    Args:
        event_type: Event class to subscribe to
        handler: Event handler function
        priority: Event processing priority
        filter: Optional event filter
        once: Remove subscription after first event
        weak_ref: Use weak reference to handler
        
    Returns:
        Subscription ID
    """
    return get_event_bus().subscribe(event_type, handler, priority, filter, once, weak_ref)


def unsubscribe_from_event(subscription_id: str) -> bool:
    """
    Unsubscribe from event on global event bus.
    
    Args:
        subscription_id: Subscription ID
        
    Returns:
        True if unsubscribed successfully
    """
    return get_event_bus().unsubscribe(subscription_id)


def process_events(max_events: Optional[int] = None) -> int:
    """
    Process events on global event bus.
    
    Args:
        max_events: Maximum number of events to process
        
    Returns:
        Number of events processed
    """
    return get_event_bus().process_events(max_events)
