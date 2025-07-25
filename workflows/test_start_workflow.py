import asyncio
from temporalio.client import Client
from sample_workflow import SampleWorkflow

async def main():
    client = await Client.connect("localhost:7233")
    result = await client.execute_workflow(
        SampleWorkflow.run,
        "World",
        id="sample-workflow-id",
        task_queue="sample-task-queue",
    )
    print("Workflow result:", result)

if __name__ == "__main__":
    asyncio.run(main()) 