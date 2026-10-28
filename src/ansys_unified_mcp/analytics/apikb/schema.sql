-- ANSYS API Knowledge Base SQLite Schema
CREATE TABLE IF NOT EXISTS symbols (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product TEXT NOT NULL,
    kind TEXT NOT NULL,
    fqname TEXT NOT NULL,
    name TEXT NOT NULL,
    doc TEXT,
    release TEXT NOT NULL DEFAULT 'unknown',
    interface TEXT NOT NULL DEFAULT 'unknown',
    source_id INTEGER,
    UNIQUE(product, release, interface, fqname),
    FOREIGN KEY(source_id) REFERENCES api_sources(id)
);

CREATE TABLE IF NOT EXISTS api_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product TEXT NOT NULL,
    release TEXT NOT NULL,
    interface TEXT NOT NULL,
    source_path TEXT NOT NULL,
    sdk_version TEXT NOT NULL DEFAULT '',
    sha256 TEXT NOT NULL,
    artifact_sha256 TEXT NOT NULL DEFAULT '',
    rea_evidence_id TEXT NOT NULL DEFAULT '',
    ingested_at TEXT NOT NULL,
    UNIQUE(product, release, interface, source_path)
);

CREATE TABLE IF NOT EXISTS api_kb_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sig_hash TEXT UNIQUE NOT NULL,
    kind TEXT NOT NULL,
    name TEXT NOT NULL,
    signature TEXT,
    return_type TEXT,
    doc TEXT
);

CREATE TABLE IF NOT EXISTS symbol_members (
    symbol_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    is_inherited INTEGER DEFAULT 0,
    PRIMARY KEY (symbol_id, member_id),
    FOREIGN KEY (symbol_id) REFERENCES symbols(id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    src_symbol_id INTEGER NOT NULL,
    dst_symbol_id INTEGER NOT NULL,
    rel TEXT NOT NULL,
    via_member_id INTEGER,
    FOREIGN KEY (src_symbol_id) REFERENCES symbols(id) ON DELETE CASCADE,
    FOREIGN KEY (dst_symbol_id) REFERENCES symbols(id) ON DELETE CASCADE,
    FOREIGN KEY (via_member_id) REFERENCES members(id) ON DELETE SET NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS search_fts USING fts5(
    item_type UNINDEXED,
    ref_id UNINDEXED,
    product,
    fqname,
    name,
    name_split,
    signature,
    doc,
    release UNINDEXED,
    interface UNINDEXED,
    source_id UNINDEXED,
    tokenize = 'trigram'
);


-- Stage 3: Transitive Closure & Navigation
CREATE TABLE IF NOT EXISTS api_navigation_closure (
    from_uid INTEGER NOT NULL,
    to_uid INTEGER NOT NULL,
    path_semantics TEXT NOT NULL,
    path_hash TEXT NOT NULL,
    product TEXT NOT NULL,
    depth INTEGER NOT NULL,
    path_nodes TEXT NOT NULL,
    path_steps TEXT NOT NULL,
    path_display TEXT,
    from_name TEXT,
    to_name TEXT,
    is_from_root INTEGER DEFAULT 0,
    is_from_hub INTEGER DEFAULT 0,
    is_to_hub INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (from_uid, to_uid, path_semantics, path_hash)
);

CREATE INDEX IF NOT EXISTS idx_closure_from ON api_navigation_closure(from_uid);
CREATE INDEX IF NOT EXISTS idx_closure_to ON api_navigation_closure(to_uid);
CREATE INDEX IF NOT EXISTS idx_closure_product ON api_navigation_closure(product);
CREATE INDEX IF NOT EXISTS idx_closure_semantics ON api_navigation_closure(path_semantics);
CREATE INDEX IF NOT EXISTS idx_closure_lookup ON api_navigation_closure(from_name, to_name);
