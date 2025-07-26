#!/usr/bin/env python3
"""
Consolidated Workflows File
Contains all Temporal workflows for the AWS Agents Hackathon project:
- UpsellWorkflow: Customer upsell automation workflow
- AlertProcessingWorkflow: Alert processing workflow
- BatchAlertProcessingWorkflow: Batch alert processing
- SampleWorkflow: Basic sample workflow
"""

import asyncio
import logging
import uuid
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from temporalio import workflow, activity
from temporalio.common import RetryPolicy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================

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
    email_subject: Optional[str] = None
    email_body: Optional[str] = None


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


# ============================================================================
# GLOBAL STORAGE FOR USAGE DATA
# ============================================================================

# Global storage for usage data (in-memory for demo purposes)
usage_data_store = {}


# ============================================================================
# UPSELL WORKFLOW ACTIVITIES
# ============================================================================

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


@activity.defn
async def fetch_contract(account_id: str) -> ContractData:
    """Fetch current contract information for the account from MongoDB"""
    
    # Check if MongoDB integration is enabled
    from config_checker import is_mongodb_enabled
    
    if not is_mongodb_enabled():
        logger.info(f"🗄️ MongoDB integration is disabled - using default contract data for {account_id}")
        # Return default contract data if MongoDB is disabled
        return ContractData(
            account_id=account_id,
            current_plan="Basic",
            contract_end_date="2024-12-31",
            renewal_date="2024-11-30",
            current_spend=99.0,
            contract_terms={"term_length": "12 months", "auto_renewal": True},
            contact_info={"primary": "contact@company.com", "secondary": "billing@company.com"}
        )
    
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
    
    # Check if Claude integration is enabled
    from config_checker import is_claude_enabled
    
    if not is_claude_enabled():
        logger.info("🤖 Claude integration is disabled - using fallback logic")
        return _fallback_upsell_plan(usage_data, contract_data)
    
    # Import AWS libraries inside activity to avoid sandbox restrictions
    import boto3
    from botocore.config import Config
    import anthropic
    
    # Transform data to webhook format
    webhook_data = _transform_to_webhook_format(usage_data, contract_data)
    
    # Create Claude prompt
    prompt = _create_claude_prompt(webhook_data)
    
    # Try Bedrock first, then Anthropic API, then fallback
    try:
        # Try AWS Bedrock
        bearer_token = os.getenv('AWS_BEARER_TOKEN_BEDROCK')
        if bearer_token:
            logger.info("🔄 Trying AWS Bedrock...")
            session = boto3.Session()
            bedrock_client = session.client(
                'bedrock-runtime',
                region_name='us-east-1',
                config=Config(
                    region_name='us-east-1',
                    retries={'max_attempts': 3}
                )
            )
            
            response = await _call_claude_bedrock(bedrock_client, prompt)
            claude_result = _parse_claude_response(response)
            upsell_plan = _convert_to_upsell_plan(claude_result, usage_data, contract_data)
            
            logger.info(f"🤖 Claude (Bedrock) generated upsell plan: {upsell_plan.recommended_plan}")
            return upsell_plan
            
    except Exception as e:
        logger.warning(f"❌ Bedrock failed: {e}")
        
        try:
            # Try Anthropic API as fallback
            anthropic_key = os.getenv('ANTHROPIC_API_KEY')
            if anthropic_key:
                logger.info("🔄 Trying Anthropic API...")
                response = await _call_claude_anthropic(anthropic_key, prompt)
                claude_result = _parse_claude_response(response)
                upsell_plan = _convert_to_upsell_plan(claude_result, usage_data, contract_data)
                
                logger.info(f"🤖 Claude (Anthropic API) generated upsell plan: {upsell_plan.recommended_plan}")
                return upsell_plan
                
        except Exception as e2:
            logger.error(f"❌ Anthropic API failed: {e2}")
    
    # Final fallback to rule-based logic
    logger.info("🔄 Using rule-based fallback logic")
    return _fallback_upsell_plan(usage_data, contract_data)


