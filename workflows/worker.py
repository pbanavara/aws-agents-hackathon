import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from sample_workflow import SampleWorkflow

async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="sample-task-queue",
        workflows=[SampleWorkflow],
    )
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main()) 