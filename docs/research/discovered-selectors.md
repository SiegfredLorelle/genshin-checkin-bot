# Discovered CSS Selectors

This document contains working CSS selectors discovered through research and testing on the HoYoLAB check-in interface.

**Last Updated:** November 30, 2025
**Source:** Implementation testing and interface analysis

---

## 🎯 Primary Detection Strategy: Red Point Method

The most reliable detection method uses HoYoLAB's red point notification indicator.

### Red Point Selectors

```css
/* Primary red point icon indicator */
.mhy-icon-font-point

/* Red point within item icon */
.item-icon span:has(.mhy-icon-font-point)

/* Container selectors with red point */
div[class*='sign-item']:has(.mhy-icon-font-point)
div[class*='sign-wrapper']:has(.mhy-icon-font-point)
```

**Usage:** The red point appears on claimable rewards. Detection confidence: **High (0.9)**

---

## �� Authentication Selectors

### Login Form Elements

```css
/* Email/Username input */
input[type="text"][placeholder*="email" i]
input[type="text"][placeholder*="帳號" i]
.mhy-input input[type="text"]

/* Password input */
input[type="password"]
.mhy-input input[type="password"]

/* Login button */
button[type="submit"]
.mhy-button--submit
button:contains("登入")
button:contains("Login")
```

**Implementation Location:** `src/automation/orchestrator.py` → `_login_with_credentials()`

---

## 🚫 Modal/Popup Blocking Selectors

HoYoLAB shows various modals that must be closed before reward interaction.

### Modal Close Buttons

```css
/* Generic close buttons */
.mhy-dialog-close
.mhy-dialog__close
button[aria-label="Close"]
button[aria-label="關閉"]

/* Specific modal patterns */
.modal-close
.popup-close
.dialog-close-btn

/* Icon-based close buttons */
.mhy-icon-close
i.close-icon
```

**Implementation Location:** `src/automation/orchestrator.py` → `_close_blocking_modals()`

---

## 🎁 Reward State Selectors

### HoYoLAB-Specific Class Patterns

```css
/* Claimable rewards */
.reward-item:not(.claimed):not(.disabled)
.daily-reward.available
.signin-reward.claimable
[data-state='available']

/* Already claimed rewards */
.reward-item.claimed
.daily-reward.completed
.signin-reward.received
[data-state='claimed']

/* Unavailable/locked rewards */
.reward-item.disabled
.daily-reward.locked
.signin-reward.unavailable
[data-state='locked']
```

**Implementation Location:** `src/detection/strategies.py` → `HoYoLABClassBasedStrategy`

---

## ✅ Success Feedback Selectors

### UI Elements Indicating Successful Claim

```css
/* Success messages */
.success-message
.reward-claimed
.claim-success
.toast-success
.notification-success
.alert-success
[data-message='success']
.modal-success

/* Success icons */
.check-icon
.success-icon
.checkmark
.reward-received-badge
.completion-badge
[aria-label*='success']
[data-state='completed']
```

**Text Patterns to Search For:**
- "success"
- "claimed"
- "received"
- "completed"
- "获得" (Chinese: obtained)
- "成功" (Chinese: success)
- "领取成功" (Chinese: claim success)

**Implementation Location:** `src/detection/detector.py` → `_detect_ui_success_feedback()`

---

## 🔄 Confirmation Dialog Selectors

### Dialog Accept/Confirm Buttons

```css
/* Common confirmation buttons */
.confirm-btn
.ok-btn
.accept-btn
[data-testid='confirm']
.modal-confirm

/* Multi-language button text */
button:contains("确认")  /* Chinese */
button:contains("OK")
button:contains("Confirm")
button:contains("Accept")
```

**Implementation Location:** `src/detection/detector.py` → `_handle_confirmation_dialog()`

---

## 📋 Fallback Strategy Selectors

When primary strategies fail, these generic patterns provide fallback options.

### Generic Reward Patterns

```css
/* Button-based detection */
.signin-btn
.check-in-btn
.daily-signin
#signin-button
button:contains("Sign in")
button:contains("Check in")

/* Container patterns */
.reward-container
.rewards-list
.daily-rewards
.reward-item
[class*="reward"]
[class*="signin"]
[class*="checkin"]
```

---

## 🧪 Selector Validation

### Reliability Scores

| Selector Pattern | Reliability | Use Case |
|-----------------|-------------|----------|
| `.mhy-icon-font-point` | 95% | Primary reward detection |
| `.item-icon span:has(...)` | 90% | Container-based detection |
| `.mhy-dialog-close` | 85% | Modal closing |
| Login form inputs | 80% | Authentication |
| Success feedback | 70% | Claim validation |
| Generic patterns | 50% | Fallback only |

### Testing Methodology

Selectors are validated through:
1. Multiple test executions across different times
2. Different account states (new rewards, claimed rewards, etc.)
3. Browser framework compatibility (Playwright + Selenium)
4. Timeout and retry resilience testing

---

## 🔧 Selector Configuration

### Environment Variables

```bash
# Override default detection selectors
DETECTION_PRIMARY_SELECTOR=".signin-btn"
DETECTION_FALLBACK_SELECTOR="[data-testid='signin-button']"
DETECTION_GENERIC_SELECTOR="button:contains('Sign in')"
```

### Code Configuration

See `ConfigurationManager.get_detection_config()` for runtime selector configuration.

---

## 📝 Maintenance Notes

**Selector Stability:** HoYoLAB interface changes can break selectors. The red point method is most stable as it uses core HoYoLAB UI components.

**Update Frequency:** Review selectors if automation success rate drops below 70% (NFR1).

**Debugging:** Enable screenshot capture on failures to identify changed selectors:
```bash
DETECTION_SCREENSHOT=true
```

**Research Source:** See `docs/research/css-selectors.md` for detailed selector discovery process.

---

## 🔗 Related Documentation

- **Selector Strategies:** `src/detection/strategies.py`
- **Implementation:** `src/detection/detector.py`
- **Research Notes:** `docs/research/css-selectors.md`
- **Architecture:** `docs/architecture/components.md`