def _transform_to_webhook_format(usage_data: UsageData, contract_data: ContractData) -> Dict[str, Any]:
    """Transform usage and contract data to webhook format expected by Claude"""
    
    # Map metric types to enum values
    metric_type_mapping = {
        "trade_volume": "TRADE_VOLUME",
        "trade_count": "TRADE_COUNT", 
        "trade_value": "TRADE_VALUE",
        "latency": "LATENCY",
        "sla_violation": "SLA_VIOLATION",
        "balance_change": "BALANCE_CHANGE",
        "trading_pattern": "TRADING_PATTERN",
        "account_activity": "ACCOUNT_ACTIVITY"
    }
    
    # Create alert data
    alert = {
        "alert_id": f"alert-{usage_data.account_id}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
        "metric_type": metric_type_mapping.get(usage_data.metric_type, "TRADE_VOLUME"),
        "threshold_condition": {
            "operator": ">",
            "value": usage_data.threshold_exceeded,
            "unit": "trades" if "trade" in usage_data.metric_type else "ms"
        },
        "metric_data": {
            "metric_name": usage_data.metric_type,
            "current_value": usage_data.current_usage,
            "threshold_value": usage_data.threshold_exceeded,
            "account_id": usage_data.account_id,
            "timestamp": datetime.utcnow().isoformat(),
            "usage_trend": usage_data.usage_trend,
            "usage_period": usage_data.usage_period
        },
        "severity": "HIGH" if usage_data.current_usage > usage_data.threshold_exceeded * 1.5 else "MEDIUM",
        "status": "ACTIVE",
        "title": f"High {usage_data.metric_type.replace('_', ' ').title()} Alert",
        "description": f"Account {usage_data.account_id} has exceeded {usage_data.metric_type} threshold",
        "tags": ["revenue-opportunity", "upsell-candidate"],
        "context": usage_data.additional_context
    }
    
    # Create contract context
    contract_context = {
        "current_plan": contract_data.current_plan,
        "contract_end_date": contract_data.contract_end_date,
        "renewal_date": contract_data.renewal_date,
        "current_spend": contract_data.current_spend,
        "contract_terms": contract_data.contract_terms,
        "contact_info": contract_data.contact_info
    }
    
    return {
        "alerts": [alert],
        "contract_context": contract_context
    }


def _create_claude_prompt(webhook_data: Dict[str, Any]) -> str:
    """Create the prompt for Claude"""
    
    prompt = """You are a revenue-focused Customer Success / Ops agent for the EasyTrade platform.

INPUT: A WebhookRequest JSON containing one or more UsageMetricsAlert objects (see schema below). Each alert includes:
- metric_type (Enum): TRADE_VOLUME, TRADE_COUNT, TRADE_VALUE, LATENCY, SLA_VIOLATION, BALANCE_CHANGE, TRADING_PATTERN, ACCOUNT_ACTIVITY
- threshold_condition (operator/value/unit)
- metric_data (metric_name/current_value/threshold_value/account_id/timestamp/...)
- severity, status, title, description, tags, context, etc.

TASK:
For each alert that presents a monetizable opportunity (e.g., usage/volume/value over threshold, abnormal activity suggesting premium monitoring, SLA upgrade, etc.), produce ONE recommendation to drive revenue (upsell/cross-sell/contract true-up). If the alert is operational only (e.g., latency breach) and no credible revenue action exists, mark it as non-revenue.

RULES:
- Output STRICT JSON only. No prose, no markdown.
- Follow the OUTPUT SCHEMA exactly. No extra keys.
- Never invent prices or limits—use given pricing/contract data. If absent, set requires_manual_review=true.
- If multiple alerts arrive, output an array of results—one object per alert.
- Keep email copy 120–220 words, consultative tone, include {{first_name}} and {{cs_owner_name}} placeholders.
- If no revenue move: set "no_revenue_action": true and explain briefly in "reason".

OUTPUT SCHEMA:

{
  "batch_id": "string|null",
  "results": [
    {
      "alert_id": "string",
      "metric_type": "string",
      "playbook_id": "string",                  // choose from provided list or "default"
      "no_revenue_action": false,               // true if nothing to sell
      "tier_recommendation": "string|null",     // e.g. "Pro-250k", null if none
      "expected_arr_delta": 0,                  // number (annual USD), 0 if none
      "billing_change_description": "string|null",
      "reason": "string",                       // why this recommendation
      "risk_if_ignored": "string|null",
      "email_subject": "string|null",
      "email_body": "string|null",
      "next_steps": ["send_email","wait_reply","create_zoom_if_positive"],  // ordered array
      "confidence": 0.0,                        // 0–1
      "requires_manual_review": false
    }
  ]
}

WEBHOOK DATA:
"""
    
    prompt += json.dumps(webhook_data, indent=2)
    prompt += "\n\nOUTPUT:"
    
    return prompt


