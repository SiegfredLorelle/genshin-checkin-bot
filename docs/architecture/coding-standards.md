# Coding Standards

Critical rules for AI agents to prevent common mistakes and ensure consistency across the automation codebase.

## 🔴 CRITICAL: Python Execution Rules

- **ALWAYS Use uv:** ALL Python commands MUST be prefixed with `uv run` (e.g., `uv run python script.py`, `uv run pytest`)
- **NEVER run python directly:** Commands like `python script.py` or `pytest` will use wrong Python version and dependencies
- **Python Version:** Project is pinned to Python 3.11 via `.python-version` file - `uv run` respects this automatically
- **Dependency Management:** Use `uv add`, `uv sync`, and `uv lock` - never pip directly
- **Version Verification:** Before running tests or scripts, verify with `uv run python --version` (should show 3.11.x)

## Critical Automation Rules

- **Environment Variable Access:** Always access through ConfigurationManager, never os.environ directly to ensure validation and type conversion
- **Browser Resource Management:** Always use context managers or try/finally blocks for browser cleanup to prevent resource leaks
- **Secret Handling:** Never log credentials or tokens, always use secret redaction in logging configuration
- **Element Detection:** Always implement timeout and retry logic for DOM element detection due to dynamic loading
- **Error Context:** All exceptions must include sufficient context for debugging without exposing sensitive information
- **State Consistency:** Always log execution results even on failure to maintain success rate tracking accuracy

## Naming Conventions

| Element | Frontend | Backend | Example |
|---------|----------|---------|---------|
| Classes | N/A | PascalCase | `AutomationOrchestrator` |
| Functions | N/A | snake_case | `execute_checkin()` |
| Constants | N/A | UPPER_SNAKE_CASE | `MAX_RETRY_ATTEMPTS` |
| Files | N/A | snake_case | `reward_detector.py` |
| Environment Variables | N/A | UPPER_SNAKE_CASE | `HOYOLAB_LTUID` |
