# Coding Standards

Critical rules for AI agents to prevent common mistakes and ensure consistency across the automation codebase.

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
