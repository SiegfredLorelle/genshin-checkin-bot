"""Browser management with framework abstraction layer.

This module provides a unified interface for browser automation,
supporting both Playwright (primary) and Selenium (fallback) frameworks.
"""

from abc import ABC, abstractmethod
from typing import Optional

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


class BrowserManager:
    """Main browser manager with framework selection logic."""

    def __init__(self, framework: str = "playwright"):
        """Initialize with specified framework.

        Args:
            framework: "playwright" (default) or "selenium"
        """
        self.framework = framework
        self._browser_impl: Optional[BrowserManagerInterface] = None

    async def initialize(self) -> BrowserManagerInterface:
        """Initialize the selected browser framework.

        Returns:
            Browser implementation instance

        Raises:
            ImportError: If framework dependencies are not available
            RuntimeError: If framework initialization fails
        """
        try:
            if self.framework == "playwright":
                from .playwright_impl import PlaywrightBrowserManager

                self._browser_impl = PlaywrightBrowserManager()
            elif self.framework == "selenium":
                from .selenium_impl import SeleniumBrowserManager

                self._browser_impl = SeleniumBrowserManager()
            else:
                raise ValueError(f"Unsupported framework: {self.framework}")

            await self._browser_impl.launch()
            logger.info("Browser framework initialized", framework=self.framework)
            return self._browser_impl

        except ImportError as e:
            logger.error(
                "Framework dependencies missing",
                framework=self.framework,
                error=str(e),
            )
            # Auto-fallback to Selenium if Playwright fails
            if self.framework == "playwright":
                logger.info("Attempting fallback to Selenium")
                self.framework = "selenium"
                return await self.initialize()
            raise
        except Exception as e:
            logger.error(
                "Framework initialization failed",
                framework=self.framework,
                error=str(e),
            )
            raise RuntimeError(f"Failed to initialize {self.framework}: {e}")
