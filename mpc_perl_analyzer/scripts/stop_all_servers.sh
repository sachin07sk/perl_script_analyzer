#!/bin/bash
# Stop all MCP servers
# Usage: ./stop_all_servers.sh

echo "Stopping all MPC MCP Servers..."
echo "================================"

# Get the project root directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Stop all servers via server manager
python -c "
from mcp_servers.server_manager import MCPServerManager
manager = MCPServerManager()
manager.shutdown_all()
print('All servers stopped.')
"

echo "================================"
echo "All servers have been stopped."