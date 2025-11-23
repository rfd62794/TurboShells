"""
Error handling utilities for TurboShells game.

This module provides common error handling patterns and utilities
for a portfolio project focused on clean, maintainable code.
"""

import logging
from typing import Optional, Callable, Any, TypeVar, Union
from functools import wraps

from .logging_config import log_exception_with_context

T = TypeVar('T')


class TurboShellsError(Exception):
    """Base exception for TurboShells game."""
    pass


class GameError(TurboShellsError):
    """Raised for general game logic errors."""
    pass


class SaveError(TurboShellsError):
    """Raised when save/load operations fail."""
    pass


class UIError(TurboShellsError):
    """Raised for UI-related errors."""
    pass


class GeneticsError(TurboShellsError):
    """Raised for genetics calculation errors."""
    pass


def safe_execute(
    func: Callable[..., T],
    default: T = None,
    error_context: str = "",
    log_errors: bool = True
) -> Callable[..., T]:
    """
    Decorator for safe function execution with error handling.
    
    Args:
        func: Function to execute safely
        default: Default value to return on error
        error_context: Context description for error logging
        log_errors: Whether to log errors
        
    Returns:
        Function result or default value on error
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if log_errors:
                log_exception_with_context(e, error_context or func.__name__)
            return default
    return wrapper


def handle_game_error(
    error: Exception,
    context: str = "",
    fallback_action: Optional[Callable] = None
) -> None:
    """
    Handle game errors with appropriate fallback actions.
    
    Args:
        error: The exception that occurred
        context: Context where error occurred
        fallback_action: Optional fallback function to execute
    """
    log_exception_with_context(error, context)
    
    # Execute fallback action if provided
    if fallback_action:
        try:
            fallback_action()
        except Exception as fallback_error:
            log_exception_with_context(
                fallback_error, 
                f"fallback action for {context}"
            )


class ErrorHandler:
    """
    Context manager for handling errors in specific operations.
    """
    
    def __init__(
        self, 
        operation_name: str,
        fallback_result: Any = None,
        raise_on_error: bool = False
    ):
        """Initialize error handler.
        
        Args:
            operation_name: Name of the operation being performed
            fallback_result: Result to return on error
            raise_on_error: Whether to re-raise exceptions
        """
        self.operation_name = operation_name
        self.fallback_result = fallback_result
        self.raise_on_error = raise_on_error
        self.error_occurred = False
        self.exception = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error_occurred = True
            self.exception = exc_val
            
            if self.raise_on_error:
                return False  # Re-raise the exception
            
            # Log the error but don't re-raise
            log_exception_with_context(exc_val, self.operation_name)
            return True  # Suppress the exception
        
        return False
    
    def get_result(self, success_result: Any = None) -> Any:
        """Get the operation result, fallback on error."""
        if self.error_occurred:
            return self.fallback_result
        return success_result


def validate_game_state(state: dict, required_keys: list) -> None:
    """
    Validate that game state has required keys.
    
    Args:
        state: Game state dictionary
        required_keys: List of required keys
        
    Raises:
        GameError: If validation fails
    """
    missing_keys = [key for key in required_keys if key not in state]
    if missing_keys:
        raise GameError(f"Missing required state keys: {missing_keys}")


def safe_file_operation(
    operation: str,
    file_path: str,
    default_result: Any = None
):
    """
    Context manager for safe file operations.
    
    Args:
        operation: Description of the file operation
        file_path: Path to the file
        default_result: Default result on error
    """
    return ErrorHandler(
        f"file operation: {operation} on {file_path}",
        fallback_result=default_result
    )


# Common error handling patterns for game development
def with_error_handling(
    default_return: Any = None,
    log_error: bool = True,
    error_type: type = Exception
):
    """
    Decorator for adding standard error handling to functions.
    
    Args:
        default_return: Value to return on error
        log_error: Whether to log errors
        error_type: Exception type to catch
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except error_type as e:
                if log_error:
                    log_exception_with_context(e, func.__name__)
                return default_return
        return wrapper
    return decorator


# Example usage patterns for portfolio project
def example_usage():
    """Examples of how to use the error handling utilities."""
    
    # Safe execution decorator
    @safe_execute(default={"status": "error"})
    def risky_calculation():
        # Some risky operation
        pass
    
    # Context manager error handling
    with ErrorHandler("loading save file", fallback_result={}):
        # Load save file operation
        pass
    
    # Game state validation
    try:
        validate_game_state({"money": 100}, ["money", "turtles"])
    except GameError as e:
        print(f"Validation failed: {e}")
