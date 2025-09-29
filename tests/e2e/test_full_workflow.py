"""End-to-end tests for complete reward detection and claiming workflow."""

import pytest
from unittest.mock import AsyncMock, patch

from src.automation.orchestrator import AutomationOrchestrator
from src.config.manager import ConfigurationManager
from src.utils.exceptions import AutomationError


class TestFullWorkflow:
    """End-to-end test cases for complete check-in workflow."""

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration manager."""
        config = AsyncMock(spec=ConfigurationManager)
        config.get_hoyolab_url.return_value = (
            "https://act.hoyolab.com/ys/event/signin-sea-v3/index.html"
        )
        config.get_hoyolab_credentials.return_value = AsyncMock(
            ltuid="test_uid", ltoken="test_token", account_id="test_account"
        )
        config.get_browser_config.return_value = {}
        config.get_detection_config.return_value = {}
        config.get_timing_config.return_value = {}
        return config

    @pytest.fixture
    def orchestrator(self, mock_config):
        """Create orchestrator instance for testing."""
        return AutomationOrchestrator(mock_config)

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_complete_checkin_workflow_dry_run(self, orchestrator):
        """Test complete check-in workflow in dry run mode."""
        # Mock all browser operations
        with patch.object(
            orchestrator, '_navigate_to_hoyolab', new_callable=AsyncMock
        ) as mock_nav, \
             patch.object(
                 orchestrator, '_authenticate', return_value=True
             ) as mock_auth, \
             patch.object(
                 orchestrator.reward_detector, 'detect_reward_availability'
             ) as mock_detect:

            # Mock reward detection result
            mock_detect.return_value = {
                "claimable_rewards": [
                    {
                        "selector": ".reward-item.claimable",
                        "state": "claimable",
                        "confidence": 0.9
                    }
                ],
                "claimed_rewards": [
                    {"selector": ".reward-item.claimed", "state": "claimed", "confidence": 0.9}
                ],
                "total_rewards_found": 2,
                "detection_confidence": 0.8,
            }

            # Initialize orchestrator
            await orchestrator.initialize()

            # Execute dry run workflow
            result = await orchestrator.execute_checkin(dry_run=True)

            # Verify workflow completion
            assert result["success"] is True
            assert result["workflow_completed"] is True
            assert result["dry_run"] is True
            assert result["step_completed"] == "dry_run_complete"
            assert result["authentication_success"] is True
            assert len(result["reward_detection"]["claimable_rewards"]) == 1
            assert result["claiming_results"]["dry_run"] is True

            # Verify all steps were called
            mock_nav.assert_called_once()
            mock_auth.assert_called_once()
            mock_detect.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_complete_checkin_workflow_with_claiming(self, orchestrator):
        """Test complete check-in workflow with actual reward claiming."""
        # Mock all browser operations including claiming
        with patch.object(orchestrator, '_navigate_to_hoyolab', new_callable=AsyncMock) as mock_nav, \
             patch.object(orchestrator, '_authenticate', return_value=True) as mock_auth, \
             patch.object(orchestrator.reward_detector, 'detect_reward_availability') as mock_detect, \
             patch.object(orchestrator.reward_detector, 'claim_available_rewards') as mock_claim, \
             patch.object(orchestrator.reward_detector, 'validate_claim_success') as mock_validate:
            
            # Mock detection result with claimable rewards
            mock_detect.return_value = {
                "claimable_rewards": [
                    {"selector": ".reward-item.claimable", "state": "claimable", "confidence": 0.9}
                ],
                "claimed_rewards": [],
                "total_rewards_found": 1,
                "detection_confidence": 0.8,
            }

            # Mock successful claiming
            mock_claim.return_value = {
                "success": True,
                "claims_processed": 1,
                "successful_claims": [{"reward": {"selector": ".reward-item.claimable"}}],
                "failed_claims": [],
                "timing_applied": True,
            }

            # Mock successful validation
            mock_validate.return_value = {
                "claim_validated": True,
                "validation_confidence": 0.9,
                "ui_feedback_detected": [{"type": "success_message"}],
                "screenshot_captured": True,
            }

            # Initialize orchestrator
            await orchestrator.initialize()

            # Execute complete workflow
            result = await orchestrator.execute_checkin(dry_run=False)

            # Verify workflow completion
            assert result["success"] is True
            assert result["workflow_completed"] is True
            assert result["dry_run"] is False
            assert result["step_completed"] == "claim_validation"
            assert result["claiming_results"]["success"] is True
            assert result["claiming_results"]["claims_processed"] == 1
            assert result["validation_results"]["claim_validated"] is True

            # Verify all workflow steps were executed
            mock_nav.assert_called_once()
            mock_auth.assert_called_once()
            mock_detect.assert_called_once()
            mock_claim.assert_called_once()
            mock_validate.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_workflow_with_no_claimable_rewards(self, orchestrator):
        """Test workflow when no claimable rewards are found."""
        with patch.object(orchestrator, '_navigate_to_hoyolab', new_callable=AsyncMock), \
             patch.object(orchestrator, '_authenticate', return_value=True), \
             patch.object(orchestrator.reward_detector, 'detect_reward_availability') as mock_detect:
            
            # Mock detection result with no claimable rewards
            mock_detect.return_value = {
                "claimable_rewards": [],
                "claimed_rewards": [
                    {"selector": ".reward-item.claimed", "state": "claimed", "confidence": 0.9}
                ],
                "total_rewards_found": 1,
                "detection_confidence": 0.8,
            }

            await orchestrator.initialize()
            result = await orchestrator.execute_checkin(dry_run=False)

            # Verify workflow handles no rewards gracefully
            assert result["success"] is True
            assert result["step_completed"] == "no_rewards_to_claim"
            assert result["claiming_results"]["no_rewards"] is True
            assert len(result["reward_detection"]["claimable_rewards"]) == 0

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_workflow_authentication_failure(self, orchestrator):
        """Test workflow failure handling during authentication."""
        with patch.object(orchestrator, '_navigate_to_hoyolab', new_callable=AsyncMock), \
             patch.object(orchestrator, '_authenticate', return_value=False):
            
            await orchestrator.initialize()

            # Should raise AutomationError due to auth failure
            with pytest.raises(AutomationError) as exc_info:
                await orchestrator.execute_checkin(dry_run=False)

            assert "Authentication failed" in str(exc_info.value)

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_workflow_error_handling_with_recovery(self, orchestrator):
        """Test workflow error handling and recovery mechanisms."""
        with patch.object(orchestrator, '_navigate_to_hoyolab', new_callable=AsyncMock), \
             patch.object(orchestrator, '_authenticate', new_callable=AsyncMock, return_value=True), \
             patch.object(orchestrator.reward_detector, 'detect_reward_availability') as mock_detect, \
             patch.object(orchestrator.reward_detector, 'handle_claiming_errors') as mock_error_handler:
            
            # Mock detection failure
            mock_detect.side_effect = Exception("Network timeout")

            # Mock error handler
            mock_error_handler.return_value = {
                "error_type": "Exception", 
                "retry_recommended": True,
                "recovery_attempted": True,
            }

            await orchestrator.initialize()

            # Should raise AutomationError but with error handling context
            with pytest.raises(AutomationError) as exc_info:
                await orchestrator.execute_checkin(dry_run=False)

            assert "Network timeout" in str(exc_info.value)

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_workflow_cleanup_on_failure(self, orchestrator):
        """Test that cleanup happens even when workflow fails."""
        with patch.object(orchestrator, '_navigate_to_hoyolab', new_callable=AsyncMock), \
             patch.object(orchestrator, '_authenticate', side_effect=Exception("Auth failure")), \
             patch.object(orchestrator, 'cleanup', new_callable=AsyncMock) as mock_cleanup:
            
            await orchestrator.initialize()

            # Should raise error but still call cleanup
            with pytest.raises(AutomationError):
                await orchestrator.execute_checkin(dry_run=False)

            # Cleanup should be called in finally block
            mock_cleanup.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_workflow_comprehensive_logging(self, orchestrator):
        """Test that workflow logs comprehensive execution results."""
        with patch.object(orchestrator, '_navigate_to_hoyolab', new_callable=AsyncMock), \
             patch.object(orchestrator, '_authenticate', return_value=True), \
             patch.object(orchestrator.reward_detector, 'detect_reward_availability') as mock_detect, \
             patch.object(orchestrator, '_log_execution_result', new_callable=AsyncMock) as mock_log:
            
            mock_detect.return_value = {
                "claimable_rewards": [],
                "claimed_rewards": [],
                "total_rewards_found": 0,
                "detection_confidence": 0.8,
            }

            await orchestrator.initialize()
            result = await orchestrator.execute_checkin(dry_run=True)

            # Verify comprehensive logging was called
            mock_log.assert_called_once()
            
            # Verify log contains expected structure
            log_call_args = mock_log.call_args[0][0]
            assert "success" in log_call_args
            assert "workflow_completed" in log_call_args
            assert "reward_detection" in log_call_args
            assert "claiming_results" in log_call_args