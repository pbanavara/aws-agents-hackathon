import asyncio
import json
import requests
from datetime import datetime
from alert_schema import AlertPayload, AlertSource, AlertContext, AlertType, AlertSeverity


def create_sample_alerts():
    """Create sample alert data for testing"""
    
    # Sample security alert
    security_alert = AlertPayload(
        title="Suspicious Login Attempt Detected",
        description="Multiple failed login attempts detected from unknown IP address",
        message="Security alert: 10 failed login attempts from 192.168.1.100",
        type=AlertType.SECURITY,
        severity=AlertSeverity.HIGH,
        source=AlertSource(
            name="Security Monitoring System",
            type="security",
            identifier="sec-mon-001"
        ),
        context=AlertContext(
            environment="production",
            service="user-authentication",
            region="us-west-2",
            tags={"team": "security", "component": "auth"}
        ),
        data={
            "ip_address": "192.168.1.100",
            "failed_attempts": 10,
            "target_user": "admin"
        },
        priority=8
    )
    
    # Sample performance alert
    performance_alert = AlertPayload(
        title="High CPU Usage Detected",
        description="CPU usage has exceeded 90% for the last 5 minutes",
        message="Performance alert: CPU usage at 95% on web-server-01",
        type=AlertType.PERFORMANCE,
        severity=AlertSeverity.MEDIUM,
        source=AlertSource(
            name="CloudWatch",
            type="aws",
            identifier="cw-metrics"
        ),
        context=AlertContext(
            environment="production",
            service="web-application",
            component="web-server",
            region="us-west-2"
        ),
        metrics={
            "cpu_usage": 95.2,
            "memory_usage": 78.5,
            "disk_usage": 45.1
        },
        priority=5
    )
    
    # Sample infrastructure alert
    infrastructure_alert = AlertPayload(
        title="Database Connection Pool Exhausted",
        description="All database connections are in use, new requests are being queued",
        message="Infrastructure alert: Database connection pool at 100% capacity",
        type=AlertType.INFRASTRUCTURE,
        severity=AlertSeverity.CRITICAL,
        source=AlertSource(
            name="Database Monitoring",
            type="custom",
            identifier="db-mon-001"
        ),
        context=AlertContext(
            environment="production",
            service="database",
            component="postgresql",
            region="us-west-2"
        ),
        data={
            "connection_pool_size": 100,
            "active_connections": 100,
            "queued_requests": 15
        },
        priority=9
    )
    
    return [security_alert, performance_alert, infrastructure_alert]


def test_webhook_sync():
    """Test the synchronous webhook endpoint"""
    print("Testing synchronous webhook endpoint...")
    
    # Create sample alerts
    alerts = create_sample_alerts()
    
    # Prepare request payload
    payload = {
        "alerts": [alert.model_dump() for alert in alerts],
        "batch_id": f"test-batch-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
        "metadata": {
            "test": True,
            "source": "test-script"
        }
    }
    
    # Send request
    try:
        response = requests.post(
            "http://localhost:8000/webhook/alerts/sync",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


def test_webhook_async():
    """Test the asynchronous webhook endpoint"""
    print("\nTesting asynchronous webhook endpoint...")
    
    # Create sample alerts
    alerts = create_sample_alerts()
    
    # Prepare request payload
    payload = {
        "alerts": [alert.model_dump() for alert in alerts],
        "batch_id": f"test-batch-async-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
        "metadata": {
            "test": True,
            "source": "test-script"
        }
    }
    
    # Send request
    try:
        response = requests.post(
            "http://localhost:8000/webhook/alerts",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


def test_health_check():
    """Test the health check endpoint"""
    print("\nTesting health check endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


def test_single_alert():
    """Test with a single alert"""
    print("\nTesting single alert...")
    
    # Create a single alert
    alert = AlertPayload(
        title="Test Single Alert",
        description="This is a test alert for single alert processing",
        message="Test message",
        type=AlertType.CUSTOM,
        severity=AlertSeverity.LOW,
        source=AlertSource(
            name="Test System",
            type="test",
            identifier="test-001"
        )
    )
    
    payload = {
        "alerts": [alert.model_dump()],
        "metadata": {"test": True}
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/webhook/alerts",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


if __name__ == "__main__":
    print("Alert Webhook Test Script")
    print("=" * 50)
    
    # Test health check first
    test_health_check()
    
    # Test single alert
    test_single_alert()
    
    # Test async webhook
    test_webhook_async()
    
    # Test sync webhook
    test_webhook_sync()
    
    print("\nTest completed!") 