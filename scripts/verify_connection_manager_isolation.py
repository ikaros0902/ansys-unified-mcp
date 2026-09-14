"""Empirical Verification Script: Audit Mock Integrity & OS Isolation of tests/unit/test_connection_manager.py.

Usage:
    python scripts/verify_connection_manager_isolation.py

Verifies:
1. Whether any unit test makes un-mocked real TCP socket connections to localhost.
2. Whether test_get_registered_instances_default_directory accesses host disk or calls real psutil.pid_exists.
"""

import sys
sys.path.insert(0, ".")
sys.path.insert(0, "src")

import socket
import psutil
import traceback
import pytest
from pathlib import Path

socket_leaks = []
psutil_leaks = []

real_connect = socket.socket.connect
real_pid_exists = psutil.pid_exists

def spy_connect(self, *args, **kwargs):
    tb = traceback.format_stack()
    caller = "".join(tb[-6:-1])
    socket_leaks.append((args, kwargs, caller))
    return real_connect(self, *args, **kwargs)

def spy_pid_exists(pid):
    tb = traceback.format_stack()
    caller = "".join(tb[-6:-1])
    psutil_leaks.append((pid, caller))
    return real_pid_exists(pid)

socket.socket.connect = spy_connect
psutil.pid_exists = spy_pid_exists

print("=" * 70)
print("1. RUNNING UNIT TESTS WITH REAL OS INTERCEPTION SPIES")
print("=" * 70)

ret = pytest.main(["-q", "tests/unit/test_connection_manager.py"])

print("\n" + "=" * 70)
print("2. AUDIT FINDINGS: NETWORK & PROCESS LEAK DETECTION")
print("=" * 70)

print(f"\n[A] Real socket.connect() calls during tests: {len(socket_leaks)}")
for i, leak in enumerate(socket_leaks, 1):
    print(f"  Leak #{i}: target={leak[0]}")
    print("  Traceback excerpt:")
    for line in leak[2].strip().split("\n"):
        print(f"    {line}")

print(f"\n[B] Real psutil.pid_exists() calls during tests: {len(psutil_leaks)}")
for i, leak in enumerate(psutil_leaks, 1):
    print(f"  Leak #{i}: pid={leak[0]}")

print("\n" + "=" * 70)
print("3. AUDIT FINDINGS: DEFAULT REGISTRY DIRECTORY ISOLATION")
print("=" * 70)
reg_dir = Path("workbench_queue/registry")
dummy_file = reg_dir / "99999.json"
try:
    reg_dir.mkdir(parents=True, exist_ok=True)
    dummy_file.write_text('{"pid": 99999, "name": "canary"}', encoding="utf-8")
    
    from ansys_unified_mcp.connection_manager import ConnectionManager
    cm = ConnectionManager()
    cm.get_registered_instances()  # Called without registry_dir, as in test
    file_survived = dummy_file.exists()
    print(f"Canary file in workbench_queue/registry survived: {file_survived}")
    if not file_survived:
        print("  CRITICAL: Real registry directory was mutated (file unlinked) during un-scoped call!")
finally:
    if dummy_file.exists():
        dummy_file.unlink()

print("\n" + "=" * 70)
if len(socket_leaks) > 0 or not file_survived:
    print("FINAL VERDICT: FAIL - Mock isolation violations empirically confirmed.")
else:
    print("FINAL VERDICT: PASS - Fully isolated.")
print("=" * 70)

sys.exit(0 if (len(socket_leaks) == 0 and file_survived) else 1)
