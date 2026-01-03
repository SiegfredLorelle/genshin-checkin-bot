# GitHub Actions Deployment Guide

This guide walks you through deploying the Genshin Check-in Bot to GitHub Actions for automated daily execution.

## 📋 Prerequisites

- GitHub account (free tier is sufficient)
- Your HoYoLAB username and password
- Repository pushed to GitHub
- Completed local testing (POC working)

## 🎯 Deployment Overview

**Platform:** GitHub Actions (Free Tier)
**Cost:** $0 (within 2000 minutes/month limit)
**Execution:** Daily at 6 AM PHT (10 PM UTC)
**Timeout:** 5 minutes per run
**Storage:** 90 days for logs, 30 days for screenshots

## 🔐 Step 1: Configure GitHub Secrets

GitHub Secrets securely store your HoYoLAB credentials.

### 1.1 Add Your Credentials

1. Go to your repository on GitHub
2. Click `Settings` (top menu)
3. In left sidebar: `Secrets and variables` → `Actions`
4. Click `New repository secret` button

**Add these two secrets:**

| Secret Name | Value | Example |
|------------|-------|---------|
| `HOYOLAB_USERNAME` | Your HoYoLAB email/username | `your@email.com` |
| `HOYOLAB_PASSWORD` | Your HoYoLAB password | `YourPassword123` |

⚠️ **IMPORTANT:** Never commit these values to your repository!

### 1.2 Optional: Configure Variables

For non-sensitive configuration (optional):

1. Same location: `Secrets and variables` → `Actions`
2. Click `Variables` tab
3. Add variables if you want to customize:

| Variable Name | Default Value | Purpose |
|--------------|---------------|---------|
| `CHECKIN_URL` | Auto-set | Custom check-in URL |
| `MIN_DELAY` | `2.0` | Minimum delay between actions (seconds) |
| `MAX_DELAY` | `8.0` | Maximum delay between actions (seconds) |

## ⚙️ Step 2: Enable GitHub Actions

1. Go to repository `Settings`
2. In left sidebar: `Actions` → `General`
3. Under **Actions permissions:**
   - Select: ✅ `Allow all actions and reusable workflows`
4. Under **Workflow permissions:**
   - Select: ✅ `Read and write permissions`
   - Check: ✅ `Allow GitHub Actions to create and approve pull requests` (optional)
5. Click `Save`

## 🚀 Step 3: Test Your Deployment

### 3.1 Manual Test Run

1. Go to repository `Actions` tab
2. Click `Daily HoYoLAB Check-in` workflow (left sidebar)
3. Click `Run workflow` button (right side)
4. Configure test run:
   - **Dry run:** ✅ Check this box (recommended for first test)
   - **Reason:** "Initial deployment test"
5. Click green `Run workflow` button
6. Wait ~2-3 minutes for completion

### 3.2 Verify Success

**Check workflow status:**
- ✅ Green checkmark = Success
- ❌ Red X = Failure (check logs)
- 🟡 Yellow dot = Running

**Review logs:**
1. Click the workflow run
2. Click `checkin` job
3. Expand each step to see output
4. Check "Report execution status" for summary

**Download artifacts (if available):**
- `execution-logs-XXX` - Full execution history
- `failure-screenshots-XXX` - Only present on failure

### 3.3 Production Test (Optional)

After successful dry-run:
1. Run workflow again
2. Leave "Dry run" **unchecked**
3. This will actually claim rewards
4. Verify in-game that reward was claimed

## 📅 Step 4: Enable Scheduled Runs

The workflow is **already configured** to run automatically!

**Schedule:** Every day at 10 PM UTC (6 AM PHT)
**Cron expression:** `0 22 * * *`

No additional configuration needed - it will start daily automatically.

### Modify Schedule (Optional)

To change the time, edit `.github/workflows/daily-checkin.yml`:

```yaml
schedule:
  - cron: '0 22 * * *'  # Change this line
```

