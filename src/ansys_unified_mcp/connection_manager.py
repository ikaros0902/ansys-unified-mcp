import psutil
import socket
import logging
import time
from typing import Optional, List, Dict

from .config import config

logger = logging.getLogger(__name__)

class ConnectionManager:
    """自動連線管理器：負責掃描、探測與附加至正在執行的 ANSYS 實例。"""
    
    def __init__(self):
        self.config = config
        
    def _is_port_open(self, port: int, host: str = "127.0.0.1") -> bool:
        """測試特定的 TCP port 是否在監聽中。"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.1)
            try:
                s.connect((host, port))
                return True
            except (socket.timeout, ConnectionRefusedError):
                return False

    def scan_for_mechanical_grpc(self, start_port: int = 10000, end_port: int = 10010) -> Optional[int]:
        """
        掃描本地是否存在開放的 Mechanical gRPC port (通常 10000+)。
        當 ACT 外掛自動執行 StartGrpcServer() 後，此函數能抓到該 Port。
        """
        for port in range(start_port, end_port + 1):
            if self._is_port_open(port):
                logger.info(f"偵測到可能的 Mechanical gRPC 服務於 Port {port}")
                return port
        return None
        
    def scan_for_spaceclaim_grpc(self, start_port: int = 50051, end_port: int = 50060) -> Optional[int]:
        """
        掃描 SpaceClaim gRPC (預設 50051 起)。
        SpaceClaim 的 Python Add-in 啟動時會綁定至該 Port。
        """
        for port in range(start_port, end_port + 1):
            if self._is_port_open(port):
                logger.info(f"偵測到可能的 SpaceClaim gRPC 服務於 Port {port}")
                return port
        return None

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
        
        for proc in psutil.process_iter(['name', 'exe', 'pid']):
            try:
                name = proc.info['name'].lower() if proc.info['name'] else ""
                
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
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
                
        return processes

    def attach_to_workbench(self) -> bool:
        """
        嘗試檢查 Workbench 是否在執行中，並確認通訊是否暢通。
        由於 Workbench 採用 File-Queue IPC，此處主要確認進程存在。
        """
        procs = self.find_running_ansys_processes()["workbench"]
        if procs:
            logger.info(f"發現執行中的 Workbench (PID: {procs[0].info['pid']})")
            return True
        return False
        
    def attach_to_fluent(self) -> Optional[int]:
        """
        偵測 Fluent process。
        若 Fluent 透過啟動掛鉤自動開啟 gRPC，我們這裡可以掃描其預設 Port。
        預設 Fluent gRPC 通常由 Scheme 腳本指定，假設我們指定 50052。
        """
        procs = self.find_running_ansys_processes()["fluent"]
        if not procs:
            return None
            
        logger.info(f"發現執行中的 Fluent (PID: {procs[0].info['pid']})")
        # 假設 Fluent 掛鉤將 Port 寫入暫存檔或預設為 50052
        fluent_port = 50052
        if self._is_port_open(fluent_port):
            return fluent_port
        return None

# 全域連線管理器實例
connection_manager = ConnectionManager()
