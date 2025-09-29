# Genshin Impact HoYoLAB Check-in Bot

An automated browser-based solution for daily HoYoLAB check-ins with robust error handling and multi-framework support.

## Features

- **Dual Browser Framework Support**: Playwright (primary) with Selenium WebDriver fallback
- **Robust Error Handling**: Automatic retry logic and comprehensive failure screenshots
- **Structured Logging**: JSON-formatted logs with secret redaction for production safety
- **Educational Focus**: Well-documented code for learning web automation best practices

## Prerequisites

- **Python 3.9+** (Check with `python3 --version`)
- **Git** for repository management
- **Chrome/Chromium browser** (automatically managed by Playwright)

## Quick Start

### 1. Clone and Setup Environment

```bash
# Clone repository
git clone https://github.com/SiegfredLorelle/genshin-checkin-bot.git
cd genshin-checkin-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (primary framework)
playwright install chromium
```

### 2. Configure Credentials

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your HoYoLAB credentials
# See "Credential Configuration" section below
```

### 3. Test Installation

```bash
# Run dependency verification
python scripts/verify_dependencies.py

# Run unit tests
pytest tests/unit/

# Test browser automation (dry run)
python -m src.automation.orchestrator --dry-run
```

## Credential Configuration

### Finding Your HoYoLAB Credentials

1. **Login to HoYoLAB**: Visit https://www.hoyolab.com and login
2. **Open Browser DevTools**: F12 or right-click → Inspect
3. **Go to Application/Storage Tab**: Find Cookies section
4. **Locate Cookies for hoyolab.com**:
   - `ltuid` → Use as `HOYOLAB_LTUID`
   - `ltoken` → Use as `HOYOLAB_LTOKEN`

### Environment File Setup

Edit `.env` file with your credentials:

```bash
# HoYoLAB Authentication (REQUIRED)
HOYOLAB_LTUID=your_ltuid_here
HOYOLAB_LTOKEN=your_ltoken_here

# Automation Configuration (Optional - defaults provided)
CHECKIN_URL=https://act.hoyolab.com/ys/event/signin-sea-v3/index.html
MIN_DELAY=2.0
MAX_DELAY=8.0

# Framework Selection (Optional)
BROWSER_FRAMEWORK=playwright  # or "selenium"
```

**⚠️ Security Note**: Never commit `.env` file to git. It's included in `.gitignore` for safety.

## Development Commands

```bash
# Code Quality
black src/ tests/              # Format code
isort src/ tests/              # Sort imports  
flake8 src/ tests/             # Lint code
mypy src/                      # Type checking

# Testing
pytest tests/unit/             # Unit tests only
pytest tests/integration/      # Integration tests only
pytest tests/ --cov=src        # All tests with coverage

# Local Testing
python -m src.automation.orchestrator          # Full execution
python -m src.automation.orchestrator --dry-run # Test without actions
```

## Browser Framework Selection

### Playwright (Primary - Recommended)

**Advantages:**
- Superior reliability and stability
- Built-in async support
- Advanced waiting strategies
- Excellent debugging tools
- Better GitHub Actions integration

**Requirements:**
```bash
playwright install chromium
```

### Selenium WebDriver (Fallback)

**When to Use:**
- Playwright installation issues
- Platform compatibility requirements
- Familiar with Selenium ecosystem

**Requirements:**
```bash
# ChromeDriver auto-managed by selenium-manager in v4.15+
# No manual installation needed
```

### Framework Switching

The system automatically falls back to Selenium if Playwright fails. Manual switching:

```bash
# Set in .env file
BROWSER_FRAMEWORK=selenium

# Or via command line
python -m src.automation.orchestrator --framework selenium
```

## Troubleshooting

### Common Installation Issues

**Playwright Browser Installation Fails:**
```bash
# Try manual installation
npx playwright install chromium

# Or switch to Selenium fallback
echo "BROWSER_FRAMEWORK=selenium" >> .env
```

**Import Errors:**
```bash
# Verify virtual environment is activated
which python  # Should point to venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Permission Issues (macOS/Linux):**
```bash
# Fix Python permissions
chmod +x venv/bin/python

# Fix Playwright permissions
chmod +x venv/bin/playwright
```

### Browser Issues

**Chromium Won't Launch:**
- Ensure adequate disk space (>1GB for Playwright browsers)
- Check firewall settings aren't blocking browser
- Try headless mode: `HEADLESS=true` in `.env`

**Element Detection Fails:**
- Check HoYoLAB UI hasn't changed
- Verify credentials are still valid
- Review logs in `logs/debug/` directory

### Dependency Conflicts

**Version Conflicts:**
```bash
# Clean install
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Platform-Specific Issues:**
- **Windows**: Use `venv\Scripts\activate` instead of `source venv/bin/activate`
- **macOS**: May need Xcode command line tools: `xcode-select --install`
- **Linux**: Install browser dependencies: `playwright install-deps`

## Project Structure

```
genshin-checkin-bot/
├── src/                        # Core automation code
│   ├── automation/            # Main automation logic
│   ├── browser/               # Browser framework abstraction
│   ├── detection/             # Reward detection logic
│   ├── config/                # Configuration management
│   ├── state/                 # State and analytics
│   └── utils/                 # Shared utilities
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── fixtures/              # Test data
├── logs/                      # Execution logs and screenshots
├── scripts/                   # Setup and maintenance scripts
└── docs/                      # Documentation
```

## Security Considerations

- **Never commit credentials** to version control
- **Use environment variables** for all sensitive configuration
- **Enable log redaction** to prevent credential exposure
- **Regularly rotate tokens** if compromised

## Contributing

1. Follow code style: `black` formatting, `isort` imports, `flake8` linting
2. Add tests for new features
3. Update documentation for API changes
4. Ensure all tests pass: `pytest tests/`

## License

MIT License - see LICENSE file for details.
