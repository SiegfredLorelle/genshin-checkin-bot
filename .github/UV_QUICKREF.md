# uv Quick Reference Card

## Essential Commands

### Setup & Installation
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync                    # Install all dependencies
uv sync --extra dev        # Include dev dependencies
uv sync --extra test       # Include test dependencies
```

### Running Commands
```bash
# Run Python scripts
uv run python script.py
uv run pytest
uv run python -m src.automation.orchestrator --dry-run

# Run tools
uv run black src/ tests/
uv run mypy src/
uv run flake8 src/
```

### Dependency Management
```bash
# Add packages
uv add playwright          # Add to dependencies
uv add --dev black         # Add to dev dependencies

# Remove packages
uv remove playwright

# Update packages
uv lock --upgrade          # Update lock file
uv sync                    # Install updated deps
```

### Lock File Management
```bash
# Create/update lock file
uv lock

# Sync from lock file
uv sync

# Export to requirements.txt
uv pip compile pyproject.toml -o requirements.txt
```

### Environment Management
```bash
# Create venv (automatic with uv sync)
uv venv

# Clean and reinstall
rm -rf .venv/
uv sync --reinstall

# Show installed packages
uv pip list
```

## Why uv is Better

| Feature | pip | uv |
|---------|-----|-----|
| Speed | 1x | 10-100x |
| Lock files | ❌ | ✅ |
| Resolution | Slow | Fast |
| Built with | Python | Rust |
| Memory usage | High | Low |

## Emergency pip Compatibility

If you absolutely need pip, generate requirements.txt:
```bash
uv pip compile pyproject.toml -o requirements.txt
# Then use pip as normal (not recommended)
```

**Note**: This project uses uv exclusively. The above is for emergency use only.

---
📚 Full docs: https://docs.astral.sh/uv/  
🎯 Project requires: Python 3.9+ and uv installed
