"""Unit tests for ConnectionManager in ansys_unified_mcp.connection_manager.

Full logic coverage with mock psutil and socket; 0 reliance on ANSYS licenses or processes.
"""

import json
import socket
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, call, patch

import psutil
import pytest

from ansys_unified_mcp.connection_manager import (
    ConnectionManager,
    connection_manager,
)


class MockProc:
    """Mock psutil.Process instance for testing."""

    def __init__(
        self,
        pid: int,
        name: Optional[str] = None,
        status: str = "running",
        raise_on_name: bool = False,
        raise_on_status: bool = False,
        exe: Optional[str] = None,
        info: Optional[Dict[str, Any]] = None,
    ):
        self.pid = pid
        self._name = name
        self._status = status
        self._raise_on_name = raise_on_name
        self._raise_on_status = raise_on_status
        if info is not None:
            self.info = info
        else:
            self.info = {
                "pid": pid,
                "name": name,
                "exe": exe or (f"C:\\ANSYS\\{name}" if name else None),
            }

    def name(self) -> str:
        if self._raise_on_name:
            raise RuntimeError(f"Process {self.pid} vanished during name() call")
        return self._name or ""

    def status(self) -> str:
        if self._raise_on_status:
            raise RuntimeError(f"Process {self.pid} vanished during status() call")
        return self._status


# ==============================================================================
# Group 1: Initialization & Global Instance
# ==============================================================================

def test_connection_manager_init():
    """驗證 ConnectionManager 初始化與全域實例綁定。"""
    cm = ConnectionManager()
    assert cm.config is not None
    assert isinstance(connection_manager, ConnectionManager)
    assert connection_manager.config is not None


# ==============================================================================
# Group 2: _is_port_open Branches & Error Handling
# ==============================================================================

def test_is_port_open_success():
    """驗證 TCP 連線成功時回傳 True 並正確設定逾時。"""
    cm = ConnectionManager()
    with patch("socket.socket") as mock_socket_cls:
        mock_sock = MagicMock()
        mock_socket_cls.return_value.__enter__.return_value = mock_sock

        assert cm._is_port_open(10000, host="127.0.0.1") is True
        mock_sock.settimeout.assert_called_once_with(0.2)
        mock_sock.connect.assert_called_once_with(("127.0.0.1", 10000))


def test_is_port_open_custom_host():
    """驗證支援自訂主機 IP。"""
    cm = ConnectionManager()
    with patch("socket.socket") as mock_socket_cls:
        mock_sock = MagicMock()
        mock_socket_cls.return_value.__enter__.return_value = mock_sock

        assert cm._is_port_open(50051, host="192.168.1.100") is True
        mock_sock.connect.assert_called_once_with(("192.168.1.100", 50051))


@pytest.mark.parametrize(
    "exception",
    [
        ConnectionRefusedError("Connection refused"),
        socket.timeout("Socket timed out"),
        ConnectionResetError("Connection reset by peer"),
        OSError("General network unreachable"),
        OverflowError("getsockaddrarg: port must be 0-65535"),
        TypeError("port must be an integer"),
        ValueError("invalid port"),
    ],
)
def test_is_port_open_exceptions(exception):
    """驗證各種網路例外均被安全捕捉並回傳 False，不拋出未捕獲錯誤。"""
    cm = ConnectionManager()
    with patch("socket.socket") as mock_socket_cls:
        mock_sock = MagicMock()
        mock_sock.connect.side_effect = exception
        mock_socket_cls.return_value.__enter__.return_value = mock_sock

        assert cm._is_port_open(10000) is False


def test_is_port_open_out_of_range():
    """驗證 port 小於 0 或大於 65535 時直接回傳 False，不拋出 OverflowError。"""
    cm = ConnectionManager()
    assert cm._is_port_open(-1) is False
    assert cm._is_port_open(65536) is False
    assert cm._is_port_open(70000) is False


def test_is_port_open_invalid_type():
    """驗證 port 為非整數型別時直接回傳 False，不拋出 TypeError。"""
    cm = ConnectionManager()
    assert cm._is_port_open("10000") is False  # type: ignore
    assert cm._is_port_open(None) is False  # type: ignore
    assert cm._is_port_open(True) is False  # type: ignore
    assert cm._is_port_open(3.14) is False  # type: ignore


