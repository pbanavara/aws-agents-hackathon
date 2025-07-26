# Events Directory - Webhook System

This directory contains a FastAPI-based webhook system for receiving and processing alerts using Temporal workflows. The system provides reliable, scalable alert processing with automatic retries, monitoring, and orchestration.

**Note**: Workflow files have been moved to the `workflows/` directory. This directory now focuses on webhook endpoints and event processing.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   External      │    │   FastAPI       │    │   Temporal      │
│   Systems       │───▶│   Webhook       │───▶│   Workflows     │
│   (Alerts)      │    │   (Port 8000)   │    │   (Port 7233)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Alert Schema  │    │   Alert Worker  │
                       │   Validation    │    │   Processing    │
                       └─────────────────┘    └─────────────────┘
```

## Components

### 1. Alert Schema (`alert_schema.py`)
- **AlertPayload**: Main alert data structure
- **AlertSeverity**: Severity levels (LOW, MEDIUM, HIGH, CRITICAL)
- **AlertType**: Alert types (SECURITY, PERFORMANCE, INFRASTRUCTURE, etc.)
- **AlertSource**: Source system information
- **AlertContext**: Contextual information (environment, service, etc.)
- **WebhookRequest/Response**: API request/response models

### 2. Alert Workflows (`workflows/alert_workflow.py`)
- **AlertProcessingWorkflow**: Processes individual alerts
- **BatchAlertProcessingWorkflow**: Processes multiple alerts in parallel
- **Activities**: 
  - `process_alert`: Core alert processing logic
  - `send_notification`: Sends notifications (email, Slack)
  - `update_alert_status`: Updates alert status in external systems

### 3. FastAPI Webhook (`webhook.py`)
- **POST /webhook/alerts**: Asynchronous alert processing
- **POST /webhook/alerts/sync**: Synchronous alert processing
- **GET /health**: Health check endpoint
- **GET /docs**: Auto-generated API documentation

### 4. Alert Worker (`workflows/alert_worker.py`)
- Temporal worker that processes alert workflows
- Runs activities and manages workflow execution

## Setup Instructions

### Prerequisites
1. Python 3.8+
2. Docker Desktop (for Temporal server)
3. Temporal server running (see workflows/README.md)

### 1. Install Dependencies
```bash
cd events
pip install -r requirements.txt
```

### 2. Start Temporal Server
```bash
# From project root
cd ..
export ELASTICSEARCH_VERSION=7.10.1
export POSTGRESQL_VERSION=13
export TEMPORAL_VERSION=1.21.3
export TEMPORAL_ADMINTOOLS_VERSION=1.21.3
export TEMPORAL_UI_VERSION=2.15.0
docker compose up -d
```

### 3. Start Alert Worker
```bash
cd workflows
python alert_worker.py
```

### 4. Start Webhook Server
```bash
# In a new terminal
cd events
python webhook.py
```

The webhook will be available at `http://localhost:8000`

## API Endpoints

### POST /webhook/alerts
Process alerts asynchronously using Temporal workflows.

**Request Body:**
```json
{
  "alerts": [
    {
      "title": "High CPU Usage",
      "description": "CPU usage exceeded 90%",
      "type": "performance",
      "severity": "high",
      "source": {
        "name": "CloudWatch",
        "type": "aws"
      }
    }
  ],
  "batch_id": "optional-batch-id",
  "metadata": {
    "source": "monitoring-system"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Processed 1 alerts successfully",
  "processed_count": 1,
  "workflow_ids": ["alert-123-20231201-143022"],
  "errors": [],
  "timestamp": "2023-12-01T14:30:22.123456"
}
```

### POST /webhook/alerts/sync
Process alerts synchronously and wait for completion.

### GET /health
Health check endpoint.

### GET /docs
Interactive API documentation (Swagger UI).

## Alert Schema Examples

