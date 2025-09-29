# Project Brief: Genshin Impact Check-in Bot

## Executive Summary

The Genshin Impact Check-in Bot is a consistency-focused automation solution that maintains HoYoLAB daily reward collection while serving as a practical showcase of modern DevOps automation practices. The project addresses the specific pain point where dedicated Genshin Impact players lose valuable streak-based rewards due to travel, busy schedules, or forgetting the daily routine, while acknowledging the inherent security and maintenance trade-offs of any credential-based automation.

The target market consists of technically-inclined, optimization-focused Genshin Impact players who value both systematic reward collection and the learning experience of building robust automation systems. The key value proposition is providing a "set-and-forget" consistency system that maintains reward streaks during unavailable periods while serving as a portfolio-worthy demonstration of GitHub Actions, web automation, and security best practices - essentially solving both gaming consistency and professional skill development with one solution.

## Problem Statement

Dedicated Genshin Impact players who prioritize progression optimization face a consistency challenge with HoYoLAB's daily check-in system: maintaining reward streak collection requires daily attention that conflicts with travel, busy periods, and varying schedules.

While the manual check-in process takes only 30 seconds, the cognitive load of remembering daily execution over months creates friction for systematic players. Missing check-ins breaks progression streaks, particularly frustrating for players who have established consistent gaming routines and view reward optimization as part of their engagement strategy.

Current reminder solutions (bookmarks, phone alerts) address memory but don't solve execution barriers during unavailable periods. The impact varies significantly by player type - casual players may not experience this as problematic, but optimization-focused players report frustration with broken consistency during periods when manual check-ins aren't practical.

This problem primarily affects a subset of committed players who have invested in systematic gameplay approaches and value consistency in their gaming routines. The automation solution acknowledges this is a niche optimization challenge rather than a universal gaming problem, with the added benefit of serving as a practical learning platform for modern DevOps and automation practices.

## Proposed Solution

The Genshin Impact Check-in Bot implements a GitHub Actions-based automation experiment that attempts to maintain HoYoLAB daily check-ins while acknowledging significant technical and operational risks. The solution uses browser automation (Selenium) for web interaction, recognizing this approach is inherently brittle to website changes, bot detection measures, and cloud execution environment variability.

The core approach addresses four automation steps: credential-based authentication (with acknowledged security trade-offs), web navigation (vulnerable to UI changes), CSS-based reward detection (fragile to front-end updates), and result confirmation (subject to timing issues). The system includes multiple trigger mechanisms and retry logic, though these add complexity rather than guaranteed reliability.

Key characteristics include security trade-offs inherent in cloud credential storage, CSS selector dependencies that may break without notice, and browser automation patterns that websites may actively discourage or block. The solution prioritizes learning value over production reliability, positioning this as an educational project rather than a dependable service.

The system addresses availability barriers by shifting execution to cloud environments, while introducing new failure modes including GitHub service dependencies, automation script maintenance, and debugging overhead. The realistic vision positions this as a technical learning exercise that may solve consistency problems when working correctly, while building valuable automation skills and demonstrating modern CI/CD patterns.

## Target Users

### Primary User Segment: Developer-Gamers with Automation Interest

**Demographic Profile:** Software professionals aged 22-40 who already use GitHub for work/personal projects and are specifically interested in applying automation skills to personal use cases. This intersection is smaller than initially assumed - many developers prefer keeping gaming and work tools separate.

**Current Behaviors:** May automate work tasks but view gaming as a manual relaxation activity. Those interested in gaming automation likely already have personal automation projects and are comfortable with setup complexity. They evaluate solutions based on technical merit and learning value rather than pure convenience.

**Specific Needs:** Primarily interested in the technical challenge and portfolio value rather than desperate for gaming convenience. Need well-documented code they can understand, modify, and potentially showcase. Value the automation learning experience more than the gaming outcome.

**Goals:** Build automation skills in a low-stakes environment, create a portfolio project that demonstrates practical problem-solving, and potentially solve a minor gaming inconvenience as a bonus outcome.

**Market Reality Check:** The intersection of "Genshin Impact players" + "GitHub comfortable" + "wants automation" + "willing to set up credentials" is estimated at 50-200 people globally. Success metrics should focus on technical quality and learning value rather than user adoption numbers.

## Goals & Success Metrics

### Business Objectives
- **Learning Project Completion:** Successfully implement basic automation functionality within 6-10 weeks, acknowledging that technical roadblocks may extend timeline significantly
- **Technical Skill Development:** Gain hands-on experience with GitHub Actions, web automation, and credential management, regardless of final reliability metrics
- **Documentation Quality:** Create comprehensive setup guide that enables at least 1-2 technically proficient users to replicate the setup successfully
- **Honest Technical Assessment:** Document real-world challenges, failure modes, and lessons learned to provide value even if automation proves unreliable

### User Success Metrics
- **Minimum Viable Automation:** Achieve any measurable automation success rate above manual baseline, acknowledging 30-50% reliability may be realistic ceiling
- **Setup Feasibility:** Enable at least one other technically qualified user to successfully complete setup using provided documentation
- **Learning Value Delivery:** Users report gaining practical automation experience regardless of gaming outcome reliability
- **Realistic Expectations:** Users understand this is an experimental learning project, not a production service

### Key Performance Indicators (KPIs)
- **Technical Achievement:** Binary success/failure of implementing each planned feature (authentication, navigation, detection, confirmation)
- **Problem-Solving Documentation:** Quality and completeness of troubleshooting guides based on encountered issues
- **Learning Artifact Quality:** Code readability, documentation completeness, and educational value for future reference
- **Honest Reliability Reporting:** Transparent tracking and reporting of actual success rates without inflated targets
- **Security Practice Implementation:** Successful implementation of credential management best practices, regardless of user adoption

