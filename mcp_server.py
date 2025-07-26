#!/usr/bin/env python3
"""
MCP Server for Workflow Control
Allows selective enabling/disabling of workflow features from Claude Desktop
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Add the workflows directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'workflows'))

class FeatureStatus(str, Enum):
    """Status of workflow features"""
    ENABLED = "enabled"
    DISABLED = "disabled"

@dataclass
class WorkflowConfig:
    """Configuration for workflow features"""
    email_sending: FeatureStatus = FeatureStatus.ENABLED
    claude_integration: FeatureStatus = FeatureStatus.ENABLED
    slack_posting: FeatureStatus = FeatureStatus.ENABLED
    zoom_meeting: FeatureStatus = FeatureStatus.ENABLED
    mongodb_integration: FeatureStatus = FeatureStatus.ENABLED
    usage_endpoint: FeatureStatus = FeatureStatus.ENABLED

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
                    self.config = WorkflowConfig(**data)
                print(f"✅ Loaded workflow configuration from {self.config_file}")
        except Exception as e:
            print(f"⚠️ Could not load config, using defaults: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(asdict(self.config), f, indent=2)
            print(f"✅ Saved workflow configuration to {self.config_file}")
        except Exception as e:
            print(f"❌ Could not save config: {e}")
    
    def get_status(self) -> Dict[str, Any]:
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

# MCP Tool Definitions
def get_workflow_status() -> Dict[str, Any]:
    """Get current workflow feature status"""
    return {
        "name": "get_workflow_status",
        "description": "Get the current status of all workflow features",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }

def disable_workflow_feature() -> Dict[str, Any]:
    """Disable a specific workflow feature"""
    return {
        "name": "disable_workflow_feature",
        "description": "Disable a specific workflow feature (email_sending, claude_integration, slack_posting, zoom_meeting, mongodb_integration, usage_endpoint)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "feature": {
                    "type": "string",
                    "enum": ["email_sending", "claude_integration", "slack_posting", "zoom_meeting", "mongodb_integration", "usage_endpoint"],
                    "description": "The feature to disable"
                }
            },
            "required": ["feature"]
        }
    }

def enable_workflow_feature() -> Dict[str, Any]:
    """Enable a specific workflow feature"""
    return {
        "name": "enable_workflow_feature",
        "description": "Enable a specific workflow feature (email_sending, claude_integration, slack_posting, zoom_meeting, mongodb_integration, usage_endpoint)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "feature": {
                    "type": "string",
                    "enum": ["email_sending", "claude_integration", "slack_posting", "zoom_meeting", "mongodb_integration", "usage_endpoint"],
                    "description": "The feature to enable"
                }
            },
            "required": ["feature"]
        }
    }

def toggle_workflow_feature() -> Dict[str, Any]:
    """Toggle a workflow feature on/off"""
    return {
        "name": "toggle_workflow_feature",
        "description": "Toggle a workflow feature on/off (email_sending, claude_integration, slack_posting, zoom_meeting, mongodb_integration, usage_endpoint)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "feature": {
                    "type": "string",
                    "enum": ["email_sending", "claude_integration", "slack_posting", "zoom_meeting", "mongodb_integration", "usage_endpoint"],
                    "description": "The feature to toggle"
                }
            },
            "required": ["feature"]
        }
    }

def reset_workflow_features() -> Dict[str, Any]:
    """Reset all workflow features to enabled"""
    return {
        "name": "reset_workflow_features",
        "description": "Reset all workflow features to enabled state",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }

def disable_all_workflow_features() -> Dict[str, Any]:
    """Disable all workflow features"""
    return {
        "name": "disable_all_workflow_features",
        "description": "Disable all workflow features",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }

# Tool implementations
async def handle_get_workflow_status(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get workflow status request"""
    status = controller.get_status()
    return {
        "content": [
            {
                "type": "text",
                "text": f"📊 **Workflow Feature Status:**\n\n" + 
                       "\n".join([f"• **{k.replace('_', ' ').title()}**: {v}" for k, v in status.items()])
            }
        ]
    }

