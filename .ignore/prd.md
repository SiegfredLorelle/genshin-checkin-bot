# Genshin Impact Check-in Bot Product Requirements Document (PRD)

## Goals and Background Context

### Goals
- Successfully implement basic automation functionality that maintains HoYoLAB daily check-in streaks for Genshin Impact players with **minimum 70% success rate over 30-day periods**
- Gain hands-on experience with GitHub Actions, web automation, and secure credential management practices
- Create comprehensive documentation that enables technically proficient users to replicate the automation setup
- Build a portfolio-worthy demonstration of modern DevOps automation patterns and security best practices
- **Validate core assumptions with at least 3 target users before Epic 2** to ensure market fit
- Document real-world challenges, failure modes, and lessons learned to provide educational value
- **Provide manual trigger fallback option** for critical streak maintenance during automation failures

### Background Context
The Genshin Impact Check-in Bot addresses a specific consistency challenge faced by dedicated Genshin Impact players: maintaining daily HoYoLAB reward streaks during travel, busy periods, or schedule conflicts. While manual check-ins take only 30 seconds, the cognitive load of daily execution over months creates friction for players who view reward collection as part of their gaming routine.

This project serves dual purposes - solving a gaming automation problem while providing practical learning opportunities in modern DevOps practices. The solution targets both optimization-focused players seeking systematic reward collection and convenience-focused players with technical aptitude who want reliable automation. The project acknowledges significant technical risks including website changes, bot detection measures, and cloud execution variability, while maintaining clear success criteria for both automation reliability AND educational value. When these goals conflict, automation reliability takes priority to ensure user value.

### Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-09-29 | v1.0 | Initial PRD creation from Project Brief with assumption testing refinements | John (PM) |
| 2025-09-29 | v1.1 | Updated to reflect progressive credential approach and Epic 1 local validation scope | Sarah (PO) |

## Requirements

### Functional

**FR1:** The system shall authenticate users to HoYoLAB using a progressive credential management approach: hardcoded credentials for initial MVP validation, then migration to GitHub Secrets with proper environment variable handling and no credential exposure in logs

**FR2:** The system shall navigate to the Genshin Impact daily check-in page on HoYoLAB web interface using browser automation

**FR3:** The system shall detect reward state using CSS-based detection (`actived-day` + `red-point` classes) to identify claimable rewards and avoid unnecessary actions when rewards are already claimed

**FR4:** The system shall claim available daily rewards through automated interaction with the check-in interface

**FR5:** The system shall provide clear success/failure logging with screenshot capture on failures for debugging purposes

**FR6:** The system shall run as a Python script using Selenium WebDriver that successfully completes the full HoYoLAB check-in process locally

**FR7:** The system shall be designed for future GitHub Actions integration for scheduled daily execution at 6 AM PHT in a cloud environment, with initial Epic 1 focusing on local validation only

**FR8:** The system shall provide manual trigger fallback option for critical streak maintenance during automation failures

**FR9:** The system shall complete the entire check-in process within GitHub Actions' 5-minute timeout limit

### Non Functional

**NFR1:** The system must achieve minimum 70% automation success rate over 30-day periods to provide meaningful value over manual process

**NFR2:** GitHub Actions usage must stay within free tier limits (2000 minutes/month) to maintain zero-cost operation

**NFR3:** The system must handle credential storage using GitHub security best practices with no local credential persistence

**NFR4:** The system must provide comprehensive setup documentation that enables technically qualified users to replicate setup without direct support

**NFR5:** Browser automation must work reliably in GitHub Actions Ubuntu environment using Chrome/Chromium headless mode

**NFR6:** The system must implement basic error handling with try/catch logic to gracefully handle common failure scenarios

**NFR7:** The system must be designed for easy local testing and debugging before cloud deployment

**NFR8:** Code must maintain readability and educational value suitable for portfolio demonstration and learning purposes

## Technical Assumptions

### Repository Structure: **Monorepo**
Single repository containing all automation scripts, workflows, documentation, and configuration files. This approach simplifies setup, version control, and user onboarding while maintaining clear separation between components through directory structure.

**Rationale:** For a single-purpose automation tool with limited scope, monorepo reduces complexity and aligns with the educational goals. Users can clone one repository and have everything needed.

### Service Architecture
**Monolithic script approach within GitHub Actions environment.** The automation runs as a single Python script that handles the complete workflow from authentication through reward collection in one execution.

**Rationale:** Given the MVP scope and 5-minute execution window, a monolith provides simplicity and reduces inter-service communication overhead. The automation workflow is linear and doesn't benefit from service decomposition.

