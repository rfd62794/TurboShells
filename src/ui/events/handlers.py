"""
Event handlers and filters for the UI event system.

This module provides base handler classes, filters, and utilities for
processing events in the event bus system.
"""

import pygame
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, List, Dict, Union
from dataclasses import dataclass
from enum import Enum
import asyncio
import time
import weakref

from .types import Event


class HandlerResult(Enum):
    """Event handler result status."""
    SUCCESS = "success"
    FAILURE = "failure"
    STOP_PROPAGATION = "stop_propagation"
    RETRY_LATER = "retry_later"


@dataclass
class HandlerResponse:
    """Response from event handler."""
    result: HandlerResult
    message: str = ""
    retry_delay: float = 0.0
    data: Dict[str, Any] = None
    
    def __post_init__(self) -> None:
        if self.data is None:
            self.data = {}


class EventFilter(ABC):
    """Base class for event filters."""
    
    @abstractmethod
    def should_process(self, event: Event) -> bool:
        """
        Determine if event should be processed.
        
        Args:
            event: Event to filter
            
        Returns:
            True if event should be processed, False otherwise
        """
        pass


class EventTypeFilter(EventFilter):
    """Filter events by type."""
    
    def __init__(self, *event_types: type):
        """
        Initialize filter with allowed event types.
        
        Args:
            event_types: Allowed event types
        """
        self.allowed_types = set(event_types)
    
    def should_process(self, event: Event) -> bool:
        """Check if event type is allowed."""
        return type(event) in self.allowed_types


class EventSourceFilter(EventFilter):
    """Filter events by source."""
    
    def __init__(self, *sources: str):
        """
        Initialize filter with allowed sources.
        
        Args:
            sources: Allowed event sources
        """
        self.allowed_sources = set(sources)
    
    def should_process(self, event: Event) -> bool:
        """Check if event source is allowed."""
        return event.source in self.allowed_sources


class EventPriorityFilter(EventFilter):
    """Filter events by priority level."""
    
    def __init__(self, min_priority: Any):
        """
        Initialize filter with minimum priority.
        
        Args:
            min_priority: Minimum priority level to allow
        """
        self.min_priority = min_priority
    
    def should_process(self, event: Event) -> bool:
        """Check if event priority meets minimum."""
        return event.priority.value >= self.min_priority.value


class EventDataFilter(EventFilter):
    """Filter events by data content."""
    
    def __init__(self, key: str, value: Any, operator: str = "equals"):
        """
        Initialize filter with data condition.
        
        Args:
            key: Data key to check
            value: Expected value
            operator: Comparison operator ("equals", "not_equals", "contains", "greater_than", "less_than")
        """
        self.key = key
        self.value = value
        self.operator = operator
    
    def should_process(self, event: Event) -> bool:
        """Check if event data meets condition."""
        if self.key not in event.data:
            return self.operator == "not_equals"
        
        event_value = event.data[self.key]
        
        if self.operator == "equals":
            return event_value == self.value
        elif self.operator == "not_equals":
            return event_value != self.value
        elif self.operator == "contains":
            return self.value in str(event_value)
        elif self.operator == "greater_than":
            return event_value > self.value
        elif self.operator == "less_than":
            return event_value < self.value
        else:
            return False


class CompositeEventFilter(EventFilter):
    """Composite filter that combines multiple filters."""
    
    def __init__(self, operator: str = "and", *filters: EventFilter):
        """
        Initialize composite filter.
        
        Args:
            operator: Logical operator ("and", "or", "not")
            filters: Filters to combine
        """
        self.operator = operator.lower()
        self.filters = list(filters)
    
    def should_process(self, event: Event) -> bool:
        """Apply composite filter logic."""
        if not self.filters:
            return True
        
        if self.operator == "and":
            return all(f.should_process(event) for f in self.filters)
        elif self.operator == "or":
            return any(f.should_process(event) for f in self.filters)
        elif self.operator == "not":
            return not all(f.should_process(event) for f in self.filters)
        else:
            return True
    
    def add_filter(self, filter: EventFilter) -> None:
        """Add a filter to the composite."""
        self.filters.append(filter)
    
    def remove_filter(self, filter: EventFilter) -> None:
        """Remove a filter from the composite."""
        if filter in self.filters:
            self.filters.remove(filter)


class EventHandler(ABC):
    """Base class for event handlers."""
    
    @abstractmethod
    def handle(self, event: Event) -> HandlerResponse:
        """
        Handle an event.
        
        Args:
            event: Event to handle
            
        Returns:
            Handler response
        """
        pass
    
    def can_handle(self, event: Event) -> bool:
        """
        Check if handler can process the event.
        
        Args:
            event: Event to check
            
        Returns:
            True if handler can process event
        """
        return True


class FunctionEventHandler(EventHandler):
    """Event handler that wraps a function."""
    
    def __init__(self, handler_func: Callable[[Event], HandlerResponse]):
        """
        Initialize with handler function.
        
        Args:
            handler_func: Function to call for handling events
        """
        self.handler_func = handler_func
    
    def handle(self, event: Event) -> HandlerResponse:
        """Handle event using wrapped function."""
        try:
            return self.handler_func(event)
        except Exception as e:
            return HandlerResponse(
                result=HandlerResult.FAILURE,
                message=f"Handler function error: {e}"
            )
    
    def can_handle(self, event: Event) -> bool:
        """Always return True for function handlers."""
        return True


