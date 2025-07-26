#!/usr/bin/env python3
"""
Configuration Checker for Workflow Features
Checks if features should be enabled based on MCP configuration
"""

import json
import os
from typing import Dict, Any
from enum import Enum

class FeatureStatus(str, Enum):
    """Status of workflow features"""
    ENABLED = "enabled"
    DISABLED = "disabled"

class WorkflowConfig:
    """Configuration for workflow features"""
    def __init__(self):
        self.email_sending: FeatureStatus = FeatureStatus.ENABLED
        self.claude_integration: FeatureStatus = FeatureStatus.ENABLED
        self.slack_posting: FeatureStatus = FeatureStatus.ENABLED
        self.zoom_meeting: FeatureStatus = FeatureStatus.ENABLED
        self.mongodb_integration: FeatureStatus = FeatureStatus.ENABLED
        self.usage_endpoint: FeatureStatus = FeatureStatus.ENABLED

class ConfigChecker:
    """Check if workflow features should be enabled"""
    
    def __init__(self):
        self.config_file = "workflow_config.json"
        self.config = WorkflowConfig()
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self.config, key):
                            setattr(self.config, key, FeatureStatus(value))
                print(f"✅ Loaded workflow configuration from {self.config_file}")
            else:
                print(f"⚠️ No config file found, using defaults")
        except Exception as e:
            print(f"⚠️ Could not load config, using defaults: {e}")
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled"""
        if hasattr(self.config, feature):
            return getattr(self.config, feature) == FeatureStatus.ENABLED
        return True  # Default to enabled if feature not found
    
    def get_status(self) -> Dict[str, str]:
        """Get current configuration status"""
        return {
            "email_sending": self.config.email_sending.value,
            "claude_integration": self.config.claude_integration.value,
            "slack_posting": self.config.slack_posting.value,
            "zoom_meeting": self.config.zoom_meeting.value,
            "mongodb_integration": self.config.mongodb_integration.value,
            "usage_endpoint": self.config.usage_endpoint.value
        }

# Global config checker instance
config_checker = ConfigChecker()

def is_email_enabled() -> bool:
    """Check if email sending is enabled"""
    return config_checker.is_feature_enabled("email_sending")

def is_claude_enabled() -> bool:
    """Check if Claude integration is enabled"""
    return config_checker.is_feature_enabled("claude_integration")

def is_slack_enabled() -> bool:
    """Check if Slack posting is enabled"""
    return config_checker.is_feature_enabled("slack_posting")

def is_zoom_enabled() -> bool:
    """Check if Zoom meeting creation is enabled"""
    return config_checker.is_feature_enabled("zoom_meeting")

def is_mongodb_enabled() -> bool:
    """Check if MongoDB integration is enabled"""
    return config_checker.is_feature_enabled("mongodb_integration")

def is_usage_endpoint_enabled() -> bool:
    """Check if usage endpoint is enabled"""
    return config_checker.is_feature_enabled("usage_endpoint")

def get_config_status() -> Dict[str, str]:
    """Get current configuration status"""
    return config_checker.get_status() 