def test_is_port_open_socket_creation_error():
    """驗證 socket 初始化拋出 OSError (如資源耗盡) 時安全回傳 False。"""
    cm = ConnectionManager()
    with patch("socket.socket", side_effect=OSError("Too many open files")):
        assert cm._is_port_open(10000) is False


# ==============================================================================
# Group 3: gRPC Port Scanning Ranges (Mechanical, SpaceClaim, Fluent)
# ==============================================================================

def test_scan_for_mechanical_grpc():
    """驗證 Mechanical gRPC 掃描範圍 (預設 10000~10050) 與命中回傳。"""
    cm = ConnectionManager()

    # 命中 10005
    with patch.object(cm, "_is_port_open", side_effect=lambda p: p == 10005):
        assert cm.scan_for_mechanical_grpc() == 10005

    # 全域無開放
    with patch.object(cm, "_is_port_open", return_value=False):
        assert cm.scan_for_mechanical_grpc() is None

    # 自訂掃描範圍
    with patch.object(cm, "_is_port_open", side_effect=lambda p: p == 10012) as mock_scan:
        assert cm.scan_for_mechanical_grpc(start_port=10010, end_port=10015) == 10012
        assert mock_scan.call_count == 3  # 10010, 10011, 10012 (命中即返)


def test_scan_for_spaceclaim_grpc():
    """驗證 SpaceClaim gRPC 掃描範圍 (預設 50051~50070) 與命中回傳。"""
    cm = ConnectionManager()

    # 命中 50055
    with patch.object(cm, "_is_port_open", side_effect=lambda p: p == 50055):
        assert cm.scan_for_spaceclaim_grpc() == 50055

    # 全域無開放
    with patch.object(cm, "_is_port_open", return_value=False):
        assert cm.scan_for_spaceclaim_grpc() is None

    # 自訂掃描範圍
    with patch.object(cm, "_is_port_open", side_effect=lambda p: p == 50062) as mock_scan:
        assert cm.scan_for_spaceclaim_grpc(start_port=50060, end_port=50065) == 50062
        assert mock_scan.call_count == 3  # 50060, 50061, 50062


def test_scan_for_fluent_grpc():
    """驗證 Fluent gRPC 掃描範圍 (預設 50052~50070) 與命中回傳。"""
    cm = ConnectionManager()

    # 命中 50052
    with patch.object(cm, "_is_port_open", side_effect=lambda p: p == 50052):
        assert cm.scan_for_fluent_grpc() == 50052

    # 全域無開放
    with patch.object(cm, "_is_port_open", return_value=False):
        assert cm.scan_for_fluent_grpc() is None

    # 自訂掃描範圍
    with patch.object(cm, "_is_port_open", side_effect=lambda p: p == 50068):
        assert cm.scan_for_fluent_grpc(start_port=50065, end_port=50070) == 50068


# ==============================================================================
# Group 4: find_running_ansys_processes Classification & Resilience
# ==============================================================================

def test_find_running_ansys_processes_classification():
    """驗證 5 大產品進程識別、大小寫不敏感處理與非相關進程過濾。"""
    cm = ConnectionManager()

    mock_procs = [
        MockProc(101, "runwb2.exe"),
        MockProc(102, "ansyswbu.exe"),
        MockProc(103, "fluent.exe"),
        MockProc(104, "spaceclaim.exe"),
        MockProc(105, "optislang.exe"),
        MockProc(106, "notepad.exe"),
        MockProc(107, None),
        # 大小寫混寫測試
        MockProc(201, "RUNWB2.EXE"),
        MockProc(202, "AnsysWBU.exe"),
        MockProc(203, "FLUENT.EXE"),
        MockProc(204, "SpaceClaim.EXE"),
        MockProc(205, "Optislang.exe"),
    ]

    with patch("psutil.process_iter", return_value=mock_procs):
        procs = cm.find_running_ansys_processes()

        assert len(procs["workbench"]) == 2
        assert [p.pid for p in procs["workbench"]] == [101, 201]

        assert len(procs["mechanical"]) == 2
        assert [p.pid for p in procs["mechanical"]] == [102, 202]

        assert len(procs["fluent"]) == 2
        assert [p.pid for p in procs["fluent"]] == [103, 203]

        assert len(procs["spaceclaim"]) == 2
        assert [p.pid for p in procs["spaceclaim"]] == [104, 204]

        assert len(procs["optislang"]) == 2
        assert [p.pid for p in procs["optislang"]] == [105, 205]


