# Core Workflows

The following sequence diagrams illustrate key system workflows that clarify architecture decisions and complex interactions.

## Daily Check-in Automation Workflow

```mermaid
sequenceDiagram
    participant GHA as GitHub Actions
    participant AO as AutomationOrchestrator  
    participant BM as BrowserManager
    participant RD as RewardDetector
    participant CM as ConfigurationManager
    participant SM as StateManager
    participant HL as HoYoLAB

    GHA->>AO: execute_checkin() [Scheduled 6AM PHT]
    AO->>CM: validate_configuration()
    CM-->>AO: Configuration valid
    
    AO->>BM: initialize_browser()
    BM->>CM: get_browser_config()
    BM-->>AO: Browser ready
    
    AO->>BM: authenticate_session()
    BM->>CM: get_credentials()
    BM->>HL: Login with cookies
    HL-->>BM: Authentication success
    
    AO->>BM: navigate_to_checkin()
    BM->>HL: Navigate to check-in page
    HL-->>BM: Page loaded
    
    AO->>RD: detect_reward_availability()
    RD->>CM: get_selector_config()
    RD->>BM: DOM inspection (primary selector)
    
    alt Primary selector succeeds
        BM-->>RD: Element found
        RD->>RD: claim_available_rewards()
        RD->>HL: Click reward button
        HL-->>RD: Reward claimed
        RD-->>AO: Success result
    else Primary selector fails  
        BM-->>RD: Element not found
        RD->>BM: DOM inspection (fallback selector)
        BM-->>RD: Fallback element found
        RD->>HL: Click fallback button
        HL-->>RD: Reward claimed
        RD-->>AO: Success with fallback
    else All selectors fail
        RD->>BM: capture_failure_screenshot()
        RD-->>AO: Failure result
    end
    
    AO->>SM: log_execution(result)
    SM->>SM: Write to execution_history.jsonl
    
    AO->>BM: cleanup_browser()
    AO-->>GHA: Execution complete
```

## Manual Trigger Fallback Workflow

```mermaid
sequenceDiagram
    participant User as User
    participant GHA as GitHub Actions
    participant AO as AutomationOrchestrator
    participant SM as StateManager
    
    User->>GHA: Manual trigger via repository dispatch
    GHA->>AO: execute_checkin(manual=true)
    
    Note over AO: Same automation workflow as scheduled
    
    AO->>SM: log_execution(result, manual=true)
    SM->>SM: Mark as manual intervention
    
    AO-->>GHA: Manual execution complete
    GHA-->>User: Workflow status notification
```
