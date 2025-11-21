# TODO - Genshin Check-in Bot

> **Last Updated:** November 22, 2025
> **Project Status:** POC Complete, Planning Production Deployment

---

## 🎯 High Priority Tasks

### Epic/Story Evaluation
- [ ] Review which epic/stories are still needed considering our current working POC
- [ ] Identify gaps between POC and production requirements
- [ ] Prioritize remaining stories based on production readiness needs

### Deployment & Infrastructure
- [ ] Research deployment options for cron scheduling:
  - GitHub Actions/Pages
  - Vercel
  - Render
  - Other alternatives (Railway, Fly.io, etc.)
- [ ] Determine storage solution for logs and screenshots:
  - GitHub Actions artifacts
  - Cloud storage (S3, Cloudflare R2)
  - Integrated platform storage
- [ ] Evaluate cost, reliability, and maintenance for each option

### Notifications & Monitoring
- [ ] Implement failure notification system:
  - Email notifications
  - Discord webhooks
  - Other options (Slack, Telegram, etc.)
- [ ] Design notification strategy (immediate vs digest)
- [ ] Configure alert thresholds and conditions

### Authentication Review
- [ ] Investigate if cookies are still required for auth
- [ ] Test if login-only approach (without cookies) is sufficient
- [ ] Document auth flow simplification if possible
- [ ] Update authentication implementation based on findings

### Navigation Flow Improvements
- [ ] Start from HoYoLAB official page rather than direct check-in URL
- [ ] Navigate to check-in page through official links/buttons
- [ ] Avoid hardcoded check-in URLs with unknown parameters
- [ ] Document reliable navigation path from homepage to check-in
- [ ] Test stability of navigation-based approach vs direct URL

### Code Quality & Refactoring
- [ ] Refactor/shard code files with too many lines:
  - `src/detection/detector.py` (68 violations)
  - `src/automation/orchestrator.py` (16 violations)
  - Other files exceeding line limits
- [ ] Extract complex methods into smaller, focused functions
- [ ] Apply modular design patterns where appropriate

### Testing Improvements
- [ ] Create comprehensive end-to-end tests
  - Consider building a dummy/mock Genshin check-in page for testing
  - Test complete workflow from authentication to reward claiming
  - Cover failure scenarios and edge cases
- [ ] Validate test reliability and coverage

### Screenshot & Debugging
- [ ] Implement screenshot capture at every step of the process
  - Pre-authentication
  - Post-authentication
  - Reward detection
  - Before claiming
  - After claiming
  - Error states
- [ ] Organize screenshot storage and retention strategy

### Browser Configuration
- [ ] Test if headless mode works reliably for HoYoLAB
- [ ] Validate headless vs headed mode for production
- [ ] Document any limitations or anti-bot concerns with headless
- [ ] Configure optimal browser settings for deployment

### Anti-Bot Detection Enhancements
- [ ] Add random mouse movements to simulate human behavior
- [ ] Implement variable delays between actions (not fixed timing)
- [ ] Add random scroll patterns during page interaction
- [ ] Simulate human-like typing speed for login inputs
- [ ] Add occasional pauses/hesitations to mimic real user behavior
- [ ] Test effectiveness against bot detection systems

### Framework Consolidation
- [ ] Evaluate if both Playwright and Selenium are still needed
- [ ] Test production reliability with single framework
- [ ] Make recommendation to keep one or both
- [ ] Update implementation and remove unnecessary code if consolidating

### Documentation Updates
- [ ] Update architecture docs based on current POC implementation
- [ ] Update PRD to reflect production requirements
- [ ] Document implementation learnings and decisions
- [ ] Create deployment guide for chosen platform

---

## � Notes

- POC is functional with 103 passing tests
- Current blockers: 95 flake8 violations need resolution
- Python version needs alignment (3.9.23 → 3.11+)
- All Epic 1 stories technically complete but need production hardening
