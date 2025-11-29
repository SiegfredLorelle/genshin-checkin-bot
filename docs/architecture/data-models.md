# Data Models

Based on the PRD requirements, the system needs minimal but well-defined data models to support automation workflow, state tracking, and success rate measurement.

## Simplified ExecutionLog

**Purpose:** Single record per automation run for success rate tracking and failure analysis

**Key Attributes:**
- timestamp: str - ISO 8601 execution time for sorting and period calculations
- success: bool - Simple binary success/failure for NFR1 calculation
- duration_seconds: float - Performance monitoring for GitHub Actions timeout management
- error_message: Optional[str] - Failure reason for debugging (only when success=false)
- screenshot_path: Optional[str] - Path to failure screenshot for debugging
- selector_used: str - Which CSS detection strategy succeeded ("primary", "fallback_1", "fallback_2")

**Simplified Python Data Structure:**
```python
@dataclass
class ExecutionLog:
    timestamp: str  # ISO 8601
    success: bool
    duration_seconds: float
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    selector_used: str = "primary"

    def to_dict(self) -> dict:
        return asdict(self)
```

**Storage Implementation:**
```python
# Simple JSON Lines format - one log entry per line
# logs/execution_history.jsonl
{"timestamp": "2025-11-30T06:00:00Z", "success": true, "duration_seconds": 23.4, "dry_run": false}
{"timestamp": "2025-11-30T07:00:00Z", "success": false, "duration_seconds": 45.2, "error_message": "Element not found", "screenshot_path": "logs/screenshots/failure-2025-11-30.png", "dry_run": false}
```

**Note:** The actual implementation may include additional fields based on execution context. Core fields (timestamp, success, duration_seconds) are always present.

**Success Rate Calculation (Implemented in StateManager):**
```python
async def calculate_success_rate(days: int = 7) -> Dict[str, Any]:
    """Calculate success rate for last N days from log file

    Returns:
        {
            "total_executions": int,
            "successful_executions": int,
            "success_rate": float,  # Percentage
            "period_days": int,
            "analysis_timestamp": str  # ISO 8601
        }
    """
    # Implementation in src/state/manager.py
    # Uses async file I/O with locking
    # Filters logs by UTC timestamp comparison
    # Returns detailed statistics dictionary
```

**See:** `src/state/manager.py` for complete implementation with async support and thread safety.
