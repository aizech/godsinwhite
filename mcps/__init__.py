"""
MCP (Model Context Protocol) integration for the halo-agno project.
"""

# Import and expose key classes and functions
try:
    from .client import MCPClient, MCPServerConfig
    from .utils import get_mcp_server_config, display_tool_calls
    
    __all__ = [
        'MCPClient',
        'MCPServerConfig',
        'get_mcp_server_config',
        'display_tool_calls'
    ]
except ImportError as e:
    # Provide informative error message
    import sys
    print(f"Error importing MCP components: {e}", file=sys.stderr)
