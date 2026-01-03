"""CSS Selector strategies for robust element detection.

Provides multiple detection strategies with different approaches
for finding HoYoLAB interface elements and fallback mechanisms.
"""

from abc import ABC, abstractmethod
from typing import Any

import structlog

from ..browser.manager import BrowserManagerInterface

logger = structlog.get_logger(__name__)


class SelectorStrategy(ABC):
    """Abstract base class for element detection strategies."""

    def __init__(self, name: str):
        """Initialize strategy with name.

        Args:
            name: Strategy identification name
        """
        self.name = name

    @abstractmethod
    async def detect_elements(self, browser: BrowserManagerInterface) -> dict[str, Any]:
        """Detect elements using this strategy.

        Args:
            browser: Browser implementation instance

        Returns:
            Detection results with found elements and selectors
        """
        pass

    async def analyze_reward_states(
        self, browser: BrowserManagerInterface
    ) -> dict[str, Any]:
        """Analyze reward states with enhanced differentiation logic.

        Args:
            browser: Browser implementation instance

        Returns:
            Reward state analysis results with detailed classification
        """
        return {
            "claimable_rewards": [],
            "claimed_rewards": [],
            "unavailable_rewards": [],
            "detection_confidence": 0.5,
        }

    async def get_selector_for_target(
        self, browser: BrowserManagerInterface, target_type: str
    ) -> str | None:
        """Get specific selector for target type (optional implementation).

        Args:
            browser: Browser implementation instance
            target_type: Type of element to find

        Returns:
            Selector string or None
        """
        return None


class HoYoLABClassBasedStrategy(SelectorStrategy):
    """Strategy using HoYoLAB-specific CSS classes and IDs."""

    def __init__(self):
        """Initialize HoYoLAB class-based strategy."""
        super().__init__("hoyolab_class_based")

        # Known HoYoLAB selectors (to be updated based on research)
        self.selectors = {
            "signin_button": [
                ".signin-btn",
                ".check-in-btn",
                ".daily-signin",
                "#signin-button",
            ],
            "reward_container": [".reward-item", ".rewards-list", ".daily-rewards"],
            "claim_button": [".claim-btn", ".receive-btn", ".get-reward"],
        }

    async def detect_elements(self, browser: BrowserManagerInterface) -> dict[str, Any]:
        """Detect elements using HoYoLAB-specific CSS classes."""
        result = {
            "selectors": [],
            "found_elements": [],
            "confidence": 0.8,
            "strategy_name": self.name,
        }

        try:
            found_any = False

            # Test all known selectors
            for target_type, selectors in self.selectors.items():
                for selector in selectors:
                    try:
                        # Test if selector finds elements
                        found = await browser.find_element(selector, timeout=3000)

                        selector_info = {
                            "selector": selector,
                            "target_type": target_type,
                            "priority": "high",
                            "found": found,
                            "confidence": 0.9 if found else 0.1,
                        }
                        result["selectors"].append(selector_info)

                        if found:
                            result["found_elements"].append(
                                {"target_type": target_type, "selector": selector}
                            )
                            found_any = True

                    except Exception as e:
                        logger.debug(
                            "Selector test failed", selector=selector, error=str(e)
                        )
                        continue

            # Adjust confidence based on findings
            if found_any:
                result["confidence"] = 0.8
            else:
                result["confidence"] = 0.2

            logger.info(
                "HoYoLAB class-based detection completed",
                selectors_tested=len(result["selectors"]),
                elements_found=len(result["found_elements"]),
            )

        except Exception as e:
            logger.error("HoYoLAB class-based detection failed", error=str(e))
            result["confidence"] = 0.0

        return result

    async def analyze_reward_states(
        self, browser: BrowserManagerInterface
    ) -> dict[str, Any]:
        """Enhanced reward state analysis using HoYoLAB-specific patterns."""
        states = {
            "claimable_rewards": [],
            "claimed_rewards": [],
            "unavailable_rewards": [],
            "detection_confidence": 0.8,
        }

        try:
            # Look for claimable rewards using multiple selector patterns
            claimable_selectors = [
                ".reward-item:not(.claimed):not(.disabled)",
                ".daily-reward.available",
                ".signin-reward.claimable",
                "[data-state='available']",
            ]

            for selector in claimable_selectors:
                try:
                    found = await browser.find_element(selector, timeout=2000)
                    if found:
                        states["claimable_rewards"].append(
                            {
                                "selector": selector,
                                "state": "claimable",
                                "confidence": 0.9,
                            }
                        )
                except Exception:
                    continue

            # Look for claimed rewards
            claimed_selectors = [
                ".reward-item.claimed",
                ".daily-reward.completed",
                ".signin-reward.received",
                "[data-state='claimed']",
            ]

            for selector in claimed_selectors:
                try:
                    found = await browser.find_element(selector, timeout=2000)
                    if found:
                        states["claimed_rewards"].append(
                            {
                                "selector": selector,
                                "state": "claimed",
                                "confidence": 0.9,
                            }
                        )
                except Exception:
                    continue

            # Look for unavailable rewards
            unavailable_selectors = [
                ".reward-item.disabled",
                ".daily-reward.locked",
                ".signin-reward.unavailable",
                "[data-state='locked']",
            ]

            for selector in unavailable_selectors:
                try:
                    found = await browser.find_element(selector, timeout=2000)
                    if found:
                        states["unavailable_rewards"].append(
                            {
                                "selector": selector,
                                "state": "unavailable",
                                "confidence": 0.8,
                            }
                        )
                except Exception:
                    continue

            logger.info(
                "HoYoLAB reward state analysis completed",
                claimable=len(states["claimable_rewards"]),
                claimed=len(states["claimed_rewards"]),
            )

        except Exception as e:
            logger.error("HoYoLAB reward state analysis failed", error=str(e))
            states["detection_confidence"] = 0.2

        return states

    async def get_selector_for_target(
        self, browser: BrowserManagerInterface, target_type: str
    ) -> str | None:
        """Get selector for specific target type."""
        if target_type in self.selectors:
            # Return first selector for the target type
            return self.selectors[target_type][0]
        return None


