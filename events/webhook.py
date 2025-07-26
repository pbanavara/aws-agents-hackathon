import asyncio
import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

# Import our schemas and workflows
from usage_metrics_schema import WebhookRequest, WebhookResponse, UsageMetricsAlert
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from workflows.all_workflows import (
    trigger_upsell_workflow, 
    AutomationLevel
)

# Import Temporal client
from temporalio.client import Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Alert Webhook API",
    description="Webhook endpoint for receiving and processing alerts",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Temporal client
temporal_client: Client = None


@app.on_event("startup")
async def startup_event():
    """Initialize Temporal client on startup"""
    global temporal_client
    try:
        temporal_client = await Client.connect("localhost:7233")
        logger.info("Connected to Temporal server")
    except Exception as e:
        logger.error(f"Failed to connect to Temporal server: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global temporal_client
    if temporal_client:
        # Temporal client doesn't have a close method, just log the shutdown
        logger.info("Shutting down webhook server")





async def trigger_upsell_if_needed(alert_data: Dict[str, Any]) -> Optional[str]:
    """Trigger upsell workflow if the alert meets criteria"""
    global temporal_client
    
    if not temporal_client:
        logger.warning("Temporal client not available for upsell workflow")
        return None
    
    try:
        # Check if this alert should trigger an upsell workflow
        metric_type = alert_data.get('metric_type', '')
        severity = alert_data.get('severity', '')
        current_value = alert_data.get('metric_data', {}).get('current_value', 0)
        
        # Trigger upsell for high-value or critical alerts
        should_trigger_upsell = (
            severity in ['high', 'critical'] or
            current_value > 1000 or  # High value threshold
            metric_type in ['trade_volume', 'trade_value', 'balance_change']
        )
        
        if should_trigger_upsell:
            account_id = alert_data.get('metric_data', {}).get('account_id', 'unknown')
            event_id = alert_data.get('alert_id', 'unknown')
            
            logger.info(f"Triggering upsell workflow for account {account_id}, event {event_id}")
            
            # Determine automation level based on alert severity
            automation_level = AutomationLevel.HYBRID
            if severity == 'critical':
                automation_level = AutomationLevel.FULL_AUTOMATION
            elif severity == 'low':
                automation_level = AutomationLevel.HUMAN_INTERVENTION
            
            # Trigger the upsell workflow
            upsell_workflow_id = await trigger_upsell_workflow(
                client=temporal_client,
                account_id=account_id,
                event_id=event_id,
                automation_level=automation_level,
                metric_type=metric_type
            )
            
            logger.info(f"Upsell workflow triggered: {upsell_workflow_id}")
            return upsell_workflow_id
            
    except Exception as e:
        logger.error(f"Failed to trigger upsell workflow: {e}")
        # Don't fail the main alert processing if upsell fails
        return None
    
    return None


@app.post("/webhook/alerts", response_model=WebhookResponse)
async def receive_alerts(request: WebhookRequest, background_tasks: BackgroundTasks):
    """
    Receive alerts via webhook and trigger Temporal workflows
    
    This endpoint accepts a list of alerts and processes them asynchronously
    using Temporal workflows for reliable processing, retries, and monitoring.
    """
    try:
        logger.info(f"Received webhook request with {len(request.alerts)} alerts")
        
        # Validate alerts
        if not request.alerts:
            raise HTTPException(status_code=400, detail="No alerts provided")
        
        # Convert alerts to dictionaries for workflow processing
        alerts_data = []
        for alert in request.alerts:
            # Generate alert_id if not provided
            if not alert.alert_id:
                alert.alert_id = str(uuid.uuid4())
            
            # Convert to dict using model_dump
            alert_dict = alert.model_dump()
            alerts_data.append(alert_dict)
        
        workflow_ids = []
        errors = []
        
        # Process alerts - trigger upsell workflows for each alert
        for alert_data in alerts_data:
            try:
                # Trigger upsell workflow for each alert
                workflow_id = await trigger_upsell_if_needed(alert_data)
                if workflow_id:
                    workflow_ids.append(workflow_id)
                    
            except Exception as e:
                error_msg = f"Failed to process alert {alert_data.get('alert_id')}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # Prepare response
        success = len(errors) == 0
        processed_count = len(alerts_data) if success else 0
        
        response = WebhookResponse(
            success=success,
            message=f"Processed {processed_count} alerts successfully" if success else f"Failed to process {len(alerts_data)} alerts",
            processed_count=processed_count,
            workflow_ids=workflow_ids,
            errors=errors,
            timestamp=datetime.utcnow()
        )
        
        logger.info(f"Webhook response: {response}")
        return response
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid request format: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/webhook/alerts/sync", response_model=WebhookResponse)
async def receive_alerts_sync(request: WebhookRequest):
    """
    Receive alerts via webhook and process them synchronously
    
    This endpoint processes alerts immediately and returns the results.
    Use this for testing or when immediate feedback is required.
    """
    try:
        logger.info(f"Received sync webhook request with {len(request.alerts)} alerts")
        
        # Validate alerts
        if not request.alerts:
            raise HTTPException(status_code=400, detail="No alerts provided")
        
        # Convert alerts to dictionaries
        alerts_data = []
        for alert in request.alerts:
            if not alert.alert_id:
                alert.alert_id = str(uuid.uuid4())
            alert_dict = alert.model_dump()
            alerts_data.append(alert_dict)
        
        workflow_ids = []
        errors = []
        
        # Process each alert synchronously - trigger upsell workflows
        for alert_data in alerts_data:
            try:
                workflow_id = await trigger_upsell_if_needed(alert_data)
                if workflow_id:
                    workflow_ids.append(workflow_id)
                    
                    # Wait for workflow completion (for sync endpoint)
                    if temporal_client:
                        handle = temporal_client.get_workflow_handle(workflow_id)
                        await handle.result()  # Wait for completion
                    
            except Exception as e:
                error_msg = f"Failed to process alert {alert_data.get('alert_id')}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        success = len(errors) == 0
        processed_count = len(alerts_data) - len(errors)
        
        response = WebhookResponse(
            success=success,
            message=f"Processed {processed_count} alerts synchronously" if success else f"Failed to process {len(errors)} alerts",
            processed_count=processed_count,
            workflow_ids=workflow_ids,
            errors=errors,
            timestamp=datetime.utcnow()
        )
        
        return response
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid request format: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global temporal_client
    
    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "temporal_connected": temporal_client is not None
    }
    
    if temporal_client is None:
        status["status"] = "unhealthy"
        status["error"] = "Temporal client not connected"
    
    return status


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Alert Webhook API",
        "version": "1.0.0",
        "endpoints": {
            "POST /webhook/alerts": "Receive alerts asynchronously",
            "POST /webhook/alerts/sync": "Receive alerts synchronously",
            "GET /health": "Health check",
            "GET /docs": "API documentation"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 