### Testing Requirements
**Unit testing for core functions + Integration testing for HoYoLAB interaction.** Focus on testing CSS selector logic, credential handling, and error scenarios locally before cloud deployment.

**Rationale:** The brittle nature of web automation requires robust testing of the core detection logic. Integration tests ensure the automation works against the live website, while unit tests enable rapid local development.

### Additional Technical Assumptions and Requests

- **Language & Runtime:** Python 3.9+ with exact version pinning in GitHub Actions and local development for environment consistency
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

## Epic List

### Epic 1: **Foundation & Local Proof of Concept**
Establish project infrastructure, local development environment, and demonstrate core automation feasibility through successful local HoYoLAB check-in execution using hardcoded credentials. Focus on local validation only - cloud deployment deferred to Epic 3.

**Key Risks:** HoYoLAB interface complexity, browser automation setup challenges, immediate anti-bot detection

### Epic 2: **Core Automation Engine**  
Build reliable reward detection and claiming logic with comprehensive error handling, state tracking, and user validation of core assumptions.

**Key Risks:** CSS selector stability, reward detection accuracy, finding qualified test users

### Epic 3: **Cloud Deployment & Scheduling**
Migrate proven local automation to GitHub Actions with GitHub Secrets credential management, scheduled execution, and monitoring capabilities. Includes cloud environment validation previously planned for Epic 1.

**Key Risks:** Cloud environment differences, network reliability, GitHub Actions resource limitations, credential migration complexity

### Epic 4: **Production Readiness & Documentation**
Implement manual fallback options, comprehensive user documentation, and educational content to enable independent setup and operation.

**Key Risks:** Documentation maintenance overhead, user support burden, cross-platform compatibility

**Epic Structure Rationale:**

**Epic 1** establishes the critical foundation - without a working local proof of concept, cloud deployment is premature. This epic delivers immediate value through local automation while building essential project infrastructure. Risk mitigation focuses on early HoYoLAB compatibility validation and isolated test account usage.

**Epic 2** focuses on reliability and user validation before cloud complexity. The 70% success rate requirement can only be validated with robust core automation and real user feedback. Risk mitigation includes multiple CSS selector strategies and comprehensive test coverage.

**Epic 3** addresses the cloud deployment challenge once local automation is proven. This separation allows for focused debugging of cloud-specific issues without fighting core automation problems simultaneously. Risk mitigation emphasizes extensive cloud environment testing and resource monitoring.

**Epic 4** completes the user experience with safety nets and documentation. Manual fallback ensures users aren't stranded when automation fails, while comprehensive docs enable the educational goals. Risk mitigation includes automated documentation testing and clear support boundaries.

Each epic delivers deployable, testable functionality that provides value even if subsequent epics are delayed or descoped. The structure follows the technical assumptions' implementation sequence and addresses the highest-risk elements (HoYoLAB compatibility) first.

## Epic 1 Foundation & Local Proof of Concept

**Epic Goal:** Establish core automation feasibility and basic project infrastructure by validating HoYoLAB automation potential before significant investment, then building the minimal viable local automation that successfully completes check-ins. This epic proves technical viability while creating essential development foundation for subsequent work.

### Story 1.1: **HoYoLAB Feasibility Validation**

As a developer,
I want to quickly validate that HoYoLAB automation is technically possible,
so that I can confirm project viability before investing in full infrastructure setup.

#### Acceptance Criteria
**1:** Manual exploration of HoYoLAB check-in interface is completed with screenshots documenting the complete user workflow
**2:** Initial assessment of anti-bot measures, CAPTCHA requirements, and authentication complexity is documented
**3:** CSS inspection reveals reward detection elements and their class structure (`actived-day`, `red-point`, or alternatives)
**4:** Network request analysis shows authentication requirements, required headers, and session management needs
**5:** Decision point reached: Continue with automation development or pivot based on feasibility findings

### Story 1.2: **Project Setup and Development Environment**

As a developer,
I want to establish a clean project structure with proper Python environment management,
so that I can develop and test the automation with consistent dependencies and professional organization.

#### Acceptance Criteria
**1:** Repository contains organized directory structure separating source code, tests, documentation, and configuration
**2:** Python virtual environment configured with requirements.txt specifying exact versions for automation libraries
**3:** Basic README.md provides local setup instructions including hardcoded credential configuration for MVP testing
**4:** Git repository includes .gitignore excluding credentials, virtual environments, cache files, and browser artifacts
**5:** Project includes structured logging configuration suitable for both development debugging and production operation

