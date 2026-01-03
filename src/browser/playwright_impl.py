"""Playwright browser automation implementation.

Primary browser automation framework with superior reliability,
async support, and built-in waiting strategies.
"""

import structlog

from .manager import BrowserManagerInterface

logger = structlog.get_logger(__name__)


class PlaywrightBrowserManager(BrowserManagerInterface):
    """Playwright implementation of browser automation."""

    def __init__(self):
        """Initialize Playwright browser manager."""
        self.browser = None
        self.page = None
        self.context = None

    async def launch(self, headless: bool = True) -> None:
        """Launch Playwright browser instance."""
        try:
            from playwright.async_api import async_playwright

            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=headless)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()

            logger.info("Playwright browser launched successfully", headless=headless)
        except Exception as e:
            logger.error("Failed to launch Playwright browser", error=str(e))
            raise

    async def navigate(self, url: str) -> None:
        """Navigate to specified URL."""
        if not self.page:
            raise RuntimeError("Browser not initialized")

        await self.page.goto(url)
        logger.info("Navigated to URL", url=url)

    async def close(self) -> None:
        """Close browser instance and cleanup resources."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, "playwright"):
                await self.playwright.stop()

            logger.info("Playwright browser closed successfully")
        except Exception as e:
            logger.error("Error closing Playwright browser", error=str(e))

    async def screenshot(self, path: str) -> None:
        """Take screenshot for debugging."""
        if not self.page:
            raise RuntimeError("Browser not initialized")

        await self.page.screenshot(path=path)
        logger.info("Screenshot saved", path=path)

    async def set_cookie(self, cookie: dict) -> None:
        """Set browser cookie."""
        if not self.context:
            raise RuntimeError("Browser not initialized")

        await self.context.add_cookies([cookie])
        logger.debug("Cookie set", name=cookie.get("name"), domain=cookie.get("domain"))

    async def get_cookies(self) -> list:
        """Get current browser cookies."""
        if not self.context:
            raise RuntimeError("Browser not initialized")

        cookies = await self.context.cookies()
        return cookies

    async def find_element(self, selector: str, timeout: int = 10000) -> bool:
        """Find element by CSS selector with timeout."""
        if not self.page:
            raise RuntimeError("Browser not initialized")

        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception:
            return False

    async def find_elements(self, selector: str) -> list:
        """Find all elements matching CSS selector."""
        if not self.page:
            raise RuntimeError("Browser not initialized")

        try:
            elements = await self.page.query_selector_all(selector)
            # Return element information instead of actual elements
            element_info = []
            for i, element in enumerate(elements):
                try:
                    tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
                    text_content = await element.text_content()
                    is_visible = await element.is_visible()

                    element_info.append(
                        {
                            "index": i,
                            "tag_name": tag_name,
                            "text_content": text_content[:100] if text_content else "",
                            "is_visible": is_visible,
                            "selector": selector,
                        }
                    )
                except Exception as e:
                    logger.debug("Error getting element info", error=str(e))
                    continue

            return element_info
        except Exception as e:
            logger.debug("Error finding elements", selector=selector, error=str(e))
            return []

    async def wait_for_element(self, selector: str, timeout: int = 10000) -> bool:
        """Wait for element to be present and visible."""
        if not self.page:
            raise RuntimeError("Browser not initialized")

        try:
            await self.page.wait_for_selector(
                selector, timeout=timeout, state="visible"
            )
            return True
        except Exception:
            return False
