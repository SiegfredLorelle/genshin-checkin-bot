"""Unit tests for logging configuration and secret redaction."""

import os
from unittest.mock import MagicMock, patch

from src.utils.logging_config import configure_logging, get_logger, redact_secrets


class TestSecretRedaction:
    """Test cases for secret redaction functionality."""

    def test_redact_ltuid_in_event(self):
        """Test that ltuid values are redacted from event messages."""
        logger = None
        method_name = "info"
        event_dict = {
            "event": "Login attempt with ltuid=12345678 successful",
            "user": "test_user",
        }

        result = redact_secrets(logger, method_name, event_dict)

        assert "ltuid=***REDACTED***" in result["event"]
        assert "12345678" not in result["event"]

    def test_redact_ltoken_in_event(self):
        """Test that ltoken values are redacted from event messages."""
        event_dict = {
            "event": 'Auth with ltoken="abc123def456" completed',
            "timestamp": "2025-09-30T12:00:00Z",
        }

        result = redact_secrets(None, None, event_dict)

        assert 'ltoken="***REDACTED***"' in result["event"]
        assert "abc123def456" not in result["event"]

    def test_redact_multiple_secrets_in_event(self):
        """Test that multiple different secrets are redacted."""
        event_dict = {
            "event": "Config loaded: ltuid=123 ltoken=abc password=secret",
        }

        result = redact_secrets(None, None, event_dict)

        assert "ltuid=***REDACTED***" in result["event"]
        assert "ltoken=***REDACTED***" in result["event"]
        assert "password=***REDACTED***" in result["event"]
        assert "123" not in result["event"]
        assert "abc" not in result["event"]
        assert "secret" not in result["event"]

    def test_redact_secrets_in_other_fields(self):
        """Test that secrets are redacted from all string fields."""
        event_dict = {
            "event": "Authentication completed",
            "credentials": "ltuid=999888777",
            "debug_info": "token=super_secret_value",
            "numeric_field": 12345,  # Should not be processed
        }

        result = redact_secrets(None, None, event_dict)

        assert result["event"] == "Authentication completed"  # No secrets here
        assert result["credentials"] == "ltuid=***REDACTED***"
        assert result["debug_info"] == "token=***REDACTED***"
        assert result["numeric_field"] == 12345  # Unchanged

    def test_redact_case_insensitive(self):
        """Test that redaction works case-insensitively."""
        event_dict = {"event": "LTUID=123 LToken=abc Password=secret COOKIE=value"}

        result = redact_secrets(None, None, event_dict)

        assert "LTUID=***REDACTED***" in result["event"]
        assert "LToken=***REDACTED***" in result["event"]
        assert "Password=***REDACTED***" in result["event"]
        assert "COOKIE=***REDACTED***" in result["event"]

    def test_redact_various_formats(self):
        """Test redaction with different formatting patterns."""
        event_dict = {
            "event": 'ltuid: 123, "ltoken":"abc", password = secret, cookie="value"'
        }

        result = redact_secrets(None, None, event_dict)

        # Should redact all patterns
        assert "***REDACTED***" in result["event"]
        assert "123" not in result["event"]
        assert "abc" not in result["event"]

    def test_no_secrets_no_change(self):
        """Test that logs without secrets are unchanged."""
        event_dict = {
            "event": "Normal log message without secrets",
            "status": "success",
            "duration": "2.5s",
        }

        original = event_dict.copy()
        result = redact_secrets(None, None, event_dict)

        assert result == original


class TestLoggingConfiguration:
    """Test cases for logging configuration."""

    @patch("src.utils.logging_config.structlog")
    @patch("src.utils.logging_config.logging")
    def test_configure_logging_development_mode(self, mock_logging, mock_structlog):
        """Test logging configuration in development mode."""
        configure_logging(log_level="DEBUG", log_to_file=False, development_mode=True)

        # Should configure structlog with console renderer
        mock_structlog.configure.assert_called_once()
        call_args = mock_structlog.configure.call_args[1]

        # Check that processors include console renderer for development
        processors = call_args["processors"]
        assert any("ConsoleRenderer" in str(p) for p in processors)

    @patch("src.utils.logging_config.structlog")
    @patch("src.utils.logging_config.logging")
    def test_configure_logging_production_mode(self, mock_logging, mock_structlog):
        """Test logging configuration in production mode."""
        configure_logging(log_level="INFO", log_to_file=False, development_mode=False)

        mock_structlog.configure.assert_called_once()
        call_args = mock_structlog.configure.call_args[1]

        # Check that processors include JSON renderer for production
        processors = call_args["processors"]
        assert any("JSONRenderer" in str(p) for p in processors)

    @patch("src.utils.logging_config.Path")
    @patch("src.utils.logging_config.logging")
    @patch("src.utils.logging_config.structlog")
    def test_configure_logging_with_file_handlers(
        self, mock_structlog, mock_logging, mock_path
    ):
        """Test logging configuration with file handlers."""
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance

        configure_logging(
            log_level="INFO",
            log_to_file=True,
            log_dir="test_logs",
            development_mode=False,
        )

        # Should create log directory
        mock_path.assert_called_with("test_logs")
        mock_path_instance.mkdir.assert_called_with(exist_ok=True)

        # Should add file handlers to root logger
        mock_root_logger = mock_logging.getLogger.return_value
        assert mock_root_logger.addHandler.call_count >= 2  # app and error handlers

    @patch.dict(os.environ, {"LOG_LEVEL": "WARNING", "DEBUG_MODE": "true"})
    @patch("src.utils.logging_config.configure_logging")
    def test_auto_configure_from_environment(self, mock_configure):
        """Test that auto-configuration reads from environment variables."""
        # Import the module to trigger auto-configuration
        from src.utils import logging_config

        # Re-run auto-configure to test with our environment
        logging_config._auto_configure()

        # Should have called configure_logging with environment values
        mock_configure.assert_called_with(log_level="WARNING", development_mode=True)

    def test_get_logger_returns_structlog_instance(self):
        """Test that get_logger returns a structlog logger."""
        with patch("src.utils.logging_config.structlog") as mock_structlog:
            mock_logger = MagicMock()
            mock_structlog.get_logger.return_value = mock_logger

            result = get_logger("test_module")

            mock_structlog.get_logger.assert_called_once_with("test_module")
            assert result == mock_logger


class TestLoggingIntegration:
    """Integration tests for logging functionality."""

    def test_redaction_in_configure_logging(self):
        """Test that redaction is included in logging configuration."""
        with patch("src.utils.logging_config.structlog") as mock_structlog:
            configure_logging(development_mode=False)

            call_args = mock_structlog.configure.call_args[1]
            processors = call_args["processors"]

            # Should include redact_secrets processor
            assert redact_secrets in processors

    @patch("src.utils.logging_config.structlog")
    def test_logging_levels_properly_configured(self, mock_structlog):
        """Test that logging levels are properly configured."""
        configure_logging(log_level="ERROR")

        # Should create filtering bound logger with ERROR level
        call_args = mock_structlog.configure.call_args[1]
        wrapper_class = call_args["wrapper_class"]

        # The wrapper should be configured for ERROR level filtering
        assert wrapper_class is not None
