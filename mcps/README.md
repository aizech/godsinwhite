# MCP Integration for Halo-Agno

This directory contains the Model Context Protocol (MCP) integration for the Halo-Agno project. MCP allows AI agents to interact with external tools and services through a standardized protocol.

## Overview

The MCP integration provides:

1. **Client Library**: Connect to MCP servers and execute tools
2. **Utility Functions**: Helper functions for MCP operations
3. **SSL Patch**: Fix certificate verification issues on Windows
4. **Server Configurations**: Pre-configured MCP server settings

## Usage

### Setting up an MCP Agent

```python
from mcp.client import MCPClient
from mcp.utils import get_mcp_server_config

# Get MCP server configuration
server_config = get_mcp_server_config("airbnb")

# Create MCP client
mcp_client = MCPClient()

# Connect to server and get tools
mcp_tools = await mcp_client.connect_to_server(server_config)

# Use the tools in your agent
agent = Agent(
    tools=[mcp_tools],
    # other agent parameters
)
```

### Available MCP Servers

The following MCP servers are currently supported:

1. **Airbnb**: Search for and recommend Airbnb listings
   - Server ID: `airbnb`
   - Implementation: Uses the `@openbnb/mcp-server-airbnb` package

2. **LinkedIn**: Access LinkedIn data and functionality
   - Server ID: `linkedin`
   - Implementation: Uses the `@smithery/cli` with `@stickerdaniel/linkedin-mcp-server`

## Adding New MCP Servers

To add a new MCP server:

1. Update the `get_mcp_server_config` function in `utils.py`
2. Create a corresponding agent implementation in the `agents` directory
3. Create a Streamlit page for the agent in the `pages` directory

## Requirements

- Node.js and npm must be installed
- Python dependencies listed in `requirements.txt`

## Troubleshooting

If you encounter issues with MCP servers:

1. Ensure Node.js and npm are installed and in your PATH
2. Check your internet connection
3. Verify that the required npm packages can be installed
4. Look for detailed error messages in the Streamlit UI

For SSL-related issues on Windows, the `ssl_patch.py` module should automatically fix certificate verification problems.
