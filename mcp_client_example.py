#!/usr/bin/env python3
"""
Example MCP Client for testing the workflow control server
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_server():
    """Test the MCP server functionality"""
    
    # Create server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
        env={"PYTHONPATH": "."}
    )
    
    # Connect to the server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # List available tools
            tools = await session.list_tools()
            print("🔧 Available tools:")
            for tool in tools:
                print(f"  • {tool.name}: {tool.description}")
            
            # Test getting workflow status
            print("\n📊 Getting workflow status...")
            result = await session.call_tool("get_workflow_status", {})
            print(f"Result: {result.content[0].text}")
            
            # Test disabling email sending
            print("\n📧 Disabling email sending...")
            result = await session.call_tool("disable_workflow_feature", {"feature": "email_sending"})
            print(f"Result: {result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(test_mcp_server()) 