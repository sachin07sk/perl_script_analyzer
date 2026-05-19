#!/usr/bin/perl
use strict;
use warnings;
use JSON;
use IO::Socket::INET;
use POSIX qw(strftime);

# ============================================================
#  MCP Server Test Suite for Perl Script Analysis
#  Usage: perl test_mcp_server.pl
# ============================================================

# ---------- CONFIGURATION ----------
my $MCP_HOST = '127.0.0.1';   # Change if MCP server is remote
my $MCP_PORT = 3000;           # Change to your MCP server port
my $TIMEOUT  = 10;             # seconds
my $LOG_FILE = 'mcp_test_results.log';

# -----------------------------------

my $pass_count = 0;
my $fail_count = 0;
my @results;

# ============================================================
# HELPER: Logger
# ============================================================
sub log_result {
    my ($test_name, $status, $detail) = @_;
    my $timestamp = strftime("%Y-%m-%d %H:%M:%S", localtime);
    my $line = "[$timestamp] [$status] $test_name => $detail";
    push @results, $line;
    print "$line\n";
    if ($status eq 'PASS') { $pass_count++; }
    else                   { $fail_count++; }
}

# ============================================================
# HELPER: Send JSON-RPC request to MCP server
# ============================================================
sub send_mcp_request {
    my ($method, $params) = @_;

    my $socket = IO::Socket::INET->new(
        PeerAddr => $MCP_HOST,
        PeerPort => $MCP_PORT,
        Proto    => 'tcp',
        Timeout  => $TIMEOUT,
    );

    unless ($socket) {
        return (0, "Cannot connect to MCP server at $MCP_HOST:$MCP_PORT — $!");
    }

    my $request = encode_json({
        jsonrpc => "2.0",
        id      => 1,
        method  => $method,
        params  => $params // {},
    });

    print $socket "$request\n";

    my $response = '';
    eval {
        local $SIG{ALRM} = sub { die "timeout\n" };
        alarm($TIMEOUT);
        while (my $line = <$socket>) {
            $response .= $line;
            last if $response =~ /\}/;  # basic end-of-JSON detection
        }
        alarm(0);
    };

    close($socket);

    if ($@ eq "timeout\n") {
        return (0, "Request timed out after ${TIMEOUT}s");
    }

    my $decoded;
    eval { $decoded = decode_json($response) };
    if ($@) {
        return (0, "Invalid JSON response: $response");
    }

    return (1, $decoded);
}

# ============================================================
# TEST 1: TCP Connectivity
# ============================================================
sub test_connectivity {
    print "\n--- TEST 1: TCP Connectivity ---\n";
    my $socket = IO::Socket::INET->new(
        PeerAddr => $MCP_HOST,
        PeerPort => $MCP_PORT,
        Proto    => 'tcp',
        Timeout  => $TIMEOUT,
    );
    if ($socket) {
        close($socket);
        log_result("TCP Connectivity", "PASS", "Connected to $MCP_HOST:$MCP_PORT");
    } else {
        log_result("TCP Connectivity", "FAIL", "Cannot connect — $!");
    }
}

# ============================================================
# TEST 2: MCP Handshake (initialize)
# ============================================================
sub test_handshake {
    print "\n--- TEST 2: MCP Handshake ---\n";
    my ($ok, $resp) = send_mcp_request("initialize", {
        protocolVersion => "2024-11-05",
        clientInfo      => { name => "PerlTestClient", version => "1.0" },
    });

    if (!$ok) {
        log_result("MCP Handshake", "FAIL", $resp);
        return;
    }

    if (ref $resp eq 'HASH' && exists $resp->{result}) {
        log_result("MCP Handshake", "PASS", "Server responded with protocol handshake");
    } else {
        log_result("MCP Handshake", "FAIL", "Unexpected response: " . encode_json($resp));
    }
}

# ============================================================
# TEST 3: List Available Tools
# ============================================================
sub test_list_tools {
    print "\n--- TEST 3: List Available Tools ---\n";
    my ($ok, $resp) = send_mcp_request("tools/list", {});

    if (!$ok) {
        log_result("List Tools", "FAIL", $resp);
        return;
    }

    if (ref $resp eq 'HASH' && exists $resp->{result}{tools}) {
        my @tools = @{ $resp->{result}{tools} };
        my $tool_names = join(", ", map { $_->{name} } @tools);
        log_result("List Tools", "PASS", scalar(@tools) . " tools found: $tool_names");
    } else {
        log_result("List Tools", "FAIL", "No tools array in response");
    }
}

# ============================================================
# TEST 4: Analyze a Modern (valid) Perl Script
# ============================================================
sub test_analyze_modern_script {
    print "\n--- TEST 4: Analyze Modern Perl Script ---\n";

    my $modern_perl = <<'END_PERL';
#!/usr/bin/perl
use strict;
use warnings;
use feature 'say';

my @items = qw(apple banana cherry);
for my $item (@items) {
    say "Item: $item";
}
END_PERL

    my ($ok, $resp) = send_mcp_request("tools/call", {
        name      => "analyze_perl_script",
        arguments => { code => $modern_perl, filename => "modern_sample.pl" },
    });

    if (!$ok) {
        log_result("Analyze Modern Script", "FAIL", $resp);
        return;
    }

    if (ref $resp eq 'HASH' && exists $resp->{result}) {
        log_result("Analyze Modern Script", "PASS", "Analysis returned successfully");
    } else {
        log_result("Analyze Modern Script", "FAIL", "Unexpected response structure");
    }
}

