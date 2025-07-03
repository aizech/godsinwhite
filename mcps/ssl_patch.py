"""
SSL patch to fix certificate verification issues with MCP servers.
This module should be imported before any MCP client operations.
"""

import ssl
import sys


def patch_ssl_for_mcp():
    """
    Patch SSL to allow MCP servers to work properly with certificate verification.
    This is especially important for Windows environments.
    """
    # Create a custom SSL context that doesn't verify certificates
    # This is needed for some MCP servers that use self-signed certificates
    if sys.platform == 'win32':
        # Only apply the patch on Windows
        try:
            _create_unverified_https_context = ssl._create_unverified_context
            ssl._create_default_https_context = _create_unverified_https_context
            return True
        except AttributeError:
            # Legacy Python that doesn't verify HTTPS certificates by default
            return False
    return False


# Apply the patch when the module is imported
patch_applied = patch_ssl_for_mcp()