### Story 1.3: **Integrated Browser Automation and Research**

As a developer,
I want to implement browser automation that can navigate HoYoLAB and analyze the interface dynamically,
so that I can build adaptive automation based on real-time interface analysis rather than assumptions.

#### Acceptance Criteria
**1:** Browser automation successfully launches headless Chrome/Chromium and navigates to HoYoLAB login page
**2:** Authentication flow completes using hardcoded credentials for initial MVP validation (personal account with careful procedures)
**3:** Dynamic CSS selector discovery identifies multiple potential reward detection strategies with fallback options
**4:** Script implements proper wait conditions, screenshot capture, and graceful error handling for common failures
**5:** Automation generates detailed interface analysis report documenting discovered selectors, timing requirements, and potential bot detection measures

### Story 1.4: **Reward Detection and Claiming Workflow**

As a developer,
I want to implement intelligent reward detection and claiming as an integrated workflow,
so that the complete check-in automation works reliably from authentication through reward collection.

#### Acceptance Criteria
**1:** Reward detection accurately identifies claimable vs. already-claimed rewards using discovered CSS selectors with fallback strategies
**2:** Reward claiming automation handles button clicks, confirmation dialogs, and UI state changes with appropriate timing delays
**3:** Complete workflow verification confirms successful reward claiming through UI feedback and state validation
**4:** Error handling covers network timeouts, element not found, authentication failures, and unexpected UI changes
**5:** End-to-end automation runs successfully from login through reward claiming with comprehensive logging and cleanup

### Story 1.5: **Essential Local Testing and Validation**

As a developer,
I want comprehensive local testing capabilities,
so that I can ensure the automation works correctly and is ready for future cloud deployment.

#### Acceptance Criteria
**1:** Unit tests validate core functions including CSS selector logic, credential handling, and error scenarios
**2:** Integration test confirms complete automation workflow against live HoYoLAB interface with success/failure reporting
**3:** Test framework provides clear pass/fail reporting with screenshot evidence for debugging
**4:** Local validation confirms automation handles common failure scenarios (service downtime, interface changes) with appropriate logging
**5:** Documentation includes testing procedures and validation checklist for manual verification

**Refined Epic 1 Rationale:** This approach validates core feasibility first with hardcoded credentials for rapid MVP validation, combines related research and implementation work to reduce context switching, and focuses on local testing excellence. The story sequence follows a logical progression from risk validation through working automation, with each story delivering testable value. Story sizing is optimized for AI agent execution while maintaining comprehensive acceptance criteria. Cloud deployment complexity is deferred to Epic 3 for focused implementation.

**Key assumption updates:** Hardcoded credentials for MVP validation with migration to GitHub Secrets in Epic 3, multiple detection strategies planned from start, local testing focus with cloud deployment deferred, and story granularity balanced for AI agent capabilities.

## Epic 2 Core Automation Engine

**Epic Goal:** Build reliable, production-ready automation with comprehensive error handling, state tracking, and user validation. This epic transforms the proof of concept into a robust system that meets the 70% success rate requirement through enhanced reliability, user feedback integration, and systematic improvement.

*[Detailed stories would follow the same pattern as Epic 1, focusing on reliability enhancement, state management, user validation with 3 target users, and comprehensive error handling]*

## Epic 3 Cloud Deployment & Scheduling  

**Epic Goal:** Successfully migrate proven local automation to GitHub Actions with secure credential management, reliable scheduled execution, and monitoring. This epic addresses cloud-specific challenges while maintaining automation reliability and staying within free tier constraints.

*[Detailed stories would cover GitHub Actions workflow setup, credential security implementation, scheduling configuration, cloud-specific optimizations, and monitoring/alerting]*

## Epic 4 Production Readiness & Documentation

**Epic Goal:** Complete the user experience with manual fallback options, comprehensive documentation, and educational content that enables independent setup and operation. This epic ensures users can successfully adopt and maintain the automation while achieving the educational goals.

*[Detailed stories would include manual trigger implementation, comprehensive setup documentation, troubleshooting guides, educational content creation, and user onboarding optimization]*

## Next Steps

### UX Expert Prompt
*Note: This section intentionally left minimal as the project is primarily backend automation with limited UI requirements.*

### Architect Prompt
Review this PRD and create a comprehensive technical architecture document that addresses the requirements, technical assumptions, and epic structure. Focus on browser automation patterns, GitHub Actions integration, security best practices, and maintainable code organization that supports the educational goals while achieving reliable HoYoLAB check-in automation.