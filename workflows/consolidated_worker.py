#!/usr/bin/env python3
"""
Consolidated Worker for All Workflows
Handles all Temporal workflows: Upsell, Alert Processing, and Sample workflows
"""

import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker

# Import all workflows and activities from the consolidated file
from all_workflows import (
    # Workflows
    UpsellWorkflow,
    SampleWorkflow,
    
    # Activities
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
    logger.info("🚀 Starting Consolidated Temporal Worker")
    
    # Connect to Temporal server
    client = await Client.connect("localhost:7233")
    logger.info("✅ Connected to Temporal server")
    
    # Create worker with all workflows and activities
    worker = Worker(
        client,
        task_queue="consolidated-task-queue",
        workflows=[
            UpsellWorkflow,
            SampleWorkflow
        ],
        activities=[
            # Upsell workflow activities
            fetch_usage,
            fetch_contract,
            ask_claude_for_plan,
            send_email_draft,
            post_slack_summary,
            create_zoom_meeting,
            log_opportunity
        ]
    )
    
    logger.info("📋 Registered workflows:")
    logger.info("   • UpsellWorkflow")
    logger.info("   • SampleWorkflow")
    
    logger.info("🔧 Registered activities:")
    logger.info("   • fetch_usage, fetch_contract, ask_claude_for_plan")
    logger.info("   • send_email_draft, post_slack_summary, create_zoom_meeting")
    logger.info("   • log_opportunity")
    
    logger.info("🎯 Task queue: consolidated-task-queue")
    logger.info("⏳ Starting worker...")
    
    # Run the worker
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main()) 