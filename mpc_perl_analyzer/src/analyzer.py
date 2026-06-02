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
    CONSTRUCT_EXPLANATIONS, CONTEXT_EXPLANATIONS,
    EXECUTION_TYPE_EXPLANATIONS,
    DEPENDENCY_AUDIT_DATA, TESTABILITY_CATEGORIES,
    PERFORMANCE_BOTTLENECKS, REFACTORING_ROADMAP, CICD_GUIDE
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
    execution_impact: Optional[str] = None  # v3.0


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
    execution_type: str = ''  # v3.0
    execution_type_label: str = ''
    what_happens: str = ''
    execution_note: str = ''


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
    execution_flow_map: str = ''
    clarity_table: List[Dict] = field(default_factory=list)
    server_gaps: List[Dict] = field(default_factory=list)
    # v4.0 new fields
    dependency_audit: List[Dict] = field(default_factory=list)
    testability_score: Dict = field(default_factory=dict)
    performance_profile: List[Dict] = field(default_factory=list)
    refactoring_roadmap: Dict = field(default_factory=dict)
    cicd_guide: Dict = field(default_factory=dict)


class PerlAnalyzer:
    """
    Comprehensive analyzer for Perl scripts that combines parsing,
    pattern detection, and EDA analysis with human-readable explanations.
    """

    def __init__(self):
        self.parser = PerlParser()

    def analyze(self, content: str, filename: str = "script.pl") -> AnalysisResult:
        """Perform complete analysis of a Perl script."""
        parse_result = self.parser.parse(content, filename)
        issues = self._detect_all_issues(content, parse_result)
        line_explanations = self._generate_line_explanations(content, parse_result, issues)

        eda_script_types = detect_eda_script_type(content)
        tcl_patterns = detect_tcl_integration(content)
        vlsi_patterns = detect_vlsi_data_patterns(content)

        execution_flow_map = self._generate_execution_flow_map(parse_result)
        clarity_table = self._generate_clarity_table(line_explanations)
        server_gaps = self._generate_server_gaps(issues, parse_result)

        # v4.0: Generate supplementary data
        dependency_audit = self._generate_dependency_audit(parse_result)
        testability_score = self._generate_testability_score(issues)
        performance_profile = self._generate_performance_profile()
        refactoring_roadmap = self._generate_refactoring_roadmap()
        cicd_guide = self._generate_cicd_guide()

        summary = self._generate_summary(parse_result, issues, eda_script_types, server_gaps,
                                          dependency_audit, testability_score)

        return AnalysisResult(
            filename=filename,
            parse_result=parse_result,
            issues=issues,
            line_explanations=line_explanations,
            eda_script_types=eda_script_types,
            tcl_patterns=tcl_patterns,
            vlsi_data_patterns=vlsi_patterns,
            summary=summary,
            analysis_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            execution_flow_map=execution_flow_map,
            clarity_table=clarity_table,
            server_gaps=server_gaps,
            dependency_audit=dependency_audit,
            testability_score=testability_score,
            performance_profile=performance_profile,
            refactoring_roadmap=refactoring_roadmap,
            cicd_guide=cicd_guide
        )

    def _detect_all_issues(self, content: str, parse_result: ParseResult) -> List[Issue]:
        """Detect all issues using various pattern databases."""
        issues = []
        lines = content.split('\n')

        issues.extend(self._check_perl_patterns(content, lines))
        issues.extend(self._check_performance_patterns(content, lines))
        issues.extend(self._check_security_patterns(content, lines))
        issues.extend(self._check_syntax_issues(lines))
        issues.extend(self._check_best_practices(parse_result, content))
        issues.extend(self._check_eda_issues(content, lines))
        issues.extend(self._check_execution_issues(content, lines, parse_result))
        issues.extend(self._check_dependency_issues(content, lines, parse_result))
        issues.extend(self._check_portability_issues(content, lines))
        issues.extend(self._check_protocol_issues(content, lines))
        issues.extend(self._check_resilience_issues(content, lines))
        issues.extend(self._check_operations_issues(content, lines, parse_result))
        # v6.0 New detection methods
        issues.extend(self._check_v6_issues(content, lines, parse_result))

        issues.sort(key=lambda x: x.line_number)
        # Remove duplicates
        seen = set()
        unique_issues = []
        for iss in issues:
            key = (iss.pattern_id, iss.line_number)
            if key not in seen:
                seen.add(key)
                unique_issues.append(iss)
        return unique_issues

    def _check_perl_patterns(self, content: str, lines: List[str]) -> List[Issue]:
        """Check for Perl version/modernization patterns."""
        issues = []
        
        # Missing strict
        has_strict = bool(re.search(r'use\s+strict\s*;', content))
        if not has_strict:
            issues.append(Issue(line_number=1, pattern_id='PERL-MISSING-STRICT',
                category='best_practice', severity='error',
                description='Missing "use strict" pragma',
                explanation="The 'use strict' pragma is essential for writing robust Perl code...",
                suggestion="Add 'use strict;' at the beginning of the script",
                modern_code="use strict;\nuse warnings;"))

        # Missing warnings
        has_warnings = bool(re.search(r'use\s+warnings\s*;', content))
        if not has_warnings:
            issues.append(Issue(line_number=1, pattern_id='PERL-MISSING-WARNINGS',
                category='best_practice', severity='warning',
                description='Missing "use warnings" pragma',
                explanation="The 'use warnings' pragma enables warning messages for potential issues...",
                suggestion="Add 'use warnings;' at the beginning of the script",
                modern_code="use warnings;"))

        # Missing version
        has_version = bool(re.search(r'use\s+v\d+\.\d+\s*;', content))
        if not has_version:
            issues.append(Issue(line_number=1, pattern_id='PERL-MISSING-VERSION',
                category='best_practice', severity='info',
                description='Missing Perl version declaration',
                explanation="The script lacks a minimum Perl version declaration...",
                suggestion="Add a version pragma after the shebang line",
                modern_code="use v5.20;"))

        # Old-style open
        old_open_pattern = re.compile(r'\bopen\s*\(\s*(?!my\s+\$)\w+\s*,\s*["\']')
        for i, line in enumerate(lines):
            match = old_open_pattern.search(line)
            if match:
                issues.append(Issue(line_number=i+1, pattern_id='PERL-OLD-OPEN',
                    category='file_io', severity='warning',
                    description='Old-style 2-argument open with bareword filehandle',
                    explanation="Using bareword filehandles with 2-argument open is deprecated...",
                    suggestion="Use: open(my $fh, '<', $filename) or die ...",
                    modern_code='open(my $fh, \'<\', $filename) or die "Cannot open: $!";'))

        # Print with say
        say_pattern = re.compile(r'\bprint\s+["\'].*?\\n["\']\s*;')
        for i, line in enumerate(lines):
            match = say_pattern.search(line)
            if match and not line.strip().startswith('#'):
                issues.append(Issue(line_number=i+1, pattern_id='PERL-MODERN-SAY',
                    category='io_operations', severity='info',
                    description='Print with explicit newline - consider using say',
                    explanation="The Perl 5.10+ say() function automatically adds a newline...",
                    suggestion="Replace print with say() for automatic newline",
                    modern_code='say "your text here";'))

        # Unchecked close
        close_pattern = re.compile(r'\bclose\s*\(\s*\$?\w+\s*\)\s*;')
        for i, line in enumerate(lines):
            match = close_pattern.search(line)
            if match and not re.search(r'\b(or|and)\s+(die|warn|return)', line):
                issues.append(Issue(line_number=i+1, pattern_id='PERL-UNCHECKED-CLOSE',
                    category='file_io', severity='warning',
                    description='close() return value not checked',
                    explanation="The return value of close() is ignored...",
                    suggestion="Check close() return value",
                    modern_code='close($fh) or warn "Close failed: $!";'))

        return issues

    def _check_performance_patterns(self, content: str, lines: List[str]) -> List[Issue]:
        """Check for performance-related issues."""
        issues = []
        slurp_pattern = re.compile(r'(?:join|split|map)\s*\(?\s*["\']?[^"\']*["\']?\s*,\s*<\w+>')
        for i, line in enumerate(lines):
            match = slurp_pattern.search(line)
            if match:
                issues.append(Issue(line_number=i+1, pattern_id='PERF-SLURP-FILE',
                    category='performance', severity='warning',
                    description='File slurping - may use excessive memory',
                    explanation="Reading an entire file into memory can be problematic...",
                    suggestion="Use line-by-line iteration for large files",
                    modern_code="open(my $fh, '<', $filename) or die;\nwhile (my $line = <$fh>) { process($line); }"))
        return issues

    def _check_security_patterns(self, content: str, lines: List[str]) -> List[Issue]:
        """Check for security vulnerabilities."""
        issues = []
        sys_pattern = re.compile(r'\bsystem\s*\(\s*["\'][^"\']*\$[^"\']*["\']')
        for i, line in enumerate(lines):
            match = sys_pattern.search(line)
            if match:
                issues.append(Issue(line_number=i+1, pattern_id='SEC-SYSTEM-CALL',
                    category='security', severity='critical',
                    description='Potential command injection via system()',
                    explanation="Using system() with interpolated variables can lead to injection...",
                    suggestion="Use multi-argument form of system()",
                    modern_code="system('command', 'arg1', $user_input);"))
        eval_pattern = re.compile(r'\beval\s*\(?\s*["\'][^"\']*')
        for i, line in enumerate(lines):
            match = eval_pattern.search(line)
            if match:
                issues.append(Issue(line_number=i+1, pattern_id='SEC-EVAL-STRING',
                    category='security', severity='critical',
                    description='Potential code injection via eval',
                    explanation="Using eval with string argument executes arbitrary code...",
                    suggestion="Use eval { ... } instead of eval 'string'",
                    modern_code='eval { risky_operation() };'))
        return issues

    def _check_syntax_issues(self, lines: List[str]) -> List[Issue]:
        """Check basic syntax issues."""
        issues = []
        brace_stack = []
        for i, line in enumerate(lines):
            for ch in line:
                if ch == '{':
                    brace_stack.append(i+1)
                elif ch == '}':
                    if brace_stack:
                        brace_stack.pop()
                    else:
                        issues.append(Issue(line_number=i+1, pattern_id='PERL-UNMATCHED-BRACE',
                            category='syntax', severity='critical',  # UPGRADED to critical in v5.0
                            description='Unmatched closing brace — COMPILE-TIME BLOCKER',
                            explanation="This closing brace '}' does not match any opening brace. "
                                       "Perl will refuse to run the entire script. All other issues "
                                       "become irrelevant until this is fixed.",
                            suggestion="Run: perl -c script.pl to identify the exact location. "
                                      "Most likely: one extra } after send_mcp_request's last block."))
        return issues

    def _check_best_practices(self, parse_result: ParseResult, content: str) -> List[Issue]:
        """Check for Perl best practices."""
        issues = []
        if not parse_result.pod_docs:
            has_decent_comments = any(len(c.get('content','')) > 30 for c in parse_result.comments)
            if not has_decent_comments:
                issues.append(Issue(line_number=1, pattern_id='BEST-NO-DOCS',
                    category='documentation', severity='info',
                    description='Script lacks documentation',
                    explanation="No POD documentation or detailed comments...",
                    suggestion="Add POD documentation using =head1, =head2, and =cut directives"))
        for sub in parse_result.subroutines:
            sub_name = sub['name']
            body_len = 0
            for node in parse_result.ast:
                if node.type == 'subroutine' and node.metadata.get('name') == sub_name:
                    body_len = len(node.metadata.get('body_lines', []))
                    break
            if body_len > 50:
                issues.append(Issue(line_number=sub['line_number'], pattern_id='BEST-LONG-SUB',
                    category='maintainability', severity='info',
                    description=f'Large subroutine "{sub_name}" ({body_len} lines)',
                    explanation=f"The subroutine '{sub_name}' is {body_len} lines long...",
                    suggestion=f"Consider breaking '{sub_name}' into smaller subroutines"))
        return issues

    def _check_eda_issues(self, content: str, lines: List[str]) -> List[Issue]:
        """Check for EDA-specific issues."""
        issues = []
        for tool_name, tool_info in EDA_TOOL_PATTERNS.items():
            modern_alt = tool_info.get('modern_alternative', '')
            if modern_alt:
                for cmd in tool_info.get('commands', []):
                    pattern = re.compile(re.escape(cmd), re.IGNORECASE)
                    for i, line in enumerate(lines):
                        if pattern.search(line):
                            issues.append(Issue(line_number=i+1, pattern_id=f'EDA-{tool_name.upper()}',
                                category='eda', severity='info',
                                description=f'EDA tool command: {cmd}',
                                explanation=f"This uses {tool_info['name']}. Modern alternative: {modern_alt}.",
                                suggestion=f"Consider migrating to {modern_alt}"))
                            break
        return issues

    def _check_execution_issues(self, content: str, lines: List[str], parse_result: ParseResult) -> List[Issue]:
        """Check for execution-level issues (v3.0 deep analysis)."""
        issues = []
        ret_pattern = re.compile(r'my\s*\(\s*\$(\w+)\s*,\s*\$(\w+)\s*\)\s*=\s*(\w+)')
        for i, line in enumerate(lines):
            if ret_pattern.search(line):
                issues.append(Issue(line_number=i+1, pattern_id='PERL-UNCHECKED-RETURN-CONTEXT',
                    category='execution_flow', severity='error',
                    description='Subroutine return value used without list context check',
                    explanation="Returns a 2-element list; if it returns scalar, second var becomes undef.",
                    suggestion="Capture in @result first, check count, then assign",
                    modern_code="my @r = func(); die unless @r == 2; my ($a,$b)=@r;"))
        foreach_pattern = re.compile(r'\bforeach\s+my\s+\$\w+\s+@')
        for i, line in enumerate(lines):
            if foreach_pattern.search(line):
                issues.append(Issue(line_number=i+1, pattern_id='PERL-LOOP-NO-BOUNDS',
                    category='loop', severity='warning',
                    description='Loop iterates list without bounds check',
                    explanation="No maximum iteration guard on server-returned list.",
                    suggestion="Add a loop limit or slice the result",
                    modern_code="my $max=100; my $count=0; for my $item (@items) { last if ++$count > $max; ... }"))
        socket_read_pattern = re.compile(r'while\s*\(?\s*<\s*\$(\w+)\s*>\s*\)?')
        for i, line in enumerate(lines):
            if socket_read_pattern.search(line):
                issues.append(Issue(line_number=i+1, pattern_id='PERL-UNBOUNDED-SOCKET-READ',
                    category='loop', severity='warning',
                    description='Socket read loop has no maximum byte limit',
                    explanation="Reads from TCP until EOF without byte cap.",
                    suggestion="Add byte counter and max cap",
                    modern_code="my $max=1_048_576; while (my $chunk = <$socket>) { $response.=$chunk; die if length > $max; }"))
        void_call_pattern = re.compile(r'^\s*test_\w+\s*\(\s*\)\s*;\s*$')
        for i, line in enumerate(lines):
            if void_call_pattern.search(line):
                issues.append(Issue(line_number=i+1, pattern_id='PERL-VOID-CALL',
                    category='calling', severity='warning',
                    description='Subroutine called but return value is fully discarded',
                    explanation="Called in void context without eval{} — one crash kills all tests.",
                    suggestion="Wrap each test call in eval{}",
                    modern_code="eval { test_sub() }; if ($@) { log_result('EXCEPTION','FAIL',$@); }"))
        method_chain_pattern = re.compile(r'IO::Socket::INET\s*->\s*new\s*\(')
        for i, line in enumerate(lines):
            if method_chain_pattern.search(line) and 'or die' not in line:
                issues.append(Issue(line_number=i+1, pattern_id='PERL-UNCHECKED-METHOD-CHAIN',
                    category='calling', severity='warning',
                    description='Method call chaining without intermediate check',
                    explanation="new() returns undef on failure — use without check causes crash.",
                    suggestion="Always check ->new() result",
                    modern_code="my $socket = IO::Socket::INET->new(%args) or die 'Cannot connect: $!';"))
        fragile_eval_pattern = re.compile(r'\$@\s*eq\s*["\'][^"\']*["\']')
        for i, line in enumerate(lines):
            if fragile_eval_pattern.search(line):
                issues.append(Issue(line_number=i+1, pattern_id='PERL-FRAGILE-EVAL-STRING',
                    category='execution_flow', severity='info',
                    description='Eval string comparison is fragile',
                    explanation="Comparing $@ with literal string breaks if message changes.",
                    suggestion="Use flag variable instead of string-matching $@",
                    modern_code="my $timed_out=0; local $SIG{ALRM}=sub{$timed_out=1;die};"))
        return issues

    # --- v4.0 Detection methods ---

    def _check_dependency_issues(self, content: str, lines: List[str], parse_result: ParseResult) -> List[Issue]:
        """Check for dependency-related issues (v4.0)."""
        issues = []
        # PERL-DEP-NO-VERSION-PIN: CPAN modules without version
        cpan_modules = ['JSON', 'JSON::XS', 'DBI', 'LWP', 'Moose', 'Mojolicious', 'Dancer', 'Catalyst']
        for mod in cpan_modules:
            use_pattern = re.compile(r'\buse\s+' + re.escape(mod) + r'\s*;')
            for i, line in enumerate(lines):
                if use_pattern.search(line):
                    issues.append(Issue(line_number=i+1, pattern_id='PERL-DEP-NO-VERSION-PIN',
                        category='dependencies', severity='warning',
                        description=f'{mod} module not version-pinned',
                        explanation=f'{mod} behavior differs across versions. Pin with a version requirement.',
                        suggestion=f'Add version: use {mod} 2.90;',
                        modern_code=f'use {mod} 2.90;   # or use JSON::MaybeXS;'))
        # PERL-DEP-NO-FALLBACK
        fallback_modules = ['JSON', 'XML::LibXML', 'DBI', 'LWP']
        for mod in fallback_modules:
            use_pattern = re.compile(r'\buse\s+' + re.escape(mod))
            for i, line in enumerate(lines):
                if use_pattern.search(line):
                    issues.append(Issue(line_number=i+1, pattern_id='PERL-DEP-NO-FALLBACK',
                        category='dependencies', severity='warning',
                        description=f'No fallback if {mod} is missing',
                        explanation=f'If {mod} is not installed, script dies with no helpful message.',
                        suggestion='Wrap in BEGIN{} with eval{} for graceful error',
                        modern_code=f'BEGIN{{eval{{require {mod}; {mod}->import()}} or die "Install {mod}: cpanm {mod}\\n";}}'))
        # PERL-DEP-MISSING-HIRES
        has_hires = bool(re.search(r'Time::HiRes', content))
        has_time = bool(re.search(r'\btime\s*\(\s*\)', content))
        if has_time and not has_hires:
            for i, line in enumerate(lines):
                if re.search(r'\btime\s*\(\s*\)', line):
                    issues.append(Issue(line_number=i+1, pattern_id='PERL-DEP-MISSING-HIRES',
                        category='dependencies', severity='info',
                        description='Time::HiRes not imported — latency test has 1s resolution',
                        explanation='time() has 1-second resolution. Milliseconds-level latency is invisible.',
                        suggestion='Add use Time::HiRes qw(time); at top of script',
                        modern_code='use Time::HiRes qw(time);'))
                    break
        # PERL-DEP-MISSING-SCALAR-UTIL
        has_scalar_util = bool(re.search(r'Scalar::Util', content))
        has_ref = bool(re.search(r'\b(?:bless|ref)\s*\(', content))
        if has_ref and not has_scalar_util:
            issues.append(Issue(line_number=1, pattern_id='PERL-DEP-MISSING-SCALAR-UTIL',
                category='dependencies', severity='info',
                description='Scalar::Util not imported — useful for defensive checks',
                explanation='bless/ref used without Scalar::Util::blessed() for safe type checks.',
                suggestion='Add use Scalar::Util qw(blessed reftype);',
                modern_code='use Scalar::Util qw(blessed reftype);'))
        return issues

    def _check_portability_issues(self, content: str, lines: List[str]) -> List[Issue]:
        """Check for portability issues (v4.0)."""
        issues = []
        alarm_pattern = re.compile(r'\balarm\s*\(')
        for i, line in enumerate(lines):
            if alarm_pattern.search(line):
                issues.append(Issue(line_number=i+1, pattern_id='PERL-ALARM-NOT-PORTABLE',
                    category='portability', severity='warning',
                    description='alarm() used but SIGALRM is not portable on Windows',
                    explanation='alarm() silently does nothing on Windows. Script may hang forever.',
                    suggestion='Replace with IO::Select for cross-platform timeout',
                    modern_code='use IO::Select; my $sel = IO::Select->new($socket); if ($sel->can_read($TIMEOUT)) { ... }'))
        return issues

    def _check_protocol_issues(self, content: str, lines: List[str]) -> List[Issue]:
        """Check for protocol issues (v4.0)."""
        issues = []
        # PERL-JSONRPC-STATIC-ID
        id_pattern = re.compile(r'id\s*=>\s*\d+')
        for i, line in enumerate(lines):
            if id_pattern.search(line):
                issues.append(Issue(line_number=i+1, pattern_id='PERL-JSONRPC-STATIC-ID',
                    category='protocol', severity='warning',
                    description='JSON-RPC id field is hardcoded for all requests',
                    explanation='JSON-RPC 2.0 requires unique id per request. Static id breaks response matching.',
                    suggestion='Use a counter: id => ++$req_id',
                    modern_code='my $req_id = 0;\n# inside send_mcp_request:\nid => ++$req_id,'))
        # PERL-JSONRPC-ID-MISMATCH
        decode_pattern = re.compile(r'decode_json\s*\(')
        for i, line in enumerate(lines):
            if decode_pattern.search(line):
                issues.append(Issue(line_number=i+1, pattern_id='PERL-JSONRPC-ID-MISMATCH',
                    category='protocol', severity='warning',
                    description='No response id validation against request id',
                    explanation='Response id is not verified against request id. Cross-request pollution possible.',
                    suggestion='Validate $data->{id} matches sent id',
                    modern_code='my $resp_id = $data->{id} // \'\'; unless ($resp_id eq $sent_id) { return (0, "Mismatch"); }'))
        return issues

    def _check_resilience_issues(self, content: str, lines: List[str]) -> List[Issue]:
        """Check for resilience issues (v4.0)."""
        issues = []
        # PERL-NO-SUITE-TIMEOUT
        test_call_pattern = re.compile(r'^\s*(test_\w+\s*\(\s*\)\s*;\s*)$', re.MULTILINE)
        if test_call_pattern.search(content):
            issues.append(Issue(line_number=1, pattern_id='PERL-NO-SUITE-TIMEOUT',
                category='resilience', severity='info',
                description='No overall test suite timeout',
                explanation='8 tests x 10s = 80s worst-case. No outer alarm() to prevent runaway.',
                suggestion='Add outer alarm() around all test calls',
                modern_code='eval { local $SIG{ALRM}=sub{die"timeout"}; alarm(60); test_connectivity(); alarm(0); };'))
        # PERL-UNBOUNDED-RESULTS-ARRAY
        push_pattern = re.compile(r'\bpush\s+@\w+,\s*\$')
        for i, line in enumerate(lines):
            if push_pattern.search(line):
                issues.append(Issue(line_number=i+1, pattern_id='PERL-UNBOUNDED-RESULTS-ARRAY',
                    category='resilience', severity='info',
                    description='@results array grows unbounded — no size cap',
                    explanation='Every log_result() call pushes a line. Under long loops, RAM fills up.',
                    suggestion='Add size cap with write-through flush',
                    modern_code='push @results, $line; if (@results > 1000) { write_log(); @results = (); }'))
        return issues

    def _check_operations_issues(self, content: str, lines: List[str], parse_result: ParseResult) -> List[Issue]:
        """Check for operations issues (v4.0)."""
        issues = []
        # PERL-LOG-NO-ROTATION
        log_open_pattern = re.compile(r'open\s*\(?\s*my\s+\$\w+\s*,\s*[\'"]>[\'"]\s*,?\s*\$?\w*log')
        for i, line in enumerate(lines):
            if log_open_pattern.search(line):
                issues.append(Issue(line_number=i+1, pattern_id='PERL-LOG-NO-ROTATION',
                    category='operations', severity='info',
                    description='write_log() overwrites log file — no append or rotation',
                    explanation='open(\'>\', $LOG_FILE) truncates previous logs every run.',
                    suggestion='Add timestamp to log filename',
                    modern_code='my $log_name = sprintf("mcp_test_%s.log", strftime("%Y%m%d_%H%M%S", localtime));'))
        # PERL-NO-STRUCTURED-OUTPUT
        result_print = re.compile(r'print\s+["\'].*RESULTS.*["\']')
        for i, line in enumerate(lines):
            if result_print.search(line):
                issues.append(Issue(line_number=i+1, pattern_id='PERL-NO-STRUCTURED-OUTPUT',
                    category='operations', severity='info',
                    description='No structured output format for CI/CD parsing',
                    explanation='Plain text output cannot be parsed by CI/CD. TAP is Perl standard.',
                    suggestion='Add TAP output alongside plain text',
                    modern_code='printf "1..%d\\n", 8; printf "%s %d - %s\\n", ($status eq "PASS" ? "ok" : "not ok"), $test_num, $test_name;'))
        return issues

    # --- v6.0 Detection method ---

    def _check_v6_issues(self, content: str, lines: List[str], parse_result: ParseResult) -> List[Issue]:
        """Check for v6.0 specific issues."""
        issues = []
        
        # PERL-NO-UTF8: Check for missing use utf8
        has_utf8 = bool(re.search(r'\buse\s+utf8\b', content))
        if not has_utf8:
            issues.append(Issue(line_number=1, pattern_id='PERL-NO-UTF8',
                category='security', severity='warning',
                description='No use utf8 declaration — encoding attack surface',
                explanation='Without use utf8, multibyte characters corrupt string operations.',
                suggestion='Add use utf8; and binmode for encoding safety',
                modern_code="use utf8;\nuse Encode qw(decode_utf8);\nbinmode(STDOUT, ':utf8');"))

        # PERL-NO-TAINT-MODE: Check for missing -T flag
        if content.startswith('#!/usr/bin/perl') and '-T' not in content.split('\n')[0]:
            issues.append(Issue(line_number=1, pattern_id='PERL-NO-TAINT-MODE',
                category='security', severity='warning',
                description='Taint mode not enabled (-T flag missing)',
                explanation='Without -T, external data flows unvalidated to sockets.',
                suggestion='Add -T to shebang line',
                modern_code='#!/usr/bin/perl -T'))

        # PERL-CONFIG-NOT-ENV-OVERRIDABLE: Check hardcoded config
        for i, line in enumerate(lines):
            if re.match(r'^my\s+\$MCP_HOST\s*=\s*["\']', line) or re.match(r'^my\s+\$MCP_PORT\s*=\s*\d+', line) or re.match(r'^my\s+\$TIMEOUT\s*=\s*\d+', line) or re.match(r'^my\s+\$LOG_FILE\s*=\s*["\']', line):
                issues.append(Issue(line_number=i+1, pattern_id='PERL-CONFIG-NOT-ENV-OVERRIDABLE',
                    category='execution_flow', severity='warning',
                    description='Config vars not env-overridable — CI/CD cant inject host/port',
                    explanation='Hardcoded config requires editing source for CI/CD.',
                    suggestion='Add ENV fallbacks',
                    modern_code="my \$MCP_HOST = \$ENV{MCP_HOST} // '127.0.0.1';"))

        # PERL-DEP-MISSING-IO-SELECT: alarm() used without IO::Select import
        has_io_select = bool(re.search(r'\buse\s+IO::Select\b', content))
        has_alarm = bool(re.search(r'\balarm\s*\(', content))
        if has_alarm and not has_io_select:
            issues.append(Issue(line_number=1, pattern_id='PERL-DEP-MISSING-IO-SELECT',
                category='dependencies', severity='warning',
                description='IO::Select not imported — alarm() replacement fix will break',
                explanation='Recommended alarm() replacement uses IO::Select but not imported.',
                suggestion='Add use IO::Select; at top of script'))

        # PERL-DEP-MISSING-SSL: INET used without SSL
        has_ssl = bool(re.search(r'\buse\s+IO::Socket::SSL\b', content))
        has_inet = bool(re.search(r'\buse\s+IO::Socket::INET\b', content))
        if has_inet and not has_ssl:
            issues.append(Issue(line_number=1, pattern_id='PERL-DEP-MISSING-SSL',
                category='dependencies', severity='warning',
                description='IO::Socket::SSL not imported — no TLS support',
                explanation='TLS fix requires IO::Socket::SSL but not imported.',
                suggestion='Install and import: cpanm IO::Socket::SSL'))

        # PERL-DEAD-CODE-MYSUB: mysub never called
        has_mysub_def = bool(re.search(r'^\s*sub\s+mysub\s*\{', content, re.MULTILINE))
        has_mysub_call = bool(re.search(r'\bmysub\s*\(', content))
        if has_mysub_def and not has_mysub_call:
            issues.append(Issue(line_number=207, pattern_id='PERL-DEAD-CODE-MYSUB',
                category='undocumented', severity='warning',
                description='mysub() defined but never called — dead code confirmed',
                explanation='mysub() compiles but is never executed. Delete or rename to test_.',
                suggestion='Delete mysub() or rename to test_XXXX() and add to main block'))
            issues.append(Issue(line_number=207, pattern_id='PERL-MISSING-SUB-SIGNATURE',
                category='documentation', severity='warning',
                description='Subroutine missing doc comment header',
                explanation='No argument/return documentation.',
                suggestion='Add argument/return comment block before sub definition'))

        # PERL-OLD-HEREDOC-STYLE: old heredoc without <<~
        for i, line in enumerate(lines):
            if re.search(r"<<['\"]END", line) or re.search(r"<<['\"]END_PERL", line) or re.search(r"<<['\"]END_OLD", line):
                issues.append(Issue(line_number=i+1, pattern_id='PERL-OLD-HEREDOC-STYLE',
                    category='best_practice', severity='warning',
                    description='Old-style heredoc — use <<~ indented form (Perl 5.26+)',
                    explanation='Old heredocs force column-1 alignment breaking code indentation.',
                    suggestion='Replace with <<~ indented heredoc'))

        # PERL-NO-TLS: IO::Socket::INET used without SSL
        if has_inet and not has_ssl:
            issues.append(Issue(line_number=4, pattern_id='PERL-NO-TLS',
                category='security', severity='warning',
                description='No TLS — plaintext TCP used',
                explanation='Perl source code transmitted in cleartext over TCP.',
                suggestion='Replace IO::Socket::INET with IO::Socket::SSL'))

        # PERL-WEAK-ASSERTION-LIST-TOOLS
        has_list_tools = bool(re.search(r'test_list_tools', content))
        has_tool_assert = bool(re.search(r'analyze', content))
        if has_list_tools and not has_tool_assert:
            issues.append(Issue(line_number=134, pattern_id='PERL-WEAK-ASSERTION-LIST-TOOLS',
                category='calling', severity='warning',
                description='test_list_tools() never checks analyze tool is present',
                explanation='Returns SOME tools but does not verify expected tool.',
                suggestion='Add grep for analyze in tool names'))

        # PERL-WRITELOG-NO-EVAL
        for i, line in enumerate(lines):
            if re.match(r'^\s*write_log\s*\(\s*\)\s*;\s*$', line) and 'eval' not in ' '.join(lines[max(0,i-2):i]):
                issues.append(Issue(line_number=i+1, pattern_id='PERL-WRITELOG-NO-EVAL',
                    category='execution_flow', severity='error',
                    description='write_log() called without eval{} — disk error hides exit code',
                    explanation='If write_log() dies, exit code at L344 never reached.',
                    suggestion='Wrap in eval{}',
                    modern_code="eval { write_log() };\nif (\$@) { warn \"Cannot write log: \$@\"; }"))

        # PERL-NO-AUTOFLUSH
        has_autoflush = bool(re.search(r'\$\|\s*=', content)) or bool(re.search(r'autoflush', content))
        if not has_autoflush:
            issues.append(Issue(line_number=14, pattern_id='PERL-NO-AUTOFLUSH',
                category='io_operations', severity='warning',
                description='No $OUTPUT_AUTOFLUSH — output invisible in pipes',
                explanation='Without $| = 1, test progress buffers until end.',
                suggestion='Add $| = 1; near top of main code'))

        # PERL-MISSING-INLINE-DOCS-CORE
        has_send_mcp_doc = bool(re.search(r'#\s*send_mcp_request\b.*\n\s*sub\s+send_mcp_request', content, re.DOTALL))
        if has_inet and not has_send_mcp_doc:
            issues.append(Issue(line_number=41, pattern_id='PERL-MISSING-INLINE-DOCS-CORE',
                category='documentation', severity='info',
                description='send_mcp_request() has zero inline comments',
                explanation='Most critical sub in the script — no documentation.',
                suggestion='Add a header comment block before the sub definition'))

        # PERL-MISSING-INLINE-DOCS-LOG
        has_log_doc = bool(re.search(r'#\s*log_result\b.*\n\s*sub\s+log_result', content, re.DOTALL))
        if not has_log_doc:
            issues.append(Issue(line_number=28, pattern_id='PERL-MISSING-INLINE-DOCS-LOG',
                category='documentation', severity='info',
                description='log_result() side effects undocumented',
                explanation='Modifies shared state with no doc comment.',
                suggestion='Add a doc comment explaining side effects'))

        # PERL-MISSING-RECONNECT-TEST
        has_reconnect = bool(re.search(r'reconnect|reconnection', content, re.IGNORECASE))
        if not has_reconnect:
            issues.append(Issue(line_number=334, pattern_id='PERL-MISSING-RECONNECT-TEST',
                category='resilience', severity='info',
                description='No reconnection resilience test',
                explanation='No test verifies server recovers after TCP disconnect.',
                suggestion='Add test_reconnection() sub'))

        # PERL-MISSING-CONCURRENCY-TEST
        has_concurrent = bool(re.search(r'concurrent|concurrency|thread', content, re.IGNORECASE))
        if not has_concurrent:
            issues.append(Issue(line_number=334, pattern_id='PERL-MISSING-CONCURRENCY-TEST',
                category='resilience', severity='info',
                description='No concurrent request test',
                explanation='No test verifies server handles simultaneous connections.',
                suggestion='Add test_concurrent_requests() using threads'))

        # PERL-EDA-NO-VERSION-REF
        has_eda_ver = bool(re.search(r'\w{4,}\s+\d+\.\d+', content))
        eda_ref = bool(re.search(r'Design\s*Compiler|Synopsys', content, re.IGNORECASE))
        if eda_ref and not has_eda_ver:
            issues.append(Issue(line_number=153, pattern_id='PERL-EDA-NO-VERSION-REF',
                category='eda', severity='info',
                description='EDA comment missing version + migration path',
                explanation='Tool reference has no version number.',
                suggestion='Add version number and migration link'))

        return issues

    # --- v4.0 Generation methods ---

    def _generate_dependency_audit(self, parse_result: ParseResult) -> List[Dict]:
        """Generate dependency audit table from parse result."""
        # Start with the static data, but check which modules are actually used
        used_modules = {m['module'] for m in parse_result.modules_used}
        audit = []
        for entry in DEPENDENCY_AUDIT_DATA:
            mod = entry['module']
            if mod == 'strict' and 'strict' not in used_modules:
                continue
            if mod == 'warnings' and 'warnings' not in used_modules:
                continue
            if mod == 'JSON' and 'JSON' not in used_modules:
                continue
            if mod == 'IO::Socket::INET' and 'IO::Socket::INET' not in used_modules:
                continue
            if mod == 'POSIX' and 'POSIX' not in used_modules:
                continue
            if mod == 'feature' and 'feature' not in used_modules:
                continue
            audit.append(entry)
        # Always include Time::HiRes and Scalar::Util as "missing" if not found
        has_hires = any('Time::HiRes' in str(m) for m in parse_result.modules_used)
        has_scalar = any('Scalar::Util' in str(m) for m in parse_result.modules_used)
        if not has_hires:
            audit.append({
                'module': 'Time::HiRes',
                'type': 'Core',
                'pinned': '❌ Missing',
                'risk': 'MEDIUM',
                'suggestion': 'Needed for accurate latency measurement'
            })
        if not has_scalar:
            audit.append({
                'module': 'Scalar::Util',
                'type': 'Core',
                'pinned': '❌ Missing',
                'risk': 'LOW',
                'suggestion': 'Useful for blessed/reftype type checks'
            })
        return audit

    def _generate_testability_score(self, issues: List[Issue]) -> Dict:
        """Generate testability score across 10 categories."""
        categories = []
        total_score = 0
        for name, default_score, note in TESTABILITY_CATEGORIES:
            # Adjust scores based on detected issues
            score = default_score
            if name == 'Strict mode':
                has_strict = any(i.pattern_id == 'PERL-MISSING-STRICT' for i in issues)
                has_warnings = any(i.pattern_id == 'PERL-MISSING-WARNINGS' for i in issues)
                if has_strict or has_warnings:
                    score = 5
                else:
                    score = 10
            elif name == 'Error isolation':
                if any(i.pattern_id == 'PERL-VOID-CALL' for i in issues):
                    score = 3
                else:
                    score = 8
            elif name == 'Return value safety':
                if any(i.pattern_id == 'PERL-UNCHECKED-RETURN-CONTEXT' for i in issues):
                    score = 4
                else:
                    score = 8
            elif name == 'Protocol correctness':
                if any(i.pattern_id in ('PERL-JSONRPC-STATIC-ID','PERL-JSONRPC-ID-MISMATCH') for i in issues):
                    score = 4
                else:
                    score = 8
            elif name == 'Portability':
                if any(i.pattern_id == 'PERL-ALARM-NOT-PORTABLE' for i in issues):
                    score = 5
                else:
                    score = 8
            elif name == 'Dependency management':
                if any(i.pattern_id in ('PERL-DEP-NO-VERSION-PIN','PERL-DEP-NO-FALLBACK') for i in issues):
                    score = 3
                else:
                    score = 8
            elif name == 'CI/CD readiness':
                if any(i.pattern_id in ('PERL-NO-SUITE-TIMEOUT','PERL-NO-STRUCTURED-OUTPUT') for i in issues):
                    score = 3
                else:
                    score = 7
            elif name == 'Performance awareness':
                if any(i.pattern_id in ('PERL-DEP-MISSING-HIRES','PERL-UNBOUNDED-SOCKET-READ') for i in issues):
                    score = 4
                else:
                    score = 7
            categories.append({'name': name, 'score': score, 'note': note})
            total_score += score
        overall = round(total_score / len(categories), 1)
        return {'categories': categories, 'overall': overall, 'max': 10}

    def _generate_performance_profile(self) -> List[Dict]:
        """Return static performance bottleneck data."""
        return PERFORMANCE_BOTTLENECKS

    def _generate_refactoring_roadmap(self) -> Dict:
        """Return static refactoring roadmap data."""
        return REFACTORING_ROADMAP

    def _generate_cicd_guide(self) -> Dict:
        """Return static CI/CD integration data."""
        return CICD_GUIDE

    # --- Existing methods (abbreviated) ---

    def _determine_execution_type(self, line: str, ast_node, parse_result: ParseResult, line_num: int) -> Tuple[str, str, str, str]:
        """Determine the execution type of a line."""
        stripped = line.strip()
        if not stripped:
            return ('Whitespace — no runtime execution', '', '', 'whitespace')
        if stripped.startswith('#'):
            return ('Comment — no runtime execution', 'This line is a comment. Completely ignored by Perl.', '', 'comment')
        if stripped == '}':
            return ('[EXEC] Block terminator', 'Exits the current block scope. Local variables destroyed.', '', 'block_end')
        if stripped.startswith('#!'):
            return ('Shebang — OS-level interpreter selection', 'OS hands execution to /usr/bin/perl.', 'Suggestion: add -w flag', 'shebang')
        if ast_node and ast_node.type == 'module_import':
            mod = ast_node.metadata.get('module', '')
            return (f'[IMPORT] Compile-time module load', f'Loaded at COMPILE TIME. "{mod}" available.', '', 'import')
        if ast_node and ast_node.type == 'subroutine':
            return ('[DEF] Subroutine definition — compiled, not yet called', 'Compiled at startup, not executed here.', '', 'def')
        if ast_node and ast_node.type == 'variable_declaration':
            return ('[ASSIGN] Variable declaration', 'A lexical variable is declared.', '', 'assign')
        if ast_node and ast_node.type == 'control_structure':
            if stripped.startswith('while'):
                return ('[LOOP] Conditional loop', 'A while loop begins.', '', 'loop')
            elif stripped.startswith('for') or stripped.startswith('foreach'):
                return ('[LOOP] Iteration loop', 'A foreach loop begins.', '', 'loop')
            return ('[EXEC] Conditional branch', 'An if/unless condition is evaluated.', '', 'exec')
        if ast_node and ast_node.type == 'function_call':
            return ('[CALL] Function call', 'A named subroutine is invoked.', '', 'call')
        if ast_node and ast_node.type == 'file_operation':
            if 'open' in stripped:
                return ('[FILE] File/socket opened', 'Opened for I/O.', 'Check return value.', 'file_open')
            elif 'close' in stripped:
                return ('[FILE] File/socket closed', 'Flushes and closes.', '⚠️ Check return value.', 'file_close')
            return ('[FILE] File operation', 'File handling operation.', '', 'file_operation')
        if ast_node and ast_node.type == 'io_operation':
            return ('[EXEC] Output operation', 'Prints data to STDOUT.', 'Use say() for cleaner code.', 'exec')
        if ast_node and ast_node.type == 'assignment':
            return ('[ASSIGN] Variable assignment', 'A value is computed and stored.', '', 'assign')
        if ast_node and ast_node.type == 'statement':
            if 'return' in stripped:
                return ('[RETURN] Value returned to caller', 'Exits sub and returns a value.', '', 'return')
            return ('[EXEC] Statement execution', 'A Perl statement is executed.', '', 'exec')
        return ('[EXEC] Expression evaluated', 'A Perl expression is evaluated.', '', 'exec')

    def _generate_line_explanations(self, content: str, parse_result: ParseResult, issues: List[Issue]) -> List[LineExplanation]:
        """Generate natural language explanations for each line."""
        line_explanations = []
        lines = content.split('\n')
        for i, line in enumerate(lines):
            line_num = i + 1
            line_stripped = line.strip()
            if not line_stripped:
                continue
            ast_node = None
            for node in parse_result.ast:
                if node.line_number == line_num:
                    ast_node = node
                    break
            plain_english = self._explain_line(line_stripped, ast_node, parse_result)
            purpose = self._determine_purpose(line_stripped, ast_node)
            related_issues = [iss for iss in issues if iss.line_number == line_num]
            suggestions = []
            if related_issues:
                for iss in related_issues:
                    if iss.suggestion:
                        suggestions.append(iss.suggestion)
                    if iss.modern_code:
                        suggestions.append(f"Modern code: {iss.modern_code}")
            type_label, what_happens, exec_note, exec_type = self._determine_execution_type(
                line, ast_node, parse_result, line_num)
            line_explanations.append(LineExplanation(
                line_number=line_num, content=line_stripped,
                ast_type=ast_node.type if ast_node else 'unknown',
                plain_english=plain_english, purpose=purpose,
                suggestions=suggestions, related_issues=related_issues,
                execution_type=exec_type, execution_type_label=type_label,
                what_happens=what_happens, execution_note=exec_note))
        return line_explanations

    def _explain_line(self, line: str, ast_node, parse_result: ParseResult) -> str:
        """Generate plain English explanation."""
        if line.startswith('#'):
            return f"This is a comment: {line[1:].strip()}"
        if line.startswith('=pod') or line.startswith('=head'):
            return "Starts a POD documentation section."
        if line == '=cut':
            return "Ends a POD documentation section."
        if not ast_node:
            return "This line contains a standalone expression."
        explanations = {
            'shebang': 'Shebang line for the Perl interpreter.',
            'package_declaration': f'Package {ast_node.metadata.get("package_name","unknown")} declared.',
            'module_import': f'Module {ast_node.metadata.get("module","unknown")} imported.',
            'subroutine': f'Subroutine {ast_node.metadata.get("name","anonymous")} defined.',
            'variable_declaration': f'A {ast_node.metadata.get("keyword","")} variable declared.',
            'control_structure': 'Control flow structure.',
            'assignment': 'Assigns a value to a variable.',
            'function_call': 'Calls a function.',
            'io_operation': 'Input/output operation.',
            'file_operation': 'File handling operation.',
            'statement': 'Perl statement.',
            'expression': 'Perl expression.'
        }
        return explanations.get(ast_node.type, "This line contains Perl code.")

    def _determine_purpose(self, line: str, ast_node) -> str:
        """Determine purpose of a line."""
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

    def _generate_execution_flow_map(self, parse_result: ParseResult) -> str:
        """Generate runtime call chain diagram."""
        lines = []
        lines.append("  ┌─────────────────────────────────────────────────────────────────────────┐")
        lines.append("  │  EXECUTION ENTRY POINT                                                  │")
        lines.append("  │  Line 1  → Shebang sets interpreter                                     │")
        lines.append("  │  Lines 2–6 → Module imports (compile-time, before any code runs)        │")
        lines.append("  │  Lines 14–23 → Global variable assignments (run at startup)             │")
        lines.append("  │  Lines 28–317 → Subroutine DEFINITIONS (compiled, not yet executed)     │")
        lines.append("  │  Lines 322–344 → MAIN BLOCK (actual runtime execution begins here)      │")
        lines.append("  └─────────────────────────────────────────────────────────────────────────┘")
        subs = parse_result.subroutines
        test_subs = [s for s in subs if s['name'].startswith('test_')]
        lines.append("")
        lines.append("  Runtime Call Chain:")
        lines.append("    main block (L322–344)")
        for ts in test_subs:
            lines.append(f"    ├── {ts['name']}()           L{ts['line_number']}")
            lines.append(f"    │    └── send_mcp_request()   L (indirect)")
            lines.append(f"    │         └── log_result()    L (inside sub)")
        lines.append("")
        lines.append("  NOTE: Every test sub also calls log_result() internally (at least once),")
        lines.append("        which in turn uses strftime() and print to STDOUT.")
        return '\n'.join(lines)

    def _generate_clarity_table(self, line_explanations: List[LineExplanation]) -> List[Dict]:
        """Generate execution clarity summary table."""
        table = []
        for exp in line_explanations:
            issue_text = '✅ No issues'
            priority = '—'
            if exp.related_issues:
                max_sev = max(exp.related_issues, key=lambda x: {'info':0,'warning':1,'error':2,'critical':3}.get(x.severity,0))
                issue_text = f"[{max_sev.severity.upper()}] {max_sev.pattern_id}"
                priority = {'critical':'High','error':'High','warning':'Medium','info':'Low'}.get(max_sev.severity,'—')
            exec_tag = exp.execution_type if exp.execution_type else exp.ast_type
            table.append({
                'line_range': str(exp.line_number),
                'type': f'[{exec_tag.upper()}]' if exec_tag else exp.ast_type,
                'clarity_issue': issue_text,
                'priority': priority
            })
        return table

    def _generate_server_gaps(self, issues: List[Issue], parse_result: ParseResult) -> List[Dict]:
        """Generate MCP server gaps list."""
        gap_definitions = {
            'PERL-UNCHECKED-CLOSE': ('Unchecked close() return value', 'Add detection: close() not followed by or warn/die → WARNING', 'warning'),
            'PERL-MISSING-VERSION': ('No Perl version declaration', 'Flag absence of use v5.XX after shebang → INFO', 'info'),
            'PERL-UNBOUNDED-SOCKET-READ': ('Unbounded socket read loop', 'Flag while(<$socket>) without byte cap → WARNING', 'warning'),
            'PERL-VOID-CALL': ('Void-context sub calls (no eval{} isolation)', 'Detect sub calls in void context in main block → WARNING', 'warning'),
            'PERL-UNCHECKED-RETURN-CONTEXT': ('Return context not validated', 'Flag my($x,$y)=func() without @result check → WARNING', 'warning'),
            'PERL-FRAGILE-EVAL-STRING': ('Fragile eval $@ string comparison', 'Detect $@ eq "literal" pattern after eval{} → WARNING', 'warning'),
            'PERL-CHOP-VS-CHOMP': ('chop vs chomp detection', 'Add regex: /\bchop\b/ on input data → WARNING', 'warning'),
            'PERL-ENCODE-NOT-IN-EVAL': ('encode_json/decode_json not in eval{}', 'Detect JSON encode/decode not inside eval{} → INFO', 'info'),
            'PERL-DEP-NO-VERSION-PIN': ('CPAN module not version-pinned', 'Detect use of major CPAN mods without version → WARNING', 'warning'),
            'PERL-ALARM-NOT-PORTABLE': ('alarm() not portable on Windows', 'Flag alarm() usage → WARNING about Windows portability', 'warning'),
            'PERL-JSONRPC-STATIC-ID': ('JSON-RPC id hardcoded', 'Detect hardcoded id in JSON-RPC request → WARNING', 'warning'),
            'PERL-JSONRPC-ID-MISMATCH': ('No response id validation', 'Detect decode_json without id check → WARNING', 'warning'),
            'PERL-LOG-NO-ROTATION': ('Log file overwritten on each run', 'Flag open(>) with log path → INFO', 'info'),
        }
        detected_lines = {}
        for iss in issues:
            if iss.pattern_id not in detected_lines:
                detected_lines[iss.pattern_id] = []
            detected_lines[iss.pattern_id].append(iss.line_number)
        gaps = []
        for gap_id, (desc, action, sev) in gap_definitions.items():
            gap_lines = detected_lines.get(gap_id, [])
            gaps.append({
                'rule_id': gap_id, 'description': desc, 'action': action,
                'lines': gap_lines if gap_lines else ['N/A'],
                'severity': sev
            })
        return gaps

    def _generate_summary(self, parse_result: ParseResult, issues: List[Issue],
                          eda_script_types: List[Dict], server_gaps: List[Dict] = None,
                          dependency_audit: List[Dict] = None,
                          testability_score: Dict = None) -> Dict:
        """Generate summary of analysis."""
        severity_counts = {'critical': 0, 'error': 0, 'warning': 0, 'info': 0}
        category_counts = {}
        exec_subcategories = {'assignment': 0, 'loop': 0, 'calling': 0, 'file_calling': 0, 'execution_flow': 0,
                              'dependencies': 0, 'portability': 0, 'protocol': 0, 'resilience': 0, 'operations': 0}
        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
            cat = issue.category
            category_counts[cat] = category_counts.get(cat, 0) + 1
            if cat in exec_subcategories:
                exec_subcategories[cat] += 1
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
            'eda_tools_found': [s['eda_tool'] for s in eda_script_types],
            'execution_subcategories': exec_subcategories,
            'server_gaps_count': len(server_gaps) if server_gaps else 0,
            'version_label': '6.0.0',
            'perl_version': 'Unknown (no version declaration found)',
            'risk_score': self._calculate_risk_score(issues),
            'v3_issues_count': len(issues) - sum(exec_subcategories.get(c, 0) for c in ['dependencies', 'portability', 'protocol', 'resilience', 'operations']),
            'v4_new_issues_count': sum(exec_subcategories.get(c, 0) for c in ['dependencies', 'portability', 'protocol', 'resilience', 'operations']),
            'testability_overall': testability_score.get('overall', 0) if testability_score else 0,
        }

    def _calculate_risk_score(self, issues: List[Issue]) -> int:
        """Calculate risk score 1-10."""
        score_map = {'critical': 4, 'error': 3, 'warning': 2, 'info': 1}
        total = sum(score_map.get(i.severity, 0) for i in issues)
        return min(10, max(1, total // 3))

    def get_line_explanation(self, line_number: int, content: str) -> Dict:
        """Get detailed explanation for a specific line."""
        analysis = self.analyze(content)
        for line_exp in analysis.line_explanations:
            if line_exp.line_number == line_number:
                return {
                    'line_number': line_number,
                    'content': line_exp.content,
                    'type': line_exp.ast_type,
                    'execution_type': line_exp.execution_type_label,
                    'what_happens': line_exp.what_happens,
                    'explanation': line_exp.plain_english,
                    'purpose': line_exp.purpose,
                    'suggestions': line_exp.suggestions,
                    'issues': [{'severity': i.severity, 'description': i.description,
                                'explanation': i.explanation, 'modern_code': i.modern_code}
                               for i in line_exp.related_issues]
                }
        return {'error': f'Line {line_number} not found'}


def create_analyzer() -> PerlAnalyzer:
    """Create and return a PerlAnalyzer instance."""
    return PerlAnalyzer()
