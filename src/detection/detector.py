"""Reward Detector for intelligent reward detection using multiple CSS strategies.

Provides dynamic CSS selector discovery, DOM analysis for reward states,
and fallback mechanisms for robust interface interaction.
"""

import asyncio
from typing import Any, Dict, List, Optional

import structlog

from ..browser.manager import BrowserManagerInterface
from ..utils.exceptions import DetectionError
from .strategies import SelectorStrategy, SelectorStrategyFactory

logger = structlog.get_logger(__name__)


class RewardDetector:
    """Intelligent reward detection with multiple CSS selector strategies."""

    def __init__(self):
        """Initialize reward detector."""
        self.strategies: List[SelectorStrategy] = []
        self.strategy_factory = SelectorStrategyFactory()

    async def initialize(self) -> None:
        """Initialize detector with available strategies."""
        try:
            # Load all available detection strategies
            self.strategies = self.strategy_factory.get_all_strategies()

            logger.info("Reward detector initialized", strategy_count=len(self.strategies))

        except Exception as e:
            raise DetectionError(f"Failed to initialize reward detector: {e}")

    async def detect_reward_availability(self, browser: BrowserManagerInterface) -> Dict[str, Any]:
        """Enhanced reward detection with state differentiation and confidence scoring.

        Args:
            browser: Browser implementation instance

        Returns:
            Reward detection results with detailed state analysis and confidence metrics

        Raises:
            DetectionError: If reward detection fails completely
        """
        detection_result = {
            "claimable_rewards": [],
            "claimed_rewards": [],
            "unavailable_rewards": [],
            "total_rewards_found": 0,
            "detection_confidence": 0.0,
            "strategies_used": [],
            "fallback_strategies": [],
            "state_analysis": {},
            "timestamp": None,
        }

        try:
            logger.info("Starting enhanced reward availability detection")

            # Run interface analysis first
            interface_analysis = await self.analyze_interface(browser)
            detection_result["strategies_used"] = interface_analysis.get("primary_strategy", [])
            detection_result["fallback_strategies"] = interface_analysis.get(
                "fallback_strategies", []
            )

            if interface_analysis["detection_confidence"] < 0.3:
                logger.warning(
                    "Low interface detection confidence",
                    confidence=interface_analysis["detection_confidence"],
                )
                detection_result["detection_confidence"] = interface_analysis[
                    "detection_confidence"
                ]
                return detection_result

            # Enhanced reward state differentiation
            reward_states = await self._detect_reward_states_with_confidence(
                browser, interface_analysis
            )
            detection_result.update(reward_states)

            # Calculate total rewards found
            detection_result["total_rewards_found"] = (
                len(detection_result["claimable_rewards"])
                + len(detection_result["claimed_rewards"])
                + len(detection_result["unavailable_rewards"])
            )

            # Set timestamp
            from datetime import datetime, timezone

            detection_result["timestamp"] = datetime.now(timezone.utc).isoformat()

            logger.info(
                "Reward availability detection completed",
                total_rewards=detection_result["total_rewards_found"],
                claimable=len(detection_result["claimable_rewards"]),
                confidence=detection_result["detection_confidence"],
            )

            return detection_result

        except Exception as e:
            logger.error("Reward availability detection failed", error=str(e))
            raise DetectionError(f"Reward availability detection failed: {e}")

    async def _detect_reward_states_with_confidence(
        self, browser: BrowserManagerInterface, interface_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect reward states with confidence scoring and fallback strategies.

        Args:
            browser: Browser implementation instance
            interface_analysis: Results from interface analysis

        Returns:
            Enhanced reward state detection results
        """
        state_result = {
            "claimable_rewards": [],
            "claimed_rewards": [],
            "unavailable_rewards": [],
            "detection_confidence": 0.0,
            "state_analysis": {},
        }

        try:
            # Use primary strategy for state detection
            primary_strategy_name = interface_analysis.get("primary_strategy")
            if primary_strategy_name:
                primary_strategy = self.strategy_factory.get_strategy_by_name(primary_strategy_name)

                if primary_strategy and hasattr(primary_strategy, "analyze_reward_states"):
                    primary_states = await primary_strategy.analyze_reward_states(browser)
                    state_result.update(primary_states)
                    state_result["detection_confidence"] = interface_analysis.get(
                        "detection_confidence", 0.5
                    )

            # Fallback strategy implementation
            if state_result["detection_confidence"] < 0.6:
                logger.info("Using fallback strategies for reward state detection")
                await self._apply_fallback_detection(browser, state_result, interface_analysis)

            # Validate and score confidence based on multiple factors
            state_result["detection_confidence"] = self._calculate_confidence_score(state_result)

            # Add detailed state analysis
            state_result["state_analysis"] = await self._analyze_state_indicators(
                browser, state_result
            )

            return state_result

        except Exception as e:
            logger.error("Reward state detection with confidence failed", error=str(e))
            state_result["detection_confidence"] = 0.0
            return state_result

    async def _apply_fallback_detection(
        self,
        browser: BrowserManagerInterface,
        state_result: Dict[str, Any],
        interface_analysis: Dict[str, Any],
    ) -> None:
        """Apply fallback detection strategies for improved reliability.

        Args:
            browser: Browser implementation instance
            state_result: Current state detection results to enhance
            interface_analysis: Interface analysis results
        """
        try:
            fallback_strategies = interface_analysis.get("fallback_strategies", [])

            for strategy_name in fallback_strategies[:2]:  # Limit to 2 fallback attempts
                try:
                    strategy = self.strategy_factory.get_strategy_by_name(strategy_name)
                    if strategy and hasattr(strategy, "analyze_reward_states"):
                        fallback_states = await strategy.analyze_reward_states(browser)

                        # Merge results with existing state_result
                        self._merge_detection_results(state_result, fallback_states)

                        logger.debug("Applied fallback strategy", strategy=strategy_name)

                except Exception as e:
                    logger.debug("Fallback strategy failed", strategy=strategy_name, error=str(e))
                    continue

        except Exception as e:
            logger.error("Fallback detection application failed", error=str(e))

    def _merge_detection_results(
        self, primary_result: Dict[str, Any], fallback_result: Dict[str, Any]
    ) -> None:
        """Merge detection results from fallback strategies.

        Args:
            primary_result: Primary detection results to update
            fallback_result: Fallback detection results to merge
        """
        try:
            # Merge reward lists while avoiding duplicates
            for key in ["claimable_rewards", "claimed_rewards", "unavailable_rewards"]:
                if key in fallback_result:
                    existing_items = primary_result.get(key, [])
                    new_items = fallback_result[key]

                    # Simple duplicate avoidance (can be enhanced with selector comparison)
                    for item in new_items:
                        if item not in existing_items:
                            existing_items.append(item)

                    primary_result[key] = existing_items

        except Exception as e:
            logger.debug("Result merging failed", error=str(e))

    def _calculate_confidence_score(self, state_result: Dict[str, Any]) -> float:
        """Calculate confidence score based on detection results.

        Args:
            state_result: State detection results

        Returns:
            Confidence score between 0.0 and 1.0
        """
        try:
            base_confidence = state_result.get("detection_confidence", 0.0)
            total_rewards = (
                len(state_result.get("claimable_rewards", []))
                + len(state_result.get("claimed_rewards", []))
                + len(state_result.get("unavailable_rewards", []))
            )

            # Boost confidence if we found rewards
            if total_rewards > 0:
                reward_bonus = min(0.3, total_rewards * 0.1)
                base_confidence += reward_bonus

            # Cap at 1.0
            return min(1.0, base_confidence)

        except Exception as e:
            logger.debug("Confidence calculation failed", error=str(e))
            return 0.0

    async def _analyze_state_indicators(
        self, browser: BrowserManagerInterface, state_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze visual indicators and DOM attributes for state validation.

        Args:
            browser: Browser implementation instance
            state_result: Current state detection results

        Returns:
            State indicator analysis results
        """
        indicators = {
            "visual_indicators_found": [],
            "dom_attributes_analyzed": [],
            "state_validation_score": 0.0,
        }

        try:
            # Look for common visual state indicators
            visual_selectors = [
                ".claimed",
                ".disabled",
                ".unavailable",
                ".available",
                ".claimable",
                ".ready",
                "[disabled]",
                ".btn-success",
                ".btn-primary",
            ]

            for selector in visual_selectors:
                try:
                    found = await browser.find_element(selector, timeout=1000)
                    if found:
                        indicators["visual_indicators_found"].append(selector)
                except Exception:
                    continue

            # Analyze DOM attributes that indicate state
            dom_attributes = ["data-state", "aria-disabled", "class", "data-claimed"]
            indicators["dom_attributes_analyzed"] = dom_attributes

            # Calculate validation score
            indicators["state_validation_score"] = min(
                1.0, len(indicators["visual_indicators_found"]) * 0.2
            )

        except Exception as e:
            logger.debug("State indicator analysis failed", error=str(e))

        return indicators

    async def claim_available_rewards(
        self, browser: BrowserManagerInterface, detection_result: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Automated reward claiming with confirmation dialog handling and timing delays.

        Args:
            browser: Browser implementation instance
            detection_result: Optional previous detection results to use

        Returns:
            Claiming operation results with success status and details

        Raises:
            DetectionError: If claiming operation fails completely
        """
        claiming_result = {
            "success": False,
            "claims_processed": 0,
            "successful_claims": [],
            "failed_claims": [],
            "total_attempts": 0,
            "error_details": [],
            "timing_applied": True,
            "timestamp": None,
        }

        try:
            logger.info("Starting automated reward claiming")

            # Get claimable rewards if not provided
            if not detection_result:
                detection_result = await self.detect_reward_availability(browser)

            claimable_rewards = detection_result.get("claimable_rewards", [])
            if not claimable_rewards:
                logger.info("No claimable rewards found")
                claiming_result["success"] = True  # No rewards to claim is still success
                return claiming_result

            # Import timing utilities
            from ..utils.timing import TimingUtils

            timing = TimingUtils()

            claiming_result["total_attempts"] = len(claimable_rewards)

            # Process each claimable reward
            for i, reward in enumerate(claimable_rewards):
                try:
                    logger.info(f"Processing reward {i+1}/{len(claimable_rewards)}")

                    # Apply human-like delay between claims
                    if i > 0:
                        await timing.human_delay(2000, variance=0.4)  # 2s base with variance

                    # Attempt to claim the reward
                    claim_success = await self._claim_single_reward(browser, reward, timing)

                    if claim_success["success"]:
                        claiming_result["successful_claims"].append(
                            {
                                "reward": reward,
                                "attempt_number": i + 1,
                                "claim_details": claim_success,
                            }
                        )
                        claiming_result["claims_processed"] += 1
                    else:
                        claiming_result["failed_claims"].append(
                            {
                                "reward": reward,
                                "attempt_number": i + 1,
                                "error": claim_success.get("error", "Unknown error"),
                            }
                        )

                except Exception as e:
                    logger.error(f"Error claiming reward {i+1}", error=str(e))
                    claiming_result["failed_claims"].append(
                        {"reward": reward, "attempt_number": i + 1, "error": str(e)}
                    )
                    claiming_result["error_details"].append(str(e))

            # Set overall success status
            claiming_result["success"] = claiming_result["claims_processed"] > 0

            # Set timestamp
            from datetime import datetime, timezone

            claiming_result["timestamp"] = datetime.now(timezone.utc).isoformat()

            logger.info(
                "Reward claiming completed",
                processed=claiming_result["claims_processed"],
                failed=len(claiming_result["failed_claims"]),
                success=claiming_result["success"],
            )

            return claiming_result

        except Exception as e:
            logger.error("Reward claiming operation failed", error=str(e))
            claiming_result["error_details"].append(str(e))
            raise DetectionError(f"Reward claiming failed: {e}")

    async def _claim_single_reward(
        self, browser: BrowserManagerInterface, reward: Dict[str, Any], timing: Any
    ) -> Dict[str, Any]:
        """Claim a single reward with proper timing and confirmation handling.

        Args:
            browser: Browser implementation instance
            reward: Reward details including selector
            timing: TimingUtils instance for human-like delays

        Returns:
            Single claim operation result
        """
        claim_result = {
            "success": False,
            "clicked": False,
            "confirmed": False,
            "retry_attempts": 0,
            "error": None,
        }

        try:
            reward_selector = reward.get("selector")
            if not reward_selector:
                claim_result["error"] = "No selector provided for reward"
                return claim_result

            # Attempt to click the reward element with retries
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    claim_result["retry_attempts"] = attempt + 1

                    # Pre-click timing delay
                    await timing.human_delay(800, variance=0.3)

                    # Click the reward element
                    click_success = await browser.click_element(reward_selector, timeout=5000)

                    if click_success:
                        claim_result["clicked"] = True
                        logger.debug(
                            "Reward element clicked successfully", selector=reward_selector[:30]
                        )
                        break
                    else:
                        logger.warning(
                            f"Click attempt {attempt + 1} failed for reward",
                            selector=reward_selector[:30],
                        )

                except Exception as e:
                    logger.debug(
                        f"Click attempt {attempt + 1} exception",
                        selector=reward_selector[:30],
                        error=str(e),
                    )
                    if attempt == max_retries - 1:
                        claim_result[
                            "error"
                        ] = f"Failed to click reward after {max_retries} attempts: {e}"
                        return claim_result

                # Small delay before retry
                if attempt < max_retries - 1:
                    await timing.human_delay(1000, variance=0.2)

            # Handle confirmation dialog if click succeeded
            if claim_result["clicked"]:
                confirmation_success = await self._handle_confirmation_dialog(browser, timing)
                claim_result["confirmed"] = confirmation_success["confirmed"]

                if confirmation_success["error"]:
                    claim_result["error"] = confirmation_success["error"]

            # Determine overall success
            claim_result["success"] = claim_result["clicked"] and (
                claim_result["confirmed"] or True
            )

            # Post-claim delay
            await timing.human_delay(1500, variance=0.4)

        except Exception as e:
            claim_result["error"] = f"Single reward claim failed: {e}"
            logger.error("Single reward claim exception", error=str(e))

        return claim_result

    async def _handle_confirmation_dialog(
        self, browser: BrowserManagerInterface, timing: Any
    ) -> Dict[str, Any]:
        """Handle confirmation dialogs that may appear after clicking rewards.

        Args:
            browser: Browser implementation instance
            timing: TimingUtils instance for human-like delays

        Returns:
            Confirmation handling result
        """
        confirmation_result = {
            "confirmed": False,
            "dialog_found": False,
            "error": None,
        }

        try:
            # Wait for potential confirmation dialog
            await timing.human_delay(1200, variance=0.3)

            # Common confirmation dialog selectors
            confirmation_selectors = [
                ".confirm-btn",
                ".ok-btn",
                ".accept-btn",
                "[data-testid='confirm']",
                ".modal-confirm",
                "button:contains('确认')",  # Chinese "confirm"
                "button:contains('OK')",
                "button:contains('Confirm')",
            ]

            # Look for confirmation dialog
            for selector in confirmation_selectors:
                try:
                    found = await browser.find_element(selector, timeout=2000)
                    if found:
                        confirmation_result["dialog_found"] = True
                        logger.debug("Confirmation dialog detected", selector=selector[:30])

                        # Click confirmation button
                        await timing.human_delay(500, variance=0.2)
                        click_success = await browser.click_element(selector, timeout=3000)

                        if click_success:
                            confirmation_result["confirmed"] = True
                            logger.debug("Confirmation dialog accepted successfully")
                            break
                        else:
                            logger.warning("Failed to click confirmation button")

                except Exception as e:
                    logger.debug(
                        "Confirmation selector test failed", selector=selector[:30], error=str(e)
                    )
                    continue

            # If no dialog found, assume confirmation not required
            if not confirmation_result["dialog_found"]:
                confirmation_result["confirmed"] = True
                logger.debug("No confirmation dialog detected, assuming success")

        except Exception as e:
            confirmation_result["error"] = f"Confirmation dialog handling failed: {e}"
            logger.error("Confirmation dialog handling exception", error=str(e))

        return confirmation_result

    async def validate_claim_success(
        self, browser: BrowserManagerInterface, pre_claim_state: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Validate successful reward claiming through UI feedback and state changes.

        Args:
            browser: Browser implementation instance
            pre_claim_state: Optional state before claiming for comparison

        Returns:
            Claim validation results with success indicators and UI feedback

        Raises:
            DetectionError: If validation process fails completely
        """
        validation_result = {
            "claim_validated": False,
            "ui_feedback_detected": [],
            "state_changes_detected": [],
            "success_indicators": [],
            "validation_confidence": 0.0,
            "screenshot_captured": False,
            "timestamp": None,
        }

        try:
            logger.info("Starting claim success validation")

            # Check for UI success feedback
            ui_feedback = await self._detect_ui_success_feedback(browser)
            validation_result["ui_feedback_detected"] = ui_feedback["feedback_elements"]

            # Detect state changes if pre-claim state provided
            if pre_claim_state:
                state_changes = await self._detect_state_changes(browser, pre_claim_state)
                validation_result["state_changes_detected"] = state_changes["changes"]

            # Look for success indicators
            success_indicators = await self._find_success_indicators(browser)
            validation_result["success_indicators"] = success_indicators["indicators"]

            # Calculate validation confidence
            validation_result["validation_confidence"] = self._calculate_validation_confidence(
                validation_result
            )

            # Determine overall validation result
            validation_result["claim_validated"] = validation_result["validation_confidence"] > 0.6

            # Capture screenshot for verification if successful
            if validation_result["claim_validated"]:
                screenshot_success = await self._capture_success_screenshot(browser)
                validation_result["screenshot_captured"] = screenshot_success

            # Set timestamp
            from datetime import datetime, timezone

            validation_result["timestamp"] = datetime.now(timezone.utc).isoformat()

            logger.info(
                "Claim success validation completed",
                validated=validation_result["claim_validated"],
                confidence=validation_result["validation_confidence"],
            )

            return validation_result

        except Exception as e:
            logger.error("Claim success validation failed", error=str(e))
            raise DetectionError(f"Claim validation failed: {e}")

    async def _detect_ui_success_feedback(self, browser: BrowserManagerInterface) -> Dict[str, Any]:
        """Detect UI feedback elements indicating successful reward claiming.

        Args:
            browser: Browser implementation instance

        Returns:
            UI feedback detection results
        """
        feedback_result = {
            "feedback_elements": [],
            "feedback_confidence": 0.0,
        }

        try:
            # Success feedback selectors
            success_selectors = [
                ".success-message",
                ".reward-claimed",
                ".claim-success",
                ".toast-success",
                ".notification-success",
                ".alert-success",
                "[data-message='success']",
                ".modal-success",
            ]

            # Success text patterns
            success_patterns = [
                "success",
                "claimed",
                "received",
                "completed",
                "获得",
                "成功",
                "领取成功",  # Chinese success messages
            ]

            # Look for visual success elements
            for selector in success_selectors:
                try:
                    found = await browser.find_element(selector, timeout=3000)
                    if found:
                        feedback_result["feedback_elements"].append(
                            {"type": "visual_element", "selector": selector, "confidence": 0.9}
                        )
                        logger.debug("Success UI element found", selector=selector)
                except Exception:
                    continue

            # Look for success text content
            for pattern in success_patterns:
                try:
                    text_selector = f"*:contains('{pattern}')"
                    found = await browser.find_element(text_selector, timeout=2000)
                    if found:
                        feedback_result["feedback_elements"].append(
                            {"type": "text_content", "pattern": pattern, "confidence": 0.7}
                        )
                        logger.debug("Success text pattern found", pattern=pattern)
                except Exception:
                    continue

            # Calculate feedback confidence
            if feedback_result["feedback_elements"]:
                avg_confidence = sum(
                    elem.get("confidence", 0.5) for elem in feedback_result["feedback_elements"]
                ) / len(feedback_result["feedback_elements"])
                feedback_result["feedback_confidence"] = min(1.0, avg_confidence)

        except Exception as e:
            logger.error("UI success feedback detection failed", error=str(e))

        return feedback_result

    async def _detect_state_changes(
        self, browser: BrowserManagerInterface, pre_claim_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect state changes by comparing current state with pre-claim state.

        Args:
            browser: Browser implementation instance
            pre_claim_state: State before claiming for comparison

        Returns:
            State change detection results
        """
        change_result = {
            "changes": [],
            "change_confidence": 0.0,
        }

        try:
            # Get current state after claiming
            current_state = await self.detect_reward_availability(browser)

            # Compare claimable rewards count
            pre_claimable = len(pre_claim_state.get("claimable_rewards", []))
            current_claimable = len(current_state.get("claimable_rewards", []))

            if current_claimable < pre_claimable:
                change_result["changes"].append(
                    {
                        "type": "claimable_rewards_decreased",
                        "pre_count": pre_claimable,
                        "current_count": current_claimable,
                        "confidence": 0.9,
                    }
                )

            # Compare claimed rewards count
            pre_claimed = len(pre_claim_state.get("claimed_rewards", []))
            current_claimed = len(current_state.get("claimed_rewards", []))

            if current_claimed > pre_claimed:
                change_result["changes"].append(
                    {
                        "type": "claimed_rewards_increased",
                        "pre_count": pre_claimed,
                        "current_count": current_claimed,
                        "confidence": 0.9,
                    }
                )

            # Calculate change confidence
            if change_result["changes"]:
                avg_confidence = sum(
                    change.get("confidence", 0.5) for change in change_result["changes"]
                ) / len(change_result["changes"])
                change_result["change_confidence"] = avg_confidence

        except Exception as e:
            logger.error("State change detection failed", error=str(e))

        return change_result

    async def _find_success_indicators(self, browser: BrowserManagerInterface) -> Dict[str, Any]:
        """Find general success indicators in the UI.

        Args:
            browser: Browser implementation instance

        Returns:
            Success indicator detection results
        """
        indicator_result = {
            "indicators": [],
            "indicator_confidence": 0.0,
        }

        try:
            # Success indicator selectors
            indicator_selectors = [
                ".check-icon",
                ".success-icon",
                ".checkmark",
                ".reward-received-badge",
                ".completion-badge",
                "[aria-label*='success']",
                "[data-state='completed']",
            ]

            for selector in indicator_selectors:
                try:
                    found = await browser.find_element(selector, timeout=2000)
                    if found:
                        indicator_result["indicators"].append(
                            {"type": "success_icon", "selector": selector, "confidence": 0.8}
                        )
                except Exception:
                    continue

            # Calculate indicator confidence
            if indicator_result["indicators"]:
                avg_confidence = sum(
                    ind.get("confidence", 0.5) for ind in indicator_result["indicators"]
                ) / len(indicator_result["indicators"])
                indicator_result["indicator_confidence"] = avg_confidence

        except Exception as e:
            logger.error("Success indicator detection failed", error=str(e))

        return indicator_result

    def _calculate_validation_confidence(self, validation_result: Dict[str, Any]) -> float:
        """Calculate overall validation confidence based on multiple factors.

        Args:
            validation_result: Validation result data

        Returns:
            Overall confidence score between 0.0 and 1.0
        """
        try:
            confidence_factors = []

            # UI feedback confidence
            ui_feedback = validation_result.get("ui_feedback_detected", [])
            if ui_feedback:
                ui_confidence = sum(elem.get("confidence", 0.5) for elem in ui_feedback) / len(
                    ui_feedback
                )
                confidence_factors.append(ui_confidence * 0.4)  # 40% weight

            # State change confidence
            state_changes = validation_result.get("state_changes_detected", [])
            if state_changes:
                state_confidence = sum(
                    change.get("confidence", 0.5) for change in state_changes
                ) / len(state_changes)
                confidence_factors.append(state_confidence * 0.4)  # 40% weight

            # Success indicator confidence
            success_indicators = validation_result.get("success_indicators", [])
            if success_indicators:
                indicator_confidence = sum(
                    ind.get("confidence", 0.5) for ind in success_indicators
                ) / len(success_indicators)
                confidence_factors.append(indicator_confidence * 0.2)  # 20% weight

            # Return average of available confidence factors
            if confidence_factors:
                return sum(confidence_factors) / len(confidence_factors)
            else:
                return 0.0

        except Exception as e:
            logger.debug("Validation confidence calculation failed", error=str(e))
            return 0.0

    async def _capture_success_screenshot(self, browser: BrowserManagerInterface) -> bool:
        """Capture screenshot for successful claim verification.

        Args:
            browser: Browser implementation instance

        Returns:
            True if screenshot captured successfully, False otherwise
        """
        try:
            from datetime import datetime
            from pathlib import Path

            # Generate screenshot filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_dir = Path("logs/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)

            screenshot_path = screenshot_dir / f"reward_claim_success_{timestamp}.png"

            # Attempt to capture screenshot
            success = await browser.capture_screenshot(str(screenshot_path))

            if success:
                logger.info("Success screenshot captured", path=str(screenshot_path))
                return True
            else:
                logger.warning("Failed to capture success screenshot")
                return False

        except Exception as e:
            logger.error("Screenshot capture failed", error=str(e))
            return False

    async def handle_claiming_errors(
        self, browser: BrowserManagerInterface, error: Exception, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Enhanced error handling for reward claiming operations.

        Args:
            browser: Browser implementation instance
            error: Exception that occurred
            context: Additional context for error handling

        Returns:
            Error handling result with recovery actions and retry recommendations
        """
        from ..utils.exceptions import (
            AuthenticationError,
            ElementNotFoundError,
            NetworkTimeoutError,
            UIChangeError,
        )

        handling_result = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "recovery_attempted": False,
            "recovery_success": False,
            "retry_recommended": False,
            "fallback_available": False,
            "context_preserved": True,
            "timestamp": None,
        }

        try:
            logger.error(
                "Handling claiming error", error_type=type(error).__name__, context=context or {}
            )

            # Handle network timeout errors
            if (
                isinstance(error, (NetworkTimeoutError, TimeoutError))
                or "timeout" in str(error).lower()
            ):
                handling_result.update(await self._handle_network_timeout(browser, error, context))

            # Handle element not found errors
            elif isinstance(error, ElementNotFoundError) or "not found" in str(error).lower():
                handling_result.update(
                    await self._handle_element_not_found(browser, error, context)
                )

            # Handle authentication errors
            elif isinstance(error, AuthenticationError) or "auth" in str(error).lower():
                handling_result.update(
                    await self._handle_authentication_failure(browser, error, context)
                )

            # Handle unexpected UI changes
            elif isinstance(error, UIChangeError) or "ui" in str(error).lower():
                handling_result.update(await self._handle_ui_changes(browser, error, context))

            # Handle generic errors
            else:
                handling_result.update(await self._handle_generic_error(browser, error, context))

            # Set timestamp
            from datetime import datetime, timezone

            handling_result["timestamp"] = datetime.now(timezone.utc).isoformat()

            # Log comprehensive error context (without exposing secrets)
            self._log_error_context(handling_result, context)

        except Exception as e:
            logger.error("Error handling itself failed", error=str(e))
            handling_result["error_message"] += f" | Error handling failed: {e}"

        return handling_result

    async def _handle_network_timeout(
        self, browser: BrowserManagerInterface, error: Exception, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle network timeout scenarios during claiming."""
        result = {
            "recovery_attempted": True,
            "retry_recommended": True,
            "fallback_available": True,
        }

        try:
            logger.info("Handling network timeout error")

            # Wait before retry
            import asyncio

            await asyncio.sleep(5)

            # Test browser connection
            connection_ok = await self._test_browser_connection(browser)

            if connection_ok:
                result["recovery_success"] = True
                result["retry_recommended"] = True
                logger.info("Network connection restored, retry recommended")
            else:
                result["recovery_success"] = False
                result["fallback_available"] = True
                logger.warning("Network connection still unstable, fallback strategy recommended")

        except Exception as e:
            logger.error("Network timeout handling failed", error=str(e))
            result["recovery_success"] = False

        return result

    async def _handle_element_not_found(
        self, browser: BrowserManagerInterface, error: Exception, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle element not found errors with fallback strategies."""
        result = {
            "recovery_attempted": True,
            "retry_recommended": False,
            "fallback_available": True,
        }

        try:
            logger.info("Handling element not found error")

            # Try fallback selectors
            fallback_success = await self._try_fallback_selectors(browser, context)

            if fallback_success:
                result["recovery_success"] = True
                result["retry_recommended"] = True
                logger.info("Fallback selector found, retry with fallback recommended")
            else:
                result["recovery_success"] = False
                result["fallback_available"] = False
                logger.warning("No fallback selectors available")

        except Exception as e:
            logger.error("Element not found handling failed", error=str(e))
            result["recovery_success"] = False

        return result

    async def _handle_authentication_failure(
        self, browser: BrowserManagerInterface, error: Exception, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle authentication failure detection and re-authentication logic."""
        result = {
            "recovery_attempted": True,
            "retry_recommended": False,
            "fallback_available": False,
        }

        try:
            logger.info("Handling authentication failure")

            # Check if we're on login page or logged out
            auth_status = await self._check_authentication_status(browser)

            if not auth_status["authenticated"]:
                logger.warning("Authentication lost, re-authentication needed")
                result["retry_recommended"] = False  # Need re-auth, not just retry
                result["fallback_available"] = True  # Re-authentication is the fallback
            else:
                logger.info("Authentication appears valid, may be false positive")
                result["retry_recommended"] = True
                result["recovery_success"] = True

        except Exception as e:
            logger.error("Authentication failure handling failed", error=str(e))
            result["recovery_success"] = False

        return result

    async def _handle_ui_changes(
        self, browser: BrowserManagerInterface, error: Exception, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle unexpected UI change detection and recovery procedures."""
        result = {
            "recovery_attempted": True,
            "retry_recommended": False,
            "fallback_available": True,
        }

        try:
            logger.info("Handling unexpected UI changes")

            # Re-analyze interface to detect changes
            interface_analysis = await self.analyze_interface(browser)

            if interface_analysis["detection_confidence"] > 0.3:
                result["recovery_success"] = True
                result["retry_recommended"] = True
                logger.info("UI re-analysis successful, updated selectors available")
            else:
                result["recovery_success"] = False
                result["fallback_available"] = False
                logger.warning("UI changes too significant, manual intervention may be needed")

        except Exception as e:
            logger.error("UI change handling failed", error=str(e))
            result["recovery_success"] = False

        return result

    async def _handle_generic_error(
        self, browser: BrowserManagerInterface, error: Exception, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle generic errors with basic recovery attempts."""
        result = {
            "recovery_attempted": True,
            "retry_recommended": True,
            "fallback_available": True,
            "recovery_success": False,
        }

        try:
            logger.info("Handling generic error with basic recovery")

            # Basic recovery: wait and test browser
            import asyncio

            await asyncio.sleep(2)

            connection_ok = await self._test_browser_connection(browser)
            if connection_ok:
                result["recovery_success"] = True
                logger.info("Basic recovery successful")

        except Exception as e:
            logger.error("Generic error handling failed", error=str(e))

        return result

    async def _test_browser_connection(self, browser: BrowserManagerInterface) -> bool:
        """Test if browser connection is working."""
        try:
            # Simple test to verify browser responsiveness
            current_url = await browser.get_current_url()
            return current_url is not None
        except Exception:
            return False

    async def _try_fallback_selectors(
        self, browser: BrowserManagerInterface, context: Dict[str, Any]
    ) -> bool:
        """Try alternative selectors as fallback."""
        try:
            # Get fallback strategies
            for strategy in self.strategies[1:]:  # Skip primary strategy
                try:
                    detection_result = await strategy.detect_elements(browser)
                    if detection_result.get("found_elements"):
                        logger.info("Fallback selector strategy worked", strategy=strategy.name)
                        return True
                except Exception:
                    continue
            return False
        except Exception:
            return False

    async def _check_authentication_status(
        self, browser: BrowserManagerInterface
    ) -> Dict[str, Any]:
        """Check current authentication status."""
        auth_status = {
            "authenticated": False,
            "login_page_detected": False,
        }

        try:
            # Look for login indicators
            login_selectors = [".login-form", "#login", ".signin-btn", "[data-testid='login']"]

            for selector in login_selectors:
                try:
                    found = await browser.find_element(selector, timeout=2000)
                    if found:
                        auth_status["login_page_detected"] = True
                        break
                except Exception:
                    continue

            # If no login elements found, assume authenticated
            auth_status["authenticated"] = not auth_status["login_page_detected"]

        except Exception as e:
            logger.error("Authentication status check failed", error=str(e))

        return auth_status

    def _log_error_context(self, handling_result: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Log comprehensive error context while preserving security."""
        try:
            # Create safe context (remove sensitive information)
            safe_context = {}
            if context:
                for key, value in context.items():
                    if key.lower() in ["password", "token", "secret", "key", "credential"]:
                        safe_context[key] = "[REDACTED]"
                    else:
                        safe_context[key] = str(value)[:100]  # Limit length

            logger.error(
                "Comprehensive error context",
                error_type=handling_result.get("error_type"),
                recovery_attempted=handling_result.get("recovery_attempted"),
                recovery_success=handling_result.get("recovery_success"),
                context=safe_context,
            )

        except Exception as e:
            logger.debug("Error context logging failed", error=str(e))

    async def analyze_interface(self, browser: BrowserManagerInterface) -> Dict[str, Any]:
        """Analyze interface for reward detection opportunities.

        Args:
            browser: Browser implementation instance

        Returns:
            Interface analysis results with discovered selectors and states

        Raises:
            DetectionError: If interface analysis fails completely
        """
        analysis_result = {
            "selectors": [],
            "reward_states": {},
            "interface_elements": [],
            "detection_confidence": 0.0,
            "primary_strategy": None,
            "fallback_strategies": [],
            "analysis_timestamp": None,
        }

        try:
            logger.info("Starting interface analysis")

            # Try each strategy until we find working selectors
            successful_strategies = []

            for strategy in self.strategies:
                try:
                    logger.debug("Testing detection strategy", strategy=strategy.name)

                    result = await strategy.detect_elements(browser)

                    if result["found_elements"]:
                        successful_strategies.append(
                            {
                                "strategy": strategy.name,
                                "selectors": result["selectors"],
                                "element_count": len(result["found_elements"]),
                                "confidence": result.get("confidence", 0.5),
                            }
                        )

                        # Add to analysis result
                        analysis_result["selectors"].extend(result["selectors"])

                except Exception as e:
                    logger.warning("Strategy failed", strategy=strategy.name, error=str(e))
                    continue

            if successful_strategies:
                # Sort by confidence and element count
                successful_strategies.sort(
                    key=lambda x: (x["confidence"], x["element_count"]), reverse=True
                )

                analysis_result["primary_strategy"] = successful_strategies[0]["strategy"]
                analysis_result["fallback_strategies"] = [
                    s["strategy"] for s in successful_strategies[1:]
                ]
                analysis_result["detection_confidence"] = successful_strategies[0]["confidence"]

                # Analyze reward states using primary strategy
                reward_states = await self._analyze_reward_states(browser, successful_strategies[0])
                analysis_result["reward_states"] = reward_states

                logger.info(
                    "Interface analysis completed successfully",
                    primary_strategy=analysis_result["primary_strategy"],
                    selector_count=len(analysis_result["selectors"]),
                    confidence=analysis_result["detection_confidence"],
                )
            else:
                logger.warning("No successful detection strategies found")
                analysis_result["detection_confidence"] = 0.0

            # Set analysis timestamp
            from datetime import datetime, timezone

            analysis_result["analysis_timestamp"] = datetime.now(timezone.utc).isoformat()

            return analysis_result

        except Exception as e:
            logger.error("Interface analysis failed", error=str(e))
            raise DetectionError(f"Interface analysis failed: {e}")

    async def _analyze_reward_states(
        self, browser: BrowserManagerInterface, strategy_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze reward availability states using DOM inspection.

        Args:
            browser: Browser implementation instance
            strategy_result: Results from successful detection strategy

        Returns:
            Reward state analysis results
        """
        reward_states = {
            "claimable_rewards": [],
            "claimed_rewards": [],
            "unavailable_rewards": [],
            "total_found": 0,
            "analysis_method": strategy_result["strategy"],
        }

        try:
            # Use the specific strategy to analyze states
            strategy = self.strategy_factory.get_strategy_by_name(strategy_result["strategy"])

            if strategy and hasattr(strategy, "analyze_reward_states"):
                states = await strategy.analyze_reward_states(browser)
                reward_states.update(states)

            reward_states["total_found"] = (
                len(reward_states["claimable_rewards"])
                + len(reward_states["claimed_rewards"])
                + len(reward_states["unavailable_rewards"])
            )

            logger.info(
                "Reward states analyzed",
                claimable=len(reward_states["claimable_rewards"]),
                claimed=len(reward_states["claimed_rewards"]),
                total=reward_states["total_found"],
            )

        except Exception as e:
            logger.error("Reward state analysis failed", error=str(e))
            reward_states["error"] = str(e)

        return reward_states

    async def find_best_selector(
        self, browser: BrowserManagerInterface, target_type: str = "signin_button"
    ) -> Optional[str]:
        """Find the most reliable selector for a specific target.

        Args:
            browser: Browser implementation instance
            target_type: Type of element to find (signin_button, reward_claim, etc.)

        Returns:
            Best selector string or None if not found
        """
        try:
            for strategy in self.strategies:
                if hasattr(strategy, "get_selector_for_target"):
                    selector = await strategy.get_selector_for_target(browser, target_type)
                    if selector:
                        logger.info(
                            "Found selector for target",
                            target=target_type,
                            selector=selector[:50] + "..." if len(selector) > 50 else selector,
                            strategy=strategy.name,
                        )
                        return selector

            logger.warning("No selector found for target", target=target_type)
            return None

        except Exception as e:
            logger.error("Selector search failed", target=target_type, error=str(e))
            return None

    async def validate_selector_reliability(
        self, browser: BrowserManagerInterface, selector: str, attempts: int = 3
    ) -> Dict[str, Any]:
        """Validate selector reliability through multiple attempts.

        Args:
            browser: Browser implementation instance
            selector: CSS selector to validate
            attempts: Number of validation attempts

        Returns:
            Reliability validation results
        """
        validation_result = {
            "selector": selector,
            "successful_attempts": 0,
            "total_attempts": attempts,
            "reliability_score": 0.0,
            "average_find_time": 0.0,
            "errors": [],
        }

        try:
            find_times = []

            for attempt in range(attempts):
                try:
                    start_time = asyncio.get_event_loop().time()

                    # Attempt to find element using selector
                    # This will be implemented based on browser framework
                    found = await self._test_selector(browser, selector)

                    if found:
                        validation_result["successful_attempts"] += 1
                        find_times.append(asyncio.get_event_loop().time() - start_time)

                    # Small delay between attempts
                    await asyncio.sleep(0.5)

                except Exception as e:
                    validation_result["errors"].append(str(e))

            # Calculate reliability metrics
            validation_result["reliability_score"] = (
                validation_result["successful_attempts"] / attempts
            )

            if find_times:
                validation_result["average_find_time"] = sum(find_times) / len(find_times)

            logger.info(
                "Selector reliability validated",
                selector=selector[:30] + "..." if len(selector) > 30 else selector,
                reliability=validation_result["reliability_score"],
                avg_time=validation_result["average_find_time"],
            )

        except Exception as e:
            logger.error("Selector validation failed", selector=selector, error=str(e))
            validation_result["errors"].append(str(e))

        return validation_result

    async def _test_selector(self, browser: BrowserManagerInterface, selector: str) -> bool:
        """Test if a selector can find elements on current page.

        Args:
            browser: Browser implementation instance
            selector: CSS selector to test

        Returns:
            True if element found, False otherwise
        """
        try:
            found = await browser.find_element(selector, timeout=5000)
            logger.debug("Selector test result", selector=selector, found=found)
            return found

        except Exception as e:
            logger.debug("Selector test failed", selector=selector, error=str(e))
            return False