## MVP Scope

### Core Features (Must Have)

- **Local Proof of Concept:** Python script using Selenium WebDriver that successfully completes one full HoYoLAB check-in process locally, proving core technical feasibility before cloud complexity

- **CSS-Based Reward Detection:** Intelligent reward state detection using discovered CSS classes (`actived-day` + `red-point`) to identify claimable rewards and avoid unnecessary actions when rewards are already claimed

- **Basic GitHub Actions Integration:** Simple workflow that runs the proven local script in GitHub Actions environment with scheduled daily execution at 6 AM PHT

- **Secure Credential Management:** GitHub Secrets integration for encrypted storage of HoYoLAB login credentials with proper environment variable handling and no credential exposure in logs

- **Essential Error Handling:** Basic try/catch logic, screenshot capture on failures for debugging, and clear success/failure logging to enable troubleshooting

- **Setup Documentation:** Clear instructions for repository setup, secrets configuration, and local testing to enable replication

### Out of Scope for MVP

- Multi-trigger systems or manual workflow dispatch
- Advanced retry logic with exponential backoff
- Monitoring dashboards, analytics, or success rate tracking
- Session persistence optimization or lightweight HTTP alternatives
- Multiple game support or extensible framework architecture
- Community features, notifications, or external service integrations

### MVP Success Criteria

The MVP succeeds when it demonstrates technical feasibility through local execution, then successfully migrates to GitHub Actions for at least one automated check-in. Success includes basic error logging that enables debugging when automation fails, and documentation sufficient for technical users to replicate the setup without direct support.

**Success Philosophy:** This is a learning-focused technical experiment that validates automation feasibility while building practical GitHub Actions and web automation skills, with any reliable gaming automation being a valuable bonus outcome.

## Technical Considerations

### Platform Requirements
- **Target Platforms:** GitHub Actions (Ubuntu latest), local development on macOS/Windows/Linux
- **Browser Support:** Chrome/Chromium headless mode for Selenium automation
- **Performance Requirements:** Complete check-in process within 5-minute GitHub Actions timeout limit

### Technology Preferences
- **Frontend:** Web automation via Selenium WebDriver (Python)
- **Backend:** Python 3.9+ with selenium, requests libraries
- **Database:** None required for MVP (file-based logging only)
- **Hosting/Infrastructure:** GitHub Actions (free tier sufficient for single-user daily execution)

### Architecture Considerations
- **Repository Structure:** Single repository with clear separation of automation scripts, workflows, and documentation
- **Service Architecture:** Monolithic script approach for MVP simplicity, designed for easy local testing and cloud execution
- **Integration Requirements:** GitHub Secrets API for credential management, HoYoLAB web interface interaction
- **Security/Compliance:** Follow GitHub security best practices for credential storage, no local credential persistence

## Constraints & Assumptions

### Constraints
- **Budget:** $0 - Must work within GitHub Actions free tier (2000 minutes/month)
- **Timeline:** 6-10 weeks for MVP completion, acknowledging learning curve and technical roadblocks
- **Resources:** Single developer with limited HoYoLAB automation experience, relying on documentation and community resources
- **Technical:** GitHub Actions environment limitations, HoYoLAB anti-bot measures, Selenium reliability in headless cloud environments

### Key Assumptions
- HoYoLAB will continue supporting email/password authentication without major changes
- Current CSS class structure for reward detection will remain stable during development period
- GitHub Actions environment can reliably run Selenium with Chrome headless browser
- Target users have basic GitHub familiarity and can follow technical setup instructions
- Project value lies primarily in learning experience rather than production gaming automation

## Risks & Open Questions

### Key Risks
- **Technical Feasibility:** HoYoLAB may implement bot detection or CAPTCHA that prevents automation entirely
- **Platform Dependency:** GitHub Actions changes or outages could break automation without alternative execution environment
- **Maintenance Overhead:** Website changes may require frequent script updates, exceeding available maintenance time
- **Security Exposure:** Credential management errors could compromise user gaming accounts
- **Learning ROI:** Time investment may exceed educational value if technical challenges prove too complex

### Open Questions
- How frequently does HoYoLAB update their web interface and break automation scripts?
- What specific anti-bot measures does HoYoLAB currently implement or may implement?
- Can GitHub Actions environment reliably run headless browser automation long-term?
- What is the actual overlap between Genshin Impact players and developers interested in automation projects?
- Would alternative approaches (browser extension, mobile app automation) be more reliable?

### Areas Needing Further Research
- HoYoLAB Terms of Service regarding automated access and account security implications
- Alternative authentication methods (session tokens, mobile app APIs) that might be more stable
- Comparison of automation reliability between different web automation tools (Selenium vs Playwright vs Puppeteer)
- Community feedback on gaming automation projects and what makes them successful vs abandoned

## Next Steps

### Immediate Actions
1. **Technical Validation:** Create local Python environment and test basic HoYoLAB login automation to validate core feasibility
2. **Repository Setup:** Initialize GitHub repository with proper structure for code, documentation, and workflows
3. **Documentation Framework:** Create README and setup guide templates based on anticipated user needs
4. **Community Research:** Survey existing gaming automation projects to understand common patterns and failure modes

### PM Handoff

This Project Brief provides comprehensive context for the Genshin Impact Check-in Bot learning project. The next phase involves systematic technical implementation following the MVP scope, with emphasis on documenting challenges and lessons learned throughout the development process. Success metrics focus on educational value and technical skill development rather than production reliability or user adoption.