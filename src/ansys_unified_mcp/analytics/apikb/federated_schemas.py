"""
ANSYS 聯邦 API 知識圖譜架構與 64-bit 位元分區識別碼 (Federated Schemas & Bit-Partitioned UID).

本模組實作 Stage 3 聯邦圖譜的識別碼編碼規範與子圖架構：
1. 64-bit Bit-Partitioned symbol_uid：
   - 最高 8 位元 (56~63): domain_id (0~10)
   - 低 56 位元 (0~55): canonical_uri 的 xxhash64 摘要 (降級支援 sha256)
   - 公式：symbol_uid = (domain_id << 56) | (hash56(canonical_uri) & 0x00FFFFFFFFFFFFFF)
2. O(1) 零查找子圖路由：
   - domain_id = (symbol_uid >> 56) & 0x7F
3. 支援 10 大領域子圖與跨領域多物理場橋接圖之 DDL 與資料結構。
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
import re
import sqlite3
from typing import Any, Final, Optional, Union

# 嘗試載入高效能 xxhash；若未安裝則平滑降級至 hashlib.sha256
try:
    import xxhash  # type: ignore[import-not-found]
    HAS_XXHASH: bool = True
except ImportError:
    xxhash = None
    HAS_XXHASH = False


# ============================================================================
# 常數與領域定義 (Domain Definitions)
# ============================================================================

MASK_56_BITS: Final[int] = 0x00FFFFFFFFFFFFFF
DOMAIN_BIT_SHIFT: Final[int] = 56
DOMAIN_ID_MASK: Final[int] = 0x7F


class DomainID(IntEnum):
    """領域代碼枚舉 (0~10)"""
    FOUNDATION = 0
    STRUCTURAL = 1
    FLUIDS = 2
    ELECTROMAGNETICS = 3
    OPTICS = 4
    THERMAL = 5
    MULTIBODY = 6
    PARTICLES = 7
    MATERIALS = 8
    FRAMEWORK = 9
    BRIDGE = 10


DOMAIN_NAMES: Final[dict[int, str]] = {
    DomainID.FOUNDATION: "foundation",
    DomainID.STRUCTURAL: "structural",
    DomainID.FLUIDS: "fluids",
    DomainID.ELECTROMAGNETICS: "electromagnetics",
    DomainID.OPTICS: "optics",
    DomainID.THERMAL: "thermal",
    DomainID.MULTIBODY: "multibody",
    DomainID.PARTICLES: "particles",
    DomainID.MATERIALS: "materials",
    DomainID.FRAMEWORK: "framework",
    DomainID.BRIDGE: "bridge",
}

DOMAIN_SUBGRAPH_FILES: Final[dict[int, str]] = {
    DomainID.FOUNDATION: "00_foundation_kb.sqlite",
    DomainID.STRUCTURAL: "01_structural_kb.sqlite",
    DomainID.FLUIDS: "02_fluids_kb.sqlite",
    DomainID.ELECTROMAGNETICS: "03_electromagnetics_kb.sqlite",
    DomainID.OPTICS: "04_optics_kb.sqlite",
    DomainID.THERMAL: "05_thermal_kb.sqlite",
    DomainID.MULTIBODY: "06_multibody_kb.sqlite",
    DomainID.PARTICLES: "07_particles_kb.sqlite",
    DomainID.MATERIALS: "08_materials_kb.sqlite",
    DomainID.FRAMEWORK: "09_framework_kb.sqlite",
    DomainID.BRIDGE: "multiphysics_bridge.sqlite",
}

NAME_TO_DOMAIN_ID: Final[dict[str, int]] = {
    name: domain_id for domain_id, name in DOMAIN_NAMES.items()
}

# 別名相容對照
NAME_TO_DOMAIN_ID.update({
    "mechanical": DomainID.STRUCTURAL,
    "mapdl": DomainID.STRUCTURAL,
    "lsdyna": DomainID.STRUCTURAL,
    "fluent": DomainID.FLUIDS,
    "cfx": DomainID.FLUIDS,
    "maxwell": DomainID.ELECTROMAGNETICS,
    "hfss": DomainID.ELECTROMAGNETICS,
    "speos": DomainID.OPTICS,
    "zemax": DomainID.OPTICS,
    "icepak": DomainID.THERMAL,
    "motion": DomainID.MULTIBODY,
    "rocky": DomainID.PARTICLES,
    "granta": DomainID.MATERIALS,
    "spaceclaim": DomainID.FRAMEWORK,
    "workbench": DomainID.FRAMEWORK,
    "optislang": DomainID.FRAMEWORK,
})


# ============================================================================
# URI 與 Hash 計算 (Canonical URI & Hashing)
# ============================================================================

def create_canonical_uri(
    domain: str,
    namespace: str,
    fqn: str,
    arity: int = 0
) -> str:
    """
    建立標準化 Canonical URI。

    格式: ansys://{domain}/{namespace}/{fqn}#{arity}
    範例:
        create_canonical_uri("structural", "mechanical", "Ansys.ACT.Automation.Mechanical.Analysis", 0)
        -> "ansys://structural/mechanical/Ansys.ACT.Automation.Mechanical.Analysis#0"
    """
    clean_domain = domain.strip().lower()
    clean_ns = namespace.strip().strip("/")
    clean_fqn = fqn.strip().strip("/")
    safe_arity = max(0, int(arity))

    if clean_ns:
        return f"ansys://{clean_domain}/{clean_ns}/{clean_fqn}#{safe_arity}"
    return f"ansys://{clean_domain}/{clean_fqn}#{safe_arity}"


_CANONICAL_URI_PATTERN = re.compile(
    r"^ansys://(?P<domain>[^/]+)/(?:(?P<namespace>[^/]+)/)?(?P<fqn>[^#]+)(?:#(?P<arity>\d+))?$"
)


def parse_canonical_uri(canonical_uri: str) -> dict[str, Any]:
    """
    解析 Canonical URI 為組成元件 (domain, namespace, fqn, arity)。
    """
    match = _CANONICAL_URI_PATTERN.match(canonical_uri.strip())
    if not match:
        raise ValueError(f"無效的 Canonical URI 格式: {canonical_uri}")
    
    data = match.groupdict()
    return {
        "domain": data["domain"],
        "namespace": data["namespace"] or "",
        "fqn": data["fqn"],
        "arity": int(data["arity"]) if data["arity"] is not None else 0,
    }


def compute_uri_hash56(canonical_uri: str) -> int:
    """
    計算 Canonical URI 之 56-bit 哈希值。

    優先使用 xxhash64 (xxh64)；若本機未安裝 xxhash 則平滑降級至 hashlib.sha256，
    截取其 56-bit 摘要，確保任何環境 100% 可用且數值分佈均勻。
    """
    uri_bytes = canonical_uri.encode("utf-8")
    if HAS_XXHASH and xxhash is not None:
        raw_hash = xxhash.xxh64(uri_bytes).intdigest()
    else:
        # sha256 降級：取前 8 位元組解析為大端序 64 位元整數
        raw_hash = int.from_bytes(hashlib.sha256(uri_bytes).digest()[:8], byteorder="big")
    return raw_hash & MASK_56_BITS


# ============================================================================
# 位元分區 64-bit UID 產生與解析 (Bit-Partitioned UID)
# ============================================================================

def parse_domain_id(domain: Union[str, int, DomainID]) -> int:
    """將字串名稱、別名、枚舉或整數標準化為 domain_id (0~10)"""
    if isinstance(domain, DomainID):
        return int(domain.value)
    if isinstance(domain, int):
        if 0 <= domain <= 127:
            return domain
        raise ValueError(f"domain_id 超出有效範圍 (0~127): {domain}")
    
    clean_name = domain.strip().lower()
    if clean_name in NAME_TO_DOMAIN_ID:
        return NAME_TO_DOMAIN_ID[clean_name]
    
    # 嘗試從數字字串轉換
    try:
        val = int(clean_name)
        if 0 <= val <= 127:
            return val
    except ValueError:
        pass

    raise ValueError(f"無法識別的領域名稱或代碼: '{domain}'")


def generate_symbol_uid(
    domain: Union[str, int, DomainID],
    canonical_uri: str
) -> int:
    """
    產生 64-bit 位元分區識別碼 (symbol_uid)。

    公式：symbol_uid = (domain_id << 56) | (xxhash64(canonical_uri) & 0x00FFFFFFFFFFFFFF)
    """
    d_id = parse_domain_id(domain)
    local_hash = compute_uri_hash56(canonical_uri)
    return (d_id << DOMAIN_BIT_SHIFT) | local_hash


def create_symbol_uid(
    domain: Union[str, int, DomainID],
    namespace: str,
    fqn: str,
    arity: int = 0
) -> int:
    """
    根據領域與 FQN 元件一步生成 64-bit symbol_uid。
    """
    d_id = parse_domain_id(domain)
    domain_name = DOMAIN_NAMES.get(d_id, str(domain))
    uri = create_canonical_uri(domain_name, namespace, fqn, arity)
    return generate_symbol_uid(d_id, uri)


def extract_domain_id(symbol_uid: int) -> int:
    """
    從 64-bit symbol_uid 中提取 domain_id。

    公式：(symbol_uid >> 56) & 0x7F
    達成 O(1) 零查找子圖路由。
    """
    return (symbol_uid >> DOMAIN_BIT_SHIFT) & DOMAIN_ID_MASK


def extract_local_hash(symbol_uid: int) -> int:
    """提取 64-bit symbol_uid 中低 56-bit 的局部哈希值"""
    return symbol_uid & MASK_56_BITS


def get_domain_name(domain_id_or_uid: int) -> str:
    """
    根據 domain_id 或完整 symbol_uid 取得領域名稱。
    若傳入大於 127 的數值，自動提取 domain_id。
    """
    d_id = domain_id_or_uid if domain_id_or_uid <= 127 else extract_domain_id(domain_id_or_uid)
    return DOMAIN_NAMES.get(d_id, f"unknown_domain_{d_id}")


def get_subgraph_filename(domain_id_or_uid: Union[int, DomainID]) -> str:
    """
    根據 domain_id 或完整 symbol_uid 取得對應之 SQLite 子圖檔名。
    達成 O(1) 零查找子圖路由。
    """
    if isinstance(domain_id_or_uid, DomainID):
        d_id = int(domain_id_or_uid.value)
    else:
        val = int(domain_id_or_uid)
        d_id = val if val <= 127 else extract_domain_id(val)
    
    if d_id in DOMAIN_SUBGRAPH_FILES:
        return DOMAIN_SUBGRAPH_FILES[d_id]
    return f"{d_id:02d}_domain_kb.sqlite"


# ============================================================================
# 資料模型 (Data Models)
# ============================================================================

@dataclass(frozen=True)
class FederatedSymbolRecord:
    """領域子圖 symbols 表資料紀錄"""
    symbol_uid: int
    domain_id: int
    canonical_uri: str
    fqn: str
    symbol_kind: str
    return_type_uid: Optional[int] = None
    is_root_entry: int = 0
    is_hub_anchor: int = 0
    l0_summary_json: Optional[str] = None
    l1_signature_json: Optional[str] = None


@dataclass(frozen=True)
class NavigationClosureRecord:
    """領域子圖 api_navigation_closure 表資料紀錄"""
    from_uid: int
    to_uid: int
    path_semantics: str
    path_hash: int
    hop_count: int
    is_to_hub: int = 0
    edge_chain_json: Optional[str] = None


@dataclass(frozen=True)
class CrossDomainInterfaceRecord:
    """跨領域介面映射 cross_domain_interfaces 表資料紀錄"""
    interface_id: Optional[int]
    source_domain_id: int
    source_uid: int
    target_domain_id: int
    target_uid: int
    coupling_type: str
    mapping_contract_json: Optional[str] = None


# ============================================================================
# DDL 與資料庫初始化工具 (Database Initialization Helpers)
# ============================================================================

FEDERATED_SCHEMA_SQL_PATH: Final[Path] = Path(__file__).resolve().parent / "federated_schema.sql"

SUBGRAPH_SCHEMA_DDL: Final[str] = """
-- 領域子圖 DDL (WITHOUT ROWID)
CREATE TABLE IF NOT EXISTS symbols (
    symbol_uid INTEGER NOT NULL PRIMARY KEY,
    domain_id INTEGER NOT NULL,
    canonical_uri TEXT NOT NULL UNIQUE,
    fqn TEXT NOT NULL,
    symbol_kind TEXT NOT NULL,
    return_type_uid INTEGER,
    is_root_entry INTEGER NOT NULL DEFAULT 0,
    is_hub_anchor INTEGER NOT NULL DEFAULT 0,
    l0_summary_json TEXT,
    l1_signature_json TEXT
) WITHOUT ROWID;