async def handle_disable_workflow_feature(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle disable workflow feature request"""
    feature = args.get("feature")
    result = controller.disable_feature(feature)
    
    if result["success"]:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"✅ **{result['message']}**\n\n📊 **Current Status:**\n" + 
                           "\n".join([f"• **{k.replace('_', ' ').title()}**: {v}" for k, v in result['status'].items()])
                }
            ]
        }
    else:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"❌ **{result['message']}**\n\nAvailable features: {', '.join(result['available_features'])}"
                }
            ]
        }

async def handle_enable_workflow_feature(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle enable workflow feature request"""
    feature = args.get("feature")
    result = controller.enable_feature(feature)
    
    if result["success"]:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"✅ **{result['message']}**\n\n📊 **Current Status:**\n" + 
                           "\n".join([f"• **{k.replace('_', ' ').title()}**: {v}" for k, v in result['status'].items()])
                }
            ]
        }
    else:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"❌ **{result['message']}**\n\nAvailable features: {', '.join(result['available_features'])}"
                }
            ]
        }

async def handle_toggle_workflow_feature(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle toggle workflow feature request"""
    feature = args.get("feature")
    result = controller.toggle_feature(feature)
    
    if result["success"]:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"🔄 **{result['message']}**\n\n📊 **Current Status:**\n" + 
                           "\n".join([f"• **{k.replace('_', ' ').title()}**: {v}" for k, v in result['status'].items()])
                }
            ]
        }
    else:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"❌ **{result['message']}**\n\nAvailable features: {', '.join(result['available_features'])}"
                }
            ]
        }

async def handle_reset_workflow_features(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle reset workflow features request"""
    result = controller.reset_all()
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"🔄 **{result['message']}**\n\n📊 **Current Status:**\n" + 
                       "\n".join([f"• **{k.replace('_', ' ').title()}**: {v}" for k, v in result['status'].items()])
            }
        ]
    }

async def handle_disable_all_workflow_features(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle disable all workflow features request"""
    result = controller.disable_all()
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"🔄 **{result['message']}**\n\n📊 **Current Status:**\n" + 
                       "\n".join([f"• **{k.replace('_', ' ').title()}**: {v}" for k, v in result['status'].items()])
            }
        ]
    }

# Tool registry
TOOLS = {
    "get_workflow_status": {
        "definition": get_workflow_status(),
        "handler": handle_get_workflow_status
    },
    "disable_workflow_feature": {
        "definition": disable_workflow_feature(),
        "handler": handle_disable_workflow_feature
    },
    "enable_workflow_feature": {
        "definition": enable_workflow_feature(),
        "handler": handle_enable_workflow_feature
    },
    "toggle_workflow_feature": {
        "definition": toggle_workflow_feature(),
        "handler": handle_toggle_workflow_feature
    },
    "reset_workflow_features": {
        "definition": reset_workflow_features(),
        "handler": handle_reset_workflow_features
    },
    "disable_all_workflow_features": {
        "definition": disable_all_workflow_features(),
        "handler": handle_disable_all_workflow_features
    }
}

# MCP Server implementation
class MCPServer:
    """Simple MCP Server for workflow control"""
    
    def __init__(self):
        self.tools = TOOLS
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        return [tool["definition"] for tool in self.tools.values()]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool"""
        if name in self.tools:
            handler = self.tools[name]["handler"]
            return await handler(arguments)
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"❌ Unknown tool: {name}\n\nAvailable tools: {', '.join(self.tools.keys())}"
                    }
                ]
            }

# Create server instance
server = MCPServer()

# Example usage
if __name__ == "__main__":
    print("🚀 Workflow MCP Server")
    print("Available tools:")
    for tool_name in server.tools.keys():
        print(f"  • {tool_name}")
    print("\nConfiguration file: workflow_config.json")
    print("Use this server with Claude Desktop to control workflow features!") 