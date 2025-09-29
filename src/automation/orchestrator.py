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
        self.browser_manager = BrowserManager(framework="playwright")
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

            # Step 2: Authenticate
            auth_result = await self._authenticate()
            workflow_result["authentication_success"] = auth_result
            workflow_result["step_completed"] = "authentication"

            if not auth_result:
                raise AuthenticationError("Authentication failed")

            # Step 3: Detect reward availability
            detection_result = await self.reward_detector.detect_reward_availability(
                self.browser_impl
            )
            workflow_result["reward_detection"] = detection_result
            workflow_result["step_completed"] = "reward_detection"

            logger.info(
                "Reward detection completed",
                claimable_count=len(detection_result.get("claimable_rewards", [])),
                confidence=detection_result.get("detection_confidence", 0.0),
            )

            # Step 4: Claim rewards (skip if dry_run)
            if not dry_run and detection_result.get("claimable_rewards"):
                # Store state for validation
                pre_claim_state = detection_result.copy()

                claiming_result = await self.reward_detector.claim_available_rewards(
                    self.browser_impl, detection_result
                )
                workflow_result["claiming_results"] = claiming_result
                workflow_result["step_completed"] = "reward_claiming"

                # Step 5: Validate claim success
                if claiming_result.get("success"):
                    validation_result = await self.reward_detector.validate_claim_success(
                        self.browser_impl, pre_claim_state
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
                workflow_result["claiming_results"] = {"no_rewards": True, "success": True}
                workflow_result["step_completed"] = "no_rewards_to_claim"

            # Step 6: Log execution results
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
            screenshot_path = await self._capture_debug_screenshot("checkin_workflow_error")
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
            error_handling_result["error_message"] += f" | Handling failed: {handling_error}"

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
                        workflow_result.get("reward_detection", {}).get("claimable_rewards", [])
                    ),
                    "detection_confidence": (
                        workflow_result.get("reward_detection", {}).get("detection_confidence", 0.0)
                    ),
                },
                "claiming_results": {
                    "claims_processed": (
                        workflow_result.get("claiming_results", {}).get("claims_processed", 0)
                    ),
                    "claiming_success": (
                        workflow_result.get("claiming_results", {}).get("success", False)
                    ),
                },
                "validation_results": {
                    "claim_validated": (
                        workflow_result.get("validation_results", {}).get("claim_validated", False)
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
                claims_processed=(execution_record["claiming_results"]["claims_processed"]),
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

            # Set authentication cookies
            await self._set_authentication_cookies(credentials)

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
            logger.error("Failed to set cookie", cookie_name=cookie.get("name"), error=str(e))
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
            analysis_result = await self.reward_detector.analyze_interface(self.browser_impl)

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

    async def _generate_interface_report(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
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
                    report["selector_inventory"]["high_confidence"].append(selector_info)
                elif confidence >= 0.5:
                    report["selector_inventory"]["medium_confidence"].append(selector_info)
                else:
                    report["selector_inventory"]["low_confidence"].append(selector_info)

            # Calculate overall reliability
            total_selectors = len(selectors)
            high_conf_count = len(report["selector_inventory"]["high_confidence"])

            if total_selectors > 0:
                stability_score = (high_conf_count / total_selectors) * 100
                report["reliability_assessment"]["stability_score"] = round(stability_score, 2)

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
