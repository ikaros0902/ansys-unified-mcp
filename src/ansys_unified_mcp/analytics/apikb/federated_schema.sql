-- ============================================================================
-- ANSYS Federated API Knowledge Base Schemas (Stage 3)
-- ============================================================================
-- 本檔案定義 10 個領域子圖與跨領域多物理場橋接資料庫之標準 DDL。
-- 領域子圖 (00_foundation ~ 09_framework) 使用 WITHOUT ROWID 最佳化查詢與儲存空間。
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 區塊 1: 領域子圖標準 DDL (00_foundation_kb.sqlite ~ 09_framework_kb.sqlite)
-- ----------------------------------------------------------------------------

-- 1.1 符號主表 (Symbols Table)
-- 儲存 64-bit 位元分區識別碼、規格化 URI、全限定名及層級摘要
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

-- 1.2 API 導航傳遞閉包表 (API Navigation Transitive Closure Table)
-- 預先計算並快取符號間的有向導航路徑（包含跳數、路徑語意及是否直達樞紐節點）
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

-- 導航查詢覆蓋索引：加速從起點展開路徑檢索
CREATE INDEX IF NOT EXISTS idx_closure_lookup ON api_navigation_closure (
    from_uid,
    hop_count,
    to_uid
);

-- 樞紐跳躍覆蓋索引：加速從起點快速收斂至 Hub Anchor
CREATE INDEX IF NOT EXISTS idx_closure_to_hub ON api_navigation_closure (
    from_uid,
    is_to_hub,
    hop_count,
    to_uid
);


-- ----------------------------------------------------------------------------
-- 區塊 2: 跨領域介面映射表 DDL (multiphysics_bridge.sqlite)
-- ----------------------------------------------------------------------------

-- 2.1 多物理場跨領域介面映射表 (Cross-Domain Interfaces Table)
-- 記錄熱-結構、流-固等跨領域物理場介面耦合與映射關係
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
