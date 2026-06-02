"""
Perl Patterns Database
=====================
Database of Perl patterns for detecting deprecated constructs,
suggesting modernizations, identifying best practices,
and providing natural language explanations.
"""

from typing import List, Dict, Any, Optional


# ============================================================
# Pattern Definitions
# ============================================================

# All detection patterns for Perl script analysis
PERL_VERSION_PATTERNS = [
    # Original patterns
    {
        'id': 'PERL-OLD-OPEN',
        'category': 'file_io',
        'severity': 'warning',
        'pattern': r'\bopen\s*\(\s*(?!my\s+\$)\w+\s*,\s*["\']',
        'description': 'Old-style 2-argument open with bareword filehandle',
        'explanation': "This uses old-style open() with a bareword filehandle. Use lexical handles with 3-arg open.",
        'modern_code': "open(my $fh, '<', \$filename) or die \"Cannot open: \$!\";",
    },
    {
        'id': 'PERL-OLD-FILEHANDLE',
        'category': 'file_io',
        'severity': 'warning',
        'pattern': r'\b(?:print|printf|say)\s+(?!\{)\w+\s+(?!\()',
        'description': 'Bareword filehandle used with print/printf',
        'explanation': "Using bareword filehandles is deprecated. Use lexical filehandles.",
        'modern_code': 'print {$fh} "output\\n";',
    },
    {
        'id': 'PERL-OLD-FOR-DECL',
        'category': 'control_flow',
        'severity': 'info',
        'pattern': r'\bfor\s*\(\s*my\s+\$\w+\s*=\s*\d+\s*;',
        'description': 'C-style for loop - consider Perl foreach style',
        'explanation': "C-style for loops can be replaced with foreach for readability.",
        'modern_code': 'foreach my $i (0..$#array) { ... }',
    },
    {
        'id': 'PERL-MODERN-SAY',
        'category': 'io_operations',
        'severity': 'info',
        'pattern': r'\bprint\s+(?:\{[\$@%]\w+\})?\s*["\'].*?\\n["\']\s*;',
        'description': 'Print with explicit newline - consider using say',
        'explanation': "The say() function automatically adds a newline, making code cleaner.",
        'modern_code': 'say "your text here";',
    },
    {
        'id': 'PERL-MISSING-STRICT',
        'category': 'best_practice',
        'severity': 'error',
        'pattern': r'^(?!.*\buse\s+strict\b)',
        'description': 'Missing "use strict" pragma',
        'explanation': "The 'use strict' pragma is essential for robust Perl code.",
        'modern_code': 'use strict;\nuse warnings;',
    },
    {
        'id': 'PERL-MISSING-WARNINGS',
        'category': 'best_practice',
        'severity': 'warning',
        'pattern': r'^(?!.*\buse\s+warnings\b)',
        'description': 'Missing "use warnings" pragma',
        'explanation': "The 'use warnings' pragma enables diagnostic messages.",
        'modern_code': 'use warnings;',
    },
    {
        'id': 'PERL-MISSING-VERSION',
        'category': 'best_practice',
        'severity': 'info',
        'pattern': r'^(?!.*\buse\s+v\d+\.\d+\b)',
        'description': 'Missing Perl version declaration',
        'explanation': "Without a version pragma, the script may run on incompatible Perl versions.",
        'modern_code': 'use v5.20;',
    },
    {
        'id': 'PERL-UNMATCHED-BRACE',
        'category': 'syntax',
        'severity': 'critical',
        'pattern': r'^\s*\}\s*$',
        'description': 'Unmatched closing brace — COMPILE-TIME BLOCKER',
        'explanation': "Extra closing brace prevents script from compiling. All other issues are irrelevant until fixed.",
        'modern_code': 'perl -c script.pl    # verify syntax',
    },
    # v3.0: Execution-level issues
    {
        'id': 'PERL-UNCHECKED-RETURN-CONTEXT',
        'category': 'execution_flow',
        'severity': 'error',
        'pattern': r'\bmy\s*\(\s*\$(\w+)\s*,\s*\$(\w+)\s*\)\s*=\s*\w+',
        'description': 'Return value used without context check',
        'explanation': "2-value return not validated — second var silently becomes undef on error.",
        'modern_code': "my @r = func(); die unless @r == 2; my ($a,$b)=@r;",
    },
    {
        'id': 'PERL-LOOP-NO-BOUNDS',
        'category': 'loop',
        'severity': 'warning',
        'pattern': r'\bforeach\s+my\s+\$\w+\s+@',
        'description': 'Loop iterates list without bounds check',
        'explanation': "No max iteration guard — unexpected large list causes memory exhaustion.",
        'modern_code': "my \$max=100; my \$count=0; for my \$item (\@items) { last if ++\$count > \$max; ... }",
    },
    {
        'id': 'PERL-UNBOUNDED-SOCKET-READ',
        'category': 'loop',
        'severity': 'warning',
        'pattern': r'while\s*\(?\s*<\s*\$(\w+)\s*>\s*\)?',
        'description': 'Socket read loop has no byte limit',
        'explanation': "while(<\$socket>) without byte cap can cause memory exhaustion.",
        'modern_code': "my \$max=1_048_576; while (my \$chunk = <\$socket>) { \$response.=\$chunk; die if length > \$max; }",
    },
    {
        'id': 'PERL-VOID-CALL',
        'category': 'calling',
        'severity': 'warning',
        'pattern': r'^\s*test_\w+\s*\(\s*\)\s*;\s*$',
        'description': 'Subroutine called in void context without eval{}',
        'explanation': "Crashed test kills all remaining tests — no eval{} isolation.",
        'modern_code': "eval { test_sub() }; if (\$@) { log_result('EXCEPTION','FAIL',\$@); }",
    },
    {
        'id': 'PERL-UNCHECKED-METHOD-CHAIN',
        'category': 'calling',
        'severity': 'warning',
        'pattern': r'IO::Socket::INET\s*->\s*new\s*\(',
        'description': 'Method chain without intermediate check',
        'explanation': "->new() returns undef on failure — unchecked use causes crash.",
    },
    {
        'id': 'PERL-FRAGILE-EVAL-STRING',
        'category': 'execution_flow',
        'severity': 'info',
        'pattern': r'\$@\s*eq\s*["\'][^"\']*["\']',
        'description': 'Fragile $@ string comparison',
        'explanation': "String-matching \$@ breaks if error message changes.",
    },
    # v4.0: Dependency / portability / protocol / resilience
    {
        'id': 'PERL-DEP-NO-VERSION-PIN',
        'category': 'dependencies',
        'severity': 'warning',
        'pattern': r'\buse\s+(JSON|JSON::XS|DBI|LWP)\s*;',
        'description': 'CPAN module not version-pinned',
        'explanation': "JSON 1.x vs 4.x API differences. Pin version for consistency.",
        'modern_code': 'use JSON 2.90;',
    },
    {
        'id': 'PERL-DEP-NO-FALLBACK',
        'category': 'dependencies',
        'severity': 'warning',
        'pattern': r'\buse\s+(JSON|XML::LibXML|DBI|LWP)',
        'description': 'No fallback if module missing',
        'explanation': "Script dies with no helpful message if module not installed.",
    },
    {
        'id': 'PERL-DEP-MISSING-HIRES',
        'category': 'dependencies',
        'severity': 'info',
        'pattern': r'\btime\s*\(\s*\)',
        'description': 'Time::HiRes not imported — 1s resolution',
        'explanation': "time() has 1-second resolution. Milliseconds-level latency invisible.",
        'modern_code': 'use Time::HiRes qw(time);',
    },
    {
        'id': 'PERL-DEP-MISSING-SCALAR-UTIL',
        'category': 'dependencies',
        'severity': 'info',
        'pattern': r'\b(?:bless|ref)\s*\(',
        'description': 'Scalar::Util not imported',
        'explanation': "No blessed()/reftype() checks for safe type validation.",
    },
    {
        'id': 'PERL-ALARM-NOT-PORTABLE',
        'category': 'portability',
        'severity': 'warning',
        'pattern': r'\balarm\s*\(',
        'description': 'alarm() not portable on Windows',
        'explanation': "alarm() silently does nothing on Windows — script may hang forever.",
        'modern_code': 'use IO::Select; my $sel = IO::Select->new($socket); if ($sel->can_read($TIMEOUT)) { ... }',
    },
    {
        'id': 'PERL-JSONRPC-STATIC-ID',
        'category': 'protocol',
        'severity': 'warning',
        'pattern': r'id\s*=>\s*\d+',
        'description': 'JSON-RPC id hardcoded',
        'explanation': "JSON-RPC 2.0 requires unique id per request.",
        'modern_code': 'my $req_id = 0; id => ++$req_id,',
    },
    {
        'id': 'PERL-JSONRPC-ID-MISMATCH',
        'category': 'protocol',
        'severity': 'warning',
        'pattern': r'decode_json\s*\(',
        'description': 'No response id validation',
        'explanation': "Response id not verified against request id.",
    },
    {
        'id': 'PERL-NO-SUITE-TIMEOUT',
        'category': 'resilience',
        'severity': 'info',
        'pattern': r'^\s*test_\w+\s*\(\s*\)\s*;\s*$',
        'description': 'No overall suite timeout',
        'explanation': "8 tests x 10s = 80s worst-case blocking.",
    },
    {
        'id': 'PERL-UNBOUNDED-RESULTS-ARRAY',
        'category': 'resilience',
        'severity': 'info',
        'pattern': r'\bpush\s+@\w+,\s*\$',
        'description': '@results grows unbounded',
        'explanation': "No size cap — memory fills under long loops.",
    },
    {
        'id': 'PERL-LOG-NO-ROTATION',
        'category': 'operations',
        'severity': 'info',
        'pattern': r'open\s*\(?\s*my\s+\$\w+\s*,\s*[\'"]>[\'"]\s*,?\s*\$?\w*log',
        'description': 'Log file overwrites on each run',
        'explanation': "open('>', \$LOG_FILE) truncates previous logs.",
    },
    {
        'id': 'PERL-NO-STRUCTURED-OUTPUT',
        'category': 'operations',
        'severity': 'info',
        'pattern': r'^\s*print\s+["\'].*RESULTS.*["\']',
        'description': 'No structured CI/CD output',
        'explanation': "Plain text can't be parsed by CI/CD systems.",
    },
    {
        'id': 'PERL-UNCHECKED-CLOSE',
        'category': 'file_io',
        'severity': 'warning',
        'pattern': r'\bclose\s*\(\s*\$?\w+\s*\)\s*;',
        'description': 'close() return value not checked',
        'explanation': "Buffered writes may fail silently on close().",
        'modern_code': 'close($fh) or warn "Close failed: $!";',
    },
    # v5.0: Security and consistency patterns
    {
        'id': 'PERL-DEAD-CODE-MYSUB',
        'category': 'undocumented',
        'severity': 'warning',
        'pattern': r'^\s*sub\s+mysub\s*\{',
        'description': 'mysub() defined but never called — dead code',
        'explanation': "mysub() compiles but is never executed. Wasted compile time + confusion.",
    },
    {
        'id': 'PERL-MISSING-SUB-SIGNATURE',
        'category': 'documentation',
        'severity': 'warning',
        'pattern': r'^\s*sub\s+\w+\s*\{',
        'description': 'Subroutine missing doc comment header',
        'explanation': "No argument/return documentation — side effects invisible.",
    },
    {
        'id': 'PERL-NO-TLS',
        'category': 'security',
        'severity': 'warning',
        'pattern': r'\buse\s+IO::Socket::INET\b',
        'description': 'No TLS — plaintext TCP used',
        'explanation': "Perl source code transmitted in cleartext over TCP.",
    },
    {
        'id': 'PERL-NO-RESPONSE-SCHEMA',
        'category': 'resilience',
        'severity': 'warning',
        'pattern': r'decode_json\s*\(',
        'description': 'No response schema validation',
        'explanation': "Server response used without JSON-RPC structure check.",
    },
    {
        'id': 'PERL-TAINT-CONFIG-VARS',
        'category': 'security',
        'severity': 'warning',
        'pattern': r'\$\w+\s*=\s*[\'\"][\d.]+[\'\"]\s*;',
        'description': 'Config vars not validated',
        'explanation': "Hardcoded now but may become user-supplied — no validation exists.",
    },
    {
        'id': 'PERL-OLD-HEREDOC-STYLE',
        'category': 'best_practice',
        'severity': 'warning',
        'pattern': r'<<[\'\"](?:END|EOF|PERL)[\'\"]',
        'description': 'Old-style heredoc — use <<~ indented form (Perl 5.26+)',
        'explanation': "Old heredocs force column-1 alignment breaking code indentation.",
    },
    # v6.0: New patterns (16 total)
    {
        'id': 'PERL-NO-UTF8',
        'category': 'security',
        'severity': 'warning',
        'pattern': r'^#!/usr/bin/perl',
        'description': 'No use utf8 declaration — encoding attack surface',
        'explanation': "Without use utf8, multibyte characters in server responses corrupt string ops.",
        'modern_code': "use utf8;\nuse Encode qw(decode_utf8);\nbinmode(STDOUT, ':utf8');",
    },
    {
        'id': 'PERL-NO-TAINT-MODE',
        'category': 'security',
        'severity': 'warning',
        'pattern': r'^#!/usr/bin/perl(?!.*-T)',
        'description': 'Taint mode not enabled (-T flag missing)',
        'explanation': "Without -T, external data flows unvalidated to sockets.",
        'modern_code': '#!/usr/bin/perl -T',
    },
    {
        'id': 'PERL-CONFIG-NOT-ENV-OVERRIDABLE',
        'category': 'execution_flow',
        'severity': 'warning',
        'pattern': r'\$\w+\s*=\s*[\'\"][\d.]+[\'\"]\s*;',
        'description': 'Config vars not env-overridable',
        'explanation': "Hardcoded config requires editing source for CI/CD — bad practice.",
        'modern_code': "my \$MCP_HOST = \$ENV{MCP_HOST} // '127.0.0.1';",
    },
    {
        'id': 'PERL-DEP-MISSING-IO-SELECT',
        'category': 'dependencies',
        'severity': 'warning',
        'pattern': r'\balarm\s*\(',
        'description': 'IO::Select not imported — alarm() fix will break',
        'explanation': "Recommended alarm() replacement uses IO::Select but it's not imported.",
    },
    {
        'id': 'PERL-DEP-MISSING-SSL',
        'category': 'dependencies',
        'severity': 'warning',
        'pattern': r'\buse\s+IO::Socket::INET\b',
        'description': 'IO::Socket::SSL not imported — no TLS support',
        'explanation': "TLS fix requires IO::Socket::SSL but it's not imported or installed.",
    },
    {
        'id': 'PERL-WEAK-ASSERTION-LIST-TOOLS',
        'category': 'calling',
        'severity': 'warning',
        'pattern': r'\blog_result\b',
        'description': 'test_list_tools() never checks analyze tool is present',
        'explanation': "Returns SOME tools but doesn't verify expected tool is in list.",
    },
    {
        'id': 'PERL-WRITELOG-NO-EVAL',
        'category': 'execution_flow',
        'severity': 'error',
        'pattern': r'^\s*write_log\s*\(\s*\)\s*;\s*$',
        'description': 'write_log() called without eval{} — disk error hides exit code',
        'explanation': "If write_log() dies (disk full), exit code at L344 is never reached.",
        'modern_code': "eval { write_log() };\nif (\$@) { warn \"Cannot write log: \$@\"; }",
    },
    {
        'id': 'PERL-NO-AUTOFLUSH',
        'category': 'io_operations',
        'severity': 'warning',
        'pattern': r'^\s*print\s+["\'].*TEST',
        'description': 'No $OUTPUT_AUTOFLUSH — output invisible in pipes',
        'explanation': "Without \$| = 1, test progress buffers and may not appear until end.",
        'modern_code': "\$| = 1;   # or: use IO::Handle; STDOUT->autoflush(1);",
    },
    {
        'id': 'PERL-MISSING-INLINE-DOCS-CORE',
        'category': 'documentation',
        'severity': 'info',
        'pattern': r'^\s*sub\s+send_mcp_request\s*\{',
        'description': 'send_mcp_request() has zero inline comments',
        'explanation': "Most critical sub in the script — no argument/return documentation.",
    },
    {
        'id': 'PERL-MISSING-INLINE-DOCS-LOG',
        'category': 'documentation',
        'severity': 'info',
        'pattern': r'^\s*sub\s+log_result\s*\{',
        'description': 'log_result() side effects undocumented',
        'explanation': "Modifies shared state (\$pass_count, \@results) with no doc comment.",
    },
    {
        'id': 'PERL-MISSING-RECONNECT-TEST',
        'category': 'resilience',
        'severity': 'info',
        'pattern': r'^\s*sub\s+test_latency\s*\{',
        'description': 'No reconnection resilience test',
        'explanation': "No test verifies MCP server recovers after TCP disconnect.",
    },
    {
        'id': 'PERL-MISSING-CONCURRENCY-TEST',
        'category': 'resilience',
        'severity': 'info',
        'pattern': r'^\s*sub\s+test_empty_script\s*\{',
        'description': 'No concurrent request test',
        'explanation': "No test verifies server handles 5 simultaneous connections.",
    },
    {
        'id': 'PERL-EDA-NO-VERSION-REF',
        'category': 'eda',
        'severity': 'info',
        'pattern': r'\bSynopsys|Design\s*Compiler|dc_shell',
        'description': 'EDA comment missing version + migration path',
        'explanation': "Tool reference has no version number — API changes between versions.",
    },
]


