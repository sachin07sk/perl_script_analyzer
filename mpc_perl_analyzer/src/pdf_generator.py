"""
PDF Report Generator Module
===========================
Generates comprehensive PDF reports with full script explanations,
line-by-line analysis, and modernization suggestions in 
human-readable English format.
"""

import os
from typing import List, Dict, Optional
from datetime import datetime


class PDFReportGenerator:
    """
    Generates PDF reports for Perl script analysis with various
    levels of detail: full, line-by-line, or selected lines.
    Uses a text-based approach that can be enhanced with
    proper PDF libraries like ReportLab.
    """

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_full_report(self, analysis_result, output_filename: str = None) -> str:
        """
        Generate comprehensive full report as a structured text file
        that can be converted to PDF.

        Args:
            analysis_result: AnalysisResult from PerlAnalyzer
            output_filename: Optional custom filename

        Returns:
            Path to the generated report file
        """
        if not output_filename:
            base = os.path.splitext(analysis_result.filename)[0]
            output_filename = f"{base}_analysis_report.txt"

        output_path = os.path.join(self.output_dir, output_filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            self._write_header(f, analysis_result)
            self._write_summary(f, analysis_result)
            self._write_script_overview(f, analysis_result)
            self._write_issues_section(f, analysis_result)
            self._write_line_by_line_explanations(f, analysis_result)
            self._write_eda_analysis(f, analysis_result)
            self._write_modernization_suggestions(f, analysis_result)
            self._write_footer(f, analysis_result)

        return output_path

    def generate_line_by_line_report(self, analysis_result, output_filename: str = None) -> str:
        """
        Generate a report focused on line-by-line explanations.

        Args:
            analysis_result: AnalysisResult from PerlAnalyzer
            output_filename: Optional custom filename

        Returns:
            Path to generated report file
        """
        if not output_filename:
            base = os.path.splitext(analysis_result.filename)[0]
            output_filename = f"{base}_line_by_line.txt"

        output_path = os.path.join(self.output_dir, output_filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"LINE-BY-LINE SCRIPT EXPLANATION\n")
            f.write(f"Script: {analysis_result.filename}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")

            for line_exp in analysis_result.line_explanations:
                f.write("-" * 70 + "\n")
                f.write(f"Line {line_exp.line_number:4d} | {line_exp.content}\n")
                f.write("-" * 70 + "\n")
                f.write(f"  Type    : {line_exp.ast_type}\n")
                f.write(f"  Purpose : {line_exp.purpose}\n")
                f.write(f"  Explanation:\n")
                f.write(f"    {line_exp.plain_english}\n\n")

                if line_exp.related_issues:
                    f.write("  Issues Found:\n")
                    for iss in line_exp.related_issues:
                        f.write(f"    [{iss.severity.upper()}] {iss.description}\n")
                        f.write(f"    Suggestion: {iss.suggestion}\n")
                        if iss.modern_code:
                            f.write(f"    Modern Code: {iss.modern_code}\n")
                        f.write("\n")

                if line_exp.suggestions:
                    f.write("  Suggestions:\n")
                    for s in line_exp.suggestions:
                        f.write(f"    - {s}\n")
                    f.write("\n")

        return output_path

    def generate_selected_lines_report(self, analysis_result, line_numbers: List[int], 
                                        output_filename: str = None) -> str:
        """
        Generate a report for selected specific lines.

        Args:
            analysis_result: AnalysisResult from PerlAnalyzer
            line_numbers: List of line numbers to explain
            output_filename: Optional custom filename

        Returns:
            Path to generated report file
        """
        if not output_filename:
            base = os.path.splitext(analysis_result.filename)[0]
            output_filename = f"{base}_selected_lines.txt"

        output_path = os.path.join(self.output_dir, output_filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"SELECTED LINES EXPLANATION\n")
            f.write(f"Script: {analysis_result.filename}\n")
            f.write(f"Selected Lines: {', '.join(str(ln) for ln in sorted(line_numbers))}\n")
            f.write("=" * 80 + "\n\n")

            for line_exp in analysis_result.line_explanations:
                if line_exp.line_number in line_numbers:
                    f.write("-" * 70 + "\n")
                    f.write(f"Line {line_exp.line_number:4d} | {line_exp.content}\n")
                    f.write("-" * 70 + "\n")
                    f.write(f"  Type      : {line_exp.ast_type}\n")
                    f.write(f"  Purpose   : {line_exp.purpose}\n")
                    f.write(f"  Explanation:\n")
                    f.write(f"    {line_exp.plain_english}\n\n")

                    if line_exp.related_issues:
                        f.write("  Issues Found:\n")
                        for iss in line_exp.related_issues:
                            f.write(f"    [{iss.severity.upper()}] {iss.description}\n")
                            f.write(f"    Why: {iss.explanation}\n")
                            f.write(f"    Fix: {iss.suggestion}\n")
                            if iss.modern_code:
                                f.write(f"    Code: {iss.modern_code}\n")
                            f.write("\n")

                    if line_exp.suggestions:
                        f.write("  Suggestions:\n")
                        for s in line_exp.suggestions:
                            f.write(f"    - {s}\n")
                        f.write("\n")

        return output_path

    def generate_comparison_report(self, old_analysis, new_analysis, 
                                    output_filename: str = None) -> str:
        """
        Generate a comparison report between old and new script versions.

        Args:
            old_analysis: AnalysisResult of original script
            new_analysis: AnalysisResult of modernized script
            output_filename: Optional custom filename

        Returns:
            Path to generated report file
        """
        if not output_filename:
            base = os.path.splitext(old_analysis.filename)[0]
            output_filename = f"{base}_comparison.txt"

        output_path = os.path.join(self.output_dir, output_filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("SCRIPT MODERNIZATION COMPARISON REPORT\n")
            f.write(f"Original: {old_analysis.filename}\n")
            f.write(f"Modernized: {new_analysis.filename}\n")
            f.write("=" * 80 + "\n\n")

            # Compare statistics
            old_issues = old_analysis.summary['total_issues']
            new_issues = new_analysis.summary['total_issues']
            improvement = old_issues - new_issues

            f.write("IMPROVEMENT SUMMARY\n")
            f.write("-" * 40 + "\n")
            f.write(f"  Original Issues    : {old_issues}\n")
            f.write(f"  Modernized Issues  : {new_issues}\n")
            f.write(f"  Issues Resolved    : {improvement}\n\n")

            # Compare issues
            if improvement > 0:
                f.write("RESOLVED ISSUES\n")
                f.write("-" * 40 + "\n")
                old_issue_ids = {i.pattern_id: i for i in old_analysis.issues}
                new_issue_ids = {i.pattern_id: i for i in new_analysis.issues}

                for pid, issue in old_issue_ids.items():
                    if pid not in new_issue_ids:
                        f.write(f"  [+] Resolved: {issue.description}\n")
                        f.write(f"      Fixed by: {issue.suggestion}\n\n")

                for pid, issue in new_issue_ids.items():
                    if pid not in old_issue_ids:
                        f.write(f"  [!] New: {issue.description}\n")
                        f.write(f"      Suggestion: {issue.suggestion}\n\n")

        return output_path

    def _write_header(self, f, result):
        """Write report header."""
        f.write("=" * 80 + "\n")
        f.write(f"                    PERL SCRIPT ANALYSIS REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"  Script      : {result.filename}\n")
        f.write(f"  Analyzed On : {result.analysis_time}\n")
        f.write(f"  Total Lines : {result.summary['total_lines']}\n\n")

    def _write_summary(self, f, result):
        """Write executive summary section."""
        f.write("=" * 80 + "\n")
        f.write("1. EXECUTIVE SUMMARY\n")
        f.write("=" * 80 + "\n\n")

        summary = result.summary

        f.write(f"  Script Type       : {summary['script_type']}\n")
        if summary['eda_tools_found']:
            f.write(f"  EDA Tools Detected : {', '.join(summary['eda_tools_found'])}\n")
        f.write(f"  Total Issues      : {summary['total_issues']}\n")
        f.write(f"  ├─ Critical       : {summary['severity_summary'].get('critical', 0)}\n")
        f.write(f"  ├─ Errors         : {summary['severity_summary'].get('error', 0)}\n")
        f.write(f"  ├─ Warnings       : {summary['severity_summary'].get('warning', 0)}\n")
        f.write(f"  └─ Info           : {summary['severity_summary'].get('info', 0)}\n\n")

        f.write(f"  Modules Used      : {summary['modules_count']}\n")
        f.write(f"  Subroutines       : {summary['subroutines_count']}\n")
        f.write(f"  Variables         : {summary['variables_count']}\n")
        f.write(f"  Best Practices    : ")
        if summary['has_strict'] and summary['has_warnings']:
            f.write("Good (strict + warnings enabled)\n\n")
        elif summary['has_strict']:
            f.write("Fair (strict enabled, missing warnings)\n\n")
        else:
            f.write("Poor (missing strict and warnings)\n\n")

        # Issues by category
        if summary['category_summary']:
            f.write("  Issues by Category:\n")
            for cat, count in sorted(summary['category_summary'].items()):
                f.write(f"    - {cat}: {count}\n")
            f.write("\n")

    def _write_script_overview(self, f, result):
        """Write script overview section."""
        f.write("=" * 80 + "\n")
        f.write("2. SCRIPT OVERVIEW\n")
        f.write("=" * 80 + "\n\n")

        # Shebang
        if result.parse_result.shebang:
            f.write(f"  Interpreter : {result.parse_result.shebang}\n\n")

        # Modules
        if result.parse_result.modules_used:
            f.write("  Modules Used:\n")
            for mod in result.parse_result.modules_used:
                f.write(f"    Line {mod['line_number']:4d}: {mod['type']} {mod['module']}\n")
            f.write("\n")

        # Subroutines
        if result.parse_result.subroutines:
            f.write("  Subroutines Defined:\n")
            for sub in result.parse_result.subroutines:
                f.write(f"    Line {sub['line_number']:4d}: {sub['name']}\n")
            f.write("\n")

        # Packages
        if result.parse_result.packages:
            f.write("  Packages: " + ", ".join(result.parse_result.packages) + "\n\n")

    def _write_issues_section(self, f, result):
        """Write issues section with detailed explanations."""
        if not result.issues:
            return

        f.write("=" * 80 + "\n")
        f.write("3. ALL ISSUES FOUND\n")
        f.write("=" * 80 + "\n\n")

        for issue in result.issues:
            f.write(f"  [{issue.severity.upper()}] {issue.description}\n")
            f.write(f"  Line: {issue.line_number}\n")
            f.write(f"  Why this is an issue:\n")
            f.write(f"    {issue.explanation}\n")
            f.write(f"  Suggested fix:\n")
            f.write(f"    {issue.suggestion}\n")
            if issue.modern_code:
                f.write(f"  Recommended modern code:\n")
                f.write(f"    {issue.modern_code}\n")
            f.write("\n")

    def _write_line_by_line_explanations(self, f, result):
        """Write line-by-line explanations section."""
        f.write("=" * 80 + "\n")
        f.write("4. LINE-BY-LINE EXPLANATION\n")
        f.write("=" * 80 + "\n\n")

        for line_exp in result.line_explanations:
            f.write("-" * 70 + "\n")
            f.write(f"  Line {line_exp.line_number:4d} | {line_exp.content}\n")
            f.write("-" * 70 + "\n")
            f.write(f"  Purpose     : {line_exp.purpose}\n")
            f.write(f"  Explanation : {line_exp.plain_english}\n\n")

            if line_exp.related_issues:
                f.write("  Issues at this line:\n")
                for iss in line_exp.related_issues:
                    sev_symbol = {
                        'critical': '!! CRITICAL',
                        'error': '! ERROR',
                        'warning': '? WARNING',
                        'info': 'i INFO'
                    }.get(iss.severity, '  ')
                    f.write(f"    [{sev_symbol}] {iss.description}\n")
                    f.write(f"    Fix: {iss.suggestion}\n\n")

    def _write_eda_analysis(self, f, result):
        """Write EDA-specific analysis section."""
        if not (result.eda_script_types or result.tcl_patterns or result.vlsi_data_patterns):
            return

        f.write("=" * 80 + "\n")
        f.write("5. EDA / VLSI ANALYSIS\n")
        f.write("=" * 80 + "\n\n")

        if result.eda_script_types:
            f.write("  5.1 EDA Script Types Detected:\n\n")
            for eda in result.eda_script_types:
                f.write(f"  Category: {eda['category'].upper()}\n")
                f.write(f"  Tool    : {eda['eda_tool']}\n")
                f.write(f"  Desc.   : {eda['description']}\n")
                f.write(f"  Explanation:\n")
                f.write(f"    {eda['explanation']}\n\n")
                if eda.get('common_issues'):
                    f.write("  Common Issues:\n")
                    for ci in eda['common_issues']:
                        f.write(f"    - {ci}\n")
                    f.write("\n")

        if result.tcl_patterns:
            f.write("  5.2 TCL Integration Patterns:\n\n")
            for tcl in result.tcl_patterns:
                f.write(f"  {tcl['description']}\n")
                f.write(f"  {tcl['explanation']}\n")
                if tcl.get('modern_suggestion'):
                    f.write(f"  Modernization: {tcl['modern_suggestion']}\n")
                f.write("\n")

        if result.vlsi_data_patterns:
            f.write("  5.3 VLSI Data Patterns:\n\n")
            for vp in result.vlsi_data_patterns:
                f.write(f"  {vp['description']}\n")
                f.write(f"  {vp['explanation']}\n\n")

    def _write_modernization_suggestions(self, f, result):
        """Write modernization suggestions section."""
        if not result.issues:
            return

        issues_with_suggestions = [i for i in result.issues if i.modern_code]
        if not issues_with_suggestions:
            return

        f.write("=" * 80 + "\n")
        f.write("6. MODERNIZATION SUGGESTIONS\n")
        f.write("=" * 80 + "\n\n")

        f.write("The following modernizations are recommended:\n\n")

        for issue in issues_with_suggestions:
            f.write(f"  Suggestion {issue.pattern_id}:\n")
            f.write(f"  Location: Line {issue.line_number}\n")
            f.write(f"  Issue   : {issue.description}\n")
            f.write(f"  Code    : {issue.modern_code}\n\n")

        f.write("  Benefits of Modernization:\n")
        f.write("    • Improved code readability and maintainability\n")
        f.write("    • Better performance and reduced memory usage\n")
        f.write("    • Enhanced security against code injection\n")
        f.write("    • Compatibility with modern Perl versions (5.32+)\n")
        f.write("    • Easier integration with modern EDA tools\n\n")

    def _write_footer(self, f, result):
        """Write report footer."""
        f.write("=" * 80 + "\n")
        f.write("                    END OF REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"  Generated by MPC Protocol - Perl Script Analyzer\n")
        f.write(f"  Analysis completed at: {result.analysis_time}\n")
        f.write("=" * 80 + "\n")


def create_pdf_generator(output_dir: str = "output") -> PDFReportGenerator:
    """Create and return a PDFReportGenerator instance."""
    return PDFReportGenerator(output_dir)