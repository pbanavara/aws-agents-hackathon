import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker

# Import our workflows and activities
from alert_workflow import (
    AlertProcessingWorkflow, 
    BatchAlertProcessingWorkflow,
    process_alert,
    send_notification,
    update_alert_status
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main worker function"""
    logger.info("Starting Alert Processing Worker...")
    
    # Connect to Temporal server
    client = await Client.connect("localhost:7233")
    
    # Create worker
    worker = Worker(
        client,
        task_queue="alert-task-queue",
        workflows=[
            AlertProcessingWorkflow,
            BatchAlertProcessingWorkflow
        ],
        activities=[
            process_alert,
            send_notification,
            update_alert_status
        ],
    )
    
    logger.info("Alert Processing Worker started. Listening for tasks...")
    
    # Run the worker
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main()) 