class MockErrorProc:
    """Mock psutil.Process where info access raises a psutil exception."""

    def __init__(self, exc: Exception):
        self._exc = exc

    @property
    def info(self):
        raise self._exc


def test_find_running_ansys_processes_exceptions():
    """驗證遇到 NoSuchProcess, AccessDenied, ZombieProcess 時安全略過。"""
    cm = ConnectionManager()

    mock_procs = [
        MockProc(101, "ansyswbu.exe"),
        MockErrorProc(psutil.NoSuchProcess(pid=102)),
        MockProc(103, "fluent.exe"),
        MockErrorProc(psutil.AccessDenied(pid=104)),
        MockProc(105, "spaceclaim.exe"),
        MockErrorProc(psutil.ZombieProcess(pid=106)),
        MockProc(107, "optislang.exe"),
    ]

    with patch("psutil.process_iter", return_value=mock_procs):
        procs = cm.find_running_ansys_processes()
        assert len(procs["mechanical"]) == 1
        assert len(procs["fluent"]) == 1
        assert len(procs["spaceclaim"]) == 1
        assert len(procs["optislang"]) == 1


def test_find_running_ansys_processes_defensive_edge_cases():
    """驗證 process_iter 拋出 None、缺乏 info、generator 拋出例外時均能安全防禦。"""
    cm = ConnectionManager()

    # 1. 包含 None 物件、非 dict 的 info 與 info['name'] 為 None
    mock_bad_proc = MagicMock()
    mock_bad_proc.info = None
    mock_list_proc = MagicMock()
    mock_list_proc.info = "not a dict"
    mock_none_name = MagicMock()
    mock_none_name.info = {"name": None}

    mock_procs = [
        None,
        mock_bad_proc,
        mock_list_proc,
        mock_none_name,
        MockProc(101, "ansyswbu.exe"),
    ]

    with patch("psutil.process_iter", return_value=mock_procs):
        procs = cm.find_running_ansys_processes()
        assert len(procs["mechanical"]) == 1
        assert procs["mechanical"][0].pid == 101

    # 2. generator 拋出 RuntimeError
    def failing_iter(attrs):
        yield MockProc(101, "ansyswbu.exe")
        raise RuntimeError("Process table locked")

    with patch("psutil.process_iter", side_effect=failing_iter):
        procs = cm.find_running_ansys_processes()
        assert len(procs["mechanical"]) == 1




# ==============================================================================
# Group 5: find_mechanical_instances Multi-Instance Discovery
# ==============================================================================

def test_find_mechanical_instances_with_port():
    """驗證發現多個 Mechanical 進程並成功綁定掃描到的 gRPC 埠。"""
    cm = ConnectionManager()
    mock_mechanical_procs = [
        MockProc(1001, "ansyswbu.exe", status="running"),
        MockProc(1002, "ansyswbu.exe", status="idle"),
    ]

    with patch.object(cm, "find_running_ansys_processes", return_value={"mechanical": mock_mechanical_procs}):
        with patch.object(cm, "scan_for_mechanical_grpc", return_value=10000):
            instances = cm.find_mechanical_instances()
            assert len(instances) == 2
            assert instances[0] == {
                "pid": 1001,
                "name": "ansyswbu.exe",
                "grpc_port": 10000,
                "status": "running",
            }
            assert instances[1] == {
                "pid": 1002,
                "name": "ansyswbu.exe",
                "grpc_port": 10000,
                "status": "idle",
            }


def test_find_mechanical_instances_no_port():
    """驗證發現 Mechanical 進程但無開放 gRPC 埠時 grpc_port 為 None。"""
    cm = ConnectionManager()
    mock_mechanical_procs = [MockProc(1001, "ansyswbu.exe")]

    with patch.object(cm, "find_running_ansys_processes", return_value={"mechanical": mock_mechanical_procs}):
        with patch.object(cm, "scan_for_mechanical_grpc", return_value=None):
            instances = cm.find_mechanical_instances()
            assert len(instances) == 1
            assert instances[0]["grpc_port"] is None


def test_find_mechanical_instances_empty():
    """驗證無 Mechanical 進程時回傳空串列，且 scan_for_mechanical_grpc 被 mock / 未被呼叫。"""
    cm = ConnectionManager()
    with patch.object(cm, "find_running_ansys_processes", return_value={"mechanical": []}):
        with patch.object(cm, "scan_for_mechanical_grpc", return_value=None) as mock_scan:
            assert cm.find_mechanical_instances() == []
            mock_scan.assert_not_called()


