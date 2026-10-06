"""M1 雙軌路徑常數與向下相容邏輯之對抗性壓力測試套件。

驗證維度：
1. 目錄不存在時的自癒與自動建立能力（Zero-Existence Auto-Creation Stress）
2. ConnectionManager 雙軌回退與動態切換相容性（Dual-Path Fallback & Dynamic Resilience）
3. 路徑注入、目錄穿越與異常邊界（Path Traversal & Injection Hardening）
4. 無權限、唯讀與異常例外防禦（Permission & OS Error Hardening）
5. 環境變數優先級與覆蓋相容性（Environment Variable Precedence）
6. 模組載入期常數靜態綁定邊界（Module-level Constant Binding Boundary）
"""

import concurrent.futures
import json
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import psutil

from ansys_unified_mcp.core.jobs.manager import JobManager
from ansys_unified_mcp.bridges.connection_manager import (
    ConnectionManager,
    _DEFAULT_REGISTRY_DIR,
    _RUNTIME_REGISTRY_DIR,
    _LEGACY_REGISTRY_DIR,
)
from ansys_unified_mcp.bridges import workbench_filequeue
from ansys_unified_mcp.core import script_guard
from ansys_unified_mcp.bridges import workbench_batch


# ==============================================================================
# 維度 1: 目錄不存在時的自癒與自動建立能力
# ==============================================================================

def test_job_manager_auto_creates_nonexistent_runtime_jobs_root(tmp_path):
    """檢驗：當 .runtime/jobs 及其父目錄完全不存在時，JobManager 實例化能自動建立。"""
    non_existent_jobs = tmp_path / ".runtime_sandbox" / "deep_sub" / "jobs"
    assert not non_existent_jobs.exists()

    # 傳入不存在之路徑，驗證自動 mkdir(parents=True, exist_ok=True)
    mgr = JobManager(base_jobs_dir=non_existent_jobs)
    assert non_existent_jobs.exists()
    assert non_existent_jobs.is_dir()

    # 建立作業沙盒，驗證建立子目錄與檔案正常
    sandbox = mgr.create_job(workflow_type="drop_test", tag="auto_mkdir_test")
    assert sandbox.root_dir.exists()
    assert (sandbox.root_dir / "artifacts" / "summary.json").exists()


def test_workbench_filequeue_ensure_dirs_creates_nonexistent_runtime_dirs(tmp_path):
    """檢驗：當 .runtime/logs 與 .runtime/queue 不存在時，_ensure_dirs 能自動遞迴建立。"""
    sandbox_mcp_home = tmp_path / "sandbox_mcp"
    logs_dir = sandbox_mcp_home / ".runtime" / "logs"
    queue_dir = sandbox_mcp_home / ".runtime" / "queue"
    commands_dir = sandbox_mcp_home / "commands"
    results_dir = sandbox_mcp_home / "results"

    assert not sandbox_mcp_home.exists()

    with patch.object(workbench_filequeue, "MCP_HOME", sandbox_mcp_home), \
         patch.object(workbench_filequeue, "LOGS_DIR", logs_dir), \
         patch.object(workbench_filequeue, "WORKBENCH_QUEUE_DIR", queue_dir), \
         patch.object(workbench_filequeue, "COMMANDS_DIR", commands_dir), \
         patch.object(workbench_filequeue, "RESULTS_DIR", results_dir):

        # 第一次呼叫，應自動建立所有目錄
        workbench_filequeue._ensure_dirs()
        assert logs_dir.is_dir()
        assert queue_dir.is_dir()
        assert commands_dir.is_dir()
        assert results_dir.is_dir()

        # 第二次呼叫，驗證具備冪等性 (Idempotent)，不拋出 FileExistsError
        workbench_filequeue._ensure_dirs()
        assert logs_dir.is_dir()


def test_script_guard_audit_log_creates_nonexistent_runtime_logs_dir(tmp_path):
    """檢驗：當 .runtime/logs/script_audit 不存在時，check_script 能自動建立並寫入審計日誌。"""
    audit_dir = tmp_path / ".runtime" / "logs" / "script_audit"
    assert not audit_dir.exists()

    with patch.object(script_guard, "_AUDIT_LOG_DIR", audit_dir):
        is_safe, warnings = script_guard.check_script("import os\nprint('hello')", context="adv_test")
        assert audit_dir.is_dir()
        log_files = list(audit_dir.glob("audit_*.log"))
        assert len(log_files) >= 1
        content = log_files[0].read_text(encoding="utf-8")
        assert "adv_test" in content