### Security Alert
```json
{
  "title": "Suspicious Login Attempt",
  "description": "Multiple failed login attempts detected",
  "type": "security",
  "severity": "high",
  "source": {
    "name": "Security Monitoring",
    "type": "security"
  },
  "context": {
    "environment": "production",
    "service": "user-authentication"
  },
  "data": {
    "ip_address": "192.168.1.100",
    "failed_attempts": 10
  }
}
```

### Performance Alert
```json
{
  "title": "High CPU Usage",
  "description": "CPU usage exceeded 90%",
  "type": "performance",
  "severity": "medium",
  "source": {
    "name": "CloudWatch",
    "type": "aws"
  },
  "metrics": {
    "cpu_usage": 95.2,
    "memory_usage": 78.5
  }
}
```

### Infrastructure Alert
```json
{
  "title": "Database Connection Pool Exhausted",
  "description": "All database connections in use",
  "type": "infrastructure",
  "severity": "critical",
  "source": {
    "name": "Database Monitoring",
    "type": "custom"
  },
  "data": {
    "connection_pool_size": 100,
    "active_connections": 100
  }
}
```

## Testing

### Run Test Script
```bash
python test_webhook.py
```

### Manual Testing with curl
```bash
# Health check
curl http://localhost:8000/health

# Send single alert
curl -X POST http://localhost:8000/webhook/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "alerts": [{
      "title": "Test Alert",
      "description": "Test description",
      "type": "custom",
      "severity": "low",
      "source": {
        "name": "Test System",
        "type": "test"
      }
    }]
  }'
```

## Usage Patterns

### 1. Single Alert Processing
- Use for individual alerts that need immediate processing
- Triggers `AlertProcessingWorkflow`
- Best for high-priority, time-sensitive alerts

### 2. Batch Alert Processing
- Use for multiple alerts from the same source
- Triggers `BatchAlertProcessingWorkflow`
- Processes alerts in parallel for better performance
- Ideal for bulk alerts from monitoring systems

### 3. Synchronous Processing
- Use `/webhook/alerts/sync` for immediate feedback
- Waits for workflow completion before responding
- Good for testing and debugging

### 4. Asynchronous Processing
- Use `/webhook/alerts` for production workloads
- Returns immediately with workflow IDs
- Better for high-throughput scenarios

## Monitoring

### Temporal Web UI
- Access at `http://localhost:8080`
- Monitor workflow execution
- View workflow history and logs
- Debug failed workflows

### Logs
- Webhook logs: Check the FastAPI server output
- Worker logs: Check the alert worker output
- Workflow logs: Available in Temporal Web UI

## Error Handling

### Retry Policy
- Activities have automatic retry policies
- Failed activities are retried with exponential backoff
- Maximum retry attempts are configured per activity

### Error Response
- Validation errors return 400 status
- Temporal connection errors return 500 status
- Detailed error messages in response body

## Production Considerations

### Security
- Add authentication/authorization
- Validate webhook signatures
- Use HTTPS in production
- Configure CORS appropriately

### Scalability
- Run multiple worker instances
- Use load balancer for webhook endpoints
- Configure Temporal task queue partitioning
- Monitor resource usage

### Monitoring
- Add metrics collection (Prometheus)
- Set up alerting for webhook failures
- Monitor Temporal workflow metrics
- Track alert processing latency

## Troubleshooting

### Common Issues

1. **Temporal Connection Failed**
   - Ensure Temporal server is running
   - Check `docker ps` for container status
   - Verify port 7233 is accessible

2. **Worker Not Processing Tasks**
   - Check worker logs for errors
   - Verify task queue name matches
   - Ensure workflows/activities are registered

3. **Webhook Validation Errors**
   - Check alert schema compliance
   - Verify required fields are present
   - Use `/docs` endpoint to test payload format

4. **Workflow Timeouts**
   - Increase activity timeouts
   - Check for long-running operations
   - Monitor Temporal server resources 