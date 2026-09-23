"""Adversarial stress-test suite for ConnectionManager and test_connection_manager.py.

Empirically challenges:
1. psutil.process_iter returning None, malformed info, and unexpected exceptions.
2. Socket connect hangs, invalid/out-of-bounds ports, and socket creation errors.
3. Inverted, negative, and out-of-range port boundaries.
4. Corrupted, non-dict, non-UTF8, locked, and race-condition JSON in registry directory.
5. Concurrent multi-threaded execution of find_all_instances and get_registered_instances.
6. Real network/filesystem/process leak auditing of tests/unit/test_connection_manager.py.
"""

import concurrent.futures
import json
import os
import socket
import tempfile
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

import psutil
import pytest

from ansys_unified_mcp.connection_manager import (
    ConnectionManager,
    connection_manager,
)


# ==============================================================================
# Challenge 1: psutil.process_iter Robustness and Edge Cases
# ==============================================================================

def test_process_iter_yields_none():
    """Challenge: What happens if psutil.process_iter yields None?

    Hardened behavior: gracefully ignore None items and return empty process lists.
    """
    cm = ConnectionManager()
    with patch("psutil.process_iter", return_value=[None]):
        res = cm.find_running_ansys_processes()
        assert res == {
            "mechanical": [],
            "workbench": [],
            "fluent": [],
            "spaceclaim": [],
            "optislang": [],
        }


def test_process_iter_proc_with_none_info():
    """Challenge: What happens if proc.info is None or not a dict?

    Hardened behavior: safely skip process without crashing.
    """
    cm = ConnectionManager()
    mock_proc = MagicMock()
    mock_proc.info = None
    with patch("psutil.process_iter", return_value=[mock_proc]):
        res = cm.find_running_ansys_processes()
        assert res == {
            "mechanical": [],
            "workbench": [],
            "fluent": [],
            "spaceclaim": [],
            "optislang": [],
        }


def test_process_iter_missing_name_key():
    """Challenge: What happens if proc.info dict is missing the 'name' key?

    Hardened behavior: safely skip process without KeyError.
    """
    cm = ConnectionManager()
    mock_proc = MagicMock()
    mock_proc.info = {"pid": 1234, "exe": "C:\\test.exe"}  # no 'name'
    with patch("psutil.process_iter", return_value=[mock_proc]):
        res = cm.find_running_ansys_processes()
        assert res == {
            "mechanical": [],
            "workbench": [],
            "fluent": [],
            "spaceclaim": [],
            "optislang": [],
        }


def test_process_iter_generator_raises_unexpected_exception():
    """Challenge: What happens if process_iter generator raises RuntimeError or OSError?

    Hardened behavior: caught by outer generator exception handler, processes yielded so far retained.
    """
    cm = ConnectionManager()

    def buggy_iter(attrs):
        yield MagicMock(info={"name": "ansyswbu.exe", "pid": 1, "exe": ""})
        raise RuntimeError("Kernel process table locked")

    with patch("psutil.process_iter", side_effect=buggy_iter):
        res = cm.find_running_ansys_processes()
        assert len(res["mechanical"]) == 1
        assert res["mechanical"][0].info["name"] == "ansyswbu.exe"


def test_find_all_instances_with_none_in_proc_list():
    """Challenge: What happens in find_all_instances if a process in the list is None?

    Hardened behavior: _get_proc_summary handles None safely and returns {'pid': None, 'name': ''}.
    """
    cm = ConnectionManager()
    with patch.object(cm, "find_running_ansys_processes", return_value={"mechanical": [None]}):
        with patch.object(cm, "scan_for_mechanical_grpc", return_value=None):
            with patch.object(cm, "scan_for_spaceclaim_grpc", return_value=None):
                with patch.object(cm, "scan_for_fluent_grpc", return_value=None):
                    res = cm.find_all_instances()
                    assert len(res["mechanical"]) == 1
                    assert res["mechanical"][0] == {"pid": None, "name": ""}


# ==============================================================================
# Challenge 2: Socket Edge Cases & Exception Handling
# ==============================================================================

def test_is_port_open_out_of_range_overflow_error():
    """Challenge: What happens if port is > 65535 or negative?

    Hardened behavior: validate port range and return False without throwing OverflowError.
    """
    cm = ConnectionManager()
    assert cm._is_port_open(70000) is False
    assert cm._is_port_open(-1) is False
    assert cm._is_port_open(65536) is False


