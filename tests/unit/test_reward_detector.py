"""Unit tests for RewardDetector CSS selector strategies."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.detection.detector import RewardDetector
from src.detection.strategies import AttributeBasedStrategy, HoYoLABClassBasedStrategy


class TestRewardDetector:
    """Test cases for RewardDetector class."""

    @pytest.fixture
    def detector(self):
        """Create detector instance for testing."""
        return RewardDetector()

    @pytest.fixture
    def mock_browser(self):
        """Create mock browser implementation."""
        browser = AsyncMock()
        browser.find_element.return_value = True
        browser.find_elements.return_value = [
            {
                "index": 0,
                "tag_name": "button",
                "text_content": "Sign in",
                "is_visible": True,
            }
        ]
        return browser

    @pytest.mark.asyncio
    async def test_initialize(self, detector):
        """Test detector initialization."""
        await detector.initialize()

        assert len(detector.strategies) > 0
        assert detector.strategy_factory is not None

    @pytest.mark.asyncio
    async def test_analyze_interface_success(self, detector, mock_browser):
        """Test successful interface analysis."""
        # Mock strategy results
        mock_strategy = AsyncMock()
        mock_strategy.name = "test_strategy"
        mock_strategy.detect_elements.return_value = {
            "found_elements": ["signin_button"],
            "selectors": [{"selector": ".signin-btn", "target_type": "button"}],
            "confidence": 0.8,
        }

        detector.strategies = [mock_strategy]

        with patch.object(
            detector, "_analyze_reward_states", new_callable=AsyncMock
        ) as mock_analyze_states:
            mock_analyze_states.return_value = {"claimable_rewards": []}

            result = await detector.analyze_interface(mock_browser)

            assert result["primary_strategy"] == "test_strategy"
            assert result["detection_confidence"] == 0.8
            assert len(result["selectors"]) == 1
            assert "analysis_timestamp" in result

    @pytest.mark.asyncio
    async def test_analyze_interface_no_strategies_found(self, detector, mock_browser):
        """Test interface analysis when no strategies find elements."""
        mock_strategy = AsyncMock()
        mock_strategy.name = "failing_strategy"
        mock_strategy.detect_elements.return_value = {
            "found_elements": [],
            "selectors": [],
            "confidence": 0.0,
        }

        detector.strategies = [mock_strategy]

        result = await detector.analyze_interface(mock_browser)

        assert result["detection_confidence"] == 0.0
        assert result["primary_strategy"] is None
        assert len(result["fallback_strategies"]) == 0

    @pytest.mark.asyncio
    async def test_analyze_interface_strategy_failure(self, detector, mock_browser):
        """Test interface analysis with strategy failures."""
        mock_strategy = AsyncMock()
        mock_strategy.name = "failing_strategy"
        mock_strategy.detect_elements.side_effect = Exception("Strategy failed")

        detector.strategies = [mock_strategy]

        result = await detector.analyze_interface(mock_browser)

        assert result["detection_confidence"] == 0.0

    @pytest.mark.asyncio
    async def test_find_best_selector(self, detector, mock_browser):
        """Test finding best selector for target."""
        mock_strategy = AsyncMock()
        mock_strategy.get_selector_for_target.return_value = ".signin-btn"

        detector.strategies = [mock_strategy]

        result = await detector.find_best_selector(mock_browser, "signin_button")

        assert result == ".signin-btn"
        mock_strategy.get_selector_for_target.assert_called_once_with(
            mock_browser, "signin_button"
        )

    @pytest.mark.asyncio
    async def test_find_best_selector_not_found(self, detector, mock_browser):
        """Test finding selector when none found."""
        mock_strategy = AsyncMock()
        mock_strategy.get_selector_for_target.return_value = None

        detector.strategies = [mock_strategy]

        result = await detector.find_best_selector(mock_browser, "nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_validate_selector_reliability(self, detector, mock_browser):
        """Test selector reliability validation."""
        mock_browser.find_element.return_value = True

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.time.side_effect = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5]

            result = await detector.validate_selector_reliability(
                mock_browser, ".test-selector", attempts=3
            )

            assert result["selector"] == ".test-selector"
            assert result["successful_attempts"] == 3
            assert result["total_attempts"] == 3
            assert result["reliability_score"] == 1.0

    @pytest.mark.asyncio
    async def test_validate_selector_reliability_partial_success(
        self, detector, mock_browser
    ):
        """Test selector reliability with partial success."""
        # Mock find_element to fail once, succeed twice
        mock_browser.find_element.side_effect = [False, True, True]

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.time.side_effect = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5]

            result = await detector.validate_selector_reliability(
                mock_browser, ".test-selector", attempts=3
            )

            assert result["successful_attempts"] == 2
            assert result["reliability_score"] == pytest.approx(0.67, rel=1e-2)

    @pytest.mark.asyncio
    async def test_test_selector_success(self, detector, mock_browser):
        """Test successful selector testing."""
        mock_browser.find_element.return_value = True

        result = await detector._test_selector(mock_browser, ".test-selector")

        assert result is True
        mock_browser.find_element.assert_called_once_with(
            ".test-selector", timeout=5000
        )

    @pytest.mark.asyncio
    async def test_test_selector_failure(self, detector, mock_browser):
        """Test selector testing failure."""
        mock_browser.find_element.return_value = False

        result = await detector._test_selector(mock_browser, ".nonexistent")

        assert result is False

    @pytest.mark.asyncio
    async def test_analyze_reward_states(self, detector, mock_browser):
        """Test reward state analysis."""
        mock_strategy = AsyncMock()
        mock_strategy.name = "test_strategy"
        mock_strategy.analyze_reward_states.return_value = {
            "claimable_rewards": ["reward1"],
            "claimed_rewards": ["reward2"],
            "unavailable_rewards": [],
        }

        detector.strategy_factory.get_strategy_by_name = MagicMock(
            return_value=mock_strategy
        )

        strategy_result = {"strategy": "test_strategy"}
        result = await detector._analyze_reward_states(mock_browser, strategy_result)

        assert result["total_found"] == 2
        assert len(result["claimable_rewards"]) == 1
        assert len(result["claimed_rewards"]) == 1
        assert result["analysis_method"] == "test_strategy"

    @pytest.mark.asyncio
    async def test_analyze_reward_states_no_strategy(self, detector, mock_browser):
        """Test reward state analysis with no strategy found."""
        detector.strategy_factory.get_strategy_by_name = MagicMock(return_value=None)

        strategy_result = {"strategy": "nonexistent_strategy"}
        result = await detector._analyze_reward_states(mock_browser, strategy_result)

        assert result["total_found"] == 0
        assert result["analysis_method"] == "nonexistent_strategy"


class TestSelectorStrategies:
    """Test cases for selector strategies."""

    @pytest.fixture
    def detector(self):
        """Create detector instance for testing."""
        return RewardDetector()

    @pytest.fixture
    def mock_browser(self):
        """Create mock browser implementation."""
        browser = AsyncMock()
        browser.find_element.return_value = True
        browser.find_elements.return_value = [
            {
                "index": 0,
                "tag_name": "button",
                "text_content": "Sign in",
                "is_visible": True,
            }
        ]
        return browser

    @pytest.mark.asyncio
    async def test_hoyolab_class_based_strategy(self, mock_browser):
        """Test HoYoLAB class-based strategy."""
        strategy = HoYoLABClassBasedStrategy()
        mock_browser.find_element.return_value = True

        result = await strategy.detect_elements(mock_browser)

        assert result["strategy_name"] == "hoyolab_class_based"
        assert len(result["selectors"]) > 0

    @pytest.mark.asyncio
    async def test_hoyolab_strategy_no_elements_found(self, mock_browser):
        """Test HoYoLAB strategy when no elements found."""
        strategy = HoYoLABClassBasedStrategy()
        mock_browser.find_element.return_value = False

        result = await strategy.detect_elements(mock_browser)

        assert result["confidence"] == 0.2
        assert len(result["found_elements"]) == 0

    @pytest.mark.asyncio
    async def test_attribute_based_strategy(self, mock_browser):
        """Test attribute-based strategy."""
        strategy = AttributeBasedStrategy()
        mock_browser.find_element.return_value = True

        result = await strategy.detect_elements(mock_browser)

        assert result["strategy_name"] == "attribute_based"
        assert len(result["selectors"]) > 0

    @pytest.mark.asyncio
    async def test_strategy_get_selector_for_target(self):
        """Test getting selector for specific target."""
        strategy = HoYoLABClassBasedStrategy()

        selector = await strategy.get_selector_for_target(None, "signin_button")

        assert selector == ".signin-btn"

    @pytest.mark.asyncio
    async def test_strategy_get_selector_for_unknown_target(self):
        """Test getting selector for unknown target."""
        strategy = HoYoLABClassBasedStrategy()

        selector = await strategy.get_selector_for_target(None, "unknown_target")

        assert selector is None

    @pytest.mark.asyncio
    async def test_detect_reward_availability_enhanced(self, detector, mock_browser):
        """Test enhanced reward availability detection with state differentiation."""
        await detector.initialize()
        
        # Mock the entire detect_reward_availability method for focused testing
        with patch.object(detector, 'analyze_interface') as mock_analyze:
            mock_analyze.return_value = {
                "detection_confidence": 0.8,
                "primary_strategy": "test_strategy",
                "fallback_strategies": []
            }
            
            with patch.object(detector, '_detect_reward_states_with_confidence') as mock_states:
                mock_states.return_value = {
                    "claimable_rewards": [{"selector": ".reward-item.claimable"}],
                    "claimed_rewards": [{"selector": ".reward-item.claimed"}],
                    "unavailable_rewards": [],
                    "detection_confidence": 0.8,
                }
                
                result = await detector.detect_reward_availability(mock_browser)
                
                assert result["total_rewards_found"] == 2
                assert len(result["claimable_rewards"]) == 1
                assert len(result["claimed_rewards"]) == 1
                assert result["detection_confidence"] >= 0.8
                assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_claim_available_rewards_success(self, detector, mock_browser):
        """Test successful reward claiming automation."""
        await detector.initialize()
        
        # Mock browser click behavior
        mock_browser.click_element.return_value = True
        mock_browser.find_element.return_value = True
        
        # Mock detection result
        detection_result = {
            "claimable_rewards": [
                {"selector": ".reward-item.claimable", "state": "claimable", "confidence": 0.9}
            ],
            "detection_confidence": 0.8,
        }
        
        result = await detector.claim_available_rewards(mock_browser, detection_result)
        
        assert result["success"] is True
        assert result["claims_processed"] == 1
        assert len(result["successful_claims"]) == 1
        assert result["timing_applied"] is True
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_claim_available_rewards_no_rewards(self, detector, mock_browser):
        """Test claiming when no rewards are available."""
        await detector.initialize()
        
        detection_result = {
            "claimable_rewards": [],
            "detection_confidence": 0.8,
        }
        
        result = await detector.claim_available_rewards(mock_browser, detection_result)
        
        assert result["success"] is True  # No rewards to claim is still success
        assert result["claims_processed"] == 0
        assert len(result["successful_claims"]) == 0

    @pytest.mark.asyncio
    async def test_validate_claim_success(self, detector, mock_browser):
        """Test claim success validation with UI feedback."""
        await detector.initialize()
        
        # Mock UI success feedback
        def mock_find_element(selector, timeout=None):
            if "success" in selector:
                return True
            return False
        
        mock_browser.find_element.side_effect = mock_find_element
        mock_browser.capture_screenshot.return_value = True
        
        pre_claim_state = {
            "claimable_rewards": [{"selector": ".reward-1"}],
            "claimed_rewards": [],
        }
        
        result = await detector.validate_claim_success(mock_browser, pre_claim_state)
        
        assert "claim_validated" in result
        assert "validation_confidence" in result
        assert "ui_feedback_detected" in result
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_enhanced_error_handling(self, detector, mock_browser):
        """Test enhanced error handling for various failure scenarios."""
        await detector.initialize()
        
        from src.utils.exceptions import NetworkTimeoutError, ElementNotFoundError
        
        # Test network timeout handling
        timeout_error = NetworkTimeoutError("Network timeout occurred")
        context = {"step": "reward_claiming", "attempt": 1}
        
        result = await detector.handle_claiming_errors(mock_browser, timeout_error, context)
        
        assert result["error_type"] == "NetworkTimeoutError"
        assert result["retry_recommended"] is True
        assert result["context_preserved"] is True
        
        # Test element not found handling
        element_error = ElementNotFoundError("Element not found")
        
        result = await detector.handle_claiming_errors(mock_browser, element_error, context)
        
        assert result["error_type"] == "ElementNotFoundError"
        assert result["fallback_available"] is True