def test_find_mechanical_instances_exception_resilience():
    """驗證進程調用 name() 或 status() 拋出例外時安全掠過。"""
    cm = ConnectionManager()
    mock_procs = [
        MockProc(1001, "ansyswbu.exe", raise_on_name=True),
        MockProc(1002, "ansyswbu.exe", status="running"),
        MockProc(1003, "ansyswbu.exe", raise_on_status=True),
    ]

    with patch.object(cm, "find_running_ansys_processes", return_value={"mechanical": mock_procs}):
        with patch.object(cm, "scan_for_mechanical_grpc", return_value=10001):
            instances = cm.find_mechanical_instances()
            assert len(instances) == 1
            assert instances[0]["pid"] == 1002


# ==============================================================================
# Group 6: find_all_instances Structure & Process Information
# ==============================================================================

def test_find_all_instances_structure_and_ports():
    """驗證 find_all_instances 正確彙整 5 大產品進程與 3 大 gRPC 掃描通訊埠。"""
    cm = ConnectionManager()

    procs_map = {
        "mechanical": [MockProc(101, "ansyswbu.exe")],
        "workbench": [MockProc(201, "runwb2.exe")],
        "fluent": [MockProc(301, "fluent.exe")],
        "spaceclaim": [MockProc(401, "spaceclaim.exe")],
        "optislang": [MockProc(501, "optislang.exe")],
    }

    with patch.object(cm, "find_running_ansys_processes", return_value=procs_map):
        with patch.object(cm, "scan_for_mechanical_grpc", return_value=10000):
            with patch.object(cm, "scan_for_spaceclaim_grpc", return_value=50051):
                with patch.object(cm, "scan_for_fluent_grpc", return_value=50052):
                    res = cm.find_all_instances()

                    assert "mechanical" in res
                    assert res["mechanical"] == [{"pid": 101, "name": "ansyswbu.exe"}]
                    assert res["workbench"] == [{"pid": 201, "name": "runwb2.exe"}]
                    assert res["fluent"] == [{"pid": 301, "name": "fluent.exe"}]
                    assert res["spaceclaim"] == [{"pid": 401, "name": "spaceclaim.exe"}]
                    assert res["optislang"] == [{"pid": 501, "name": "optislang.exe"}]

                    assert res["detected_ports"] == {
                        "mechanical_grpc": 10000,
                        "spaceclaim_grpc": 50051,
                        "fluent_grpc": 50052,
                    }


def test_find_all_instances_process_name_failure_fallback():
    """驗證進程調用 name() 失敗時能透過 info 屬性或空字串安全降級。"""
    cm = ConnectionManager()

    # proc1: name() 拋出例外，但 info['name'] 存在
    proc1 = MockProc(101, "ansyswbu.exe", raise_on_name=True)
    # proc2: name() 拋出例外，且無 info
    proc2 = MockProc(102, None, raise_on_name=True, info={})

    procs_map = {
        "mechanical": [proc1, proc2],
        "workbench": [],
        "fluent": [],
        "spaceclaim": [],
        "optislang": [],
    }

    with patch.object(cm, "find_running_ansys_processes", return_value=procs_map):
        with patch.object(cm, "scan_for_mechanical_grpc", return_value=None):
            with patch.object(cm, "scan_for_spaceclaim_grpc", return_value=None):
                with patch.object(cm, "scan_for_fluent_grpc", return_value=None):
                    res = cm.find_all_instances()
                    assert len(res["mechanical"]) == 2
                    assert res["mechanical"][0] == {"pid": 101, "name": "ansyswbu.exe"}
                    assert res["mechanical"][1] == {"pid": 102, "name": ""}


def test_find_all_instances_with_none_proc():
    """驗證 find_all_instances 遇到包含 None 的進程列表時安全降級。"""
    cm = ConnectionManager()
    with patch.object(cm, "find_running_ansys_processes", return_value={"mechanical": [None]}):
        with patch.object(cm, "scan_for_mechanical_grpc", return_value=None):
            with patch.object(cm, "scan_for_spaceclaim_grpc", return_value=None):
                with patch.object(cm, "scan_for_fluent_grpc", return_value=None):
                    res = cm.find_all_instances()
                    assert res["mechanical"] == [{"pid": None, "name": ""}]


