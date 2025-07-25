from flask import Flask, request, jsonify
import asyncio
import uuid
from temporalio.client import Client
from sample_workflow import SampleWorkflow

app = Flask(__name__)

# Global client variable
temporal_client = None

async def get_temporal_client():
    """Get or create Temporal client"""
    global temporal_client
    if temporal_client is None:
        temporal_client = await Client.connect("localhost:7233")
    return temporal_client

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint that receives payload and starts a Temporal workflow"""
    try:
        # Get the JSON payload from the request
        payload = request.get_json()
        
        if payload is None:
            return jsonify({"error": "No JSON payload provided"}), 400
        
        # Generate a unique workflow ID
        workflow_id = f"webhook-workflow-{uuid.uuid4()}"
        
        # Start the workflow asynchronously
        asyncio.create_task(start_workflow(workflow_id, payload))
        
        return jsonify({
            "status": "success",
            "message": "Workflow started successfully",
            "workflow_id": workflow_id,
            "payload": payload
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

async def start_workflow(workflow_id: str, payload: dict):
    """Start a Temporal workflow with the given payload"""
    try:
        client = await get_temporal_client()
        
        # Start the workflow with the payload as input
        handle = await client.start_workflow(
            SampleWorkflow.run,
            str(payload),  # Convert payload to string for the workflow
            id=workflow_id,
            task_queue="sample-task-queue",
        )
        
        print(f"Started workflow {workflow_id} with payload: {payload}")
        
    except Exception as e:
        print(f"Error starting workflow {workflow_id}: {e}")

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    print("Starting webhook server on http://localhost:5000")
    print("Webhook endpoint: POST http://localhost:5000/webhook")
    print("Health check: GET http://localhost:5000/health")
    app.run(host='0.0.0.0', port=5000, debug=True) 