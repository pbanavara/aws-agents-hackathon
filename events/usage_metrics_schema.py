from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict, Any


class MetricType(str, Enum):
    """Types of usage metrics that can trigger alerts"""
    TRADE_VOLUME = "trade_volume"
    TRADE_COUNT = "trade_count"
    TRADE_VALUE = "trade_value"
    LATENCY = "latency"
    SLA_VIOLATION = "sla_violation"
    BALANCE_CHANGE = "balance_change"
    TRADING_PATTERN = "trading_pattern"
    ACCOUNT_ACTIVITY = "account_activity"


class ThresholdOperator(str, Enum):
    """Operators for threshold comparisons"""
    GREATER_THAN = ">"
    GREATER_THAN_EQUAL = ">="
    LESS_THAN = "<"
    LESS_THAN_EQUAL = "<="
    EQUAL = "=="
    NOT_EQUAL = "!="


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ThresholdCondition(BaseModel):
    """Threshold condition for triggering alerts"""
    operator: ThresholdOperator
    value: float
    unit: Optional[str] = None  # e.g., "trades", "dollars", "seconds"


class MetricData(BaseModel):
    """Actual metric data that triggered the alert"""
    metric_name: str
    current_value: float
    threshold_value: float
    account_id: Optional[str] = None
    trade_type: Optional[str] = None  # "buy", "sell", "long-buy", "quick-sell", etc.
    timestamp: datetime
    additional_context: Optional[Dict[str, Any]] = None


class UsageMetricsAlert(BaseModel):
    """Alert schema for usage-based metrics"""
    alert_id: str = Field(..., description="Unique alert identifier")
    metric_type: MetricType = Field(..., description="Type of metric that triggered the alert")
    severity: AlertSeverity = Field(..., description="Alert severity level")
    status: AlertStatus = Field(default=AlertStatus.ACTIVE, description="Current alert status")
    
    # Threshold information
    threshold_condition: ThresholdCondition = Field(..., description="Threshold condition that was violated")
    
    # Metric data
    metric_data: MetricData = Field(..., description="Actual metric data that triggered the alert")
    
    # Alert metadata
    title: str = Field(..., description="Alert title")
    description: str = Field(..., description="Detailed alert description")
    source: str = Field(default="EasyTrade Platform", description="Source system")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Alert creation timestamp")
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Additional context
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context data")
    
    def model_dump(self, **kwargs):
        """Override model_dump to handle datetime serialization"""
        data = super().model_dump(**kwargs)
        # Convert datetime objects to ISO format strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data


class WebhookRequest(BaseModel):
    """Webhook request payload for usage metrics alerts"""
    alerts: List[UsageMetricsAlert] = Field(..., description="List of usage metrics alerts")
    batch_id: Optional[str] = Field(default=None, description="Batch identifier for multiple alerts")
    source_system: str = Field(default="EasyTrade", description="Source system name")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")


class WebhookResponse(BaseModel):
    """Webhook response"""
    success: bool = Field(..., description="Whether the request was processed successfully")
    message: str = Field(..., description="Response message")
    processed_count: int = Field(..., description="Number of alerts processed")
    workflow_ids: List[str] = Field(default_factory=list, description="List of workflow IDs created")
    errors: List[str] = Field(default_factory=list, description="List of errors if any")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    def model_dump(self, **kwargs):
        """Override model_dump to handle datetime serialization"""
        data = super().model_dump(**kwargs)
        # Convert datetime objects to ISO format strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data


# Example alert creators for different metric types
def create_high_volume_alert(account_id: str, current_volume: float, threshold: float) -> UsageMetricsAlert:
    """Create an alert for high trade volume"""
    return UsageMetricsAlert(
        alert_id=f"high-volume-{account_id}-{datetime.utcnow().timestamp()}",
        metric_type=MetricType.TRADE_VOLUME,
        severity=AlertSeverity.HIGH,
        threshold_condition=ThresholdCondition(
            operator=ThresholdOperator.GREATER_THAN,
            value=threshold,
            unit="trades"
        ),
        metric_data=MetricData(
            metric_name="trade_volume",
            current_value=current_volume,
            threshold_value=threshold,
            account_id=account_id,
            timestamp=datetime.utcnow()
        ),
        title=f"High Trade Volume Alert - Account {account_id}",
        description=f"Account {account_id} has exceeded the trade volume threshold of {threshold} trades. Current volume: {current_volume}",
        tags=["volume", "trading", "account"]
    )


def create_sla_violation_alert(trade_type: str, current_latency: float, threshold: float) -> UsageMetricsAlert:
    """Create an alert for SLA violation"""
    return UsageMetricsAlert(
        alert_id=f"sla-violation-{trade_type}-{datetime.utcnow().timestamp()}",
        metric_type=MetricType.SLA_VIOLATION,
        severity=AlertSeverity.CRITICAL,
        threshold_condition=ThresholdCondition(
            operator=ThresholdOperator.GREATER_THAN,
            value=threshold,
            unit="seconds"
        ),
        metric_data=MetricData(
            metric_name="response_latency",
            current_value=current_latency,
            threshold_value=threshold,
            trade_type=trade_type,
            timestamp=datetime.utcnow()
        ),
        title=f"SLA Violation Alert - {trade_type}",
        description=f"{trade_type} operations are exceeding SLA threshold of {threshold}s. Current latency: {current_latency}s",
        tags=["sla", "latency", "performance"]
    )


def create_high_value_transaction_alert(account_id: str, trade_amount: float, threshold: float) -> UsageMetricsAlert:
    """Create an alert for high value transactions"""
    return UsageMetricsAlert(
        alert_id=f"high-value-{account_id}-{datetime.utcnow().timestamp()}",
        metric_type=MetricType.TRADE_VALUE,
        severity=AlertSeverity.MEDIUM,
        threshold_condition=ThresholdCondition(
            operator=ThresholdOperator.GREATER_THAN,
            value=threshold,
            unit="dollars"
        ),
        metric_data=MetricData(
            metric_name="trade_value",
            current_value=trade_amount,
            threshold_value=threshold,
            account_id=account_id,
            timestamp=datetime.utcnow()
        ),
        title=f"High Value Transaction Alert - Account {account_id}",
        description=f"Account {account_id} has made a high-value transaction of ${trade_amount:.2f}, exceeding threshold of ${threshold:.2f}",
        tags=["value", "transaction", "account"]
    ) 