# ============================================================
# TEST 5: Detect OLD / Deprecated Perl Patterns
# ============================================================
sub test_detect_old_patterns {
    print "\n--- TEST 5: Detect Old/Deprecated Perl Patterns ---\n";

    # Script with intentionally OLD patterns
    my $old_perl = <<'END_OLD';
#!/usr/bin/perl
# No strict, no warnings — old style

&mysub();               # Old-style sub call with &
$x = 1;                 # No my/our declaration
*glob = *other;         # Typeglob manipulation
require "oldlib.pl";    # require with quotes (old style)
local($x, $y) = @_;    # Overuse of local
open(FILE, ">out.txt"); # Old 2-arg open
print FILE "hello\n";   # Old bareword filehandle
close(FILE);

sub mysub {
    return 1;
}
END_OLD

    my ($ok, $resp) = send_mcp_request("tools/call", {
        name      => "analyze_perl_script",
        arguments => { code => $old_perl, filename => "old_sample.pl" },
    });

    if (!$ok) {
        log_result("Detect Old Patterns", "FAIL", $resp);
        return;
    }

    # Check if response flags deprecated patterns
    my $result_text = encode_json($resp->{result} // {});
    if ($result_text =~ /deprecated|old|warn|issue|strict/i) {
        log_result("Detect Old Patterns", "PASS", "Server correctly flagged old patterns");
    } else {
        log_result("Detect Old Patterns", "WARN", "Server responded but did not flag old patterns — check manually");
    }
}

# ============================================================
# TEST 6: Error Handling — Send Malformed Perl
# ============================================================
sub test_malformed_script {
    print "\n--- TEST 6: Malformed Perl Input ---\n";

    my $bad_perl = 'sub broken { my $x = ; }';  # Syntax error

    my ($ok, $resp) = send_mcp_request("tools/call", {
        name      => "analyze_perl_script",
        arguments => { code => $bad_perl, filename => "broken.pl" },
    });

    if (!$ok) {
        log_result("Malformed Script Handling", "FAIL", $resp);
        return;
    }

    my $result_text = encode_json($resp // {});
    if ($result_text =~ /error|syntax|invalid/i) {
        log_result("Malformed Script Handling", "PASS", "Server correctly reported syntax error");
    } else {
        log_result("Malformed Script Handling", "WARN", "Server did not flag syntax error — verify manually");
    }
}

# ============================================================
# TEST 7: Empty Script Edge Case
# ============================================================
sub test_empty_script {
    print "\n--- TEST 7: Empty Script Edge Case ---\n";

    my ($ok, $resp) = send_mcp_request("tools/call", {
        name      => "analyze_perl_script",
        arguments => { code => "", filename => "empty.pl" },
    });

    if (!$ok) {
        log_result("Empty Script Edge Case", "FAIL", $resp);
        return;
    }

    if (ref $resp eq 'HASH') {
        log_result("Empty Script Edge Case", "PASS", "Server handled empty input without crashing");
    } else {
        log_result("Empty Script Edge Case", "FAIL", "Unexpected response for empty input");
    }
}

# ============================================================
# TEST 8: Response Time / Latency Check
# ============================================================
sub test_latency {
    print "\n--- TEST 8: Response Latency ---\n";

    my $start = time();
    my ($ok, $resp) = send_mcp_request("tools/list", {});
    my $elapsed = time() - $start;

    if (!$ok) {
        log_result("Latency Check", "FAIL", $resp);
        return;
    }

    if ($elapsed <= $TIMEOUT) {
        log_result("Latency Check", "PASS", "Response in ${elapsed}s (threshold: ${TIMEOUT}s)");
    } else {
        log_result("Latency Check", "FAIL", "Response took ${elapsed}s — exceeded ${TIMEOUT}s threshold");
    }
}

# ============================================================
# WRITE RESULTS TO LOG FILE
# ============================================================
sub write_log {
    open(my $fh, '>', $LOG_FILE) or die "Cannot write log: $!";
    print $fh "=" x 60 . "\n";
    print $fh "MCP SERVER TEST RESULTS\n";
    print $fh "Run at: " . strftime("%Y-%m-%d %H:%M:%S", localtime) . "\n";
    print $fh "Server: $MCP_HOST:$MCP_PORT\n";
    print $fh "=" x 60 . "\n\n";
    print $fh "$_\n" for @results;
    print $fh "\n" . "=" x 60 . "\n";
    print $fh "SUMMARY: $pass_count PASSED | $fail_count FAILED\n";
    print $fh "=" x 60 . "\n";
    close($fh);
}

# ============================================================
# MAIN — Run All Tests
# ============================================================
print "=" x 60 . "\n";
print " MCP SERVER TEST SUITE — Perl Script Analyzer\n";
print " Target: $MCP_HOST:$MCP_PORT\n";
print "=" x 60 . "\n";

test_connectivity();
test_handshake();
test_list_tools();
test_analyze_modern_script();
test_detect_old_patterns();
test_malformed_script();
test_empty_script();
test_latency();

# Final Summary
print "\n" . "=" x 60 . "\n";
print " RESULTS: $pass_count PASSED | $fail_count FAILED\n";
print "=" x 60 . "\n";

write_log();
print "\nFull results saved to: $LOG_FILE\n";

exit($fail_count > 0 ? 1 : 0);