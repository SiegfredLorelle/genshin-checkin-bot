# Dependency Resolution and Troubleshooting Guide

This document covers version conflicts, platform-specific issues, and browser automation framework switching procedures.

## Browser Framework Decision Matrix

| Criteria | Playwright | Selenium WebDriver | Recommendation |
|----------|------------|-------------------|----------------|
| **Reliability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Use Playwright |
| **Async Support** | ⭐⭐⭐⭐⭐ | ⭐⭐ | Use Playwright |
| **Platform Support** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Use Selenium for edge cases |
| **Setup Complexity** | ⭐⭐⭐ | ⭐⭐⭐⭐ | Use Playwright |
| **Documentation** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Use Selenium for learning |
| **Debugging Tools** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Use Playwright |

### When to Use Selenium Fallback

1. **Playwright Installation Fails**: Missing system dependencies
2. **Corporate Environments**: Restricted browser installation
3. **ARM64/M1 Mac Issues**: Architecture compatibility problems
4. **Educational Purposes**: Learning widely-documented patterns

## Known Version Conflicts and Resolutions

### Python Version Conflicts

**Issue**: `playwright` requires Python 3.8+, `mypy` needs 3.7+
```bash
# Error: No matching distribution found for playwright
```

**Resolution**:
```bash
# Check Python version
python3 --version

# If < 3.8, upgrade Python or use Selenium fallback
echo "BROWSER_FRAMEWORK=selenium" >> .env
```

### Dependency Conflicts

**Issue**: `pytest-playwright` conflicts with older `pytest` versions
```bash
# Error: pytest-playwright 0.4.0 has requirement pytest>=6.0.0
```

**Resolution**:
```bash
# Force upgrade pytest
pip install --upgrade pytest>=7.4.0

# Or clean install
pip install -r requirements.txt --force-reinstall
```

**Issue**: `structlog` conflicts with older `logging` libraries
```bash
# Error: Cannot import name 'Processor' from 'structlog.types'
```

**Resolution**:
```bash
# Upgrade structlog
pip install --upgrade structlog>=23.1.0

# Clear cache if needed
pip cache purge
```

## Platform-Specific Issues

### macOS

**Issue**: Playwright browser installation fails on M1/M2 Macs
```bash
# Error: Failed to download Chromium
```

**Resolution**:
```bash
# Install Rosetta 2 for compatibility
/usr/sbin/softwareupdate --install-rosetta

# Or use native ARM build
PLAYWRIGHT_BROWSERS_PATH=0 playwright install chromium

# Fallback to Selenium
echo "BROWSER_FRAMEWORK=selenium" >> .env
brew install chromedriver
```

**Issue**: Permission denied errors
```bash
# Error: [Errno 13] Permission denied: '/usr/local/bin/playwright'
```

**Resolution**:
```bash
# Fix permissions
sudo chown -R $(whoami) /usr/local/bin/
chmod +x venv/bin/playwright

# Or install user-local
pip install --user playwright
```

### Windows

**Issue**: Playwright installation fails with Windows Defender
```bash
# Error: Access denied when downloading browsers
```

**Resolution**:
```bash
# Temporarily disable real-time protection
# Or add exception for Python/venv directory

# Use Selenium fallback
set BROWSER_FRAMEWORK=selenium
pip install webdriver-manager
```

**Issue**: Path length limitations (Windows < 10)
```bash
# Error: File name too long
```

**Resolution**:
```bash
# Enable long path support or move to shorter directory
# HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem
# Set LongPathsEnabled = 1

# Or use shorter paths
cd C:\
git clone https://github.com/SiegfredLorelle/genshin-checkin-bot.git bot
cd bot
```

### Linux

**Issue**: Missing system dependencies for Playwright
```bash
# Error: Dependencies are missing for Chromium
```

**Resolution**:
```bash
# Install system dependencies
playwright install-deps

# Or manually install
sudo apt-get update
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgtk-3-0 \
    libatspi2.0-0

# Fallback to Selenium
export BROWSER_FRAMEWORK=selenium
sudo apt-get install chromium-browser
```

**Issue**: Headless display issues
```bash
# Error: Failed to launch browser, no display
```

