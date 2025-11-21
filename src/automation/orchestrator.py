"""Automation Orchestrator for HoYoLAB check-in automation.

Main entry point that coordinates the complete workflow from authentication
through interface analysis with proper error handling and state logging.
"""

from pathlib import Path
from typing import Any, Dict, Optional

import structlog

from ..browser.manager import BrowserManager
from ..config.manager import ConfigurationManager
from ..detection.detector import RewardDetector
from ..state.manager import StateManager
from ..utils.exceptions import AuthenticationError, AutomationError

logger = structlog.get_logger(__name__)


class AutomationOrchestrator:
    """Main orchestrator for browser automation workflow."""

    def __init__(self, config_manager: Optional[ConfigurationManager] = None):
        """Initialize automation orchestrator.

        Args:
            config_manager: Optional configuration manager instance
        """
        self.config = config_manager or ConfigurationManager()
        browser_config = self.config.get_browser_config()
        self.browser_manager = BrowserManager(
            framework="playwright", headless=browser_config.get("headless", True)
        )
        self.reward_detector = RewardDetector()
        self.state_manager = StateManager()
        self.browser_impl = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup."""
        await self.cleanup()

    async def initialize(self) -> None:
        """Initialize all components and browser."""
        try:
            logger.info("Initializing automation orchestrator")

            # Initialize browser with fallback mechanism
            self.browser_impl = await self.browser_manager.initialize()

            # Initialize other components
            await self.reward_detector.initialize()
            await self.state_manager.initialize()

            logger.info("Automation orchestrator initialized successfully")

        except Exception as e:
            logger.error("Failed to initialize orchestrator", error=str(e))
            await self.cleanup()
            raise AutomationError(f"Orchestrator initialization failed: {e}")

    async def execute_checkin(self, dry_run: bool = False) -> Dict[str, Any]:
        """Execute complete check-in workflow from authentication through
        reward claiming.

        Args:
            dry_run: If True, perform analysis without actual claiming

        Returns:
            Complete workflow execution results including claiming status

        Raises:
            AutomationError: If workflow execution fails
        """
        workflow_result = {
            "success": False,
            "workflow_completed": False,
            "step_completed": None,
            "authentication_success": False,
            "interface_analysis": {},
            "reward_detection": {},
            "claiming_results": {},
            "validation_results": {},
            "screenshots": [],
            "errors": [],
            "dry_run": dry_run,
            "cleanup_completed": False,
        }

        try:
            logger.info("Starting complete check-in workflow", dry_run=dry_run)

            # Step 1: Navigate to HoYoLAB
            await self._navigate_to_hoyolab()
            workflow_result["step_completed"] = "navigation"

            # Step 2: Close any blocking modals FIRST (before login)
            await self._close_blocking_modals()
            workflow_result["step_completed"] = "modal_handling"

            # Step 3: Authenticate (after modals are closed)
            auth_result = await self._authenticate()
            workflow_result["authentication_success"] = auth_result
            workflow_result["step_completed"] = "authentication"

            if not auth_result:
                raise AuthenticationError("Authentication failed")

            # Step 4: Detect reward availability (look for red point indicator)
            logger.info("🔍 Looking for rewards with red point indicator...")
            detection_result = await self._detect_rewards_with_red_point()
            workflow_result["reward_detection"] = detection_result
            workflow_result["step_completed"] = "reward_detection"

            logger.info(
                "Reward detection completed",
                claimable_count=len(detection_result.get("claimable_rewards", [])),
                confidence=detection_result.get("detection_confidence", 0.0),
            )

            # Step 5: Claim rewards (skip if dry_run)
            if not dry_run and detection_result.get("claimable_rewards"):
                # Store state for validation
                pre_claim_state = detection_result.copy()

                # Directly click the reward element with red point
                claiming_result = await self._claim_reward_with_red_point(
                    detection_result
                )
                workflow_result["claiming_results"] = claiming_result
                workflow_result["step_completed"] = "reward_claiming"

                # Step 6: Validate claim success
                if claiming_result.get("success"):
                    validation_result = (
                        await self.reward_detector.validate_claim_success(
                            self.browser_impl, pre_claim_state
                        )
                    )
                    workflow_result["validation_results"] = validation_result
                    workflow_result["step_completed"] = "claim_validation"

            elif dry_run:
                logger.info("Dry run mode: skipping reward claiming")
                workflow_result["claiming_results"] = {"dry_run": True, "success": True}
                workflow_result["validation_results"] = {"dry_run": True}
                workflow_result["step_completed"] = "dry_run_complete"

            else:
                logger.info("No claimable rewards found")
                workflow_result["claiming_results"] = {
                    "no_rewards": True,
                    "success": True,
                }
                workflow_result["step_completed"] = "no_rewards_to_claim"

            # Step 7: Log execution results
            await self._log_execution_result(workflow_result)

            # Mark workflow as completed
            workflow_result["success"] = True
            workflow_result["workflow_completed"] = True
            logger.info("Complete check-in workflow finished successfully")

            return workflow_result

        except Exception as e:
            # Enhanced error handling
            error_context = {
                "step": workflow_result["step_completed"],
                "dry_run": dry_run,
                "browser_active": self.browser_impl is not None,
            }

            error_handling_result = await self._handle_workflow_error(e, error_context)
            workflow_result["error_handling"] = error_handling_result
            workflow_result["errors"].append(str(e))

            # Capture debug screenshot
            screenshot_path = await self._capture_debug_screenshot(
                "checkin_workflow_error"
            )
            if screenshot_path:
                workflow_result["screenshots"].append(screenshot_path)

            # Log failure with comprehensive context
            await self._log_execution_result(workflow_result)

            logger.error(
                "Check-in workflow failed",
                step=workflow_result["step_completed"],
                error=str(e),
                retry_recommended=error_handling_result.get("retry_recommended", False),
            )

            raise AutomationError(
                f"Check-in workflow failed at {workflow_result['step_completed']}: {e}"
            )

        finally:
            # Ensure cleanup always happens
            try:
                await self.cleanup()
                workflow_result["cleanup_completed"] = True
            except Exception as cleanup_error:
                logger.error("Cleanup failed", error=str(cleanup_error))
                workflow_result["cleanup_completed"] = False

    async def execute_workflow(self) -> Dict[str, Any]:
        """Execute complete automation workflow.

        Returns:
            Dict containing workflow execution results

        Raises:
            AutomationError: If workflow execution fails
        """
        workflow_result = {
            "success": False,
            "step_completed": None,
            "authentication_success": False,
            "interface_analysis": {},
            "screenshots": [],
            "errors": [],
        }

        try:
            logger.info("Starting automation workflow")

            # Step 1: Navigate to HoYoLAB
            await self._navigate_to_hoyolab()
            workflow_result["step_completed"] = "navigation"

            # Step 2: Authenticate
            auth_result = await self._authenticate()
            workflow_result["authentication_success"] = auth_result
            workflow_result["step_completed"] = "authentication"

            if not auth_result:
                raise AuthenticationError("Authentication failed")

            # Step 3: Analyze interface
            analysis_result = await self._analyze_interface()
            workflow_result["interface_analysis"] = analysis_result
            workflow_result["step_completed"] = "interface_analysis"

            # Step 4: Log success
            await self.state_manager.log_execution_result(
                {
                    "timestamp": self.state_manager.get_current_timestamp(),
                    "success": True,
                    "workflow_result": workflow_result,
                }
            )

            workflow_result["success"] = True
            logger.info("Automation workflow completed successfully")

            return workflow_result

        except Exception as e:
            error_msg = str(e)
            workflow_result["errors"].append(error_msg)

            # Take debug screenshot
            screenshot_path = await self._capture_debug_screenshot("workflow_error")
            if screenshot_path:
                workflow_result["screenshots"].append(screenshot_path)

            # Log failure
            await self.state_manager.log_execution_result(
                {
                    "timestamp": self.state_manager.get_current_timestamp(),
                    "success": False,
                    "error": error_msg,
                    "workflow_result": workflow_result,
                }
            )

            logger.error(
                "Automation workflow failed",
                step=workflow_result["step_completed"],
                error=error_msg,
            )

            raise AutomationError(
                f"Workflow failed at {workflow_result['step_completed']}: {error_msg}"
            )

    async def _handle_workflow_error(
        self, error: Exception, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle workflow errors with context-aware recovery strategies.

        Args:
            error: Exception that occurred
            context: Error context information

        Returns:
            Error handling result with recovery recommendations
        """
        error_handling_result = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "recovery_attempted": False,
            "retry_recommended": False,
            "context_preserved": True,
        }

        try:
            # Use RewardDetector's enhanced error handling if available
            if hasattr(self.reward_detector, "handle_claiming_errors"):
                detector_handling = await self.reward_detector.handle_claiming_errors(
                    self.browser_impl, error, context
                )
                error_handling_result.update(detector_handling)
            else:
                # Basic error handling
                if "timeout" in str(error).lower():
                    error_handling_result["retry_recommended"] = True
                elif "auth" in str(error).lower():
                    # Need re-auth
                    error_handling_result["retry_recommended"] = False
                else:
                    error_handling_result["retry_recommended"] = True

            logger.info(
                "Workflow error handled",
                error_type=error_handling_result["error_type"],
                retry_recommended=error_handling_result["retry_recommended"],
            )

        except Exception as handling_error:
            logger.error("Error handling failed", error=str(handling_error))
            error_handling_result[
                "error_message"
            ] += f" | Handling failed: {handling_error}"

        return error_handling_result

    async def _log_execution_result(self, workflow_result: Dict[str, Any]) -> None:
        """Log comprehensive execution results to state manager.

        Args:
            workflow_result: Complete workflow execution results
        """
        try:
            execution_record = {
                "timestamp": self.state_manager.get_current_timestamp(),
                "success": workflow_result.get("success", False),
                "workflow_completed": workflow_result.get("workflow_completed", False),
                "step_completed": workflow_result.get("step_completed"),
                "reward_detection": {
                    "total_rewards": len(
                        workflow_result.get("reward_detection", {}).get(
                            "claimable_rewards", []
                        )
                    ),
                    "detection_confidence": (
                        workflow_result.get("reward_detection", {}).get(
                            "detection_confidence", 0.0
                        )
                    ),
                },
                "claiming_results": {
                    "claims_processed": (
                        workflow_result.get("claiming_results", {}).get(
                            "claims_processed", 0
                        )
                    ),
                    "claiming_success": (
                        workflow_result.get("claiming_results", {}).get(
                            "success", False
                        )
                    ),
                },
                "validation_results": {
                    "claim_validated": (
                        workflow_result.get("validation_results", {}).get(
                            "claim_validated", False
                        )
                    ),
                    "validation_confidence": (
                        workflow_result.get("validation_results", {}).get(
                            "validation_confidence", 0.0
                        )
                    ),
                },
                "error_count": len(workflow_result.get("errors", [])),
                "screenshots_captured": len(workflow_result.get("screenshots", [])),
                "cleanup_completed": workflow_result.get("cleanup_completed", False),
            }

            # Add error details if present (without sensitive info)
            if workflow_result.get("errors"):
                # Limit to first 3 errors
                execution_record["error_summary"] = workflow_result["errors"][:3]

            await self.state_manager.log_execution_result(execution_record)

            logger.info(
                "Execution result logged",
                success=execution_record["success"],
                claims_processed=(
                    execution_record["claiming_results"]["claims_processed"]
                ),
            )

        except Exception as e:
            logger.error("Failed to log execution result", error=str(e))

    async def _navigate_to_hoyolab(self) -> None:
        """Navigate to HoYoLAB login page."""
        hoyolab_url = self.config.get_hoyolab_url()
        await self.browser_impl.navigate(hoyolab_url)
        logger.info("Navigated to HoYoLAB", url=hoyolab_url)

    async def _authenticate(self) -> bool:
        """Execute authentication flow.

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            logger.info("Starting HoYoLAB authentication flow")

            # Get credentials from configuration
            credentials = self.config.get_hoyolab_credentials()

            # Choose authentication method
            if credentials.auth_method == "login":
                # Use username/password login
                auth_result = await self._login_with_credentials(credentials)
            else:
                # Use cookie-based authentication
                await self._set_authentication_cookies(credentials)
                auth_result = True

            if not auth_result:
                logger.warning("Authentication failed")
                return False

            # Wait for page to load with authentication
            from ..utils.timing import page_load_delay

            await page_load_delay()

            # Validate authentication state
            auth_valid = await self._validate_authentication()

            if auth_valid:
                logger.info("Authentication successful")
                return True
            else:
                logger.warning("Authentication validation failed")
                return False

        except Exception as e:
            logger.error("Authentication failed", error=str(e))
            return False

    async def _detect_rewards_with_red_point(self) -> Dict[str, Any]:
        """Detect claimable rewards by looking for the red point indicator.

        The red point indicator shows which reward is available to claim today.

        Returns:
            Detection result with claimable rewards
        """
        detection_result = {
            "claimable_rewards": [],
            "claimed_rewards": [],
            "unavailable_rewards": [],
            "total_rewards_found": 0,
            "detection_confidence": 0.0,
            "detection_method": "red_point_indicator",
        }

        try:
            import asyncio

            await asyncio.sleep(2)  # Wait for page to stabilize

            # Selector for red point indicator based on provided HTML
            # <span class="components-home-assets-__sign-content-test_---
            # red-point---2jUBf9"></span>
            red_point_selectors = [
                (
                    ".components-home-assets-__sign-content-test_---"
                    "red-point---2jUBf9"
                ),
                "span[class*='red-point']",
                ".red-point",
            ]

            logger.info("🔍 Looking for red point indicator on rewards...")

            red_point_element = None
            used_selector = None

            # Try each selector
            for selector in red_point_selectors:
                try:
                    logger.info(f"   Trying red point selector: {selector}")
                    found = await self.browser_impl.find_element(selector, timeout=3000)
                    if found:
                        red_point_element = selector
                        used_selector = selector
                        logger.info(f"✓ Found red point with selector: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Red point selector failed: {selector}", error=str(e))
                    continue

            if not red_point_element:
                logger.warning(
                    "❌ No red point indicator found - no claimable rewards today"
                )
                detection_result["detection_confidence"] = 0.3
                return detection_result

            # The red point is inside the sign-item wrapper, we need to click the parent
            # Structure: div.sign-wrapper > div.actived-day > span.red-point
            # We want to click the sign-wrapper div

            # Try to get the clickable parent element
            clickable_selectors = [
                # Parent of red point
                (
                    ".components-home-assets-__sign-content-test_---sign-item"
                    f"---3gtMqV:has({used_selector})"
                ),
                (
                    ".components-home-assets-__sign-content-test_---sign-wrapper"
                    f"---22GpLY:has({used_selector})"
                ),
                f"div[class*='sign-item']:has({used_selector})",
                f"div[class*='sign-wrapper']:has({used_selector})",
                # Generic parent selectors
                f"{used_selector} >> xpath=../.. ",  # Go up 2 levels
            ]

            claimable_element = None
            for selector in clickable_selectors:
                try:
                    logger.info(f"   Trying clickable parent: {selector[:60]}...")
                    found = await self.browser_impl.find_element(selector, timeout=2000)
                    if found:
                        claimable_element = selector
                        logger.info(
                            "✓ Found clickable reward element: " f"{selector[:60]}..."
                        )
                        break
                except Exception as e:
                    logger.debug(
                        f"Parent selector failed: {selector[:60]}", error=str(e)
                    )
                    continue

            if claimable_element:
                detection_result["claimable_rewards"].append(
                    {
                        "selector": claimable_element,
                        "state": "claimable",
                        "red_point_detected": True,
                    }
                )
                detection_result["total_rewards_found"] = 1
                detection_result["detection_confidence"] = 0.95
                logger.info(
                    "✓ Successfully identified claimable reward with "
                    "red point indicator"
                )
            else:
                logger.warning(
                    "⚠ Found red point but couldn't identify clickable element"
                )
                detection_result["detection_confidence"] = 0.4

            return detection_result

        except Exception as e:
            logger.error("Red point detection failed", error=str(e))
            detection_result["detection_confidence"] = 0.0
            return detection_result

    async def _claim_reward_with_red_point(
        self, detection_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Claim reward by clicking the element with red point indicator.

        Args:
            detection_result: Result from red point detection

        Returns:
            Claiming result with success status
        """
        claiming_result = {
            "success": False,
            "claims_processed": 0,
            "successful_claims": [],
            "failed_claims": [],
            "error_details": [],
        }

        try:
            import asyncio

            claimable_rewards = detection_result.get("claimable_rewards", [])
            if not claimable_rewards:
                logger.warning("No claimable rewards to click")
                return claiming_result

            reward = claimable_rewards[0]
            selector = reward.get("selector")

            logger.info(
                "🎯 Attempting to click reward with selector: " f"{selector[:80]}..."
            )

            # Wait a moment before clicking
            await asyncio.sleep(1)

            # Click using Playwright's page.click()
            try:
                await self.browser_impl.page.click(selector, timeout=10000)
                logger.info("✓ Successfully clicked reward element!")

                # Wait for claim to process
                await asyncio.sleep(3)

                claiming_result["success"] = True
                claiming_result["claims_processed"] = 1
                claiming_result["successful_claims"].append(
                    {
                        "selector": selector,
                        "timestamp": self.state_manager.get_current_timestamp(),
                    }
                )

            except Exception as click_error:
                logger.error("❌ Failed to click reward element", error=str(click_error))
                claiming_result["failed_claims"].append(
                    {
                        "selector": selector,
                        "error": str(click_error),
                    }
                )
                claiming_result["error_details"].append(str(click_error))

            return claiming_result

        except Exception as e:
            logger.error("Reward claiming failed", error=str(e))
            claiming_result["error_details"].append(str(e))
            return claiming_result

    async def _close_blocking_modals(self) -> None:
        """Close any blocking modals that may appear after page load.

        This handles modals like:
        - App download promotion modal
        - Cookie consent dialogs
        - Age verification popups
        """
        try:
            logger.info("🔍 Checking for blocking modals...")

            # Wait a bit for modals to appear
            from ..utils.timing import page_load_delay

            await page_load_delay()

            # List of modal close button selectors to try
            modal_close_selectors = [
                # App download modal close button (specific from your HTML)
                ".components-home-assets-__sign-guide_---guide-close---2VvmzE",
                "span.components-home-assets-__sign-guide_---guide-close---2VvmzE",
                # Generic modal close buttons
                ".modal-close",
                ".close-button",
                "[aria-label='Close']",
                "button[class*='close']",
                "span[class*='close']",
            ]

            closed_count = 0
            for selector in modal_close_selectors:
                try:
                    # Check if element exists
                    element_found = await self.browser_impl.find_element(
                        selector, timeout=2000
                    )

                    if element_found:
                        # Click the close button
                        await self.browser_impl.page.click(selector)
                        closed_count += 1
                        logger.info(
                            "✓ Closed modal using selector: " f"{selector[:60]}..."
                        )

                        # Wait a moment after closing for animations
                        import asyncio

                        await asyncio.sleep(1.5)

                except Exception:
                    # Element not found or click failed, continue to next selector
                    logger.debug(f"Modal close selector not found: {selector[:60]}...")
                    continue

            if closed_count > 0:
                logger.info(f"✓ Successfully closed {closed_count} modal(s)")
            else:
                logger.info(
                    "ℹ No blocking modals found " "(this is normal if already closed)"
                )

        except Exception as e:
            logger.warning("⚠ Error while closing modals", error=str(e))
            # Don't fail the workflow if modal closing fails

    async def _login_with_credentials(self, credentials) -> bool:
        """Login using username and password.

        Args:
            credentials: HoYoLAB credentials object with username and password

        Returns:
            True if login successful, False otherwise
        """
        try:
            logger.info("Starting username/password login flow")

            # Wait for page to stabilize after modal closing
            import asyncio

            await asyncio.sleep(2)

            # Step 1: Click the profile/avatar icon first
            logger.info("Looking for profile/avatar icon to click...")
            avatar_selectors = [
                ".mhy-hoyolab-account-block__avatar-icon",
                ".mhy-hoyolab-account-block__avatar",
                ".mhy-hoyolab-account-block",
            ]

            avatar_clicked = False
            for avatar_selector in avatar_selectors:
                try:
                    logger.info(f"Trying avatar selector: {avatar_selector}")
                    element = await self.browser_impl.page.wait_for_selector(
                        avatar_selector, state="visible", timeout=5000
                    )
                    if element:
                        await self.browser_impl.page.click(
                            avatar_selector, timeout=5000
                        )
                        logger.info(f"✓ Clicked profile icon: {avatar_selector}")
                        avatar_clicked = True
                        break
                except Exception:
                    logger.debug("Avatar selector failed", selector=avatar_selector)
                    continue

            if not avatar_clicked:
                logger.error("✗ Could not find or click profile icon")
                return False

            # Step 2: Wait for the dropdown/modal to appear
            # (give it time to render)
            logger.info(
                "⏳ Waiting 15 seconds for login modal/menu to appear "
                "(modal shows late)..."
            )
            await asyncio.sleep(15)  # Increased wait - user confirmed modal shows late

            # Step 3: Look for login iframe (HoYoLAB loads login form in iframe)
            logger.info("🔍 Looking for login iframe...")
            iframe = None
            try:
                # Wait a bit for iframe to load
                await asyncio.sleep(3)

                # Look for the HoYoLAB account iframe
                frames = self.browser_impl.page.frames
                logger.info(f"ℹ Found {len(frames)} frame(s) on page")

                for frame in frames:
                    frame_url = frame.url
                    logger.info(f"   Frame URL: {frame_url[:120]}")
                    if (
                        "account.hoyolab.com" in frame_url
                        or "login-platform" in frame_url
                    ):
                        logger.info("✓ Found login iframe!")
                        iframe = frame
                        break

                if not iframe:
                    logger.warning("⚠ No login iframe found yet, will try direct page")
            except Exception as e:
                logger.warning("Error checking for iframe", error=str(e))

            # Step 4: Wait for the actual login FORM to fully render in iframe
            if iframe:
                logger.info(
                    "⏳ Waiting 5 more seconds for login form in iframe "
                    "to fully render..."
                )
                await asyncio.sleep(5)

            # Use iframe if found, otherwise use main page
            page_or_frame = iframe if iframe else self.browser_impl.page

            if iframe:
                logger.info("✓ Will interact with form inside iframe")
            else:
                logger.info("ℹ Will interact with form on main page")

            # DEBUG: Log page content to see what's actually there
            try:
                page_content = await self.browser_impl.page.content()
                # Check if login modal elements exist in the HTML
                if "hyv-dialog-container" in page_content:
                    logger.info("✓ Login dialog container found in HTML")
                if "input" in page_content and "username" in page_content.lower():
                    logger.info("✓ Username input field likely present")
                if "el-dialog" in page_content:
                    logger.info("✓ Element UI dialog found")

                # Log a sample of the HTML around "username" if it exists
                if "username" in page_content.lower():
                    import re

                    match = re.search(
                        r".{100}username.{100}", page_content, re.IGNORECASE
                    )
                    if match:
                        logger.info(
                            f"HTML sample around 'username': ...{match.group()}..."
                        )
            except Exception as e:
                logger.debug(f"Could not dump page content: {e}")

            # Fill in username/email - try multiple selectors IN THE IFRAME
            username_selectors = [
                'input[name="username"]',  # Most likely based on your HTML
                '.el-input__inner[name="username"]',  # With class from your HTML
                'input[autocomplete="username"]',  # With autocomplete attribute
                'input[type="text"][name="username"]',  # Full specification
                'input[placeholder*="Username"]',
                'input[placeholder*="Email"]',
            ]

            username_filled = False
            for username_selector in username_selectors:
                try:
                    logger.info(f"   Trying username selector: {username_selector}")
                    # Wait for the element to be visible IN THE FRAME
                    await page_or_frame.wait_for_selector(
                        username_selector, state="visible", timeout=5000
                    )
                    await page_or_frame.fill(
                        username_selector, credentials.username, timeout=5000
                    )
                    logger.info(f"✓ Filled username: {credentials.username}")
                    username_filled = True
                    await asyncio.sleep(0.8)
                    break
                except Exception as e:
                    logger.debug(f"   Failed: {str(e)[:60]}")
                    continue

            if not username_filled:
                logger.error("✗ Failed to fill username with all selectors")
                # Save debug screenshot
                try:
                    await self.browser_impl.page.screenshot(
                        path="logs/screenshots/username_field_not_found.png"
                    )
                    logger.info(
                        "📸 Debug screenshot: "
                        "logs/screenshots/username_field_not_found.png"
                    )
                except Exception:
                    pass
                return False

            # Fill in password - try multiple selectors IN THE IFRAME
            password_selectors = [
                'input[name="password"]',
                'input[type="password"]',
                '.el-input__inner[name="password"]',
                '.el-input__inner[type="password"]',
                'input[autocomplete="current-password"]',
            ]

            password_filled = False
            for password_selector in password_selectors:
                try:
                    logger.info(f"   Trying password selector: {password_selector}")
                    await page_or_frame.wait_for_selector(
                        password_selector, state="visible", timeout=5000
                    )
                    await page_or_frame.fill(
                        password_selector, credentials.password, timeout=5000
                    )
                    logger.info("✓ Filled password field")
                    password_filled = True
                    await asyncio.sleep(0.8)
                    break
                except Exception as e:
                    logger.debug(f"   Failed: {str(e)[:60]}")
                    continue

            if not password_filled:
                logger.error("✗ Failed to fill password with all selectors")
                return False

            # Click login button IN THE IFRAME
            login_button_selectors = [
                'button[type="submit"]',
                "button.hyv-button",
                'button:has-text("Log In")',
                'button:has-text("Sign In")',
                ".hyv-button-login",
            ]

            login_clicked = False
            for login_button_selector in login_button_selectors:
                try:
                    logger.info(f"   Trying login button: {login_button_selector}")
                    await page_or_frame.click(login_button_selector, timeout=5000)
                    logger.info("✓ Clicked login button!")
                    login_clicked = True
                    break
                except Exception as e:
                    logger.debug(f"   Failed: {str(e)[:60]}")
                    continue

            if not login_clicked:
                logger.error("✗ Failed to click login button")
                return False

            # Wait for login to process and page to load
            logger.info("⏳ Waiting for login to process...")
            await asyncio.sleep(5)

            logger.info("✓ Login flow completed successfully")
            return True

        except Exception as e:
            logger.error("✗ Login with credentials failed", error=str(e))
            return False

    async def _set_authentication_cookies(self, credentials) -> None:
        """Set HoYoLAB authentication cookies.

        Args:
            credentials: HoYoLAB credentials object
        """
        try:
            # Set required HoYoLAB cookies for authentication
            cookies = [
                {
                    "name": "ltuid",
                    "value": credentials.ltuid,
                    "domain": ".hoyolab.com",
                    "path": "/",
                    "secure": True,
                    "httpOnly": False,
                },
                {
                    "name": "ltoken",
                    "value": credentials.ltoken,
                    "domain": ".hoyolab.com",
                    "path": "/",
                    "secure": True,
                    "httpOnly": False,
                },
            ]

            if credentials.account_id:
                cookies.append(
                    {
                        "name": "account_id",
                        "value": credentials.account_id,
                        "domain": ".hoyolab.com",
                        "path": "/",
                        "secure": True,
                        "httpOnly": False,
                    }
                )

            # Set cookies using browser implementation
            for cookie in cookies:
                await self._set_browser_cookie(cookie)

            logger.info("Authentication cookies set", cookie_count=len(cookies))

        except Exception as e:
            logger.error("Failed to set authentication cookies", error=str(e))
            raise AuthenticationError(f"Cookie setting failed: {e}")

    async def _set_browser_cookie(self, cookie: dict) -> None:
        """Set cookie using browser implementation.

        Args:
            cookie: Cookie dictionary with name, value, domain, etc.
        """
        try:
            logger.debug("Setting cookie", name=cookie["name"], domain=cookie["domain"])
            await self.browser_impl.set_cookie(cookie)

        except Exception as e:
            logger.error(
                "Failed to set cookie", cookie_name=cookie.get("name"), error=str(e)
            )
            raise

    async def _validate_authentication(self) -> bool:
        """Validate that authentication was successful.

        Returns:
            True if authentication is valid, False otherwise
        """
        try:
            # Check for authentication indicators on the page
            # This is a placeholder implementation for MVP

            logger.info("Validating authentication state")

            # In a real implementation, we would:
            # 1. Check for user profile elements
            # 2. Verify no login prompts are present
            # 3. Test API endpoints that require authentication

            # For MVP, we'll assume success if cookies were set
            return True

        except Exception as e:
            logger.error("Authentication validation failed", error=str(e))
            return False

    async def _analyze_interface(self) -> Dict[str, Any]:
        """Analyze interface for reward detection.

        Returns:
            Interface analysis results
        """
        try:
            logger.info("Starting interface analysis")

            # Perform comprehensive interface analysis
            analysis_result = await self.reward_detector.analyze_interface(
                self.browser_impl
            )

            # Generate detailed interface report
            report = await self._generate_interface_report(analysis_result)
            analysis_result["detailed_report"] = report

            # Take screenshot for analysis documentation
            screenshot_path = await self._capture_debug_screenshot("interface_analysis")
            if screenshot_path:
                analysis_result["analysis_screenshot"] = screenshot_path

            logger.info(
                "Interface analysis completed",
                selectors_found=len(analysis_result.get("selectors", [])),
                confidence=analysis_result.get("detection_confidence", 0.0),
            )
            return analysis_result

        except Exception as e:
            logger.error("Interface analysis failed", error=str(e))
            return {"error": str(e), "selectors": [], "detection_confidence": 0.0}

    async def _generate_interface_report(
        self, analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate detailed interface analysis report.

        Args:
            analysis_result: Raw analysis results from RewardDetector

        Returns:
            Detailed interface report
        """
        report = {
            "analysis_summary": {
                "total_strategies_tested": 0,
                "successful_strategies": 0,
                "primary_detection_method": analysis_result.get("primary_strategy"),
                "fallback_methods": analysis_result.get("fallback_strategies", []),
                "overall_confidence": analysis_result.get("detection_confidence", 0.0),
            },
            "selector_inventory": {
                "high_confidence": [],
                "medium_confidence": [],
                "low_confidence": [],
            },
            "timing_requirements": {
                "page_load_time": "2-3 seconds",
                "element_wait_time": "5-10 seconds",
                "anti_bot_delays": "1-2 seconds between actions",
            },
            "potential_bot_detection": {
                "captcha_presence": False,
                "rate_limiting_indicators": False,
                "suspicious_elements": [],
            },
            "reliability_assessment": {
                "stability_score": 0.0,
                "maintenance_requirements": "medium",
                "recommended_monitoring": [],
            },
        }

        try:
            # Categorize selectors by confidence
            selectors = analysis_result.get("selectors", [])
            for selector in selectors:
                confidence = selector.get("confidence", 0.5)
                selector_info = {
                    "selector": selector.get("selector", ""),
                    "target_type": selector.get("target_type", "unknown"),
                    "strategy": selector.get("strategy", "unknown"),
                }

                if confidence >= 0.8:
                    report["selector_inventory"]["high_confidence"].append(
                        selector_info
                    )
                elif confidence >= 0.5:
                    report["selector_inventory"]["medium_confidence"].append(
                        selector_info
                    )
                else:
                    report["selector_inventory"]["low_confidence"].append(selector_info)

            # Calculate overall reliability
            total_selectors = len(selectors)
            high_conf_count = len(report["selector_inventory"]["high_confidence"])

            if total_selectors > 0:
                stability_score = (high_conf_count / total_selectors) * 100
                report["reliability_assessment"]["stability_score"] = round(
                    stability_score, 2
                )

            # Add monitoring recommendations
            if stability_score < 50:
                report["reliability_assessment"]["recommended_monitoring"].extend(
                    [
                        "Weekly selector validation",
                        "Interface change detection",
                        "Fallback strategy testing",
                    ]
                )

            logger.info(
                "Interface report generated",
                high_confidence_selectors=high_conf_count,
                total_selectors=total_selectors,
                stability_score=stability_score,
            )

        except Exception as e:
            logger.error("Failed to generate interface report", error=str(e))
            report["error"] = str(e)

        return report

    async def _capture_debug_screenshot(self, prefix: str = "debug") -> Optional[str]:
        """Capture screenshot for debugging.

        Args:
            prefix: Filename prefix for screenshot

        Returns:
            Screenshot file path or None if failed
        """
        try:
            timestamp = self.state_manager.get_current_timestamp().replace(":", "-")
            screenshot_path = f"logs/screenshots/{prefix}_{timestamp}.png"

            # Ensure directory exists
            Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)

            await self.browser_impl.screenshot(screenshot_path)
            logger.info("Debug screenshot captured", path=screenshot_path)
            return screenshot_path

        except Exception as e:
            logger.error("Failed to capture screenshot", error=str(e))
            return None

    async def cleanup(self) -> None:
        """Clean up resources."""
        try:
            if self.browser_impl:
                await self.browser_impl.close()
                logger.info("Browser resources cleaned up")
        except Exception as e:
            logger.error("Error during cleanup", error=str(e))
