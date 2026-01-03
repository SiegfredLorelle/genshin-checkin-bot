# 🚀 GitHub Actions Deployment - Quick Start

**Time to deploy:** ~5 minutes | **Cost:** $0 (free tier)

## Prerequisites Checklist

- [ ] GitHub account
- [ ] Repository pushed to GitHub
- [ ] Local POC tested and working
- [ ] HoYoLAB username and password ready

## 5-Minute Setup

### Step 1: Prepare Your Credentials (1 min)

You have your HoYoLAB login credentials ready (email + password).

### Step 2: Add to GitHub (1 min)

1. GitHub repo → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add two secrets:
   - Name: `HOYOLAB_USERNAME` | Value: [your email]
   - Name: `HOYOLAB_PASSWORD` | Value: [your password]

### Step 3: Enable Actions (30 sec)

1. Settings → Actions → General
2. Select "Allow all actions and reusable workflows"
3. Select "Read and write permissions"
4. Save

### Step 4: Test (1 min)

1. Actions tab → "Daily HoYoLAB Check-in"
2. Run workflow → ✅ Check "Dry run" → Run
3. Wait 2-3 minutes
4. ✅ Green = Success | ❌ Red = Check logs

### Step 5: Production Test (30 sec)

1. Run workflow again → ⬜ Uncheck "Dry run" → Run
2. Verify reward claimed in-game

## ✅ Done!

Automation runs automatically every day at 6 AM PHT (10 PM UTC).

## Quick Commands

**Manual trigger (if you miss a day):**
```text
Actions → Daily HoYoLAB Check-in → Run workflow
```

**Check logs:**
```text
Actions → Select run → Download "execution-logs-XXX"
```

**Update cookies (every 3-6 months):**
```text
Settings → Secrets → Click secret → Update secret
```

## Troubleshooting One-Liners

| Problem | Solution |
|---------|----------|
| "Secret not found" | Add secrets in Step 2 |
| Workflow doesn't run | Enable Actions in Step 3 |
| Auth fails | Update cookies (they expired) |
| Times out | HoYoLAB slow, will retry tomorrow |

## Resource Usage

- **Your usage:** ~5 min/day = 150 min/month
- **Free tier:** 2000 min/month
- **Status:** ✅ Well within limits

## Need More Help?

📖 **Full guide with screenshots:** [DEPLOYMENT.md](DEPLOYMENT.md)

🆘 **Still stuck?** Open a GitHub issue with:
- Workflow run number
- Error message (hide credentials!)
- What step failed
