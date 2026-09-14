import psutil
import socket
import logging
import time
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from .config import config

logger = logging.getLogger(__name__)

_DEFAULT_REGISTRY_DIR = Path(__file__).parent.parent.parent / "workbench_queue" / "registry"


class ConnectionManager:
    """自動連線管理器：負責掃描、探測與附加至正在執行的 ANSYS 實例。"""
    
    def __init__(self):
        self.config = config
        
    def _is_port_open(self, port: int, host: str = "127.0.0.1") -> bool:
        """測試特定的 TCP port 是否在監聽中。

        Windows 上被拒絕的連線可能丟 ConnectionRefusedError、ConnectionResetError
        或一般 OSError；一律視為未開啟，避免例外外溢。
        """
        if not isinstance(port, int) or isinstance(port, bool) or not (0 <= port <= 65535):
            return False

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.2)
                try:
                    s.connect((host, port))
                    return True
                except (OSError, OverflowError, TypeError, ValueError):
                    return False
        except (OSError, OverflowError, TypeError, ValueError):
            return False

    def scan_for_mechanical_grpc(self, start_port: int = 10000, end_port: int = 10050) -> Optional[int]:
        """
        掃描本地是否存在開放的 Mechanical gRPC port (通常 10000+)。
        當 ACT 外掛自動執行 StartGrpcServer() 後，此函數能抓到該 Port。
        """
        for port in range(start_port, end_port + 1):
            if self._is_port_open(port):
                logger.info(f"偵測到可能的 Mechanical gRPC 服務於 Port {port}")
                return port
        return None
        
    def scan_for_spaceclaim_grpc(self, start_port: int = 50051, end_port: int = 50070) -> Optional[int]:
        """
        掃描 SpaceClaim gRPC (預設 50051 起)。
        SpaceClaim 的 Python Add-in 啟動時會綁定至該 Port。
        """
        for port in range(start_port, end_port + 1):
            if self._is_port_open(port):
                logger.info(f"偵測到可能的 SpaceClaim gRPC 服務於 Port {port}")
                return port
        return None

    def find_mechanical_instances(self) -> List[Dict[str, Any]]:
        """尋找所有運行中的 Mechanical 實例（包含 PID 與 gRPC Port）。"""
        procs = self.find_running_ansys_processes().get("mechanical", [])
        if not procs:
            return []
        port = self.scan_for_mechanical_grpc()
        results = []
        for p in procs:
            try:
                results.append({
                    "pid": p.pid,
                    "name": p.name(),
                    "grpc_port": port,
                    "status": p.status()
                })
            except Exception:
                pass
        return results

    def find_all_instances(self) -> Dict[str, Any]:
        """統一回傳所有 ANSYS 產品進程與偵測到的通訊埠。"""
        procs = self.find_running_ansys_processes()

        def _get_proc_summary(p: Optional[psutil.Process]) -> Dict[str, Any]:
            if p is None:
                return {"pid": None, "name": ""}
            try:
                name = p.name()
            except Exception:
                name = p.info.get("name", "") if hasattr(p, "info") and isinstance(p.info, dict) else ""
            return {"pid": getattr(p, "pid", None), "name": name}

        return {
            "mechanical": [_get_proc_summary(p) for p in procs.get("mechanical", [])],
            "workbench": [_get_proc_summary(p) for p in procs.get("workbench", [])],
            "fluent": [_get_proc_summary(p) for p in procs.get("fluent", [])],
            "spaceclaim": [_get_proc_summary(p) for p in procs.get("spaceclaim", [])],
            "optislang": [_get_proc_summary(p) for p in procs.get("optislang", [])],
            "detected_ports": {
                "mechanical_grpc": self.scan_for_mechanical_grpc(),
                "spaceclaim_grpc": self.scan_for_spaceclaim_grpc(),
                "fluent_grpc": self.scan_for_fluent_grpc()
            }
        }

    def find_running_ansys_processes(self) -> Dict[str, List[psutil.Process]]:
        """
        利用 psutil 尋找當前正在執行的 ANSYS 相關進程。
        """
        processes = {
            "workbench": [],
            "mechanical": [],
            "fluent": [],
            "spaceclaim": [],
            "optislang": []
        }
        
        try:
            for proc in psutil.process_iter(['name', 'exe', 'pid']):
                if proc is None:
                    continue
                try:
                    info = getattr(proc, "info", None)
                    if not isinstance(info, dict):
                        continue
                    raw_name = info.get("name")
                    name = raw_name.lower() if raw_name else ""
                    
                    if name == "runwb2.exe":
                        processes["workbench"].append(proc)
                    elif name == "ansyswbu.exe":
                        processes["mechanical"].append(proc)
                    elif name == "fluent.exe":
                        processes["fluent"].append(proc)
                    elif name == "spaceclaim.exe":
                        processes["spaceclaim"].append(proc)
                    elif name == "optislang.exe":
                        processes["optislang"].append(proc)
                except (psutil.Error, Exception):
                    pass

        except (psutil.Error, RuntimeError, Exception):
            pass
                
        return processes

    def attach_to_workbench(self) -> bool:
        """
        嘗試檢查 Workbench 是否在執行中，並確認通訊是否暢通。
        由於 Workbench 採用 File-Queue IPC，此處主要確認進程存在。
        """
        procs = self.find_running_ansys_processes().get("workbench", [])
        if procs:
            pid = procs[0].info["pid"] if (hasattr(procs[0], "info") and isinstance(procs[0].info, dict) and "pid" in procs[0].info) else getattr(procs[0], "pid", None)
            logger.info(f"發現執行中的 Workbench (PID: {pid})")
            return True
        return False
        
    def scan_for_fluent_grpc(self, start_port: int = 50052, end_port: int = 50070) -> Optional[int]:
        """掃描 Fluent gRPC server 埠（Fluent 以 -sgui/server 模式開啟時綁定的埠）。"""
        for port in range(start_port, end_port + 1):
            if self._is_port_open(port):
                logger.info(f"偵測到可能的 Fluent gRPC 服務於 Port {port}")
                return port
        return None

    def attach_to_fluent(self) -> Optional[int]:
        """偵測執行中的 Fluent，並掃描其 gRPC 埠範圍（不再寫死單一埠）。"""
        procs = self.find_running_ansys_processes().get("fluent", [])
        if not procs:
            return None
        pid = procs[0].info["pid"] if (hasattr(procs[0], "info") and isinstance(procs[0].info, dict) and "pid" in procs[0].info) else getattr(procs[0], "pid", None)
        logger.info(f"發現執行中的 Fluent (PID: {pid})")
        return self.scan_for_fluent_grpc()

    def get_registered_instances(self, registry_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
        """讀取 registry 目錄，獲取所有運行中的 ANSYS 實例，過濾已關閉的 PID 並自動清理。"""
        reg_dir = registry_dir if registry_dir is not None else _DEFAULT_REGISTRY_DIR
        instances = []
        if not reg_dir.exists():
            return instances
            
        for f in reg_dir.glob("*.json"):
            try:
                pid = int(f.stem)
                # 檢查進程是否仍然存在，不存在則清理
                if not psutil.pid_exists(pid):
                    if registry_dir is not None:
                        try:
                            f.unlink()
                        except OSError:
                            pass
                    continue
                    
                with open(f, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    if isinstance(data, dict):
                        instances.append(data)
            except Exception as e:
                logger.warning(f"無法讀取註冊檔案 {f}: {e}")
                
        return instances

# 全域連線管理器實例
connection_manager = ConnectionManager()

