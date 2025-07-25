#!/usr/bin/env python3
"""
Test script for the Usage Data Endpoint
Demonstrates how to post usage data to the fetch_usage endpoint
"""

import asyncio
import requests
import json
import time
from datetime import datetime


def test_usage_endpoint():
    """Test the usage data endpoint"""
    print("🧪 Testing Usage Data Endpoint")
    print("=" * 40)
    
    base_url = "http://localhost:8001"
    
    # Test 1: Health check
    print("\n1️⃣ Testing Health Check")
    try:
        response = requests.get(f"{base_url}/usage/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Status: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Could not connect to usage endpoint: {e}")
        print("   Make sure the upsell workflow is running to start the endpoint")
        return
    
    # Test 2: Post usage data for multiple accounts
    print("\n2️⃣ Posting Usage Data")
    
    test_accounts = [
        {
            "account_id": "account_000001",
            "current_usage": 2500.0,
            "usage_trend": "increasing",
            "usage_period": "monthly",
            "threshold_exceeded": 2000.0,
            "metric_type": "trade_volume",
            "additional_context": {
                "source": "webhook_test",
                "alert_severity": "high",
                "previous_usage": 1800.0
            }
        },
        {
            "account_id": "account_000002",
            "current_usage": 85000.0,
            "usage_trend": "increasing",
            "usage_period": "monthly",
            "threshold_exceeded": 50000.0,
            "metric_type": "trade_value",
            "additional_context": {
                "source": "webhook_test",
                "alert_severity": "critical",
                "previous_usage": 65000.0
            }
        },
        {
            "account_id": "account_000003",
            "current_usage": 28.5,
            "usage_trend": "decreasing",
            "usage_period": "monthly",
            "threshold_exceeded": 23.0,
            "metric_type": "latency",
            "additional_context": {
                "source": "webhook_test",
                "alert_severity": "medium",
                "previous_usage": 25.0
            }
        }
    ]
    
    for i, account_data in enumerate(test_accounts, 1):
        try:
            print(f"   Posting data for account {account_data['account_id']}...")
            response = requests.post(
                f"{base_url}/usage/data",
                json=account_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success: {result['message']}")
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error posting data: {e}")
    
    # Test 3: Retrieve usage data
    print("\n3️⃣ Retrieving Usage Data")
    
    for account_data in test_accounts:
        account_id = account_data['account_id']
        try:
            response = requests.get(f"{base_url}/usage/data/{account_id}")
            
            if response.status_code == 200:
                result = response.json()
                data = result['data']
                print(f"   ✅ Retrieved data for {account_id}:")
                print(f"      Usage: {data['current_usage']} {data['metric_type']}")
                print(f"      Trend: {data['usage_trend']}")
                print(f"      Threshold: {data['threshold_exceeded']}")
            else:
                print(f"   ❌ Failed to retrieve data for {account_id}: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error retrieving data for {account_id}: {e}")
    
    # Test 4: Test with non-existent account
    print("\n4️⃣ Testing Non-existent Account")
    try:
        response = requests.get(f"{base_url}/usage/data/non_existent_account")
        
        if response.status_code == 404:
            print("   ✅ Correctly returned 404 for non-existent account")
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error testing non-existent account: {e}")
    
    print("\n✅ Usage endpoint test completed!")


def simulate_webhook_usage_data():
    """Simulate webhook posting usage data"""
    print("\n🔄 Simulating Webhook Usage Data")
    print("=" * 40)
    
    base_url = "http://localhost:8001"
    
    # Simulate real-time usage data from webhook
    usage_scenarios = [
        {
            "account_id": "account_000001",
            "current_usage": 3000.0,
            "usage_trend": "increasing",
            "usage_period": "monthly",
            "threshold_exceeded": 2000.0,
            "metric_type": "trade_volume",
            "additional_context": {
                "source": "webhook_simulation",
                "timestamp": datetime.now().isoformat(),
                "alert_triggered": True
            }
        },
        {
            "account_id": "account_000002",
            "current_usage": 95000.0,
            "usage_trend": "increasing",
            "usage_period": "monthly",
            "threshold_exceeded": 50000.0,
            "metric_type": "trade_value",
            "additional_context": {
                "source": "webhook_simulation",
                "timestamp": datetime.now().isoformat(),
                "alert_triggered": True
            }
        }
    ]
    
    for scenario in usage_scenarios:
        try:
            print(f"📊 Posting usage data for {scenario['account_id']}...")
            response = requests.post(
                f"{base_url}/usage/data",
                json=scenario,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print(f"   ✅ Posted: {scenario['current_usage']} {scenario['metric_type']}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Small delay between posts
        time.sleep(1)
    
    print("✅ Webhook simulation completed!")


def main():
    """Main test function"""
    print("🚀 Usage Data Endpoint Test Suite")
    print("=" * 50)
    
    # Wait a moment for the endpoint to start
    print("⏳ Waiting for usage endpoint to start...")
    time.sleep(2)
    
    # Run tests
    test_usage_endpoint()
    simulate_webhook_usage_data()
    
    print("\n📋 Test Summary:")
    print("   - Usage endpoint should be running on http://localhost:8001")
    print("   - Webhook can POST usage data to /usage/data")
    print("   - Upsell workflow can fetch data via fetch_usage activity")
    print("   - Health check available at /usage/health")


if __name__ == "__main__":
    main() 