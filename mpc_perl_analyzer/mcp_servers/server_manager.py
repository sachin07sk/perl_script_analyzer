"""
MCP Server Manager
==================
Orchestrates on-demand activation and idle-timeout shutdown
of MCP servers for resource-efficient operation.
"""

import os
import sys
import json
import time
import threading
import subprocess
import signal
from typing import Dict, Optional, Callable
from datetime import datetime, timedelta


# Server configuration
DEFAULT_SERVER_CONFIG = {
    "parser": {
        "port": 5001,
        "idle_timeout": 900,  # 15 minutes
        "auto_start": False,
        "max_instances": 2,
        "description": "Perl Script Parser Server"
    },
    "analyzer": {
        "port": 5002,
        "idle_timeout": 900,
        "auto_start": False,
        "max_instances": 2,
        "description": "Perl Script Analyzer Server"
    },
    "modernizer": {
        "port": 5003,
        "idle_timeout": 1200,
        "auto_start": False,
        "max_instances": 1,
        "description": "Code Modernizer Server"
    },
    "pdf_generator": {
        "port": 5004,
        "idle_timeout": 1800,
        "auto_start": False,
        "max_instances": 1,
        "description": "PDF Report Generator Server"
    },
    "eda_knowledge": {
        "port": 5005,
        "idle_timeout": 600,
        "auto_start": False,
        "max_instances": 1,
        "description": "EDA Knowledge Base Server"
    }
}


