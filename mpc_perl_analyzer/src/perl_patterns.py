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

# Patterns for detecting Perl version-related issues
PERL_VERSION_PATTERNS = [
    {
        'id': 'PERL-OLD-OPEN',
        'category': 'file_io',
        'severity': 'warning',
        'pattern': r'\bopen\s*\(\s*(?!my\s+\$)\w+\s*,\s*["\']',
        'description': 'Old-style 2-argument open with bareword filehandle',
        'explanation': (
            "This uses the old-style open() function with a bareword filehandle "
            "(like FILEHANDLE instead of $fh). Modern Perl recommends using "
            "a lexical filehandle variable (my $fh) with 3-argument open for "
            "better security, scoping, and error handling."
        ),
        'modern_code': 'open(my $fh, \'<\', $filename) or die "Cannot open $filename: $!";',
        'perl_version_introduced': '5.6',
        'benefits': [
            'Lexical scoping prevents accidental global access',
            '3-argument open prevents shell injection attacks',
            'Automatic cleanup when variable goes out of scope',
            'Better error messages with explicit filename'
        ]
    },
    {
        'id': 'PERL-OLD-FILEHANDLE',
        'category': 'file_io',
        'severity': 'warning',
        'pattern': r'\b(?:print|printf|say)\s+(?!\{)\w+\s+(?!\()',
        'description': 'Bareword filehandle used with print/printf',
        'explanation': (
            "Using a bareword filehandle directly with print/printf is an "
            "older Perl style. Modern Perl prefers using a lexical filehandle "
            "variable in curly braces, which provides better scoping and "
            "makes code easier to read and maintain."
        ),
        'modern_code': 'print {$fh} "output\\n";',
        'perl_version_introduced': '5.6',
        'benefits': [
            'Lexical scoping for filehandles',
            'Consistent syntax with other Perl constructs',
            'Easier to refactor and maintain'
        ]
    },
    {
        'id': 'PERL-OLD-FOR-DECL',
        'category': 'control_flow',
        'severity': 'info',
        'pattern': r'\bfor\s*\(\s*my\s+\$\w+\s*=\s*\d+\s*;\s*\$\w+\s*<\s*\d+\s*;\s*\$\w+\+\+\s*\)',
        'description': 'C-style for loop - consider Perl foreach style',
        'explanation': (
            "This is a C-style for loop. Perl offers more readable foreach "
            "loops and range operators that are often simpler and more "
            "idiomatic. Consider using foreach my $i (0..$n-1) instead."
        ),
        'modern_code': 'foreach my $i (0..$#array) { ... }',
        'perl_version_introduced': '4.0',
        'benefits': [
            'More readable and Perl-idiomatic',
            'Less boilerplate code',
            'Works naturally with arrays/hashes'
        ]
    },
    {
        'id': 'PERL-OLD-GREP',
        'category': 'functional',
        'severity': 'info',
        'pattern': r'\b(?:map|grep)\s*\{[^}]*\}\s*(?!\s*\))',
        'description': 'Old-style map/grep with block - consider using with expr',
        'explanation': (
            "Using map/grep with a block {} is perfectly valid Perl. However, "
            "for simple operations, using the expression form with a comma "
            "can be more concise and readable."
        ),
        'modern_code': 'my @results = map { $_->process() } @items;',
        'perl_version_introduced': '5.0',
        'benefits': [
            'Block form allows multi-statement operations',
            'More readable for complex transformations'
        ]
    },
    {
        'id': 'PERL-OLD-SWITCH',
        'category': 'control_flow',
        'severity': 'warning',
        'pattern': r'\b(?:if\s*\(.+\)\s*\{[^}]*\}\s*elsif\s*\(.+\)\s*\{[^}]*\}\s*elsif)',
        'description': 'Long if-elsif chain - consider given/when or dispatch table',
        'explanation': (
            "Long chains of if-elsif statements can be hard to read and "
            "maintain. Perl 5.10+ introduced the given/when switch statement. "
            "Alternatively, consider using a dispatch table with a hash."
        ),
        'modern_code': (
            "use feature 'switch';\n"
            "given ($value) {\n"
            "    when ('case1') { ... }\n"
            "    when ('case2') { ... }\n"
            "    default { ... }\n"
            "}"
        ),
        'perl_version_introduced': '5.10',
        'benefits': [
            'Cleaner switch-like syntax',
            'Better performance with dispatch tables',
            'Easier to add new cases'
        ]
    },
    {
        'id': 'PERL-MODERN-SAY',
        'category': 'io_operations',
        'severity': 'info',
        'pattern': r'\bprint\s+(?:\{[\$@%]\w+\})?\s*["\'].*?\\n["\']\s*;',
        'description': 'Print with explicit newline - consider using say',
        'explanation': (
            "Using print with an explicit newline character \\n can be replaced "
            "with the say() function (available since Perl 5.10), which "
            "automatically appends a newline. This makes the code cleaner and "
            "less error-prone."
        ),
        'modern_code': 'say "Hello, World!";',
        'perl_version_introduced': '5.10',
        'benefits': [
            'Automatic newline handling',
            'Less typing and cleaner code',
            'Part of Perl 5.10+ core features'
        ]
    },
    {
        'id': 'PERL-OLD-DEFINED-OR',
        'category': 'operators',
        'severity': 'info',
        'pattern': r'\bdefined\s*\(\s*(\$\w+)\s*\)\s*(?:&&|\?)\s*',
        'description': 'Defined-or check - consider using // operator',
        'explanation': (
            "Checking if a variable is defined before using it can be simplified "
            "with the defined-or operator // (Perl 5.10+). This operator returns "
            "the left side if it's defined, otherwise the right side."
        ),
        'modern_code': 'my $value = $var // "default";',
        'perl_version_introduced': '5.10',
        'benefits': [
            'More concise than explicit defined() checks',
            'Works with all defined-or scenarios',
            'Part of Perl 5.10+ core'
        ]
    },
    {
        'id': 'PERL-OLD-EXPR-REF',
        'category': 'references',
        'severity': 'info',
        'pattern': r'\\\s*@(\w+)\b',
        'description': 'Backslash reference to array - consider [@array]',
        'explanation': (
            "Using \\@array to create a reference to an array works, but using "
            "square brackets [...] is more explicit and creates an anonymous "
            "array reference. This is the preferred modern Perl style."
        ),
        'modern_code': 'my $array_ref = [@array];  # instead of \\@array',
        'perl_version_introduced': '5.0',
        'benefits': [
            'More explicit intention',
            'Creates anonymous array reference',
            'Consistent with hash references'
        ]
    },
    {
        'id': 'PERL-MISSING-STRICT',
        'category': 'best_practice',
        'severity': 'error',
        'pattern': r'^(?!.*\buse\s+strict\b)',
        'description': 'Missing "use strict" pragma',
        'explanation': (
            "The 'use strict' pragma is essential for writing robust Perl code. "
            "It enforces variable declaration with my/our, prevents bareword "
            "usage, and catches many common programming errors. It should be "
            "the first pragma after the shebang line."
        ),
        'modern_code': 'use strict;\\nuse warnings;',
        'perl_version_introduced': '5.0',
        'benefits': [
            'Forces variable declaration, preventing typos',
            'Prevents accidental bareword interpretation',
            'Catches common errors at compile time',
            'Industry standard for Perl development'
        ]
    },
    {
        'id': 'PERL-MISSING-WARNINGS',
        'category': 'best_practice',
        'severity': 'warning',
        'pattern': r'^(?!.*\buse\s+warnings\b)',
        'description': 'Missing "use warnings" pragma',
        'explanation': (
            "The 'use warnings' pragma enables warning messages for potential "
            "issues in your code, such as uninitialized variables, deprecated "
            "constructs, and type mismatches. It's essential for debugging "
            "and writing reliable Perl code."
        ),
        'modern_code': 'use warnings;',
        'perl_version_introduced': '5.6',
        'benefits': [
            'Catches uninitialized variable usage',
            'Identifies deprecated constructs',
            'Helps with debugging and testing'
        ]
    },
    {
        'id': 'PERL-OLD-QW',
        'category': 'best_practice',
        'severity': 'info',
        'pattern': r'\bqw\s*\((?!\))',
        'description': 'Use qw() with parentheses',
        'explanation': (
            "Using qw() (quote words) with quoted strings like ('word1', 'word2') "
            "can be simplified. The qw() function automatically splits on "
            "whitespace, so you can write qw(word1 word2) instead."
        ),
        'modern_code': 'my @list = qw(element1 element2 element3);',
        'perl_version_introduced': '5.0',
        'benefits': [
            'Less typing',
            'Cleaner code',
            'No need for quotes or commas'
        ]
    },
    {
        'id': 'PERL-OLD-HASH-ACCESS',
        'category': 'data_structures',
        'severity': 'info',
        'pattern': r'\$\w+\{["\']([^"\']+)["\']\}',
        'description': 'Hash access with quoted string keys - bareword keys suffice',
        'explanation': (
            "Accessing hash elements with quoted string keys like $hash{'key'} "
            "is valid but unnecessary. Perl automatically treats barewords as "
            "strings when used as hash keys, so $hash{key} is preferred in "
            "modern Perl."
        ),
        'modern_code': 'my $value = $hash{key};  # instead of $hash{\'key\'}',
        'perl_version_introduced': '4.0',
        'benefits': [
            'Cleaner and more readable',
            'Less visual clutter',
            'Consistent with Perl idioms'
        ]
    }
]


