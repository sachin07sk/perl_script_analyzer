"""
Test script for MPC Perl Analyzer.
Tests parsing, analysis, EDA detection, and report generation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.parser import create_parser
from src.analyzer import create_analyzer
from src.pdf_generator import create_pdf_generator


def test_parser():
    """Test the Perl parser with sample script."""
    print("=" * 60)
    print("TEST 1: Parser Test")
    print("=" * 60)

    parser = create_parser()
    script_path = os.path.join(os.path.dirname(__file__), 
                               'sample_scripts', 'vlsa_timing_analysis.pl')
    
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    result = parser.parse(content, 'vlsa_timing_analysis.pl')
    
    print(f"  Lines: {len(result.lines)}")
    print(f"  Shebang: {result.shebang}")
    print(f"  Subroutines: {len(result.subroutines)}")
    print(f"  Variables: {len(result.variables)}")
    print(f"  Comments: {len(result.comments)}")
    print(f"  AST Nodes: {len(result.ast)}")
    
    # Show AST types
    ast_types = {}
    for node in result.ast:
        ast_types[node.type] = ast_types.get(node.type, 0) + 1
    print(f"  AST Types: {ast_types}")
    
    print("  PASSED!\n")
    return True


def test_analyzer():
    """Test the analyzer with the sample VLSI script."""
    print("=" * 60)
    print("TEST 2: Analyzer Test (VLSI/EDA Script)")
    print("=" * 60)

    analyzer = create_analyzer()
    script_path = os.path.join(os.path.dirname(__file__), 
                               'sample_scripts', 'vlsa_timing_analysis.pl')
    
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    result = analyzer.analyze(content, 'vlsa_timing_analysis.pl')
    
    print(f"  Total Issues: {result.summary['total_issues']}")
    print(f"  Severity: {result.summary['severity_summary']}")
    print(f"  Script Type: {result.summary['script_type']}")
    
    if result.summary['eda_tools_found']:
        print(f"  EDA Tools Found: {', '.join(result.summary['eda_tools_found'])}")
    
    print(f"  EDA Script Types: {len(result.eda_script_types)}")
    for e in result.eda_script_types:
        print(f"    - {e['category']}: {e['eda_tool']}")
    
    print(f"  Line Explanations: {len(result.line_explanations)}")
    
    # Show top issues
    print("\n  Top Issues:")
    for issue in result.issues[:5]:
        print(f"    Line {issue.line_number:4d}: [{issue.severity:8s}] {issue.description}")
    
    print("  PASSED!\n")
    return True


def test_line_explanation():
    """Test getting line-specific explanations."""
    print("=" * 60)
    print("TEST 3: Line Explanation Test")
    print("=" * 60)

    analyzer = create_analyzer()
    script_path = os.path.join(os.path.dirname(__file__), 
                               'sample_scripts', 'vlsa_timing_analysis.pl')
    
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Explain line 18 (old-style open)
    line_info = analyzer.get_line_explanation(18, content)
    print(f"  Line 18:")
    print(f"    Content: '{line_info.get('content', 'N/A')}'")
    print(f"    Type: {line_info.get('type', 'N/A')}")
    print(f"    Explanation: {line_info.get('explanation', 'N/A')}")
    print(f"    Issues: {len(line_info.get('issues', []))}")
    for iss in line_info.get('issues', []):
        print(f"      [{iss['severity']}] {iss['description']}")
        print(f"      Modern Code: {iss.get('modern_code', 'N/A')}")

    # Explain line 93 (eval security)
    line_info = analyzer.get_line_explanation(93, content)
    print(f"\n  Line 93:")
    print(f"    Content: '{line_info.get('content', 'N/A')}'")
    print(f"    Type: {line_info.get('type', 'N/A')}")
    print(f"    Explanation: {line_info.get('explanation', 'N/A')}")
    for iss in line_info.get('issues', []):
        print(f"      [{iss['severity']}] {iss['description']}")
        print(f"      Fix: {iss.get('explanation', 'N/A')[:80]}...")

    print("  PASSED!\n")
    return True


def test_report_generation():
    """Test report generation."""
    print("=" * 60)
    print("TEST 4: Report Generation Test")
    print("=" * 60)

    analyzer = create_analyzer()
    pdf_gen = create_pdf_generator('output')
    
    script_path = os.path.join(os.path.dirname(__file__), 
                               'sample_scripts', 'vlsa_timing_analysis.pl')
    
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    result = analyzer.analyze(content, 'vlsa_timing_analysis.pl')
    
    # Generate full report
    path = pdf_gen.generate_full_report(result)
    print(f"  Full Report: {path}")
    print(f"    Size: {os.path.getsize(path)} bytes")
    
    # Generate line-by-line report
    path2 = pdf_gen.generate_line_by_line_report(result)
    print(f"  Line-by-Line: {path2}")
    print(f"    Size: {os.path.getsize(path2)} bytes")
    
    # Generate selected lines report
    path3 = pdf_gen.generate_selected_lines_report(result, [1, 18, 93, 103])
    print(f"  Selected Lines: {path3}")
    print(f"    Size: {os.path.getsize(path3)} bytes")

    print("  PASSED!\n")
    return True


def test_general_perl_script():
    """Test with a general (non-EDA) Perl script analysis."""
    print("=" * 60)
    print("TEST 5: General Perl Script Analysis")
    print("=" * 60)

    analyzer = create_analyzer()
    
    # Create a simple Perl script inline
    perl_code = """#!/usr/bin/perl
use strict;
use warnings;
use File::Basename;

my $filename = "test.txt";
my $count = 0;

# Process the file
open(my $fh, '<', $filename) or die "Cannot open $filename: $!";
while (my $line = <$fh>) {
    chomp $line;
    $count++;
    print "Line $count: $line\\n";
}
close($fh);

print "Total lines: $count\\n";

sub process_data {
    my ($data, $options) = @_;
    my $result = {};
    
    foreach my $key (keys %$data) {
        if ($options->{filter} && $key =~ /$options->{filter}/) {
            $result->{$key} = $data->{$key};
        }
    }
    
    return $result;
}
"""

    result = analyzer.analyze(perl_code, 'test_script.pl')
    
    print(f"  Total Issues: {result.summary['total_issues']}")
    print(f"  Severity: {result.summary['severity_summary']}")
    print(f"  Script Type: {result.summary['script_type']}")
    print(f"  Subroutines: {result.summary['subroutines_count']}")
    print(f"  Has strict: {result.summary['has_strict']}")
    print(f"  Has warnings: {result.summary['has_warnings']}")
    
    print("  PASSED!\n")
    return True


def run_all_tests():
    """Run all tests."""
    print("\n\n" + "=" * 60)
    print("MPC Protocol - Perl Script Analyzer Test Suite")
    print("=" * 60 + "\n")
    
    tests = [
        test_parser,
        test_analyzer,
        test_line_explanation,
        test_report_generation,
        test_general_perl_script
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  FAILED with exception: {e}\n")
            failed += 1
    
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed, {len(tests)} total")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)