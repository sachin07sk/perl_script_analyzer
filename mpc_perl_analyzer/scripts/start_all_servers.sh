#!/bin/bash
# Start all MCP servers
# Usage: ./start_all_servers.sh

echo "Starting all MPC MCP Servers..."
echo "================================"

# Get the project root directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Start server manager with all servers
echo "Starting Server Manager with all servers..."
python -c "
from mcp_servers.server_manager import MCPServerManager
manager = MCPServerManager()
for server in ['parser', 'analyzer', 'modernizer', 'pdf_generator', 'eda_knowledge']:
    manager.activate_server(server)
print('All servers started!')
print(manager.get_server_status())
"

echo "================================"
echo "All servers are now running."
echo "Use '../main.py server --status' to check status."
echo "Use './stop_all_servers.sh' to stop all servers."