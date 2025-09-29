# Testing Strategy

A comprehensive testing approach ensures the 70% success rate requirement while supporting educational goals and maintaining code quality.

## Testing Pyramid

```
        E2E Tests
       /          \
  Integration Tests  
 /                  \
Unit Tests    Browser Tests
```

## Test Organization

**Unit Tests:**
```
tests/unit/
├── test_orchestrator.py          # AutomationOrchestrator logic
├── test_browser_manager.py       # Browser management without actual browser
├── test_reward_detector.py       # Detection logic with mocked DOM
├── test_config_manager.py        # Configuration validation and access
├── test_state_manager.py         # State management and success calculation  
└── test_utilities.py             # Utility functions and helpers
```

**Integration Tests:**
```  
tests/integration/
├── test_browser_integration.py   # Real browser automation against test pages
├── test_hoyolab_integration.py   # Live HoYoLAB integration (careful with credentials)
└── test_github_actions_compat.py # GitHub Actions environment compatibility
```

**E2E Tests:**
```
tests/e2e/
├── test_full_workflow.py         # Complete automation workflow
├── test_failure_scenarios.py     # Error handling and recovery
└── test_manual_trigger.py        # Manual execution workflow
```

## Test Examples

**Unit Test Example:**
```python
import pytest
from unittest.mock import Mock, patch
from src.detection.detector import RewardDetector

class TestRewardDetector:
    @pytest.fixture
    def detector(self):
        config_manager = Mock()
        browser_manager = Mock()
        return RewardDetector(config_manager, browser_manager)
    
    def test_primary_selector_success(self, detector):
        # Mock successful element detection
        detector.browser_manager.find_element.return_value = Mock()
        detector.config_manager.get_selector_config.return_value = {
            'primary': '.test-selector',
            'fallback_1': '.fallback-1',
            'fallback_2': '.fallback-2'
        }
        
        result = detector.detect_reward_availability()
        
        assert result.success is True
        assert result.selector_used == 'primary'
        detector.browser_manager.find_element.assert_called_once_with('.test-selector')
```

**Integration Test Example:**
```python
import pytest
from playwright.async_api import async_playwright
from src.browser.playwright_impl import PlaywrightBrowserManager

@pytest.mark.asyncio
@pytest.mark.integration
async def test_browser_initialization():
    """Test browser manager can initialize and navigate to test page"""
    config_manager = Mock()
    config_manager.get_browser_config.return_value = {
        'headless': True,
        'user_agent': 'Mozilla/5.0 Test Agent'
    }
    
    browser_manager = PlaywrightBrowserManager(config_manager)
    
    try:
        await browser_manager.initialize_browser()
        await browser_manager.navigate_to('https://httpbin.org/html')
        
        title = await browser_manager.get_page_title()
        assert 'HTML' in title
        
    finally:
        await browser_manager.cleanup_browser()
```

**E2E Test Example:**
```python
import pytest
from src.automation.orchestrator import AutomationOrchestrator

@pytest.mark.e2e
@pytest.mark.slow
def test_complete_automation_workflow(test_credentials):
    """Test complete automation from start to finish"""
    # Use test account credentials (never production)
    orchestrator = AutomationOrchestrator(
        credentials=test_credentials,
        dry_run=True  # No actual reward claiming
    )
    
    result = orchestrator.execute_checkin()
    
    # Verify workflow completion regardless of HoYoLAB state
    assert result.completed is True
    assert result.duration_seconds < 120  # Under 2 minutes
    assert result.logs_created is True
    
    if result.success:
        assert result.rewards_detected is True
    else:
        assert result.error_message is not None
        assert result.screenshot_captured is True
```