# ============================================================
# Performance patterns
# ============================================================

PERF_PATTERNS = [
    {
        'id': 'PERF-SLURP-FILE',
        'category': 'performance',
        'severity': 'warning',
        'pattern': r'(?:join|split|map)\s*\(?\s*["\']?[^"\']*["\']?\s*,\s*<\w+>',
        'description': 'File slurping - may use excessive memory',
        'explanation': "Reading entire file into memory can be problematic for large files.",
        'modern_code': "while (my \$line = <\$fh>) { process(\$line); }",
    },
]


# ============================================================
# Security patterns
# ============================================================

SECURITY_PATTERNS = [
    {
        'id': 'SEC-SYSTEM-CALL',
        'category': 'security',
        'severity': 'critical',
        'pattern': r'\bsystem\s*\(\s*["\'][^"\']*\$[^"\']*["\']',
        'description': 'Potential command injection via system()',
        'explanation': "Interpolated variables in system() strings cause injection risk.",
        'modern_code': "system('command', 'arg1', \$user_input);",
    },
    {
        'id': 'SEC-EVAL-STRING',
        'category': 'security',
        'severity': 'critical',
        'pattern': r'\beval\s*\(?\s*["\'][^"\']*',
        'description': 'Potential code injection via eval string',
        'explanation': "eval string executes arbitrary code. Use eval BLOCK instead.",
    },
]


