# perl_script_analyzer
to updateing the old perl script to new script and to analysis the file and explain in nature. make suggestion of the updated perl scripts upon the industrial standed using MCP protocol backend upon


# MPC Protocol - VLSI/EDA Perl Script Analyzer

**Multi-Purpose Checker (MPC) Protocol** for analyzing, error-detecting, modernizing, and explaining Perl scripts in VLSI/EDA environments with human-readable PDF reports.

## Features

### 🔍 Error Detection
- **Syntax Errors**: Unmatched braces/parentheses detection
- **Deprecated Constructs**: Old-style open(), bareword filehandles, etc.
- **Security Vulnerabilities**: eval injection, system() command injection
- **Performance Issues**: File slurping detection

### 🏭 EDA/VLSI Analysis
- **5 EDA Tools**: Synopsys DC, PrimeTime, Cadence Innovus, Genus, Mentor Calibre
- **6 Script Types**: Synthesis, Timing Analysis, P&R, Verification, DFT, Power
- **TCL Integration**: Detection of Perl-to-TCL patterns
- **VLSI Data Patterns**: SDC, SDF, SPEF, LEF/DEF handling

### 📖 Human-Readable Explanations
- **Full Reports**: Executive summary → Overview → Issues → Line-by-line → EDA
- **Line-by-Line**: Each line explained in plain English
- **Selected Lines**: Focus on specific line numbers
- **Comparison Reports**: Before/after modernization comparison

### 🚀 MCP Servers (On-Demand)
- **5 Independent Servers** on ports 5001-5005
- **On-Demand Activation**: Servers start only when needed
- **Idle Timeout**: Auto-shutdown after configurable inactivity
- **Auto-Restart**: Failed servers restart on next request

## Project Structure

```
mpc_perl_analyzer/
├── mcp_servers/
│   ├── __init__.py                    # MCP servers package init
│   ├── server_manager.py              # On-demand server management
│   ├── parser_server.py               # MCP Parser Server (port 5001)
│   ├── analyzer_server.py             # MCP Analyzer Server (port 5002)
│   ├── modernizer_server.py           # MCP Modernizer Server (port 5003)
│   ├── pdf_server.py                  # MCP PDF Generator Server (port 5004)
│   ├── eda_knowledge_server.py        # MCP EDA Knowledge Server (port 5005)
│   └── shared/
│       ├── pattern_db.py              # Shared pattern database
│       ├── cache.py                   # Shared cache layer
│       └── utils.py                   # Shared utilities
├── src/
│   ├── __init__.py                    # Package init
│   ├── parser.py                      # Core Perl parsing logic
│   ├── analyzer.py                    # Core analysis logic
│   ├── modernizer.py                  # Core modernization logic
│   ├── pdf_generator.py               # Core PDF generation
│   ├── eda_patterns.py                # EDA pattern definitions
│   ├── perl_patterns.py               # Perl pattern definitions
│   └── utils.py                       # Utility functions
├── config/
│   ├── server_config.json             # Server configuration
│   ├── eda_tools.json                 # EDA tool configurations
│   └── perl_versions.json             # Perl version mappings
├── templates/
│   └── pdf_template.html              # PDF report template
├── tests/
│   ├── test_servers.py                # MCP server tests
│   ├── test_parser.py                 # Parser unit tests
│   ├── test_analyzer.py               # Integration tests
│   └── sample_scripts/
│       └── vlsa_timing_analysis.pl    # Sample VLSI Perl script
├── scripts/
│   ├── start_all_servers.sh           # Start all servers
│   ├── stop_all_servers.sh            # Stop all servers
│   └── check_server_status.sh         # Check server status
├── output/                            # Generated reports
├── main.py                            # CLI entry point
├── requirements.txt                   # Python dependencies
├── setup.py                           # Package setup
└── README.md                          # This file
```

## Installation

```bash
# Clone the repository
git clone https://github.com/example/mpc-perl-analyzer.git
cd mpc_perl_analyzer

# No additional dependencies needed - uses Python standard library only!
```

## Quick Start

### 1. Analyze a Perl Script

```bash
python main.py analyze tests/sample_scripts/vlsa_timing_analysis.pl
```

Output:
```
Analyzing: tests/sample_scripts/vlsa_timing_analysis.pl
Lines: 153
--------------------------------------------------
Analysis Summary:
  Issues Found: 17
  ├─ Critical: 1
  ├─ Errors:   1
  ├─ Warnings: 3
  └─ Info:     12
  Script Type: VLSI/EDA
  EDA Tools:   Synopsys DC / Cadence Genus, Synopsys PrimeTime / Cadence Tempus, ...
```

### 2. Explain a Specific Line

```bash
python main.py explain tests/sample_scripts/vlsa_timing_analysis.pl --line 18
```

Output:
```
LINE 18 EXPLANATION
============================================================
  Content:    open(REPORT, "< $ARGV[0]") or die "Cannot open $ARGV[0]";
  Type:       io_operation
  Purpose:    Input/Output
  Explanation: This line performs input/output operations.
  Issues at this line:
    [WARNING] Old-style 2-argument open with bareword filehandle
    Fix: Use: open(my $fh, '<', $filename) or die ...
```

### 3. Generate Line-by-Line Report

```bash
python main.py line-by-line tests/sample_scripts/vlsa_timing_analysis.pl
```

### 4. Manage MCP Servers

```bash
# Interactive server manager
python main.py server --manager

# Check server status
python main.py server --status
```

### 5. Compare Two Script Versions

```bash
python main.py compare old_script.pl new_script.pl
```

## MCP Server Management

The system includes 5 MCP (Model Context Protocol) servers that activate on-demand:

| Server | Port | Purpose | Idle Timeout |
|--------|------|---------|-------------|
| Parser Server | 5001 | Parse Perl scripts into AST | 15 min |
| Analyzer Server | 5002 | Error detection & analysis | 15 min |
| Modernizer Server | 5003 | Code modernization suggestions | 20 min |
| PDF Generator | 5004 | Report generation | 30 min |
| EDA Knowledge | 5005 | EDA tool pattern knowledge | 10 min |

Servers automatically shutdown after their idle timeout to save resources.

## API Usage (MCP Protocol)

Each MCP server exposes a REST-like API:

```bash
# Health check
curl http://localhost:5001/health

# List available tools
curl http://localhost:5001/tools

# Analyze a script (POST)
curl -X POST http://localhost:5002/ -H "Content-Type: application/json" \
  -d '{"action": "get_analysis_summary", "content": "#!/usr/bin/perl\n..."}'
```

## Test Suite

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test files
python tests/test_parser.py
python tests/test_analyzer.py
python tests/test_servers.py
```

## Requirements

- **Python 3.8+** (standard library only - no external dependencies required)
- Optional: `reportlab` for enhanced PDF output
- Optional: `pytest` for running tests

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details.

## Support

For issues and feature requests, please use the GitHub Issues page.
