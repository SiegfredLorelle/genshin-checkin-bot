# Technical Assumptions

## Repository Structure: **Monorepo**
Single repository containing all automation scripts, workflows, documentation, and configuration files. This approach simplifies setup, version control, and user onboarding while maintaining clear separation between components through directory structure.

**Rationale:** For a single-purpose automation tool with limited scope, monorepo reduces complexity and aligns with the educational goals. Users can clone one repository and have everything needed.

## Service Architecture
**Monolithic script approach within GitHub Actions environment.** The automation runs as a single Python script that handles the complete workflow from authentication through reward collection in one execution.

**Rationale:** Given the MVP scope and 5-minute execution window, a monolith provides simplicity and reduces inter-service communication overhead. The automation workflow is linear and doesn't benefit from service decomposition.

## Testing Requirements
**Unit testing for core functions + Integration testing for HoYoLAB interaction.** Focus on testing CSS selector logic, credential handling, and error scenarios locally before cloud deployment.

**Rationale:** The brittle nature of web automation requires robust testing of the core detection logic. Integration tests ensure the automation works against the live website, while unit tests enable rapid local development.

## Additional Technical Assumptions and Requests

- **Language & Runtime:** Python 3.11+ with exact version pinning in GitHub Actions and local development for environment consistency
- **Browser Automation:** Evaluate Playwright vs Selenium WebDriver through prototype testing against actual HoYoLAB interface before architectural commitment
- **Anti-Bot Detection:** Implement randomized timing (2-8 second delays), realistic user-agent strings, and session cookie management to mitigate detection
- **Dependency Management:** pip with requirements.txt and exact version pinning, monthly security review of Python packages with automated dependency updates
- **State Management:** File-based JSON logging for execution history, success rate tracking, and failure pattern analysis to support NFR1 measurement
- **Network Resilience:** 3-retry policy with exponential backoff for network timeouts, configurable timeout values for different operations
- **Configuration Management:** Externalized CSS selectors, URLs, and timing parameters in environment variables to enable updates without code changes
- **Logging Framework:** Enhanced logging with automation-specific context including DOM snapshots, timing data, and screenshot capture for comprehensive debugging
- **Security Model:** GitHub Secrets for credential storage, no sensitive data in code or logs, secure session handling with automatic cleanup
- **Failure Notifications:** GitHub Actions workflow status provides basic alerting, with optional email integration for critical failures
- **Platform Support:** Primary support for macOS/Linux development environments, Windows support as best-effort with documented limitations
- **Performance Monitoring:** Track execution time and memory usage to stay within GitHub Actions resource limits, optimize for <2 minute typical execution
- **Environment Consistency:** Consider Docker containerization for reproducible execution environments across local and cloud deployment
- **Documentation Format:** Markdown-based README with step-by-step setup guide, troubleshooting section, architecture overview, and cross-platform setup instructions

**Rationale:** These expanded assumptions address the operational realities of web automation including failure modes, maintenance overhead, and user support needs. The choices prioritize long-term maintainability while working within GitHub Actions constraints and zero-cost operation requirements.
