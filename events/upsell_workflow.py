from temporalio import workflow, activity
from temporalio.workflow import execute_activity
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum
import asyncio
from datetime import timedelta, datetime


class AutomationLevel(str, Enum):
    """Configuration for automation level"""
    FULL_AUTOMATION = "full_automation"
    HUMAN_INTERVENTION = "human_intervention"
    HYBRID = "hybrid"


class ReplyStatus(str, Enum):
    """Status of customer reply"""
    PENDING = "pending"
    YES = "yes"
    NO = "no"
    MAYBE = "maybe"


@dataclass
class UsageData:
    """Usage data structure"""
    account_id: str
    current_usage: float
    usage_trend: str  # "increasing", "decreasing", "stable"
    usage_period: str  # "daily", "weekly", "monthly"
    threshold_exceeded: float
    metric_type: str
    additional_context: Dict[str, Any]


@dataclass
class ContractData:
    """Contract data structure"""
    account_id: str
    current_plan: str
    contract_end_date: str
    renewal_date: str
    current_spend: float
    contract_terms: Dict[str, Any]
    contact_info: Dict[str, str]


@dataclass
class UpsellPlan:
    """Upsell plan recommendation"""
    recommended_plan: str
    estimated_value: float
    justification: str
    features: List[str]
    roi_analysis: str
    risk_assessment: str


@dataclass
class EmailDraft:
    """Email draft structure"""
    subject: str
    body: str
    recipient: str
    cc_list: List[str]
    attachments: List[str]
    send_date: Optional[str] = None


@dataclass
class SlackSummary:
    """Slack summary structure"""
    channel: str
    message: str
    attachments: List[Dict[str, Any]]
    thread_ts: Optional[str] = None


@dataclass
class ZoomMeeting:
    """Zoom meeting structure"""
    topic: str
    start_time: str
    duration_minutes: int
    attendees: List[str]
    meeting_url: Optional[str] = None
    meeting_id: Optional[str] = None


@dataclass
class OpportunityLog:
    """Opportunity logging structure"""
    account_id: str
    event_id: str
    opportunity_type: str
    estimated_value: float
    status: str
    created_at: str
    updated_at: str
    notes: str


# Global storage for usage data (in-memory for demo purposes)
usage_data_store = {}

# Activity Definitions
@activity.defn
async def fetch_usage(account_id: str, metric_type: str) -> UsageData:
    """Fetch current usage data for the account from the usage endpoint"""
    try:
        # Check if we have stored usage data for this account
        if account_id in usage_data_store:
            stored_data = usage_data_store[account_id]
            return UsageData(
                account_id=account_id,
                current_usage=stored_data.get('current_usage', 150.0),
                usage_trend=stored_data.get('usage_trend', 'increasing'),
                usage_period=stored_data.get('usage_period', 'monthly'),
                threshold_exceeded=stored_data.get('threshold_exceeded', 100.0),
                metric_type=metric_type,
                additional_context=stored_data.get('additional_context', {"source": "usage_endpoint"})
            )
        else:
            # Return default data if no usage data found
            print(f"Warning: No usage data found for account {account_id}, using default data")
            return UsageData(
                account_id=account_id,
                current_usage=150.0,
                usage_trend="increasing",
                usage_period="monthly",
                threshold_exceeded=100.0,
                metric_type=metric_type,
                additional_context={"source": "default_data"}
            )
    except Exception as e:
        print(f"Error fetching usage data for account {account_id}: {e}")
        # Return fallback data
        return UsageData(
            account_id=account_id,
            current_usage=150.0,
            usage_trend="increasing",
            usage_period="monthly",
            threshold_exceeded=100.0,
            metric_type=metric_type,
            additional_context={"source": "error_fallback"}
        )


