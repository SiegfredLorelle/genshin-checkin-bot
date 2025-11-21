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

# 5. Set up pre-commit hooks
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg

# 6. Run tests
uv run pytest
```

## Pre-commit Hooks

This project uses `pre-commit` to enforce code quality and commit message standards.

### Initial Setup

```bash
# Install pre-commit hooks (one-time setup)
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
```

### What Gets Checked

**On every commit:**
- Trailing whitespace removal
- End-of-file fixing
- YAML syntax validation
- Large file detection
- Merge conflict markers
- Code formatting (black)
- Import sorting (isort)
- Code linting (flake8)

**On commit message:**
- Conventional Commits format validation
- Type prefix required (feat, fix, docs, etc.)
- Subject line max 72 characters
- Body lines max 100 characters

### Commit Message Format

All commits must follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Valid types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no logic change)
- `refactor`: Code restructuring (no behavior change)
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `build`: Build system or dependencies
- `ci`: CI/CD changes
- `chore`: Other changes (tooling, configs)
- `revert`: Revert a previous commit

**Examples:**
```bash
# Good commits
git commit -m "feat(browser): add retry logic for element detection"
git commit -m "fix(config): handle missing environment variables gracefully"
git commit -m "docs: update setup instructions for uv"
git commit -m "test(detector): add tests for reward claiming workflow"

# Bad commits (will be rejected)
git commit -m "Updated stuff"  # No type
git commit -m "feat: Add new feature that exceeds the maximum allowed character length for subject"  # Too long
git commit -m "FEAT: new feature"  # Uppercase type
```

### Manual Hook Execution

```bash
# Run all hooks on staged files
uv run pre-commit run

# Run all hooks on all files
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run black --all-files
uv run pre-commit run commitlint --hook-stage commit-msg --commit-msg-filename .git/COMMIT_EDITMSG
```

### Skipping Hooks (Use Sparingly)

```bash
# Skip pre-commit hooks (NOT recommended)
git commit --no-verify -m "feat: emergency fix"
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

## Continuous Integration

### Commit Validation in CI

All commits pushed to the repository are automatically validated in GitHub Actions:

- **On Push to Main/Develop**: Validates the latest commit message
- **On Pull Requests**: Validates all commits in the PR

The CI will fail if any commit message doesn't follow Conventional Commits format. This ensures:
- Consistent commit history across all branches
- Automated changelog generation capability
- Clear communication of changes in version control

### Workflow Location

See `.github/workflows/commit-lint.yml` for the CI configuration.

## Need Help?

- 📚 [uv Documentation](https://docs.astral.sh/uv/)
- 📖 [Quick Reference](../.github/UV_QUICKREF.md)
- 🔄 [Migration Guide](setup/UV_MIGRATION.md)
- ❓ [Project Issues](https://github.com/SiegfredLorelle/genshin-checkin-bot/issues)
- 📝 [Conventional Commits](https://www.conventionalcommits.org/)

## Requirements

- Python 3.9 or higher
- uv (latest version recommended)
- Git

That's it! No pip, no venv, just uv. 🚀
