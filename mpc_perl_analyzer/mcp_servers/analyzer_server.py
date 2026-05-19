"""
MCP Analyzer Server
===================
Provides Perl script analysis capabilities via MCP protocol.
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


class AnalyzerRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MCP Analyzer Server."""

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
            self._send_response({
                'status': 'ok',
                'server': 'analyzer',
                'version': '1.0.0'
            })
        elif self.path == '/tools':
            self._send_response({
                'tools': [
                    {
                        'name': 'detect_syntax_errors',
                        'description': 'Find syntax errors in Perl script',
                        'parameters': {
                            'content': {'type': 'string', 'description': 'Perl script content'}
                        }
                    },
                    {
                        'name': 'detect_deprecated_constructs',
                        'description': 'Find deprecated Perl patterns',
                        'parameters': {
                            'content': {'type': 'string', 'description': 'Perl script content'}
                        }
                    },
                    {
                        'name': 'analyze_performance',
                        'description': 'Identify performance issues',
                        'parameters': {
                            'content': {'type': 'string', 'description': 'Perl script content'}
                        }
                    },
                    {
                        'name': 'detect_eda_patterns',
                        'description': 'Find VLSI/EDA-specific patterns',
                        'parameters': {
                            'content': {'type': 'string', 'description': 'Perl script content'}
                        }
                    },
                    {
                        'name': 'get_analysis_summary',
                        'description': 'Complete analysis report',
                        'parameters': {
                            'content': {'type': 'string', 'description': 'Perl script content'},
                            'filename': {'type': 'string', 'optional': True}
                        }
                    }
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

        if action == 'detect_syntax_errors':
            syntax_issues = [i for i in result.issues if i.category in ('syntax', 'best_practice')]
            return {'syntax_issues': [
                {
                    'line': i.line_number,
                    'severity': i.severity,
                    'description': i.description,
                    'explanation': i.explanation,
                    'suggestion': i.suggestion
                } for i in syntax_issues
            ]}

        elif action == 'detect_deprecated_constructs':
            dep_issues = [i for i in result.issues if i.category in ('file_io', 'control_flow', 'operators', 'io_operations')]
            return {'deprecated_constructs': [
                {
                    'line': i.line_number,
                    'description': i.description,
                    'explanation': i.explanation,
                    'modern_code': i.modern_code,
                    'suggestion': i.suggestion
                } for i in dep_issues
            ]}

        elif action == 'analyze_performance':
            perf_issues = [i for i in result.issues if i.category == 'performance']
            return {'performance_issues': [
                {
                    'line': i.line_number,
                    'description': i.description,
                    'explanation': i.explanation,
                    'optimization': i.suggestion
                } for i in perf_issues
            ]}

        elif action == 'detect_eda_patterns':
            return {
                'eda_script_types': result.eda_script_types,
                'tcl_patterns': result.tcl_patterns,
                'vlsi_data_patterns': result.vlsi_data_patterns
            }

        elif action == 'get_analysis_summary':
            return {
                'summary': result.summary,
                'issues_count': len(result.issues),
                'issues': [
                    {
                        'line': i.line_number,
                        'severity': i.severity,
                        'category': i.category,
                        'description': i.description,
                        'suggestion': i.suggestion
                    } for i in result.issues
                ],
                'eda_analysis': {
                    'script_types': [s['description'] for s in result.eda_script_types],
                    'tcl_patterns': [t['description'] for t in result.tcl_patterns]
                }
            }

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


def run_server(port: int = 5002):
    server = HTTPServer(('0.0.0.0', port), AnalyzerRequestHandler)
    print(f"MPC Analyzer Server running on port {port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopping...")
        server.server_close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MCP Analyzer Server')
    parser.add_argument('--port', '-p', type=int, default=5002, help='Server port')
    args = parser.parse_args()
    run_server(args.port)