async def start_usage_endpoint():
    """Start the usage data endpoint server"""
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    import uvicorn
    import asyncio
    from typing import Dict, Any
    
    app = FastAPI(title="Usage Data Endpoint", version="1.0.0")
    
    class UsageDataRequest(BaseModel):
        account_id: str
        current_usage: float
        usage_trend: str
        usage_period: str
        threshold_exceeded: float
        metric_type: str
        additional_context: Dict[str, Any] = {}
    
    class UsageDataResponse(BaseModel):
        success: bool
        message: str
        account_id: str
    
    @app.post("/usage/data", response_model=UsageDataResponse)
    async def post_usage_data(request: UsageDataRequest):
        """Endpoint to receive usage data from webhook"""
        try:
            # Store the usage data
            usage_data_store[request.account_id] = {
                'current_usage': request.current_usage,
                'usage_trend': request.usage_trend,
                'usage_period': request.usage_period,
                'threshold_exceeded': request.threshold_exceeded,
                'metric_type': request.metric_type,
                'additional_context': request.additional_context
            }
            
            print(f"✅ Received usage data for account {request.account_id}: {request.current_usage} {request.metric_type}")
            
            return UsageDataResponse(
                success=True,
                message=f"Usage data stored for account {request.account_id}",
                account_id=request.account_id
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to store usage data: {str(e)}")
    
    @app.get("/usage/data/{account_id}")
    async def get_usage_data(account_id: str):
        """Get stored usage data for an account"""
        if account_id in usage_data_store:
            return {
                "success": True,
                "data": usage_data_store[account_id]
            }
        else:
            raise HTTPException(status_code=404, detail=f"No usage data found for account {account_id}")
    
    @app.get("/usage/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "stored_accounts": len(usage_data_store)}
    
    # Start the server in a separate thread
    config = uvicorn.Config(app, host="0.0.0.0", port=8001, log_level="info")
    server = uvicorn.Server(config)
    
    # Run the server in background
    import threading
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()
    
    print("🚀 Usage data endpoint started on http://0.0.0.0:8001")
    print("📊 POST usage data to: http://localhost:8001/usage/data")
    print("🔍 GET usage data from: http://localhost:8001/usage/data/{account_id}")
    print("❤️ Health check at: http://localhost:8001/usage/health")


# Start the usage endpoint when the module is imported
import asyncio
try:
    asyncio.create_task(start_usage_endpoint())
except Exception as e:
    print(f"Warning: Could not start usage endpoint: {e}")


@activity.defn
async def fetch_contract(account_id: str) -> ContractData:
    """Fetch current contract information for the account from MongoDB"""
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'integrations'))
        
        from mongo_db import get_mongo_manager, initialize_mongodb
        
        # Initialize MongoDB if not already done
        if not await get_mongo_manager():
            connection_string = "mongodb+srv://pbanavara:XTOpPHXOfTmGCsgS@cluster0.bljn2lo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
            success = await initialize_mongodb(connection_string)
            if not success:
                raise Exception("Failed to connect to MongoDB")
        
        mongo_manager = await get_mongo_manager()
        if not mongo_manager:
            raise Exception("MongoDB manager not available")
        
        # Fetch contract from MongoDB
        contract = await mongo_manager.get_contract_by_account_id(account_id)
        
        if contract:
            # Convert MongoDB contract to ContractData
            return ContractData(
                account_id=contract.get('account_id', account_id),
                current_plan=contract.get('contract_type', 'Basic'),
                contract_end_date=contract.get('end_date', datetime.utcnow() + timedelta(days=365)).isoformat(),
                renewal_date=contract.get('renewal_date', datetime.utcnow() + timedelta(days=335)).isoformat(),
                current_spend=contract.get('base_monthly_fee', 0.0),
                contract_terms={
                    "term_length": "12 months",
                    "auto_renewal": contract.get('auto_renewal', True),
                    "features": contract.get('features', []),
                    "usage_limits": contract.get('usage_limits', {})
                },
                contact_info={
                    "primary": contract.get('primary_contact', {}).get('email', 'contact@company.com'),
                    "secondary": contract.get('billing_contact', {}).get('email', 'billing@company.com')
                }
            )
        else:
            # Return default contract data if no contract found
            return ContractData(
                account_id=account_id,
                current_plan="Basic",
                contract_end_date="2024-12-31",
                renewal_date="2024-11-30",
                current_spend=99.0,
                contract_terms={"term_length": "12 months", "auto_renewal": True},
                contact_info={"primary": "contact@company.com", "secondary": "billing@company.com"}
            )
            
    except Exception as e:
        # Log the error and return default data
        print(f"Warning: Failed to fetch contract from MongoDB: {e}")
        print("Using default contract data")
        
        return ContractData(
            account_id=account_id,
            current_plan="Basic",
            contract_end_date="2024-12-31",
            renewal_date="2024-11-30",
            current_spend=99.0,
            contract_terms={"term_length": "12 months", "auto_renewal": True},
            contact_info={"primary": "contact@company.com", "secondary": "billing@company.com"}
        )


