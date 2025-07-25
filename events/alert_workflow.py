import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from temporalio import workflow, activity
from temporalio.common import RetryPolicy

# Import the alert schema
from alert_schema import AlertPayload, AlertSeverity, AlertType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@activity.defn
async def process_alert(alert_data: Dict[str, Any]) -> Dict[str, Any]:
    """Activity to process a single alert"""
    logger.info(f"Processing alert: {alert_data.get('title', 'Unknown')}")
    
    # Simulate some processing time
    await asyncio.sleep(1)
    
    # Process based on alert type
    alert_type = alert_data.get('type')
    severity = alert_data.get('severity')
    
    result = {
        'alert_id': alert_data.get('id'),
        'processed_at': datetime.utcnow().isoformat(),
        'status': 'processed',
        'actions_taken': []
    }
    
    if alert_type == AlertType.SECURITY:
        result['actions_taken'].append('security_scan_initiated')
        result['actions_taken'].append('threat_assessment_started')
        
    elif alert_type == AlertType.PERFORMANCE:
        result['actions_taken'].append('performance_analysis_started')
        result['actions_taken'].append('scaling_recommendations_generated')
        
    elif alert_type == AlertType.INFRASTRUCTURE:
        result['actions_taken'].append('infrastructure_health_check')
        result['actions_taken'].append('backup_verification')
    
    # High severity alerts get additional processing
    if severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
        result['actions_taken'].append('immediate_notification_sent')
        result['actions_taken'].append('escalation_triggered')
    
    logger.info(f"Alert processed: {result}")
    return result


@activity.defn
async def send_notification(alert_data: Dict[str, Any], processed_result: Dict[str, Any]) -> Dict[str, Any]:
    """Activity to send notifications about processed alerts"""
    logger.info(f"Sending notification for alert: {alert_data.get('title', 'Unknown')}")
    
    # Simulate notification sending
    await asyncio.sleep(0.5)
    
    notification_result = {
        'notification_sent': True,
        'recipients': ['oncall@company.com'],
        'channel': 'email',
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # Add Slack notification for high severity
    if alert_data.get('severity') in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
        notification_result['recipients'].append('#alerts-slack')
        notification_result['channel'] = 'slack'
    
    logger.info(f"Notification sent: {notification_result}")
    return notification_result


@activity.defn
async def update_alert_status(alert_id: str, status: str) -> Dict[str, Any]:
    """Activity to update alert status in external systems"""
    logger.info(f"Updating alert status: {alert_id} -> {status}")
    
    # Simulate status update
    await asyncio.sleep(0.3)
    
    return {
        'alert_id': alert_id,
        'status_updated': True,
        'new_status': status,
        'updated_at': datetime.utcnow().isoformat()
    }


@workflow.defn
class AlertProcessingWorkflow:
    """Workflow to process alerts received from webhook"""
    
    @workflow.run
    async def run(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main workflow execution"""
        logger.info(f"Starting alert processing workflow for: {alert_data.get('title', 'Unknown')}")
        
        # Process the alert
        processed_result = await workflow.execute_activity(
            process_alert,
            alert_data,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                maximum_attempts=3
            )
        )
        
        # Send notifications
        notification_result = await workflow.execute_activity(
            send_notification,
            alert_data,
            processed_result,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=5),
                maximum_attempts=2
            )
        )
        
        # Update alert status
        status_result = await workflow.execute_activity(
            update_alert_status,
            alert_data.get('id', 'unknown'),
            'acknowledged',
            start_to_close_timeout=timedelta(minutes=1),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=5),
                maximum_attempts=2
            )
        )
        
        # Compile final result
        workflow_result = {
            'workflow_id': workflow.info().workflow_id,
            'alert_id': alert_data.get('id'),
            'processing_completed': True,
            'processed_at': datetime.utcnow().isoformat(),
            'results': {
                'processing': processed_result,
                'notification': notification_result,
                'status_update': status_result
            }
        }
        
        logger.info(f"Alert processing workflow completed: {workflow_result}")
        return workflow_result


@workflow.defn
class BatchAlertProcessingWorkflow:
    """Workflow to process multiple alerts in batch"""
    
    @workflow.run
    async def run(self, alerts_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process multiple alerts in parallel"""
        logger.info(f"Starting batch alert processing for {len(alerts_data)} alerts")
        
        # Process all alerts in parallel
        processing_tasks = []
        for alert_data in alerts_data:
            task = workflow.execute_activity(
                process_alert,
                alert_data,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=10),
                    maximum_attempts=3
                )
            )
            processing_tasks.append(task)
        
        # Wait for all processing to complete
        processing_results = await asyncio.gather(*processing_tasks)
        
        # Send notifications for all alerts
        notification_tasks = []
        for i, alert_data in enumerate(alerts_data):
            task = workflow.execute_activity(
                send_notification,
                alert_data,
                processing_results[i],
                start_to_close_timeout=timedelta(minutes=2),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=5),
                    maximum_attempts=2
                )
            )
            notification_tasks.append(task)
        
        notification_results = await asyncio.gather(*notification_tasks)
        
        # Compile batch result
        batch_result = {
            'workflow_id': workflow.info().workflow_id,
            'batch_size': len(alerts_data),
            'processing_completed': True,
            'processed_at': datetime.utcnow().isoformat(),
            'results': {
                'processing': processing_results,
                'notifications': notification_results
            }
        }
        
        logger.info(f"Batch alert processing completed: {batch_result}")
        return batch_result 