# GitHub Actions Troubleshooting Guide

Quick solutions for common GitHub Actions deployment issues.

## 🔍 Diagnostic Commands

Before troubleshooting, gather information:

```bash
# Check workflow syntax locally
cat .github/workflows/daily-checkin.yml

# Verify secrets are set (in GitHub UI)
Settings → Secrets and variables → Actions → Repository secrets

# Check recent workflow runs
Actions tab → Daily HoYoLAB Check-in → Recent runs
```

## 🚨 Common Issues & Solutions

### 1. Workflow Doesn't Appear in Actions Tab

**Symptoms:**
- "Daily HoYoLAB Check-in" not listed in Actions tab
- No workflows shown

**Causes & Solutions:**

**A. YAML syntax error:**
```bash
# Validate locally
cat .github/workflows/daily-checkin.yml | grep -E 'name:|on:|jobs:'

# Check for common issues:
- Indentation (must be 2 spaces, not tabs)
- Missing colons after keys
- Incorrect file location (must be .github/workflows/)
```

**B. Actions disabled:**
1. Settings → Actions → General
2. Select "Allow all actions and reusable workflows"
3. Click Save

**C. Branch issue:**
- Workflow files only appear when pushed to main/master branch
- Check: Actions tab → "There are no workflows" message

### 2. "Secret Not Found" Error

**Symptoms:**
```bash
Error: The secret `HOYOLAB_LTUID` has not been set
```

**Solution:**
1. Go to Settings → Secrets and variables → Actions
2. Verify secrets exist with **exact names** based on your auth method:

**For Username/Password (default):**
- `HOYOLAB_USERNAME` (not `username` or `USERNAME`)
- `HOYOLAB_PASSWORD` (not `password` or `PASSWORD`)

**For Cookies (if AUTH_METHOD=cookies):**
- `HOYOLAB_LTUID` (not `ltuid` or `LTUID`)
- `HOYOLAB_LTOKEN` (not `ltoken` or `LTOKEN`)

3. If missing, add them
4. If present, check for typos in workflow file

**Test:**
Run workflow manually with dry-run mode to verify secrets work.

### 3. Authentication Failure

**Symptoms:**
```bash
Authentication failed
Invalid credentials
Cookie expired
```

**Solutions:**

**A. Wrong password (most common for login method):**
1. Verify you can login manually at <https://www.hoyolab.com>
2. Update `HOYOLAB_PASSWORD` secret in GitHub
3. Re-run workflow

**B. Expired cookies (if using cookie method):**
1. Login fresh to <https://www.hoyolab.com>
2. Get new cookies (F12 → Application → Cookies)
3. Update `HOYOLAB_LTUID` and `HOYOLAB_LTOKEN` secrets
4. Re-run workflow

