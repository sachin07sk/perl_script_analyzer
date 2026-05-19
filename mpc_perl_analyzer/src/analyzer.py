"""
Comprehensive Analyzer Module
=============================
Integrates parsing, pattern matching, and EDA analysis 
to provide a complete analysis of Perl scripts with 
human-readable explanations.
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from .parser import PerlParser, ParseResult
from .perl_patterns import (
    PERL_VERSION_PATTERNS, PERF_PATTERNS, SECURITY_PATTERNS,
    CONSTRUCT_EXPLANATIONS, CONTEXT_EXPLANATIONS
)
from .eda_patterns import (
    detect_eda_script_type, detect_tcl_integration,
    detect_vlsi_data_patterns, get_eda_tool_update,
    EDA_TOOL_PATTERNS
)


@dataclass
class Issue:
    """Represents a detected issue with explanation."""
    line_number: int
    pattern_id: str
    category: str
    severity: str  # 'info', 'warning', 'error', 'critical'
    description: str
    explanation: str
    suggestion: str
    modern_code: Optional[str] = None


@dataclass
class LineExplanation:
    """Detailed explanation for a specific line."""
    line_number: int
    content: str
    ast_type: str
    plain_english: str
    purpose: str
    suggestions: List[str]
    related_issues: List[Issue]


@dataclass
class AnalysisResult:
    """Complete analysis result for a Perl script."""
    filename: str
    parse_result: ParseResult
    issues: List[Issue]
    line_explanations: List[LineExplanation]
    eda_script_types: List[Dict]
    tcl_patterns: List[Dict]
    vlsi_data_patterns: List[Dict]
    summary: Dict
    analysis_time: str


class PerlAnalyzer:
    """
    Comprehensive analyzer for Perl scripts that combines parsing,
    pattern detection, and EDA analysis with human-readable explanations.
    """

    def __init__(self):
        self.parser = PerlParser()

    def analyze(self, content: str, filename: str = "script.pl") -> AnalysisResult:
        """
        Perform complete analysis of a Perl script.

        Args:
            content: The script content
            filename: Name of the script file

        Returns:
            AnalysisResult with all findings
        """
        # Step 1: Parse the script
        parse_result = self.parser.parse(content, filename)

        # Step 2: Detect issues
        issues = self._detect_all_issues(content, parse_result)

        # Step 3: Generate line explanations
        line_explanations = self._generate_line_explanations(content, parse_result, issues)

        # Step 4: EDA analysis
        eda_script_types = detect_eda_script_type(content)
        tcl_patterns = detect_tcl_integration(content)
        vlsi_patterns = detect_vlsi_data_patterns(content)

        # Step 5: Generate summary
        summary = self._generate_summary(parse_result, issues, eda_script_types)

        return AnalysisResult(
            filename=filename,
            parse_result=parse_result,
            issues=issues,
            line_explanations=line_explanations,
            eda_script_types=eda_script_types,
            tcl_patterns=tcl_patterns,
            vlsi_data_patterns=vlsi_patterns,
            summary=summary,
            analysis_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    def _detect_all_issues(self, content: str, parse_result: ParseResult) -> List[Issue]:
        """Detect all issues using various pattern databases."""
        issues = []
        lines = content.split('\n')

        # Check Perl version patterns
        issues.extend(self._check_perl_patterns(content, lines))

        # Check performance patterns
        issues.extend(self._check_performance_patterns(content, lines))

        # Check security patterns
        issues.extend(self._check_security_patterns(content, lines))

        # Check basic syntax issues
        issues.extend(self._check_syntax_issues(lines))

        # Check best practices
        issues.extend(self._check_best_practices(parse_result, content))

        # Check EDA-specific issues
        issues.extend(self._check_eda_issues(content, lines))

        # Sort issues by line number
        issues.sort(key=lambda x: x.line_number)

        return issues

    def _check_perl_patterns(self, content: str, lines: List[str]) -> List[Issue]:
        """Check for Perl version/modernization patterns."""
        issues = []
        
        # Check for missing 'use strict'
        has_strict = bool(re.search(r'use\s+strict\s*;', content))
        if not has_strict:
            issues.append(Issue(
                line_number=1,
                pattern_id='PERL-MISSING-STRICT',
                category='best_practice',
                severity='error',
                description='Missing "use strict" pragma',
                explanation=(
                    "The 'use strict' pragma is essential for writing robust "
                    "Perl code. It enforces variable declaration with my/our, "
                    "prevents bareword usage, and catches many common errors."
                ),
                suggestion="Add 'use strict;' at the beginning of the script",
                modern_code="use strict;\nuse warnings;"
            ))

        # Check for missing 'use warnings'
        has_warnings = bool(re.search(r'use\s+warnings\s*;', content))
        if not has_warnings:
            issues.append(Issue(
                line_number=1,
                pattern_id='PERL-MISSING-WARNINGS',
                category='best_practice',
                severity='warning',
                description='Missing "use warnings" pragma',
                explanation=(
                    "The 'use warnings' pragma enables warning messages for "
                    "potential issues in your code."
                ),
                suggestion="Add 'use warnings;' at the beginning of the script",
                modern_code="use warnings;"
            ))

        # Check for old-style open
        old_open_pattern = re.compile(r'\bopen\s*\(\s*(?!my\s+\$)\w+\s*,\s*["\']')
        for i, line in enumerate(lines):
            match = old_open_pattern.search(line)
            if match:
                issues.append(Issue(
                    line_number=i + 1,
                    pattern_id='PERL-OLD-OPEN',
                    category='file_io',
                    severity='warning',
                    description='Old-style 2-argument open with bareword filehandle',
                    explanation=(
                        "Using bareword filehandles with 2-argument open is "
                        "deprecated. Use lexical filehandles with 3-argument "
                        "open for better security."
                    ),
                    suggestion="Use: open(my $fh, '<', $filename) or die ...",
                    modern_code='open(my $fh, \'<\', $filename) or die "Cannot open: $!";'
                ))

        # Check for print with explicit newline (consider say)
        say_pattern = re.compile(r'\bprint\s+["\'].*?\\n["\']\s*;')
        for i, line in enumerate(lines):
            match = say_pattern.search(line)
            if match and not line.strip().startswith('#'):
                issues.append(Issue(
                    line_number=i + 1,
                    pattern_id='PERL-MODERN-SAY',
                    category='io_operations',
                    severity='info',
                    description='Print with explicit newline - consider using say',
                    explanation=(
                        "The Perl 5.10+ say() function automatically adds a "
                        "newline, making code cleaner."
                    ),
                    suggestion="Replace print with say() for automatic newline",
                    modern_code='say "your text here";'
                ))

        return issues

    def _check_performance_patterns(self, content: str, lines: List[str]) -> List[Issue]:
        """Check for performance-related issues."""
        issues = []
        
        # Check for file slurping
        slurp_pattern = re.compile(r'(?:join|split|map)\s*\(?\s*["\']?[^"\']*["\']?\s*,\s*<\w+>')
        for i, line in enumerate(lines):
            match = slurp_pattern.search(line)
            if match:
                issues.append(Issue(
                    line_number=i + 1,
                    pattern_id='PERF-SLURP-FILE',
                    category='performance',
                    severity='warning',
                    description='File slurping - may use excessive memory',
                    explanation=(
                        "Reading an entire file into memory can be problematic "
                        "for large files. Process line-by-line instead."
                    ),
                    suggestion="Use line-by-line iteration for large files",
                    modern_code=(
                        "open(my $fh, '<', $filename) or die;\n"
                        "while (my $line = <$fh>) { process($line); }"
                    )
                ))

        return issues

    def _check_security_patterns(self, content: str, lines: List[str]) -> List[Issue]:
        """Check for security vulnerabilities."""
        issues = []

        # Check for system() with variables
        sys_pattern = re.compile(r'\bsystem\s*\(\s*["\'][^"\']*\$[^"\']*["\']')
        for i, line in enumerate(lines):
            match = sys_pattern.search(line)
            if match:
                issues.append(Issue(
                    line_number=i + 1,
                    pattern_id='SEC-SYSTEM-CALL',
                    category='security',
                    severity='critical',
                    description='Potential command injection via system()',
                    explanation=(
                        "Using system() with interpolated variables can lead "
                        "to command injection attacks."
                    ),
                    suggestion="Use multi-argument form of system()",
                    modern_code="system('command', 'arg1', $user_input);"
                ))

        # Check for eval with string
        eval_pattern = re.compile(r'\beval\s*\(?\s*["\'][^"\']*')
        for i, line in enumerate(lines):
            match = eval_pattern.search(line)
            if match:
                issues.append(Issue(
                    line_number=i + 1,
                    pattern_id='SEC-EVAL-STRING',
                    category='security',
                    severity='critical',
                    description='Potential code injection via eval',
                    explanation=(
                        "Using eval with string argument executes arbitrary "
                        "code. Use eval BLOCK instead."
                    ),
                    suggestion="Use eval { ... } instead of eval 'string'",
                    modern_code='eval { risky_operation() };'
                ))

        return issues

    def _check_syntax_issues(self, lines: List[str]) -> List[Issue]:
        """Check basic syntax issues."""
        issues = []
        brace_stack = []
        paren_stack = []

        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Track brace matching
            for ch in line:
                if ch == '{':
                    brace_stack.append(line_num)
                elif ch == '}':
                    if brace_stack:
                        brace_stack.pop()
                    else:
                        issues.append(Issue(
                            line_number=line_num,
                            pattern_id='SYN-UNBALANCED-BRACE',
                            category='syntax',
                            severity='error',
                            description='Unmatched closing brace',
                            explanation=(
                                "This closing brace '}' does not match any "
                                "opening brace in the code."
                            ),
                            suggestion="Check for missing opening brace '{'"
                        ))

                # Track parenthesis matching  
                if ch == '(':
                    paren_stack.append(line_num)
                elif ch == ')':
                    if paren_stack:
                        paren_stack.pop()
                    else:
                        issues.append(Issue(
                            line_number=line_num,
                            pattern_id='SYN-UNBALANCED-PAREN',
                            category='syntax',
                            severity='error',
                            description='Unmatched closing parenthesis',
                            explanation="This ')' does not match any opening '('.",
                            suggestion="Check for missing opening parenthesis"
                        ))

        # Report unclosed braces
        for opening_line in brace_stack:
            issues.append(Issue(
                line_number=opening_line,
                pattern_id='SYN-UNCLOSED-BRACE',
                category='syntax',
                severity='error',
                description='Unclosed opening brace',
                explanation="This '{' has no matching closing brace '}'.",
                suggestion="Add a closing '}' at the appropriate location"
            ))

        return issues

    def _check_best_practices(self, parse_result: ParseResult, content: str) -> List[Issue]:
        """Check for Perl best practices."""
        issues = []

        # Check for POD documentation
        if not parse_result.pod_docs:
            has_decent_comments = any(
                len(c.get('content', '')) > 30 for c in parse_result.comments
            )
            if not has_decent_comments:
                issues.append(Issue(
                    line_number=1,
                    pattern_id='BEST-NO-DOCS',
                    category='documentation',
                    severity='info',
                    description='Script lacks documentation',
                    explanation=(
                        "This script has no POD documentation or detailed "
                        "comments. Adding documentation helps others understand "
                        "the script's purpose and usage."
                    ),
                    suggestion=(
                        "Add POD documentation at the end of the script using "
                        "=head1, =head2, and =cut directives"
                    )
                ))

        # Check for large subroutines (potential refactoring)
        for sub in parse_result.subroutines:
            sub_name = sub['name']
            sub_start = sub['line_number']
            body_len = 0
            for node in parse_result.ast:
                if (node.type == 'subroutine' and 
                    node.metadata.get('name') == sub_name):
                    body_len = len(node.metadata.get('body_lines', []))
                    break
            
            if body_len > 50:
                issues.append(Issue(
                    line_number=sub_start,
                    pattern_id='BEST-LONG-SUB',
                    category='maintainability',
                    severity='info',
                    description=f'Large subroutine "{sub_name}" ({body_len} lines)',
                    explanation=(
                        f"The subroutine '{sub_name}' is {body_len} lines long. "
                        "Large subroutines can be hard to understand and maintain."
                    ),
                    suggestion=(
                        f"Consider breaking '{sub_name}' into smaller, "
                        f"focused subroutines"
                    )
                ))

        return issues

    def _check_eda_issues(self, content: str, lines: List[str]) -> List[Issue]:
        """Check for EDA-specific issues and suggestions."""
        issues = []

        # Check for deprecated EDA tools
        for tool_name, tool_info in EDA_TOOL_PATTERNS.items():
            modern_alt = tool_info.get('modern_alternative', '')
            if modern_alt:
                for cmd in tool_info.get('commands', []):
                    pattern = re.compile(re.escape(cmd), re.IGNORECASE)
                    for i, line in enumerate(lines):
                        if pattern.search(line):
                            issues.append(Issue(
                                line_number=i + 1,
                                pattern_id=f'EDA-{tool_name.upper()}',
                                category='eda',
                                severity='info',
                                description=f'EDA tool command: {cmd}',
                                explanation=(
                                    f"This script uses {tool_info['name']} commands. "
                                    f"The modern alternative is {modern_alt}."
                                ),
                                suggestion=f"Consider migrating to {modern_alt}"
                            ))
                            break

        # Check TCL integration patterns
        tcl_pattern_data = detect_tcl_integration(content)
        for tcl_pat in tcl_pattern_data:
            pat_id = tcl_pat['id']
            pat_regex_map = {
                'TCL-EXEC': r'(?:system|exec|qx)\s*\(?\s*["\']\s*\$?\w+\s*(?:tcl|tclsh)',
                'TCL-GENERATION': r'(?:print|printf|say)\s+\w+\s*["\'].*?(?:dc_shell|innovus|genus|pt_shell|calibre)',
                'TCL-FILE-WRITE': r'open\s*\(?\s*\w+\s*,\s*["\']>[^"\']*\.tcl'
            }
            regex = pat_regex_map.get(pat_id, '')
            if regex:
                for i, line in enumerate(lines):
                    if re.search(regex, line, re.IGNORECASE):
                        issues.append(Issue(
                            line_number=i + 1,
                            pattern_id=pat_id,
                            category='eda_tcl',
                            severity='info',
                            description=tcl_pat['description'],
                            explanation=tcl_pat['explanation'],
                            suggestion=tcl_pat.get('modern_suggestion', '')
                        ))
                        # Only add once per pattern
                        break

        return issues

    def _generate_line_explanations(self, content: str, parse_result: ParseResult, 
                                      issues: List[Issue]) -> List[LineExplanation]:
        """Generate natural language explanations for each line."""
        line_explanations = []
        lines = content.split('\n')

        for i, line in enumerate(lines):
            line_num = i + 1
            line_stripped = line.strip()

            # Skip empty lines
            if not line_stripped:
                continue

            # Get AST info
            ast_node = None
            for node in parse_result.ast:
                if node.line_number == line_num:
                    ast_node = node
                    break

            # Generate plain English explanation
            plain_english = self._explain_line(line_stripped, ast_node, parse_result)

            # Determine purpose
            purpose = self._determine_purpose(line_stripped, ast_node)

            # Get related issues
            related_issues = [iss for iss in issues if iss.line_number == line_num]

            # Generate suggestions
            suggestions = []
            if related_issues:
                for iss in related_issues:
                    if iss.suggestion:
                        suggestions.append(iss.suggestion)
                    if iss.modern_code:
                        suggestions.append(f"Modern code: {iss.modern_code}")

            line_explanations.append(LineExplanation(
                line_number=line_num,
                content=line_stripped,
                ast_type=ast_node.type if ast_node else 'unknown',
                plain_english=plain_english,
                purpose=purpose,
                suggestions=suggestions,
                related_issues=related_issues
            ))

        return line_explanations

    def _explain_line(self, line: str, ast_node: Optional[object], 
                      parse_result: ParseResult) -> str:
        """Generate a plain English explanation for a single line."""
        if line.startswith('#'):
            return f"This is a comment: {line[1:].strip()}"

        if line.startswith('=pod') or line.startswith('=head'):
            return "This starts a POD documentation section."

        if line == '=cut':
            return "This ends a POD documentation section."

        if not ast_node:
            return "This line contains a standalone expression."

        # Explain based on AST type
        explanations = {
            'shebang': (
                f"This is the shebang line that tells the system to use "
                f"the Perl interpreter to execute this script."
            ),
            'package_declaration': (
                f"This declares the package namespace "
                f"'{ast_node.metadata.get('package_name', 'unknown')}'. "
                f"All subsequent code belongs to this package."
            ),
            'module_import': (
                f"This imports the module "
                f"'{ast_node.metadata.get('module', 'unknown')}'. "
                f"This makes the module's functions and variables available."
            ),
            'subroutine': (
                f"This defines the subroutine "
                f"'{ast_node.metadata.get('name', 'anonymous')}'. "
                f"Subroutines encapsulate reusable code blocks."
            ),
            'variable_declaration': (
                f"This declares a '{ast_node.metadata.get('keyword', '')}' "
                f"variable. This variable is now available for use."
            ),
            'control_structure': (
                f"This is a control structure that controls the flow "
                f"of execution based on conditions or iteration."
            ),
            'assignment': "This line assigns a value to a variable.",
            'function_call': (
                "This line calls a function to perform a specific operation."
            ),
            'io_operation': "This line performs input/output operations.",
            'file_operation': "This line performs file handling operations.",
            'statement': (
                "This is a Perl statement that performs an action."
            ),
            'expression': "This is a Perl expression that computes a value."
        }

        return explanations.get(ast_node.type, "This line contains Perl code.")

    def _determine_purpose(self, line: str, ast_node: Optional[object]) -> str:
        """Determine the purpose of a line of code."""
        if not ast_node:
            return "Code execution"

        purposes = {
            'shebang': 'Interpreter specification',
            'package_declaration': 'Namespace definition',
            'module_import': 'External functionality import',
            'subroutine': 'Custom function definition',
            'variable_declaration': 'Variable creation',
            'control_structure': 'Flow control',
            'assignment': 'Data storage',
            'function_call': 'Operation execution',
            'io_operation': 'Input/Output',
            'file_operation': 'File management',
            'statement': 'Action',
            'expression': 'Computation'
        }

        return purposes.get(ast_node.type, 'Code execution')

    def _generate_summary(self, parse_result: ParseResult, issues: List[Issue],
                          eda_script_types: List[Dict]) -> Dict:
        """Generate a summary of the analysis."""
        severity_counts = {'critical': 0, 'error': 0, 'warning': 0, 'info': 0}
        category_counts = {}

        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
            cat = issue.category
            if cat not in category_counts:
                category_counts[cat] = 0
            category_counts[cat] += 1

        return {
            'total_lines': len(parse_result.lines),
            'total_issues': len(issues),
            'severity_summary': severity_counts,
            'category_summary': category_counts,
            'modules_count': len(parse_result.modules_used),
            'subroutines_count': len(parse_result.subroutines),
            'variables_count': len(parse_result.variables),
            'eda_script_count': len(eda_script_types),
            'has_strict': any(m['module'] == 'strict' for m in parse_result.modules_used),
            'has_warnings': any(m['module'] == 'warnings' for m in parse_result.modules_used),
            'script_type': 'VLSI/EDA' if eda_script_types else 'General',
            'eda_tools_found': [s['eda_tool'] for s in eda_script_types]
        }

    def get_line_explanation(self, line_number: int, content: str) -> Dict:
        """
        Get detailed explanation for a selected line.

        Args:
            line_number: 1-based line number
            content: Full script content

        Returns:
            Dict with line info and detailed explanation
        """
        analysis = self.analyze(content)
        
        for line_exp in analysis.line_explanations:
            if line_exp.line_number == line_number:
                return {
                    'line_number': line_number,
                    'content': line_exp.content,
                    'type': line_exp.ast_type,
                    'explanation': line_exp.plain_english,
                    'purpose': line_exp.purpose,
                    'suggestions': line_exp.suggestions,
                    'issues': [
                        {
                            'severity': i.severity,
                            'description': i.description,
                            'explanation': i.explanation,
                            'modern_code': i.modern_code
                        }
                        for i in line_exp.related_issues
                    ]
                }

        return {'error': f'Line {line_number} not found in analysis'}


def create_analyzer() -> PerlAnalyzer:
    """Create and return a PerlAnalyzer instance."""
    return PerlAnalyzer()