class MCPServerManager:
    """
    Manages the lifecycle of MCP servers with on-demand activation
    and automatic shutdown after idle timeout.
    """

    def __init__(self, config_file: str = None):
        self.servers = {}  # server_name -> process info
        self.idle_timers = {}  # server_name -> timer
        self.last_activity = {}  # server_name -> timestamp
        self.lock = threading.RLock()
        self.running = True
        self._stop_event = threading.Event()

        # Load configuration
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.config = json.load(f).get('servers', DEFAULT_SERVER_CONFIG)
        else:
            self.config = DEFAULT_SERVER_CONFIG

        # Start monitor thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self._monitor_started = True

    def activate_server(self, server_name: str) -> bool:
        """
        Activate a server on-demand. Starts if not running.

        Args:
            server_name: Name of the server to activate

        Returns:
            True if server is active, False otherwise
        """
        if server_name not in self.config:
            print(f"Unknown server: {server_name}")
            return False

        with self.lock:
            if server_name in self.servers:
                # Server is already running - reset idle timer
                self._reset_idle_timer(server_name)
                self.last_activity[server_name] = datetime.now()
                print(f"Server '{server_name}' is already active. Timer reset.")
                return True

            # Start the server
            return self._start_server(server_name)

    def deactivate_server(self, server_name: str) -> bool:
        """
        Deactivate a server immediately.

        Args:
            server_name: Name of the server to deactivate

        Returns:
            True if server was stopped, False otherwise
        """
        with self.lock:
            return self._stop_server(server_name)

    def get_server_status(self, server_name: str = None) -> Dict:
        """
        Get status of servers.

        Args:
            server_name: Specific server or None for all

        Returns:
            Dict with server status information
        """
        with self.lock:
            if server_name:
                info = self.servers.get(server_name)
                config = self.config.get(server_name, {})
                if info:
                    idle_time = (datetime.now() - self.last_activity.get(server_name, datetime.now())).seconds
                    return {
                        'name': server_name,
                        'status': 'active',
                        'port': config.get('port'),
                        'description': config.get('description'),
                        'idle_seconds': idle_time,
                        'timeout_seconds': config.get('idle_timeout', 900),
                        'pid': info.get('pid'),
                        'started_at': info.get('started_at').strftime('%H:%M:%S') if info.get('started_at') else None
                    }
                else:
                    return {
                        'name': server_name,
                        'status': 'inactive',
                        'port': config.get('port'),
                        'description': config.get('description'),
                        'idle_seconds': 0,
                        'timeout_seconds': config.get('idle_timeout', 900)
                    }

            # Return all servers
            statuses = {}
            for name in self.config:
                statuses[name] = self.get_server_status(name)
            return {
                'active_count': len(self.servers),
                'total_servers': len(self.config),
                'servers': statuses
            }

    def request_server(self, server_name: str) -> Optional[int]:
        """
        Request a server, activating it if needed. Returns port number.

        Args:
            server_name: Name of the server to use

        Returns:
            Port number if server is active, None if failed
        """
        if self.activate_server(server_name):
            config = self.config.get(server_name, {})
            return config.get('port')
        return None

    def shutdown_all(self):
        """Shutdown all servers gracefully."""
        if not self.running:
            return
        self.running = False
        self._stop_event.set()  # Interrupt monitor thread immediately
        with self.lock:
            for server_name in list(self.servers.keys()):
                self._stop_server(server_name)
        # Wait for monitor thread to finish (with short timeout)
        if hasattr(self, '_monitor_started') and self._monitor_started:
            self.monitor_thread.join(timeout=2)
        print("All servers stopped.")

    def _start_server(self, server_name: str) -> bool:
        """Internal method to start a server process."""
        config = self.config.get(server_name)
        if not config:
            return False

        # Get the server script path
        script_map = {
            'parser': 'mcp_servers/parser_server.py',
            'analyzer': 'mcp_servers/analyzer_server.py',
            'modernizer': 'mcp_servers/modernizer_server.py',
            'pdf_generator': 'mcp_servers/pdf_server.py',
            'eda_knowledge': 'mcp_servers/eda_knowledge_server.py'
        }

        script_path = script_map.get(server_name)
        if not script_path or not os.path.exists(script_path):
            # Check relative to project root
            alt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), script_path)
            if not os.path.exists(alt_path):
                print(f"Server script not found: {script_path}")
                return False
            script_path = alt_path

        try:
            # Start the server process
            process = subprocess.Popen(
                [sys.executable, script_path, '--port', str(config['port'])],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.servers[server_name] = {
                'process': process,
                'pid': process.pid,
                'started_at': datetime.now(),
                'port': config['port']
            }
            self.last_activity[server_name] = datetime.now()
            self._reset_idle_timer(server_name)

            print(f"Server '{server_name}' started on port {config['port']} (PID: {process.pid})")
            return True

        except Exception as e:
            print(f"Failed to start server '{server_name}': {e}")
            return False

    def _stop_server(self, server_name: str) -> bool:
        """Internal method to stop a server process."""
        if server_name not in self.servers:
            return False

        info = self.servers[server_name]
        process = info.get('process')

        # Cancel idle timer
        self._cancel_idle_timer(server_name)

        try:
            if process and process.poll() is None:
                # Try graceful shutdown
                if os.name == 'nt':  # Windows
                    process.terminate()
                else:
                    process.send_signal(signal.SIGTERM)

                # Wait up to 5 seconds
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()

            print(f"Server '{server_name}' stopped.")
            del self.servers[server_name]
            if server_name in self.last_activity:
                del self.last_activity[server_name]
            return True

        except Exception as e:
            print(f"Error stopping server '{server_name}': {e}")
            return False

    def _reset_idle_timer(self, server_name: str):
        """Reset the idle timer for a server."""
        self._cancel_idle_timer(server_name)
        timeout = self.config.get(server_name, {}).get('idle_timeout', 900)

        timer = threading.Timer(timeout, self._handle_idle_timeout, [server_name])
        timer.daemon = True
        timer.start()
        self.idle_timers[server_name] = timer

    def _cancel_idle_timer(self, server_name: str):
        """Cancel the idle timer for a server."""
        if server_name in self.idle_timers:
            self.idle_timers[server_name].cancel()
            del self.idle_timers[server_name]

    def _handle_idle_timeout(self, server_name: str):
        """Handle server idle timeout."""
        with self.lock:
            if server_name in self.servers:
                print(f"Server '{server_name}' idle timeout reached. Stopping...")
                self._stop_server(server_name)

    def _monitor_loop(self):
        """Background monitor loop to check server health."""
        while self.running and not self._stop_event.is_set():
            # Use event.wait() so shutdown_all() can interrupt immediately
            if self._stop_event.wait(timeout=10):
                break  # Stop event was set
            with self.lock:
                for server_name in list(self.servers.keys()):
                    info = self.servers[server_name]
                    process = info.get('process')
                    if process and process.poll() is not None:
                        # Process died unexpectedly
                        print(f"Server '{server_name}' stopped unexpectedly.")
                        del self.servers[server_name]
                        self._cancel_idle_timer(server_name)
                        if server_name in self.last_activity:
                            del self.last_activity[server_name]


# CLI Interface
def print_server_status(manager: MCPServerManager):
    """Print formatted server status."""
    status = manager.get_server_status()
    print("\n" + "=" * 60)
    print(f"  MPC Server Manager - {status['active_count']}/{status['total_servers']} servers active")
    print("=" * 60)

    for name, info in status['servers'].items():
        if info['status'] == 'active':
            idle_pct = (info['idle_seconds'] / info['timeout_seconds']) * 100
            bar = '#' * int(idle_pct / 10) + '-' * (10 - int(idle_pct / 10))
            print(f"  [{name:15s}] ACTIVE   |{bar}| {info['idle_seconds']:3d}s / {info['timeout_seconds']}s idle")
        else:
            print(f"  [{name:15s}] INACTIVE |          | Port {info['port']}")

    print("=" * 60)


def main():
    """CLI entry point for server manager."""
    import argparse

    parser = argparse.ArgumentParser(description='MPC Server Manager')
    parser.add_argument('--config', '-c', help='Server configuration file')
    parser.add_argument('--start', '-s', help='Start a specific server')
    parser.add_argument('--stop', help='Stop a specific server')
    parser.add_argument('--status', action='store_true', help='Show server status')
    parser.add_argument('--all', action='store_true', help='Start all servers')

    args = parser.parse_args()

    manager = MCPServerManager(args.config)

    if args.start:
        if args.start == 'all' or args.all:
            for server in DEFAULT_SERVER_CONFIG:
                manager.activate_server(server)
        else:
            manager.activate_server(args.start)

    if args.stop:
        if args.stop == 'all':
            manager.shutdown_all()
        else:
            manager.deactivate_server(args.stop)

    if args.status:
        print_server_status(manager)

    # If no specific action, start interactive mode
    if not (args.start or args.stop or args.status):
        print("\nMPC Server Manager - Interactive Mode")
        print("Commands: start <server>, stop <server>, status, exit")
        print("Servers: parser, analyzer, modernizer, pdf_generator, eda_knowledge")

        try:
            while True:
                cmd = input("\n> ").strip().lower()
                if not cmd:
                    continue
                if cmd == 'exit' or cmd == 'quit':
                    manager.shutdown_all()
                    break
                elif cmd == 'status':
                    print_server_status(manager)
                elif cmd.startswith('start '):
                    server = cmd[6:]
                    if server == 'all':
                        for s in DEFAULT_SERVER_CONFIG:
                            manager.activate_server(s)
                    else:
                        manager.activate_server(server)
                elif cmd.startswith('stop '):
                    server = cmd[5:]
                    if server == 'all':
                        manager.shutdown_all()
                    else:
                        manager.deactivate_server(server)
                else:
                    print("Unknown command. Try: start <server>, stop <server>, status, exit")
        except KeyboardInterrupt:
            print("\n")
            manager.shutdown_all()


if __name__ == '__main__':
    main()