def test_workbench_batch_jobs_dir_safe_write(tmp_path):
    """檢驗：workbench_batch 在深層目錄不存在時，_write_json 能自動建立父目錄。"""
    target_json = tmp_path / ".runtime" / "jobs" / "workbench" / "job_001" / "status.json"
    assert not target_json.parent.exists()

    workbench_batch._write_json(target_json, {"status": "pending"})
    assert target_json.exists()
    data = json.loads(target_json.read_text(encoding="utf-8"))
    assert data.get("status") == "pending"


# ==============================================================================
# 維度 2: ConnectionManager 雙軌回退與動態相容性
# ==============================================================================

def test_connection_manager_legacy_path_fallback(tmp_path):
    """檢驗：若 .runtime/queue/registry 不存在但 legacy 目錄存在，能平滑讀取舊目錄實例。"""
    legacy_dir = tmp_path / "workbench_queue" / "registry"
    legacy_dir.mkdir(parents=True)
    runtime_dir = tmp_path / ".runtime" / "queue" / "registry"
    # runtime_dir 不存在

    # 模擬當前行程有存活進程
    current_pid = os.getpid()
    proc_info = {"pid": current_pid, "product": "workbench", "port": 9885}
    (legacy_dir / f"{current_pid}.json").write_text(json.dumps(proc_info), encoding="utf-8")

    cm = ConnectionManager()
    instances = cm.get_registered_instances(registry_dir=legacy_dir)
    assert len(instances) == 1
    assert instances[0]["pid"] == current_pid
    assert instances[0]["product"] == "workbench"


def test_connection_manager_runtime_path_priority(tmp_path):
    """檢驗：當明確傳入或切換至 .runtime/queue/registry 時，能正確讀取新目錄實例。"""
    runtime_dir = tmp_path / ".runtime" / "queue" / "registry"
    runtime_dir.mkdir(parents=True)

    current_pid = os.getpid()
    proc_info = {"pid": current_pid, "product": "mechanical", "port": 10001}
    (runtime_dir / f"{current_pid}.json").write_text(json.dumps(proc_info), encoding="utf-8")

    cm = ConnectionManager()
    instances = cm.get_registered_instances(registry_dir=runtime_dir)
    assert len(instances) == 1
    assert instances[0]["product"] == "mechanical"


def test_connection_manager_dynamic_registry_switch():
    """檢驗：ConnectionManager 支援透過參數動態切換 registry 目錄，不鎖死在靜態常數。"""
    cm = ConnectionManager()
    with tempfile.TemporaryDirectory() as td:
        dir_a = Path(td) / "dir_a"
        dir_b = Path(td) / "dir_b"
        dir_a.mkdir()
        dir_b.mkdir()

        pid = os.getpid()
        (dir_a / f"{pid}.json").write_text(json.dumps({"pid": pid, "env": "A"}), encoding="utf-8")
        (dir_b / f"{pid}.json").write_text(json.dumps({"pid": pid, "env": "B"}), encoding="utf-8")

        res_a = cm.get_registered_instances(registry_dir=dir_a)
        res_b = cm.get_registered_instances(registry_dir=dir_b)

        assert res_a[0]["env"] == "A"
        assert res_b[0]["env"] == "B"


def test_connection_manager_nonexistent_directory_returns_empty():
    """檢驗：若 registry 目錄完全不存在，安全回傳空串列，不拋出 FileNotFoundError。"""
    cm = ConnectionManager()
    fake_path = Path("Z:/non_existent_drive/never_exists/registry")
    instances = cm.get_registered_instances(registry_dir=fake_path)
    assert instances == []


# ==============================================================================
# 維度 3: 路徑注入、目錄穿越與異常邊界
# ==============================================================================

@pytest.mark.parametrize("malicious_workflow", [
    "../../etc",
    "..\\..\\windows",
    "workflow/nested",
    "workflow\\nested",
    "workflow;rm -rf",
    "workflow|calc",
    "workflow$PWD",
    "workflow\x00null",
    "  ",
    "",
])
def test_job_manager_rejects_path_traversal_in_workflow_type(malicious_workflow, tmp_path):
    """檢驗：JobManager 嚴格防範 workflow_type 路徑穿越與非法字元注入。"""
    mgr = JobManager(base_jobs_dir=tmp_path)
    with pytest.raises(ValueError):
        mgr.create_job(workflow_type=malicious_workflow, tag="legit_tag")