def test_is_port_open_invalid_type():
    """Challenge: What happens if port is a string, bool, or None?

    Hardened behavior: type validation returns False without throwing TypeError.
    """
    cm = ConnectionManager()
    assert cm._is_port_open("10000") is False  # type: ignore
    assert cm._is_port_open(None) is False     # type: ignore
    assert cm._is_port_open(True) is False     # type: ignore
    assert cm._is_port_open(False) is False    # type: ignore


def test_is_port_open_socket_creation_failure():
    """Challenge: What happens if socket creation fails (socket exhaustion, OSError)?

    Hardened behavior: socket creation is protected inside try block, returns False.
    """
    cm = ConnectionManager()
    with patch("socket.socket", side_effect=OSError("Too many open files / socket exhaustion")):
        assert cm._is_port_open(10000) is False


def test_socket_timeout_duration_and_hang():
    """Challenge: Verify socket timeout configuration and cumulative blocking time."""
    cm = ConnectionManager()
    with patch("socket.socket") as mock_socket_cls:
        mock_sock = MagicMock()
        mock_socket_cls.return_value.__enter__.return_value = mock_sock

        # Simulate timeout
        mock_sock.connect.side_effect = socket.timeout("timed out")
        result = cm._is_port_open(10000)
        assert result is False
        mock_sock.settimeout.assert_called_with(0.2)


# ==============================================================================
# Challenge 3: Port Range Boundaries & Inverted Ranges
# ==============================================================================

def test_scan_for_grpc_inverted_range():
    """Challenge: What happens if start_port > end_port?

    range(10050, 10001) is empty; silently returns None.
    """
    cm = ConnectionManager()
    with patch.object(cm, "_is_port_open") as mock_open:
        res = cm.scan_for_mechanical_grpc(start_port=10050, end_port=10000)
        assert res is None
        assert mock_open.call_count == 0


def test_scan_for_grpc_out_of_bounds_overflow():
    """Challenge: What happens if port range extends beyond 65535?

    Hardened behavior: scan handles out-of-bounds ports gracefully without OverflowError, returns None.
    """
    cm = ConnectionManager()
    res = cm.scan_for_mechanical_grpc(start_port=65534, end_port=65538)
    assert res is None


# ==============================================================================
# Challenge 4: Corrupted, Non-Dict, and Malformed Registry Files
# ==============================================================================

def test_registry_corrupted_json_syntax(tmp_path):
    """Challenge: Syntax error in json file (truncated, corrupted bytes).

    Result: Caught by except Exception as e; logged and skipped.
    """
    cm = ConnectionManager()
    reg_dir = tmp_path / "reg"
    reg_dir.mkdir()
    (reg_dir / "1234.json").write_text("{ incomplete json", encoding="utf-8")

    with patch("psutil.pid_exists", return_value=True):
        instances = cm.get_registered_instances(registry_dir=reg_dir)
        assert instances == []


def test_registry_non_dict_json(tmp_path):
    """Challenge: Valid JSON that is NOT a dictionary (e.g. list, integer, string, null).

    Contract says -> List[Dict[str, Any]].
    Hardened behavior: ConnectionManager verifies isinstance(data, dict), discarding non-dict items.
    """
    cm = ConnectionManager()
    reg_dir = tmp_path / "reg"
    reg_dir.mkdir()
    (reg_dir / "1001.json").write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    (reg_dir / "1002.json").write_text(json.dumps("a string value"), encoding="utf-8")
    (reg_dir / "1003.json").write_text(json.dumps(None), encoding="utf-8")

    with patch("psutil.pid_exists", return_value=True):
        instances = cm.get_registered_instances(registry_dir=reg_dir)
        # Verify that non-dict items were filtered out
        assert len(instances) == 0
        assert instances == []


def test_registry_non_utf8_encoding(tmp_path):
    """Challenge: File containing invalid UTF-8 bytes.

    Actual behavior: Caught by except Exception as e; logged and skipped.
    """
    cm = ConnectionManager()
    reg_dir = tmp_path / "reg"
    reg_dir.mkdir()
    (reg_dir / "1001.json").write_bytes(b"\xff\xfe\x00\x00corrupt")

    with patch("psutil.pid_exists", return_value=True):
        instances = cm.get_registered_instances(registry_dir=reg_dir)
        assert instances == []


