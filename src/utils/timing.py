"""Anti-bot timing utilities for human-like automation behavior.

Provides timing functions with randomization to avoid detection
and simulate natural human interaction patterns.
"""

import asyncio
import random
from typing import Union

import structlog

logger = structlog.get_logger(__name__)


class TimingUtils:
    """Anti-bot timing utilities with human-like delays."""

    def __init__(self, base_variance: float = 0.3):
        """Initialize timing utilities.

        Args:
            base_variance: Default variance factor for timing randomization (0.0-1.0)
        """
        self.base_variance = max(0.0, min(1.0, base_variance))

    async def human_delay(
        self, base_ms: Union[int, float], variance: float = None
    ) -> None:
        """Add human-like delay with randomization.

        Args:
            base_ms: Base delay in milliseconds
            variance: Variance factor (0.0-1.0), uses base_variance if None
        """
        if variance is None:
            variance = self.base_variance

        # Calculate randomized delay
        variance_amount = base_ms * variance
        delay_ms = base_ms + random.uniform(-variance_amount, variance_amount)
        delay_ms = max(100, delay_ms)  # Minimum 100ms delay

        delay_seconds = delay_ms / 1000.0

        logger.debug(
            "Human delay applied",
            base_ms=base_ms,
            actual_ms=delay_ms,
            variance_used=variance,
        )

        await asyncio.sleep(delay_seconds)

    async def page_load_delay(self) -> None:
        """Standard delay for page loading."""
        await self.human_delay(2000, variance=0.4)

    async def click_delay(self) -> None:
        """Standard delay before/after clicks."""
        await self.human_delay(1000, variance=0.5)

    async def typing_delay(self) -> None:
        """Standard delay between keystrokes."""
        await self.human_delay(100, variance=0.8)

    async def navigation_delay(self) -> None:
        """Standard delay for navigation operations."""
        await self.human_delay(3000, variance=0.3)

    async def random_pause(self, min_ms: int = 500, max_ms: int = 2000) -> None:
        """Random pause within specified range.

        Args:
            min_ms: Minimum delay in milliseconds
            max_ms: Maximum delay in milliseconds
        """
        delay_ms = random.randint(min_ms, max_ms)
        await asyncio.sleep(delay_ms / 1000.0)

        logger.debug("Random pause applied", delay_ms=delay_ms)

    def get_human_typing_intervals(self, text_length: int) -> list:
        """Generate human-like typing intervals for text input.

        Args:
            text_length: Length of text to be typed

        Returns:
            List of delays in milliseconds for each character
        """
        intervals = []

        for i in range(text_length):
            # Base typing speed: 150-300ms per character
            base_interval = random.randint(150, 300)

            # Add occasional longer pauses (thinking/hesitation)
            if random.random() < 0.1:  # 10% chance
                base_interval += random.randint(500, 1500)

            intervals.append(base_interval)

        return intervals

    async def simulate_reading_time(self, content_length: int) -> None:
        """Simulate time needed to read content.

        Args:
            content_length: Approximate length of content (characters or words)
        """
        # Average reading speed: ~200-250 words per minute
        # Assume ~5 characters per word
        words = max(1, content_length // 5)
        reading_time_seconds = (words / 225) * 60  # 225 WPM average

        # Add some variance and minimum time
        reading_time_seconds = max(1.0, reading_time_seconds)
        reading_time_ms = reading_time_seconds * 1000

        await self.human_delay(reading_time_ms, variance=0.4)

        logger.debug(
            "Reading time simulated",
            words=words,
            reading_time_seconds=reading_time_seconds,
        )


# Global instance for convenience
timing = TimingUtils()


# Convenience functions
async def human_delay(base_ms: Union[int, float], variance: float = 0.3) -> None:
    """Convenience function for human-like delay."""
    await timing.human_delay(base_ms, variance)


async def page_load_delay() -> None:
    """Convenience function for page load delay."""
    await timing.page_load_delay()


async def click_delay() -> None:
    """Convenience function for click delay."""
    await timing.click_delay()


async def typing_delay() -> None:
    """Convenience function for typing delay."""
    await timing.typing_delay()


async def navigation_delay() -> None:
    """Convenience function for navigation delay."""
    await timing.navigation_delay()


async def random_pause(min_ms: int = 500, max_ms: int = 2000) -> None:
    """Convenience function for random pause."""
    await timing.random_pause(min_ms, max_ms)
