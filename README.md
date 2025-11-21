# Genshin Impact HoYoLAB Check-in Bot

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

An automated browser-based solution for daily HoYoLAB check-ins with robust error handling and multi-framework support.

> **⚠️ Important**: This project uses [`uv`](https://docs.astral.sh/uv/) for dependency management. Traditional pip/venv workflows are not supported. See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for setup instructions.

## Features

- **Dual Browser Framework Support**: Playwright (primary) with Selenium WebDriver fallback
- **Robust Error Handling**: Automatic retry logic and comprehensive failure screenshots
- **Structured Logging**: JSON-formatted logs with secret redaction for production safety
- **Educational Focus**: Well-documented code for learning web automation best practices

## Prerequisites

- **Python 3.9+** (Check with `python3 --version`)
- **uv** - Modern Python package manager ([Install Guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Git** for repository management
- **Chrome/Chromium browser** (automatically managed by Playwright)

## Quick Start

### 1. Clone and Setup Environment

```bash
# Clone repository
git clone https://github.com/SiegfredLorelle/genshin-checkin-bot.git
cd genshin-checkin-bot

# Install uv (fast Python package manager) if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# or: pip install uv

# Create virtual environment and install all dependencies (one command!)
uv sync

# Install Playwright browsers (primary framework)
uv run playwright install chromium
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
uv run python scripts/verify_dependencies.py

# Run unit tests
uv run pytest tests/unit/

# Test browser automation (dry run)
uv run python -m src.automation.orchestrator --dry-run
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
uv run black src/ tests/              # Format code
uv run isort src/ tests/              # Sort imports
uv run flake8 src/ tests/             # Lint code
uv run mypy src/                      # Type checking

# Testing
uv run pytest tests/unit/             # Unit tests only
uv run pytest tests/integration/      # Integration tests only
uv run pytest tests/ --cov=src        # All tests with coverage

# Local Testing
uv run python -m src.automation.orchestrator          # Full execution
uv run python -m src.automation.orchestrator --dry-run # Test without actions

# Dependency Management
uv add package-name                   # Add new package
uv add --dev package-name             # Add dev dependency
uv lock --upgrade                     # Update lock file
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
# Verify uv environment
uv run python --version  # Should show correct Python version

# Reinstall dependencies
uv sync --reinstall

# Clear cache and reinstall
rm -rf .venv/
uv sync
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
# Clean install with uv
rm -rf .venv/
uv sync --reinstall

# Update lock file and reinstall
uv lock --upgrade
uv sync
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

1. **Set up commit message template** (recommended):
   ```bash
   git config commit.template .gitmessage
   ```
2. **Install pre-commit hooks**:
   ```bash
   uv run pre-commit install
   uv run pre-commit install --hook-type commit-msg
   ```
3. Follow code style: `black` formatting, `isort` imports, `flake8` linting
4. Follow [Conventional Commits](https://www.conventionalcommits.org/) format for commit messages
5. Add tests for new features
6. Update documentation for API changes
7. Ensure all tests pass: `pytest tests/`

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for detailed development setup and [.github/COMMIT_CONVENTION.md](.github/COMMIT_CONVENTION.md) for commit message guidelines.

## License

MIT License - see LICENSE file for details.
