"""Configuration Manager for centralized application configuration.

Provides secure credential access, environment variable management,
and configuration validation for automation components.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

import structlog
from decouple import config

from ..utils.exceptions import ConfigurationError

logger = structlog.get_logger(__name__)


@dataclass
class HoYoLABCredentials:
    """HoYoLAB authentication credentials for username/password login."""

    username: str
    password: str


class ConfigurationManager:
    """Centralized configuration management with secure credential access."""

    def __init__(self):
        """Initialize configuration manager."""
        self._credentials: Optional[HoYoLABCredentials] = None
        self._config_cache: Dict[str, Any] = {}

    def get_hoyolab_url(self) -> str:
        """Get HoYoLAB URL for automation.

        Returns:
            HoYoLAB login URL
        """
        return config(
            "CHECKIN_URL",
            default="https://act.hoyolab.com/ys/event/signin-sea-v3/index.html",
        )

    def get_hoyolab_credentials(self) -> HoYoLABCredentials:
        """Get HoYoLAB authentication credentials.

        Returns:
            HoYoLAB credentials for authentication

        Raises:
            ConfigurationError: If required credentials are missing
        """
        if self._credentials is None:
            try:
                # Load username/password credentials
                username = config("HOYOLAB_USERNAME", default=None)
                password = config("HOYOLAB_PASSWORD", default=None)

                # Validate credentials
                if not username or not password:
                    raise ConfigurationError(
                        "HOYOLAB_USERNAME and HOYOLAB_PASSWORD are required. "
                        "Please set these environment variables."
                    )

                self._credentials = HoYoLABCredentials(
                    username=username,
                    password=password,
                )

                logger.info(
                    "HoYoLAB credentials loaded successfully",
                    has_username=bool(username),
                    has_password=bool(password),
                )

            except Exception as e:
                raise ConfigurationError(f"Failed to load HoYoLAB credentials: {e}")

        return self._credentials

    def get_browser_config(self) -> Dict[str, Any]:
        """Get browser configuration settings.

        Returns:
            Browser configuration dictionary
        """
        return {
            "headless": config("BROWSER_HEADLESS", default=True, cast=bool),
            "timeout": config("BROWSER_TIMEOUT", default=30000, cast=int),
            "user_agent": config(
                "BROWSER_USER_AGENT",
                default=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/119.0.0.0 Safari/537.36"
                ),
            ),
            "viewport": {
                "width": config("BROWSER_WIDTH", default=1920, cast=int),
                "height": config("BROWSER_HEIGHT", default=1080, cast=int),
            },
        }

    def get_detection_config(self) -> Dict[str, Any]:
        """Get reward detection configuration.

        Returns:
            Detection configuration dictionary
        """
        return {
            "wait_timeout": config("DETECTION_WAIT_TIMEOUT", default=10000, cast=int),
            "retry_attempts": config("DETECTION_RETRY_ATTEMPTS", default=3, cast=int),
            "screenshot_on_failure": config(
                "DETECTION_SCREENSHOT", default=True, cast=bool
            ),
            "primary_selectors": [
                config("DETECTION_PRIMARY_SELECTOR", default=".signin-btn"),
                config(
                    "DETECTION_FALLBACK_SELECTOR",
                    default="[data-testid='signin-button']",
                ),
                config(
                    "DETECTION_GENERIC_SELECTOR", default="button:contains('Sign in')"
                ),
            ],
        }

    def get_timing_config(self) -> Dict[str, Any]:
        """Get anti-bot timing configuration.

        Returns:
            Timing configuration for human-like delays
        """
        return {
            "page_load_delay": config("TIMING_PAGE_LOAD", default=2000, cast=int),
            "click_delay": config("TIMING_CLICK_DELAY", default=1000, cast=int),
            "typing_delay": config("TIMING_TYPING_DELAY", default=100, cast=int),
            "navigation_delay": config("TIMING_NAVIGATION", default=3000, cast=int),
            "random_variance": config("TIMING_VARIANCE", default=0.3, cast=float),
        }

    def redact_secrets(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive information from data for safe logging.

        Args:
            data: Data dictionary that may contain secrets

        Returns:
            Data with secrets redacted
        """
        redacted = data.copy()

        # Secret field patterns to redact
        secret_patterns = [
            "password",
            "token",
            "secret",
            "key",
            "ltuid",
            "ltoken",
            "credential",
            "auth",
            "session",
            "cookie",
        ]

        for key in list(redacted.keys()):
            if any(pattern in key.lower() for pattern in secret_patterns):
                if isinstance(redacted[key], str) and len(redacted[key]) > 4:
                    redacted[key] = redacted[key][:4] + "***REDACTED***"
                else:
                    redacted[key] = "***REDACTED***"

        return redacted

    def validate_environment(self) -> bool:
        """Validate that required environment variables are present.

        Returns:
            True if environment is valid for automation
        """
        try:
            # Check critical configurations
            self.get_hoyolab_credentials()
            self.get_browser_config()
            self.get_detection_config()

            logger.info("Environment validation successful")
            return True

        except Exception as e:
            logger.error("Environment validation failed", error=str(e))
            return False