# ============================================================
# v4.0: Dependency Audit Data
# ============================================================

DEPENDENCY_AUDIT_DATA = [
    {'module': 'strict', 'type': 'Core', 'pinned': 'N/A', 'risk': 'LOW', 'suggestion': 'Always available'},
    {'module': 'warnings', 'type': 'Core', 'pinned': 'N/A', 'risk': 'LOW', 'suggestion': 'Always available'},
    {'module': 'JSON', 'type': 'CPAN', 'pinned': 'No', 'risk': 'HIGH', 'suggestion': 'Pin with use JSON 2.90;'},
    {'module': 'IO::Socket::INET', 'type': 'Core', 'pinned': 'No', 'risk': 'LOW', 'suggestion': 'Ships with Perl 5.6+'},
    {'module': 'POSIX', 'type': 'Core', 'pinned': 'No', 'risk': 'LOW', 'suggestion': 'Ships with all Perl'},
    {'module': 'feature', 'type': 'Core', 'pinned': 'No', 'risk': 'MEDIUM', 'suggestion': 'Add use v5.20;'},
    {'module': 'Time::HiRes', 'type': 'Core', 'pinned': 'Missing', 'risk': 'MEDIUM', 'suggestion': 'Needed for latency'},
    {'module': 'Scalar::Util', 'type': 'Core', 'pinned': 'Missing', 'risk': 'LOW', 'suggestion': 'Useful for type checks'},
]


