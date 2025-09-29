# Development Workflow

The development setup and workflow supports both local development and cloud deployment while maintaining consistency and educational value.

## Local Development Setup

**Prerequisites:**
```bash
# Install Python 3.9+
python3 --version

# Install pip and venv
python3 -m pip install --upgrade pip
python3 -m venv --help

# Install Playwright browser dependencies (if using Playwright)
npx playwright install-deps
```

**Initial Setup:**
```bash
# Clone repository
git clone https://github.com/SiegfredLorelle/genshin-checkin-bot.git
cd genshin-checkin-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (if using Playwright)
playwright install chromium

# Copy environment template
cp .env.example .env
# Edit .env with your HoYoLAB credentials (see SECURITY.md for safe practices)
```

**Development Commands:**
```bash
# Start local automation test
python -m src.automation.orchestrator --dry-run

# Run specific test suites  
pytest tests/unit/                    # Unit tests only
pytest tests/integration/             # Integration tests only
pytest tests/                        # All tests

# Run with coverage
pytest --cov=src tests/

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Lint code
flake8 src/ tests/
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
