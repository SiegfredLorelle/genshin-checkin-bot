# Migration to uv Package Manager

**Date**: November 21, 2025  
**Status**: ✅ Complete

## What Changed

We migrated from traditional `pip + requirements.txt` to modern `uv + pyproject.toml` for faster, more reliable dependency management.

## Why uv?

- ⚡ **10-100x faster** than pip for installations
- 🔒 **Lock files** (`uv.lock`) ensure reproducible builds
- 🛠️ **Single tool** for virtual envs + package management
- 📦 **Modern standard** (PEP 621 pyproject.toml)
- 🚀 **Built in Rust** for reliability

## Quick Start (New Contributors)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# or: pip install uv

# Clone and setup (one command!)
git clone https://github.com/SiegfredLorelle/genshin-checkin-bot.git
cd genshin-checkin-bot
uv sync

# Install Playwright browsers
uv run playwright install chromium

# Run tests
uv run pytest
```

## For Existing Contributors

**This project now uses uv exclusively** - no backwards compatibility with pip.

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Remove old venv if it exists
rm -rf venv/

# Install with uv
uv sync

# Done! All dependencies installed with lock file
```

### Why No pip Support?

- **Modern standards**: PEP 621 + lock files are the future
- **Consistency**: Everyone uses the same tool and gets identical environments
- **Performance**: 10-100x faster for everyone
- **Simplicity**: One tool, one way, better documentation

## Common Commands Comparison

| Old (pip) | New (uv) |
|-----------|----------|
| `pip install -r requirements.txt` | `uv sync` |
| `pip install package` | `uv add package` |
| `pip install --upgrade package` | `uv lock --upgrade` |
| `python -m pytest` | `uv run pytest` |
| `python script.py` | `uv run python script.py` |
| `pip freeze` | `uv pip list` or `uv tree` |

## File Changes

### Modified Files
- ✅ `pyproject.toml` - Now contains all dependencies (PEP 621 format)
- ✅ `README.md` - Updated setup instructions
- ✅ `docs/architecture/tech-stack.md` - Documented uv choice
- ✅ `docs/architecture/development-workflow.md` - Updated commands

### New Files
- ✅ `uv.lock` - Lock file for reproducible installs (committed to git)
- ✅ `.venv/` - New virtual environment directory (gitignored)

### Removed Files
- ❌ `venv/` - Old virtual environment (replaced by `.venv/`)
- ❌ `requirements.txt` - No longer needed (replaced by pyproject.toml)

## Troubleshooting

### "uv: command not found"
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# Restart shell or source ~/.bashrc
```

### "Import errors after migration"
```bash
# Reinstall all dependencies
uv sync --reinstall
```

### "I really need pip compatibility"
```bash
# Generate requirements.txt from pyproject.toml if absolutely needed
uv pip compile pyproject.toml -o requirements.txt
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Note: This is not officially supported. Use uv instead!
```

## CI/CD (GitHub Actions)

GitHub Actions will be updated in Epic 3 to use uv:

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v1
  
- name: Install dependencies
  run: uv sync
```

This will make CI/CD ~10x faster! 🚀

## Questions?

- uv docs: https://docs.astral.sh/uv/
- Report issues: https://github.com/SiegfredLorelle/genshin-checkin-bot/issues

---

**Migration completed by**: John (Product Manager Agent)  
**Architecture alignment**: ✅ All docs updated  
**Approach**: 🚀 Modern-only (no backwards compatibility)  
**Status**: Production-ready