**C. Wrong authentication method:**
- If using username/password: Ensure `AUTH_METHOD` is `login` (or not set - it's default)
- If using cookies: Set variable `AUTH_METHOD` = `cookies`

**D. Wrong region:**
- Check `CHECKIN_URL` matches your region
- SEA: `signin-sea-v3`
- NA: `signin-us-v3`
- EU: `signin-os-v3`

**E. Account issues:**
- Verify you can manually check-in on HoYoLAB website
- Check if account is banned/restricted

### 4. Playwright Installation Fails

**Symptoms:**
```bash
Error: Playwright installation failed
chromium browser not found
```

**Solutions:**

**A. Missing dependencies:**
```yaml
# Ensure workflow has --with-deps flag:
- name: Install Playwright browsers
  run: uv run playwright install chromium --with-deps
```

**B. Disk space:**
- Unlikely on GitHub runners (they have plenty)
- Check workflow logs for "no space left" errors

**C. Network timeout:**
- Re-run the workflow (temporary GitHub infrastructure issue)

### 5. Timeout (5 Minutes)

**Symptoms:**
```bash
The job running on runner [...] exceeded the maximum execution time of 5 minutes
```

**Causes & Solutions:**

**A. HoYoLAB is slow/down:**
- Check <https://www.hoyolab.com> is accessible
- Wait and let tomorrow's run retry
- Trigger manual run later

**B. Wrong page/navigation:**
- Review screenshots in artifacts
- Check if check-in page layout changed
- Update selectors if needed

**C. Delays too long:**
```bash
# In workflow, check env vars:
MIN_DELAY: ${{ vars.MIN_DELAY || '2.0' }}
MAX_DELAY: ${{ vars.MAX_DELAY || '8.0' }}

# If you set custom variables, reduce them:
Settings → Secrets and variables → Actions → Variables
MAX_DELAY: 8.0 → 5.0
```

### 6. Python Version Issues

**Symptoms:**
```bash
Python 3.9 found but 3.11 required
Module not found
```

**Solution:**

**A. Check workflow Python setup:**
```yaml
- name: Set up Python 3.11
  run: uv python install 3.11

- name: Verify Python version
  run: uv run python --version  # Should show 3.11.x
```

**B. If using wrong Python:**
```yaml
# Ensure ALL commands use 'uv run'
run: uv run python -m src  # ✅ Correct
run: python -m src          # ❌ Wrong
```

### 7. Dependency Installation Fails

**Symptoms:**
```bash
uv sync failed
Package not found
Dependency conflict
```

**Solutions:**

**A. Check uv.lock is committed:**
```bash
# Locally verify:
git ls-files uv.lock
# Should show: uv.lock

# If missing:
uv lock
git add uv.lock
git commit -m "chore: add uv.lock file"
git push
```

**B. Cache issue:**
```yaml
# Workflow already has caching, but if issues persist:
- name: Install uv
  uses: astral-sh/setup-uv@v2
  with:
    enable-cache: false  # Disable cache temporarily
```

### 8. Artifact Upload Fails

**Symptoms:**
```yaml
Error: Artifact upload failed
No files matched pattern
```

**Solutions:**

**A. Logs directory doesn't exist:**
- Workflow creates logs during execution
- If script fails early, no logs exist
- Solution: Check why script failed (previous steps)

**B. Path issue:**
```yaml
# Verify paths in workflow match your structure:
path: logs/screenshots/        # Must match actual directory
path: logs/execution_history.jsonl
```

### 9. Scheduled Cron Not Running

**Symptoms:**
- Manual runs work fine
- Scheduled runs don't trigger

**Possible Causes:**

**A. GitHub Actions cron delay (normal):**
- Scheduled runs can be delayed 3-15 minutes
- This is expected GitHub behavior
- Not an error

**B. Repository inactive:**
- GitHub disables scheduled workflows after 60 days of no commits
- Solution: Make a commit to re-enable

**C. Wrong cron syntax:**
```yaml
# Verify syntax at https://crontab.guru/
schedule:
  - cron: '0 22 * * *'  # Valid: Daily at 22:00 UTC

# Common mistakes:
- cron: '22 0 * * *'   # Wrong: Hour comes first, not minute
- cron: '0 22 * *'     # Wrong: Missing day-of-week field
```

### 10. Workflow Status Badge Not Showing

**Symptoms:**
- Badge shows "unknown" or "no status"

**Solutions:**

**A. Wait for first run:**
- Badge only works after first workflow execution
- Run workflow manually to initialize

**B. Check badge URL:**
```markdown
# In README.md, verify format:
[![Daily Check-in](https://github.com/USER/REPO/actions/workflows/daily-checkin.yml/badge.svg)](https://github.com/USER/REPO/actions/workflows/daily-checkin.yml)

# Replace USER and REPO with your actual values
```

**C. Branch mismatch:**
```markdown
# If on different branch, add branch parameter:
badge.svg?branch=main
```

## 🔬 Advanced Debugging

### Enable Debug Logging

1. Settings → Secrets and variables → Actions
2. Add secret:
   - Name: `ACTIONS_STEP_DEBUG`
   - Value: `true`
3. Re-run workflow - see detailed logs

### Download and Inspect Artifacts

```bash
# After workflow run:
1. Click workflow run
2. Scroll to "Artifacts" section
3. Download execution-logs-XXX.zip
4. Extract and view logs/execution_history.jsonl

# Analyze logs:
cat execution_history.jsonl | jq '.'
```

### Test Workflow Locally with act

```bash
# Install act (https://github.com/nektos/act)
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Test workflow locally:
act workflow_dispatch -s HOYOLAB_LTUID=your_ltuid -s HOYOLAB_LTOKEN=your_ltoken

# Dry run:
act workflow_dispatch -j checkin --dryrun
```

## 📞 Getting Help

If issues persist:

1. **Gather information:**
   - Workflow run number
   - Full error message
   - Recent changes to code
   - Screenshots (redact credentials!)

2. **Check GitHub Status:**
   - <https://www.githubstatus.com/>
   - Verify Actions service is operational

3. **Open Issue:**
   - Repository issues tab
   - Include: run number, error, what you tried
   - Redact all credentials

## ✅ Health Check Checklist

Run through this before troubleshooting:

- [ ] Secrets exist and names match exactly
- [ ] Actions enabled in repository settings
- [ ] Workflow file pushed to main branch
- [ ] Workflow file has valid YAML syntax
- [ ] uv.lock file is committed
- [ ] HoYoLAB cookies are fresh (< 3 months old)
- [ ] Can manually check-in on HoYoLAB website
- [ ] Local POC works (test before deploying)

## �� Quick Fixes Summary

| Issue | Quick Fix |
|-------|-----------|
| Workflow not visible | Check Actions enabled + push to main |
| Secret not found | Add/verify exact secret names in Settings |
| Auth fails | Refresh cookies and update secrets |
| Timeout | Check HoYoLAB status, reduce delays |
| Python wrong version | Ensure all commands use `uv run` |
| Cron not running | Normal 15-min delay, wait or check syntax |
| Badge not showing | Wait for first run, verify URL |

---

**Still need help?** Check [DEPLOYMENT.md](DEPLOYMENT.md) for full guide or open a GitHub issue.
