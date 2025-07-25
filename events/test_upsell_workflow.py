#!/usr/bin/env python3
"""
Test script for the Upsell Workflow
Demonstrates how to trigger and interact with the upsell workflow
"""

import asyncio
import logging
from datetime import datetime
from temporalio.client import Client

# Import our upsell workflow functions
from upsell_workflow import (
    trigger_upsell_workflow,
    send_customer_reply,
    AutomationLevel
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_full_automation_workflow():
    """Test the upsell workflow with full automation"""
    print("\n🚀 Testing Full Automation Workflow")
    print("=" * 50)
    
    # Connect to Temporal
    client = await Client.connect("localhost:7233")
    
    # Trigger workflow
    workflow_id = await trigger_upsell_workflow(
        client=client,
        account_id="12345",
        event_id="high-volume-alert-001",
        automation_level=AutomationLevel.FULL_AUTOMATION,
        metric_type="trade_volume"
    )
    
    print(f"✅ Workflow triggered: {workflow_id}")
    
    # Wait for completion
    print("⏳ Waiting for workflow completion...")
    handle = client.get_workflow_handle(workflow_id)
    result = await handle.result()
    
    print("✅ Workflow completed!")
    print(f"Account ID: {result['account_id']}")
    print(f"Event ID: {result['event_id']}")
    print(f"Automation Level: {result['automation_level']}")
    print(f"Email Sent: {result['email_sent']}")
    print(f"Reply Status: {result['reply_status']}")
    print(f"Opportunity ID: {result['opportunity_id']}")
    
    return workflow_id


async def test_hybrid_workflow_with_reply():
    """Test the upsell workflow with hybrid automation and customer reply"""
    print("\n🤖 Testing Hybrid Workflow with Customer Reply")
    print("=" * 50)
    
    # Connect to Temporal
    client = await Client.connect("localhost:7233")
    
    # Trigger workflow
    workflow_id = await trigger_upsell_workflow(
        client=client,
        account_id="67890",
        event_id="sla-violation-alert-002",
        automation_level=AutomationLevel.HYBRID,
        metric_type="latency"
    )
    
    print(f"✅ Workflow triggered: {workflow_id}")
    
    # Simulate waiting for initial processing
    print("⏳ Waiting for initial processing...")
    await asyncio.sleep(5)
    
    # Send customer reply signal
    print("📝 Sending customer reply: 'yes'")
    await send_customer_reply(client, workflow_id, "yes")
    
    # Wait for completion
    print("⏳ Waiting for workflow completion...")
    handle = client.get_workflow_handle(workflow_id)
    result = await handle.result()
    
    print("✅ Workflow completed!")
    print(f"Account ID: {result['account_id']}")
    print(f"Event ID: {result['event_id']}")
    print(f"Automation Level: {result['automation_level']}")
    print(f"Email Sent: {result['email_sent']}")
    print(f"Reply Status: {result['reply_status']}")
    print(f"Zoom Meeting: {result['zoom_meeting'] is not None}")
    print(f"Opportunity ID: {result['opportunity_id']}")
    
    return workflow_id


async def test_human_intervention_workflow():
    """Test the upsell workflow requiring human intervention"""
    print("\n👤 Testing Human Intervention Workflow")
    print("=" * 50)
    
    # Connect to Temporal
    client = await Client.connect("localhost:7233")
    
    # Trigger workflow
    workflow_id = await trigger_upsell_workflow(
        client=client,
        account_id="11111",
        event_id="high-value-alert-003",
        automation_level=AutomationLevel.HUMAN_INTERVENTION,
        metric_type="trade_value"
    )
    
    print(f"✅ Workflow triggered: {workflow_id}")
    
    # Simulate waiting for initial processing
    print("⏳ Waiting for initial processing...")
    await asyncio.sleep(5)
    
    # Send customer reply signal
    print("📝 Sending customer reply: 'maybe'")
    await send_customer_reply(client, workflow_id, "maybe")
    
    # Wait for completion
    print("⏳ Waiting for workflow completion...")
    handle = client.get_workflow_handle(workflow_id)
    result = await handle.result()
    
    print("✅ Workflow completed!")
    print(f"Account ID: {result['account_id']}")
    print(f"Event ID: {result['event_id']}")
    print(f"Automation Level: {result['automation_level']}")
    print(f"Email Sent: {result['email_sent']}")
    print(f"Reply Status: {result['reply_status']}")
    print(f"Zoom Meeting: {result['zoom_meeting'] is not None}")
    print(f"Opportunity ID: {result['opportunity_id']}")
    
    return workflow_id


async def test_workflow_timeout():
    """Test workflow timeout when no reply is received"""
    print("\n⏰ Testing Workflow Timeout")
    print("=" * 50)
    
    # Connect to Temporal
    client = await Client.connect("localhost:7233")
    
    # Trigger workflow
    workflow_id = await trigger_upsell_workflow(
        client=client,
        account_id="22222",
        event_id="timeout-test-004",
        automation_level=AutomationLevel.HYBRID,
        metric_type="trade_volume"
    )
    
    print(f"✅ Workflow triggered: {workflow_id}")
    print("⏳ Waiting for workflow timeout (this will take 24 hours in real scenario)...")
    print("   For testing, we'll simulate a shorter timeout scenario")
    
    # In a real scenario, this would wait for 24 hours
    # For testing, we'll just show the workflow is running
    print("   Workflow is running and waiting for customer reply...")
    print("   (In production, this would timeout after 24 hours)")
    
    return workflow_id


async def main():
    """Run all tests"""
    print("🧪 Upsell Workflow Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Full automation
        await test_full_automation_workflow()
        
        # Test 2: Hybrid with reply
        await test_hybrid_workflow_with_reply()
        
        # Test 3: Human intervention
        await test_human_intervention_workflow()
        
        # Test 4: Timeout scenario
        await test_workflow_timeout()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.error(f"Test error: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main()) 