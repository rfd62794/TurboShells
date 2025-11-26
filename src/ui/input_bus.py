"""Input Event Bus for TurboShells

Provides decoupled input event distribution following the Observer pattern.
Enables clean separation between input sources and event handlers.
"""

import pygame
from typing import Dict, List, Callable, Any, Union
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum


class EventPriority(Enum):
    """Priority levels for event processing."""
    HIGHEST = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    LOWEST = 5


@dataclass
class EventSubscription:
    """Represents an event subscription with metadata."""
    callback: Callable
    priority: EventPriority
    filter_func: Optional[Callable] = None
    enabled: bool = True
    subscription_id: str = ""


class InputBus:
    """Decoupled input event distribution system.
    
    Responsibilities:
    - Manage event subscriptions with priorities
    - Route events to appropriate handlers
    - Support event filtering and conditional processing
    - Maintain subscription lifecycle
    
    This class implements the Observer pattern to decouple input detection
    from input handling, enabling flexible and maintainable event processing.
    """
    
    def __init__(self):
        """Initialize the input event bus."""
        self.subscribers: Dict[Union[str, int], List[EventSubscription]] = defaultdict(list)
        self.global_subscribers: List[EventSubscription] = []
        self._subscription_counter = 0
        self._event_history: List[Dict[str, Any]] = []
        self._max_history = 100
        
    def subscribe(self, 
                  event_type: Union[str, int], 
                  callback: Callable, 
                  priority: EventPriority = EventPriority.NORMAL,
                  filter_func: Optional[Callable] = None,
                  subscription_id: str = "") -> str:
        """Subscribe to specific input events.
        
        Args:
            event_type: PyGame event type (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, etc.)
            callback: Function to call when event occurs
            priority: Priority level for event processing
            filter_func: Optional function to filter events before callback
            subscription_id: Optional unique identifier for subscription
            
        Returns:
            Unique subscription ID for unsubscribing later
        """
        # Generate unique subscription ID if not provided
        if not subscription_id:
            subscription_id = f"sub_{self._subscription_counter}"
            self._subscription_counter += 1
            
        subscription = EventSubscription(
            callback=callback,
            priority=priority,
            filter_func=filter_func,
            enabled=True,
            subscription_id=subscription_id
        )
        
        # Add to subscribers and sort by priority
        self.subscribers[event_type].append(subscription)
        self.subscribers[event_type].sort(key=lambda s: s.priority.value)
        
        return subscription_id
    
    def subscribe_global(self, 
                        callback: Callable, 
                        priority: EventPriority = EventPriority.NORMAL,
                        filter_func: Optional[Callable] = None,
                        subscription_id: str = "") -> str:
        """Subscribe to all events (global handler).
        
        Args:
            callback: Function to call for any event
            priority: Priority level for event processing
            filter_func: Optional function to filter events before callback
            subscription_id: Optional unique identifier for subscription
            
        Returns:
            Unique subscription ID for unsubscribing later
        """
        if not subscription_id:
            subscription_id = f"global_{self._subscription_counter}"
            self._subscription_counter += 1
            
        subscription = EventSubscription(
            callback=callback,
            priority=priority,
            filter_func=filter_func,
            enabled=True,
            subscription_id=subscription_id
        )
        
        self.global_subscribers.append(subscription)
        self.global_subscribers.sort(key=lambda s: s.priority.value)
        
        return subscription_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events using subscription ID.
        
        Args:
            subscription_id: ID of subscription to remove
            
        Returns:
            True if subscription was found and removed, False otherwise
        """
        # Search in type-specific subscriptions
        for event_type, subscriptions in self.subscribers.items():
            for i, sub in enumerate(subscriptions):
                if sub.subscription_id == subscription_id:
                    subscriptions.pop(i)
                    return True
        
        # Search in global subscriptions
        for i, sub in enumerate(self.global_subscribers):
            if sub.subscription_id == subscription_id:
                self.global_subscribers.pop(i)
                return True
                
        return False
    
    def unsubscribe_all(self, event_type: Union[str, int]) -> None:
        """Unsubscribe all handlers for a specific event type.
        
        Args:
            event_type: Event type to clear all subscriptions for
        """
        if event_type in self.subscribers:
            self.subscribers[event_type].clear()
    
    def enable_subscription(self, subscription_id: str) -> bool:
        """Enable a specific subscription.
        
        Args:
            subscription_id: ID of subscription to enable
            
        Returns:
            True if subscription was found and enabled, False otherwise
        """
        subscription = self._find_subscription(subscription_id)
        if subscription:
            subscription.enabled = True
            return True
        return False
    
    def disable_subscription(self, subscription_id: str) -> bool:
        """Disable a specific subscription.
        
        Args:
            subscription_id: ID of subscription to disable
            
        Returns:
            True if subscription was found and disabled, False otherwise
        """
        subscription = self._find_subscription(subscription_id)
        if subscription:
            subscription.enabled = False
            return True
        return False
    
    def publish(self, event: pygame.event.Event) -> bool:
        """Publish event to subscribers.
        
        Args:
            event: PyGame event to publish
            
        Returns:
            True if event was consumed by any subscriber, False otherwise
        """
        event_consumed = False
        
        # Add to event history
        self._add_to_history(event)
        
        # Process global subscribers first
        for subscription in self.global_subscribers:
            if subscription.enabled and self._should_process_event(subscription, event):
                try:
                    if subscription.callback(event):
                        event_consumed = True
                        break  # Event consumed, stop processing
                except Exception as e:
                    print(f"Error in global event subscriber: {e}")
        
        # Process type-specific subscribers if not consumed
        if not event_consumed:
            event_type = event.type if hasattr(event, 'type') else type(event)
            for subscription in self.subscribers.get(event_type, []):
                if subscription.enabled and self._should_process_event(subscription, event):
                    try:
                        if subscription.callback(event):
                            event_consumed = True
                            break  # Event consumed, stop processing
                    except Exception as e:
                        print(f"Error in event subscriber: {e}")
        
        return event_consumed
    
    def _find_subscription(self, subscription_id: str) -> Optional[EventSubscription]:
        """Find a subscription by ID.
        
        Args:
            subscription_id: ID to search for
            
        Returns:
            Subscription if found, None otherwise
        """
        # Search in type-specific subscriptions
        for subscriptions in self.subscribers.values():
            for sub in subscriptions:
                if sub.subscription_id == subscription_id:
                    return sub
        
        # Search in global subscriptions
        for sub in self.global_subscribers:
            if sub.subscription_id == subscription_id:
                return sub
                
        return None
    
    def _should_process_event(self, subscription: EventSubscription, event: pygame.event.Event) -> bool:
        """Check if subscription should process the event.
        
        Args:
            subscription: Subscription to check
            event: Event to check against filter
            
        Returns:
            True if event should be processed, False otherwise
        """
        if subscription.filter_func is None:
            return True
            
        try:
            return subscription.filter_func(event)
        except Exception as e:
            print(f"Error in event filter function: {e}")
            return True  # Process event if filter fails
    
    def _add_to_history(self, event: pygame.event.Event) -> None:
        """Add event to history buffer.
        
        Args:
            event: Event to add to history
        """
        event_info = {
            'type': event.type if hasattr(event, 'type') else str(type(event)),
            'timestamp': pygame.time.get_ticks(),
            'event': event
        }
        
        self._event_history.append(event_info)
        
        # Maintain history size
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
    
    def get_event_history(self, event_type: Optional[Union[str, int]] = None, 
                         limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get event history.
        
        Args:
            event_type: Filter by specific event type (optional)
            limit: Maximum number of events to return (optional)
            
        Returns:
            List of event information dictionaries
        """
        history = self._event_history
        
        if event_type is not None:
            history = [e for e in history if e['type'] == event_type]
        
        if limit is not None:
            history = history[-limit:]
            
        return history
    
    def get_subscription_count(self, event_type: Optional[Union[str, int]] = None) -> int:
        """Get number of active subscriptions.
        
        Args:
            event_type: Specific event type to count (optional)
            
        Returns:
            Number of active subscriptions
        """
        if event_type is not None:
            return len([s for s in self.subscribers.get(event_type, []) if s.enabled])
        else:
            # Count all enabled subscriptions
            total = len([s for s in self.global_subscribers if s.enabled])
            for subscriptions in self.subscribers.values():
                total += len([s for s in subscriptions if s.enabled])
            return total
    
    def clear_all_subscriptions(self) -> None:
        """Clear all event subscriptions."""
        self.subscribers.clear()
        self.global_subscribers.clear()
        self._event_history.clear()
    
    def print_subscription_info(self) -> None:
        """Print debugging information about subscriptions."""
        print("=== Input Bus Subscription Info ===")
        print(f"Global subscribers: {len(self.global_subscribers)}")
        for sub in self.global_subscribers:
            print(f"  - {sub.subscription_id} (Priority: {sub.priority.name}, Enabled: {sub.enabled})")
        
        print("Type-specific subscribers:")
        for event_type, subscriptions in self.subscribers.items():
            enabled_count = len([s for s in subscriptions if s.enabled])
            print(f"  {event_type}: {enabled_count}/{len(subscriptions)} enabled")
            for sub in subscriptions:
                print(f"    - {sub.subscription_id} (Priority: {sub.priority.name}, Enabled: {sub.enabled})")
        print("=" * 35)
