# Requirements

## Functional

**FR1:** The system shall authenticate users to HoYoLAB using secure credential management via GitHub Secrets with proper environment variable handling and no credential exposure in logs

**FR2:** The system shall navigate to the Genshin Impact daily check-in page on HoYoLAB web interface using browser automation

**FR3:** The system shall detect reward state using CSS-based detection (`actived-day` + `red-point` classes) to identify claimable rewards and avoid unnecessary actions when rewards are already claimed

**FR4:** The system shall claim available daily rewards through automated interaction with the check-in interface

**FR5:** The system shall provide clear success/failure logging with screenshot capture on failures for debugging purposes

**FR6:** The system shall run as a Python script using Selenium WebDriver that successfully completes the full HoYoLAB check-in process locally

**FR7:** The system shall integrate with GitHub Actions for scheduled daily execution at 6 AM PHT in a cloud environment

**FR8:** The system shall provide manual trigger fallback option for critical streak maintenance during automation failures

**FR9:** The system shall complete the entire check-in process within GitHub Actions' 5-minute timeout limit

## Non Functional

**NFR1:** The system must achieve minimum 70% automation success rate over 30-day periods to provide meaningful value over manual process

**NFR2:** GitHub Actions usage must stay within free tier limits (2000 minutes/month) to maintain zero-cost operation

**NFR3:** The system must handle credential storage using GitHub security best practices with no local credential persistence

**NFR4:** The system must provide comprehensive setup documentation that enables technically qualified users to replicate setup without direct support

**NFR5:** Browser automation must work reliably in GitHub Actions Ubuntu environment using Chrome/Chromium headless mode

**NFR6:** The system must implement basic error handling with try/catch logic to gracefully handle common failure scenarios

**NFR7:** The system must be designed for easy local testing and debugging before cloud deployment

**NFR8:** Code must maintain readability and educational value suitable for portfolio demonstration and learning purposes