async def _call_claude_bedrock(bedrock_client, prompt: str) -> str:
    """Call Claude via AWS Bedrock"""
    
    model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4000,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    # For AWS Bedrock, the bearer token should be used as AWS credentials
    # The boto3 client will handle authentication automatically
    response = bedrock_client.invoke_model(
        modelId=model_id,
        body=json.dumps(request_body)
    )
    
    response_body = json.loads(response['body'].read())
    return response_body['content'][0]['text']


async def _call_claude_anthropic(api_key: str, prompt: str) -> str:
    """Call Claude via Anthropic API"""
    
    client = anthropic.Anthropic(api_key=api_key)
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    
    return response.content[0].text


def _parse_claude_response(response: str) -> Dict[str, Any]:
    """Parse Claude's JSON response"""
    try:
        # Extract JSON from response (in case there's extra text)
        start_idx = response.find('{')
        end_idx = response.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON found in response")
        
        json_str = response[start_idx:end_idx]
        return json.loads(json_str)
        
    except Exception as e:
        logger.error(f"Failed to parse Claude response: {e}")
        logger.error(f"Response: {response}")
        raise


def _convert_to_upsell_plan(claude_result: Dict[str, Any], usage_data: UsageData, contract_data: ContractData) -> UpsellPlan:
    """Convert Claude's response to UpsellPlan"""
    
    if not claude_result.get('results') or len(claude_result['results']) == 0:
        return _fallback_upsell_plan(usage_data, contract_data)
    
    result = claude_result['results'][0]  # Take first result
    
    # Check if no revenue action
    if result.get('no_revenue_action', False):
        return UpsellPlan(
            recommended_plan="No Action Required",
            estimated_value=0.0,
            justification=result.get('reason', 'No revenue opportunity identified'),
            features=[],
            roi_analysis="No revenue impact",
            risk_assessment="No risk identified"
        )
    
    # Extract data from Claude response
    recommended_plan = result.get('tier_recommendation', 'Professional')
    estimated_value = result.get('expected_arr_delta', 0.0)
    justification = result.get('reason', 'Usage-based recommendation')
    billing_change = result.get('billing_change_description', '')
    risk_if_ignored = result.get('risk_if_ignored', '')
    email_subject = result.get('email_subject', '')
    email_body = result.get('email_body', '')
    
    # Determine features based on plan
    features = _get_features_for_plan(recommended_plan)
    
    return UpsellPlan(
        recommended_plan=recommended_plan,
        estimated_value=estimated_value,
        justification=justification,
        features=features,
        roi_analysis=billing_change if billing_change else f"Expected ${estimated_value:,.0f} annual revenue increase",
        risk_assessment=risk_if_ignored if risk_if_ignored else "Low risk, high potential value",
        email_subject=email_subject,
        email_body=email_body
    )


