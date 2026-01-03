# Genshin Impact HoYoLAB Check-in Bot

[![Daily Check-in](https://github.com/SiegfredLorelle/genshin-checkin-bot/actions/workflows/daily-checkin.yml/badge.svg)](https://github.com/SiegfredLorelle/genshin-checkin-bot/actions/workflows/daily-checkin.yml)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

An automated browser-based solution for daily HoYoLAB check-ins with robust error handling and multi-framework support.

🚀 **NEW:** Now deployable to GitHub Actions for fully automated daily check-ins! See [Deployment Guide](docs/DEPLOYMENT.md).

> **⚠️ CRITICAL**: This project **REQUIRES** [`uv`](https://docs.astral.sh/uv/) for dependency management and Python version management. Traditional pip/venv workflows are **NOT SUPPORTED**. All Python commands must be prefixed with `uv run`. See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for details.

## Features

- **Dual Browser Framework Support**: Playwright (primary) with Selenium WebDriver fallback
- **Robust Error Handling**: Automatic retry logic and comprehensive failure screenshots
- **Structured Logging**: JSON-formatted logs with secret redaction for production safety
- **Educational Focus**: Well-documented code for learning web automation best practices

## Prerequisites

- **Python 3.11+** - Project is pinned to Python 3.11 via `.python-version`
- **uv** - **REQUIRED** Python package manager ([Install Guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Git** for repository management
- **Chrome/Chromium browser** (automatically managed by Playwright)

> **📌 Important**: The project uses `.python-version` to pin Python 3.11. Your system `python` command may differ, but `uv run python` will automatically use the correct version. Always use `uv run` for all Python commands.

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
# Verify Python version (should show 3.11.x)
uv run python --version

# Run dependency verification
uv run python scripts/verify_dependencies.py

# Run unit tests
uv run pytest tests/unit/

# Test browser automation (dry run)
uv run python -m src.automation.orchestrator --dry-run
```

> **⚠️ Common Mistake**: Do NOT run `python script.py` directly. Always use `uv run python script.py` to ensure the correct Python version (3.11) and dependencies are used.

## Credential Configuration

### Setting Up Your HoYoLAB Credentials

Simply provide your HoYoLAB username and password in the `.env` file:

```bash
# HoYoLAB Authentication (REQUIRED)
HOYOLAB_USERNAME=your_email@example.com
HOYOLAB_PASSWORD=your_password_here
```

### Environment File Setup

Edit `.env` file with your credentials:

```bash
# HoYoLAB Authentication (REQUIRED)
HOYOLAB_USERNAME=your_email@example.com
HOYOLAB_PASSWORD=your_password_here

# Automation Configuration (Optional - defaults provided)
CHECKIN_URL=https://act.hoyolab.com/ys/event/signin-sea-v3/index.html
MIN_DELAY=2.0
MAX_DELAY=8.0

# Framework Selection (Optional)
BROWSER_FRAMEWORK=playwright  # or "selenium"
```

**⚠️ Security Note**: Never commit `.env` file to git. It's included in `.gitignore` for safety.

## 🚀 Deployment (GitHub Actions)

### Quick Deploy

Want to run this automatically every day at 6 AM PHT? Deploy to GitHub Actions in 5 minutes:

1. **Push to GitHub** (if not already)
2. **Add Secrets**: Settings → Secrets → Actions
   - `HOYOLAB_USERNAME` = Your HoYoLAB email
   - `HOYOLAB_PASSWORD` = Your HoYoLAB password
3. **Enable Actions**: Settings → Actions → General → Allow all actions
4. **Test Run**: Actions tab → Daily HoYoLAB Check-in → Run workflow (dry-run)
5. **Done!** Runs automatically daily at 6 AM PHT

📖 **Full deployment guide with screenshots:** [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

**Benefits:**
- ✅ Zero cost (GitHub Actions free tier)
- ✅ No server management
- ✅ Secure credential storage
- ✅ Automatic email notifications on failure
- ✅ 90-day execution logs
- ✅ Manual trigger button for missed runs

## Development Commands

> **🔴 CRITICAL**: ALL commands below MUST be run with `uv run` prefix. Direct Python execution will use the wrong version and dependencies.

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
uv sync                               # Sync dependencies after pulling changes

# Python Version Management
uv python list                        # List available Python versions
uv python install 3.11                # Install Python 3.11 if needed
uv python pin 3.11                    # Pin project to Python 3.11 (updates .python-version)
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

# Or via command line (MUST use uv run)
uv run python -m src.automation.orchestrator --framework selenium
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
3. Follow code style: `ruff` for formatting and linting
4. Follow [Conventional Commits](https://www.conventionalcommits.org/) format for commit messages
5. Add tests for new features
6. Update documentation for API changes
7. Ensure all tests pass: `pytest tests/`

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for detailed development setup and [.github/COMMIT_CONVENTION.md](.github/COMMIT_CONVENTION.md) for commit message guidelines.

## License

MIT License - see LICENSE file for details.
