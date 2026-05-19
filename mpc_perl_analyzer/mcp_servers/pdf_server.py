"""
MCP PDF Generator Server
========================
Provides PDF report generation capabilities via MCP protocol.
On-demand activation with idle timeout.
"""

import sys
import json
import argparse
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.analyzer import create_analyzer
from src.pdf_generator import create_pdf_generator


class PDFRequestHandler(BaseHTTPRequestHandler):

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
            self._send_response({'status': 'ok', 'server': 'pdf_generator', 'version': '1.0.0'})
        elif self.path == '/tools':
            self._send_response({
                'tools': [
                    {'name': 'generate_full_report', 'description': 'Complete PDF report',
                     'parameters': {'content': {'type': 'string'}, 'filename': {'type': 'string', 'optional': True}}},
                    {'name': 'generate_line_by_line_report', 'description': 'Line-by-line PDF',
                     'parameters': {'content': {'type': 'string'}}},
                    {'name': 'generate_selected_lines_report', 'description': 'Selected lines report',
                     'parameters': {'content': {'type': 'string'}, 'line_numbers': {'type': 'array', 'items': {'type': 'integer'}}}},
                    {'name': 'generate_comparison_report', 'description': 'Before/after comparison',
                     'parameters': {'old_content': {'type': 'string'}, 'new_content': {'type': 'string'}}}
                ]
            })
        else:
            self._send_response({'error': 'Not found'}, 404)

    def _handle_request(self, request: Dict) -> Dict:
        action = request.get('action', '')
        content = request.get('content', '')
        filename = request.get('filename', 'script.pl')
        output_dir = request.get('output_dir', 'output')

        analyzer = create_analyzer()
        result = analyzer.analyze(content, filename)
        pdf_gen = create_pdf_generator(output_dir)

        if action == 'generate_full_report':
            report_path = pdf_gen.generate_full_report(result, filename)
            return {
                'status': 'success',
                'report_path': report_path,
                'report_type': 'full',
                'summary': result.summary,
                'issues_count': len(result.issues)
            }

        elif action == 'generate_line_by_line_report':
            report_path = pdf_gen.generate_line_by_line_report(result, filename)
            return {
                'status': 'success',
                'report_path': report_path,
                'report_type': 'line_by_line',
                'total_explanations': len(result.line_explanations)
            }

        elif action == 'generate_selected_lines_report':
            line_numbers = request.get('line_numbers', [])
            if not line_numbers:
                return {'error': 'line_numbers required'}
            report_path = pdf_gen.generate_selected_lines_report(result, line_numbers, filename)
            return {
                'status': 'success',
                'report_path': report_path,
                'report_type': 'selected_lines',
                'selected_lines': line_numbers,
                'found_lines': len([l for l in result.line_explanations if l.line_number in line_numbers])
            }

        elif action == 'generate_comparison_report':
            old_content = request.get('old_content', '')
            new_content = request.get('new_content', '')
            if not old_content or not new_content:
                return {'error': 'old_content and new_content required'}
            
            old_result = analyzer.analyze(old_content, 'old_' + filename)
            new_result = analyzer.analyze(new_content, 'new_' + filename)
            report_path = pdf_gen.generate_comparison_report(old_result, new_result, filename)
            return {
                'status': 'success',
                'report_path': report_path,
                'report_type': 'comparison',
                'old_issues': len(old_result.issues),
                'new_issues': len(new_result.issues)
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


def run_server(port: int = 5004):
    server = HTTPServer(('0.0.0.0', port), PDFRequestHandler)
    print(f"MPC PDF Generator Server running on port {port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopping...")
        server.server_close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MCP PDF Generator Server')
    parser.add_argument('--port', '-p', type=int, default=5004, help='Server port')
    args = parser.parse_args()
    run_server(args.port)