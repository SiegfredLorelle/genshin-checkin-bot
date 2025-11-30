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
- [x] Research deployment options for cron scheduling:
  - ✅ GitHub Actions (SELECTED - free tier, 2000 min/month)
  - Vercel (not ideal for browser automation)
  - Render (possible alternative)
  - Other alternatives (Railway, Fly.io, etc.)
- [x] Determine storage solution for logs and screenshots:
  - ✅ GitHub Actions artifacts (SELECTED - 90 days logs, 30 days screenshots)
  - Cloud storage (S3, Cloudflare R2) — not needed
- [x] Evaluate cost, reliability, and maintenance for each option
- [x] Create GitHub Actions workflow file (`.github/workflows/daily-checkin.yml`)
- [x] Create comprehensive deployment documentation (`docs/DEPLOYMENT.md`)
- [x] Update README with deployment section and workflow badge
- [x] Test workflow in GitHub Actions (requires push to GitHub)
- [x] Configure GitHub Secrets for credentials
- [x] Run initial dry-run test
- [x] Run production test and verify in-game
- [x] **Document GitHub Actions Secrets vs Variables distinction**
  - ✅ Sensitive credentials (passwords, tokens) → Secrets tab (encrypted)
  - ✅ Non-sensitive config (URLs, settings) → Variables tab (plain text)
  - ✅ Workflow uses `${{ secrets.NAME }}` for Secrets, `${{ vars.NAME }}` for Variables
  - ✅ Added troubleshooting documentation for missing `act_id` parameter issue

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
- [ ] **Consider migrating from flake8 to Ruff**
  - Ruff is 10-100x faster than flake8
  - Single tool replaces flake8, isort, and more
  - Better error messages and modern Python support
  - Already using `uv` (same ecosystem)
- [ ] Refactor/shard code files with too many lines:
  - `src/detection/detector.py` (68 violations)
  - `src/automation/orchestrator.py` (16 violations)
  - Other files exceeding line limits
- [ ] Extract complex methods into smaller, focused functions
- [ ] Apply modular design patterns where appropriate
- [ ] Fix proper exit/cleanup after accepting rewards
  - Ensure graceful exit after successful reward claiming
  - Handle cleanup when reward is already claimed
  - Implement proper error handling and cleanup on failures
- [ ] **Fix validation failure causing workflow to report "success: false"**
  - Logs show reward claimed successfully (`"claiming_success": true`, `claims_processed: 1`)
  - But validation fails (`"claim_validated": false`, `validation_confidence: 0.36`)
  - Workflow reports `"success": false` in execution log despite reward being claimed
  - Issue: Validation logic may be checking wrong page state or timing out too early
  - Program may not be exiting properly after reward collection

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