class AsyncEventHandler(EventHandler):
    """Base class for asynchronous event handlers."""
    
    @abstractmethod
    async def handle_async(self, event: Event) -> HandlerResponse:
        """
        Handle an event asynchronously.
        
        Args:
            event: Event to handle
            
        Returns:
            Handler response
        """
        pass
    
    def handle(self, event: Event) -> HandlerResponse:
        """Handle event synchronously by running async function."""
        try:
            # Run async function synchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(self.handle_async(event))
                return result
            finally:
                loop.close()
        except Exception as e:
            return HandlerResponse(
                result=HandlerResult.FAILURE,
                message=f"Async handler error: {e}"
            )


class ConditionalEventHandler(EventHandler):
    """Event handler that applies conditions before handling."""
    
    def __init__(self, condition: Callable[[Event], bool], handler: EventHandler):
        """
        Initialize with condition and handler.
        
        Args:
            condition: Function that returns True if handler should be called
            handler: Handler to call if condition is met
        """
        self.condition = condition
        self.handler = handler
    
    def handle(self, event: Event) -> HandlerResponse:
        """Handle event if condition is met."""
        if self.condition(event):
            return self.handler.handle(event)
        else:
            return HandlerResponse(
                result=HandlerResult.SUCCESS,
                message="Condition not met, event not handled"
            )
    
    def can_handle(self, event: Event) -> bool:
        """Check if condition is met."""
        return self.condition(event) and self.handler.can_handle(event)