@activity.defn
async def ask_claude_for_plan(
    usage_data: UsageData, 
    contract_data: ContractData,
    automation_level: AutomationLevel
) -> UpsellPlan:
    """Use Claude to analyze usage and contract data to recommend an upsell plan"""
    # TODO: Implement Claude integration
    # This would typically call Claude API with structured prompt
    return UpsellPlan(
        recommended_plan="Professional",
        estimated_value=15000.0,
        justification="Account shows 50% usage increase with high-value transactions",
        features=["Advanced Analytics", "Priority Support", "Custom Integrations"],
        roi_analysis="Expected 3x ROI based on usage patterns",
        risk_assessment="Low risk - account shows strong engagement"
    )


@activity.defn
async def send_email_draft(
    email_draft: EmailDraft,
    automation_level: AutomationLevel
) -> bool:
    """Send email draft using NLX/SES"""
    # TODO: Implement email sending
    # This would typically use AWS SES or similar service
    print(f"📧 Sending email to {email_draft.recipient}")
    print(f"Subject: {email_draft.subject}")
    print(f"Body: {email_draft.body[:100]}...")
    return True


@activity.defn
async def post_slack_summary(
    slack_summary: SlackSummary,
    automation_level: AutomationLevel
) -> str:
    """Post summary to Slack channel"""
    # TODO: Implement Slack integration
    # This would typically use Slack Web API
    print(f"💬 Posting to Slack channel: {slack_summary.channel}")
    print(f"Message: {slack_summary.message}")
    return "slack_message_ts_123"


@activity.defn
async def create_zoom_meeting(
    zoom_meeting: ZoomMeeting,
    automation_level: AutomationLevel
) -> ZoomMeeting:
    """Create Zoom meeting for follow-up"""
    # TODO: Implement Zoom API integration
    # This would typically use Zoom API
    print(f"📹 Creating Zoom meeting: {zoom_meeting.topic}")
    print(f"Start time: {zoom_meeting.start_time}")
    print(f"Attendees: {zoom_meeting.attendees}")
    
    # Mock meeting creation
    zoom_meeting.meeting_url = "https://zoom.us/j/123456789"
    zoom_meeting.meeting_id = "123456789"
    return zoom_meeting


@activity.defn
async def log_opportunity(opportunity: OpportunityLog) -> str:
    """Log opportunity to database (Mongo/ClickHouse)"""
    # TODO: Implement database logging
    # This would typically write to MongoDB or ClickHouse
    print(f"📊 Logging opportunity for account {opportunity.account_id}")
    print(f"Type: {opportunity.opportunity_type}")
    print(f"Value: ${opportunity.estimated_value}")
    print(f"Status: {opportunity.status}")
    return f"opp_{opportunity.account_id}_{opportunity.event_id}"


