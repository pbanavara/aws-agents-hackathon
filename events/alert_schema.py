from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status"""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    CLOSED = "closed"


class AlertType(str, Enum):
    """Types of alerts/events"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    INFRASTRUCTURE = "infrastructure"
    APPLICATION = "application"
    BUSINESS = "business"
    MONITORING = "monitoring"
    CUSTOM = "custom"


class AlertSource(BaseModel):
    """Source information for the alert"""
    name: str = Field(..., description="Name of the source system")
    type: str = Field(..., description="Type of source (e.g., 'aws', 'gcp', 'azure', 'custom')")
    identifier: Optional[str] = Field(None, description="Unique identifier for the source")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional source metadata")


class AlertContext(BaseModel):
    """Contextual information for the alert"""
    environment: Optional[str] = Field(None, description="Environment (e.g., 'production', 'staging')")
    service: Optional[str] = Field(None, description="Service name")
    component: Optional[str] = Field(None, description="Component name")
    region: Optional[str] = Field(None, description="Geographic region")
    tags: Optional[Dict[str, str]] = Field(None, description="Key-value tags")
    correlation_id: Optional[str] = Field(None, description="Correlation ID for tracking")


class AlertPayload(BaseModel):
    """Main alert payload schema"""
    # Core alert information
    id: Optional[str] = Field(None, description="Unique alert ID (auto-generated if not provided)")
    title: str = Field(..., description="Alert title/summary")
    description: Optional[str] = Field(None, description="Detailed description of the alert")
    message: Optional[str] = Field(None, description="Alert message content")
    
    # Classification
    type: AlertType = Field(..., description="Type of alert")
    severity: AlertSeverity = Field(..., description="Alert severity level")
    status: AlertStatus = Field(default=AlertStatus.OPEN, description="Current alert status")
    
    # Timing
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Alert timestamp")
    created_at: Optional[datetime] = Field(None, description="When the alert was created")
    updated_at: Optional[datetime] = Field(None, description="When the alert was last updated")
    
    # Source and context
    source: AlertSource = Field(..., description="Source information")
    context: Optional[AlertContext] = Field(None, description="Contextual information")
    
    # Additional data
    data: Optional[Dict[str, Any]] = Field(None, description="Additional alert data")
    metrics: Optional[Dict[str, float]] = Field(None, description="Related metrics")
    logs: Optional[List[str]] = Field(None, description="Related log entries")
    
    # Actions and routing
    assignee: Optional[str] = Field(None, description="Assigned team member or team")
    priority: Optional[int] = Field(None, description="Priority level (1-10)")
    sla_target: Optional[datetime] = Field(None, description="SLA target time")
    
    # Integration fields
    external_id: Optional[str] = Field(None, description="External system ID")
    external_url: Optional[str] = Field(None, description="External system URL")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def model_dump(self, **kwargs):
        """Override model_dump to handle datetime serialization"""
        data = super().model_dump(**kwargs)
        # Convert datetime objects to ISO format strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data


class WebhookRequest(BaseModel):
    """Webhook request wrapper"""
    alerts: List[AlertPayload] = Field(..., description="List of alerts to process")
    batch_id: Optional[str] = Field(None, description="Batch identifier for grouped alerts")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional request metadata")


class WebhookResponse(BaseModel):
    """Webhook response schema"""
    success: bool = Field(..., description="Whether the request was processed successfully")
    message: str = Field(..., description="Response message")
    processed_count: int = Field(..., description="Number of alerts processed")
    workflow_ids: List[str] = Field(default=[], description="IDs of created workflows")
    errors: List[str] = Field(default=[], description="List of errors if any")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    def model_dump(self, **kwargs):
        """Override model_dump to handle datetime serialization"""
        data = super().model_dump(**kwargs)
        # Convert datetime objects to ISO format strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data


# Example usage schemas for different alert types
class SecurityAlert(AlertPayload):
    """Security-specific alert schema"""
    type: AlertType = Field(default=AlertType.SECURITY)
    threat_level: Optional[str] = Field(None, description="Threat level assessment")
    affected_assets: Optional[List[str]] = Field(None, description="List of affected assets")
    ioc_indicators: Optional[List[str]] = Field(None, description="Indicators of compromise")


class PerformanceAlert(AlertPayload):
    """Performance-specific alert schema"""
    type: AlertType = Field(default=AlertType.PERFORMANCE)
    metric_name: Optional[str] = Field(None, description="Name of the metric that triggered the alert")
    threshold: Optional[float] = Field(None, description="Threshold value")
    current_value: Optional[float] = Field(None, description="Current metric value")
    duration: Optional[str] = Field(None, description="Duration of the issue")


class InfrastructureAlert(AlertPayload):
    """Infrastructure-specific alert schema"""
    type: AlertType = Field(default=AlertType.INFRASTRUCTURE)
    resource_type: Optional[str] = Field(None, description="Type of infrastructure resource")
    resource_id: Optional[str] = Field(None, description="Resource identifier")
    availability_zone: Optional[str] = Field(None, description="Availability zone")
    instance_type: Optional[str] = Field(None, description="Instance type (for compute resources)") 