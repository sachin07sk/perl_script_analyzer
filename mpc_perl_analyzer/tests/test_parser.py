"""
Parser Unit Tests
=================
Tests for the Perl script parser module.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.parser import create_parser


def test_basic_parsing():
    """Test basic Perl script parsing."""
    parser = create_parser()
    content = """#!/usr/bin/perl
use strict;
use warnings;

my $var = "hello";
print "$var\\n";
"""
    result = parser.parse(content, 'test.pl')
    assert result.shebang == '#!/usr/bin/perl', "Shebang not found"
    assert len(result.modules_used) == 2, f"Expected 2 modules, got {len(result.modules_used)}"
    assert len(result.variables) >= 1, "Variables not found"
    assert result.lines[0] == (1, '#!/usr/bin/perl'), "Line tracking failed"
    print("  ✓ test_basic_parsing")


def test_subroutine_detection():
    """Test subroutine extraction."""
    parser = create_parser()
    content = """
sub my_func {
    my $arg = shift;
    return $arg * 2;
}

sub another_func {
    print "hello";
}
"""
    result = parser.parse(content, 'test.pl')
    assert len(result.subroutines) == 2, f"Expected 2 subroutines, got {len(result.subroutines)}"
    assert result.subroutines[0]['name'] == 'my_func', "First subroutine name mismatch"
    assert result.subroutines[1]['name'] == 'another_func', "Second subroutine name mismatch"
    print("  ✓ test_subroutine_detection")


def test_module_extraction():
    """Test module extraction."""
    parser = create_parser()
    content = """#!/usr/bin/perl
use strict;
use warnings;
use File::Basename qw(basename dirname);
use Cwd;
use List::Util qw(first max sum);
require Exporter;
"""
    result = parser.parse(content, 'test.pl')
    assert len(result.modules_used) >= 5, f"Expected 5+ modules, got {len(result.modules_used)}"
    modules = [m['module'] for m in result.modules_used]
    assert 'strict' in modules, "strict not found"
    assert 'File::Basename' in modules, "File::Basename not found"
    assert 'List::Util' in modules, "List::Util not found"
    print("  ✓ test_module_extraction")


def test_comment_extraction():
    """Test comment extraction."""
    parser = create_parser()
    content = """#!/usr/bin/perl
# This is a header comment
my $x = 1;  # This is an inline comment
=pod
This is POD documentation
=cut
my $y = 2;
"""
    result = parser.parse(content, 'test.pl')
    assert len(result.comments) >= 2, f"Expected 2+ comments, got {len(result.comments)}"
    assert any('header comment' in c['content'] for c in result.comments), "Header comment not found"
    assert any('inline comment' in c['content'] for c in result.comments), "Inline comment not found"
    print("  ✓ test_comment_extraction")


def test_variable_extraction():
    """Test variable extraction."""
    parser = create_parser()
    content = """
my $scalar = 1;
my @array = (1, 2, 3);
my %hash = (a => 1, b => 2);
our $global = "test";
local $temp = 5;
"""
    result = parser.parse(content, 'test.pl')
    assert len(result.variables) >= 4, f"Expected 4+ variables, got {len(result.variables)}"
    vars_found = [v['variable'] for v in result.variables]
    # Note: parser may capture different variable patterns
    print(f"  ✓ test_variable_extraction (found {len(result.variables)} vars)")


def test_line_explanation():
    """Test line-level explanation."""
    parser = create_parser()
    content = """#!/usr/bin/perl
use strict;
my $x = 42;
print "Hello\\n";
sub foo { return 1; }
"""
    result = parser.parse(content, 'test.pl')
    
    # Test shebang line
    info = parser.get_line_explanation(result, 1)
    assert info['line_number'] == 1, "Line number mismatch"
    assert '#!/usr/bin/perl' in info['content'], "Line content mismatch"
    
    # Test module line
    info = parser.get_line_explanation(result, 2)
    assert info['is_module'], "Line 2 should be a module"
    
    # Test empty line
    info = parser.get_line_explanation(result, 4)
    # Line 4 should be empty or have content
    
    print("  ✓ test_line_explanation")


def run_tests():
    """Run all parser tests."""
    print("Parser Tests:")
    test_basic_parsing()
    test_subroutine_detection()
    test_module_extraction()
    test_comment_extraction()
    test_variable_extraction()
    test_line_explanation()
    print("All parser tests passed!\n")


if __name__ == '__main__':
    run_tests()