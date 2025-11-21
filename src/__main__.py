"""Main entry point for HoYoLAB check-in automation."""

import asyncio
import sys

import structlog

from .automation.orchestrator import AutomationOrchestrator
from .utils.logging_config import configure_logging


async def main(dry_run: bool = False) -> int:
    """Main execution function.

    Args:
        dry_run: If True, analyze interface without claiming rewards

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Configure logging
    configure_logging()
    logger = structlog.get_logger(__name__)

    logger.info("Starting HoYoLAB check-in automation", dry_run=dry_run)

    try:
        # Initialize and run orchestrator
        async with AutomationOrchestrator() as orchestrator:
            await orchestrator.initialize()
            result = await orchestrator.execute_checkin(dry_run=dry_run)

            # Print summary
            print("\n" + "=" * 60)
            print("AUTOMATION SUMMARY")
            print("=" * 60)
            print(f"Success: {result['success']}")
            print(f"Workflow Completed: {result['workflow_completed']}")
            print(f"Step Completed: {result['step_completed']}")
            print(f"Dry Run: {dry_run}")

            if result.get("reward_detection"):
                rd = result["reward_detection"]
                print(f"\nRewards Found: {len(rd.get('claimable_rewards', []))}")
                print(f"Detection Confidence: {rd.get('detection_confidence', 0):.1%}")

            if result.get("claiming_results"):
                cr = result["claiming_results"]
                print(f"\nClaims Processed: {cr.get('claims_processed', 0)}")
                print(f"Claiming Success: {cr.get('success', False)}")

            if result.get("screenshots"):
                print(f"\nScreenshots: {len(result['screenshots'])}")
                for screenshot in result["screenshots"]:
                    print(f"  - {screenshot}")

            if result.get("errors"):
                print(f"\nErrors: {len(result['errors'])}")
                for error in result["errors"][:3]:
                    print(f"  - {error}")

            print("=" * 60 + "\n")

            return 0 if result["success"] else 1

    except KeyboardInterrupt:
        logger.warning("Automation interrupted by user")
        return 130

    except Exception as e:
        logger.error("Automation failed", error=str(e), exc_info=True)
        print(f"\n❌ Automation failed: {e}\n")
        return 1


if __name__ == "__main__":
    # Parse command line args
    dry_run = "--dry-run" in sys.argv or "-d" in sys.argv

    # Run main
    exit_code = asyncio.run(main(dry_run=dry_run))
    sys.exit(exit_code)