def test_find_all_instances_annotation_valid():

    """驗證 find_all_instances 的型別註解正確解析為 Dict[str, Any]，不拋出 NameError。"""
    annotations = ConnectionManager.find_all_instances.__annotations__
    assert "return" in annotations
    # 驗證回傳註解本體為 Dict[str, Any]
    ret_type = annotations["return"]
    assert getattr(ret_type, "__origin__", None) in (dict, Dict)


# ==============================================================================
# Group 7: attach_to_workbench & attach_to_fluent
# ==============================================================================

def test_attach_to_workbench_presence():
    """驗證 Workbench 進程存在時回傳 True，不存在時回傳 False。"""
    cm = ConnectionManager()

    # 存在進程
    with patch.object(cm, "find_running_ansys_processes", return_value={"workbench": [MockProc(1234, "runwb2.exe")]}):
        assert cm.attach_to_workbench() is True

    # 無進程
    with patch.object(cm, "find_running_ansys_processes", return_value={"workbench": []}):
        assert cm.attach_to_workbench() is False

    # 進程無 info 字典但有 pid 屬性
    mock_raw_proc = MagicMock()
    mock_raw_proc.pid = 9999
    mock_raw_proc.info = None
    with patch.object(cm, "find_running_ansys_processes", return_value={"workbench": [mock_raw_proc]}):
        assert cm.attach_to_workbench() is True


def test_attach_to_fluent_branches():
    """驗證 Fluent 附加邏輯：無進程回傳 None、有進程且 port 開放回傳 port、port 未開回傳 None。"""
    cm = ConnectionManager()

    # 1. 無 Fluent 進程
    with patch.object(cm, "find_running_ansys_processes", return_value={"fluent": []}):
        assert cm.attach_to_fluent() is None

    # 2. 有 Fluent 進程且 gRPC 埠開啟
    mock_fluent = MockProc(5678, "fluent.exe")
    with patch.object(cm, "find_running_ansys_processes", return_value={"fluent": [mock_fluent]}):
        with patch.object(cm, "scan_for_fluent_grpc", return_value=50052):
            assert cm.attach_to_fluent() == 50052

    # 3. 有 Fluent 進程但 gRPC 埠未開啟
    with patch.object(cm, "find_running_ansys_processes", return_value={"fluent": [mock_fluent]}):
        with patch.object(cm, "scan_for_fluent_grpc", return_value=None):
            assert cm.attach_to_fluent() is None

    # 4. Fluent 進程無 info 字典但有 pid 屬性
    mock_raw_fluent = MagicMock()
    mock_raw_fluent.pid = 8888
    mock_raw_fluent.info = None
    with patch.object(cm, "find_running_ansys_processes", return_value={"fluent": [mock_raw_fluent]}):
        with patch.object(cm, "scan_for_fluent_grpc", return_value=50055):
            assert cm.attach_to_fluent() == 50055


# ==============================================================================
# Group 8: get_registered_instances Lifecycle & File Cleanup
# ==============================================================================

def test_get_registered_instances_dir_not_exists(tmp_path):
    """驗證註冊目錄不存在時回傳空串列。"""
    cm = ConnectionManager()
    non_existent_dir = tmp_path / "does_not_exist"
    assert cm.get_registered_instances(registry_dir=non_existent_dir) == []


def test_get_registered_instances_active_and_dead_cleanup(tmp_path):
    """驗證讀取註冊檔案，存活 PID 正確載入，已死亡 PID 自動刪除檔案。"""
    cm = ConnectionManager()
    reg_dir = tmp_path / "registry"
    reg_dir.mkdir(parents=True, exist_ok=True)

    # 建立存活實例檔案
    alive_file = reg_dir / "1001.json"
    alive_data = {"pid": 1001, "product": "Mechanical", "port": 10000}
    alive_file.write_text(json.dumps(alive_data), encoding="utf-8")

    # 建立已死亡實例檔案
    dead_file = reg_dir / "2002.json"
    dead_data = {"pid": 2002, "product": "SpaceClaim", "port": 50051}
    dead_file.write_text(json.dumps(dead_data), encoding="utf-8")

    def mock_pid_exists(pid: int) -> bool:
        return pid == 1001

    with patch("psutil.pid_exists", side_effect=mock_pid_exists):
        instances = cm.get_registered_instances(registry_dir=reg_dir)

        assert len(instances) == 1
        assert instances[0] == alive_data

        # 驗證死亡檔案已被 unlink 刪除
        assert dead_file.exists() is False
        assert alive_file.exists() is True


