# Development Workflow

The development setup and workflow supports both local development and cloud deployment while maintaining consistency and educational value.

## Local Development Setup

**Prerequisites:**
```bash
# Install Python 3.11+
python3 --version

# Install uv (fast Python package manager)
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip:
pip install uv

# Install Playwright browser dependencies (if using Playwright)
npx playwright install-deps
```

**Initial Setup:**
```bash
# Clone repository
git clone https://github.com/SiegfredLorelle/genshin-checkin-bot.git
cd genshin-checkin-bot

# Create virtual environment and install dependencies (one command!)
uv sync

# Alternative: Install specific dependency groups
uv sync --extra dev --extra test

# Install Playwright browsers (if using Playwright)
uv run playwright install chromium

# Copy environment template
cp .env.example .env
# Edit .env with your HoYoLAB credentials (see SECURITY.md for safe practices)
```

**Why uv?**
- ⚡ 10-100x faster than pip
- 🔒 Automatic lock file (`uv.lock`) for reproducible installs
- 🛠️ Single tool for venv + package management
- 📦 Modern Python standards (PEP 621)
- 🚀 Built in Rust for reliability and speed

**Note**: This project uses **uv exclusively**. Traditional pip/venv workflows are not supported.

**Development Commands:**
```bash
# Start local automation test
uv run python -m src.automation.orchestrator --dry-run

# Run specific test suites
uv run pytest tests/unit/                    # Unit tests only
uv run pytest tests/integration/             # Integration tests only
uv run pytest tests/                        # All tests

# Run with coverage
uv run pytest --cov=src tests/

# Format code
uv run black src/ tests/
uv run isort src/ tests/

# Type checking
uv run mypy src/

# Lint code
uv run flake8 src/ tests/

# Add new dependency
uv add package-name

# Add development dependency
uv add --dev package-name

# Update dependencies
uv lock --upgrade

# Show dependency tree
uv tree
```

## Environment Configuration

**Required Environment Variables:**

**Backend (.env):**
```bash
# HoYoLAB Authentication
HOYOLAB_LTUID=your_user_id_here
HOYOLAB_LTOKEN=your_auth_token_here

# Automation Configuration
CHECKIN_URL=https://act.hoyolab.com/ys/event/signin-sea-v3/index.html
ACT_ID=e202102251931481
USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

# Timing Configuration
MIN_DELAY=2.0
MAX_DELAY=8.0
PAGE_LOAD_TIMEOUT=30.0
ELEMENT_TIMEOUT=15.0

# CSS Selectors
PRIMARY_SELECTOR=".calendar-container .today-sign"
FALLBACK_SELECTOR_1="[data-testid='check-in-button']"
FALLBACK_SELECTOR_2=".sign-in-btn:not(.disabled)"

# Logging
LOG_LEVEL=INFO
SCREENSHOT_ON_FAILURE=true
LOG_DOM_SNAPSHOTS=false
```

**Shared:**
```bash
# GitHub Actions (auto-populated in cloud)
GITHUB_RUN_ATTEMPT=1
GITHUB_WORKSPACE=/github/workspace
GITHUB_REPOSITORY=SiegfredLorelle/genshin-checkin-bot
```
