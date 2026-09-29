import hashlib
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Dict, Any

@dataclass
class EvidenceManifest:
    """證據檔案清單資料結構。"""
    file_path: str
    sha256_hash: str
    semantic_ids: List[str]
    timestamp: str

def create_manifest(file_path: str, semantic_ids: List[str]) -> Dict[str, Any]:
    """建立檔案的 EvidenceManifest，包含 SHA256 Hash。"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"找不到檔案: {file_path}")
    
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        # 讀取大檔案時建議分塊，不過這裡直接用 chunks
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
            
    manifest = EvidenceManifest(
        file_path=file_path,
        sha256_hash=sha256.hexdigest(),
        semantic_ids=semantic_ids,
        timestamp=datetime.now(timezone.utc).isoformat()
    )
    return asdict(manifest)

def verify_manifest(manifest: Dict[str, Any]) -> bool:
    """驗證檔案的完整性，比對當前 Hash 是否與 Manifest 一致。"""
    file_path = manifest.get("file_path")
    expected_hash = manifest.get("sha256_hash")
    
    if not file_path or not expected_hash:
        return False
        
    if not os.path.exists(file_path):
        return False
        
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
    except Exception:
        return False
        
    return sha256.hexdigest() == expected_hash
