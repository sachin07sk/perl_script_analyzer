"""
MCP Modernizer Server
=====================
Provides Perl code modernization suggestions via MCP protocol.
On-demand activation with idle timeout.
"""

import sys
import os
import json
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.analyzer import create_analyzer


class ModernizerRequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
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
        if self.path == '/health':
            self._send_response({'status': 'ok', 'server': 'modernizer', 'version': '1.0.0'})
        elif self.path == '/tools':
            self._send_response({
                'tools': [
                    {'name': 'suggest_perl_modernization', 'description': 'Perl version updates',
                     'parameters': {'content': {'type': 'string'}}},
                    {'name': 'suggest_eda_updates', 'description': 'EDA tool command updates',
                     'parameters': {'content': {'type': 'string'}}},
                    {'name': 'optimize_code', 'description': 'Performance optimization suggestions',
                     'parameters': {'content': {'type': 'string'}}},
                    {'name': 'apply_best_practices', 'description': 'Modern Perl best practices',
                     'parameters': {'content': {'type': 'string'}}},
                    {'name': 'generate_modernized_code', 'description': 'Output modernized script',
                     'parameters': {'content': {'type': 'string'}}}
                ]
            })
        else:
            self._send_response({'error': 'Not found'}, 404)

    def _handle_request(self, request: Dict) -> Dict:
        action = request.get('action', '')
        content = request.get('content', '')
        filename = request.get('filename', 'script.pl')

        analyzer = create_analyzer()
        result = analyzer.analyze(content, filename)

        if action == 'suggest_perl_modernization':
            perl_issues = [i for i in result.issues if i.category in ('file_io', 'control_flow', 'io_operations', 'best_practice')]
            return {'modernization_suggestions': [
                {
                    'line': i.line_number,
                    'issue': i.description,
                    'explanation': i.explanation,
                    'modern_code': i.modern_code,
                    'benefits': i.suggestion
                } for i in perl_issues if i.modern_code
            ]}

        elif action == 'suggest_eda_updates':
            eda_issues = [i for i in result.issues if i.category == 'eda']
            return {'eda_updates': [
                {
                    'line': i.line_number,
                    'description': i.description,
                    'explanation': i.explanation,
                    'suggestion': i.suggestion
                } for i in eda_issues
            ]}

        elif action == 'optimize_code':
            perf_issues = [i for i in result.issues if i.category == 'performance']
            return {'optimizations': [
                {
                    'line': i.line_number,
                    'description': i.description,
                    'explanation': i.explanation,
                    'optimization': i.suggestion
                } for i in perf_issues
            ]}

        elif action == 'apply_best_practices':
            bp_issues = [i for i in result.issues if i.category in ('best_practice', 'documentation', 'maintainability')]
            return {'best_practices': [
                {
                    'line': i.line_number,
                    'description': i.description,
                    'explanation': i.explanation,
                    'recommendation': i.suggestion
                } for i in bp_issues
            ]}

        elif action == 'generate_modernized_code':
            # Return script with annotations for modernization
            lines = content.split('\n')
            annotations = []
            for issue in result.issues:
                if issue.modern_code:
                    idx = issue.line_number - 1
                    if 0 <= idx < len(lines):
                        annotations.append({
                            'line': issue.line_number,
                            'original': lines[idx],
                            'modernized': issue.modern_code,
                            'reason': issue.explanation
                        })
            return {'modernizations': annotations, 'script_lines': len(lines)}

        else:
            return {'error': f'Unknown action: {action}'}

    def _send_response(self, data: Dict, status: int = 200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def log_message(self, format, *args):
        from datetime import datetime
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]} {args[1]} {args[2]}")


def run_server(port: int = 5003):
    server = HTTPServer(('0.0.0.0', port), ModernizerRequestHandler)
    print(f"MPC Modernizer Server running on port {port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopping...")
        server.server_close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MCP Modernizer Server')
    parser.add_argument('--port', '-p', type=int, default=5003, help='Server port')
    args = parser.parse_args()
    run_server(args.port)