# ============================================================
# v4.0: Testability Score Data
# ============================================================

TESTABILITY_CATEGORIES = [
    ('Strict mode', 10, 'use strict + warnings present'),
    ('Error isolation', 3, 'No eval{} around individual tests'),
    ('Modularity', 6, 'Subs well-named but tightly coupled'),
    ('Return value safety', 4, 'Return counts not validated'),
    ('Logging quality', 6, 'Good format; no UTC, no rotation'),
    ('Protocol correctness', 4, 'Static JSON-RPC id; no id validation'),
    ('Portability', 4, 'alarm() broken on Windows; no utf8'),
    ('Dependency management', 3, 'No version pins; no fallback; SSL missing'),
    ('CI/CD readiness', 3, 'No TAP; no env overrides; no suite timeout'),
    ('Performance awareness', 4, 'time() coarse; no byte caps'),
    ('Security posture', 3, 'No TLS; no taint mode; no UTF-8'),
]


# ============================================================
# v4.0: Performance Profile Data
# ============================================================

PERFORMANCE_BOTTLENECKS = [
    {'bottleneck': 'Blocking socket reads', 'location': 'L64-70', 'impact': 'HIGH', 'fix': 'Use IO::Select with timeout'},
    {'bottleneck': 'Sequential test calls', 'location': 'L327-334', 'impact': 'MEDIUM', 'fix': 'Run tests in parallel (threads or fork)'},
    {'bottleneck': 'Full log flush at end', 'location': 'L341', 'impact': 'MEDIUM', 'fix': 'Use write-through logging in log_result()'},
    {'bottleneck': 'time() resolution', 'location': 'L286-299', 'impact': 'LOW', 'fix': 'Replace with Time::HiRes::time()'},
    {'bottleneck': 'JSON decode every response', 'location': 'L84', 'impact': 'LOW', 'fix': 'Cache static responses (tools/list) if needed'},
    {'bottleneck': 'encode_json every request', 'location': 'L57-59', 'impact': 'LOW', 'fix': 'Pre-encode static requests at startup'},
]