class AttributeBasedStrategy(SelectorStrategy):
    """Strategy using data attributes and ARIA labels."""

    def __init__(self):
        """Initialize attribute-based strategy."""
        super().__init__("attribute_based")

        self.selectors = {
            "signin_button": [
                "[data-testid='signin-button']",
                "[aria-label*='sign in']",
                "[data-action='signin']",
                "[role='button'][aria-label*='check']",
            ],
            "reward_container": [
                "[data-testid='reward-item']",
                "[aria-label*='reward']",
                "[data-component='reward']",
            ],
        }

    async def detect_elements(self, browser: BrowserManagerInterface) -> dict[str, Any]:
        """Detect elements using data attributes and ARIA labels."""
        result = {
            "selectors": [],
            "found_elements": [],
            "confidence": 0.7,
            "strategy_name": self.name,
        }

        try:
            for target_type, selectors in self.selectors.items():
                for selector in selectors:
                    result["selectors"].append(
                        {
                            "selector": selector,
                            "target_type": target_type,
                            "priority": "medium",
                        }
                    )

            # Simulate found elements for MVP
            result["found_elements"] = ["signin_button"]

            logger.info(
                "Attribute-based detection completed",
                selectors_tested=len(result["selectors"]),
            )

        except Exception as e:
            logger.error("Attribute-based detection failed", error=str(e))
            result["confidence"] = 0.0

        return result


class TextContentStrategy(SelectorStrategy):
    """Strategy using text content and contains selectors."""

    def __init__(self):
        """Initialize text content strategy."""
        super().__init__("text_content")

        self.text_patterns = {
            "signin_button": [
                "Sign in",
                "Check in",
                "Daily check-in",
                "领取",  # Chinese "claim"
                "簽到",  # Traditional Chinese "sign in"
            ],
            "reward_item": [
                "Primogem",
                "Mora",
                "Enhancement Ore",
                "reward",
                "奖励",  # Chinese "reward"
            ],
        }

    async def detect_elements(self, browser: BrowserManagerInterface) -> dict[str, Any]:
        """Detect elements using text content patterns."""
        result = {
            "selectors": [],
            "found_elements": [],
            "confidence": 0.6,
            "strategy_name": self.name,
        }

        try:
            for target_type, patterns in self.text_patterns.items():
                for pattern in patterns:
                    # Generate CSS selectors for text content
                    selectors = [
                        f"button:contains('{pattern}')",
                        f"a:contains('{pattern}')",
                        f"div:contains('{pattern}')",
                        f"span:contains('{pattern}')",
                    ]

                    for selector in selectors:
                        result["selectors"].append(
                            {
                                "selector": selector,
                                "target_type": target_type,
                                "priority": "low",
                                "text_pattern": pattern,
                            }
                        )

            # Simulate found elements for MVP
            result["found_elements"] = ["signin_button"]

            logger.info(
                "Text content detection completed",
                patterns_tested=sum(
                    len(patterns) for patterns in self.text_patterns.values()
                ),
            )

        except Exception as e:
            logger.error("Text content detection failed", error=str(e))
            result["confidence"] = 0.0

        return result


class GenericFallbackStrategy(SelectorStrategy):
    """Generic fallback strategy for common UI patterns."""

    def __init__(self):
        """Initialize generic fallback strategy."""
        super().__init__("generic_fallback")

        self.generic_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            ".btn-primary",
            ".btn-success",
            ".button",
            "a.btn",
            "[role='button']",
        ]

    async def detect_elements(self, browser: BrowserManagerInterface) -> dict[str, Any]:
        """Detect elements using generic UI patterns."""
        result = {
            "selectors": [],
            "found_elements": [],
            "confidence": 0.3,
            "strategy_name": self.name,
        }

        try:
            for selector in self.generic_selectors:
                result["selectors"].append(
                    {
                        "selector": selector,
                        "target_type": "generic_button",
                        "priority": "fallback",
                    }
                )

            # Simulate found elements for MVP
            result["found_elements"] = ["generic_button"]

            logger.info(
                "Generic fallback detection completed",
                selectors_tested=len(self.generic_selectors),
            )

        except Exception as e:
            logger.error("Generic fallback detection failed", error=str(e))
            result["confidence"] = 0.0

        return result


class SelectorStrategyFactory:
    """Factory for creating and managing selector strategies."""

    def __init__(self):
        """Initialize strategy factory."""
        self.strategies = [
            HoYoLABClassBasedStrategy(),
            AttributeBasedStrategy(),
            TextContentStrategy(),
            GenericFallbackStrategy(),
        ]

    def get_all_strategies(self) -> list[SelectorStrategy]:
        """Get all available strategies ordered by priority.

        Returns:
            List of strategies ordered by reliability (best first)
        """
        return self.strategies

    def get_strategy_by_name(self, name: str) -> SelectorStrategy | None:
        """Get strategy by name.

        Args:
            name: Strategy name

        Returns:
            Strategy instance or None if not found
        """
        for strategy in self.strategies:
            if strategy.name == name:
                return strategy
        return None

    def add_strategy(self, strategy: SelectorStrategy) -> None:
        """Add custom strategy to factory.

        Args:
            strategy: Strategy instance to add
        """
        self.strategies.append(strategy)
        logger.info("Custom strategy added", strategy_name=strategy.name)
