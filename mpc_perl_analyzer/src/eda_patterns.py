"""
EDA Patterns Database for VLSI Script Analysis
==============================================
Patterns for detecting EDA (Electronic Design Automation) tool commands,
TCL integration patterns, VLSI-specific code constructs,
and providing modernization suggestions.
"""

from typing import List, Dict, Any


# ============================================================
# EDA Tool Command Patterns
# ============================================================

EDA_TOOL_PATTERNS = {
    'synopsys_dc': {
        'name': 'Synopsys Design Compiler',
        'commands': [
            'dc_shell', 'analyze', 'elaborate', 'compile', 'write -f ddc',
            'write -f verilog', 'write_sdf', 'write_sdc', 'report_timing',
            'report_area', 'report_power', 'report_qor', 'current_design',
            'link', 'uniquify', 'set_dont_touch', 'set_dont_use',
            'set_max_delay', 'set_min_delay', 'set_input_delay',
            'set_output_delay', 'set_clock', 'set_clock_latency',
            'set_clock_uncertainty', 'set_clock_transition',
            'set_load', 'set_fanout_load', 'set_max_area',
            'set_max_fanout', 'set_max_transition', 'set_operating_conditions',
            'set_wire_load_model', 'set_wire_load_mode'
        ],
        'modern_alternative': 'Genus Synthesis Tool',
        'version_updates': {
            'dc_shell-t': 'genus -legacy_ui',
            'analyze -library WORK -format verilog': 'read_hdl -library WORK',
            'compile -map_effort high': 'syn_generic; syn_map -effort high'
        }
    },
    'synopsys_pt': {
        'name': 'Synopsys PrimeTime',
        'commands': [
            'pt_shell', 'read_verilog', 'read_vhdl', 'read_db',
            'read_sdc', 'read_spef', 'read_parasitics',
            'report_timing', 'report_analysis_coverage',
            'report_constraint', 'report_min_pulse_width',
            'report_cppr', 'report_clock_gating',
            'update_timing', 'set_operating_conditions',
            'set_analysis_mode', 'set_timing_derate',
            'set_clock_latency', 'set_clock_uncertainty'
        ],
        'modern_alternative': 'PrimeTime 2020+',
        'version_updates': {
            'pt_shell': 'primetime_shell',
            'report_timing -max_paths': 'report_timing -nworst'
        }
    },
    'cadence_innovus': {
        'name': 'Cadence Innovus',
        'commands': [
            'innovus', 'encounter', 'floorplan', 'place_opt_design',
            'ccopt_design', 'route_design', 'opt_design',
            'time_design', 'report_timing', 'report_qor',
            'report_power', 'report_area', 'defIn', 'lefIn',
            'verilogIn', 'placeDesign', 'routeDesign',
            'addFiller', 'addWellTap', 'setDrawView',
            'setAnalysisMode', 'setOptMode'
        ],
        'modern_alternative': 'Innovus 21+',
        'version_updates': {
            'encounter': 'innovus',
            'setMultiCpuUsage': 'set_host_options -max_cores'
        }
    },
    'cadence_genus': {
        'name': 'Cadence Genus',
        'commands': [
            'genus', 'read_hdl', 'read_db', 'read_sdc',
            'syn_generic', 'syn_map', 'syn_opt',
            'report_timing', 'report_area', 'report_power',
            'write_hdl', 'write_sdc', 'write_db'
        ],
        'modern_alternative': 'Genus 21+',
        'version_updates': {
            'read_hdl -v2001': 'read_hdl -language v2001'
        }
    },
    'mentor_calibre': {
        'name': 'Mentor/Siemens Calibre',
        'commands': [
            'calibre', 'calibre -drc', 'calibre -lvs',
            'calibre -xrc', 'calibre_64', 'drc_rules',
            'lvs_rules', 'PEX', 'nmLVS', 'nmDRC'
        ],
        'modern_alternative': 'Calibre 2021+',
        'version_updates': {}
    }
}


