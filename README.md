# Genshin Impact HoYoLAB Check-in Bot
> Automated daily check-ins for Genshin Impact HoYoLAB rewards

[![Daily Check-in](https://github.com/SiegfredLorelle/genshin-checkin-bot/actions/workflows/daily-checkin.yml/badge.svg)](https://github.com/SiegfredLorelle/genshin-checkin-bot/actions/workflows/daily-checkin.yml)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

An automated browser-based solution for daily HoYoLAB check-ins using Playwright with robust error handling. Can run locally or be deployed to GitHub Actions for fully automated daily check-ins at 6 AM PhST with zero cost.

---

## Table of Contents

- [Genshin Impact HoYoLAB Check-in Bot](#genshin-impact-hoyolab-check-in-bot)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Prerequisites](#prerequisites)
    - [For Native Installation:](#for-native-installation)
    - [For GitHub Actions Deployment:](#for-github-actions-deployment)
  - [Configuration](#configuration)
    - [Environment Setup](#environment-setup)
  - [Installation](#installation)
    - [Native Installation](#native-installation)
      - [1. Install uv Package Manager](#1-install-uv-package-manager)
      - [2. Install Dependencies](#2-install-dependencies)
      - [3. Verify Installation](#3-verify-installation)
    - [GitHub Actions Deployment](#github-actions-deployment)
      - [Setup Steps:](#setup-steps)
  - [Usage](#usage)
    - [Running the Application](#running-the-application)
      - [Native Execution](#native-execution)
      - [GitHub Actions Execution](#github-actions-execution)
  - [Development](#development)
    - [Project Structure](#project-structure)
  - [Browser Automation](#browser-automation)
  - [Troubleshooting](#troubleshooting)
    - [Common Installation Issues](#common-installation-issues)
    - [Browser Issues](#browser-issues)
  - [Project Structure](#project-structure-1)
  - [Security Considerations](#security-considerations)
  - [Contributing](#contributing)

## Features

- **Automated Daily Check-ins**: Never miss HoYoLAB rewards with scheduled automation
- **Playwright Browser Automation**: Reliable and modern web automation with Chromium
- **Robust Error Handling**: Automatic retry logic and comprehensive failure screenshots
- **Structured Logging**: JSON-formatted logs with secret redaction for production safety
- **GitHub Actions Support**: Deploy for automated daily check-ins at 6 AM PhST with zero cost
- **Educational Focus**: Well-documented code for learning web automation best practices

## Prerequisites

Before you begin, ensure you have the following:

### For Native Installation:
- **Python 3.11+**: Download from [python.org](https://www.python.org/downloads/)
- **Git**: For cloning the repository
- **uv**: Python package manager ([Install Guide](https://docs.astral.sh/uv/getting-started/installation/))

### For GitHub Actions Deployment:
- **GitHub Account**: For hosting and running the automation
- **HoYoLAB Account**: Your game account credentials

## Configuration

⚠️ **Important**: Complete this configuration step before proceeding with installation.

### Environment Setup

1. **Clone the Repository**

   **Option 1: HTTPS (recommended for most users)**
   ```bash
   git clone https://github.com/SiegfredLorelle/genshin-checkin-bot.git
   cd genshin-checkin-bot
   ```

   **Option 2: SSH (recommended for developers with SSH keys set up)**
   ```bash
   git clone git@github.com:SiegfredLorelle/genshin-checkin-bot.git
   cd genshin-checkin-bot
   ```

2. **Create environment configuration:**
   ```bash
   cp .env.example .env
   # Note: `cp` is a UNIX command
   # On Windows, manually create `.env` file following `.env.example` contents
   ```

3. **Edit the `.env` file with your configuration:**
   ```bash
   nvim .env  # or use your preferred text editor
   ```

4. **Add your required environment variables:**

   ```env
   # HoYoLAB Authentication (REQUIRED)
   HOYOLAB_USERNAME=your_email@example.com
   HOYOLAB_PASSWORD=your_password_here

   # Automation Configuration (Optional - defaults provided)
   CHECKIN_URL=https://act.hoyolab.com/ys/event/signin-sea-v3/index.html
   MIN_DELAY=2.0
   MAX_DELAY=8.0
   ```

**⚠️ Security Note**: Never commit `.env` file to git. It's included in `.gitignore` for safety.

## Installation

### Native Installation

⚠️ **Prerequisites**: Ensure you have completed the [Configuration](#configuration) section above before running these commands.

#### 1. Install uv Package Manager

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 2. Install Dependencies

```bash
# Install all dependencies (automatically creates virtual environment)
uv sync

# Install Playwright browsers
uv run playwright install chromium
```

> **📌 Important**: All Python commands must be prefixed with `uv run` (e.g., `uv run python script.py`). This ensures correct Python version (3.11) and dependencies are used.

#### 3. Verify Installation

```bash
# Verify Python version (should show 3.11.x)
uv run python --version

# Run dependency verification
uv run python scripts/verify_dependencies.py

# Run unit tests
uv run pytest tests/unit/
```

### GitHub Actions Deployment

⚠️ **Prerequisites**: Ensure you have a GitHub account and have pushed your repository to GitHub.

Automate daily check-ins at 6 AM PhST using GitHub Actions (free tier):

#### Setup Steps:

1. **Push to GitHub** (if not already)
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Add Secrets**:
   - Navigate to: Repository Settings → Secrets and variables → Actions → New repository secret
   - Add the following secrets:
     - `HOYOLAB_USERNAME` = Your HoYoLAB email
     - `HOYOLAB_PASSWORD` = Your HoYoLAB password

3. **Enable Actions**:
   - Settings → Actions → General → Allow all actions

4. **Test Run**:
   - Actions tab → Daily HoYoLAB Check-in → Run workflow → Enable dry-run

5. **Done!** Runs automatically daily at 6 AM PhST

📖 **Full deployment guide with screenshots:** [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

**Benefits:**
- ✅ Zero cost (GitHub Actions free tier)
- ✅ No server management required
- ✅ Secure credential storage
- ✅ 90-day execution logs
- ✅ Manual trigger button for missed runs

## Usage

### Running the Application

#### Native Execution

Test the bot locally with a dry run (no actual check-in):

```bash
uv run python -m src --dry-run
```

Run the full check-in automation:

```bash
uv run python -m src
# Note: command may be `uv run python3` depending on OS or installation
```

#### GitHub Actions Execution

After setting up GitHub Actions deployment, the automation runs automatically at 6 AM PhST daily. You can also:

- **Manual Trigger**: Actions tab → Daily HoYoLAB Check-in → Run workflow
- **View Logs**: Actions tab → Select workflow run → View logs
- **Check Status**: README badge shows latest run status

## Development

### Project Structure

> **Note**: All commands must use `uv run` prefix to ensure correct Python version and dependencies.

```bash
# Code Quality
uv run ruff format src/ tests/        # Format code
uv run ruff check src/ tests/         # Lint code
uv run ruff check --fix src/ tests/   # Lint and auto-fix
uv run mypy src/                      # Type checking

# Testing
uv run pytest tests/unit/             # Unit tests only
uv run pytest tests/integration/      # Integration tests only
uv run pytest tests/ --cov=src        # All tests with coverage

# Local Testing
uv run python -m src                  # Full execution
uv run python -m src --dry-run        # Test without actions

# Dependency Management
uv add package-name                   # Add new package
uv add --dev package-name             # Add dev dependency
uv lock --upgrade                     # Update lock file
uv sync                               # Sync dependencies after pulling changes
```

[&#9650; Back to Top](#genshin-impact-hoyolab-check-in-bot)

---

## Browser Automation

This project uses **Playwright** for browser automation, providing reliable and modern web automation capabilities.

**Key Features:**
- Superior reliability and stability
- Built-in async support
- Advanced waiting strategies
- Excellent debugging tools
- Optimized for GitHub Actions integration

**Browser Installation:**
```bash
uv run playwright install chromium
```

[&#9650; Back to Top](#genshin-impact-hoyolab-check-in-bot)

---

## Troubleshooting

### Common Installation Issues

- **Playwright Browser Installation Fails:**

  ```bash
  # Try manual installation with dependencies
  uv run playwright install chromium --with-deps

  # Or install system dependencies separately (Linux)
  uv run playwright install-deps
  ```

- **Import Errors:**

  ```bash
  # Verify uv environment
  uv run python --version  # Should show correct Python version

  # Reinstall dependencies
  uv sync --reinstall

  # Clear cache and reinstall
  rm -rf .venv/
  uv sync
  ```

### Browser Issues

- **Chromium Won't Launch:**
  - Ensure adequate disk space (>1GB for Playwright browsers)
  - Check firewall settings aren't blocking browser
  - Try headless mode: `HEADLESS=true` in `.env`

- **Element Detection Fails:**
  - Check HoYoLAB UI hasn't changed
  - Verify credentials are still valid
  - Review logs in `logs/` directory

[&#9650; Back to Top](#genshin-impact-hoyolab-check-in-bot)

---

## Project Structure

```
genshin-checkin-bot/
├── src/                       # Core automation code
│   ├── automation/           # Main automation logic
│   ├── browser/              # Browser framework abstraction
│   ├── detection/            # Reward detection logic
│   ├── config/               # Configuration management
│   ├── state/                # State and analytics
│   └── utils/                # Shared utilities
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── e2e/                  # End-to-end tests
├── logs/                     # Execution logs and screenshots
├── scripts/                  # Setup and maintenance scripts
└── docs/                     # Documentation
```

[&#9650; Back to Top](#genshin-impact-hoyolab-check-in-bot)

---

## Security Considerations

- **Never commit credentials** to version control
- **Use environment variables** for all sensitive configuration
- **Enable log redaction** to prevent credential exposure
- **Regularly rotate credentials** if compromised
- **GitHub Secrets**: Store credentials as repository secrets, not in workflow files

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow code style: Use `ruff` for formatting and linting
4. Follow [Conventional Commits](https://www.conventionalcommits.org/) format for commit messages
5. Add tests for new features
6. Ensure all tests pass: `uv run pytest tests/`
7. Update documentation for changes
8. Submit a pull request

**Setup pre-commit hooks** (recommended):
```bash
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
```

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for detailed development setup.

---

For more questions, contact:
- **GitHub:** https://github.com/SiegfredLorelle
- **Repository:** https://github.com/SiegfredLorelle/genshin-checkin-bot
