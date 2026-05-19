"""
Perl Script Parser Module
=========================
Parses Perl scripts into an Abstract Syntax Tree (AST) with 
line number tracking for detailed analysis and explanation.
"""

import re
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ASTNode:
    """Represents a node in the Perl AST."""
    type: str
    line_number: int
    content: str
    children: List['ASTNode'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParseResult:
    """Result of parsing a Perl script."""
    filename: str
    lines: List[Tuple[int, str]]
    ast: List[ASTNode]
    shebang: Optional[str]
    modules_used: List[Dict]
    subroutines: List[Dict]
    variables: List[Dict]
    comments: List[Dict]
    pod_docs: List[Dict]
    packages: List[str]
    hashes: Dict[str, str]
    parse_time: str


class PerlParser:
    """
    Parses Perl scripts and builds a structured representation
    with line-level tracking for detailed analysis.
    """

    # Perl keywords for syntax highlighting and categorization
    KEYWORDS = {
        'my', 'our', 'local', 'state', 'use', 'require', 'no',
        'if', 'else', 'elsif', 'unless', 'while', 'until', 'for', 'foreach',
        'do', 'sub', 'package', 'return', 'next', 'last', 'redo', 'goto',
        'die', 'warn', 'exit', 'eval', 'defined', 'undef', 'ref',
        'open', 'close', 'print', 'printf', 'say', 'chomp', 'chop',
        'push', 'pop', 'shift', 'unshift', 'splice', 'split', 'join',
        'map', 'grep', 'sort', 'keys', 'values', 'each', 'exists', 'delete',
        'bless', 'new', 'isa', 'can'
    }

    # Built-in Perl variables
    SPECIAL_VARIABLES = {
        '$_', '$!', '$@', '$?', '$\\', '$$', '$0', '$|',
        '$[', '$]', '$"', '$,', '$.', '$/', '$\\', '$:',
        '$#', '$~', '$^', '$^A', '$^C', '$^D', '$^E', '$^F',
        '$^H', '$^I', '$^L', '$^M', '$^O', '$^P', '$^R', '$^S',
        '$^T', '$^V', '$^W', '$^X', '@_', '@ARGV', '%ENV', '%SIG'
    }

    def __init__(self):
        self.sub_pattern = re.compile(
            r'^\s*sub\s+(\w+)\s*(?:\{|\(?.*\)?\s*\{)?'
        )
        self.my_pattern = re.compile(
            r'\b(my|our|local|state)\s+\$?([\w:]+)'
        )
        self.use_pattern = re.compile(
            r'^\s*use\s+([\w:]+)(?:\s+([\d.]+))?(?:\s+qw\s*\((.*?)\))?\s*;'
        )
        self.package_pattern = re.compile(
            r'^\s*package\s+([\w:]+)\s*;'
        )
        self.assignment_pattern = re.compile(
            r'\b(\$[\w:]+)\s*='
        )

    def parse(self, content: str, filename: str = "script.pl") -> ParseResult:
        """
        Parse a Perl script and return structured analysis.

        Args:
            content: The Perl script content as a string
            filename: Name of the script file

        Returns:
            ParseResult with all parsed information
        """
        lines = content.split('\n')
        line_tuples = [(i + 1, line) for i, line in enumerate(lines)]

        ast = self._build_ast(lines)
        shebang = self._extract_shebang(lines)
        modules = self._extract_modules(lines)
        subroutines = self._extract_subroutines(lines)
        variables = self._extract_variables(lines)
        comments = self._extract_all_comments(lines)
        pod_docs = self._extract_pod(lines)
        packages = self._extract_packages(lines)

        return ParseResult(
            filename=filename,
            lines=line_tuples,
            ast=ast,
            shebang=shebang,
            modules_used=modules,
            subroutines=subroutines,
            variables=variables,
            comments=comments,
            pod_docs=pod_docs,
            packages=packages,
            hashes={
                'md5': __import__('hashlib').md5(content.encode()).hexdigest(),
                'lines': str(len(lines))
            },
            parse_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    def _build_ast(self, lines: List[str]) -> List[ASTNode]:
        """Build a simplified AST from the script lines."""
        ast = []
        i = 0
        while i < len(lines):
            line_num = i + 1
            line = lines[i].strip()

            if not line:
                i += 1
                continue

            # Skip comments and POD
            if line.startswith('#') or line.startswith('=pod') or line.startswith('=head'):
                i += 1
                continue
            if line == '=cut':
                i += 1
                continue

            # Shebang line
            if line.startswith('#!'):
                ast.append(ASTNode(
                    type='shebang',
                    line_number=line_num,
                    content=line
                ))
                i += 1
                continue

            # Package declaration
            pkg_match = self.package_pattern.match(lines[i])
            if pkg_match:
                ast.append(ASTNode(
                    type='package_declaration',
                    line_number=line_num,
                    content=line,
                    metadata={'package_name': pkg_match.group(1)}
                ))
                i += 1
                continue

            # Use/Require statements
            use_match = self.use_pattern.match(lines[i])
            if use_match:
                module_info = {
                    'module': use_match.group(1),
                    'version': use_match.group(2) if use_match.group(2) else '',
                    'import_list': use_match.group(3) if use_match.group(3) else ''
                }
                ast.append(ASTNode(
                    type='module_import',
                    line_number=line_num,
                    content=line,
                    metadata=module_info
                ))
                i += 1
                continue

            # Subroutine definition
            sub_match = self.sub_pattern.match(lines[i])
            if sub_match:
                sub_name = sub_match.group(1)
                sub_body_lines = []
                brace_depth = line.count('{') - line.count('}')
                i += 1
                while i < len(lines) and brace_depth > 0:
                    sub_body_lines.append((i + 1, lines[i]))
                    brace_depth += lines[i].count('{') - lines[i].count('}')
                    i += 1
                ast.append(ASTNode(
                    type='subroutine',
                    line_number=line_num,
                    content=f'sub {sub_name} {{...}}',
                    metadata={'name': sub_name, 'body_lines': sub_body_lines}
                ))
                continue

            # Variable declarations
            var_match = self.my_pattern.search(lines[i])
            if var_match and ('my' in lines[i] or 'our' in lines[i] or 'local' in lines[i]):
                ast.append(ASTNode(
                    type='variable_declaration',
                    line_number=line_num,
                    content=line,
                    metadata={
                        'keyword': var_match.group(1),
                        'variable': var_match.group(2)
                    }
                ))
                i += 1
                continue

            # Control structures
            if any(lines[i].startswith(kw) for kw in ['if', 'unless', 'while', 'until', 'for', 'foreach', 'do']):
                ast.append(ASTNode(
                    type='control_structure',
                    line_number=line_num,
                    content=line
                ))
                i += 1
                continue

            # Expressions/statements
            if line.endswith(';') or line.endswith('{') or line.endswith('}'):
                # Determine statement type
                stmt_type = 'statement'
                if '= ' in line or '=>' in line:
                    if '(' in line and ')' in line:
                        stmt_type = 'function_call'
                    else:
                        stmt_type = 'assignment'
                elif re.search(r'\b(print|say|printf|warn|die)\b', line):
                    stmt_type = 'io_operation'
                elif re.search(r'\b(open|close|read|write)\b', line):
                    stmt_type = 'file_operation'

                ast.append(ASTNode(
                    type=stmt_type,
                    line_number=line_num,
                    content=line
                ))
                i += 1
                continue

            # Default: treat as expression
            ast.append(ASTNode(
                type='expression',
                line_number=line_num,
                content=line
            ))
            i += 1

        return ast

    def _extract_shebang(self, lines: List[str]) -> Optional[str]:
        """Extract the shebang line if present."""
        if lines and lines[0].startswith('#!'):
            return lines[0]
        return None

    def _extract_modules(self, lines: List[str]) -> List[Dict]:
        """Extract all use/require/no statements."""
        modules = []
        for i, line in enumerate(lines):
            use_match = re.match(r'^\s*use\s+([\w:]+)', line)
            require_match = re.match(r'^\s*require\s+([\w:]+)', line)
            no_match = re.match(r'^\s*no\s+([\w:]+)', line)

            if use_match:
                modules.append({
                    'line_number': i + 1,
                    'type': 'use',
                    'module': use_match.group(1)
                })
            elif require_match:
                modules.append({
                    'line_number': i + 1,
                    'type': 'require',
                    'module': require_match.group(1)
                })
            elif no_match:
                modules.append({
                    'line_number': i + 1,
                    'type': 'no',
                    'module': no_match.group(1)
                })

        return modules

    def _extract_subroutines(self, lines: List[str]) -> List[Dict]:
        """Extract all subroutine definitions."""
        subroutines = []
        for i, line in enumerate(lines):
            sub_match = self.sub_pattern.match(line)
            if sub_match:
                subroutines.append({
                    'line_number': i + 1,
                    'name': sub_match.group(1),
                    'signature': line.strip()
                })
        return subroutines

    def _extract_variables(self, lines: List[str]) -> List[Dict]:
        """Extract all variable declarations and significant assignments."""
        variables = []
        for i, line in enumerate(lines):
            # Skip comments
            if line.strip().startswith('#'):
                continue

            # Variable declarations
            for match in self.my_pattern.finditer(line):
                variables.append({
                    'line_number': i + 1,
                    'keyword': match.group(1),
                    'variable': match.group(2),
                    'type': 'declaration'
                })

            # Package global variables
            our_match = re.search(r'\bour\s+(\$[\w:]+)', line)
            if our_match:
                variables.append({
                    'line_number': i + 1,
                    'keyword': 'our',
                    'variable': our_match.group(1),
                    'type': 'global'
                })

        return variables

    def _extract_all_comments(self, lines: List[str]) -> List[Dict]:
        """Extract all inline comments."""
        comments = []
        for i, line in enumerate(lines):
            comment_match = re.search(r'#(.+)$', line)
            if comment_match and not line.strip().startswith('#!'):
                comments.append({
                    'line_number': i + 1,
                    'content': comment_match.group(1).strip(),
                    'code_before': line[:comment_match.start()].strip() if comment_match.start() > 0 else ''
                })
        return comments

    def _extract_pod(self, lines: List[str]) -> List[Dict]:
        """Extract POD documentation sections."""
        pod_docs = []
        in_pod = False
        current_pod = []

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped in ('=pod', '=head1', '=head2', '=head3', '=over', '=item', '=begin')or re.match(r'^=\w+', stripped):
                in_pod = True
                if not current_pod:
                    current_pod.append((i + 1, stripped))
                else:
                    pod_docs.append({
                        'start_line': current_pod[0][0],
                        'content': '\n'.join(c[1] for c in current_pod)
                    })
                    current_pod = [(i + 1, stripped)]
            elif stripped == '=cut':
                if current_pod:
                    current_pod.append((i + 1, stripped))
                    pod_docs.append({
                        'start_line': current_pod[0][0],
                        'content': '\n'.join(c[1] for c in current_pod)
                    })
                    current_pod = []
                in_pod = False
            elif in_pod:
                current_pod.append((i + 1, stripped))

        # Close any remaining POD
        if current_pod:
            pod_docs.append({
                'start_line': current_pod[0][0],
                'content': '\n'.join(c[1] for c in current_pod)
            })

        return pod_docs

    def _extract_packages(self, lines: List[str]) -> List[str]:
        """Extract all package declarations."""
        packages = []
        for i, line in enumerate(lines):
            pkg_match = self.package_pattern.match(line)
            if pkg_match:
                packages.append(pkg_match.group(1))
        return packages

    def get_line_explanation(self, parse_result: ParseResult, line_number: int) -> Dict:
        """
        Get detailed explanation for a specific line.

        Args:
            parse_result: Result from parse()
            line_number: 1-based line number to explain

        Returns:
            Dict with line info, context, and explanation
        """
        # Find the line
        line_info = None
        for ln, content in parse_result.lines:
            if ln == line_number:
                line_info = content
                break

        if line_info is None:
            return {'error': f'Line {line_number} not found'}

        # Find AST node for this line
        ast_node = None
        for node in parse_result.ast:
            if node.line_number == line_number:
                ast_node = node
                break

        # Check if it's a comment
        comment_info = None
        for c in parse_result.comments:
            if c['line_number'] == line_number:
                comment_info = c
                break

        # Check if it's POD
        pod_info = None
        for p in parse_result.pod_docs:
            if p['start_line'] <= line_number <= p['start_line'] + p['content'].count('\n'):
                pod_info = p
                break

        return {
            'line_number': line_number,
            'content': line_info,
            'ast_type': ast_node.type if ast_node else 'unknown',
            'is_comment': comment_info is not None,
            'is_pod': pod_info is not None,
            'comment_content': comment_info['content'] if comment_info else None,
            'is_module': any(m['line_number'] == line_number for m in parse_result.modules_used),
            'is_subroutine': any(s['line_number'] == line_number for s in parse_result.subroutines),
            'is_variable': any(v['line_number'] == line_number for v in parse_result.variables),
            'is_empty': line_info.strip() == '',
            'is_pod_delimiter': line_info.strip() == '=cut' or line_info.strip().startswith('=')
        }


# Factory function for easy access
def create_parser() -> PerlParser:
    """Create and return a PerlParser instance."""
    return PerlParser()