"""Unit tests for AutomationOrchestrator workflow logic."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.automation.orchestrator import AutomationOrchestrator
from src.utils.exceptions import AutomationError


class TestAutomationOrchestrator:
    """Test cases for AutomationOrchestrator class."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance for testing."""
        with patch("src.automation.orchestrator.ConfigurationManager") as mock_config:
            mock_config.return_value.get_hoyolab_url.return_value = (
                "https://hoyolab.com"
            )
            mock_config.return_value.get_hoyolab_credentials.return_value = MagicMock(
                ltuid="test_ltuid", ltoken="test_ltoken", account_id="test_account"
            )

            orchestrator = AutomationOrchestrator()
            return orchestrator

    @pytest.mark.asyncio
    async def test_initialization_success(self, orchestrator):
        """Test successful orchestrator initialization."""
        with patch.object(
            orchestrator.browser_manager, "initialize", new_callable=AsyncMock
        ) as mock_browser_init, patch.object(
            orchestrator.reward_detector, "initialize", new_callable=AsyncMock
        ) as mock_detector_init, patch.object(
            orchestrator.state_manager, "initialize", new_callable=AsyncMock
        ) as mock_state_init:
            mock_browser_impl = AsyncMock()
            mock_browser_init.return_value = mock_browser_impl

            await orchestrator.initialize()

            assert orchestrator.browser_impl == mock_browser_impl
            mock_browser_init.assert_called_once()
            mock_detector_init.assert_called_once()
            mock_state_init.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialization_failure(self, orchestrator):
        """Test orchestrator initialization failure handling."""
        with patch.object(
            orchestrator.browser_manager, "initialize", new_callable=AsyncMock
        ) as mock_browser_init, patch.object(
            orchestrator, "cleanup", new_callable=AsyncMock
        ) as mock_cleanup:
            mock_browser_init.side_effect = Exception("Browser init failed")

            with pytest.raises(
                AutomationError, match="Orchestrator initialization failed"
            ):
                await orchestrator.initialize()

            mock_cleanup.assert_called_once()

    @pytest.mark.asyncio
    async def test_workflow_success(self, orchestrator):
        """Test successful complete workflow execution."""
        mock_browser_impl = AsyncMock()
        orchestrator.browser_impl = mock_browser_impl

        with patch.object(
            orchestrator, "_navigate_to_hoyolab", new_callable=AsyncMock
        ) as mock_nav, patch.object(
            orchestrator, "_authenticate", new_callable=AsyncMock
        ) as mock_auth, patch.object(
            orchestrator, "_analyze_interface", new_callable=AsyncMock
        ) as mock_analyze, patch.object(
            orchestrator.state_manager, "log_execution_result", new_callable=AsyncMock
        ) as mock_log:
            mock_auth.return_value = True
            mock_analyze.return_value = {"selectors": ["test"], "confidence": 0.8}

            result = await orchestrator.execute_workflow()

            assert result["success"] is True
            assert result["authentication_success"] is True
            assert result["step_completed"] == "interface_analysis"

            mock_nav.assert_called_once()
            mock_auth.assert_called_once()
            mock_analyze.assert_called_once()
            mock_log.assert_called_once()

    @pytest.mark.asyncio
    async def test_workflow_authentication_failure(self, orchestrator):
        """Test workflow failure due to authentication."""
        mock_browser_impl = AsyncMock()
        orchestrator.browser_impl = mock_browser_impl

        with patch.object(
            orchestrator, "_navigate_to_hoyolab", new_callable=AsyncMock
        ), patch.object(
            orchestrator, "_authenticate", new_callable=AsyncMock
        ) as mock_auth, patch.object(
            orchestrator, "_capture_debug_screenshot", new_callable=AsyncMock
        ) as mock_screenshot, patch.object(
            orchestrator.state_manager, "log_execution_result", new_callable=AsyncMock
        ) as mock_log:
            mock_auth.return_value = False
            mock_screenshot.return_value = "screenshot.png"

            with pytest.raises(
                AutomationError, match="Workflow failed at authentication"
            ):
                await orchestrator.execute_workflow()

            mock_log.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticate_success(self, orchestrator):
        """Test successful authentication flow."""
        mock_browser_impl = AsyncMock()
        orchestrator.browser_impl = mock_browser_impl

        with patch.object(
            orchestrator, "_set_authentication_cookies", new_callable=AsyncMock
        ) as mock_cookies, patch.object(
            orchestrator, "_validate_authentication", new_callable=AsyncMock
        ) as mock_validate, patch(
            "src.utils.timing.page_load_delay", new_callable=AsyncMock
        ) as mock_delay:
            mock_validate.return_value = True

            result = await orchestrator._authenticate()

            assert result is True
            mock_cookies.assert_called_once()
            mock_validate.assert_called_once()
            mock_delay.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_authentication_cookies(self, orchestrator):
        """Test authentication cookie setting."""
        mock_browser_impl = AsyncMock()
        orchestrator.browser_impl = mock_browser_impl

        credentials = MagicMock()
        credentials.ltuid = "test_ltuid"
        credentials.ltoken = "test_ltoken"
        credentials.account_id = "test_account"

        with patch.object(
            orchestrator, "_set_browser_cookie", new_callable=AsyncMock
        ) as mock_set_cookie:
            await orchestrator._set_authentication_cookies(credentials)

            # Should be called 3 times for ltuid, ltoken, and account_id
            assert mock_set_cookie.call_count == 3

    @pytest.mark.asyncio
    async def test_capture_debug_screenshot(self, orchestrator):
        """Test debug screenshot capture."""
        mock_browser_impl = AsyncMock()
        orchestrator.browser_impl = mock_browser_impl

        with patch.object(
            orchestrator.state_manager, "get_current_timestamp"
        ) as mock_timestamp, patch("pathlib.Path.mkdir"):
            mock_timestamp.return_value = "2023-01-01T12:00:00"

            result = await orchestrator._capture_debug_screenshot("test")

            assert result is not None
            assert "test_2023-01-01T12-00-00.png" in result
            mock_browser_impl.screenshot.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup(self, orchestrator):
        """Test resource cleanup."""
        mock_browser_impl = AsyncMock()
        orchestrator.browser_impl = mock_browser_impl

        await orchestrator.cleanup()

        mock_browser_impl.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager(self, orchestrator):
        """Test async context manager functionality."""
        with patch.object(
            orchestrator, "cleanup", new_callable=AsyncMock
        ) as mock_cleanup:
            async with orchestrator:
                pass

            mock_cleanup.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_interface_report(self, orchestrator):
        """Test interface report generation."""
        analysis_result = {
            "selectors": [
                {
                    "selector": ".test",
                    "confidence": 0.9,
                    "target_type": "button",
                    "strategy": "test",
                },
                {
                    "selector": ".test2",
                    "confidence": 0.3,
                    "target_type": "link",
                    "strategy": "test",
                },
            ],
            "primary_strategy": "test_strategy",
            "fallback_strategies": ["fallback1"],
            "detection_confidence": 0.8,
        }

        report = await orchestrator._generate_interface_report(analysis_result)

        assert report["analysis_summary"]["primary_detection_method"] == "test_strategy"
        assert len(report["selector_inventory"]["high_confidence"]) == 1
        assert len(report["selector_inventory"]["low_confidence"]) == 1
        assert report["reliability_assessment"]["stability_score"] == 50.0