# EDA Script Patterns for detection
EDA_SCRIPT_PATTERNS = [
    {
        'id': 'EDA-SYNTHESIS-SCRIPT',
        'category': 'synthesis',
        'pattern': r'(?:dc_shell|synopsys|analyze.*\-library|compile|syn_generic|syn_map)',
        'description': 'Synthesis script pattern detected',
        'eda_tool': 'Synopsys DC / Cadence Genus',
        'explanation': (
            "This script contains synthesis tool commands. Synthesis converts "
            "RTL (Verilog/VHDL) code into gate-level netlists. Understanding "
            "the synthesis flow is crucial for timing closure and area optimization."
        ),
        'common_issues': [
            'Incorrect constraint application order',
            'Missing clock definitions',
            'Improper compile strategies'
        ]
    },
    {
        'id': 'EDA-TIMING-ANALYSIS',
        'category': 'timing',
        'pattern': r'(?:report_timing|pt_shell|primetime|update_timing|set_timing_derate|read_sdc)',
        'description': 'Timing analysis script pattern',
        'eda_tool': 'Synopsys PrimeTime / Cadence Tempus',
        'explanation': (
            "This script performs static timing analysis (STA). Timing analysis "
            "verifies that all paths in the design meet timing constraints "
            "(setup, hold, recovery, removal)."
        ),
        'common_issues': [
            'Missing timing exceptions',
            'Incorrect clock definitions',
            'Improper OCV derating factors'
        ]
    },
    {
        'id': 'EDA-PNR-SCRIPT',
        'category': 'physical_design',
        'pattern': r'(?:floorplan|place_design|route_design|innovus|encounter|icc2|ccopt)',
        'description': 'Physical design (P&R) script pattern',
        'eda_tool': 'Cadence Innovus / Synopsys ICC2',
        'explanation': (
            "This script manages the physical design flow: floorplanning, "
            "placement, clock tree synthesis (CTS), and routing. Physical "
            "design is the process of translating a synthesized netlist into "
            "a physical layout."
        ),
        'common_issues': [
            'Incorrect floorplan aspect ratio',
            'Poor power grid design',
            'Insufficient routing resources'
        ]
    },
    {
        'id': 'EDA-VERIFICATION',
        'category': 'verification',
        'pattern': r'(?:calibre|drc|lvs|nmLVS|nmDRC|verification|formal|formality)',
        'description': 'Verification script pattern (DRC/LVS)',
        'eda_tool': 'Siemens Calibre / Synopsys ICV',
        'explanation': (
            "This script runs design rule checking (DRC) and layout vs. "
            "schematic (LVS) verification. These checks ensure that the "
            "physical layout meets manufacturing rules and matches the "
            "original circuit design."
        ),
        'common_issues': [
            'DRC violations due to incorrect spacing',
            'LVS mismatches from improper connections',
            'Missing density fill patterns'
        ]
    },
    {
        'id': 'EDA-DFT-SCRIPT',
        'category': 'test',
        'pattern': r'(?:dft|scan|atpg|tetramax|tessent|insert_scan|boundary_scan)',
        'description': 'Design-for-Test (DFT) script pattern',
        'eda_tool': 'Synopsys DFT Compiler / Siemens Tessent',
        'explanation': (
            "This script implements design-for-test features like scan chains, "
            "built-in self-test (BIST), and boundary scan. DFT enables "
            "manufacturing test to detect fabrication defects."
        ),
        'common_issues': [
            'Incomplete scan chain stitching',
            'Missing test points',
            'ATPG coverage below target'
        ]
    },
    {
        'id': 'EDA-POWER-ANALYSIS',
        'category': 'power',
        'pattern': r'(?:report_power|set_switching_activity|read_vcd|read_saif|set_power_estimation)',
        'description': 'Power analysis script pattern',
        'eda_tool': 'Synopsys PrimePower / Cadence Joules',
        'explanation': (
            "This script performs power analysis to estimate dynamic and "
            "static power consumption. Power analysis is critical for meeting "
            "battery life and thermal constraints."
        ),
        'common_issues': [
            'Missing switching activity data',
            'Incorrect toggle rates',
            'Incomplete power domain definitions'
        ]
    }
]


# ============================================================
# TCL Integration Patterns
# ============================================================

