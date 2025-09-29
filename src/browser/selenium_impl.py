"""Selenium WebDriver browser automation implementation.

Fallback browser automation framework for platform compatibility
and widely documented usage patterns.
"""

import structlog

from .manager import BrowserManagerInterface

logger = structlog.get_logger(__name__)


class SeleniumBrowserManager(BrowserManagerInterface):
    """Selenium WebDriver implementation of browser automation."""

    def __init__(self):
        """Initialize Selenium browser manager."""
        self.driver = None

    async def launch(self, headless: bool = True) -> None:
        """Launch Selenium WebDriver instance."""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options

            options = Options()
            if headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            self.driver = webdriver.Chrome(options=options)
            logger.info("Selenium WebDriver launched successfully", headless=headless)
        except Exception as e:
            logger.error("Failed to launch Selenium WebDriver", error=str(e))
            raise

    async def navigate(self, url: str) -> None:
        """Navigate to specified URL."""
        if not self.driver:
            raise RuntimeError("Browser not initialized")

        self.driver.get(url)
        logger.info("Navigated to URL", url=url)

    async def close(self) -> None:
        """Close browser instance and cleanup resources."""
        try:
            if self.driver:
                self.driver.quit()
            logger.info("Selenium WebDriver closed successfully")
        except Exception as e:
            logger.error("Error closing Selenium WebDriver", error=str(e))

    async def screenshot(self, path: str) -> None:
        """Take screenshot for debugging."""
        if not self.driver:
            raise RuntimeError("Browser not initialized")

        self.driver.save_screenshot(path)
        logger.info("Screenshot saved", path=path)

    async def set_cookie(self, cookie: dict) -> None:
        """Set browser cookie."""
        if not self.driver:
            raise RuntimeError("Browser not initialized")

        # Convert cookie format for Selenium
        selenium_cookie = {
            "name": cookie["name"],
            "value": cookie["value"],
            "domain": cookie["domain"],
            "path": cookie.get("path", "/"),
            "secure": cookie.get("secure", False),
        }

        self.driver.add_cookie(selenium_cookie)
        logger.debug("Cookie set", name=cookie["name"], domain=cookie["domain"])

    async def get_cookies(self) -> list:
        """Get current browser cookies."""
        if not self.driver:
            raise RuntimeError("Browser not initialized")

        cookies = self.driver.get_cookies()
        return cookies

    async def find_element(self, selector: str, timeout: int = 10000) -> bool:
        """Find element by CSS selector with timeout."""
        if not self.driver:
            raise RuntimeError("Browser not initialized")

        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.support.ui import WebDriverWait

            wait = WebDriverWait(self.driver, timeout / 1000.0)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            return True
        except Exception:
            return False

    async def find_elements(self, selector: str) -> list:
        """Find all elements matching CSS selector."""
        if not self.driver:
            raise RuntimeError("Browser not initialized")

        try:
            from selenium.webdriver.common.by import By

            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            element_info = []

            for i, element in enumerate(elements):
                try:
                    element_info.append(
                        {
                            "index": i,
                            "tag_name": element.tag_name.lower(),
                            "text_content": element.text[:100] if element.text else "",
                            "is_visible": element.is_displayed(),
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
        if not self.driver:
            raise RuntimeError("Browser not initialized")

        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.support.ui import WebDriverWait

            wait = WebDriverWait(self.driver, timeout / 1000.0)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
            return True
        except Exception:
            return False
