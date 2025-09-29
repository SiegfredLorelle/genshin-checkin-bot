# Browser Framework Selection Guide

This guide covers the decision matrix, switching procedures, and troubleshooting for browser automation frameworks.

## Framework Comparison Matrix

| Criteria | Playwright (Primary) | Selenium (Fallback) |
|----------|---------------------|---------------------|
| **Reliability** | ⭐⭐⭐⭐⭐ Superior | ⭐⭐⭐⭐ Good |
| **Async Support** | ⭐⭐⭐⭐⭐ Native | ⭐⭐ Limited |
| **Installation** | ⭐⭐⭐ Complex | ⭐⭐⭐⭐⭐ Simple |
| **Documentation** | ⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐⭐ Extensive |
| **Platform Support** | ⭐⭐⭐⭐ Wide | ⭐⭐⭐⭐⭐ Universal |
| **GitHub Actions** | ⭐⭐⭐⭐⭐ Optimized | ⭐⭐⭐⭐ Standard |
| **Learning Curve** | ⭐⭐⭐ Moderate | ⭐⭐⭐⭐ Gentle |

## When to Use Each Framework

### Use Playwright When:
- ✅ Setting up a new automation project
- ✅ Need superior reliability and stability
- ✅ Deploying to GitHub Actions (recommended)
- ✅ Working with complex async workflows
- ✅ Require advanced debugging capabilities

### Use Selenium When:
- ✅ Playwright installation fails on your platform
- ✅ Working in a restricted environment
- ✅ Team is already familiar with Selenium
- ✅ Need maximum platform compatibility
- ✅ Using legacy browser versions

## Framework Switching Procedures

### Automatic Fallback (Recommended)

The system automatically falls back to Selenium if Playwright fails:

```python
# This happens automatically in BrowserManager
browser_manager = BrowserManager(framework="playwright")
try:
    browser = await browser_manager.initialize()
except ImportError:
    # Automatically switches to Selenium
    print("Falling back to Selenium WebDriver")
```

### Manual Framework Selection

#### Option 1: Environment Variable
```bash
# In .env file
BROWSER_FRAMEWORK=selenium

# Or set temporarily
export BROWSER_FRAMEWORK=selenium
python -m src.automation.orchestrator
```

#### Option 2: Command Line
```bash
# For one-time execution
python -m src.automation.orchestrator --framework selenium

# For testing
python -m src.automation.orchestrator --framework selenium --dry-run
```

#### Option 3: Code Configuration
```python
from src.browser.manager import BrowserManager

# Explicit framework selection
browser_manager = BrowserManager(framework="selenium")
browser = await browser_manager.initialize()
```

## Installation Troubleshooting

### Playwright Issues

**Problem: Playwright installation fails**
```bash
# Solution 1: Manual browser installation
npx playwright install chromium

# Solution 2: System dependencies (Linux)
sudo npx playwright install-deps

# Solution 3: Use Selenium fallback
echo "BROWSER_FRAMEWORK=selenium" >> .env
```

**Problem: Browser won't launch**
```bash
# Check disk space (need ~1GB for browsers)
df -h

# Verify browser installation
playwright show-trace

# Try headless mode
echo "HEADLESS=true" >> .env
```

### Selenium Issues

**Problem: ChromeDriver not found**
```bash
# Selenium 4.15+ auto-manages ChromeDriver
pip install selenium --upgrade

# Manual ChromeDriver installation (if needed)
# Download from https://chromedriver.chromium.org
```

**Problem: Chrome browser not found**
```bash
# macOS: Install Chrome from Google
# Linux: sudo apt-get install google-chrome-stable
# Windows: Download from google.com/chrome
```

## Platform-Specific Considerations

### macOS
- **Playwright**: May require Xcode command line tools
- **Selenium**: Usually works out of the box
- **Recommendation**: Try Playwright first, fallback to Selenium

### Linux (Ubuntu/Debian)
- **Playwright**: Requires system dependencies
- **Selenium**: Needs Chrome/Chromium package
- **Recommendation**: Selenium for CI/CD, Playwright for development

### Windows
- **Playwright**: Good support with Windows PowerShell
- **Selenium**: Excellent compatibility
- **Recommendation**: Both work well, use preference

### GitHub Actions
- **Playwright**: Optimized with pre-installed browsers
- **Selenium**: Requires Chrome installation step
- **Recommendation**: Playwright for better performance

## Switching Checklist

When switching frameworks, verify:

- [ ] Framework dependencies installed (`pip list | grep playwright` or `pip list | grep selenium`)
- [ ] Browser/driver available (run `scripts/verify_dependencies.py`)
- [ ] Environment variable updated (check `.env` file)
- [ ] Test with dry run (`python -m src.automation.orchestrator --dry-run`)
- [ ] Check logs for framework initialization messages

## Performance Comparison

| Metric | Playwright | Selenium |
|--------|------------|----------|
| **Startup Time** | ~2-3 seconds | ~1-2 seconds |
| **Memory Usage** | ~150-200MB | ~100-150MB |
| **CPU Usage** | Low | Low |
| **Network Efficiency** | Excellent | Good |
| **Screenshot Speed** | Fast | Moderate |

## Debugging Framework Issues

### Enable Debug Logging
```bash
# In .env file
LOG_LEVEL=DEBUG
DEBUG_MODE=true

# Run with debug output
python -m src.automation.orchestrator --dry-run
```

### Check Framework Status
```bash
# Run verification script
python scripts/verify_dependencies.py

# Test specific framework
python -c "from src.browser.manager import BrowserManager; import asyncio; asyncio.run(BrowserManager('playwright').initialize())"
```

### Common Error Messages

**"No module named 'playwright'"**
- Solution: `pip install playwright`

**"Executable doesn't exist at ..."**
- Solution: `playwright install chromium`

**"ChromeDriver not found"**
- Solution: `pip install selenium --upgrade`

**"Chrome binary not found"**
- Solution: Install Google Chrome browser

## Framework Migration Guide

### From Selenium to Playwright
1. Install Playwright: `pip install playwright`
2. Install browsers: `playwright install chromium`
3. Update .env: `BROWSER_FRAMEWORK=playwright`
4. Test: `python scripts/verify_dependencies.py`

### From Playwright to Selenium
1. Install Selenium: `pip install selenium`
2. Update .env: `BROWSER_FRAMEWORK=selenium`
3. Test: `python scripts/verify_dependencies.py`

## Best Practices

1. **Use Automatic Fallback**: Let the system choose the best available framework
2. **Test Both Frameworks**: Ensure your automation works with both options
3. **Monitor Performance**: Check logs for framework-specific issues
4. **Keep Updated**: Regularly update framework dependencies
5. **Document Choice**: Record why you chose a specific framework for your environment

For additional support, check the troubleshooting section in README.md or run the dependency verification script.
