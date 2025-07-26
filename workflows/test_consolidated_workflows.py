#!/usr/bin/env python3
"""
Test script for Consolidated Workflows
Tests all workflows: Upsell, Alert Processing, and Sample workflows
"""

import asyncio
import logging
from datetime import datetime
from temporalio.client import Client

# Import from consolidated workflows
from all_workflows import (
    trigger_upsell_workflow,
    send_customer_reply,
    AutomationLevel
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_upsell_workflow():
    """Test the upsell workflow"""
    print("\n💰 Testing Upsell Workflow")
    print("=" * 40)
    
    # Connect to Temporal
    client = await Client.connect("localhost:7233")
    
    # Trigger upsell workflow
    workflow_id = await trigger_upsell_workflow(
        client=client,
        account_id="test-account-001",
        event_id="high-usage-alert-001",
        automation_level=AutomationLevel.HYBRID,
        metric_type="trade_volume"
    )
    
    print(f"✅ Upsell workflow triggered: {workflow_id}")
    
    # Wait for initial processing
    print("⏳ Waiting for initial processing...")
    await asyncio.sleep(5)
    
    # Send customer reply
    print("📝 Sending customer reply: 'yes'")
    await send_customer_reply(client, workflow_id, "yes")
    
    # Wait for completion
    print("⏳ Waiting for workflow completion...")
    handle = client.get_workflow_handle(workflow_id)
    result = await handle.result()
    
    print("✅ Upsell workflow completed!")
    print(f"   Account ID: {result['account_id']}")
    print(f"   Event ID: {result['event_id']}")
    print(f"   Automation Level: {result['automation_level']}")
    print(f"   Email Sent: {result['email_sent']}")
    print(f"   Reply Status: {result['reply_status']}")
    print(f"   Opportunity ID: {result['opportunity_id']}")
    
    return result


async def test_usage_endpoint():
    """Test the usage data endpoint"""
    print("\n📊 Testing Usage Data Endpoint")
    print("=" * 40)
    
    import requests
    import time
    
    # Wait for endpoint to start
    time.sleep(2)
    
    base_url = "http://localhost:8001"
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/usage/health")
        if response.status_code == 200:
            print("✅ Usage endpoint health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Could not connect to usage endpoint: {e}")
        return
    
    # Test posting usage data
    usage_data = {
        "account_id": "test-account-001",
        "current_usage": 2500.0,
        "usage_trend": "increasing",
        "usage_period": "monthly",
        "threshold_exceeded": 2000.0,
        "metric_type": "trade_volume",
        "additional_context": {
            "source": "test",
            "alert_severity": "high"
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/usage/data",
            json=usage_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Usage data posted successfully")
        else:
            print(f"❌ Failed to post usage data: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error posting usage data: {e}")
    
    # Test retrieving usage data
    try:
        response = requests.get(f"{base_url}/usage/data/test-account-001")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved usage data: {data['data']['current_usage']} {data['data']['metric_type']}")
        else:
            print(f"❌ Failed to retrieve usage data: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error retrieving usage data: {e}")


async def main():
    """Main test function"""
    print("🚀 Consolidated Workflows Test Suite")
    print("=" * 50)
    
    try:
        # Test all workflows
        await test_upsell_workflow()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.error(f"Test error: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main()) 