#!/usr/bin/perl
#
# timing_analysis.pl - VLSI Timing Analysis Script
# 
# This script analyzes timing reports from Synopsys PrimeTime
# and generates a summary of timing violations.
#
# Usage: perl timing_analysis.pl <timing_report> <output_file>

# Legacy Perl: Missing strict/warnings

# Configuration
$timing_threshold = 0.5;  # Timing violation threshold in ns
$max_paths = 100;
$search_directory = "./timing_reports";

# Open the timing report file (old-style bareword filehandle)
open(REPORT, "< $ARGV[0]") or die "Cannot open $ARGV[0]";
open(OUT, "> $ARGV[1]") or die "Cannot open $ARGV[1]";

print OUT "Timing Analysis Report\n";
print OUT "=" x 40 . "\n";

# Read and parse the timing report
$violation_count = 0;
$total_paths = 0;
$worst_slack = 0;
$worst_path = "";

while (<REPORT>) {
    chomp;
    
    # Skip comments and empty lines
    next if /^#/;
    next if /^\s*$/;
    
    $total_paths++;
    
    # Parse timing path information
    if (/Path\s+(\d+):\s+(.+)/) {
        $path_id = $1;
        $path_name = $2;
        print OUT "Path $path_id: $path_name\n";
    }
    
    # Check for slack values
    if (/slack\s+([-+]?\d+\.?\d*)/) {
        $slack = $1;
        print OUT "  Slack: ${slack}ns\n";
        
        if ($slack < $timing_threshold) {
            $violation_count++;
            print OUT "  !! TIMING VIOLATION: Slack $slack ns < $timing_threshold ns\n";
            
            if ($slack < $worst_slack) {
                $worst_slack = $slack;
                $worst_path = $path_name;
            }
        }
    }
    
    # Check EDA tool patterns - Synopsys DC style
    if (/dc_shell|synopsys|pt_shell/) {
        print OUT "  Note: EDA tool command detected\n";
    }
    
    # Check for TCL integration
    if (/tclsh|tcl_set|tcl_get/) {
        print OUT "  Note: TCL integration detected\n";
    }
}

# Generate summary
print OUT "\n" . "=" x 40 . "\n";
print OUT "SUMMARY\n";
print OUT "=" x 40 . "\n";
print OUT "Total Paths Analyzed: $total_paths\n";
print OUT "Timing Violations: $violation_count\n";
print OUT "Worst Slack: ${worst_slack}ns\n";
print OUT "Worst Path: $worst_path\n";

# Calculate violation percentage
if ($total_paths > 0) {
    $violation_pct = ($violation_count / $total_paths) * 100;
    print OUT "Violation Percentage: ${violation_pct}%\n";
}

# Open worst path report
if ($worst_path ne "") {
    print OUT "\nDetailed analysis of worst path: $worst_path\n";
    
    # Old-style: using eval on string (security concern)
    eval "print OUT 'Worst path: $worst_path'";
    
    # System call with variable (security concern)  
    system("echo 'Reporting worst path: $worst_path'");
}

# Close files
close(REPORT);
close(OUT);

print "Analysis complete. Results written to $ARGV[1]\n";

# Subroutine to parse timing path (for demonstration)
sub parse_timing_path {
    my $line = shift;
    my ($startpoint, $endpoint, $delay);
    
    if ($line =~ /Startpoint:\s+(.+)/) {
        $startpoint = $1;
    }
    if ($line =~ /Endpoint:\s+(.+)/) {
        $endpoint = $1;
    }
    if ($line =~ /Data\s+Delay:\s+([-+]?\d+\.?\d*)/) {
        $delay = $1;
    }
    
    return ($startpoint, $endpoint, $delay);
}

# Subroutine to filter paths by slack threshold
sub filter_paths {
    my @paths = @_;
    my @filtered;
    
    foreach my $path (@paths) {
        if ($path->{slack} <= $timing_threshold) {
            push @filtered, $path;
        }
    }
    
    return @filtered;
}

# Subroutine to generate EDA tool commands
sub generate_eda_commands {
    my $design = shift;
    
    # Generate Synopsys DC synthesis commands
    print OUT "analyze -library WORK -format verilog {${design}.v}\n";
    print OUT "elaborate $design\n";
    print OUT "compile -map_effort high\n";
    
    # Generate Innovus P&R commands
    print OUT "floorplan -coreMargins 10\n";
    print OUT "place_opt_design\n";
    print OUT "ccopt_design\n";
    print OUT "route_design\n";
}

1;