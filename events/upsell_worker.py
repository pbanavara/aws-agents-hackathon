#!/usr/bin/env python3
"""
Worker for the Upsell Workflow
Handles all upsell-related activities and workflows
"""

import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker

# Import our upsell workflow and activities
from upsell_workflow import (
    UpsellWorkflow,
    fetch_usage,
    fetch_contract,
    ask_claude_for_plan,
    send_email_draft,
    post_slack_summary,
    create_zoom_meeting,
    log_opportunity
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main worker function"""
    logger.info("Starting Upsell Workflow Worker...")
    
    # Connect to Temporal server
    client = await Client.connect("localhost:7233")
    
    # Create worker
    worker = Worker(
        client,
        task_queue="upsell-task-queue",
        workflows=[UpsellWorkflow],
        activities=[
            fetch_usage,
            fetch_contract,
            ask_claude_for_plan,
            send_email_draft,
            post_slack_summary,
            create_zoom_meeting,
            log_opportunity
        ],
    )
    
    logger.info("Upsell worker started. Listening for tasks...")
    logger.info("Task queue: upsell-task-queue")
    logger.info("Workflows: UpsellWorkflow")
    logger.info("Activities: fetch_usage, fetch_contract, ask_claude_for_plan, send_email_draft, post_slack_summary, create_zoom_meeting, log_opportunity")
    
    # Run the worker
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main()) 