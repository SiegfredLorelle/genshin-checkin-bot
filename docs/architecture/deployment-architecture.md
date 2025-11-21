# Deployment Architecture

The deployment strategy leverages GitHub's native infrastructure for zero-cost operation while maintaining reliability and educational value.

## Deployment Strategy

**Backend Deployment:**
- **Platform:** GitHub Actions Ubuntu runners
- **Execution Method:** Scheduled workflow via cron syntax
- **Deployment Method:** Direct code execution from repository
- **Environment:** Serverless execution with 5-minute timeout limit

## CI/CD Pipeline

```yaml
name: Daily Check-in Automation
on:
  schedule:
    - cron: '0 22 * * *'  # 6 AM PHT (UTC+8)
  workflow_dispatch:      # Manual trigger
    inputs:
      reason:
        description: 'Reason for manual execution'
        required: false
        default: 'Manual intervention'

jobs:
  checkin:
    runs-on: ubuntu-latest
    timeout-minutes: 5

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Install Playwright browsers
      run: playwright install chromium

    - name: Run check-in automation
      env:
        HOYOLAB_LTUID: ${{ secrets.HOYOLAB_LTUID }}
        HOYOLAB_LTOKEN: ${{ secrets.HOYOLAB_LTOKEN }}
      run: python -m src.automation.orchestrator

    - name: Upload failure screenshots
      if: failure()
      uses: actions/upload-artifact@v3
      with:
        name: failure-screenshots
        path: logs/screenshots/
        retention-days: 30

    - name: Commit execution logs
      if: always()
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add logs/execution_history.jsonl
        git diff --staged --quiet || git commit -m "Add execution log: $(date -u +%Y-%m-%d_%H:%M:%S)"
        git push
```

## Environments

| Environment | Frontend URL | Backend URL | Purpose |
|-------------|--------------|-------------|---------|
| Development | N/A | Local execution | Local development and testing |
| Production | N/A | GitHub Actions | Live automation execution |