**Common timezone conversions:**
- 6 AM PHT (UTC+8) = `0 22 * * *` (10 PM UTC)
- 8 AM EST (UTC-5) = `0 13 * * *` (1 PM UTC)
- 12 PM UTC = `0 12 * * *`

Use https://crontab.guru/ to validate cron expressions.

## 📊 Step 5: Monitoring & Maintenance

### Daily Monitoring

**Quick check:**
1. Go to `Actions` tab
2. See recent workflow runs
3. Green = Success, Red = Investigate

**Email notifications:**
- GitHub automatically emails you on workflow failures
- Configure in: Settings → Notifications → Actions

### View Execution History

**Web UI:**
1. Actions tab → Select run → View logs

**Download logs:**
1. Select workflow run
2. Scroll to bottom "Artifacts" section
3. Download `execution-logs-XXX`

### Troubleshooting Common Issues

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| "Secret not found" error | Secrets not configured | Verify Step 1 completed |
| Workflow doesn't run | Actions disabled | Enable in repository settings |
| Authentication failure | Invalid/expired cookies | Refresh cookies from browser |
| Timeout (5 minutes) | HoYoLAB slow/network issue | Check logs, may auto-retry tomorrow |
| Screenshot artifacts | Check-in page changed | Review failure screenshots |

### Credential Rotation

**When to update:**
- Every 3-6 months (cookies can expire)
- After changing HoYoLAB password
- After authentication errors

**How to update:**
1. Get fresh cookies from browser (Step 1.1)
2. Go to Settings → Secrets → Actions
3. Click secret name → `Update secret`
4. Paste new value → `Update secret`

## 🎮 Usage Examples

### Manual Trigger (Dry Run)
Use when testing or debugging:
```text
Actions → Daily HoYoLAB Check-in → Run workflow
✅ Dry run: checked
Reason: "Testing new changes"
```

### Manual Trigger (Production)
Use if automated run failed:
```text
Actions → Daily HoYoLAB Check-in → Run workflow
⬜ Dry run: unchecked
Reason: "Missed daily check-in"
```

### Disable Automation
To temporarily stop automated runs:
1. Edit `.github/workflows/daily-checkin.yml`
2. Comment out the schedule section:
```yaml
# schedule:
#   - cron: '0 22 * * *'
```
3. Commit and push

## 📈 Resource Usage Tracking

**Free Tier Limits:**
- 2000 minutes/month for private repos
- Unlimited for public repos

**Your usage:**
- ~3-5 minutes per run
- 30 runs/month = ~150 minutes
- Well within limits! ✅

**Check usage:**
1. Settings → Billing → Plans and usage
2. View "Actions" section

## 🔒 Security Best Practices

✅ **Do:**
- Use GitHub Secrets for credentials
- Rotate cookies periodically
- Keep repository private if concerned
- Review workflow logs regularly

❌ **Don't:**
- Commit `.env` file
- Share screenshots with credentials visible
- Give repository access to untrusted users
- Hardcode credentials in workflow files

## 🆘 Getting Help

**Workflow failing?**
1. Check workflow logs (expand each step)
2. Download failure screenshots
3. Review execution logs artifact
4. Check HoYoLAB website for changes

**Need support?**
- Open GitHub issue with:
  - Workflow run number
  - Error message (redact credentials!)
  - Failure screenshot (if relevant)

## ✅ Deployment Checklist

Before marking deployment complete:

- [ ] Secrets configured (`HOYOLAB_LTUID`, `HOYOLAB_LTOKEN`)
- [ ] GitHub Actions enabled
- [ ] Workflow permissions set to "Read and write"
- [ ] Dry-run test completed successfully
- [ ] Production test completed successfully
- [ ] Verified reward claimed in-game
- [ ] Scheduled runs enabled (automatic)
- [ ] Monitoring configured (email notifications)
- [ ] Documentation reviewed

**Congratulations!** 🎉 Your automation is now deployed and will run daily at 6 AM PHT!
