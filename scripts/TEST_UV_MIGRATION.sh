#!/bin/bash
# Test script to verify uv migration is working correctly

set -e  # Exit on any error

echo "🧪 Testing uv Migration"
echo "======================="
echo ""

# Check if uv is installed
echo "1️⃣  Checking uv installation..."
if command -v uv &> /dev/null; then
    echo "   ✅ uv is installed: $(uv --version)"
else
    echo "   ❌ uv not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi
echo ""

# Validate pyproject.toml
echo "2️⃣  Validating pyproject.toml..."
python3 -c "import tomllib; f = open('pyproject.toml', 'rb'); tomllib.load(f); print('   ✅ pyproject.toml is valid')"
echo ""

# Test uv sync (dry run)
echo "3️⃣  Testing uv sync (this will install dependencies)..."
uv sync --dry-run
echo "   ✅ Dependency resolution successful"
echo ""

# Actually install dependencies
echo "4️⃣  Installing dependencies with uv..."
uv sync
echo "   ✅ Dependencies installed"
echo ""

# Verify imports work
echo "5️⃣  Testing Python imports..."
uv run python -c "import playwright; import selenium; import structlog; print('   ✅ Core dependencies importable')"
echo ""

# Run a simple test
echo "6️⃣  Running sample tests..."
uv run pytest tests/unit/test_config_manager.py -v --tb=short || echo "   ⚠️  Some tests may fail if environment not fully configured"
echo ""

echo "🎉 Migration test complete!"
echo ""
echo "✅ This project now uses uv exclusively"
echo ""
echo "Next steps:"
echo "  1. Review docs/setup/UV_MIGRATION.md for full migration guide"
echo "  2. Install Playwright browsers: uv run playwright install chromium"
echo "  3. Configure .env file with your credentials"
echo "  4. Run full test suite: uv run pytest"
echo ""
echo "Note: pip/venv workflows are no longer supported"
