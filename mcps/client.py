"""
MCP Client module for the halo-agno project.
Provides classes and functions for connecting to MCP servers.
"""

import os
import sys
import subprocess
from contextlib import AsyncExitStack
from typing import List, Optional, Dict, Any, Union

from agno.tools.mcp import MCPTools
from agno.utils.log import logger

# Try to import from mcp package, but provide fallbacks if not available
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    mcp_imports_available = True
except ImportError:
    logger.warning("MCP package not available. Using fallback implementations.")
    mcp_imports_available = False
    # Define placeholder classes
    class StdioServerParameters:
        def __init__(self, command, args):
            self.command = command
            self.args = args
    
    class ClientSession:
        def __init__(self, stdio, write):
            self.stdio = stdio
            self.write = write
        
        async def initialize(self):
            pass

from pydantic import BaseModel


class MCPServerConfig(BaseModel):
    """Configuration for an MCP server."""

    id: str
    command: str
    args: Optional[List[str]] = None


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session = None
        self.exit_stack = AsyncExitStack()
        self.tools = []
        self.server_id = None

    async def connect_to_server(self, server_config):
        """Connect to an MCP server using the provided configuration

        Args:
            server_config: Configuration for the MCP server
        """
        self.server_id = server_config.id

        # Always use direct MCPTools approach which is more reliable across environments
        cmd = f"{server_config.command} {' '.join(server_config.args)}" if server_config.args else server_config.command
        logger.info(f"Using direct MCPTools with command: {cmd}")
        
        try:
            # Create MCPTools directly
            mcp_tools = MCPTools(cmd)
            logger.info(f"Successfully created MCPTools for {self.server_id}")
            return mcp_tools
        except Exception as e:
            logger.error(f"Error creating MCPTools for {self.server_id}: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Create a minimal mock MCPTools as absolute fallback
            from agno.tools.mcp import MCPTools as BaseMCPTools
            
            class MockMCPTools(BaseMCPTools):
                def __init__(self, cmd):
                    super().__init__(cmd)
                    self.cmd = cmd
                    logger.info(f"Created MockMCPTools with command: {cmd}")
                
                async def run(self, *args, **kwargs):
                    logger.info(f"MockMCPTools run called with args: {args}, kwargs: {kwargs}")
                    return {
                        "result": f"Mock response for {self.server_id} MCP server. The actual server could not be started."
                    }
            
            logger.info(f"Using MockMCPTools as fallback for {self.server_id}")
            return MockMCPTools(cmd)

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()
