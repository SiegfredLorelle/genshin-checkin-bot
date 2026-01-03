"""Unit tests for browser manager and framework abstraction."""

from unittest.mock import AsyncMock, patch

import pytest

from src.browser.manager import BrowserManager, BrowserManagerInterface


class TestBrowserManager:
    """Test cases for BrowserManager class."""

    def test_init_default_framework(self):
        """Test BrowserManager initializes with default playwright framework."""
        manager = BrowserManager()
        assert manager.framework == "playwright"
        assert manager._browser_impl is None

    def test_init_custom_framework(self):
        """Test BrowserManager initializes with custom framework."""
        manager = BrowserManager(framework="selenium")
        assert manager.framework == "selenium"
        assert manager._browser_impl is None

    @pytest.mark.asyncio
    async def test_initialize_playwright_success(self):
        """Test successful Playwright initialization."""
        with patch(
            "src.browser.playwright_impl.PlaywrightBrowserManager"
        ) as mock_playwright:
            mock_impl = AsyncMock()
            mock_playwright.return_value = mock_impl

            manager = BrowserManager(framework="playwright")
            result = await manager.initialize()

            mock_playwright.assert_called_once()
            mock_impl.launch.assert_called_once()
            assert result == mock_impl
            assert manager._browser_impl == mock_impl

    @pytest.mark.asyncio
    async def test_initialize_selenium_success(self):
        """Test successful Selenium initialization."""
        with patch("src.browser.selenium_impl.SeleniumBrowserManager") as mock_selenium:
            mock_impl = AsyncMock()
            mock_selenium.return_value = mock_impl

            manager = BrowserManager(framework="selenium")
            result = await manager.initialize()

            mock_selenium.assert_called_once()
            mock_impl.launch.assert_called_once()
            assert result == mock_impl

    @pytest.mark.asyncio
    async def test_initialize_unsupported_framework(self):
        """Test initialization with unsupported framework raises RuntimeError."""
        manager = BrowserManager(framework="unsupported")

        with pytest.raises(RuntimeError, match="Failed to initialize unsupported"):
            await manager.initialize()

    @pytest.mark.asyncio
    async def test_initialize_playwright_fallback_to_selenium(self):
        """Test automatic fallback from Playwright to Selenium on ImportError."""
        with (
            patch(
                "src.browser.playwright_impl.PlaywrightBrowserManager"
            ) as mock_playwright,
            patch("src.browser.selenium_impl.SeleniumBrowserManager") as mock_selenium,
        ):
            # Playwright fails with ImportError
            mock_playwright.side_effect = ImportError("Playwright not available")

            # Selenium succeeds
            mock_selenium_impl = AsyncMock()
            mock_selenium.return_value = mock_selenium_impl

            manager = BrowserManager(framework="playwright")
            result = await manager.initialize()

            # Should have tried Playwright first, then fallen back to Selenium
            mock_playwright.assert_called_once()
            mock_selenium.assert_called_once()
            mock_selenium_impl.launch.assert_called_once()

            # Framework should be updated to selenium
            assert manager.framework == "selenium"
            assert result == mock_selenium_impl

    @pytest.mark.asyncio
    async def test_initialize_runtime_error(self):
        """Test RuntimeError on framework initialization failure."""
        with patch(
            "src.browser.playwright_impl.PlaywrightBrowserManager"
        ) as mock_playwright:
            mock_impl = AsyncMock()
            mock_impl.launch.side_effect = Exception("Launch failed")
            mock_playwright.return_value = mock_impl

            manager = BrowserManager(framework="playwright")

            with pytest.raises(RuntimeError, match="Failed to initialize playwright"):
                await manager.initialize()


class MockBrowserImplementation(BrowserManagerInterface):
    """Mock implementation for testing."""

    def __init__(self):
        self.launched = False
        self.closed = False
        self.headless = True
        self.current_url = None
        self.screenshots = []
        self.cookies = []

    async def launch(self, headless: bool = True) -> None:
        self.launched = True
        self.headless = headless

    async def navigate(self, url: str) -> None:
        if not self.launched:
            raise RuntimeError("Browser not initialized")
        self.current_url = url

    async def close(self) -> None:
        self.closed = True

    async def screenshot(self, path: str) -> None:
        if not self.launched:
            raise RuntimeError("Browser not initialized")
        self.screenshots.append(path)

    async def set_cookie(self, cookie: dict) -> None:
        """Set browser cookie."""
        self.cookies.append(cookie)

    async def get_cookies(self) -> list:
        """Get current browser cookies."""
        return self.cookies.copy()

    async def find_element(self, selector: str, timeout: int = 10000) -> bool:
        """Find element by CSS selector with timeout."""
        return True  # Mock always finds element

    async def find_elements(self, selector: str) -> list:
        """Find all elements matching CSS selector."""
        return [{"selector": selector}]  # Mock returns one element

    async def wait_for_element(self, selector: str, timeout: int = 10000) -> bool:
        """Wait for element to be present and visible."""
        return True  # Mock always succeeds

    async def click_element(self, selector: str, timeout: int = 10000) -> bool:
        """Click element by CSS selector."""
        if not self.launched:
            raise RuntimeError("Browser not initialized")
        return True  # Mock always succeeds


class TestBrowserManagerInterface:
    """Test cases for the browser manager interface."""

    @pytest.mark.asyncio
    async def test_interface_implementation(self):
        """Test that the interface can be implemented correctly."""
        browser = MockBrowserImplementation()

        # Test launch
        await browser.launch(headless=False)
        assert browser.launched is True
        assert browser.headless is False

        # Test navigation
        await browser.navigate("https://example.com")
        assert browser.current_url == "https://example.com"

        # Test screenshot
        await browser.screenshot("/tmp/test.png")
        assert "/tmp/test.png" in browser.screenshots

        # Test close
        await browser.close()
        assert browser.closed is True

    @pytest.mark.asyncio
    async def test_interface_requires_launch_before_navigate(self):
        """Test that navigate requires launch to be called first."""
        browser = MockBrowserImplementation()

        with pytest.raises(RuntimeError, match="Browser not initialized"):
            await browser.navigate("https://example.com")

    @pytest.mark.asyncio
    async def test_interface_requires_launch_before_screenshot(self):
        """Test that screenshot requires launch to be called first."""
        browser = MockBrowserImplementation()

        with pytest.raises(RuntimeError, match="Browser not initialized"):
            await browser.screenshot("/tmp/test.png")
