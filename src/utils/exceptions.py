"""Custom exception classes for automation workflow.

Provides specific exception types for different automation failure scenarios
with context-rich error reporting while maintaining security.
"""


class AutomationError(Exception):
    """Base exception for automation failures."""

    def __init__(self, message: str, context: dict = None):
        """Initialize automation error.

        Args:
            message: Error description
            context: Additional context for debugging (secrets will be redacted)
        """
        super().__init__(message)
        self.context = context or {}


class AuthenticationError(AutomationError):
    """Authentication flow failure."""

    pass


class BrowserError(AutomationError):
    """Browser operation failure."""

    pass


class DetectionError(AutomationError):
    """Element detection failure."""

    pass


class ConfigurationError(AutomationError):
    """Configuration validation failure."""

    pass


class StateManagementError(AutomationError):
    """State management operation failure."""

    pass
