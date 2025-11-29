# Unified Project Structure

The following monorepo structure accommodates the automation requirements while maintaining clear separation of concerns and supporting the educational goals.

```
genshin-checkin-bot/
├── .github/                    # CI/CD and documentation
│   ├── workflows/
│   │   ├── daily-checkin.yml   # Scheduled automation with manual trigger
│   │   └── commit-lint.yml     # Commit message validation
│   ├── COMMIT_CONVENTION.md    # Conventional commits guide
│   └── UV_QUICKREF.md          # uv package manager quick reference
├── src/                        # Core automation code
│   ├── __init__.py
│   ├── __main__.py             # CLI entry point
│   ├── automation/             # Main automation logic
│   │   ├── __init__.py
│   │   └── orchestrator.py     # AutomationOrchestrator (complete workflow)
│   ├── browser/                # Browser management
│   │   ├── __init__.py
│   │   ├── manager.py          # BrowserManager (abstract interface)
│   │   ├── playwright_impl.py  # Playwright implementation
│   │   └── selenium_impl.py    # Selenium fallback
│   ├── detection/              # Reward detection
│   │   ├── __init__.py
│   │   ├── detector.py         # RewardDetector (complete implementation)
│   │   └── strategies.py       # CSS selector strategies
│   ├── config/                 # Configuration management
│   │   ├── __init__.py
│   │   └── manager.py          # ConfigurationManager (includes validation)
│   ├── state/                  # State management
│   │   ├── __init__.py
│   │   └── manager.py          # StateManager (includes analytics)
│   └── utils/                  # Shared utilities
│       ├── __init__.py
│       ├── logging_config.py   # Structured logging setup
│       ├── timing.py          # Anti-bot timing utilities
│       └── exceptions.py       # Custom exception classes
├── tests/                      # Comprehensive test suite
│   ├── unit/                   # Unit tests
│   │   ├── test_orchestrator.py
│   │   ├── test_browser_manager.py
│   │   ├── test_reward_detector.py
│   │   ├── test_config_manager.py
│   │   └── test_state_manager.py
│   ├── integration/            # Integration tests
│   │   ├── test_hoyolab_integration.py
│   │   └── test_end_to_end.py
│   ├── fixtures/               # Test fixtures and data
│   │   ├── mock_responses/
│   │   └── test_configs/
│   └── conftest.py            # Pytest configuration
├── logs/                       # Execution history and state
│   ├── execution_history.jsonl # Main execution log
│   ├── screenshots/           # Failure screenshots
│   └── debug/                 # Debug logs (local only)
├── scripts/                    # Setup and maintenance scripts
│   ├── setup_dev_env.sh       # Development environment setup
│   ├── run_local_test.py      # Local testing script
│   └── analyze_success_rate.py # Success rate analysis
├── docs/                       # Documentation
│   ├── README.md              # Main setup and usage guide
│   ├── prd.md                 # Product Requirements Document
│   ├── architecture.md        # This architecture document
│   ├── TROUBLESHOOTING.md     # Common issues and solutions
│   └── SECURITY.md           # Security considerations
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
├── pytest.ini                 # Pytest configuration
├── mypy.ini                   # Type checking configuration
└── README.md                  # Project overview and quick start
```
