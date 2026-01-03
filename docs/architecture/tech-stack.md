# Tech Stack

This is the DEFINITIVE technology selection for the entire project. All development must use these exact versions.

| Category | Technology | Version | Purpose | Rationale |
|----------|------------|---------|---------|-----------|
| Backend Language | Python | 3.11+ | Core automation logic and browser control | Mature ecosystem for web automation, excellent library support, readable for educational goals, modern performance improvements |
| Browser Automation | Playwright | ^1.40.0 | Web automation framework | Superior reliability, excellent async support, built-in waiting strategies, automatic browser management, excellent debugging tools |
| Browser Engine | Chromium | Latest (via Playwright) | Headless browser execution | Consistent rendering, good GitHub Actions support, reliable automation target |
| HTTP Client | httpx | ^0.25.0 | API requests and session management | Async support, better than requests for automation, HTTP/2 support |
| Configuration Management | python-decouple | ^3.8 | Environment variable handling | Secure config management, no hardcoded secrets, type conversion support |
| Logging Framework | structlog | ^23.1.0 | Structured logging with context | JSON logging, excellent debugging, GitHub Actions compatibility |
| State Management | JSON (stdlib) | Built-in | Execution history and success tracking | Simple, readable, no external dependencies, GitHub-friendly storage |
| Testing Framework | pytest | ^7.4.0 | Unit and integration testing | Industry standard, excellent fixture support, parametrization capabilities |
| Browser Testing | pytest-playwright | ^0.4.0 | Browser automation testing | Seamless Playwright integration, async test support |
| Assertion Library | pytest (built-in) | ^7.4.0 | Test assertions and validation | Comprehensive assertion methods, clear error messages |
| Mocking Framework | pytest-mock | ^3.11.0 | Test isolation and mocking | Clean mock syntax, pytest integration, reduces external dependencies |
| Code Formatting | black | ^23.7.0 | Consistent code style | Opinionated formatting, educational readability, industry adoption |
| Import Sorting | isort | ^5.12.0 | Import organization | Clean import structure, black compatibility |
| Linting | flake8 | ^6.0.0 | Code quality enforcement | Catches common errors, educational best practices |
| Type Checking | mypy | ^1.5.0 | Static type analysis | Type safety, better IDE support, documentation through types |
| Package Manager | uv | Latest | Fast Python package and project manager | 10-100x faster than pip, built in Rust, modern tooling, lock files for reproducibility |
| Dependency Management | pyproject.toml + uv.lock | PEP 621 | Dependency specification and locking | Modern Python standard, single source of truth, exact reproducibility across environments |
| CI/CD Platform | GitHub Actions | N/A | Automation scheduling and execution | Zero-cost, integrated secrets, Ubuntu environment, cron scheduling, uv native support |
| Secret Management | GitHub Secrets | N/A | Secure credential storage | Built-in encryption, environment variable injection, audit logging |
| Documentation | Markdown + GitHub Pages | N/A | Project documentation and guides | GitHub integration, zero-cost hosting, version control |
| Container Runtime | Docker (optional) | ^24.0.0 | Local development consistency | Optional for environment consistency, GitHub Actions has native support |
| Notification System | GitHub Actions Status | N/A | Success/failure alerting | Built-in workflow notifications, email integration available |

---

## Implementation Notes

**Module Consolidation:** Some modules were consolidated during implementation for simplicity:
- `src/config/validation.py` → Integrated into `src/config/manager.py`
- `src/state/analytics.py` → Integrated into `src/state/manager.py`
- `src/automation/workflows.py` → Integrated into `src/automation/orchestrator.py`
- `.github/workflows/manual-trigger.yml` → Integrated into `.github/workflows/daily-checkin.yml` (workflow_dispatch)

This consolidation maintains all documented functionality while reducing file complexity.

**Framework Simplification:** Selenium WebDriver was removed from the project as Playwright proved reliable and consistent. The project now uses Playwright exclusively for browser automation.

**CLI Entry Point:** Added `src/__main__.py` for direct module execution via `uv run python -m src`

**Additional Files:** Implementation includes `.github/UV_QUICKREF.md` and `.github/COMMIT_CONVENTION.md` for development workflow documentation.
