"""
Modernization Engine
====================
Dedicated module for suggesting and applying Perl and EDA
code modernizations. Separated from the analyzer for modularity.
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ModernizationSuggestion:
    """A suggested code modernization."""
    line_number: int
    pattern_id: str
    category: str
    old_code: str
    new_code: str
    reason: str
    benefits: List[str]
    effort: str  # 'easy', 'medium', 'hard'


class PerlModernizer:
    """
    Suggests modernizations for Perl code, including:
    - Perl version upgrades (5.8 → 5.32+)
    - EDA tool command updates
    - Performance optimizations
    - Best practice improvements
    """

    @staticmethod
    def suggest_perl_modernizations(content: str) -> List[ModernizationSuggestion]:
        """Suggest Perl language modernizations."""
        suggestions = []
        lines = content.split('\n')

        for i, line in enumerate(lines):
            line_num = i + 1

            # Old-style open with bareword filehandle
            open_match = re.search(
                r'\bopen\s*\(\s*(?!my\s+\$)(\w+)\s*,\s*["\']([^"\']+)["\']',
                line
            )
            if open_match:
                suggestions.append(ModernizationSuggestion(
                    line_number=line_num,
                    pattern_id='MODERN-OPEN',
                    category='perl_version',
                    old_code=open_match.group(0),
                    new_code=re.sub(
                        r'open\s*\(\s*(\w+)\s*,\s*["\']([^"\']+)["\']',
                        r'open(my $fh, \'\2\', \1)',
                        open_match.group(0)
                    ),
                    reason='Modern Perl uses lexical filehandles with 3-argument open',
                    benefits=[
                        'Lexical scoping prevents global access',
                        '3-argument open prevents shell injection',
                        'Automatic cleanup on scope exit'
                    ],
                    effort='easy'
                ))

            # print with explicit newline → say
            print_match = re.search(r'\bprint\s+["\'].*?\\n["\']\s*;', line)
            if print_match:
                suggestions.append(ModernizationSuggestion(
                    line_number=line_num,
                    pattern_id='MODERN-SAY',
                    category='perl_version',
                    old_code=print_match.group(0),
                    new_code=print_match.group(0).replace('print ', 'say ', 1).replace('\\n', ''),
                    reason='say() (Perl 5.10+) automatically adds newline',
                    benefits=[
                        'Cleaner code without \\n',
                        'Less typing',
                        'Part of Perl 5.10+ core'
                    ],
                    effort='easy'
                ))

        return suggestions

    @staticmethod
    def suggest_eda_modernizations(content: str) -> List[ModernizationSuggestion]:
        """Suggest EDA tool command modernizations."""
        suggestions = []
        lines = content.split('\n')

        # EDA tool command updates
        eda_updates = {
            'dc_shell': 'genus -legacy_ui',
            'encounter': 'innovus',
            'pt_shell': 'primetime_shell',
            'setMultiCpuUsage': 'set_host_options -max_cores',
            'compile -map_effort high': 'syn_generic; syn_map -effort high'
        }

        for i, line in enumerate(lines):
            line_num = i + 1
            for old_cmd, new_cmd in eda_updates.items():
                if old_cmd in line.lower():
                    suggestions.append(ModernizationSuggestion(
                        line_number=line_num,
                        pattern_id=f'EDA-UPDATE-{old_cmd.upper()}',
                        category='eda_tool',
                        old_code=line.strip(),
                        new_code=line.replace(old_cmd, new_cmd),
                        reason=f'This EDA command has been updated in newer tool versions',
                        benefits=[
                            f'Modern alternative: {new_cmd}',
                            'Better performance and features',
                            'Ongoing vendor support'
                        ],
                        effort='medium'
                    ))
                    break

        return suggestions

    @staticmethod
    def suggest_performance_improvements(content: str) -> List[ModernizationSuggestion]:
        """Suggest performance optimizations."""
        suggestions = []
        lines = content.split('\n')

        for i, line in enumerate(lines):
            line_num = i + 1

            # File slurping
            if re.search(r'(?:join|split|map)\s*\(?\s*["\']?[^"\']*["\']?\s*,\s*<\w+>', line):
                suggestions.append(ModernizationSuggestion(
                    line_number=line_num,
                    pattern_id='PERF-NO-SLURP',
                    category='performance',
                    old_code=line.strip(),
                    new_code='# Use line-by-line iteration instead',
                    reason='Reading entire file into memory is inefficient for large files',
                    benefits=[
                        'Lower memory usage',
                        'Faster processing for large files',
                        'Better scalability'
                    ],
                    effort='medium'
                ))

        return suggestions