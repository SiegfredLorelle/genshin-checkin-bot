"""Unit tests for ConfigurationManager."""

from unittest.mock import MagicMock, patch

import pytest

from src.config.manager import ConfigurationManager, HoYoLABCredentials
from src.utils.exceptions import ConfigurationError


class TestConfigurationManager:
    """Test cases for ConfigurationManager class."""

    @pytest.fixture
    def config_manager(self):
        """Create configuration manager for testing."""
        return ConfigurationManager()

    def test_get_hoyolab_url_default(self, config_manager):
        """Test getting default HoYoLAB URL."""
        with patch("decouple.config") as mock_config:
            mock_config.return_value = (
                "https://act.hoyolab.com/ys/event/signin-sea-v3/index.html"
            )

            url = config_manager.get_hoyolab_url()

            assert "hoyolab.com" in url
            assert "signin" in url

    def test_get_hoyolab_url_custom(self, config_manager):
        """Test getting custom HoYoLAB URL from environment."""
        with patch("src.config.manager.config") as mock_config:
            mock_config.return_value = "https://custom.hoyolab.url"

            url = config_manager.get_hoyolab_url()

            assert url == "https://custom.hoyolab.url"

    def test_get_hoyolab_credentials_from_env(self, config_manager):
        """Test getting credentials from environment variables."""
        with patch("src.config.manager.config") as mock_config:
            mock_config.side_effect = lambda key, default=None: {
                "HOYOLAB_USERNAME": "test@example.com",
                "HOYOLAB_PASSWORD": "test_password",
            }.get(key, default)

            credentials = config_manager.get_hoyolab_credentials()

            assert credentials.username == "test@example.com"
            assert credentials.password == "test_password"

    def test_get_hoyolab_credentials_missing(self, config_manager):
        """Test error when credentials are missing."""
        with patch("src.config.manager.config") as mock_config:
            mock_config.return_value = None

            with pytest.raises(ConfigurationError) as exc_info:
                config_manager.get_hoyolab_credentials()

            assert "HOYOLAB_USERNAME and HOYOLAB_PASSWORD are required" in str(
                exc_info.value
            )

    def test_get_hoyolab_credentials_cached(self, config_manager):
        """Test that credentials are cached after first load."""
        with patch("src.config.manager.config") as mock_config:
            mock_config.side_effect = lambda key, default=None: {
                "HOYOLAB_USERNAME": "cached@example.com",
                "HOYOLAB_PASSWORD": "cached_password",
            }.get(key, default)

            # First call should load credentials
            credentials1 = config_manager.get_hoyolab_credentials()
            credentials2 = config_manager.get_hoyolab_credentials()
            credentials3 = config_manager.get_hoyolab_credentials()

            # Should return same cached instance
            assert credentials1 is credentials2 is credentials3
            assert credentials1.username == "cached@example.com"

    def test_get_browser_config_defaults(self, config_manager):
        """Test getting browser configuration with defaults."""
        with patch("decouple.config") as mock_config:
            mock_config.side_effect = lambda key, default=None, cast=None: {
                "BROWSER_HEADLESS": True,
                "BROWSER_TIMEOUT": 30000,
                "BROWSER_WIDTH": 1920,
                "BROWSER_HEIGHT": 1080,
            }.get(key, default)

            config = config_manager.get_browser_config()

            assert config["headless"] is True
            assert config["timeout"] == 30000
            assert config["viewport"]["width"] == 1920
            assert config["viewport"]["height"] == 1080
            assert "user_agent" in config

    def test_get_detection_config(self, config_manager):
        """Test getting detection configuration."""
        with patch("src.config.manager.config") as mock_config:
            mock_config.side_effect = lambda key, default=None, cast=None: {
                "DETECTION_WAIT_TIMEOUT": 15000,
                "DETECTION_RETRY_ATTEMPTS": 5,
                "DETECTION_SCREENSHOT": False,
            }.get(key, default)

            config = config_manager.get_detection_config()

            assert config["wait_timeout"] == 15000
            assert config["retry_attempts"] == 5
            assert config["screenshot_on_failure"] is False
            assert "primary_selectors" in config

    def test_get_timing_config(self, config_manager):
        """Test getting timing configuration."""
        with patch("src.config.manager.config") as mock_config:
            mock_config.side_effect = lambda key, default=None, cast=None: {
                "TIMING_PAGE_LOAD": 3000,
                "TIMING_CLICK_DELAY": 1500,
                "TIMING_VARIANCE": 0.4,
            }.get(key, default)

            config = config_manager.get_timing_config()

            assert config["page_load_delay"] == 3000
            assert config["click_delay"] == 1500
            assert config["random_variance"] == 0.4

    def test_redact_secrets(self, config_manager):
        """Test secret redaction functionality."""
        data = {
            "username": "testuser",
            "password": "secret123",
            "normal_field": "normal_value",
            "api_key": "key_secret",
            "short_secret": "abc",
        }

        redacted = config_manager.redact_secrets(data)

        assert redacted["username"] == "testuser"  # Not a secret pattern
        assert "***REDACTED***" in redacted["password"]
        assert redacted["normal_field"] == "normal_value"
        assert redacted["api_key"] == "key_***REDACTED***"
        assert redacted["short_secret"] == "***REDACTED***"

    def test_validate_environment_success(self, config_manager):
        """Test successful environment validation."""
        with patch.object(
            config_manager, "get_hoyolab_credentials"
        ) as mock_creds, patch.object(
            config_manager, "get_browser_config"
        ) as mock_browser, patch.object(
            config_manager, "get_detection_config"
        ) as mock_detection:
            mock_creds.return_value = MagicMock()
            mock_browser.return_value = {}
            mock_detection.return_value = {}

            result = config_manager.validate_environment()

            assert result is True

    def test_validate_environment_failure(self, config_manager):
        """Test environment validation failure."""
        with patch.object(config_manager, "get_hoyolab_credentials") as mock_creds:
            mock_creds.side_effect = ConfigurationError("Credentials missing")

            result = config_manager.validate_environment()

            assert result is False


class TestHoYoLABCredentials:
    """Test cases for HoYoLABCredentials dataclass."""

    def test_credentials_creation(self):
        """Test creating credentials object."""
        credentials = HoYoLABCredentials(
            username="test@example.com", password="test_password"
        )

        assert credentials.username == "test@example.com"
        assert credentials.password == "test_password"
