#!/usr/bin/env python3
"""Dependency verification script for environment validation.

This script verifies that all required dependencies are properly installed
and provides troubleshooting guidance for common issues.
"""

import importlib
import subprocess
import sys
from pathlib import Path
from typing import Tuple


def check_python_version() -> Tuple[bool, str]:
    """Check if Python version meets requirements."""
    version = sys.version_info
    if version >= (3, 9):
        return True, f"✅ Python {version.major}.{version.minor}.{version.micro}"
    else:
        return (
            False,
            f"❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.9+)",
        )


def check_package_import(
    package_name: str, import_name: str = None
) -> Tuple[bool, str]:
    """Check if a package can be imported."""
    import_name = import_name or package_name
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, "__version__", "unknown")
        return True, f"✅ {package_name} {version}"
    except ImportError as e:
        return False, f"❌ {package_name} - {str(e)}"


def check_playwright_browsers() -> Tuple[bool, str]:
    """Check if Playwright browsers are installed."""
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from playwright.sync_api import sync_playwright; "
                "p = sync_playwright().start(); "
                "browser = p.chromium.launch(); browser.close(); p.stop()",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return True, "✅ Playwright Chromium browser"
        else:
            return False, f"❌ Playwright Chromium browser - {result.stderr}"
    except Exception as e:
        return False, f"❌ Playwright Chromium browser - {str(e)}"


def check_selenium_driver() -> Tuple[bool, str]:
    """Check if Selenium WebDriver is functional."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=options)
        driver.quit()
        return True, "✅ Selenium ChromeDriver"
    except Exception as e:
        return False, f"❌ Selenium ChromeDriver - {str(e)}"


def check_project_structure() -> Tuple[bool, str]:
    """Check if project structure is correct."""
    required_dirs = [
        "src",
        "src/automation",
        "src/browser",
        "src/detection",
        "src/config",
        "src/state",
        "src/utils",
        "tests",
        "tests/unit",
        "tests/integration",
        "tests/fixtures",
        "logs",
        "scripts",
    ]

    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)

    if not missing_dirs:
        return True, "✅ Project structure complete"
    else:
        return False, f"❌ Missing directories: {', '.join(missing_dirs)}"


def main():
    """Run all dependency checks and provide summary."""
    print("🔍 Verifying Genshin Check-in Bot Dependencies")
    print("=" * 50)

    checks = [
        ("Python Version", check_python_version),
        ("Project Structure", check_project_structure),
        ("Core Dependencies", lambda: check_package_import("decouple", "decouple")),
        ("HTTP Client", lambda: check_package_import("httpx")),
        ("Logging", lambda: check_package_import("structlog")),
        ("Testing", lambda: check_package_import("pytest")),
        ("Code Quality", lambda: check_package_import("black")),
        ("Browser Automation (Primary)", lambda: check_package_import("playwright")),
        ("Browser Automation (Fallback)", lambda: check_package_import("selenium")),
        ("Playwright Browsers", check_playwright_browsers),
        ("Selenium WebDriver", check_selenium_driver),
    ]

    results = []
    for name, check_func in checks:
        try:
            success, message = check_func()
            results.append((success, name, message))
            print(f"{name:30} {message}")
        except Exception as e:
            results.append((False, name, f"❌ {name} - Error: {str(e)}"))
            print(f"{name:30} ❌ Error: {str(e)}")

    print("\n" + "=" * 50)

    # Summary
    passed = sum(1 for success, _, _ in results if success)
    total = len(results)

    print(f"📊 Summary: {passed}/{total} checks passed")

    # Show failures and recommendations
    failures = [(name, message) for success, name, message in results if not success]

    if failures:
        print("\n🔧 Troubleshooting:")
        for name, message in failures:
            print(f"\n{name}:")
            print(f"  {message}")

            # Provide specific troubleshooting advice
            if "Python" in name:
                print("  💡 Install Python 3.9+ from https://python.org")
            elif "Project Structure" in name:
                print("  💡 Run: python -m scripts.setup_project_structure")
            elif "playwright" in name.lower():
                print("  💡 Run: pip install playwright && playwright install chromium")
            elif "selenium" in name.lower():
                print("  💡 Run: pip install selenium")
            elif "Browser" in name and "Playwright" in name:
                print("  💡 Run: playwright install chromium")
            elif "Browser" in name and "Selenium" in name:
                print("  💡 ChromeDriver is auto-managed in Selenium 4.15+")
                print("  💡 Try: pip install selenium --upgrade")
            else:
                print(f"  💡 Run: pip install {name.lower().replace(' ', '-')}")

    if passed == total:
        print("\n🎉 All dependencies verified! You're ready to run the automation.")
        return 0
    else:
        print(
            f"\n⚠️  {total - passed} issues found. "
            "Please resolve them before proceeding."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