# Patterns for performance optimization
PERF_PATTERNS = [
    {
        'id': 'PERF-LOOP-EXTERNAL-SUB',
        'category': 'performance',
        'severity': 'warning',
        'pattern': r'\bmap\s*\{[^}]*\w+\([^)]*\)[^}]*\}\s*(?:@|$)',
        'description': 'Function call inside map/grep - consider optimizing',
        'explanation': (
            "Calling a function inside map/grep can be slower if the function "
            "is called many times. Consider precomputing values or using "
            "a more efficient approach."
        ),
        'modern_code': 'my @results = map { expensive_function($_) } @data;',
        'optimization_tip': 'Cache function results or use a for loop instead'
    },
    {
        'id': 'PERF-INEFFICIENT-SORT',
        'category': 'performance',
        'severity': 'info',
        'pattern': r'\bsort\s*\{[^}]*\$a\s*(?:<=>|cmp)\s*\$b\s*\}\s*@',
        'description': 'Default sort comparison - can be omitted',
        'explanation': (
            "Using sort { $a cmp $b } @array is equivalent to the default "
            "sort behavior. You can simplify by just using sort @array."
        ),
        'modern_code': 'my @sorted = sort @array;',
        'optimization_tip': 'Omit default comparison for cleaner code'
    },
    {
        'id': 'PERF-SLURP-FILE',
        'category': 'performance',
        'severity': 'warning',
        'pattern': r'(?:join|split|map)\s*\(?\s*["\']?[^"\']*["\']?\s*,\s*<\w+>',
        'description': 'File slurping - may use excessive memory for large files',
        'explanation': (
            "Reading an entire file into memory (slurping) can be problematic "
            "for large files. Consider line-by-line processing for better "
            "memory efficiency."
        ),
        'modern_code': (
            "open(my $fh, '<', $filename) or die;\n"
            "while (my $line = <$fh>) { process($line); }"
        ),
        'optimization_tip': 'Use line-by-line iteration for large files'
    },
    {
        'id': 'PERF-REGEX-REUSE',
        'category': 'performance',
        'severity': 'info',
        'pattern': r'/\$(\w+)/',
        'description': 'Variable interpolation in regex - consider qr// for reuse',
        'explanation': (
            "Using a variable directly in a regex pattern with /$var/ works, "
            "but if the pattern is used multiple times, precompiling it with "
            "qr// improves performance."
        ),
        'modern_code': (
            "my $pattern = qr/$search_term/;\n"
            "if ($data =~ $pattern) { ... }"
        ),
        'optimization_tip': 'Precompile regex with qr// for repeated use'
    }
]