def test_get_registered_instances_unlink_oserror(tmp_path):
    """驗證死亡進程檔案 unlink 拋出 OSError 時安全捕捉並繼續處理。"""
    cm = ConnectionManager()
    reg_dir = tmp_path / "registry"
    reg_dir.mkdir(parents=True, exist_ok=True)

    dead_file = reg_dir / "3003.json"
    dead_file.write_text(json.dumps({"pid": 3003}), encoding="utf-8")

    with patch("psutil.pid_exists", return_value=False):
        with patch.object(Path, "unlink", side_effect=OSError("Permission denied")):
            instances = cm.get_registered_instances(registry_dir=reg_dir)
            assert instances == []


def test_get_registered_instances_corrupt_files_resilience(tmp_path):
    """驗證遇到無效檔名（非整數 PID）或毀損 JSON 檔案時不中斷運作。"""
    cm = ConnectionManager()
    reg_dir = tmp_path / "registry"
    reg_dir.mkdir(parents=True, exist_ok=True)

    # 1. 非整數檔名
    invalid_stem_file = reg_dir / "not_a_number.json"
    invalid_stem_file.write_text(json.dumps({"test": 1}), encoding="utf-8")

    # 2. 毀損 JSON
    corrupt_file = reg_dir / "4004.json"
    corrupt_file.write_text("{ this is corrupted json", encoding="utf-8")

    # 3. 正常檔案
    valid_file = reg_dir / "5005.json"
    valid_data = {"pid": 5005, "status": "ok"}
    valid_file.write_text(json.dumps(valid_data), encoding="utf-8")

    with patch("psutil.pid_exists", return_value=True):
        instances = cm.get_registered_instances(registry_dir=reg_dir)
        assert len(instances) == 1
        assert instances[0] == valid_data


def test_get_registered_instances_default_directory(tmp_path, monkeypatch):
    """驗證未提供 registry_dir 時採用預設路徑執行，不拋出未捕獲錯誤且隔離主機檔案系統。"""
    cm = ConnectionManager()

    # 1. 預設目錄不存在時回傳空串列
    monkeypatch.setattr(
        "ansys_unified_mcp.connection_manager._DEFAULT_REGISTRY_DIR",
        tmp_path / "non_existent",
    )
    assert cm.get_registered_instances() == []

    # 2. 預設目錄存在檔案時，透過 tmp_path 與 mock 隔離，安全讀取不污染主機硬碟
    mock_reg_dir = tmp_path / "mock_workbench_queue" / "registry"
    mock_reg_dir.mkdir(parents=True, exist_ok=True)
    valid_file = mock_reg_dir / "777.json"
    valid_file.write_text(json.dumps({"pid": 777, "status": "active"}), encoding="utf-8")
    dead_file = mock_reg_dir / "888.json"
    dead_file.write_text(json.dumps({"pid": 888}), encoding="utf-8")

    monkeypatch.setattr(
        "ansys_unified_mcp.connection_manager._DEFAULT_REGISTRY_DIR",
        mock_reg_dir,
    )
    with patch("psutil.pid_exists", side_effect=lambda pid: pid == 777):
        result = cm.get_registered_instances()
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["pid"] == 777
        # 預設目錄（未傳入 registry_dir）僅過濾無效實例，不刪除主機檔案
        assert dead_file.exists() is True


def test_get_registered_instances_non_dict_ignored(tmp_path):
    """驗證註冊檔案為合法的非字典 JSON (如 list, string, null) 時被安全過濾。"""
    cm = ConnectionManager()
    reg_dir = tmp_path / "reg"
    reg_dir.mkdir(parents=True, exist_ok=True)

    (reg_dir / "101.json").write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    (reg_dir / "102.json").write_text(json.dumps("some string"), encoding="utf-8")
    (reg_dir / "103.json").write_text(json.dumps(None), encoding="utf-8")
    (reg_dir / "104.json").write_text(json.dumps({"pid": 104, "valid": True}), encoding="utf-8")

    with patch("psutil.pid_exists", return_value=True):
        instances = cm.get_registered_instances(registry_dir=reg_dir)
        assert len(instances) == 1
        assert instances[0] == {"pid": 104, "valid": True}

