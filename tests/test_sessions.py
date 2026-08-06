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
