# Upsell Workflow System

## Overview

The Upsell Workflow System is designed to automatically trigger sales opportunities when usage-based alerts are detected. It integrates with the usage metrics webhook to create a complete automated sales pipeline.

## Architecture

```
Usage Alert → Webhook → Upsell Workflow → Sales Activities → Opportunity Logging
```

## Components

### 1. UpsellWorkflow (`upsell_workflow.py`)

The main workflow that orchestrates the entire upsell process.

**Workflow Steps:**
1. `fetchUsage()` - Get current usage data
2. `fetchContract()` - Retrieve contract information
3. `askClaudeForPlan()` - AI-powered upsell recommendation
4. `sendEmailDraft()` - Send personalized email
5. `postSlackSummary()` - Notify sales team
6. `waitForReply()` - Wait for customer response
7. `createZoomMeeting()` - Schedule follow-up meeting
8. `logOpportunity()` - Record opportunity in database

### 2. Automation Levels

- **FULL_AUTOMATION**: Complete automation, no human intervention
- **HUMAN_INTERVENTION**: Requires human approval for all steps
- **HYBRID**: Automated initial steps, human review for final decisions

### 3. Data Structures

#### UsageData
```python
@dataclass
class UsageData:
    account_id: str
    current_usage: float
    usage_trend: str  # "increasing", "decreasing", "stable"
    usage_period: str  # "daily", "weekly", "monthly"
    threshold_exceeded: float
    metric_type: str
    additional_context: Dict[str, Any]
```

#### ContractData
```python
@dataclass
class ContractData:
    account_id: str
    current_plan: str
    contract_end_date: str
    renewal_date: str
    current_spend: float
    contract_terms: Dict[str, Any]
    contact_info: Dict[str, str]
```

#### UpsellPlan
```python
@dataclass
class UpsellPlan:
    recommended_plan: str
    estimated_value: float
    justification: str
    features: List[str]
    roi_analysis: str
    risk_assessment: str
```

## Usage

### 1. Starting the Workers

```bash
# Start the upsell worker
python upsell_worker.py &

# Start the alert worker (if not already running)
python alert_worker.py &

# Start the webhook server
python webhook.py &
```

### 2. Triggering Workflows

#### From Agent/Code
```python
from upsell_workflow import trigger_upsell_workflow, AutomationLevel

# Trigger upsell workflow
workflow_id = await trigger_upsell_workflow(
    client=temporal_client,
    account_id="12345",
    event_id="high-volume-alert-001",
    automation_level=AutomationLevel.HYBRID,
    metric_type="trade_volume"
)
```

#### From Webhook (Automatic)
The webhook automatically triggers upsell workflows when:
- Alert severity is 'high' or 'critical'
- Current value exceeds 1000
- Metric type is 'trade_volume', 'trade_value', or 'balance_change'

### 3. Sending Customer Replies

```python
from upsell_workflow import send_customer_reply

# Send customer reply signal
await send_customer_reply(
    client=temporal_client,
    workflow_id="upsell-12345-001-20240115-140000",
    reply="yes"  # or "no", "maybe"
)
```

### 4. Testing

```bash
# Test the complete workflow
python test_upsell_workflow.py

# Test the webhook with usage metrics
python test_usage_metrics_webhook.py
```

## Configuration

### Automation Level Selection

The system automatically selects automation level based on alert severity:

- **Critical Alerts**: `FULL_AUTOMATION`
- **High Alerts**: `HYBRID`
- **Low Alerts**: `HUMAN_INTERVENTION`

### Thresholds

- **High Value Threshold**: 1000 (configurable)
- **Reply Timeout**: 24 hours
- **Activity Timeouts**: 5-10 minutes per activity

## Integration Points

### 1. Usage Data Sources
- **TODO**: Connect to your metrics/analytics system
- **Current**: Mock data in `fetch_usage()` activity

### 2. Contract Management
- **TODO**: Connect to your CRM or contract management system
- **Current**: Mock data in `fetch_contract()` activity

### 3. AI Recommendation
- **TODO**: Implement Claude API integration
- **Current**: Mock recommendations in `ask_claude_for_plan()` activity

### 4. Email System
- **TODO**: Implement AWS SES or similar
- **Current**: Mock email sending in `send_email_draft()` activity

### 5. Slack Integration
- **TODO**: Implement Slack Web API
- **Current**: Mock Slack posting in `post_slack_summary()` activity

### 6. Zoom Integration
- **TODO**: Implement Zoom API
- **Current**: Mock meeting creation in `create_zoom_meeting()` activity

### 7. Database Logging
- **TODO**: Implement MongoDB/ClickHouse integration
- **Current**: Mock logging in `log_opportunity()` activity

## Workflow States

1. **Started**: Workflow initiated
2. **Fetching Data**: Getting usage and contract information
3. **AI Analysis**: Generating upsell recommendations
4. **Email Sent**: Customer notification sent
5. **Slack Posted**: Sales team notified
6. **Waiting Reply**: Awaiting customer response
7. **Meeting Scheduled**: Zoom meeting created (if reply is yes)
8. **Completed**: Opportunity logged and workflow finished

## Error Handling

- **Activity Failures**: Automatic retries with exponential backoff
- **Timeout Handling**: 24-hour timeout for customer replies
- **Graceful Degradation**: Upsell failures don't affect main alert processing

## Monitoring

### Temporal UI
- View workflow executions at `http://localhost:8080`
- Monitor activity completion and failures
- Track workflow history and signals

### Logs
- All activities log their progress
- Workflow state transitions are logged
- Error conditions are captured with context

## Example Workflow Execution

```
1. Usage Alert Received
   ├── Account: 12345
   ├── Metric: trade_volume
   ├── Value: 150 (threshold: 100)
   └── Severity: high

2. Upsell Workflow Triggered
   ├── Automation Level: HYBRID
   ├── Workflow ID: upsell-12345-001-20240115-140000
   └── Task Queue: upsell-task-queue

3. Activities Executed
   ├── fetch_usage() → UsageData
   ├── fetch_contract() → ContractData
   ├── ask_claude_for_plan() → UpsellPlan
   ├── send_email_draft() → Email sent
   ├── post_slack_summary() → Slack notification
   ├── wait_for_reply() → Customer reply received
   ├── create_zoom_meeting() → Meeting scheduled
   └── log_opportunity() → Opportunity recorded

4. Workflow Completed
   ├── Status: completed
   ├── Email Sent: true
   ├── Reply Status: yes
   ├── Zoom Meeting: scheduled
   └── Opportunity ID: opp_12345_001
```

## Future Enhancements

1. **Multi-channel Communication**: SMS, in-app notifications
2. **A/B Testing**: Test different email templates and approaches
3. **Predictive Analytics**: Predict likelihood of upsell success
4. **Integration Hub**: Connect to more CRM and communication systems
5. **Custom Workflows**: Allow custom workflow definitions per customer segment

## Troubleshooting

### Common Issues

1. **Worker Not Starting**
   - Check Temporal server is running
   - Verify task queue name matches

2. **Workflow Not Triggering**
   - Check alert criteria in `trigger_upsell_if_needed()`
   - Verify automation level configuration

3. **Activities Failing**
   - Check activity timeouts
   - Verify external service connections

4. **Customer Reply Not Received**
   - Check signal handling
   - Verify workflow ID format

### Debug Commands

```bash
# Check Temporal server status
docker ps | grep temporal

# View workflow logs
python test_upsell_workflow.py

# Test individual activities
python -c "from upsell_workflow import fetch_usage; import asyncio; print(asyncio.run(fetch_usage('12345', 'trade_volume')))"
``` 