def _get_features_for_plan(plan: str) -> List[str]:
    """Get features for a given plan"""
    plan_features = {
        "Basic": ["Basic Analytics", "Email Support"],
        "Professional": ["Advanced Analytics", "Priority Support", "Custom Integrations"],
        "Enterprise": ["Advanced Analytics", "Priority Support", "Custom Integrations", "Dedicated Account Manager", "SLA Guarantee"],
        "Pro-250k": ["High Volume Trading", "Advanced Analytics", "Priority Support"],
        "Pro-500k": ["High Volume Trading", "Advanced Analytics", "Priority Support", "Custom Integrations"],
        "Enterprise-1M": ["Enterprise Features", "Dedicated Support", "Custom Solutions"]
    }
    
    return plan_features.get(plan, ["Advanced Analytics", "Priority Support", "Custom Integrations"])


def _fallback_upsell_plan(usage_data: UsageData, contract_data: ContractData) -> UpsellPlan:
    """Fallback logic when Claude is not available"""
    current_usage = usage_data.current_usage
    current_plan = contract_data.current_plan
    
    # Simple logic for demo purposes
    if current_plan == "Basic" and current_usage > 1000:
        recommended_plan = "Professional"
        estimated_value = 5000.0
        justification = "High usage detected, upgrade to Professional plan for better performance"
    elif current_plan == "Professional" and current_usage > 5000:
        recommended_plan = "Enterprise"
        estimated_value = 15000.0
        justification = "Enterprise-level usage detected, upgrade for dedicated support and advanced features"
    else:
        recommended_plan = "Professional"
        estimated_value = 3000.0
        justification = "Usage growth detected, upgrade for additional features and support"
    
    return UpsellPlan(
        recommended_plan=recommended_plan,
        estimated_value=estimated_value,
        justification=justification,
        features=["Advanced Analytics", "Priority Support", "Custom Integrations"],
        roi_analysis="Expected 3x ROI within 6 months",
        risk_assessment="Low risk, high potential value"
    )


