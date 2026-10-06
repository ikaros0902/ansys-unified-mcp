"""Unified session registry.

Replaces the scattered module-global sessions (``_mechanical``, ``_osl``,
``_fluent_session``, ``_modeler`` ...) with a single registry that can hold
multiple live connections per product, keyed by an arbitrary string (typically
the gRPC port, a PID, or a sentinel like ``"embedded"``).

Design goals:
- One place owns all live sessions, so "connect one way, act another way"
  can no longer silently see a different (empty) global.
- True multi-instance: several sessions may coexist per product; each product
  tracks a "current" (most recently bound) session used when a caller does not
  specify a target key.
"""

from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional


class SessionRegistry:
    """Thread-safe registry of live product sessions.

    A "product" is a logical ANSYS module name (e.g. ``"mechanical"``,
    ``"fluent"``, ``"geometry"``, ``"optislang"``). A "key" identifies one
    connection within that product (e.g. ``"10000"`` for a gRPC port).

    Multi-workspace isolation:
        Each session also belongs to a *workspace* (an opaque string, default
        ``"default"``). Two sessions for the same product but different
        workspaces are fully isolated: closing one never affects the other,
        and ``current`` is tracked per (workspace, product). Callers that omit
        ``workspace`` keep the historical single-workspace behaviour.
    """

    DEFAULT_WORKSPACE = "default"

    def __init__(self) -> None:
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._current: Dict[str, str] = {}
        self._lock = threading.RLock()

    @staticmethod
    def _scope(product: str, workspace: Optional[str]) -> str:
        """將 (workspace, product) 收斂為單一內部命名空間鍵。

        以 workspace 作為 product 的前綴命名空間，使同產品在不同 workspace
        下落在互斥的內部桶，達成隔離；workspace 省略時走 ``default``，內部鍵
        與歷史單一 workspace 時的 product 語意等價（但帶前綴），對外介面不變。
        """
        ws = workspace or SessionRegistry.DEFAULT_WORKSPACE
        return f"{ws}::{product}"

    def put(
        self,
        product: str,
        key: str,
        session: Any,
        make_current: bool = True,
        workspace: Optional[str] = None,
    ) -> None:
        """Register (or replace) a session and optionally mark it current."""
        scope = self._scope(product, workspace)
        with self._lock:
            self._sessions.setdefault(scope, {})[key] = session
            if make_current:
                self._current[scope] = key

    def get(
        self,
        product: str,
        key: Optional[str] = None,
        workspace: Optional[str] = None,
    ) -> Optional[Any]:
        """Return a session by key, or the current session when key is None."""
        scope = self._scope(product, workspace)
        with self._lock:
            product_sessions = self._sessions.get(scope)
            if not product_sessions:
                return None
            if key is None:
                key = self._current.get(scope)
                if key is None:
                    return None
            return product_sessions.get(key)

    def current_key(self, product: str, workspace: Optional[str] = None) -> Optional[str]:
        scope = self._scope(product, workspace)
        with self._lock:
            return self._current.get(scope)

    def set_current(self, product: str, key: str, workspace: Optional[str] = None) -> bool:
        """Point the product's current session at an existing key."""
        scope = self._scope(product, workspace)
        with self._lock:
            if key in self._sessions.get(scope, {}):
                self._current[scope] = key
                return True
            return False

    def get_live(
        self,
        product: str,
        key: Optional[str] = None,
        probe_fn=None,
        workspace: Optional[str] = None,
    ) -> Optional[Any]:
        """Return a session, optionally testing it with probe_fn and dropping it if dead."""
        session = self.get(product, key, workspace=workspace)
        if session is None:
            return None
        if probe_fn is not None:
            try:
                if not probe_fn(session):
                    self.drop(product, key or self.current_key(product, workspace), workspace=workspace)
                    return None
            except Exception:
                self.drop(product, key or self.current_key(product, workspace), workspace=workspace)
                return None
        return session

    def drop(
        self,
        product: str,
        key: Optional[str] = None,
        workspace: Optional[str] = None,
    ) -> Optional[Any]:
        """Remove and return a session. key=None drops the current session."""
        scope = self._scope(product, workspace)
        with self._lock:
            product_sessions = self._sessions.get(scope)
            if not product_sessions:
                return None
            if key is None:
                key = self._current.get(scope)
                if key is None:
                    return None
            session = product_sessions.pop(key, None)
            if self._current.get(scope) == key:
                # Promote any remaining session to current, else clear.
                remaining = next(iter(product_sessions), None)
                if remaining is not None:
                    self._current[scope] = remaining
                else:
                    self._current.pop(scope, None)
            return session

    def keys(self, product: str, workspace: Optional[str] = None) -> List[str]:
        scope = self._scope(product, workspace)
        with self._lock:
            return list(self._sessions.get(scope, {}).keys())

    def snapshot(self) -> Dict[str, Dict[str, Any]]:
        """Return a description of all sessions (product -> {key: current?}).

        為維持既有呼叫端的回傳格式，snapshot 以「對外 product 名稱」為頂層鍵。
        ``default`` workspace 的 product 直接以 product 名稱呈現 (向後相容)；
        非 default workspace 則以 ``workspace::product`` 複合名稱呈現，避免同
        product 跨 workspace 的鍵碰撞覆蓋。
        """
        with self._lock:
            result: Dict[str, Dict[str, Any]] = {}
            for scope, sessions in self._sessions.items():
                ws, _, product = scope.partition("::")
                label = product if ws == self.DEFAULT_WORKSPACE else scope
                result[label] = {
                    key: {"current": self._current.get(scope) == key}
                    for key in sessions
                }
            return result


# Process-wide singleton shared by all product facades.
registry = SessionRegistry()