# Workflow Definition
@workflow.defn
class UpsellWorkflow:
    """Upsell workflow triggered by usage alerts"""
    
    @workflow.run
    async def run(
        self, 
        account_id: str, 
        event_id: str,
        automation_level: AutomationLevel = AutomationLevel.HYBRID,
        metric_type: str = "trade_volume"
    ) -> Dict[str, Any]:
        """
        Main upsell workflow
        
        Args:
            account_id: The account ID that triggered the alert
            event_id: The event ID from the usage alert
            automation_level: Level of automation (full, human, hybrid)
            metric_type: Type of metric that triggered the alert
        """
        
        workflow.logger.info(f"Starting upsell workflow for account {account_id}, event {event_id}")
        
        # Step 1: Fetch usage data
        workflow.logger.info("Fetching usage data...")
        usage_data = await execute_activity(
            fetch_usage,
            account_id,
            metric_type,
            start_to_close_timeout=timedelta(minutes=5)
        )
        
        # Step 2: Fetch contract data
        workflow.logger.info("Fetching contract data...")
        contract_data = await execute_activity(
            fetch_contract,
            account_id,
            start_to_close_timeout=timedelta(minutes=5)
        )
        
        # Step 3: Get AI recommendation
        workflow.logger.info("Getting AI recommendation...")
        upsell_plan = await execute_activity(
            ask_claude_for_plan,
            usage_data,
            contract_data,
            automation_level,
            start_to_close_timeout=timedelta(minutes=10)
        )
        
        # Step 4: Create email draft
        workflow.logger.info("Creating email draft...")
        email_draft = self._create_email_draft(usage_data, contract_data, upsell_plan)
        
        # Step 5: Send email (if automation allows)
        if automation_level in [AutomationLevel.FULL_AUTOMATION, AutomationLevel.HYBRID]:
            workflow.logger.info("Sending email draft...")
            email_sent = await execute_activity(
                send_email_draft,
                email_draft,
                automation_level,
                start_to_close_timeout=timedelta(minutes=5)
            )
        else:
            workflow.logger.info("Email sending skipped - requires human intervention")
            email_sent = False
        
        # Step 6: Post Slack summary
        workflow.logger.info("Posting Slack summary...")
        slack_summary = self._create_slack_summary(usage_data, contract_data, upsell_plan, email_sent)
        slack_ts = await execute_activity(
            post_slack_summary,
            slack_summary,
            automation_level,
            start_to_close_timeout=timedelta(minutes=5)
        )
        
        # Step 7: Wait for reply (if human intervention required)
        reply_status = ReplyStatus.PENDING
        if automation_level in [AutomationLevel.HUMAN_INTERVENTION, AutomationLevel.HYBRID]:
            workflow.logger.info("Waiting for human reply...")
            reply_status = await self._wait_for_reply(account_id, event_id)
        
        # Step 8: Create Zoom meeting (if reply is yes)
        zoom_meeting = None
        if reply_status == ReplyStatus.YES:
            workflow.logger.info("Creating Zoom meeting...")
            zoom_meeting_data = self._create_zoom_meeting(account_id, contract_data, upsell_plan)
            zoom_meeting = await execute_activity(
                create_zoom_meeting,
                zoom_meeting_data,
                automation_level,
                start_to_close_timeout=timedelta(minutes=5)
            )
        
        # Step 9: Log opportunity
        workflow.logger.info("Logging opportunity...")
        opportunity = self._create_opportunity_log(account_id, event_id, upsell_plan, reply_status, zoom_meeting)
        opportunity_id = await execute_activity(
            log_opportunity,
            opportunity,
            start_to_close_timeout=timedelta(minutes=5)
        )
        
        # Return workflow results
        return {
            "account_id": account_id,
            "event_id": event_id,
            "automation_level": automation_level,
            "usage_data": usage_data,
            "contract_data": contract_data,
            "upsell_plan": upsell_plan,
            "email_sent": email_sent,
            "slack_ts": slack_ts,
            "reply_status": reply_status,
            "zoom_meeting": zoom_meeting,
            "opportunity_id": opportunity_id,
            "workflow_status": "completed"
        }
    
    def _create_email_draft(
        self, 
        usage_data: UsageData, 
        contract_data: ContractData, 
        upsell_plan: UpsellPlan
    ) -> EmailDraft:
        """Create email draft based on usage and plan data"""
        subject = f"Growth Opportunity: Upgrade to {upsell_plan.recommended_plan} Plan"
        body = f"""
Dear {contract_data.contact_info.get('primary', 'Valued Customer')},

We've noticed that your account {usage_data.account_id} has been experiencing significant growth in {usage_data.metric_type} usage.

Current Usage: {usage_data.current_usage}
Usage Trend: {usage_data.usage_trend}
Current Plan: {contract_data.current_plan}

Based on your usage patterns, we recommend upgrading to our {upsell_plan.recommended_plan} plan, which includes:

{chr(10).join([f"• {feature}" for feature in upsell_plan.features])}

Estimated Value: ${upsell_plan.estimated_value:,.2f}
ROI Analysis: {upsell_plan.roi_analysis}

Would you be interested in discussing this opportunity further?

Best regards,
Your Account Team
        """.strip()
        
        return EmailDraft(
            subject=subject,
            body=body,
            recipient=contract_data.contact_info.get('primary', ''),
            cc_list=[contract_data.contact_info.get('secondary', '')],
            attachments=[]
        )
    
    def _create_slack_summary(
        self, 
        usage_data: UsageData, 
        contract_data: ContractData, 
        upsell_plan: UpsellPlan,
        email_sent: bool
    ) -> SlackSummary:
        """Create Slack summary message"""
        message = f"""
🚀 *Upsell Opportunity Detected*

*Account:* {usage_data.account_id}
*Current Plan:* {contract_data.current_plan}
*Usage Trend:* {usage_data.usage_trend} ({usage_data.current_usage})
*Recommended Plan:* {upsell_plan.recommended_plan}
*Estimated Value:* ${upsell_plan.estimated_value:,.2f}
*Email Sent:* {'✅' if email_sent else '❌'}

*Next Steps:* {'Awaiting reply' if not email_sent else 'Monitor for response'}
        """.strip()
        
        return SlackSummary(
            channel="#sales-opportunities",
            message=message,
            attachments=[
                {
                    "title": "Usage Analysis",
                    "text": f"Current: {usage_data.current_usage}, Threshold: {usage_data.threshold_exceeded}"
                },
                {
                    "title": "ROI Analysis", 
                    "text": upsell_plan.roi_analysis
                }
            ]
        )
    
    def _create_zoom_meeting(
        self, 
        account_id: str, 
        contract_data: ContractData, 
        upsell_plan: UpsellPlan
    ) -> ZoomMeeting:
        """Create Zoom meeting details"""
        return ZoomMeeting(
            topic=f"Upsell Discussion - {account_id} - {upsell_plan.recommended_plan} Plan",
            start_time="2024-01-15T14:00:00Z",  # TODO: Calculate optimal time
            duration_minutes=30,
            attendees=[
                contract_data.contact_info.get('primary', ''),
                contract_data.contact_info.get('secondary', ''),
                'sales@company.com'
            ]
        )
    
    def _create_opportunity_log(
        self, 
        account_id: str, 
        event_id: str, 
        upsell_plan: UpsellPlan,
        reply_status: ReplyStatus,
        zoom_meeting: Optional[ZoomMeeting]
    ) -> OpportunityLog:
        """Create opportunity log entry"""
        from datetime import datetime
        
        now = datetime.utcnow().isoformat()
        
        return OpportunityLog(
            account_id=account_id,
            event_id=event_id,
            opportunity_type="usage_based_upsell",
            estimated_value=upsell_plan.estimated_value,
            status=reply_status.value,
            created_at=now,
            updated_at=now,
            notes=f"Triggered by {upsell_plan.recommended_plan} recommendation. Zoom meeting: {'Scheduled' if zoom_meeting else 'Not scheduled'}"
        )
    
    @workflow.signal
    async def customer_reply(self, reply: str) -> None:
        """Signal to receive customer reply"""
        workflow.logger.info(f"Received customer reply: {reply}")
        self._customer_reply = reply
    
    async def _wait_for_reply(self, account_id: str, event_id: str) -> ReplyStatus:
        """Wait for human reply via signal"""
        # Wait for signal with timeout
        try:
            await workflow.wait_condition(
                lambda: hasattr(self, '_customer_reply'),
                timeout=timedelta(hours=24)  # 24 hour timeout
            )
            reply = self._customer_reply.lower()
            if reply in ['yes', 'y', 'interested', 'schedule']:
                return ReplyStatus.YES
            elif reply in ['no', 'n', 'not interested']:
                return ReplyStatus.NO
            else:
                return ReplyStatus.MAYBE
        except TimeoutError:
            workflow.logger.warning("Timeout waiting for customer reply")
            return ReplyStatus.PENDING


# Agent trigger functions
async def trigger_upsell_workflow(
    client,
    account_id: str,
    event_id: str,
    automation_level: AutomationLevel = AutomationLevel.HYBRID,
    metric_type: str = "trade_volume"
) -> str:
    """Trigger upsell workflow from agent"""
    workflow_id = f"upsell-{account_id}-{event_id}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    
    handle = await client.start_workflow(
        UpsellWorkflow.run,
        account_id,
        event_id,
        automation_level,
        metric_type,
        id=workflow_id,
        task_queue="upsell-task-queue",
    )
    
    return workflow_id


async def send_customer_reply(
    client,
    workflow_id: str,
    reply: str
) -> None:
    """Send customer reply signal to workflow"""
    handle = client.get_workflow_handle(workflow_id)
    await handle.signal(UpsellWorkflow.customer_reply, reply) 