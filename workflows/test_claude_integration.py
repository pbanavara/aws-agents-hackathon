#!/usr/bin/env python3
"""
Test script for Claude integration with AWS Bedrock
"""

import asyncio
import os
import json
from all_workflows import (
    ask_claude_for_plan, 
    UsageData, 
    ContractData, 
    AutomationLevel
)

async def test_claude_integration():
    """Test the Claude integration"""
    
    print("🧪 Testing Claude Integration")
    print("=" * 50)
    
    # Check if any Claude API keys are available
    bearer_token = os.getenv('AWS_BEARER_TOKEN_BEDROCK')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not bearer_token and not anthropic_key:
        print("❌ No Claude API keys found in environment")
        print("   Set one of:")
        print("   export AWS_BEARER_TOKEN_BEDROCK='your-bedrock-token'")
        print("   export ANTHROPIC_API_KEY='your-anthropic-key'")
        return
    
    if bearer_token:
        print(f"✅ Bedrock token found: {bearer_token[:10]}...")
    if anthropic_key:
        print(f"✅ Anthropic API key found: {anthropic_key[:10]}...")
    print("   Note: Will try Bedrock first, then Anthropic API, then fallback")
    
    # Create test data
    usage_data = UsageData(
        account_id="test-account-001",
        current_usage=2500.0,
        usage_trend="increasing",
        usage_period="monthly",
        threshold_exceeded=1000.0,
        metric_type="trade_volume",
        additional_context={"trading_frequency": "high", "market_volatility": "medium"}
    )
    
    contract_data = ContractData(
        account_id="test-account-001",
        current_plan="Basic",
        contract_end_date="2024-12-31",
        renewal_date="2024-11-30",
        current_spend=500.0,
        contract_terms={"monthly_limit": 1000, "support_level": "email"},
        contact_info={"first_name": "John", "last_name": "Doe", "email": "john.doe@example.com"}
    )
    
    print(f"📊 Test Usage Data:")
    print(f"   Account: {usage_data.account_id}")
    print(f"   Current Usage: {usage_data.current_usage}")
    print(f"   Threshold: {usage_data.threshold_exceeded}")
    print(f"   Metric Type: {usage_data.metric_type}")
    
    print(f"📋 Test Contract Data:")
    print(f"   Current Plan: {contract_data.current_plan}")
    print(f"   Current Spend: ${contract_data.current_spend}")
    print(f"   Contract End: {contract_data.contract_end_date}")
    
    try:
        print("\n🤖 Calling Claude for upsell plan...")
        
        # Call Claude
        upsell_plan = await ask_claude_for_plan(
            usage_data=usage_data,
            contract_data=contract_data,
            automation_level=AutomationLevel.HYBRID
        )
        
        print("\n✅ Claude Response:")
        print(f"   Recommended Plan: {upsell_plan.recommended_plan}")
        print(f"   Estimated Value: ${upsell_plan.estimated_value:,.2f}")
        print(f"   Justification: {upsell_plan.justification}")
        print(f"   Features: {', '.join(upsell_plan.features)}")
        print(f"   ROI Analysis: {upsell_plan.roi_analysis}")
        print(f"   Risk Assessment: {upsell_plan.risk_assessment}")
        
    except Exception as e:
        print(f"\n❌ Error calling Claude: {e}")
        print("   This might be due to:")
        print("   - Invalid bearer token")
        print("   - Network connectivity issues")
        print("   - AWS Bedrock service issues")
        print("   - Missing AWS credentials for region access")

if __name__ == "__main__":
    asyncio.run(test_claude_integration()) 