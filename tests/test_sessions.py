"""Smoke tests for the core SessionRegistry.

These guard the shared session bookkeeping that products/mechanical.py and
products/optislang.py rely on. Pure Python, no ANSYS packages required.
"""

from ansys_unified_mcp.core.sessions import SessionRegistry


def test_put_get_current():
    r = SessionRegistry()
    assert r.get("mechanical") is None
    r.put("mechanical", "10000", "sessionA")
    assert r.get("mechanical") == "sessionA"           # current session
    assert r.get("mechanical", "10000") == "sessionA"  # explicit key
    assert r.current_key("mechanical") == "10000"


def test_multi_session_and_set_current():
    r = SessionRegistry()
    r.put("mechanical", "10000", "A")
    r.put("mechanical", "10001", "B")  # newest becomes current
    assert r.get("mechanical") == "B"
    assert set(r.keys("mechanical")) == {"10000", "10001"}
    assert r.set_current("mechanical", "10000") is True
    assert r.get("mechanical") == "A"
    assert r.set_current("mechanical", "missing") is False


def test_drop_promotes_then_clears():
    r = SessionRegistry()
    r.put("fluent", "1", "A")
    r.put("fluent", "2", "B")          # current = 2
    assert r.drop("fluent") == "B"     # drops current
    assert r.current_key("fluent") == "1"  # remaining promoted to current
    assert r.drop("fluent", "1") == "A"
    assert r.current_key("fluent") is None
    assert r.drop("fluent") is None    # empty product is a safe no-op


def test_snapshot_marks_current():
    r = SessionRegistry()
    r.put("optislang", "default", object())
    snap = r.snapshot()
    assert snap["optislang"]["default"]["current"] is True


def test_workspace_isolation_same_product():
    """同產品、不同 workspace 的 session 完全隔離，互不覆蓋。"""
    r = SessionRegistry()
    r.put("geometry", "50051", "wsA_session", workspace="A")
    r.put("geometry", "50052", "wsB_session", workspace="B")
    # 各自取回自己 workspace 的 current，互不干擾
    assert r.get("geometry", workspace="A") == "wsA_session"
    assert r.get("geometry", workspace="B") == "wsB_session"
    assert r.keys("geometry", workspace="A") == ["50051"]
    assert r.keys("geometry", workspace="B") == ["50052"]


def test_workspace_drop_does_not_affect_other():
    """關閉某 workspace 的 session 不影響另一 workspace。"""
    r = SessionRegistry()
    r.put("mechanical", "10000", "A", workspace="proj1")
    r.put("mechanical", "10000", "B", workspace="proj2")  # 相同 key 不同 workspace
    assert r.drop("mechanical", "10000", workspace="proj1") == "A"
    # proj1 已清空，proj2 不受影響
    assert r.get("mechanical", workspace="proj1") is None
    assert r.get("mechanical", "10000", workspace="proj2") == "B"
    assert r.current_key("mechanical", workspace="proj2") == "10000"


def test_default_workspace_backward_compatible():
    """不指定 workspace 時行為與歷史單一 workspace 完全一致。"""
    r = SessionRegistry()
    r.put("fluent", "1", "A")  # 無 workspace -> default
    # 顯式 default 與省略視為同一桶
    assert r.get("fluent", workspace="default") == "A"
    assert r.get("fluent") == "A"
    snap = r.snapshot()
    # default workspace 的 product 以 product 名稱呈現 (非複合名)
    assert "fluent" in snap
    assert snap["fluent"]["1"]["current"] is True


def test_snapshot_non_default_workspace_label():
    """非 default workspace 以複合名稱呈現，避免跨 workspace 鍵碰撞。"""
    r = SessionRegistry()
    r.put("geometry", "50051", "A")              # default
    r.put("geometry", "50051", "B", workspace="X")  # 同 product 同 key，不同 workspace
    snap = r.snapshot()
    assert "geometry" in snap               # default
    assert "X::geometry" in snap            # 非 default 複合名
    assert snap["geometry"]["50051"]["current"] is True
    assert snap["X::geometry"]["50051"]["current"] is True