# Patterns for security vulnerabilities
SECURITY_PATTERNS = [
    {
        'id': 'SEC-SYSTEM-CALL',
        'category': 'security',
        'severity': 'critical',
        'pattern': r'\bsystem\s*\(\s*["\'][^"\']*\$[^"\']*["\']',
        'description': 'Potential command injection via system() with variables',
        'explanation': (
            "Using system() with interpolated variables in a single string "
            "can lead to command injection if the variable contains shell "
            "metacharacters. Use the multi-argument form of system() or "
            "escape the input properly."
        ),
        'modern_code': "system('command', 'arg1', $user_input);  # multi-arg form",
        'fix_tip': 'Always use multi-argument system() or escape shell arguments'
    },
    {
        'id': 'SEC-EVAL-STRING',
        'category': 'security',
        'severity': 'critical',
        'pattern': r'\beval\s*\(?\s*["\'][^"\']*',
        'description': 'Potential code injection via eval with string',
        'explanation': (
            "Using eval with a string argument executes arbitrary Perl code. "
            "If the string contains user input, this can lead to code injection. "
            "Prefer eval with a block (eval { ... }) which only catches exceptions."
        ),
        'modern_code': 'eval { risky_operation(); };',
        'fix_tip': 'Use eval BLOCK instead of eval STRING for exception handling'
    },
    {
        'id': 'SEC-UNTAINT',
        'category': 'security',
        'severity': 'warning',
        'pattern': r'\b<>|@ARGV',
        'description': 'Unvalidated input - consider using taint mode',
        'explanation': (
            "Reading input from STDIN (<>) or command-line arguments (@ARGV) "
            "without validation can lead to security issues. Consider using "
            "taint mode with 'use warnings' and validate all external input."
        ),
        'modern_code': "my $input = <STDIN>;\nchomp $input;\ndie 'Invalid input' unless $input =~ /^\\w+$/;",
        'fix_tip': 'Validate all external input and consider using taint mode (-T)'
    }
]


