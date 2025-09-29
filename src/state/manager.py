"""State Manager for execution logging and result tracking.

Provides execution history management, success rate calculations,
and persistent state tracking for automation workflow analysis.
"""

import asyncio
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

from ..utils.exceptions import StateManagementError

logger = structlog.get_logger(__name__)


class StateManager:
    """Execution logging and result tracking for workflow analysis."""

    def __init__(self, history_file: str = "logs/execution_history.jsonl"):
        """Initialize state manager.

        Args:
            history_file: Path to execution history log file
        """
        self.history_file = Path(history_file)
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Initialize state manager and ensure log directory exists."""
        try:
            # Ensure logs directory exists
            self.history_file.parent.mkdir(parents=True, exist_ok=True)

            # Create history file if it doesn't exist
            if not self.history_file.exists():
                self.history_file.touch()
                logger.info("Created execution history file", path=str(self.history_file))

            logger.info("State manager initialized successfully")

        except Exception as e:
            raise StateManagementError(f"Failed to initialize state manager: {e}")

    def get_current_timestamp(self) -> str:
        """Get current UTC timestamp in ISO format.

        Returns:
            ISO format timestamp string
        """
        return datetime.now(timezone.utc).isoformat()

    async def log_execution_result(self, result: Dict[str, Any]) -> None:
        """Log execution result to history file.

        Args:
            result: Execution result dictionary

        Raises:
            StateManagementError: If logging fails
        """
        async with self._lock:
            try:
                # Ensure timestamp is present
                if "timestamp" not in result:
                    result["timestamp"] = self.get_current_timestamp()

                # Add to history file (JSONL format)
                with open(self.history_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(result) + "\n")

                logger.info(
                    "Execution result logged",
                    success=result.get("success", False),
                    timestamp=result["timestamp"],
                )

            except Exception as e:
                raise StateManagementError(f"Failed to log execution result: {e}")

    async def get_execution_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get execution history from log file.

        Args:
            limit: Maximum number of records to return (most recent first)

        Returns:
            List of execution result dictionaries

        Raises:
            StateManagementError: If reading history fails
        """
        async with self._lock:
            try:
                if not self.history_file.exists():
                    return []

                history = []
                with open(self.history_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                history.append(json.loads(line))
                            except json.JSONDecodeError:
                                logger.warning("Skipping invalid JSON line in history")

                # Sort by timestamp (most recent first)
                history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

                # Apply limit if specified
                if limit:
                    history = history[:limit]

                return history

            except Exception as e:
                raise StateManagementError(f"Failed to read execution history: {e}")

    async def calculate_success_rate(self, days: int = 7) -> Dict[str, Any]:
        """Calculate success rate over specified period.

        Args:
            days: Number of days to analyze (default: 7)

        Returns:
            Success rate statistics
        """
        try:
            history = await self.get_execution_history()

            if not history:
                return {
                    "total_executions": 0,
                    "successful_executions": 0,
                    "success_rate": 0.0,
                    "period_days": days,
                    "analysis_timestamp": self.get_current_timestamp(),
                }

            # Filter by date range
            cutoff_date = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            ) - timedelta(days=days)

            filtered_history = []
            for record in history:
                try:
                    record_date = datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))
                    if record_date >= cutoff_date:
                        filtered_history.append(record)
                except (KeyError, ValueError):
                    continue

            total = len(filtered_history)
            successful = sum(1 for record in filtered_history if record.get("success", False))

            success_rate = (successful / total * 100) if total > 0 else 0.0

            stats = {
                "total_executions": total,
                "successful_executions": successful,
                "success_rate": round(success_rate, 2),
                "period_days": days,
                "analysis_timestamp": self.get_current_timestamp(),
            }

            logger.info("Success rate calculated", **stats)
            return stats

        except Exception as e:
            raise StateManagementError(f"Failed to calculate success rate: {e}")

    async def get_last_execution_result(self) -> Optional[Dict[str, Any]]:
        """Get the most recent execution result.

        Returns:
            Most recent execution result or None if no history
        """
        try:
            history = await self.get_execution_history(limit=1)
            return history[0] if history else None

        except Exception as e:
            logger.error("Failed to get last execution result", error=str(e))
            return None

    async def cleanup_old_logs(self, keep_days: int = 30) -> None:
        """Remove old log entries to prevent file growth.

        Args:
            keep_days: Number of days of history to retain
        """
        async with self._lock:
            try:
                history = await self.get_execution_history()

                if not history:
                    return

                # Filter to keep only recent entries
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=keep_days)

                filtered_history = []
                for record in history:
                    try:
                        record_date = datetime.fromisoformat(
                            record["timestamp"].replace("Z", "+00:00")
                        )
                        if record_date >= cutoff_date:
                            filtered_history.append(record)
                    except (KeyError, ValueError):
                        continue

                # Rewrite file with filtered history
                with open(self.history_file, "w", encoding="utf-8") as f:
                    for record in reversed(filtered_history):  # Maintain chronological order
                        f.write(json.dumps(record) + "\n")

                removed_count = len(history) - len(filtered_history)
                logger.info(
                    "Cleaned up old log entries",
                    removed=removed_count,
                    retained=len(filtered_history),
                )

            except Exception as e:
                logger.error("Failed to cleanup old logs", error=str(e))
