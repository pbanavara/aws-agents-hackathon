# Workflows Directory

This directory contains all Temporal workflows and related components for the AWS Agents Hackathon project.

## 📁 File Structure

### Consolidated Workflows
- **`all_workflows.py`** - **MAIN FILE** - All workflows consolidated into one file:
  - UpsellWorkflow: Customer upsell automation
  - SampleWorkflow: Basic sample workflow
  - All activities and helper functions
  - Built-in usage data endpoint

### Workers
- **`consolidated_worker.py`** - **MAIN WORKER** - Handles all workflows

### Testing & Utilities
- **`test_consolidated_workflows.py`** - **MAIN TEST** - Tests all consolidated workflows
- **`test_usage_endpoint.py`** - Tests for the usage data endpoint

### Documentation
- **`UPSELL_WORKFLOW_README.md`** - Detailed documentation for the upsell workflow system
- **`README.md`** - This file

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd workflows
pip install -r requirements.txt
```

### 2. Start Temporal Server
```bash
# From project root
docker compose up -d
```

### 3. Run Consolidated Worker
```bash
# Start the main consolidated worker (handles all workflows)
python consolidated_worker.py &
```

### 4. Test All Workflows
```bash
# Test all consolidated workflows
python test_consolidated_workflows.py

# Test usage endpoint specifically
python test_usage_endpoint.py
```

## 🔧 Workflow Features

### Upsell Workflow
- **Activities**: fetch_usage, fetch_contract, ask_claude_for_plan, send_email_draft, post_slack_summary, create_zoom_meeting, log_opportunity
- **Automation Levels**: Full automation, Human intervention, Hybrid
- **Usage Data Endpoint**: Built-in FastAPI server on port 8001 for receiving usage data
- **MongoDB Integration**: Contract data retrieval from MongoDB Atlas



## 🌐 Usage Data Endpoint

The upsell workflow includes a built-in usage data endpoint:

- **URL**: `http://localhost:8001`
- **POST** `/usage/data` - Receive usage data from webhooks
- **GET** `/usage/data/{account_id}` - Retrieve stored usage data
- **GET** `/usage/health` - Health check

### Example Usage Data
```json
{
  "account_id": "account_000001",
  "current_usage": 2500.0,
  "usage_trend": "increasing",
  "usage_period": "monthly",
  "threshold_exceeded": 2000.0,
  "metric_type": "trade_volume",
  "additional_context": {
    "source": "webhook",
    "alert_severity": "high"
  }
}
```

## 📊 Integration Points

- **Webhook**: Receives alerts and triggers workflows
- **MongoDB**: Stores and retrieves contract data
- **Usage Endpoint**: Receives real-time usage metrics
- **Temporal**: Orchestrates workflow execution

## 🔍 Monitoring

- **Temporal UI**: `http://localhost:8080`
- **Usage Endpoint Health**: `http://localhost:8001/usage/health`
- **Workflow Logs**: Check worker console output

## 📝 Notes

- All workflows are designed to be fault-tolerant with proper error handling
- The usage data endpoint uses in-memory storage (can be extended to persistent storage)
- Workers should be restarted if workflows are modified
- MongoDB connection is configured for Atlas cluster 