@activity.defn
async def send_email_draft(
    email_draft: EmailDraft,
    automation_level: AutomationLevel
) -> bool:
    """Send email draft to customer via Amazon SES"""
    
    # Check if email sending is enabled
    from config_checker import is_email_enabled
    
    if not is_email_enabled():
        logger.info(f"📧 Email sending is disabled - skipping email to {email_draft.recipient}")
        logger.info(f"   Subject: {email_draft.subject}")
        return True  # Return success to avoid workflow failure
    
    # Import boto3 inside activity to avoid sandbox restrictions
    import boto3
    
    try:
        # Create SES client
        session = boto3.Session()
        ses_client = session.client('ses', region_name='us-east-1')
        
        # Send email via SES
        response = ses_client.send_email(
            Source='pradeepbs@gmail.com',  # From address for SES emails
            Destination={
                'ToAddresses': [email_draft.recipient]
            },
            Message={
                'Subject': {
                    'Data': email_draft.subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': email_draft.body,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        
        logger.info(f"📧 Email sent via SES to {email_draft.recipient}")
        logger.info(f"   Subject: {email_draft.subject}")
        logger.info(f"   Message ID: {response['MessageId']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send email via SES: {e}")
        return False


@activity.defn
async def post_slack_summary(
    slack_summary: SlackSummary,
    automation_level: AutomationLevel
) -> str:
    """Post summary to Slack (mock implementation)"""
    
    # Check if Slack posting is enabled
    from config_checker import is_slack_enabled
    
    if not is_slack_enabled():
        logger.info(f"💬 Slack posting is disabled - skipping message to {slack_summary.channel}")
        return f"slack_msg_disabled_{uuid.uuid4().hex[:8]}"
    
    # TODO: Implement actual Slack posting
    print(f"💬 Slack message posted to {slack_summary.channel}")
    print(f"   Message: {slack_summary.message[:100]}...")
    print(f"   Automation Level: {automation_level}")
    
    # Simulate Slack posting
    await asyncio.sleep(0.5)
    
    return f"slack_msg_{uuid.uuid4().hex[:8]}"


@activity.defn
async def create_zoom_meeting(
    zoom_meeting: ZoomMeeting,
    automation_level: AutomationLevel
) -> ZoomMeeting:
    """Create Zoom meeting (mock implementation)"""
    
    # Check if Zoom meeting creation is enabled
    from config_checker import is_zoom_enabled
    
    if not is_zoom_enabled():
        logger.info(f"📹 Zoom meeting creation is disabled - skipping meeting: {zoom_meeting.topic}")
        return ZoomMeeting(
            topic=f"[DISABLED] {zoom_meeting.topic}",
            start_time=zoom_meeting.start_time,
            duration_minutes=zoom_meeting.duration_minutes,
            attendees=zoom_meeting.attendees,
            meeting_url="https://zoom.us/j/disabled",
            meeting_id="disabled"
        )
    
    # TODO: Implement actual Zoom API integration
    print(f"📹 Zoom meeting created: {zoom_meeting.topic}")
    print(f"   Attendees: {', '.join(zoom_meeting.attendees)}")
    print(f"   Automation Level: {automation_level}")
    
    # Simulate meeting creation
    await asyncio.sleep(1)
    
    # Return meeting with generated URL and ID
    return ZoomMeeting(
        topic=zoom_meeting.topic,
        start_time=zoom_meeting.start_time,
        duration_minutes=zoom_meeting.duration_minutes,
        attendees=zoom_meeting.attendees,
        meeting_url=f"https://zoom.us/j/{uuid.uuid4().hex[:10]}",
        meeting_id=uuid.uuid4().hex[:10]
    )


@activity.defn
async def log_opportunity(opportunity: OpportunityLog) -> str:
    """Log opportunity to CRM or database (mock implementation)"""
    # TODO: Implement actual CRM integration (Salesforce, HubSpot, etc.)
    print(f"📊 Opportunity logged: {opportunity.opportunity_type}")
    print(f"   Account: {opportunity.account_id}")
    print(f"   Value: ${opportunity.estimated_value:,.2f}")
    
    # Simulate logging
    await asyncio.sleep(0.5)
    
    return f"opp_{uuid.uuid4().hex[:8]}"





# ============================================================================
# WORKFLOW DEFINITIONS
# ============================================================================

@workflow.defn
class UpsellWorkflow:
    """Main upsell workflow for customer engagement and contract upgrades"""
    
    @workflow.run
    async def run(
        self, 
        account_id: str, 
        event_id: str,
        automation_level: AutomationLevel = AutomationLevel.HYBRID,
        metric_type: str = "trade_volume"
    ) -> Dict[str, Any]:
        """Main workflow execution"""
        
        # Step 1: Fetch usage data
        usage_data = await workflow.execute_activity(
            fetch_usage,
            args=[account_id, metric_type],
            start_to_close_timeout=timedelta(seconds=30)
        )
        
        # Step 2: Fetch contract data
        contract_data = await workflow.execute_activity(
            fetch_contract,
            args=[account_id],
            start_to_close_timeout=timedelta(seconds=30)
        )
        
        # Step 3: Get AI recommendation
        upsell_plan = await workflow.execute_activity(
            ask_claude_for_plan,
            args=[usage_data, contract_data, automation_level],
            start_to_close_timeout=timedelta(seconds=60)
        )
        
        # Step 4: Send email draft
        email_draft = self._create_email_draft(usage_data, contract_data, upsell_plan)
        email_sent = await workflow.execute_activity(
            send_email_draft,
            args=[email_draft, automation_level],
            start_to_close_timeout=timedelta(seconds=30)
        )
        
        # Step 5: Post Slack summary
        slack_summary = self._create_slack_summary(usage_data, contract_data, upsell_plan, email_sent)
        slack_msg_id = await workflow.execute_activity(
            post_slack_summary,
            args=[slack_summary, automation_level],
            start_to_close_timeout=timedelta(seconds=30)
        )
        
        # Step 6: Wait for customer reply (if hybrid or human intervention)
        reply_status = ReplyStatus.PENDING
        if automation_level != AutomationLevel.FULL_AUTOMATION:
            reply_status = await self._wait_for_reply(account_id, event_id)
        
        # Step 7: Create Zoom meeting if customer replied yes
        zoom_meeting = None
        if reply_status == ReplyStatus.YES:
            zoom_meeting = self._create_zoom_meeting(account_id, contract_data, upsell_plan)
            zoom_meeting = await workflow.execute_activity(
                create_zoom_meeting,
                args=[zoom_meeting, automation_level],
                start_to_close_timeout=timedelta(seconds=60)
            )
        
        # Step 8: Log opportunity
        opportunity = self._create_opportunity_log(account_id, event_id, upsell_plan, reply_status, zoom_meeting)
        opportunity_id = await workflow.execute_activity(
            log_opportunity,
            args=[opportunity],
            start_to_close_timeout=timedelta(seconds=30)
        )
        
        return {
            'account_id': account_id,
            'event_id': event_id,
            'automation_level': automation_level,
            'usage_data': usage_data,
            'contract_data': contract_data,
            'upsell_plan': upsell_plan,
            'email_sent': email_sent,
            'slack_msg_id': slack_msg_id,
            'reply_status': reply_status,
            'zoom_meeting': zoom_meeting,
            'opportunity_id': opportunity_id,
            'completed_at': workflow.now().isoformat()
        }
    
    def _create_email_draft(
        self, 
        usage_data: UsageData, 
        contract_data: ContractData, 
        upsell_plan: UpsellPlan
    ) -> EmailDraft:
        """Create email draft for customer using Claude's response"""
        
        # Use Claude's email data if available, otherwise use fallback
        subject = upsell_plan.email_subject or f"Growth Opportunity: Upgrade to {upsell_plan.recommended_plan} Plan"
        body = upsell_plan.email_body or f"""
Dear Valued Customer,

We've noticed your usage has increased significantly ({usage_data.current_usage} {usage_data.metric_type}).
Based on your current {contract_data.current_plan} plan, we recommend upgrading to our {upsell_plan.recommended_plan} plan.

Benefits:
- {upsell_plan.justification}
- Estimated value: ${upsell_plan.estimated_value:,.2f}
- Features: {', '.join(upsell_plan.features)}

Would you like to schedule a call to discuss this opportunity?

Best regards,
Your Account Team
        """.strip()
        
        # Get email from contract data
        recipient_email = contract_data.contact_info.get('email', contract_data.contact_info.get('primary', 'customer@example.com'))
        
        return EmailDraft(
            subject=subject,
            body=body,
            recipient=recipient_email,
            cc_list=[],
            attachments=[],
            send_date=workflow.now().isoformat()
        )
    
    def _create_slack_summary(
        self, 
        usage_data: UsageData, 
        contract_data: ContractData, 
        upsell_plan: UpsellPlan,
        email_sent: bool
    ) -> SlackSummary:
        """Create Slack summary"""
        return SlackSummary(
            channel="#sales-opportunities",
            message=f"""
🎯 *Upsell Opportunity Detected*
• Account: {usage_data.account_id}
• Current Plan: {contract_data.current_plan}
• Usage: {usage_data.current_usage} {usage_data.metric_type}
• Recommended: {upsell_plan.recommended_plan}
• Value: ${upsell_plan.estimated_value:,.2f}
• Email Sent: {'✅' if email_sent else '❌'}
            """.strip(),
            attachments=[{
                'title': 'Upsell Plan Details',
                'text': upsell_plan.justification,
                'color': 'good'
            }]
        )
    
    def _create_zoom_meeting(
        self, 
        account_id: str, 
        contract_data: ContractData, 
        upsell_plan: UpsellPlan
    ) -> ZoomMeeting:
        """Create Zoom meeting details"""
        return ZoomMeeting(
            topic=f"Upsell Discussion - {account_id}",
            start_time=(workflow.now() + timedelta(days=1)).isoformat(),
            duration_minutes=30,
            attendees=[
                contract_data.contact_info['primary'],
                'sales@company.com',
                'account-manager@company.com'
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
        return OpportunityLog(
            account_id=account_id,
            event_id=event_id,
            opportunity_type="upsell",
            estimated_value=upsell_plan.estimated_value,
            status=reply_status.value,
            created_at=workflow.now().isoformat(),
            updated_at=workflow.now().isoformat(),
            notes=f"Upsell opportunity for {upsell_plan.recommended_plan} plan. Customer reply: {reply_status.value}"
        )
    
    @workflow.signal
    async def customer_reply(self, reply: str) -> None:
        """Signal to receive customer reply"""
        self._customer_reply = reply
    
    async def _wait_for_reply(self, account_id: str, event_id: str) -> ReplyStatus:
        """Wait for customer reply with timeout"""
        try:
            # Wait for customer reply signal with 24-hour timeout
            await workflow.wait_condition(
                lambda: hasattr(self, '_customer_reply'),
                timeout=timedelta(hours=24)
            )
            
            reply = self._customer_reply.lower()
            if reply in ['yes', 'y', 'sure', 'ok']:
                return ReplyStatus.YES
            elif reply in ['no', 'n', 'not interested']:
                return ReplyStatus.NO
            elif reply in ['maybe', 'later', 'call me']:
                return ReplyStatus.MAYBE
            else:
                return ReplyStatus.PENDING
                
        except TimeoutError:
            logger.info(f"Timeout waiting for customer reply for account {account_id}")
            return ReplyStatus.PENDING





@workflow.defn
class SampleWorkflow:
    """Basic sample workflow for testing"""
    
    @workflow.run
    async def run(self, name: str) -> str:
        """Simple workflow that returns a greeting"""
        return f"Hello, {name}!"


# ============================================================================
# USAGE DATA ENDPOINT
# ============================================================================

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


# Note: Usage endpoint is now started manually when needed
# Remove automatic startup to avoid port conflicts


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def trigger_upsell_workflow(
    client,
    account_id: str,
    event_id: str,
    automation_level: AutomationLevel = AutomationLevel.HYBRID,
    metric_type: str = "trade_volume"
) -> str:
    """Helper function to trigger upsell workflow"""
    workflow_id = f"upsell-{account_id}-{event_id}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    
    handle = await client.start_workflow(
        UpsellWorkflow.run,
        args=[account_id, event_id, automation_level, metric_type],
        id=workflow_id,
        task_queue="consolidated-task-queue",
    )
    
    return workflow_id


async def send_customer_reply(
    client,
    workflow_id: str,
    reply: str
) -> None:
    """Helper function to send customer reply to workflow"""
    handle = client.get_workflow_handle(workflow_id)
    await handle.signal(UpsellWorkflow.customer_reply, reply)


# Export all workflows and activities for easy importing
__all__ = [
    # Workflows
    'UpsellWorkflow',
    'SampleWorkflow',
    
    # Activities
    'fetch_usage',
    'fetch_contract',
    'ask_claude_for_plan',
    'send_email_draft',
    'post_slack_summary',
    'create_zoom_meeting',
    'log_opportunity',
    
    # Data classes
    'UsageData',
    'ContractData',
    'UpsellPlan',
    'EmailDraft',
    'SlackSummary',
    'ZoomMeeting',
    'OpportunityLog',
    
    # Enums
    'AutomationLevel',
    'ReplyStatus',
    
    # Helper functions
    'trigger_upsell_workflow',
    'send_customer_reply',
    'start_usage_endpoint'
] 