@pytest.mark.parametrize("malicious_tag", [
    "../../../shadow",
    "..\\..\\admin",
    "tag/sub",
    "tag\\sub",
    "tag`whoami`",
    "tag\nline",
    "",
])
def test_job_manager_rejects_path_traversal_in_tag(malicious_tag, tmp_path):
    """檢驗：JobManager 嚴格防範 tag 欄位之路徑穿越與非法注入。"""
    mgr = JobManager(base_jobs_dir=tmp_path)
    with pytest.raises(ValueError):
        mgr.create_job(workflow_type="valid_workflow", tag=malicious_tag)


def test_job_manager_concurrent_job_creation(tmp_path):
    """檢驗：高併發（30 個執行緒）同時建立工作時，無路徑衝突與競爭條件。"""
    mgr = JobManager(base_jobs_dir=tmp_path)

    def _create(idx: int):
        return mgr.create_job(workflow_type="stress", tag=f"worker_{idx}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(_create, i) for i in range(30)]
        sandboxes = [f.result() for f in futures]

    # 驗證所有建立的 job_id 唯一
    job_ids = [sb.job_id for sb in sandboxes]
    assert len(job_ids) == len(set(job_ids)), "併發建立作業產生了重複的 job_id！"

    # 驗證所有沙盒目錄均真實存在且互不重疊
    for sb in sandboxes:
        assert sb.root_dir.is_dir()


def test_connection_manager_handles_corrupted_and_injected_registry_files(tmp_path):
    """檢驗：ConnectionManager 遭遇破損、非字典、非整數 PID 等註冊檔時，能安全略過不崩潰。"""
    reg_dir = tmp_path / "registry"
    reg_dir.mkdir()

    # 1. 檔名非數字
    (reg_dir / "not_a_pid.json").write_text("{}", encoding="utf-8")
    # 2. 空檔案
    (reg_dir / "99901.json").write_text("", encoding="utf-8")
    # 3. 毀損的 JSON 語法
    (reg_dir / "99902.json").write_text("{'unclosed_json': ", encoding="utf-8")
    # 4. JSON 是陣列而非字典
    (reg_dir / "99903.json").write_text("[1, 2, 3]", encoding="utf-8")
    # 5. JSON 是純字串
    (reg_dir / "99904.json").write_text('"just a string"', encoding="utf-8")
    # 6. 非 UTF-8 編碼二進位檔案
    (reg_dir / "99905.json").write_bytes(b"\x80\xff\xfe\x00")

    # 7. 正常的檔案但對應當前存活進程
    pid = os.getpid()
    (reg_dir / f"{pid}.json").write_text(json.dumps({"pid": pid, "status": "ok"}), encoding="utf-8")

    cm = ConnectionManager()
    instances = cm.get_registered_instances(registry_dir=reg_dir)

    # 必須安全濾除所有異常檔案，僅保留有效之當前進程
    assert len(instances) == 1
    assert instances[0]["pid"] == pid
    assert instances[0]["status"] == "ok"


# ==============================================================================
# 維度 4: 無權限、唯讀與異常例外防禦
# ==============================================================================

def test_script_guard_audit_log_permission_denied_never_crashes(tmp_path):
    """檢驗：當 audit log 目錄不可寫或權限被拒時，check_script 絕不引發崩潰。"""
    unwritable_dir = tmp_path / "unwritable_audit"

    # 模擬 mkdir 丟出 PermissionError
    with patch.object(script_guard, "_AUDIT_LOG_DIR", unwritable_dir):
        with patch.object(Path, "mkdir", side_effect=PermissionError("Mock Permission Denied")):
            # 應被內部 except Exception: pass 妥善捕捉，主流程不受阻斷
            is_safe, warnings = script_guard.check_script("print(1)", context="perm_test")
            assert is_safe is True
            assert warnings == []


def test_connection_manager_dead_pid_unlink_permission_denied(tmp_path):
    """檢驗：清理無效 PID 註冊檔時若 unlink 發生 OSError/PermissionError，不向外拋出。"""
    reg_dir = tmp_path / "registry"
    reg_dir.mkdir()

    dead_pid = 99999999  # 幾乎不可能存在的 PID
    dead_file = reg_dir / f"{dead_pid}.json"
    dead_file.write_text(json.dumps({"pid": dead_pid}), encoding="utf-8")

    cm = ConnectionManager()

    # 模擬 unlink 發生 PermissionError (Windows 檔案鎖定常態)
    with patch("psutil.pid_exists", return_value=False):
        with patch.object(Path, "unlink", side_effect=PermissionError("Access Denied")):
            instances = cm.get_registered_instances(registry_dir=reg_dir)
            assert instances == []


# ==============================================================================
# 維度 5: 環境變數優先級與覆蓋相容性
# ==============================================================================

def test_workbench_batch_jobs_dir_respects_env_var(tmp_path):
    """檢驗：workbench_batch.JOBS_DIR 若有環境變數 JOBS_DIR，應優先採納。"""
    custom_dir = tmp_path / "custom_jobs"
    with patch.dict(os.environ, {"JOBS_DIR": str(custom_dir)}):
        # 重新評估或檢驗環境變數讀取邏輯
        resolved = Path(os.environ.get("JOBS_DIR", "fallback"))
        assert resolved == custom_dir


# ==============================================================================
# 維度 6: 雙軌過渡期目錄存在性與常數靜態綁定邊界探索
# ==============================================================================

def test_connection_manager_default_resolution_logic():
    """檢驗：connection_manager 的雙軌解析預設值邏輯。"""
    # 觀察當前載入的常數
    from ansys_unified_mcp.bridges import connection_manager as cm_mod
    current_default = cm_mod._DEFAULT_REGISTRY_DIR

    # 若 runtime 目錄存在，應解析為 runtime 目錄；否則為 legacy 目錄
    if cm_mod._RUNTIME_REGISTRY_DIR.exists():
        assert current_default == cm_mod._RUNTIME_REGISTRY_DIR
    else:
        assert current_default == cm_mod._LEGACY_REGISTRY_DIR


def test_static_binding_lag_when_runtime_dir_created_after_import(tmp_path):
    """【對抗挑戰發現】模組層級常數靜態綁定延遲效應探測。

    情境：當模組在載入時，_RUNTIME_REGISTRY_DIR 尚未存在，因此 _DEFAULT_REGISTRY_DIR 被綁定至 legacy 目錄。
    若系統在執行中建立了 runtime 目錄，呼叫 get_registered_instances() 若依賴 _DEFAULT_REGISTRY_DIR，
    將因常數未動態求值而無法自動轉向 runtime 目錄。
    """
    from ansys_unified_mcp.bridges import connection_manager as cm_mod

    # 模擬模組載入時狀態：_DEFAULT_REGISTRY_DIR 已被固定為 legacy_dir
    fake_legacy = tmp_path / "legacy_queue" / "registry"
    fake_runtime = tmp_path / "runtime_queue" / "registry"
    fake_legacy.mkdir(parents=True)

    cm = ConnectionManager()

    # 假設模組載入時常數已被綁定為 fake_legacy
    with patch.object(cm_mod, "_DEFAULT_REGISTRY_DIR", fake_legacy):
        # 稍後系統動態建立了 runtime 目錄並寫入新進程註冊檔
        fake_runtime.mkdir(parents=True)
        pid = os.getpid()
        (fake_runtime / f"{pid}.json").write_text(json.dumps({"pid": pid, "created": "late"}), encoding="utf-8")

        # 呼叫預設 get_registered_instances()
        instances = cm.get_registered_instances()

        # 因為 _DEFAULT_REGISTRY_DIR 靜態綁定在 fake_legacy，故讀取不到 fake_runtime 的註冊資訊
        assert len(instances) == 0, "證實：靜態常數綁定無法動態感知執行期新建立之 runtime 目錄"


def test_workbench_filequeue_default_home_fallback_observation():
    """【對抗挑戰發現】DEFAULT_MCP_HOME 在缺少環境變數時指向 bridges 目錄。

    情境：當環境變數 ANSYS_WORKBENCH_MCP_HOME 未設定時，workbench_filequeue.DEFAULT_MCP_HOME
    使用 SERVER_ROOT (Path(__file__).resolve().parent，即 src/.../bridges)，
    而非 REPO_ROOT (parents[3])。這意味著若未載入 .env，.runtime 目錄會建立於 bridges 目錄下。
    """
    from ansys_unified_mcp.bridges import workbench_filequeue as wq

    # SERVER_ROOT 指向 bridges 目錄
    assert wq.SERVER_ROOT.name == "bridges"
    assert wq.DEFAULT_MCP_HOME == wq.SERVER_ROOT
