"""Structured logging configuration with secret redaction.

Provides JSON-formatted logging suitable for both development debugging
and production operation with comprehensive secret redaction.
"""

import logging
import logging.handlers
import os
import re
import sys
from pathlib import Path
from typing import Any, List

import structlog


def redact_secrets(logger, method_name, event_dict):
    """Redact sensitive information from log entries."""
    sensitive_patterns = [
        (r'(ltuid["\']?\s*[:=]\s*["\']?)([^"\'&\s]+)', r"\1***REDACTED***"),
        (r'(ltoken["\']?\s*[:=]\s*["\']?)([^"\'&\s]+)', r"\1***REDACTED***"),
        (r'(password["\']?\s*[:=]\s*["\']?)([^"\'&\s]+)', r"\1***REDACTED***"),
        (r'(token["\']?\s*[:=]\s*["\']?)([^"\'&\s]+)', r"\1***REDACTED***"),
        (r'(cookie["\']?\s*[:=]\s*["\']?)([^"\'&\s]+)', r"\1***REDACTED***"),
        (r'(authorization["\']?\s*[:=]\s*["\']?)([^"\'&\s]+)', r"\1***REDACTED***"),
    ]

    # Redact from main event message
    if "event" in event_dict:
        message = str(event_dict["event"])
        for pattern, replacement in sensitive_patterns:
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
        event_dict["event"] = message

    # Redact from all other fields
    for key, value in event_dict.items():
        if isinstance(value, str):
            for pattern, replacement in sensitive_patterns:
                value = re.sub(pattern, replacement, value, flags=re.IGNORECASE)
            event_dict[key] = value

    return event_dict


def configure_logging(
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_dir: str = "logs",
    development_mode: bool = False,
) -> None:
    """Configure structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to files
        log_dir: Directory for log files
        development_mode: Enable development-friendly formatting
    """
    # Ensure log directory exists
    if log_to_file:
        Path(log_dir).mkdir(exist_ok=True)

    # Configure structlog processors
    processors: List[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="ISO", utc=True),
        redact_secrets,  # Add secret redaction
    ]

    # Add development-friendly formatting or JSON for production
    if development_mode:
        processors.extend(
            [
                structlog.dev.ConsoleRenderer(colors=True),
            ]
        )
    else:
        processors.extend(
            [
                structlog.processors.dict_tracebacks,
                structlog.processors.JSONRenderer(),
            ]
        )

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, log_level.upper())),
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Add file handlers if enabled
    if log_to_file:
        # Main application log with rotation
        app_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, "application.log"),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        app_handler.setLevel(getattr(logging, log_level.upper()))

        # Error log for warnings and above
        error_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, "errors.log"),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=3,
        )
        error_handler.setLevel(logging.WARNING)

        # Add handlers to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(app_handler)
        root_logger.addHandler(error_handler)


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a configured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


# Auto-configure logging on import
def _auto_configure():
    """Automatically configure logging based on environment."""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    development_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"

    configure_logging(
        log_level=log_level,
        development_mode=development_mode,
    )


# Initialize logging when module is imported
_auto_configure()
