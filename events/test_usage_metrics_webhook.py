#!/usr/bin/env python3
"""
Test script for the usage metrics webhook
Demonstrates how to send usage-based alerts to the webhook
"""

import requests
import json
from datetime import datetime
from usage_metrics_schema import (
    UsageMetricsAlert, WebhookRequest, WebhookResponse,
    MetricType, AlertSeverity, AlertStatus, ThresholdOperator,
    ThresholdCondition, MetricData,
    create_high_volume_alert, create_sla_violation_alert, create_high_value_transaction_alert
)

# Webhook configuration
WEBHOOK_BASE_URL = "http://localhost:8000"
ASYNC_ENDPOINT = f"{WEBHOOK_BASE_URL}/webhook/alerts"
SYNC_ENDPOINT = f"{WEBHOOK_BASE_URL}/webhook/alerts/sync"
HEALTH_ENDPOINT = f"{WEBHOOK_BASE_URL}/health"


def test_health_check():
    """Test the health endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(HEALTH_ENDPOINT)
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def create_sample_usage_alerts():
    """Create sample usage metrics alerts"""
    alerts = []
    
    # 1. High volume trading alert
    high_volume_alert = create_high_volume_alert("12345", 150, 100)
    alerts.append(high_volume_alert)
    
    # 2. SLA violation alert
    sla_alert = create_sla_violation_alert("long-buy", 25.5, 23.0)
    alerts.append(sla_alert)
    
    # 3. High value transaction alert
    high_value_alert = create_high_value_transaction_alert("67890", 50000.0, 10000.0)
    alerts.append(high_value_alert)
    
    # 4. Custom balance change alert
    balance_alert = UsageMetricsAlert(
        alert_id=f"balance-change-{datetime.utcnow().timestamp()}",
        metric_type=MetricType.BALANCE_CHANGE,
        severity=AlertSeverity.MEDIUM,
        threshold_condition=ThresholdCondition(
            operator=ThresholdOperator.GREATER_THAN,
            value=10000.0,
            unit="dollars"
        ),
        metric_data=MetricData(
            metric_name="account_balance_change",
            current_value=15000.0,
            threshold_value=10000.0,
            account_id="11111",
            timestamp=datetime.utcnow()
        ),
        title="Significant Balance Change Alert - Account 11111",
        description="Account 11111 has experienced a significant balance change of $15,000, exceeding threshold of $10,000",
        tags=["balance", "account", "financial"]
    )
    alerts.append(balance_alert)
    
    return alerts


def test_async_webhook():
    """Test the asynchronous webhook endpoint"""
    print("\n🚀 Testing async webhook endpoint...")
    
    # Create sample alerts
    alerts = create_sample_usage_alerts()
    
    # Create webhook request
    request_data = WebhookRequest(
        alerts=alerts,
        batch_id="test-batch-async",
        source_system="EasyTrade",
        timestamp=datetime.utcnow()
    )
    
    try:
        # Send request
        response = requests.post(
            ASYNC_ENDPOINT,
            json=request_data.model_dump(),
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Async webhook successful")
            print(f"   Processed: {result.get('processed_count')} alerts")
            print(f"   Workflow IDs: {result.get('workflow_ids')}")
            print(f"   Success: {result.get('success')}")
            return True
        else:
            print(f"❌ Async webhook failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Async webhook error: {e}")
        return False


def test_sync_webhook():
    """Test the synchronous webhook endpoint"""
    print("\n⚡ Testing sync webhook endpoint...")
    
    # Create sample alerts (just one for sync testing)
    alerts = [create_high_volume_alert("99999", 200, 150)]
    
    # Create webhook request
    request_data = WebhookRequest(
        alerts=alerts,
        batch_id="test-batch-sync",
        source_system="EasyTrade",
        timestamp=datetime.utcnow()
    )
    
    try:
        # Send request
        response = requests.post(
            SYNC_ENDPOINT,
            json=request_data.model_dump(),
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Sync webhook successful")
            print(f"   Processed: {result.get('processed_count')} alerts")
            print(f"   Workflow IDs: {result.get('workflow_ids')}")
            print(f"   Success: {result.get('success')}")
            return True
        else:
            print(f"❌ Sync webhook failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Sync webhook error: {e}")
        return False


def test_single_alert():
    """Test sending a single alert"""
    print("\n📊 Testing single alert...")
    
    # Create a single high-value transaction alert
    alert = create_high_value_transaction_alert("55555", 75000.0, 50000.0)
    
    # Create webhook request
    request_data = WebhookRequest(
        alerts=[alert],
        source_system="EasyTrade",
        timestamp=datetime.utcnow()
    )
    
    try:
        # Send request
        response = requests.post(
            ASYNC_ENDPOINT,
            json=request_data.model_dump(),
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Single alert successful")
            print(f"   Alert ID: {alert.alert_id}")
            print(f"   Metric Type: {alert.metric_type}")
            print(f"   Severity: {alert.severity}")
            print(f"   Workflow ID: {result.get('workflow_ids', [])[0] if result.get('workflow_ids') else 'None'}")
            return True
        else:
            print(f"❌ Single alert failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Single alert error: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 Usage Metrics Webhook Test Suite")
    print("=" * 50)
    
    # Test health check first
    if not test_health_check():
        print("❌ Health check failed. Make sure the webhook server is running.")
        return
    
    # Run tests
    tests = [
        ("Single Alert", test_single_alert),
        ("Async Webhook", test_async_webhook),
        ("Sync Webhook", test_sync_webhook),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📋 Test Summary")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the webhook server logs.")


if __name__ == "__main__":
    main() 