# Development Setup

## �� Important: This Project Uses uv

This project **requires** `uv` for dependency management. Traditional `pip` and `venv` workflows are **not supported**.

### Why uv Only?

1. **Performance**: 10-100x faster than pip
2. **Consistency**: Lock files ensure everyone has identical environments
3. **Modern**: Built on Python standards (PEP 621)
4. **Simplicity**: One tool, one workflow, less confusion

## Quick Start

```bash
# 1. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone and install dependencies
git clone https://github.com/SiegfredLorelle/genshin-checkin-bot.git
cd genshin-checkin-bot
uv sync

# 3. Install Playwright browsers
uv run playwright install chromium

# 4. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 5. Run tests
uv run pytest
```

## Common Commands

```bash
# Run automation (dry run)
uv run python -m src.automation.orchestrator --dry-run

# Run tests
uv run pytest tests/unit/
uv run pytest tests/integration/
uv run pytest --cov=src

# Code quality
uv run black src/ tests/
uv run isort src/ tests/
uv run flake8 src/ tests/
uv run mypy src/

# Add dependencies
uv add package-name          # Production dependency
uv add --dev package-name    # Development dependency

# Update dependencies
uv lock --upgrade
uv sync
```

## Need Help?

- 📚 [uv Documentation](https://docs.astral.sh/uv/)
- 📖 [Quick Reference](../.github/UV_QUICKREF.md)
- 🔄 [Migration Guide](setup/UV_MIGRATION.md)
- ❓ [Project Issues](https://github.com/SiegfredLorelle/genshin-checkin-bot/issues)

## Requirements

- Python 3.9 or higher
- uv (latest version recommended)
- Git

That's it! No pip, no venv, just uv. 🚀
