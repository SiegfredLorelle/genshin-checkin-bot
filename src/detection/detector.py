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

            logger.info(
                "Reward detector initialized", strategy_count=len(self.strategies)
            )

        except Exception as e:
            raise DetectionError(f"Failed to initialize reward detector: {e}")

    async def analyze_interface(
        self, browser: BrowserManagerInterface
    ) -> Dict[str, Any]:
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
                    logger.warning(
                        "Strategy failed", strategy=strategy.name, error=str(e)
                    )
                    continue

            if successful_strategies:
                # Sort by confidence and element count
                successful_strategies.sort(
                    key=lambda x: (x["confidence"], x["element_count"]), reverse=True
                )

                analysis_result["primary_strategy"] = successful_strategies[0][
                    "strategy"
                ]
                analysis_result["fallback_strategies"] = [
                    s["strategy"] for s in successful_strategies[1:]
                ]
                analysis_result["detection_confidence"] = successful_strategies[0][
                    "confidence"
                ]

                # Analyze reward states using primary strategy
                reward_states = await self._analyze_reward_states(
                    browser, successful_strategies[0]
                )
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

            analysis_result["analysis_timestamp"] = datetime.now(
                timezone.utc
            ).isoformat()

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
            strategy = self.strategy_factory.get_strategy_by_name(
                strategy_result["strategy"]
            )

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
                    selector = await strategy.get_selector_for_target(
                        browser, target_type
                    )
                    if selector:
                        logger.info(
                            "Found selector for target",
                            target=target_type,
                            selector=selector[:50] + "..."
                            if len(selector) > 50
                            else selector,
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
                validation_result["average_find_time"] = sum(find_times) / len(
                    find_times
                )

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

    async def _test_selector(
        self, browser: BrowserManagerInterface, selector: str
    ) -> bool:
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
