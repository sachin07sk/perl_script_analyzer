"""
MCP EDA Knowledge Server
========================
Provides EDA/VLSI pattern knowledge base via MCP protocol.
On-demand activation with idle timeout.
"""

import sys
import os
import json
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.eda_patterns import (
    get_eda_tool_patterns, detect_eda_script_type,
    detect_tcl_integration, detect_vlsi_data_patterns,
    EDA_TOOL_PATTERNS, EDA_FILE_FORMATS
)


class EDAKnowledgeRequestHandler(BaseHTTPRequestHandler):

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
            self._send_response({'status': 'ok', 'server': 'eda_knowledge', 'version': '1.0.0'})
        elif self.path == '/tools':
            self._send_response({
                'tools': [
                    {'name': 'get_eda_tool_patterns',
                     'description': 'Get patterns for specific EDA tool',
                     'parameters': {'tool_name': {'type': 'string', 'optional': True}}},
                    {'name': 'get_tcl_integration_patterns',
                     'description': 'Get TCL integration patterns',
                     'parameters': {}},
                    {'name': 'search_vlsi_patterns',
                     'description': 'Search VLSI-specific patterns',
                     'parameters': {'keyword': {'type': 'string'}}},
                    {'name': 'get_tool_command_updates',
                     'description': 'Get updated commands for EDA tools',
                     'parameters': {'tool_name': {'type': 'string'}, 'command': {'type': 'string'}}},
                    {'name': 'detect_eda_content',
                     'description': 'Detect EDA patterns in content',
                     'parameters': {'content': {'type': 'string'}}}
                ]
            })
        else:
            self._send_response({'error': 'Not found'}, 404)

    def _handle_request(self, request: Dict) -> Dict:
        action = request.get('action', '')
        content = request.get('content', '')
        tool_name = request.get('tool_name', '')
        command = request.get('command', '')
        keyword = request.get('keyword', '')
        
        if action == 'get_eda_tool_patterns':
            patterns = get_eda_tool_patterns(tool_name if tool_name else None)
            result = {}
            for name, info in patterns.items():
                result[name] = {
                    'name': info.get('name'),
                    'modern_alternative': info.get('modern_alternative'),
                    'commands_count': len(info.get('commands', [])),
                    'commands': info.get('commands', [])[:10],  # Limit to 10
                    'updates_count': len(info.get('version_updates', {}))
                }
            return {'tools': result}

        elif action == 'get_tcl_integration_patterns':
            from src.eda_patterns import TCL_PATTERNS
            return {'tcl_patterns': TCL_PATTERNS}

        elif action == 'search_vlsi_patterns':
            from src.eda_patterns import VLSI_DATA_PATTERNS
            results = [p for p in VLSI_DATA_PATTERNS if keyword.lower() in p['description'].lower()]
            return {'results': results if results else VLSI_DATA_PATTERNS[:5]}

        elif action == 'get_tool_command_updates':
            from src.eda_patterns import get_eda_tool_update
            result = get_eda_tool_update(command, tool_name)
            return result

        elif action == 'detect_eda_content':
            eda_types = detect_eda_script_type(content)
            tcl_patterns = detect_tcl_integration(content)
            vlsi_patterns = detect_vlsi_data_patterns(content)
            
            # Detect file formats referenced
            import re
            file_formats_detected = []
            for fmt_name, fmt_info in EDA_FILE_FORMATS.items():
                if re.search(fmt_info['detection_pattern'], content, re.IGNORECASE):
                    file_formats_detected.append({
                        'format': fmt_name,
                        'description': fmt_info['description']
                    })
            
            return {
                'eda_script_types': [
                    {'category': e['category'], 'tool': e['eda_tool'], 'description': e['description']}
                    for e in eda_types
                ],
                'tcl_patterns': [{'description': t['description']} for t in tcl_patterns],
                'vlsi_data_patterns': [{'description': v['description']} for v in vlsi_patterns],
                'file_formats_detected': file_formats_detected
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


def run_server(port: int = 5005):
    server = HTTPServer(('0.0.0.0', port), EDAKnowledgeRequestHandler)
    print(f"MPC EDA Knowledge Server running on port {port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopping...")
        server.server_close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MCP EDA Knowledge Server')
    parser.add_argument('--port', '-p', type=int, default=5005, help='Server port')
    args = parser.parse_args()
    run_server(args.port)