# ============================================================
# Natural Language Descriptions & Explanations
# ============================================================

# Detailed explanations for Perl constructs
CONSTRUCT_EXPLANATIONS = {
    'shebang': {
        'description': 'Shebang line',
        'explanation': (
            "The shebang line (#!) tells the operating system which interpreter "
            "to use to execute this script. #!/usr/bin/perl uses the system Perl, "
            "while #!/usr/bin/env perl is more portable across different systems."
        )
    },
    'use_statement': {
        'description': 'Module import statement',
        'explanation': (
            "The 'use' statement loads and imports a Perl module at compile time. "
            "It's equivalent to a 'require' followed by an import. This makes "
            "the module's functions and variables available in the current namespace."
        )
    },
    'my_declaration': {
        'description': 'Lexical variable declaration',
        'explanation': (
            "'my' declares a lexically-scoped variable. The variable is only "
            "visible within the current block or file. This is the standard way "
            "to declare local variables in modern Perl, providing better scoping "
            "and preventing accidental global variable access."
        )
    },
    'subroutine': {
        'description': 'Subroutine (function) definition',
        'explanation': (
            "The 'sub' keyword defines a subroutine (function) in Perl. "
            "Subroutines can accept arguments via @_ and return values using "
            "'return'. Perl passes all arguments as a list in @_."
        )
    },
    'file_open': {
        'description': 'File opening operation',
        'explanation': (
            "Opening a file allows the script to read from or write to a file. "
            "The mode '<' means read, '>' means write (overwrite), '>>' means "
            "append, and '+<' means read/write. Always check if open() succeeded."
        )
    },
    'hash_variable': {
        'description': 'Hash (associative array) variable',
        'explanation': (
            "A hash (also called an associative array) stores key-value pairs. "
            "It's declared with % prefix and accessed with $hash{key}. Hashes "
            "are unordered but provide O(1) lookup by key."
        )
    },
    'array_variable': {
        'description': 'Array variable',
        'explanation': (
            "An array stores an ordered list of values, indexed by integers "
            "starting from 0. It's declared with @ prefix and individual "
            "elements are accessed with $array[index]."
        )
    },
    'regex_match': {
        'description': 'Regular expression match',
        'explanation': (
            "The =~ operator applies a regular expression pattern match against "
            "a string. The pattern /pattern/ searches for the pattern in the "
            "string. The match variable $1, $2, etc. capture groups."
        )
    },
    'foreach_loop': {
        'description': 'Foreach loop',
        'explanation': (
            "The foreach loop iterates over a list of values, assigning each "
            "element to the loop variable in turn. Perl's foreach is versatile "
            "and works with arrays, ranges, and any list-generating expression."
        )
    },
    'package_declaration': {
        'description': 'Package declaration',
        'explanation': (
            "The 'package' declaration switches the current namespace. All "
            "subsequent subroutines and variables belong to this package. This "
            "is how Perl implements modules and namespaces."
        )
    }
}


# ============================================================
# Context-based explanation templates
# ============================================================

CONTEXT_EXPLANATIONS = {
    'assignment': {
        'simple': {
            'description': "This line assigns a value to a variable.",
            'template': "Line {line_number} assigns {value} to variable {variable}. "
                       "The variable now holds this value and can be used in subsequent operations."
        },
        'complex': {
            'description': "This line performs a complex assignment operation.",
            'template': "Line {line_number} computes and assigns the result to {variable}. "
                       "This involves {operation}, which transforms the input data."
        }
    },
    'function_call': {
        'description': "This line calls a function.",
        'template': "Line {line_number} calls the {function} function with arguments {args}. "
                   "This function {purpose}. The result is {usage}."
    },
    'control_structure': {
        'if': {
            'description': "This is a conditional statement.",
            'template': "Line {line_number} checks if {condition}. "
                       "If true, the script executes the code inside this block."
        },
        'for': {
            'description': "This is a loop that iterates over a range or list.",
            'template': "Line {line_number} starts a loop that iterates over {iterable}. "
                       "Each iteration processes one element."
        },
        'while': {
            'description': "This is a loop that continues while a condition is true.",
            'template': "Line {line_number} starts a while loop that continues as long as "
                       "{condition} is true."
        }
    },
    'file_operation': {
        'open': {
            'description': "This line opens a file.",
            'template': "Line {line_number} opens the file {filename} in {mode} mode. "
                       "This allows the script to {purpose} the file contents."
        },
        'close': {
            'description': "This line closes a file.",
            'template': "Line {line_number} closes the filehandle {handle}, "
                       "releasing system resources associated with the open file."
        }
    }
}