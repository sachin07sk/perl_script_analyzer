"""
MPC Protocol - VLSI/EDA Perl Script Analyzer
=============================================
Command-line interface for analyzing Perl scripts with
error detection, modernization suggestions, and 
human-readable PDF reports.

Usage:
    python main.py analyze <script.pl> [--output OUTPUT] [--format FORMAT]
    python main.py explain <script.pl> --line LINE_NUMBER
    python main.py line-by-line <script.pl> [--output OUTPUT]
    python main.py server [--manager | --start SERVER | --status]
    python main.py compare <old.pl> <new.pl> [--output OUTPUT]
"""

import sys
import os
import argparse
from datetime import datetime


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='MPC Protocol - VLSI/EDA Perl Script Analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py analyze script.pl
  python main.py analyze script.pl --output report.txt
  python main.py explain script.pl --line 42
  python main.py line-by-line script.pl
  python main.py server --status
  python main.py compare old_script.pl new_script.pl
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a Perl script')
    analyze_parser.add_argument('script', help='Path to Perl script')
    analyze_parser.add_argument('--output', '-o', help='Output report file path')
    analyze_parser.add_argument('--format', '-f', choices=['full', 'summary'], 
                              default='full', help='Report format')

    # Explain command (selected line)
    explain_parser = subparsers.add_parser('explain', help='Explain a specific line')
    explain_parser.add_argument('script', help='Path to Perl script')
    explain_parser.add_argument('--line', '-l', type=int, required=True, 
                               help='Line number to explain')

    # Line-by-line command
    lcl_parser = subparsers.add_parser('line-by-line', help='Generate line-by-line explanation')
    lcl_parser.add_argument('script', help='Path to Perl script')
    lcl_parser.add_argument('--output', '-o', help='Output file path')

    # Server management
    server_parser = subparsers.add_parser('server', help='Manage MCP servers')
    server_parser.add_argument('--manager', '-m', action='store_true', 
                              help='Start server manager interactive mode')
    server_parser.add_argument('--start', '-s', help='Start a server (use "all" for all servers)')
    server_parser.add_argument('--status', action='store_true', help='Show server status')

    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare two script versions')
    compare_parser.add_argument('old_script', help='Original script')
    compare_parser.add_argument('new_script', help='Modernized script')
    compare_parser.add_argument('--output', '-o', help='Output report file path')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Add src to path
    sys.path.insert(0, os.path.dirname(__file__))

    if args.command == 'analyze':
        cmd_analyze(args)
    elif args.command == 'explain':
        cmd_explain(args)
    elif args.command == 'line-by-line':
        cmd_line_by_line(args)
    elif args.command == 'server':
        cmd_server(args)
    elif args.command == 'compare':
        cmd_compare(args)


def cmd_analyze(args):
    """Handle analyze command."""
    from src.analyzer import create_analyzer
    from src.pdf_generator import create_pdf_generator

    content = read_script(args.script)
    if not content:
        print(f"Error: Cannot read script '{args.script}'")
        return

    print(f"Analyzing: {args.script}")
    print(f"Lines: {len(content.split(chr(10)))}")
    print("-" * 50)

    analyzer = create_analyzer()
    result = analyzer.analyze(content, args.script)

    # Print summary
    print(f"\nAnalysis Summary:")
    print(f"  Issues Found: {result.summary['total_issues']}")
    print(f"  ├─ Critical: {result.summary['severity_summary'].get('critical', 0)}")
    print(f"  ├─ Errors:   {result.summary['severity_summary'].get('error', 0)}")
    print(f"  ├─ Warnings: {result.summary['severity_summary'].get('warning', 0)}")
    print(f"  └─ Info:     {result.summary['severity_summary'].get('info', 0)}")
    print(f"  Subroutines: {result.summary['subroutines_count']}")
    print(f"  Modules:     {result.summary['modules_count']}")
    print(f"  Script Type: {result.summary['script_type']}")
    if result.summary['eda_tools_found']:
        print(f"  EDA Tools:   {', '.join(result.summary['eda_tools_found'])}")

    # Generate report
    if args.output:
        output_dir = os.path.dirname(args.output) or 'output'
        output_name = os.path.basename(args.output)
        os.makedirs(output_dir, exist_ok=True)
        pdf_gen = create_pdf_generator(output_dir)
        if args.format == 'full':
            report_path = pdf_gen.generate_full_report(result, output_name)
        else:
            report_path = pdf_gen.generate_line_by_line_report(result, output_name)
        print(f"\nReport saved: {report_path}")

    # Print issues
    if result.issues:
        print(f"\nIssues Found:")
        for issue in result.issues:
            icon = {'critical': '!!', 'error': '!', 'warning': '?', 'info': 'i'}.get(issue.severity, ' ')
            print(f"  [{icon}] Line {issue.line_number:4d}: {issue.description}")


