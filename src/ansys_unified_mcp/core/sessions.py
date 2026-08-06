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
    """

    def __init__(self) -> None:
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._current: Dict[str, str] = {}
        self._lock = threading.RLock()

    def put(self, product: str, key: str, session: Any, make_current: bool = True) -> None:
        """Register (or replace) a session and optionally mark it current."""
        with self._lock:
            self._sessions.setdefault(product, {})[key] = session
            if make_current:
                self._current[product] = key

    def get(self, product: str, key: Optional[str] = None) -> Optional[Any]:
        """Return a session by key, or the current session when key is None."""
        with self._lock:
            product_sessions = self._sessions.get(product)
            if not product_sessions:
                return None
            if key is None:
                key = self._current.get(product)
                if key is None:
                    return None
            return product_sessions.get(key)

    def current_key(self, product: str) -> Optional[str]:
        with self._lock:
            return self._current.get(product)

    def set_current(self, product: str, key: str) -> bool:
        """Point the product's current session at an existing key."""
        with self._lock:
            if key in self._sessions.get(product, {}):
                self._current[product] = key
                return True
            return False

    def drop(self, product: str, key: Optional[str] = None) -> Optional[Any]:
        """Remove and return a session. key=None drops the current session."""
        with self._lock:
            product_sessions = self._sessions.get(product)
            if not product_sessions:
                return None
            if key is None:
                key = self._current.get(product)
                if key is None:
                    return None
            session = product_sessions.pop(key, None)
            if self._current.get(product) == key:
                # Promote any remaining session to current, else clear.
                remaining = next(iter(product_sessions), None)
                if remaining is not None:
                    self._current[product] = remaining
                else:
                    self._current.pop(product, None)
            return session

    def keys(self, product: str) -> List[str]:
        with self._lock:
            return list(self._sessions.get(product, {}).keys())

    def snapshot(self) -> Dict[str, Dict[str, Any]]:
        """Return a description of all sessions (product -> {key: current?})."""
        with self._lock:
            return {
                product: {
                    key: {"current": self._current.get(product) == key}
                    for key in sessions
                }
                for product, sessions in self._sessions.items()
            }


# Process-wide singleton shared by all product facades.
registry = SessionRegistry()
