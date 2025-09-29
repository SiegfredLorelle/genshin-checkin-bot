"""Unit tests for StateManager."""

import json
import tempfile
from datetime import datetime, timedelta, timezone
from unittest.mock import mock_open, patch

import pytest

from src.state.manager import StateManager
from src.utils.exceptions import StateManagementError


class TestStateManager:
    """Test cases for StateManager class."""

    @pytest.fixture
    def temp_history_file(self):
        """Create temporary history file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
            return f.name

    @pytest.fixture
    def state_manager(self, temp_history_file):
        """Create state manager with temporary file."""
        return StateManager(history_file=temp_history_file)

    @pytest.mark.asyncio
    async def test_initialize_creates_directory(self, state_manager):
        """Test initialization creates necessary directories."""
        await state_manager.initialize()

        assert state_manager.history_file.parent.exists()
        assert state_manager.history_file.exists()

    def test_get_current_timestamp(self, state_manager):
        """Test timestamp generation."""
        timestamp = state_manager.get_current_timestamp()

        # Should be valid ISO format
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        assert isinstance(parsed, datetime)
        assert parsed.tzinfo is not None

    @pytest.mark.asyncio
    async def test_log_execution_result(self, state_manager):
        """Test logging execution results."""
        await state_manager.initialize()

        result = {"success": True, "step": "authentication", "details": "test details"}

        await state_manager.log_execution_result(result)

        # Verify file was written
        with open(state_manager.history_file, "r") as f:
            logged_data = json.loads(f.read().strip())

        assert logged_data["success"] is True
        assert logged_data["step"] == "authentication"
        assert "timestamp" in logged_data

    @pytest.mark.asyncio
    async def test_log_execution_result_adds_timestamp(self, state_manager):
        """Test logging automatically adds timestamp if missing."""
        await state_manager.initialize()

        result = {"success": False, "error": "test error"}

        await state_manager.log_execution_result(result)

        with open(state_manager.history_file, "r") as f:
            logged_data = json.loads(f.read().strip())

        assert "timestamp" in logged_data

    @pytest.mark.asyncio
    async def test_get_execution_history_empty(self, state_manager):
        """Test getting history from empty file."""
        await state_manager.initialize()

        history = await state_manager.get_execution_history()

        assert history == []

    @pytest.mark.asyncio
    async def test_get_execution_history_with_data(self, state_manager):
        """Test getting history with existing data."""
        await state_manager.initialize()

        # Add test data
        test_entries = [
            {"timestamp": "2023-01-01T12:00:00+00:00", "success": True},
            {"timestamp": "2023-01-01T13:00:00+00:00", "success": False},
            {"timestamp": "2023-01-01T14:00:00+00:00", "success": True},
        ]

        for entry in test_entries:
            await state_manager.log_execution_result(entry)

        history = await state_manager.get_execution_history()

        assert len(history) == 3
        # Should be sorted by timestamp (most recent first)
        assert history[0]["timestamp"] == "2023-01-01T14:00:00+00:00"
        assert history[2]["timestamp"] == "2023-01-01T12:00:00+00:00"

    @pytest.mark.asyncio
    async def test_get_execution_history_with_limit(self, state_manager):
        """Test getting limited history."""
        await state_manager.initialize()

        # Add test data
        for i in range(5):
            entry = {"timestamp": f"2023-01-01T{12+i:02d}:00:00+00:00", "success": True}
            await state_manager.log_execution_result(entry)

        history = await state_manager.get_execution_history(limit=3)

        assert len(history) == 3

    @pytest.mark.asyncio
    async def test_get_execution_history_handles_invalid_json(self, state_manager):
        """Test history reading handles invalid JSON lines."""
        await state_manager.initialize()

        # Write valid and invalid JSON
        with open(state_manager.history_file, "w") as f:
            f.write('{"valid": "json"}\n')
            f.write("invalid json line\n")
            f.write('{"another": "valid"}\n')

        history = await state_manager.get_execution_history()

        # Should only return valid entries
        assert len(history) == 2

    @pytest.mark.asyncio
    async def test_calculate_success_rate_empty_history(self, state_manager):
        """Test success rate calculation with empty history."""
        await state_manager.initialize()

        stats = await state_manager.calculate_success_rate(days=7)

        assert stats["total_executions"] == 0
        assert stats["successful_executions"] == 0
        assert stats["success_rate"] == 0.0
        assert stats["period_days"] == 7

    @pytest.mark.asyncio
    async def test_calculate_success_rate_with_data(self, state_manager):
        """Test success rate calculation with historical data."""
        await state_manager.initialize()

        # Create test data spanning multiple days
        now = datetime.now(timezone.utc)
        test_entries = [
            {"timestamp": now.isoformat(), "success": True},
            {"timestamp": now.isoformat(), "success": True},
            {"timestamp": now.isoformat(), "success": False},
            {"timestamp": now.isoformat(), "success": True},
        ]

        for entry in test_entries:
            await state_manager.log_execution_result(entry)

        stats = await state_manager.calculate_success_rate(days=1)

        assert stats["total_executions"] == 4
        assert stats["successful_executions"] == 3
        assert stats["success_rate"] == 75.0

    @pytest.mark.asyncio
    async def test_get_last_execution_result(self, state_manager):
        """Test getting most recent execution result."""
        await state_manager.initialize()

        # Add test data
        await state_manager.log_execution_result(
            {"timestamp": "2023-01-01T12:00:00+00:00", "success": False}
        )
        await state_manager.log_execution_result(
            {"timestamp": "2023-01-01T13:00:00+00:00", "success": True}
        )

        last_result = await state_manager.get_last_execution_result()

        assert last_result is not None
        assert last_result["success"] is True
        assert last_result["timestamp"] == "2023-01-01T13:00:00+00:00"

    @pytest.mark.asyncio
    async def test_get_last_execution_result_empty(self, state_manager):
        """Test getting last result when no history exists."""
        await state_manager.initialize()

        last_result = await state_manager.get_last_execution_result()

        assert last_result is None

    @pytest.mark.asyncio
    async def test_cleanup_old_logs(self, state_manager):
        """Test cleaning up old log entries."""
        await state_manager.initialize()

        # Mock file operations to make test faster
        now = datetime.now(timezone.utc)
        old_date = now - timedelta(days=20)  # Old entry
        recent_date = now - timedelta(days=5)  # Recent entry

        # Mock history data
        mock_history = [
            {"timestamp": old_date.isoformat(), "success": True},
            {"timestamp": recent_date.isoformat(), "success": True},
            {"timestamp": now.isoformat(), "success": False},
        ]

        # Mock get_execution_history to return our test data
        with patch.object(
            state_manager, "get_execution_history", return_value=mock_history
        ):
            # Mock file write operations
            with patch("builtins.open", mock_open()) as mock_file:
                # Clean up logs older than 15 days
                await state_manager.cleanup_old_logs(keep_days=15)

                # Verify file was written (indicating cleanup occurred)
                mock_file.assert_called_once()

        # Test should complete quickly without actual file I/O

    @pytest.mark.asyncio
    async def test_cleanup_old_logs_handles_invalid_timestamps(self, state_manager):
        """Test cleanup handles invalid timestamps gracefully."""
        await state_manager.initialize()

        # Mock invalid history data instead of writing to actual file
        invalid_history = [
            {"timestamp": "invalid-timestamp", "success": True},
            {"no_timestamp": True},
            {"timestamp": datetime.now(timezone.utc).isoformat(), "success": True},
        ]

        # Mock get_execution_history to return test data
        with patch.object(
            state_manager, "get_execution_history", return_value=invalid_history
        ):
            # Mock file operations
            with patch("builtins.open", mock_open()):
                # Should not crash with invalid data
                await state_manager.cleanup_old_logs(keep_days=30)

        # Test completes without actual file operations

    @pytest.mark.asyncio
    async def test_log_execution_result_failure_handling(self, state_manager):
        """Test handling of logging failures."""
        # Use a read-only file to force write failure
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = PermissionError("Permission denied")

            with pytest.raises(StateManagementError):
                await state_manager.log_execution_result({"success": True})

    @pytest.mark.asyncio
    async def test_get_execution_history_failure_handling(self, state_manager):
        """Test handling of history reading failures."""
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = PermissionError("Permission denied")

            with pytest.raises(StateManagementError):
                await state_manager.get_execution_history()

    @pytest.mark.asyncio
    async def test_calculate_success_rate_handles_malformed_dates(self, state_manager):
        """Test success rate calculation handles malformed timestamps."""
        await state_manager.initialize()

        # Write entries with various timestamp formats
        with open(state_manager.history_file, "w") as f:
            f.write('{"timestamp": "2023-01-01T12:00:00Z", "success": true}\n')
            f.write('{"timestamp": "invalid-date", "success": true}\n')
            f.write('{"no_timestamp": true}\n')
            timestamp = datetime.now(timezone.utc).isoformat()
            f.write(f'{{"timestamp": "{timestamp}", "success": false}}\n')

        stats = await state_manager.calculate_success_rate(days=7)

        # Should process valid entries only
        assert stats["total_executions"] >= 1