def cmd_explain(args):
    """Handle explain command - explain specific line."""
    from src.analyzer import create_analyzer

    content = read_script(args.script)
    if not content:
        print(f"Error: Cannot read script '{args.script}'")
        return

    analyzer = create_analyzer()
    result = analyzer.analyze(content, args.script)

    line_info = analyzer.get_line_explanation(args.line, content)
    
    if 'error' in line_info:
        print(f"Error: {line_info['error']}")
        return

    print("=" * 60)
    print(f"LINE {line_info['line_number']} EXPLANATION")
    print("=" * 60)
    print(f"  Content:    {line_info['content']}")
    print(f"  Type:       {line_info['type']}")
    print(f"  Purpose:    {line_info.get('purpose', 'N/A')}")
    print(f"  Explanation: {line_info['explanation']}")
    
    if line_info.get('issues'):
        print(f"\n  Issues at this line:")
        for iss in line_info['issues']:
            print(f"    [{iss['severity'].upper()}] {iss['description']}")
            print(f"    Reason: {iss['explanation']}")
            if iss.get('modern_code'):
                print(f"    Modern: {iss['modern_code']}")

    if line_info.get('suggestions'):
        print(f"\n  Suggestions:")
        for s in line_info['suggestions']:
            print(f"    - {s}")

    # Show context (surrounding lines)
    print(f"\n  Context (lines {max(1, args.line-2)}-{min(len(result.parse_result.lines), args.line+2)}):")
    lines = content.split('\n')
    for i in range(max(0, args.line - 3), min(len(lines), args.line + 2)):
        line_num = i + 1
        marker = '>>>' if line_num == args.line else '   '
        print(f"  {marker} {line_num:4d}| {lines[i]}")


def cmd_line_by_line(args):
    """Handle line-by-line command."""
    from src.analyzer import create_analyzer
    from src.pdf_generator import create_pdf_generator

    content = read_script(args.script)
    if not content:
        print(f"Error: Cannot read script '{args.script}'")
        return

    print(f"Generating line-by-line explanation for: {args.script}")
    
    analyzer = create_analyzer()
    pdf_gen = create_pdf_generator('output')
    result = analyzer.analyze(content, args.script)

    output_filename = args.output or f"{os.path.splitext(os.path.basename(args.script))[0]}_line_by_line.txt"
    report_path = pdf_gen.generate_line_by_line_report(result, output_filename)
    
    print(f"  Report saved: {report_path}")
    print(f"  Lines explained: {len(result.line_explanations)}/{result.summary['total_lines']}")


def cmd_server(args):
    """Handle server management command."""
    from mcp_servers.server_manager import MCPServerManager, print_server_status

    manager = MCPServerManager()

    if args.manager:
        # Start interactive mode
        print("\nMPC Server Manager - Interactive Mode")
        print("Commands: start <server>, stop <server>, status, exit")
        print("Servers: parser, analyzer, modernizer, pdf_generator, eda_knowledge")
        try:
            while True:
                cmd = input("\n> ").strip().lower()
                if not cmd:
                    continue
                if cmd in ('exit', 'quit'):
                    manager.shutdown_all()
                    break
                elif cmd == 'status' or args.status:
                    print_server_status(manager)
                elif cmd.startswith('start '):
                    server = cmd[6:]
                    if server == 'all':
                        for s in ['parser', 'analyzer', 'modernizer', 'pdf_generator', 'eda_knowledge']:
                            manager.activate_server(s)
                    else:
                        manager.activate_server(server)
                elif cmd.startswith('stop '):
                    server = cmd[5:]
                    manager.deactivate_server(server)
                else:
                    print("Unknown command")
        except KeyboardInterrupt:
            print("\n")
            manager.shutdown_all()
    elif args.start:
        if args.start == 'all':
            for s in ['parser', 'analyzer', 'modernizer', 'pdf_generator', 'eda_knowledge']:
                manager.activate_server(s)
        else:
            manager.activate_server(args.start)
        print_server_status(manager)
    elif args.status:
        print_server_status(manager)
    else:
        print("Use --manager for interactive mode, --start <server> to start a server, or --status to show status")


def cmd_compare(args):
    """Handle compare command."""
    from src.analyzer import create_analyzer
    from src.pdf_generator import create_pdf_generator

    old_content = read_script(args.old_script)
    new_content = read_script(args.new_script)

    if not old_content or not new_content:
        print("Error: Cannot read one or both scripts")
        return

    print(f"Comparing: {args.old_script} vs {args.new_script}")

    analyzer = create_analyzer()
    old_result = analyzer.analyze(old_content, args.old_script)
    new_result = analyzer.analyze(new_content, args.new_script)

    pdf_gen = create_pdf_generator('output')
    output = args.output or f"comparison_{os.path.splitext(os.path.basename(args.old_script))[0]}.txt"
    report_path = pdf_gen.generate_comparison_report(old_result, new_result, output)

    old_issues = old_result.summary['total_issues']
    new_issues = new_result.summary['total_issues']
    improvement = old_issues - new_issues

    print(f"\nComparison Results:")
    print(f"  Original Issues:     {old_issues}")
    print(f"  Modernized Issues:   {new_issues}")
    print(f"  Issues Resolved:     {improvement}")
    if improvement > 0:
        print(f"  Improvement:         {improvement / old_issues * 100:.1f}%")
    print(f"\nReport saved: {report_path}")


def read_script(filepath: str) -> str:
    """Read a script file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None


if __name__ == '__main__':
    main()