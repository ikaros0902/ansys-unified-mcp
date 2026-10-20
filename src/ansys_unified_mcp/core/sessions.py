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
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SessionRecord:
    """連線及其生命週期狀態；快取不可跨實例共用。"""

    instance: Any
    owned: bool = False
    cache: dict = field(default_factory=dict)
    # 必須維持 threading.Lock（而非 RLock）：MechanicalController 的逾時路徑
    # 經 exc.future.add_done_callback(cleanup) 在背景執行緒釋放這個鎖，與搶鎖
    # 的呼叫執行緒不同——這在 Lock 下合法，但若誤改為 RLock 會因釋放執行緒與
    # 持有執行緒不同而拋 RuntimeError。與 SessionRegistry._lock（RLock，見
    # acquire_live 的 docstring）是對稱但不同的另一個不變量，不可混淆。
    lock: Any = field(default_factory=threading.Lock)
    close_error: str | None = None

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
        *,
        owned: bool = False,
    ) -> None:
        """Register (or replace) a session and optionally mark it current."""
        scope = self._scope(product, workspace)
        with self._lock:
            previous = self._sessions.get(scope, {}).get(key)
            if previous is not None and previous.instance is session:
                previous.cache.clear()
                previous.owned = previous.owned or owned
            else:
                if previous is not None:
                    raise ValueError(f"Session {product}/{key} already exists; disconnect it first.")
                self._sessions.setdefault(scope, {})[key] = SessionRecord(session, owned)
            if make_current:
                self._current[scope] = key

    def get(self, product: str, key: Optional[str] = None, workspace: Optional[str] = None) -> Optional[Any]:
        record = self.record(product, key, workspace)
        return record.instance if record else None

    def record(self, product: str, key: Optional[str] = None, workspace: Optional[str] = None) -> Optional[SessionRecord]:
        scope = self._scope(product, workspace)
        with self._lock:
            return self._sessions.get(scope, {}).get(key if key is not None else self._current.get(scope))

    def close(self, product: str, method: str, key: Optional[str] = None, workspace: Optional[str] = None) -> dict:
        """明確關閉；失敗保留連線記錄，避免誤報成功。"""
        with self._lock:
            key = key if key is not None else self.current_key(product, workspace)
            record = self.record(product, key, workspace)
        if record is None:
            return {"ok": True, "message": "No active session."}
        if not record.lock.acquire(blocking=False):
            return {"ok": False, "error": "Session is busy."}
        try:
            getattr(record.instance, method)()
            self.drop(product, key, workspace)
            return {"ok": True, "message": "Session closed."}
        except Exception as exc:
            record.close_error = str(exc)
            return {"ok": False, "error": str(exc)}
        finally:
            record.lock.release()

    def cleanup_owned(self) -> list[dict]:
        """只終止服務自行啟動的實例；失敗記錄留待查核。"""
        methods = {"mechanical": "exit", "fluent": "exit", "geometry": "close",
                   "optislang": "dispose", "workbench": "exit"}
        with self._lock:
            targets = [(scope, key) for scope, items in self._sessions.items()
                       for key, record in items.items() if record.owned]
        results = []
        for scope, key in targets:
            workspace, _, product = scope.partition("::")
            results.append(self.close(product, methods[product], key, workspace))
        return results

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

    def get_live(self, product: str, key: Optional[str] = None, probe_fn=None,
                 workspace: Optional[str] = None) -> Optional[Any]:
        with self._lock:
            key = key if key is not None else self.current_key(product, workspace)
            record = self.record(product, key, workspace)
        if record is None:
            return None
        if probe_fn is not None:
            try:
                live = probe_fn(record.instance)
            except Exception:
                live = False
            if not live:
                with self._lock:
                    if self.record(product, key, workspace) is record:
                        self.drop(product, key, workspace)
                return None
        return record.instance


    def acquire_live(
        self,
        product: str,
        key: Optional[str] = None,
        probe_fn=None,
        workspace: Optional[str] = None,
    ) -> tuple[Optional["SessionRecord"], Optional[str]]:
        """原子化查表+搶鎖 -> 持鎖探活，三步驟合一，探活在鎖保護下執行。

        成功時回傳 (record, None)，record.lock 已被本次呼叫持有，呼叫端必須
        在 try/finally 中呼叫 record.lock.release()。
        失敗時回傳 (None, reason)，reason ∈ {"not_connected", "busy", "dead"}，
        不持有任何鎖，呼叫端不需要 release。

        注意：探活移到鎖之後執行（而非 get_live() 原先鎖外探活的順序），避免
        另一執行緒持鎖執行長時間腳本期間，探活呼叫並發送進同一底層 channel。

        [V4 訂正] drop() 與「查表+搶鎖」同在 self._lock 保護範圍內，因此另一
        個執行緒（T2）只會觀測到兩種狀態：drop() 執行前（T2 搶鎖失敗回
        "busy"，因為 T1 仍持有 record.lock）或 drop() 執行後（T2 查表直接
        得到 None 回 "not_connected"），不存在「record 已移除但鎖狀態未知」
        的中間觀測窗口。真正要避免的是反過來的順序（先 release 再 drop）：
        若先釋放鎖，T2 可能在 record 被移除之前搶到這個鎖，對一個探活剛失敗、
        即將被判定為死亡的 session 送出腳本。

        必須同時成立的兩個不變量（缺一都會引入死鎖或競態，不得在後續修改中
        單獨調整其中一個）：
        1. record.lock.acquire() 的 blocking 參數必須永遠是 False——若改成
           True 或加 timeout，會在持有 self._lock 期間等待，一旦其他執行緒
           也需要 self._lock 就立刻死鎖。
        2. self._lock 必須維持 RLock（而非 Lock）——因為下方 dead 分支是在
           已持有 self._lock 的情況下重入呼叫 self.drop()，drop() 內部也會
           `with self._lock:`；RLock 允許同一執行緒重入不卡死，若誤改為
           Lock，同一執行緒對自己已持有的鎖二次 acquire() 會永久阻塞。
        """
        scope = self._scope(product, workspace)
        with self._lock:
            key = key if key is not None else self._current.get(scope)
            record = self._sessions.get(scope, {}).get(key)
            if record is None:
                return None, "not_connected"
            if not record.lock.acquire(blocking=False):
                return None, "busy"
        if probe_fn is not None:
            try:
                alive = probe_fn(record.instance)
            except Exception:
                alive = False
            if not alive:
                # 必須先 drop 再 release：見上方 docstring 說明。
                with self._lock:
                    if self._sessions.get(scope, {}).get(key) is record:
                        self.drop(product, key, workspace)
                record.lock.release()
                return None, "dead"
        return record, None

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
            if session is not None:
                session.cache.clear()
            return session.instance if session else None

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
                    key: {"current": self._current.get(scope) == key, "owned": sessions[key].owned,
                          "busy": sessions[key].lock.locked(), "close_error": sessions[key].close_error}
                    for key in sessions
                }
            return result


    def clear_all(self) -> None:
        """清空所有 session 記錄與 current 指標，僅供測試隔離使用。

        生產程式碼不應呼叫此方法；它會丟棄所有連線記錄但不會呼叫任何
        session 的斷線方法（不負責優雅關閉底層連線，純粹清空記憶體狀態）。
        """
        with self._lock:
            self._sessions.clear()
            self._current.clear()


# Process-wide singleton shared by all product facades.
registry = SessionRegistry()