TCL_PATTERNS = [
    {
        'id': 'TCL-EXEC',
        'pattern': r'(?:system|exec|qx)\s*\(?\s*["\']\s*\$?\w+\s*(?:tcl|tclsh)',
        'description': 'TCL execution from Perl',
        'explanation': (
            "This script launches a TCL shell (tclsh) from Perl to execute "
            "EDA tool commands. This is common in VLSI environments where "
            "Perl scripts orchestrate multiple EDA tool runs."
        ),
        'modern_suggestion': (
            "Consider using Perl's Expect module for interactive TCL sessions, "
            "or use TCL packages directly via IPC for better performance."
        )
    },
    {
        'id': 'TCL-GENERATION',
        'pattern': r'(?:print|printf|say)\s+\w+\s*["\'].*?(?:dc_shell|innovus|genus|pt_shell|calibre)',
        'description': 'TCL script generation from Perl',
        'explanation': (
            "This Perl script generates TCL commands that will be passed to "
            "an EDA tool. This pattern generates run scripts dynamically "
            "based on input parameters."
        ),
        'modern_suggestion': (
            "Use template-based TCL generation with configuration files "
            "for better maintainability and version control."
        )
    },
    {
        'id': 'TCL-FILE-WRITE',
        'pattern': r'open\s*\(?\s*\w+\s*,\s*["\']>[^"\']*\.tcl',
        'description': 'Writing TCL files from Perl',
        'explanation': (
            "This script writes a TCL script file to disk, which will later "
            "be executed by an EDA tool. This is used for generating "
            "tool-specific run scripts."
        ),
        'modern_suggestion': (
            "Use a dedicated TCL template system with parameter substitution "
            "for cleaner code separation."
        )
    }
]


# ============================================================
# VLSI-Specific Data Analysis Patterns
# ============================================================

VLSI_DATA_PATTERNS = [
    {
        'id': 'VLSI-STDCELL-HANDLING',
        'pattern': r'(?:std_cell|standard_cell|liberty|\.lib|\.db)',
        'description': 'Standard cell library handling',
        'explanation': (
            "This code handles standard cell library files (Liberty format .lib "
            "or compiled .db). These libraries contain timing, power, and "
            "logical information about standard cells used in the design."
        )
    },
    {
        'id': 'VLSI-LEF-DEF',
        'pattern': r'(?:\.lef|\.def|macro.*pin|layer.*width|site.*class)',
        'description': 'Physical library (LEF/DEF) processing',
        'explanation': (
            "This code processes LEF (Library Exchange Format) and DEF "
            "(Design Exchange Format) files for physical design. LEF describes "
            "cell abstract views, while DEF describes the physical design database."
        )
    },
    {
        'id': 'VLSI-SDC-CONSTRAINTS',
        'pattern': r'(?:\.sdc|create_clock|set_input_delay|set_output_delay|set_max_delay|set_false_path|set_multicycle_path)',
        'description': 'SDC timing constraints handling',
        'explanation': (
            "This code handles SDC (Synopsys Design Constraints) format timing "
            "constraints. SDC files define clock definitions, I/O delays, "
            "timing exceptions, and operating conditions for synthesis and STA."
        )
    },
    {
        'id': 'VLSI-SDF',
        'pattern': r'(?:\.sdf|INTERCONNECT|PATHPULSE|TIMINGCHECK|SETUPHOLD)',
        'description': 'SDF (Standard Delay Format) processing',
        'explanation': (
            "This code processes SDF (Standard Delay Format) files that contain "
            "timing delay information for gate-level simulation. SDF provides "
            "cell and interconnect delays for pre- and post-layout simulation."
        )
    },
    {
        'id': 'VLSI-SPEED',
        'pattern': r'(?:\.spef|\.spf|parasitics|coupled|RCMX)',
        'description': 'SPEF parasitic extraction data',
        'explanation': (
            "This code handles SPEF (Standard Parasitic Exchange Format) files "
            "that contain extracted resistance and capacitance (RC) parasitics "
            "after layout. These are essential for accurate post-layout analysis."
        )
    }
]


# ============================================================
# EDA File Format Detection
# ============================================================