**Resolution**:
```bash
# Install virtual display
sudo apt-get install xvfb

# Or ensure headless mode
echo "HEADLESS=true" >> .env
```

## Framework Switching Procedures

### Automatic Fallback

The system automatically falls back to Selenium if Playwright fails:

```python
# In src/browser/manager.py
try:
    # Try Playwright first
    from .playwright_impl import PlaywrightBrowserManager
    self._browser_impl = PlaywrightBrowserManager()
except ImportError:
    # Auto-fallback to Selenium
    from .selenium_impl import SeleniumBrowserManager
    self._browser_impl = SeleniumBrowserManager()
```

### Manual Framework Selection

**Set via Environment Variable**:
```bash
# Use Playwright (default)
echo "BROWSER_FRAMEWORK=playwright" >> .env

# Use Selenium
echo "BROWSER_FRAMEWORK=selenium" >> .env
```

**Set via Command Line**:
```bash
# Run with specific framework
python -m src.automation.orchestrator --framework selenium
python -m src.automation.orchestrator --framework playwright
```

**Set via Code**:
```python
from src.browser.manager import BrowserManager

# Force Selenium
browser_manager = BrowserManager(framework="selenium")

# Force Playwright
browser_manager = BrowserManager(framework="playwright")
```

## Browser Installation Troubleshooting

### Playwright Browser Issues

**Complete Reinstall**:
```bash
# Remove existing browsers
rm -rf ~/.cache/ms-playwright/

# Reinstall browsers
playwright install chromium --force

# Or install all browsers
playwright install
```

**Proxy/Firewall Issues**:
```bash
# Set proxy for browser download
export HTTPS_PROXY=http://proxy.company.com:8080
playwright install chromium

# Or download manually and set path
export PLAYWRIGHT_BROWSERS_PATH=/path/to/browsers
```

### Selenium WebDriver Issues

**ChromeDriver Version Mismatch**:
```bash
# Check Chrome version
google-chrome --version
# or
chromium --version

# Install matching ChromeDriver
from webdriver_manager.chrome import ChromeDriverManager
ChromeDriverManager().install()
```

**WebDriver Not Found**:
```bash
# Manual installation
# Download from https://chromedriver.chromium.org/
# Add to PATH or set in code:

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

service = Service("/path/to/chromedriver")
driver = webdriver.Chrome(service=service)
```

## Environment Validation Script

Create dependency verification script:

```bash
# Create scripts/verify_dependencies.py
cat > scripts/verify_dependencies.py << 'EOF'
#!/usr/bin/env python3
"""Verify all dependencies are correctly installed and configured."""

import sys
import importlib
from typing import List, Tuple

def check_python_version() -> bool:
    """Check Python version requirement."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.9+)")
        return False

def check_dependencies() -> List[Tuple[str, bool]]:
    """Check required dependencies."""
    dependencies = [
        'playwright',
        'selenium', 
        'httpx',
        'decouple',
        'structlog',
        'pytest',
    ]
    
    results = []
    for dep in dependencies:
        try:
            importlib.import_module(dep)
            print(f"✅ {dep}")
            results.append((dep, True))
        except ImportError:
            print(f"❌ {dep}")
            results.append((dep, False))
    
    return results

def check_browser_frameworks() -> None:
    """Check browser framework availability."""
    # Test Playwright
    try:
        from playwright.sync_api import sync_playwright
        print("✅ Playwright available")
    except ImportError:
        print("❌ Playwright not available")
    
    # Test Selenium
    try:
        from selenium import webdriver
        print("✅ Selenium available")
    except ImportError:
        print("❌ Selenium not available")

if __name__ == "__main__":
    print("🔍 Verifying Dependencies...\n")
    
    python_ok = check_python_version()
    print()
    
    dep_results = check_dependencies()
    print()
    
    check_browser_frameworks()
    print()
    
    # Summary
    failed_deps = [dep for dep, success in dep_results if not success]
    
    if python_ok and not failed_deps:
        print("🎉 All dependencies verified successfully!")
        sys.exit(0)
    else:
        print("🚨 Issues found:")
        if not python_ok:
            print("  - Upgrade Python to 3.9+")
        if failed_deps:
            print(f"  - Install missing dependencies: {', '.join(failed_deps)}")
        sys.exit(1)
