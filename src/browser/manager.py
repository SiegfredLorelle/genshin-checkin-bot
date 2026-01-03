"""Browser management for Playwright automation.

This module provides a unified interface for Playwright browser automation.
"""

from abc import ABC, abstractmethod

import structlog

logger = structlog.get_logger(__name__)


class BrowserManagerInterface(ABC):
    """Abstract base class for browser automation frameworks."""

    @abstractmethod
    async def launch(self, headless: bool = True) -> None:
        """Launch browser instance."""
        pass

    @abstractmethod
    async def navigate(self, url: str) -> None:
        """Navigate to specified URL."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close browser instance and cleanup resources."""
        pass

    @abstractmethod
    async def screenshot(self, path: str) -> None:
        """Take screenshot for debugging."""
        pass

    @abstractmethod
    async def set_cookie(self, cookie: dict) -> None:
        """Set browser cookie."""
        pass

    @abstractmethod
    async def get_cookies(self) -> list:
        """Get current browser cookies."""
        pass

    @abstractmethod
    async def find_element(self, selector: str, timeout: int = 10000) -> bool:
        """Find element by CSS selector with timeout.

        Args:
            selector: CSS selector string
            timeout: Timeout in milliseconds

        Returns:
            True if element found, False otherwise
        """
        pass

    @abstractmethod
    async def find_elements(self, selector: str) -> list:
        """Find all elements matching CSS selector.

        Args:
            selector: CSS selector string

        Returns:
            List of element information
        """
        pass

    @abstractmethod
    async def wait_for_element(self, selector: str, timeout: int = 10000) -> bool:
        """Wait for element to be present and visible.

        Args:
            selector: CSS selector string
            timeout: Timeout in milliseconds

        Returns:
            True if element found within timeout, False otherwise
        """
        pass

    @abstractmethod
    async def click_element(self, selector: str, timeout: int = 10000) -> bool:
        """Click element by CSS selector.

        Args:
            selector: CSS selector string
            timeout: Timeout in milliseconds

        Returns:
            True if element was clicked successfully, False otherwise
        """
        pass


class BrowserManager:
    """Main browser manager for Playwright automation."""

    def __init__(self, headless: bool = True):
        """Initialize Playwright browser manager.

        Args:
            headless: Whether to run browser in headless mode
        """
        self.headless = headless
        self._browser_impl: BrowserManagerInterface | None = None

    async def initialize(self) -> BrowserManagerInterface:
        """Initialize Playwright browser framework.

        Returns:
            Browser implementation instance

        Raises:
            ImportError: If Playwright dependencies are not available
            RuntimeError: If browser initialization fails
        """
        try:
            from .playwright_impl import PlaywrightBrowserManager

            self._browser_impl = PlaywrightBrowserManager()
            await self._browser_impl.launch(headless=self.headless)
            logger.info("Playwright browser initialized successfully")
            return self._browser_impl

        except ImportError as e:
            logger.error(
                "Playwright dependencies missing",
                error=str(e),
            )
            raise ImportError(
                "Playwright is not installed. Run: uv sync or "
                "pip install playwright && playwright install chromium"
            ) from e
        except Exception as e:
            logger.error(
                "Playwright initialization failed",
                error=str(e),
            )
            raise RuntimeError(f"Failed to initialize Playwright: {e}") from e
