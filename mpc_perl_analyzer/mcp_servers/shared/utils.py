"""
Shared Utilities for MCP Servers
=================================
Common utility functions used across all MCP servers including
response formatting, error handling, and server helpers.
"""

import json
import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime


def json_response(data: Dict, status: int = 200) -> str:
    """Create a JSON response string."""
    return json.dumps({
        'status': status,
        'timestamp': datetime.now().isoformat(),
        **({'error': data} if status >= 400 else {'data': data})
    })


def error_response(message: str, status: int = 400) -> str:
    """Create an error JSON response."""
    return json.dumps({
        'status': status,
        'timestamp': datetime.now().isoformat(),
        'error': message
    })


def load_config(config_path: str) -> Dict:
    """Load a JSON configuration file."""
    if not os.path.exists(config_path):
        return {}
    with open(config_path, 'r') as f:
        return json.load(f)


def get_server_port(server_name: str, config: Dict, default_port: int) -> int:
    """Get the configured port for a server."""
    servers = config.get('servers', {})
    server_config = servers.get(server_name, {})
    return server_config.get('port', default_port)


def format_tool_list(tools: list) -> str:
    """Format a list of tool descriptions as JSON string."""
    return json.dumps({'tools': tools}, indent=2)


def server_banner(server_name: str, port: int):
    """Print server startup banner."""
    print(f"""
{'=' * 60}
  MPC {server_name.upper()} Server
  Running on port {port}
  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
  Status: ACTIVE (on-demand mode)
{'=' * 60}
    """)


def safe_import(module_name: str):
    """Safely import a module, adding project root to path."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    return __import__(module_name)