#!/usr/bin/env python3
"""
Workflow Control MCP Server using FastMCP
Allows selective enabling/disabling of workflow features from Claude Desktop
"""

import json
import os
from typing import Dict, Any, List
from enum import Enum
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Workflow Control")

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

class WorkflowController:
    """Controller for managing workflow features"""
    
    def __init__(self):
        self.config = WorkflowConfig()
        self.config_file = "workflow_config.json"
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
        except Exception as e:
            print(f"⚠️ Could not load config, using defaults: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            config_dict = {
                "email_sending": self.config.email_sending.value,
                "claude_integration": self.config.claude_integration.value,
                "slack_posting": self.config.slack_posting.value,
                "zoom_meeting": self.config.zoom_meeting.value,
                "mongodb_integration": self.config.mongodb_integration.value,
                "usage_endpoint": self.config.usage_endpoint.value
            }
            with open(self.config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
            print(f"✅ Saved workflow configuration to {self.config_file}")
        except Exception as e:
            print(f"❌ Could not save config: {e}")
    
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
    
    def disable_feature(self, feature: str) -> Dict[str, Any]:
        """Disable a specific feature"""
        if hasattr(self.config, feature):
            setattr(self.config, feature, FeatureStatus.DISABLED)
            self.save_config()
            return {
                "success": True,
                "message": f"✅ Disabled {feature}",
                "status": self.get_status()
            }
        else:
            return {
                "success": False,
                "message": f"❌ Unknown feature: {feature}",
                "available_features": [f for f in dir(self.config) if not f.startswith('_')]
            }
    
    def enable_feature(self, feature: str) -> Dict[str, Any]:
        """Enable a specific feature"""
        if hasattr(self.config, feature):
            setattr(self.config, feature, FeatureStatus.ENABLED)
            self.save_config()
            return {
                "success": True,
                "message": f"✅ Enabled {feature}",
                "status": self.get_status()
            }
        else:
            return {
                "success": False,
                "message": f"❌ Unknown feature: {feature}",
                "available_features": [f for f in dir(self.config) if not f.startswith('_')]
            }
    
    def toggle_feature(self, feature: str) -> Dict[str, Any]:
        """Toggle a feature on/off"""
        if hasattr(self.config, feature):
            current_status = getattr(self.config, feature)
            new_status = FeatureStatus.DISABLED if current_status == FeatureStatus.ENABLED else FeatureStatus.ENABLED
            setattr(self.config, feature, new_status)
            self.save_config()
            return {
                "success": True,
                "message": f"🔄 Toggled {feature} to {new_status.value}",
                "status": self.get_status()
            }
        else:
            return {
                "success": False,
                "message": f"❌ Unknown feature: {feature}",
                "available_features": [f for f in dir(self.config) if not f.startswith('_')]
            }
    
    def reset_all(self) -> Dict[str, Any]:
        """Reset all features to enabled"""
        self.config = WorkflowConfig()
        self.save_config()
        return {
            "success": True,
            "message": "🔄 Reset all features to enabled",
            "status": self.get_status()
        }
    
    def disable_all(self) -> Dict[str, Any]:
        """Disable all features"""
        for feature in [f for f in dir(self.config) if not f.startswith('_')]:
            setattr(self.config, feature, FeatureStatus.DISABLED)
        self.save_config()
        return {
            "success": True,
            "message": "🔄 Disabled all features",
            "status": self.get_status()
        }

# Global controller instance
controller = WorkflowController()

# MCP Tools

@mcp.tool()
def get_workflow_status() -> str:
    """Get the current status of all workflow features"""
    status = controller.get_status()
    status_text = "📊 **Workflow Feature Status:**\n\n"
    for feature, state in status.items():
        status_text += f"• **{feature.replace('_', ' ').title()}**: {state}\n"
    return status_text

@mcp.tool()
def disable_workflow_feature(feature: str) -> str:
    """Disable a specific workflow feature (email_sending, claude_integration, slack_posting, zoom_meeting, mongodb_integration, usage_endpoint)"""
    result = controller.disable_feature(feature)
    
    if result["success"]:
        response = f"✅ **{result['message']}**\n\n📊 **Current Status:**\n"
        for feature, state in result['status'].items():
            response += f"• **{feature.replace('_', ' ').title()}**: {state}\n"
        return response
    else:
        return f"❌ **{result['message']}**\n\nAvailable features: {', '.join(result['available_features'])}"

@mcp.tool()
def enable_workflow_feature(feature: str) -> str:
    """Enable a specific workflow feature (email_sending, claude_integration, slack_posting, zoom_meeting, mongodb_integration, usage_endpoint)"""
    result = controller.enable_feature(feature)
    
    if result["success"]:
        response = f"✅ **{result['message']}**\n\n📊 **Current Status:**\n"
        for feature, state in result['status'].items():
            response += f"• **{feature.replace('_', ' ').title()}**: {state}\n"
        return response
    else:
        return f"❌ **{result['message']}**\n\nAvailable features: {', '.join(result['available_features'])}"

@mcp.tool()
def toggle_workflow_feature(feature: str) -> str:
    """Toggle a workflow feature on/off (email_sending, claude_integration, slack_posting, zoom_meeting, mongodb_integration, usage_endpoint)"""
    result = controller.toggle_feature(feature)
    
    if result["success"]:
        response = f"🔄 **{result['message']}**\n\n📊 **Current Status:**\n"
        for feature, state in result['status'].items():
            response += f"• **{feature.replace('_', ' ').title()}**: {state}\n"
        return response
    else:
        return f"❌ **{result['message']}**\n\nAvailable features: {', '.join(result['available_features'])}"

@mcp.tool()
def reset_workflow_features() -> str:
    """Reset all workflow features to enabled state"""
    result = controller.reset_all()
    
    response = f"🔄 **{result['message']}**\n\n📊 **Current Status:**\n"
    for feature, state in result['status'].items():
        response += f"• **{feature.replace('_', ' ').title()}**: {state}\n"
    return response

@mcp.tool()
def disable_all_workflow_features() -> str:
    """Disable all workflow features"""
    result = controller.disable_all()
    
    response = f"🔄 **{result['message']}**\n\n📊 **Current Status:**\n"
    for feature, state in result['status'].items():
        response += f"• **{feature.replace('_', ' ').title()}**: {state}\n"
    return response

# MCP Resources

@mcp.resource("workflow://config")
def get_workflow_config() -> str:
    """Get the current workflow configuration as JSON"""
    return json.dumps(controller.get_status(), indent=2)

@mcp.resource("workflow://features")
def get_available_features() -> str:
    """Get list of available workflow features"""
    features = [
        "email_sending",
        "claude_integration", 
        "slack_posting",
        "zoom_meeting",
        "mongodb_integration",
        "usage_endpoint"
    ]
    return json.dumps(features, indent=2)

# MCP Prompts

@mcp.prompt()
def workflow_control_prompt(action: str, feature: str = None) -> str:
    """Generate a prompt for workflow control actions"""
    
    if action == "status":
        return "Please show me the current status of all workflow features."
    
    elif action == "disable":
        if feature:
            return f"Please disable the {feature} workflow feature."
        else:
            return "Please disable a workflow feature. Available features: email_sending, claude_integration, slack_posting, zoom_meeting, mongodb_integration, usage_endpoint"
    
    elif action == "enable":
        if feature:
            return f"Please enable the {feature} workflow feature."
        else:
            return "Please enable a workflow feature. Available features: email_sending, claude_integration, slack_posting, zoom_meeting, mongodb_integration, usage_endpoint"
    
    elif action == "toggle":
        if feature:
            return f"Please toggle the {feature} workflow feature on/off."
        else:
            return "Please toggle a workflow feature. Available features: email_sending, claude_integration, slack_posting, zoom_meeting, mongodb_integration, usage_endpoint"
    
    elif action == "reset":
        return "Please reset all workflow features to enabled state."
    
    elif action == "disable_all":
        return "Please disable all workflow features."
    
    else:
        return "Please help me control workflow features. Available actions: status, disable, enable, toggle, reset, disable_all"

if __name__ == "__main__":
    # Run the server
    mcp.run() 