CREATE INDEX IF NOT EXISTS idx_symbols_fqn ON symbols(fqn);
CREATE INDEX IF NOT EXISTS idx_symbols_domain_kind ON symbols(domain_id, symbol_kind);
CREATE INDEX IF NOT EXISTS idx_symbols_root ON symbols(domain_id, is_root_entry) WHERE is_root_entry = 1;
CREATE INDEX IF NOT EXISTS idx_symbols_hub ON symbols(domain_id, is_hub_anchor) WHERE is_hub_anchor = 1;

CREATE TABLE IF NOT EXISTS api_navigation_closure (
    from_uid INTEGER NOT NULL,
    to_uid INTEGER NOT NULL,
    path_semantics TEXT NOT NULL,
    path_hash INTEGER NOT NULL,
    hop_count INTEGER NOT NULL,
    is_to_hub INTEGER NOT NULL DEFAULT 0,
    edge_chain_json TEXT,
    PRIMARY KEY (from_uid, to_uid, path_semantics, path_hash)
) WITHOUT ROWID;

CREATE INDEX IF NOT EXISTS idx_closure_lookup ON api_navigation_closure (
    from_uid,
    hop_count,
    to_uid
);

CREATE INDEX IF NOT EXISTS idx_closure_to_hub ON api_navigation_closure (
    from_uid,
    is_to_hub,
    hop_count,
    to_uid
);
"""

BRIDGE_SCHEMA_DDL: Final[str] = """
-- 跨領域介面映射 DDL
CREATE TABLE IF NOT EXISTS cross_domain_interfaces (
    interface_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_domain_id INTEGER NOT NULL,
    source_uid INTEGER NOT NULL,
    target_domain_id INTEGER NOT NULL,
    target_uid INTEGER NOT NULL,
    coupling_type TEXT NOT NULL,
    mapping_contract_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_cdi_source ON cross_domain_interfaces (
    source_domain_id,
    source_uid
);

CREATE INDEX IF NOT EXISTS idx_cdi_target ON cross_domain_interfaces (
    target_domain_id,
    target_uid
);

CREATE INDEX IF NOT EXISTS idx_cdi_coupling ON cross_domain_interfaces (
    coupling_type
);
"""


def init_subgraph_database(db: Union[str, Path, sqlite3.Connection]) -> sqlite3.Connection:
    """初始化領域子圖資料庫結構"""
    if isinstance(db, (str, Path)):
        conn = sqlite3.connect(str(db))
    else:
        conn = db
    conn.executescript(SUBGRAPH_SCHEMA_DDL)
    conn.commit()
    return conn


def init_bridge_database(db: Union[str, Path, sqlite3.Connection]) -> sqlite3.Connection:
    """初始化多物理場橋接資料庫結構"""
    if isinstance(db, (str, Path)):
        conn = sqlite3.connect(str(db))
    else:
        conn = db
    conn.executescript(BRIDGE_SCHEMA_DDL)
    conn.commit()
    return conn
