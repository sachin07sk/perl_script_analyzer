#!/bin/bash
# Check status of all MCP servers
# Usage: ./check_server_status.sh

echo "================================"
echo "MPC MCP Server Status Check"
echo "================================"

# Get the project root directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Check server status
python -c "
from mcp_servers.server_manager import MCPServerManager, print_server_status
manager = MCPServerManager()
print_server_status(manager)
"

echo "================================"

# Check if server processes are running
echo ""
echo "Active Python Processes (server related):"
wmic process where "name='python.exe' AND commandline like '%server%'" get processid,commandline 2>/dev/null || \
ps aux | grep -i "server" | grep -v grep | head -5 2>/dev/null || \
echo "  (Process check not available on this platform)"
echo ""
