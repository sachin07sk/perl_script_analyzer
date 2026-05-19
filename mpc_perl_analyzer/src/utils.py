"""
Utility functions for MPC Perl Analyzer.

Provides helper functions for file operations, logging, 
and common transformations used across the MPC Protocol.
"""

import re
import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any


def read_file(file_path: str) -> Optional[str]:
    """
    Read a file and return its contents as a string.

    Args:
        file_path: Path to the file to read

    Returns:
        File contents as string, or None if file doesn't exist
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None


def write_file(file_path: str, content: str) -> bool:
    """
    Write content to a file.

    Args:
        file_path: Path to write to
        content: Content to write

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing file {file_path}: {e}")
        return False


def split_into_lines(content: str) -> List[str]:
    """
    Split script content into individual lines with line numbers.

    Args:
        content: Script content as string

    Returns:
        List of (line_number, line_content) tuples
    """
    lines = content.split('\n')
    return [(i + 1, line) for i, line in enumerate(lines)]


def get_line(content: str, line_number: int) -> Optional[str]:
    """
    Get a specific line from content.

    Args:
        content: Script content
        line_number: 1-based line number

    Returns:
        The line content or None if line doesn't exist
    """
    lines = content.split('\n')
    if 1 <= line_number <= len(lines):
        return lines[line_number - 1]
    return None


def get_line_range(content: str, start: int, end: int) -> List[str]:
    """
    Get a range of lines from content.

    Args:
        content: Script content
        start: Start line number (1-based, inclusive)
        end: End line number (1-based, inclusive)

    Returns:
        List of (line_number, content) tuples
    """
    lines = content.split('\n')
    result = []
    for i in range(max(1, start), min(end + 1, len(lines) + 1)):
        result.append((i, lines[i - 1]))
    return result


def compute_hash(content: str) -> str:
    """
    Compute MD5 hash of content for caching/identity.

    Args:
        content: Content to hash

    Returns:
        MD5 hash string
    """
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def extract_comments(content: str) -> List[Dict]:
    """
    Extract comments from Perl script.

    Args:
        content: Script content

    Returns:
        List of comment dicts with line_number, type, and content
    """
    comments = []
    lines = content.split('\n')
    
    in_pod = False
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # POD documentation
        if line.strip() == '=pod' or line.strip() == '=head1' or line.strip() == '=head2' or line.strip() == '=over' or line.strip() == '=item' or line.strip() == '=begin':
            in_pod = True
            comments.append({
                'line_number': line_num,
                'type': 'pod_start',
                'content': line.strip()
            })
            continue
        
        if in_pod:
            if line.strip() == '=cut':
                in_pod = False
                comments.append({
                    'line_number': line_num,
                    'type': 'pod_end',
                    'content': '=cut'
                })
            else:
                comments.append({
                    'line_number': line_num,
                    'type': 'pod',
                    'content': line.strip()
                })
            continue
        
        # Single-line comment
        comment_match = re.search(r'#(.+)$', line)
        if comment_match:
            comments.append({
                'line_number': line_num,
                'type': 'inline',
                'content': comment_match.group(1).strip(),
                'code_before': line[:comment_match.start()].strip()
            })
    
    return comments


def detect_embedding_pattern(content: str) -> Dict[str, bool]:
    """
    Detect embedded languages/patterns in Perl script.

    Args:
        content: Script content

    Returns:
        Dict of detected patterns
    """
    patterns = {
        'has_tcl_code': bool(re.search(r'\bTcl\b|\btclsh\b|\bwish\b', content, re.IGNORECASE)),
        'has_system_calls': bool(re.search(r'\bsystem\s*\(|\bqx\s*\(|\bbacktick\b|`[^`]+`', content)),
        'has_python_embed': bool(re.search(r'use\s+Inline::Python|use\s+Python', content)),
        'has_c_embed': bool(re.search(r'use\s+Inline::C|use\s+XSLoader|use\s+DynaLoader', content)),
        'has_eda_commands': bool(re.search(r'\bdc_shell\b|\bencounter\b|\binnovus\b|\bpt_shell\b|\bicc2?\b|\bgenus\b|\btempus\b', content, re.IGNORECASE)),
    }
    return patterns


def format_timestamp() -> str:
    """Return current timestamp for reports."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def truncate_string(s: str, max_length: int = 100) -> str:
    """Truncate string to max_length with ellipsis."""
    if len(s) <= max_length:
        return s
    return s[:max_length - 3] + "..."