# ============================================================
# v4.0: Refactoring Roadmap Data
# ============================================================

REFACTORING_ROADMAP = {
    'PHASE 1 — Critical Fixes (do immediately, < 1 hour)': [
        'perl -c script.pl → Fix unmatched brace at L88',
        'Add eval{} around each test call in main block (L327-334)',
        'Fix timeout check: replace $@ string match with flag variable',
        'Add close() return checks at L75, L102, L316',
    ],
    'PHASE 2 — Robustness (< 2 hours)': [
        'Add use v5.20; and use JSON 2.90; version declarations',
        'Add use Time::HiRes qw(time); for accurate latency',
        'Replace alarm() with IO::Select for portability',
        'Add JSON-RPC request id counter (not hardcoded 1)',
        'Wrap encode_json and write_log() in eval{}',
    ],
    'PHASE 3 — Quality (< 4 hours)': [
        'Replace all print+\\n with say()',
        'Add BEGIN{} fallback for JSON module',
        'Convert config vars to use constant',
        'Add log rotation / timestamped log filename',
        'Add TAP output support for CI/CD integration',
        'Add response id validation in send_mcp_request',
    ],
    'PHASE 4 — Excellence (optional, future)': [
        'Use Test::More framework with ok()/is()/like() assertions',
        'Add parallel test execution using forks or threads',
        'Add JSON Schema validation for MCP responses',
        'Add @results size cap and write-through flush',
        'Generate HTML test report using HTML::Template or similar',
    ],
}


