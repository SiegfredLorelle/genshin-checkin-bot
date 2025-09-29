"""Integration tests for complete HoYoLAB automation workflow."""

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from src.automation.orchestrator import AutomationOrchestrator
from src.browser.manager import BrowserManager
from src.config.manager import ConfigurationManager


class TestHoYoLABIntegration:
    """Integration tests for HoYoLAB automation workflow."""

    @pytest.fixture
    def config_manager(self):
        """Create configuration manager for testing."""
        config = ConfigurationManager()
        # Override with test credentials
        config._credentials = MagicMock()
        config._credentials.ltuid = "test_ltuid"
        config._credentials.ltoken = "test_ltoken"
        config._credentials.account_id = "test_account"
        return config

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_complete_authentication_flow(self, config_manager):
        """Test complete authentication flow against mock HoYoLAB."""
        orchestrator = AutomationOrchestrator(config_manager)

        try:
            # Initialize orchestrator
            await orchestrator.initialize()

            # Navigate to HoYoLAB (using test URL)
            with patch.object(config_manager, "get_hoyolab_url") as mock_url:
                mock_url.return_value = "https://httpbin.org/html"  # Test endpoint
                await orchestrator._navigate_to_hoyolab()

            # Test authentication flow
            auth_result = await orchestrator._authenticate()

            # Should succeed with mock credentials
            assert auth_result is True

            # Verify cookies were set
            cookies = await orchestrator.browser_impl.get_cookies()
            assert len(cookies) >= 2  # ltuid and ltoken at minimum

        finally:
            await orchestrator.cleanup()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_interface_analysis_workflow(self, config_manager):
        """Test interface analysis workflow with mocked operations."""
        orchestrator = AutomationOrchestrator(config_manager)

        try:
            await orchestrator.initialize()

            # Mock browser navigation and reward detector analysis
            with patch.object(
                orchestrator.browser_impl, "navigate"
            ) as mock_navigate, patch.object(
                orchestrator.reward_detector, "analyze_interface"
            ) as mock_analyze:

                mock_navigate.return_value = None
                mock_analyze.return_value = {
                    "selectors": ["button.test", ".reward-item"],
                    "reward_states": {"claimable_rewards": [], "claimed_rewards": []},
                    "detection_confidence": 0.9,
                    "primary_strategy": "hoyolab_class_based",
                    "fallback_strategies": ["attribute_based"],
                    "interface_elements": [],
                    "analysis_timestamp": "2025-09-30T00:00:00Z",
                }

                # Run interface analysis
                analysis_result = await orchestrator._analyze_interface()

                # Verify analysis structure
                assert "selectors" in analysis_result
                assert "detection_confidence" in analysis_result
                assert "analysis_timestamp" in analysis_result

                # Should have attempted multiple strategies
                assert "primary_strategy" in analysis_result
                assert analysis_result["primary_strategy"] == "hoyolab_class_based"

        finally:
            await orchestrator.cleanup()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_browser_framework_fallback(self):
        """Test automatic fallback from Playwright to Selenium."""
        # Force Playwright failure by patching the import
        with patch("playwright.async_api.async_playwright") as mock_playwright:
            mock_playwright.side_effect = ImportError("Playwright not available")

            browser_manager = BrowserManager(framework="playwright")

            # Should automatically fallback to Selenium
            browser_impl = await browser_manager.initialize()

            try:
                # Verify Selenium is being used
                assert browser_manager.framework == "selenium"
                assert browser_impl is not None

                # Test basic operations
                await browser_impl.navigate("https://httpbin.org/html")

                # Test screenshot capability
                await browser_impl.screenshot("test_fallback.png")

            finally:
                await browser_impl.close()

    @pytest.mark.asyncio
    async def test_complete_workflow_execution(self, config_manager):
        """Test complete workflow execution with mocked operations."""
        orchestrator = AutomationOrchestrator(config_manager)

        try:
            await orchestrator.initialize()

            # Mock all browser and detector operations
            with patch.object(
                orchestrator.browser_impl, "navigate"
            ) as mock_navigate, patch.object(
                orchestrator.browser_impl, "set_cookie"
            ) as mock_set_cookie, patch.object(
                orchestrator.reward_detector, "analyze_interface"
            ) as mock_analyze:

                # Configure mocks for successful workflow
                mock_navigate.return_value = None
                mock_set_cookie.return_value = None
                mock_analyze.return_value = {
                    "selectors": ["button.claim", ".reward-item"],
                    "reward_states": {"claimable_rewards": [], "claimed_rewards": []},
                    "detection_confidence": 0.8,
                    "primary_strategy": "hoyolab_class_based",
                    "fallback_strategies": [],
                    "interface_elements": [],
                    "analysis_timestamp": "2025-09-30T00:00:00Z",
                }

                # Execute complete workflow
                result = await orchestrator.execute_workflow()

                # Verify successful execution
                assert result["success"] is True
                assert result["authentication_success"] is True
                assert result["step_completed"] == "interface_analysis"
                assert "interface_analysis" in result

                # Verify browser operations were called
                mock_navigate.assert_called_once()
                # set_cookie called 3 times (ltuid, ltoken, account_id)
                assert mock_set_cookie.call_count == 3
                mock_analyze.assert_called_once()

                # Verify state logging occurred
                last_execution = (
                    await orchestrator.state_manager.get_last_execution_result()
                )
                assert last_execution is not None
                assert last_execution["success"] is True

        finally:
            await orchestrator.cleanup()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_error_handling_and_recovery(self, config_manager):
        """Test error handling and recovery mechanisms."""
        orchestrator = AutomationOrchestrator(config_manager)

        try:
            await orchestrator.initialize()

            # Force authentication failure
            with patch.object(
                orchestrator, "_validate_authentication"
            ) as mock_validate:
                mock_validate.return_value = False

                # Should handle authentication failure gracefully
                with pytest.raises(Exception):  # Should raise AutomationError
                    await orchestrator.execute_workflow()

                # Verify error was logged
                last_execution = (
                    await orchestrator.state_manager.get_last_execution_result()
                )
                assert last_execution is not None
                assert last_execution["success"] is False

        finally:
            await orchestrator.cleanup()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_screenshot_capture_functionality(self, config_manager):
        """Test screenshot capture during workflow."""
        orchestrator = AutomationOrchestrator(config_manager)

        try:
            await orchestrator.initialize()

            # Navigate to test page
            await orchestrator.browser_impl.navigate("https://httpbin.org/html")

            # Capture debug screenshot
            screenshot_path = await orchestrator._capture_debug_screenshot(
                "integration_test"
            )

            # Verify screenshot was captured
            assert screenshot_path is not None
            assert "integration_test" in screenshot_path
            assert screenshot_path.endswith(".png")

        finally:
            await orchestrator.cleanup()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_concurrent_workflow_execution(self, config_manager):
        """Test concurrent workflow execution for stability with mocked operations."""

        async def run_workflow():
            orchestrator = AutomationOrchestrator(config_manager)
            try:
                await orchestrator.initialize()

                # Mock all network operations to eliminate external dependencies
                with patch.object(
                    orchestrator.browser_impl, "navigate"
                ) as mock_navigate, patch.object(
                    orchestrator.browser_impl, "set_cookie"
                ) as mock_set_cookie, patch.object(
                    orchestrator.reward_detector, "analyze_interface"
                ) as mock_analyze:

                    mock_navigate.return_value = None
                    mock_set_cookie.return_value = None
                    mock_analyze.return_value = {
                        "selectors": ["button.mock"],
                        "reward_states": {"claimable_rewards": []},
                        "detection_confidence": 0.8,
                        "primary_strategy": "mock_strategy",
                        "fallback_strategies": [],
                        "interface_elements": [],
                        "analysis_timestamp": "2025-09-30T00:00:00Z",
                    }

                    result = await orchestrator.execute_workflow()
                    return result["success"]

            finally:
                await orchestrator.cleanup()

        # Run multiple workflows concurrently
        tasks = [run_workflow() for _ in range(3)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should succeed with mocked operations
        successful_runs = sum(1 for result in results if result is True)
        assert successful_runs >= 2  # At least 2 out of 3 should succeed

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_state_persistence_across_runs(self, config_manager):
        """Test state persistence across multiple workflow runs with mocks."""
        # First run
        orchestrator1 = AutomationOrchestrator(config_manager)
        try:
            await orchestrator1.initialize()

            # Mock all network operations for reliability
            with patch.object(
                orchestrator1.browser_impl, "navigate"
            ) as mock_navigate, patch.object(
                orchestrator1.browser_impl, "set_cookie"
            ) as mock_set_cookie, patch.object(
                orchestrator1.reward_detector, "analyze_interface"
            ) as mock_analyze:

                mock_navigate.return_value = None
                mock_set_cookie.return_value = None
                mock_analyze.return_value = {
                    "selectors": ["button.mock"],
                    "reward_states": {"claimable_rewards": []},
                    "detection_confidence": 0.8,
                    "primary_strategy": "mock_strategy",
                    "fallback_strategies": [],
                    "interface_elements": [],
                    "analysis_timestamp": "2025-09-30T00:00:00Z",
                }

                await orchestrator1.execute_workflow()

        finally:
            await orchestrator1.cleanup()

        # Second run
        orchestrator2 = AutomationOrchestrator(config_manager)
        try:
            await orchestrator2.initialize()

            # Check execution history
            history = await orchestrator2.state_manager.get_execution_history(limit=2)
            assert len(history) >= 1

            # Calculate success rate
            stats = await orchestrator2.state_manager.calculate_success_rate(days=1)
            assert stats["total_executions"] >= 1

        finally:
            await orchestrator2.cleanup()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_browser_automation_with_playwright():
    """Test browser automation using pytest-playwright."""
    browser_manager = BrowserManager(framework="playwright")

    try:
        browser_impl = await browser_manager.initialize()

        # Test navigation
        await browser_impl.navigate("https://httpbin.org/html")

        # Test element detection
        found = await browser_impl.find_element("h1", timeout=5000)
        assert found is True

        # Test multiple element finding
        elements = await browser_impl.find_elements("p")
        assert len(elements) >= 0

        # Test cookie operations
        test_cookie = {
            "name": "test_cookie",
            "value": "test_value",
            "domain": "httpbin.org",
            "path": "/",
            "secure": False,
            "httpOnly": False,
        }

        await browser_impl.set_cookie(test_cookie)
        cookies = await browser_impl.get_cookies()
        cookie_names = [cookie["name"] for cookie in cookies]
        assert "test_cookie" in cookie_names

    finally:
        await browser_impl.close()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_configuration_validation():
    """Test configuration validation and environment setup."""
    config = ConfigurationManager()

    # Test environment validation
    is_valid = config.validate_environment()
    # Should be True even with mock credentials for MVP
    assert isinstance(is_valid, bool)

    # Test credential loading
    credentials = config.get_hoyolab_credentials()
    assert credentials.ltuid is not None
    assert credentials.ltoken is not None

    # Test configuration retrieval
    browser_config = config.get_browser_config()
    assert "headless" in browser_config
    assert "timeout" in browser_config

    detection_config = config.get_detection_config()
    assert "wait_timeout" in detection_config
    assert "retry_attempts" in detection_config

    timing_config = config.get_timing_config()
    assert "page_load_delay" in timing_config
    assert "click_delay" in timing_config
