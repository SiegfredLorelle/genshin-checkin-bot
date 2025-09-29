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