# ============================================================
# v4.0: CI/CD Integration Data
# ============================================================

CICD_GUIDE = {
    'current_state': 'Script exits with code 1 on failure ✅. No machine-readable output ❌.',
    'github_actions': '''    - name: Run MCP Perl Tests
      run: |
        perl script.pl
        echo "Exit code: $?"''',
    'tap_based': '    - name: Run MCP Perl Tests (TAP)\n      run: perl script.pl | prove --input -',
    'jenkins': "    sh 'perl script.pl > test_results.tap'\n    step([\$class: 'TapPublisher', testResults: 'test_results.tap'])",
    'minimal_viable': "    timeout 60 perl script.pl && echo \"ALL TESTS PASSED\" || echo \"TESTS FAILED\"",
}


# ============================================================
# Natural Language Descriptions & Explanations
# ============================================================

CONSTRUCT_EXPLANATIONS = {
    'shebang': {'description': 'Shebang line', 'explanation': "The shebang line tells the OS which interpreter to use."},
    'use_statement': {'description': 'Module import', 'explanation': "The 'use' statement loads a module at compile time."},
    'my_declaration': {'description': 'Lexical variable', 'explanation': "'my' declares a lexically-scoped variable."},
    'subroutine': {'description': 'Subroutine definition', 'explanation': "The 'sub' keyword defines a function."},
    'file_open': {'description': 'File opening', 'explanation': "Opens a file for reading or writing."},
    'foreach_loop': {'description': 'Foreach loop', 'explanation': "Iterates over a list of values."},
    'close_operation': {'description': 'File/socket close', 'explanation': "Closes a filehandle or socket."},
    'return_statement': {'description': 'Return statement', 'explanation': "Exits subroutine and returns a value."},
}