class RetryEventHandler(EventHandler):
    """Event handler that retries on failure."""
    
    def __init__(self, handler: EventHandler, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize with handler and retry configuration.
        
        Args:
            handler: Handler to wrap
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.handler = handler
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def handle(self, event: Event) -> HandlerResponse:
        """Handle event with retry logic."""
        last_response = None
        
        for attempt in range(self.max_retries + 1):
            response = self.handler.handle(event)
            
            if response.result == HandlerResult.SUCCESS:
                return response
            
            last_response = response
            
            if attempt < self.max_retries:
                time.sleep(self.retry_delay)
        
        return last_response or HandlerResponse(
            result=HandlerResult.FAILURE,
            message=f"Handler failed after {self.max_retries} retries"
        )


class LoggingEventHandler(EventHandler):
    """Event handler that logs events."""
    
    def __init__(self, handler: EventHandler, log_level: str = "INFO"):
        """
        Initialize with handler and log level.
        
        Args:
            handler: Handler to wrap
            log_level: Log level for messages
        """
        self.handler = handler
        self.log_level = log_level.upper()
    
    def handle(self, event: Event) -> HandlerResponse:
        """Handle event with logging."""
        # Log event before handling
        self._log(f"Handling event: {type(event).__name__} from {event.source}")
        
        # Handle event
        response = self.handler.handle(event)
        
        # Log response
        self._log(f"Event handled: {response.result.value} - {response.message}")
        
        return response
    
    def _log(self, message: str) -> None:
        """Log message with configured level."""
        print(f"[{self.log_level}] {message}")


class MetricsEventHandler(EventHandler):
    """Event handler that collects metrics."""
    
    def __init__(self, handler: EventHandler):
        """
        Initialize with handler to wrap.
        
        Args:
            handler: Handler to wrap
        """
        self.handler = handler
        self.metrics = {
            "events_handled": 0,
            "events_failed": 0,
            "total_time": 0.0,
            "average_time": 0.0,
            "min_time": float('inf'),
            "max_time": 0.0
        }
    
    def handle(self, event: Event) -> HandlerResponse:
        """Handle event with metrics collection."""
        start_time = time.time()
        
        try:
            response = self.handler.handle(event)
            
            # Update metrics
            end_time = time.time()
            duration = end_time - start_time
            
            self.metrics["events_handled"] += 1
            self.metrics["total_time"] += duration
            self.metrics["average_time"] = self.metrics["total_time"] / self.metrics["events_handled"]
            self.metrics["min_time"] = min(self.metrics["min_time"], duration)
            self.metrics["max_time"] = max(self.metrics["max_time"], duration)
            
            if response.result == HandlerResult.FAILURE:
                self.metrics["events_failed"] += 1
            
            return response
        
        except Exception as e:
            self.metrics["events_failed"] += 1
            return HandlerResponse(
                result=HandlerResult.FAILURE,
                message=f"Metrics handler error: {e}"
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics."""
        return self.metrics.copy()
    
    def reset_metrics(self) -> None:
        """Reset collected metrics."""
        self.metrics = {
            "events_handled": 0,
            "events_failed": 0,
            "total_time": 0.0,
            "average_time": 0.0,
            "min_time": float('inf'),
            "max_time": 0.0
        }


class WeakReferenceEventHandler(EventHandler):
    """Event handler that uses weak references to avoid memory leaks."""
    
    def __init__(self, target_object: Any, method_name: str):
        """
        Initialize with target object and method name.
        
        Args:
            target_object: Object containing the handler method
            method_name: Name of the handler method
        """
        self.target_ref = weakref.ref(target_object)
        self.method_name = method_name
    
    def handle(self, event: Event) -> HandlerResponse:
        """Handle event using weak reference."""
        target = self.target_ref()
        if target is None:
            return HandlerResponse(
                result=HandlerResult.FAILURE,
                message="Target object has been garbage collected"
            )
        
        try:
            method = getattr(target, self.method_name)
            return method(event)
        except AttributeError:
            return HandlerResponse(
                result=HandlerResult.FAILURE,
                message=f"Method {self.method_name} not found on target object"
            )
        except Exception as e:
            return HandlerResponse(
                result=HandlerResult.FAILURE,
                message=f"Method execution error: {e}"
            )
    
    def is_valid(self) -> bool:
        """Check if weak reference is still valid."""
        return self.target_ref() is not None


class EventChain:
    """Chain of event handlers that process events in sequence."""
    
    def __init__(self, *handlers: EventHandler):
        """
        Initialize event chain.
        
        Args:
            handlers: Handlers to add to chain
        """
        self.handlers = list(handlers)
        self.stop_on_failure = False
        self.stop_on_stop_propagation = True
    
    def add_handler(self, handler: EventHandler) -> None:
        """Add handler to chain."""
        self.handlers.append(handler)
    
    def remove_handler(self, handler: EventHandler) -> None:
        """Remove handler from chain."""
        if handler in self.handlers:
            self.handlers.remove(handler)
    
    def handle(self, event: Event) -> HandlerResponse:
        """Handle event through chain."""
        last_response = None
        
        for handler in self.handlers:
            if not handler.can_handle(event):
                continue
            
            response = handler.handle(event)
            last_response = response
            
            if response.result == HandlerResult.FAILURE and self.stop_on_failure:
                break
            
            if response.result == HandlerResult.STOP_PROPAGATION and self.stop_on_stop_propagation:
                break
        
        return last_response or HandlerResponse(
            result=HandlerResult.SUCCESS,
            message="No handlers processed event"
        )
    
    def can_handle(self, event: Event) -> bool:
        """Check if any handler in chain can handle event."""
        return any(handler.can_handle(event) for handler in self.handlers)


class EventRouter:
    """Router that directs events to different handlers based on conditions."""
    
    def __init__(self):
        """Initialize event router."""
        self.routes: List[Dict[str, Any]] = []
        self.default_handler: Optional[EventHandler] = None
    
    def add_route(self, condition: Callable[[Event], bool], handler: EventHandler, priority: int = 0) -> None:
        """
        Add a route to the router.
        
        Args:
            condition: Function that determines if route matches
            handler: Handler to call for matching events
            priority: Route priority (higher = checked first)
        """
        self.routes.append({
            "condition": condition,
            "handler": handler,
            "priority": priority
        })
        
        # Sort routes by priority (descending)
        self.routes.sort(key=lambda r: r["priority"], reverse=True)
    
    def set_default_handler(self, handler: EventHandler) -> None:
        """Set default handler for unmatched events."""
        self.default_handler = handler
    
    def handle(self, event: Event) -> HandlerResponse:
        """Route event to appropriate handler."""
        for route in self.routes:
            if route["condition"](event):
                return route["handler"].handle(event)
        
        if self.default_handler:
            return self.default_handler.handle(event)
        
        return HandlerResponse(
            result=HandlerResult.SUCCESS,
            message="No route matched event and no default handler"
        )
    
    def can_handle(self, event: Event) -> bool:
        """Check if any route can handle event."""
        for route in self.routes:
            if route["condition"](event) and route["handler"].can_handle(event):
                return True
        
        return self.default_handler is not None and self.default_handler.can_handle(event)


# Utility functions for creating common handlers

def create_function_handler(func: Callable[[Event], None]) -> EventHandler:
    """Create a handler from a simple function."""
    def wrapper(event: Event) -> HandlerResponse:
        try:
            func(event)
            return HandlerResponse(result=HandlerResult.SUCCESS)
        except Exception as e:
            return HandlerResponse(
                result=HandlerResult.FAILURE,
                message=f"Function handler error: {e}"
            )
    
    return FunctionEventHandler(wrapper)


def create_logging_handler(handler: EventHandler, log_level: str = "INFO") -> EventHandler:
    """Create a logging wrapper for a handler."""
    return LoggingEventHandler(handler, log_level)


def create_metrics_handler(handler: EventHandler) -> MetricsEventHandler:
    """Create a metrics wrapper for a handler."""
    return MetricsEventHandler(handler)


def create_retry_handler(handler: EventHandler, max_retries: int = 3, retry_delay: float = 1.0) -> EventHandler:
    """Create a retry wrapper for a handler."""
    return RetryEventHandler(handler, max_retries, retry_delay)


def create_weak_handler(target_object: Any, method_name: str) -> WeakReferenceEventHandler:
    """Create a weak reference handler."""
    return WeakReferenceEventHandler(target_object, method_name)
