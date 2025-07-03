"""
Utility functions for MCP integration in the halo-agno project.
"""

import sys
import shutil
from typing import Optional, List, Dict, Any

import streamlit as st
from agno.agent import Agent
from agno.tools.mcp import MCPTools
from agno.utils.log import logger

from mcps.client import MCPServerConfig


def get_mcp_server_config(server_id: str) -> Optional[MCPServerConfig]:
    """Get MCP server configuration for a specific server ID.

    Args:
        server_id: The ID of the MCP server to configure

    Returns:
        Optional[MCPServerConfig]: A MCP server config, or None if not supported.
    """
    # Find npx path
    npx_path = shutil.which('npx')
    if not npx_path:
        logger.error("npx command not found in PATH")
        return None

    # Configure based on server ID
    if server_id == "airbnb":
        # For Windows, we need to use a different approach
        if sys.platform == 'win32':
            # Use cmd as the command and pass the npx command as an argument
            return MCPServerConfig(
                id="airbnb",
                command="cmd",
                args=["/c", "npx", "-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
            )
        else:
            # For non-Windows platforms
            return MCPServerConfig(
                id="airbnb",
                command="npx",
                args=["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
            )
    
    elif server_id == "linkedin":
        # For Windows, we need to use a different approach
        if sys.platform == 'win32':
            # Use cmd as the command and pass the npx command as an argument
            return MCPServerConfig(
                id="linkedin",
                command="cmd",
                args=["/c", "npx", "-y", "@smithery/cli@latest", "run", "@stickerdaniel/linkedin-mcp-server", "--key", "5cff50bf-6856-49ce-af34-3d7f90430171"]
            )
        else:
            # For non-Windows platforms
            return MCPServerConfig(
                id="linkedin",
                command="npx",
                args=["-y", "@smithery/cli@latest", "run", "@stickerdaniel/linkedin-mcp-server", "--key", "5cff50bf-6856-49ce-af34-3d7f90430171"]
            )
    
    # Add more MCP server configurations as needed
    
    return None


def display_tool_calls(tool_calls_container, tools):
    """Display tool calls in a streamlit container with expandable sections.

    Args:
        tool_calls_container: Streamlit container to display the tool calls
        tools: List of tool call dictionaries or ToolExecution objects
    """
    if not tools or len(tools) == 0:
        return
    
    with tool_calls_container.expander("🔧 Tool Calls", expanded=True):
        for i, tool_call in enumerate(tools):
            try:
                # Try to get the tool name
                if hasattr(tool_call, "get") and "name" in tool_call:
                    tool_name = tool_call["name"]
                elif hasattr(tool_call, "tool_name"):
                    tool_name = tool_call.tool_name
                else:
                    tool_name = f"Tool {i+1}"
                
                st.markdown(f"**{i + 1}. {tool_name}**")
                
                # Try to get arguments
                if hasattr(tool_call, "get") and "arguments" in tool_call:
                    st.code(tool_call['arguments'], language="json")
                elif hasattr(tool_call, "tool_args"):
                    st.code(tool_call.tool_args, language="json")
                
                # Try to get content
                if hasattr(tool_call, "get") and "content" in tool_call:
                    st.markdown("**Results:**")
                    st.code(tool_call['content'])
                elif hasattr(tool_call, "content"):
                    st.markdown("**Results:**")
                    st.code(tool_call.content)
            except Exception as e:
                # Fallback for any tool call that can't be processed
                st.error(f"Error displaying tool call: {str(e)}")


def add_message(role: str, content: str, tool_calls: Optional[List[Dict[str, Any]]] = None):
    """Safely add a message to the session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    message = {"role": role, "content": content}
    if tool_calls:
        message["tool_calls"] = tool_calls
    
    st.session_state.messages.append(message)
