# Data Models

Based on the PRD requirements, the system needs minimal but well-defined data models to support automation workflow, state tracking, and success rate measurement.

## Simplified ExecutionLog

**Purpose:** Single record per automation run for success rate tracking and failure analysis

**Key Attributes:**
- timestamp: str - ISO 8601 execution time for sorting and period calculations
- success: bool - Simple binary success/failure for NFR1 calculation  
- duration_seconds: float - Performance monitoring for GitHub Actions timeout management
- error_message: Optional[str] - Failure reason for debugging (only when success=false)
- screenshot_artifact: Optional[str] - GitHub Actions artifact name for failure screenshots
- selector_used: str - Which CSS detection strategy succeeded ("primary", "fallback_1", "fallback_2")

**Simplified Python Data Structure:**
```python
@dataclass
class ExecutionLog:
    timestamp: str  # ISO 8601
    success: bool
    duration_seconds: float
    error_message: Optional[str] = None
    screenshot_artifact: Optional[str] = None
    selector_used: str = "primary"
    
    def to_dict(self) -> dict:
        return asdict(self)
```

**Storage Implementation:**
```python
# Simple JSON Lines format - one log entry per line
# logs/execution_history.jsonl
{"timestamp": "2025-09-29T06:00:00Z", "success": true, "duration_seconds": 23.4, "selector_used": "primary"}
{"timestamp": "2025-09-30T06:00:00Z", "success": false, "duration_seconds": 45.2, "error_message": "Element not found", "screenshot_artifact": "failure-2025-09-30.png", "selector_used": "fallback_1"}
```

**Success Rate Calculation (On-Demand):**
```python
def calculate_success_rate(days: int = 30) -> float:
    """Calculate success rate for last N days from log file"""
    cutoff = datetime.now() - timedelta(days=days)
    
    with open('logs/execution_history.jsonl', 'r') as f:
        logs = [json.loads(line) for line in f 
                if datetime.fromisoformat(json.loads(line)['timestamp']) >= cutoff]
    
    if not logs:
        return 0.0
        
    successful = sum(1 for log in logs if log['success'])
    return (successful / len(logs)) * 100
```
