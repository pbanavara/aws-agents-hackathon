# Claude Integration with AWS Bedrock

This document describes the Claude AI integration for the upsell workflow using AWS Bedrock.

## Overview

The `ask_claude_for_plan` activity uses Claude 3 Sonnet via AWS Bedrock to analyze usage and contract data to generate intelligent upsell recommendations.

## Setup

### 1. Environment Variables

Set one or both of the following environment variables:

**Option 1: AWS Bedrock (Primary)**
```bash
export AWS_BEARER_TOKEN_BEDROCK='your-bearer-token-here'
```

**Option 2: Anthropic API (Fallback)**
```bash
export ANTHROPIC_API_KEY='your-anthropic-api-key-here'
```

**Note**: The system will try Bedrock first, then Anthropic API, then fall back to rule-based logic.

### 2. Dependencies

The integration requires both `boto3` and `anthropic` which are included in `requirements.txt`:

```bash
pip install boto3 anthropic
```

### 3. AWS Credentials (for Bedrock)

For AWS Bedrock access, you may also need:
- AWS Access Key ID and Secret Access Key
- Proper IAM permissions for Bedrock
- Or configure AWS credentials via `aws configure`

## How It Works

### 1. Data Transformation

The activity transforms `UsageData` and `ContractData` into a webhook format that Claude expects:

```python
# Input data structures
usage_data: UsageData
contract_data: ContractData

# Transformed to webhook format
{
  "alerts": [{
    "alert_id": "alert-account-001-20241225-143022",
    "metric_type": "TRADE_VOLUME",
    "threshold_condition": {"operator": ">", "value": 1000, "unit": "trades"},
    "metric_data": {
      "metric_name": "trade_volume",
      "current_value": 2500,
      "threshold_value": 1000,
      "account_id": "account-001",
      "timestamp": "2024-12-25T14:30:22",
      "usage_trend": "increasing",
      "usage_period": "monthly"
    },
    "severity": "HIGH",
    "status": "ACTIVE",
    "title": "High Trade Volume Alert",
    "description": "Account account-001 has exceeded trade_volume threshold",
    "tags": ["revenue-opportunity", "upsell-candidate"],
    "context": {"trading_frequency": "high", "market_volatility": "medium"}
  }],
  "contract_context": {
    "current_plan": "Basic",
    "contract_end_date": "2024-12-31",
    "renewal_date": "2024-11-30",
    "current_spend": 500.0,
    "contract_terms": {"monthly_limit": 1000, "support_level": "email"},
    "contact_info": {"first_name": "John", "last_name": "Doe", "email": "john.doe@example.com"}
  }
}
```

### 2. Claude API Integration

The system tries multiple Claude APIs in order:

1. **AWS Bedrock (Primary)**: Uses `AWS_BEARER_TOKEN_BEDROCK`
2. **Anthropic API (Fallback)**: Uses `ANTHROPIC_API_KEY`
3. **Rule-based Logic (Final Fallback)**: Simple heuristics

### 3. Claude Prompt

The system sends a structured prompt to Claude with:

- **Role**: Revenue-focused Customer Success agent
- **Task**: Analyze alerts for monetizable opportunities
- **Rules**: Output strict JSON, follow schema exactly
- **Output Schema**: Detailed response format with recommendations

### 3. Response Processing

Claude's response is parsed and converted to an `UpsellPlan`:

```python
UpsellPlan(
    recommended_plan="Professional",
    estimated_value=5000.0,
    justification="High usage detected, upgrade to Professional plan for better performance",
    features=["Advanced Analytics", "Priority Support", "Custom Integrations"],
    roi_analysis="Expected $5,000 annual revenue increase",
    risk_assessment="Low risk, high potential value"
)
```

## Error Handling

### Fallback Logic

If Claude integration fails, the system falls back to simple rule-based logic:

```python
def _fallback_upsell_plan(usage_data: UsageData, contract_data: ContractData) -> UpsellPlan:
    # Simple logic based on usage patterns
    if current_plan == "Basic" and current_usage > 1000:
        return "Professional" plan recommendation
    # ... more rules
```

### Common Issues

1. **Missing Bearer Token**: Falls back to rule-based logic
2. **Network Issues**: Logs error and uses fallback
3. **Invalid Response**: Parses JSON carefully, falls back if needed
4. **AWS Service Issues**: Handles Bedrock API errors gracefully

## Testing

### Test Script

Run the test script to verify the integration:

```bash
python test_claude_integration.py
```

### Expected Output

```
🧪 Testing Claude Integration
==================================================
✅ Bearer token found: your-token...
📊 Test Usage Data:
   Account: test-account-001
   Current Usage: 2500.0
   Threshold: 1000.0
   Metric Type: trade_volume
📋 Test Contract Data:
   Current Plan: Basic
   Current Spend: $500.0
   Contract End: 2024-12-31

🤖 Calling Claude for upsell plan...

✅ Claude Response:
   Recommended Plan: Professional
   Estimated Value: $5,000.00
   Justification: High usage detected, upgrade to Professional plan for better performance
   Features: Advanced Analytics, Priority Support, Custom Integrations
   ROI Analysis: Expected $5,000 annual revenue increase
   Risk Assessment: Low risk, high potential value
```

## Configuration

### Model Settings

- **Model**: `anthropic.claude-3-sonnet-20240229-v1:0`
- **Max Tokens**: 4000
- **Region**: `us-east-1` (configurable)
- **Retries**: 3 attempts

### Plan Features Mapping

The system maps plan names to features:

```python
plan_features = {
    "Basic": ["Basic Analytics", "Email Support"],
    "Professional": ["Advanced Analytics", "Priority Support", "Custom Integrations"],
    "Enterprise": ["Advanced Analytics", "Priority Support", "Custom Integrations", "Dedicated Account Manager", "SLA Guarantee"],
    "Pro-250k": ["High Volume Trading", "Advanced Analytics", "Priority Support"],
    "Pro-500k": ["High Volume Trading", "Advanced Analytics", "Priority Support", "Custom Integrations"],
    "Enterprise-1M": ["Enterprise Features", "Dedicated Support", "Custom Solutions"]
}
```

## Integration Points

### Workflow Integration

The Claude integration is used in the `UpsellWorkflow`:

```python
# In UpsellWorkflow.run()
upsell_plan = await self.ask_claude_for_plan(
    usage_data=usage_data,
    contract_data=contract_data,
    automation_level=automation_level
)
```

### Email Integration

The system now sends emails via Amazon SES using Claude's recommendations:

```python
# Create email draft using Claude's response
email_draft = self._create_email_draft(
    usage_data=usage_data,
    contract_data=contract_data,
    upsell_plan=upsell_plan
)

# Send email via SES
email_sent = await self.send_email_draft(
    email_draft=email_draft,
    automation_level=automation_level
)
```

**Email Features:**
- Uses Claude's generated email subject and body
- Sends to email address from contract data
- Integrates with Amazon SES
- Includes fallback email content if Claude doesn't provide email data

### Logging

The integration provides detailed logging:

- 🤖 Claude generated upsell plan: Professional
- ❌ Claude integration failed: [error details]
- 🔄 Falling back to default logic

## Security

- Bearer token is read from environment variables
- No hardcoded credentials
- Token is used only in request headers
- All AWS API calls use secure HTTPS

## Monitoring

Monitor the integration through:

1. **Temporal UI**: View workflow execution and activity logs
2. **Application Logs**: Check for Claude integration messages
3. **AWS CloudWatch**: Monitor Bedrock API usage and errors
4. **Custom Metrics**: Track success/failure rates of Claude calls 