EDA_FILE_FORMATS = {
    'verilog': {
        'extensions': ['.v', '.vh', '.verilog'],
        'description': 'Verilog HDL - Hardware Description Language',
        'detection_pattern': r'(?:module\s+\w+|endmodule|input\s+|output\s+|wire\s+|reg\s+)'
    },
    'vhdl': {
        'extensions': ['.vhd', '.vhdl'],
        'description': 'VHDL - VHSIC Hardware Description Language',
        'detection_pattern': r'(?:entity\s+|architecture\s+of|process\s*\(|signal\s+)'
    },
    'systemverilog': {
        'extensions': ['.sv', '.svh'],
        'description': 'SystemVerilog - Enhanced HDL',
        'detection_pattern': r'(?:always_ff|always_comb|always_latch|interface\s+|modport|clocking)'
    },
    'liberty': {
        'extensions': ['.lib', '.db'],
        'description': 'Liberty library format for standard cells',
        'detection_pattern': r'(?:library\s*\(|cell\s*\(|pin\s*\(|timing\s*\()'
    },
    'sdc': {
        'extensions': ['.sdc'],
        'description': 'Synopsys Design Constraints',
        'detection_pattern': r'(?:create_clock|set_input_delay|set_output_delay|set_false_path)'
    },
    'sdf': {
        'extensions': ['.sdf'],
        'description': 'Standard Delay Format',
        'detection_pattern': r'(?:\(DELAY|INTERCONNECT|PATHPULSE|TIMINGCHECK)'
    },
    'spef': {
        'extensions': ['.spef', '.spf'],
        'description': 'Standard Parasitic Exchange Format',
        'detection_pattern': r'(?:D_NET|R_NET|*RC)'
    }
}


def get_eda_tool_patterns(tool_name: str = None) -> Dict:
    """Get EDA tool patterns, optionally filtered by tool name."""
    if tool_name:
        return {tool_name: EDA_TOOL_PATTERNS.get(tool_name, {})}
    return EDA_TOOL_PATTERNS


def detect_eda_script_type(content: str) -> List[Dict]:
    """
    Detect EDA script types present in the content.

    Args:
        content: Script content to analyze

    Returns:
        List of detected EDA script types with details
    """
    detected = []
    for pattern in EDA_SCRIPT_PATTERNS:
        if __import__('re').search(pattern['pattern'], content, __import__('re').IGNORECASE):
            detected.append({
                'id': pattern['id'],
                'category': pattern['category'],
                'description': pattern['description'],
                'eda_tool': pattern['eda_tool'],
                'explanation': pattern['explanation'],
                'common_issues': pattern['common_issues']
            })
    return detected


def detect_tcl_integration(content: str) -> List[Dict]:
    """
    Detect TCL integration patterns in Perl script.

    Args:
        content: Script content to analyze

    Returns:
        List of detected TCL patterns
    """
    import re
    detected = []
    for pattern in TCL_PATTERNS:
        if re.search(pattern['pattern'], content, re.IGNORECASE):
            detected.append({
                'id': pattern['id'],
                'description': pattern['description'],
                'explanation': pattern['explanation'],
                'modern_suggestion': pattern['modern_suggestion']
            })
    return detected


def detect_vlsi_data_patterns(content: str) -> List[Dict]:
    """
    Detect VLSI-specific data patterns in the script.

    Args:
        content: Script content to analyze

    Returns:
        List of detected VLSI patterns
    """
    import re
    detected = []
    for pattern in VLSI_DATA_PATTERNS:
        if re.search(pattern['pattern'], content, re.IGNORECASE):
            detected.append({
                'id': pattern['id'],
                'description': pattern['description'],
                'explanation': pattern['explanation']
            })
    return detected


def get_eda_tool_update(old_command: str, tool: str) -> Dict:
    """
    Get modernization suggestion for an EDA command.

    Args:
        old_command: The old EDA command
        tool: The EDA tool name

    Returns:
        Dict with old command, new command, and explanation
    """
    tool_data = EDA_TOOL_PATTERNS.get(tool, {})
    updates = tool_data.get('version_updates', {})

    for old, new in updates.items():
        if old in old_command:
            return {
                'old': old_command,
                'new': old_command.replace(old, new),
                'tool': tool_data.get('name', tool),
                'explanation': f"This command has been updated in newer versions. "
                              f"Use '{new}' instead of '{old}' for "
                              f"{tool_data.get('name', tool)}."
            }

    return {
        'old': old_command,
        'new': None,
        'tool': tool_data.get('name', tool),
        'explanation': f"No specific update found for this command in {tool_data.get('name', tool)}."
    }