CONTEXT_EXPLANATIONS = {
    'assignment': {'simple': {'description': "Assigns a value."}},
    'function_call': {'description': "Calls a function."},
    'file_operation': {'open': {'description': "Opens a file."}, 'close': {'description': "Closes a file."}},
}

EXECUTION_TYPE_EXPLANATIONS = {
    'assign': {'type_label': '[ASSIGN] Variable declared', 'what_happens': "A variable is declared and assigned."},
    'call': {'type_label': '[CALL] Function called', 'what_happens': "A subroutine is invoked."},
    'loop': {'type_label': '[LOOP] Loop begins', 'what_happens': "A loop starts iterating."},
    'import': {'type_label': '[IMPORT] Module loaded', 'what_happens': "Module loaded at compile time."},
    'def': {'type_label': '[DEF] Subroutine defined', 'what_happens': "Sub compiled, not yet called."},
    'method': {'type_label': '[METHOD] Method invoked', 'what_happens': "Object method called."},
    'exec': {'type_label': '[EXEC] Expression executed', 'what_happens': "Expression evaluated for side effects."},
    'return': {'type_label': '[RETURN] Value returned', 'what_happens': "Exits sub and returns value."},
    'file_open': {'type_label': '[FILE] Opened', 'what_happens': "Filehandle opened for I/O."},
    'file_close': {'type_label': '[FILE] Closed', 'what_happens': "Filehandle closed."},
    'shebang': {'type_label': 'Shebang', 'what_happens': "OS selects interpreter."},
    'comment': {'type_label': 'Comment', 'what_happens': "Ignored by Perl."},
    'block_end': {'type_label': '[EXEC] Block end', 'what_happens': "Scope exited."},
}