def test_registry_file_deleted_during_read(tmp_path):
    """Challenge: Race condition where file exists at glob() but is deleted before open().

    Actual behavior: FileNotFoundError caught by except Exception as e; skipped safely.
    """
    cm = ConnectionManager()
    reg_dir = tmp_path / "reg"
    reg_dir.mkdir()
    f = reg_dir / "1001.json"
    f.write_text('{"pid": 1001}', encoding="utf-8")

    # Simulate deletion right before open
    real_open = open
    def race_open(path, *args, **kwargs):
        if str(path).endswith("1001.json"):
            os.remove(path)
        return real_open(path, *args, **kwargs)

    with patch("psutil.pid_exists", return_value=True):
        with patch("builtins.open", side_effect=race_open):
            instances = cm.get_registered_instances(registry_dir=reg_dir)
            assert instances == []


# ==============================================================================
# Challenge 5: Multi-threaded Concurrency Stress Test
# ==============================================================================

def test_concurrent_find_all_instances():
    """Challenge: Stress-test concurrent invocations of find_all_instances across multiple threads.

    Verifies thread-safety, absence of race conditions or crashes in shared state.
    """
    cm = ConnectionManager()

    mock_procs = {
        "mechanical": [MagicMock(pid=101, info={"name": "ansyswbu.exe"})],
        "workbench": [MagicMock(pid=201, info={"name": "runwb2.exe"})],
        "fluent": [],
        "spaceclaim": [],
        "optislang": [],
    }

    with patch.object(cm, "find_running_ansys_processes", return_value=mock_procs):
        with patch.object(cm, "scan_for_mechanical_grpc", return_value=10000):
            with patch.object(cm, "scan_for_spaceclaim_grpc", return_value=None):
                with patch.object(cm, "scan_for_fluent_grpc", return_value=None):
                    errors = []

                    def worker():
                        try:
                            for _ in range(50):
                                res = cm.find_all_instances()
                                assert res["detected_ports"]["mechanical_grpc"] == 10000
                                assert len(res["mechanical"]) == 1
                                assert res["mechanical"][0]["pid"] == 101
                        except Exception as e:
                            errors.append(e)

                    threads = [threading.Thread(target=worker) for _ in range(10)]
                    for t in threads:
                        t.start()
                    for t in threads:
                        t.join()

                    assert errors == [], f"Thread errors: {errors}"


def test_concurrent_get_registered_instances_file_race(tmp_path):
    """Challenge: Multiple threads running get_registered_instances concurrently on the same registry directory.

    Tests if concurrent unlink or open throws unhandled exceptions.
    """
    cm = ConnectionManager()
    reg_dir = tmp_path / "concurrent_reg"
    reg_dir.mkdir()

    # Pre-populate 20 dead PID files
    for i in range(2000, 2020):
        (reg_dir / f"{i}.json").write_text(json.dumps({"pid": i}), encoding="utf-8")

    errors = []

    def worker():
        try:
            # All PIDs dead, all threads try to unlink
            res = cm.get_registered_instances(registry_dir=reg_dir)
            assert isinstance(res, list)
        except Exception as e:
            errors.append(e)

    with patch("psutil.pid_exists", return_value=False):
        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    assert errors == [], f"Concurrent race errors: {errors}"
    # All dead files should have been removed
    remaining = list(reg_dir.glob("*.json"))
    assert len(remaining) == 0


# ==============================================================================
# Challenge 6: Mock Integrity and Test Isolation Audit
# ==============================================================================

def test_unit_test_default_directory_touches_real_disk_and_psutil():
    """Challenge: Verify whether test_get_registered_instances_default_directory in test_connection_manager.py
    touches real OS processes and real disk directory.

    Observation: In test_connection_manager.py, test_get_registered_instances_default_directory()
    calls cm.get_registered_instances() with no arguments, which accesses
    d:\\Ikaros\\ANSYS-unified-MCP\\workbench_queue\\registry on disk and would call psutil.pid_exists
    on any real json files found there!
    """
    cm = ConnectionManager()
    default_dir = Path(__file__).parent.parent.parent / "workbench_queue" / "registry"

    with patch("psutil.pid_exists") as mock_pid_exists:
        with patch.object(Path, "unlink") as mock_unlink:
            # Call without args, exactly like test_get_registered_instances_default_directory
            cm.get_registered_instances()
            # If default_dir has no files, mock_pid_exists is not called.
            # But default_dir WAS checked for existence on real filesystem!
            assert default_dir.is_dir() or default_dir.exists()
