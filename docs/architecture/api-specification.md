# API Specification

Based on the architectural analysis and tech stack selection, this project operates as a **monolithic automation script** without traditional API endpoints. However, the system interfaces with external APIs and internal configuration that requires specification.

## HoYoLAB Web Interface Integration

**Purpose:** Document the web interface interactions that the automation performs, serving as both API documentation and integration contract.

**Base URL:** `https://act.hoyolab.com/`

**Authentication Method:** Cookie-based session authentication with CSRF protection

**Key Interface Points:**

**Check-in Page Navigation:**
- **URL Pattern:** `/ys/event/signin-sea-v3/index.html?act_id={ACT_ID}`
- **Method:** GET (Browser navigation)
- **Authentication:** Required - Session cookies from login flow
- **Purpose:** Navigate to Genshin Impact daily check-in interface

**Reward State Detection:**
- **Interface Type:** DOM element inspection
- **Detection Selectors:** 
  - Primary: `.calendar-container .today-sign` (current day indicator)
  - Fallback 1: `[data-testid="check-in-button"]` 
  - Fallback 2: `.sign-in-btn:not(.disabled)`
- **Response Analysis:** Element presence and CSS classes determine reward availability

**Reward Claiming Action:**
- **Interface Type:** DOM interaction (click event)
- **Target Selector:** Dynamically determined from detection phase
- **Expected Response:** UI state change + success/error message display
- **Validation:** Post-action DOM inspection for confirmation

## Configuration API (Environment Variables)

**Required Environment Variables:**
```bash
# Authentication (GitHub Secrets in production)
HOYOLAB_LTUID=123456789              # HoYoLAB user ID
HOYOLAB_LTOKEN=abcdef123456789       # HoYoLAB auth token

# Automation Configuration
CHECKIN_URL=https://act.hoyolab.com/ys/event/signin-sea-v3/index.html
ACT_ID=e202102251931481             # Activity ID for Genshin Impact check-in
USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)..."

# Timing Configuration (seconds)
MIN_DELAY=2.0                       # Minimum wait between actions
MAX_DELAY=8.0                       # Maximum wait between actions  
PAGE_LOAD_TIMEOUT=30.0              # Maximum page load wait time
ELEMENT_TIMEOUT=15.0                # Maximum element detection wait time

# CSS Selector Configuration (fallback strategies)
PRIMARY_SELECTOR=".calendar-container .today-sign"
FALLBACK_SELECTOR_1="[data-testid='check-in-button']"
FALLBACK_SELECTOR_2=".sign-in-btn:not(.disabled)"

# Logging Configuration
LOG_LEVEL=INFO                      # DEBUG, INFO, WARNING, ERROR
SCREENSHOT_ON_FAILURE=true          # Capture failure screenshots
LOG_DOM_SNAPSHOTS=false            # Include DOM content in logs (debug only)
```
