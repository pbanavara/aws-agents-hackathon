# Temporal Workflow Setup

This directory contains a sample Temporal workflow setup with the following components:

## Files

- `sample_workflow.py` - A simple Temporal workflow that returns a greeting
- `worker.py` - A Temporal worker that processes workflow tasks
- `test_start_workflow.py` - A test script to start and execute the workflow
- `requirements.txt` - Python dependencies (temporalio)

## Prerequisites

1. Docker Desktop installed and running
2. Python 3.8+ with pip

## Setup Instructions

### 1. Start Temporal Server

The Temporal server is configured to run using Docker Compose. The following containers are started:

- **temporal** - Main Temporal server (port 7233)
- **temporal-ui** - Web UI for monitoring workflows (port 8080)
- **temporal-postgresql** - Database backend
- **temporal-elasticsearch** - Search and visibility backend
- **temporal-admin-tools** - Administrative tools

```bash
# From the project root directory
export ELASTICSEARCH_VERSION=7.10.1
export POSTGRESQL_VERSION=13
export TEMPORAL_VERSION=1.21.3
export TEMPORAL_ADMINTOOLS_VERSION=1.21.3
export TEMPORAL_UI_VERSION=2.15.0
docker compose up -d
```

### 2. Install Python Dependencies

```bash
cd workflows
pip install -r requirements.txt
```

### 3. Start the Worker

```bash
python worker.py
```

The worker will connect to the Temporal server and start polling for workflow tasks.

### 4. Test the Workflow

In a separate terminal:

```bash
python test_start_workflow.py
```

Expected output:
```
Workflow result: Hello, World!
```

## Web UI

You can monitor workflows using the Temporal Web UI at:
http://localhost:8080

## Workflow Details

The sample workflow (`SampleWorkflow`) is a simple workflow that:
- Takes a name parameter as input
- Returns a greeting message: "Hello, {name}!"

## Next Steps

To create your own workflows:

1. Define your workflow in a new Python file using the `@workflow.defn` decorator
2. Add the workflow class to the worker's `workflows` list
3. Create activities if needed using the `@activity.defn` decorator
4. Start the worker and execute your workflow

## Troubleshooting

- If the Temporal server fails to start, check the logs: `docker logs temporal`
- Ensure all environment variables are set before running `docker compose up -d`
- Make sure Docker Desktop is running and has sufficient resources allocated 