"""
MCP Parser Server
=================
Provides Perl script parsing capabilities via MCP protocol.
On-demand activation with idle timeout.
"""

import sys
import os
import json
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.parser import create_parser


class ParserRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MCP Parser Server."""

    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length else b'{}'
        
        try:
            request = json.loads(body)
            response = self._handle_request(request)
        except json.JSONDecodeError:
            response = {'error': 'Invalid JSON'}
        except Exception as e:
            response = {'error': str(e)}

        self._send_response(response)

    def do_GET(self):
        """Handle GET requests - health check and info."""
        if self.path == '/health':
            self._send_response({
                'status': 'ok',
                'server': 'parser',
                'version': '1.0.0'
            })
        elif self.path == '/tools':
            self._send_response({
                'tools': [
                    {
                        'name': 'parse_perl_script',
                        'description': 'Parse a Perl script and return AST',
                        'parameters': {
                            'content': {'type': 'string', 'description': 'Perl script content'},
                            'filename': {'type': 'string', 'description': 'Script filename', 'optional': True}
                        }
                    },
                    {
                        'name': 'get_line_info',
                        'description': 'Get detailed info about a specific line',
                        'parameters': {
                            'content': {'type': 'string', 'description': 'Perl script content'},
                            'line_number': {'type': 'integer', 'description': 'Line number (1-based)'}
                        }
                    },
                    {
                        'name': 'extract_functions',
                        'description': 'List all functions/subroutines',
                        'parameters': {
                            'content': {'type': 'string', 'description': 'Perl script content'}
                        }
                    },
                    {
                        'name': 'extract_variables',
                        'description': 'List all variables with scope info',
                        'parameters': {
                            'content': {'type': 'string', 'description': 'Perl script content'}
                        }
                    },
                    {
                        'name': 'get_dependencies',
                        'description': 'List required modules and packages',
                        'parameters': {
                            'content': {'type': 'string', 'description': 'Perl script content'}
                        }
                    }
                ]
            })
        else:
            self._send_response({'error': 'Not found'}, 404)

    def _handle_request(self, request: Dict) -> Dict:
        """Route request to appropriate handler."""
        action = request.get('action', '')
        content = request.get('content', '')
        filename = request.get('filename', 'script.pl')

        parser = create_parser()

        if action == 'parse_perl_script':
            result = parser.parse(content, filename)
            return {
                'filename': result.filename,
                'total_lines': len(result.lines),
                'shebang': result.shebang,
                'modules': [{'line': m['line_number'], 'module': m['module']} for m in result.modules_used],
                'subroutines': [{'line': s['line_number'], 'name': s['name']} for s in result.subroutines],
                'variables': [{'line': v['line_number'], 'var': v['variable']} for v in result.variables],
                'packages': result.packages,
                'comments_count': len(result.comments),
                'ast_nodes': [{'line': n.line_number, 'type': n.type} for n in result.ast]
            }

        elif action == 'get_line_info':
            line_number = request.get('line_number', 0)
            result = parser.parse(content, filename)
            info = parser.get_line_explanation(result, line_number)
            return info

        elif action == 'extract_functions':
            result = parser.parse(content, filename)
            return {
                'subroutines': [
                    {'line': s['line_number'], 'name': s['name'], 'signature': s['signature']}
                    for s in result.subroutines
                ]
            }

        elif action == 'extract_variables':
            result = parser.parse(content, filename)
            return {
                'variables': [
                    {'line': v['line_number'], 'scope': v['keyword'], 'name': v['variable']}
                    for v in result.variables
                ]
            }

        elif action == 'get_dependencies':
            result = parser.parse(content, filename)
            return {
                'modules': [
                    {'line': m['line_number'], 'type': m['type'], 'name': m['module']}
                    for m in result.modules_used
                ],
                'packages': result.packages
            }

        else:
            return {'error': f'Unknown action: {action}'}

    def _send_response(self, data: Dict, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def log_message(self, format, *args):
        """Override to add timestamp."""
        from datetime import datetime
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]} {args[1]} {args[2]}")


def run_server(port: int = 5001):
    """Run the MCP Parser Server."""
    server = HTTPServer(('0.0.0.0', port), ParserRequestHandler)
    print(f"MPC Parser Server running on port {port}")
    print(f"Health check: http://localhost:{port}/health")
    print(f"Tools: http://localhost:{port}/tools")
    print("Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopping...")
        server.server_close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MCP Parser Server')
    parser.add_argument('--port', '-p', type=int, default=5001, help='Server port')
    args = parser.parse_args()
    run_server(args.port)