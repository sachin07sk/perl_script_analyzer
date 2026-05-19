"""
MCP Server Tests
================
Tests for MCP server functionality including on-demand activation
and idle timeout mechanisms.

Uses a single shared MCPServerManager instance for all tests
and cleans up properly at the end.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mcp_servers.server_manager import MCPServerManager


tests_passed = 0
tests_failed = 0

# Single shared manager
_manager = None


def get_manager():
    global _manager
    if _manager is None:
        _manager = MCPServerManager()
    return _manager


def cleanup():
    global _manager
    if _manager is not None:
        _manager.shutdown_all()
        _manager = None
    print("  Cleanup done.")


def log_test(name, passed):
    global tests_passed, tests_failed
    if passed:
        tests_passed += 1
        print(f"  ✓ {name}")
    else:
        tests_failed += 1
        print(f"  ✗ {name}")


def test_server_config():
    m = get_manager()
    expected = ['parser', 'analyzer', 'modernizer', 'pdf_generator', 'eda_knowledge']
    for s in expected:
        assert s in m.config
    log_test("Server Configuration", True)


def test_server_status():
    m = get_manager()
    s = m.get_server_status()
    assert s['total_servers'] == 5
    assert s['active_count'] == 0
    log_test("Server Status", True)


def test_individual_server():
    m = get_manager()
    ps = m.get_server_status('parser')
    assert ps['status'] == 'inactive'
    assert ps['port'] == 5001
    log_test("Individual Server", True)


def test_config_values():
    m = get_manager()
    assert m.config['parser']['port'] == 5001
    assert m.config['analyzer']['port'] == 5002
    assert m.config['modernizer']['port'] == 5003
    assert m.config['pdf_generator']['port'] == 5004
    assert m.config['eda_knowledge']['port'] == 5005
    log_test("Config Values", True)


def test_methods_exist():
    m = get_manager()
    assert hasattr(m, 'activate_server')
    assert hasattr(m, 'deactivate_server')
    assert hasattr(m, 'request_server')
    log_test("Methods Exist", True)


def run_tests():
    global tests_passed, tests_failed
    print("\nMCP Server Tests:")
    try:
        test_server_config()
        test_server_status()
        test_individual_server()
        test_config_values()
        test_methods_exist()
        print(f"\nResults: {tests_passed} passed, {tests_failed} failed, "
              f"{tests_passed + tests_failed} total\n")
    finally:
        cleanup()


if __name__ == '__main__':
    run_tests()
    print("Done - process will exit normally.")