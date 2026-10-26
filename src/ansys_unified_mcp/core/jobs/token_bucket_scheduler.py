"""Feature-level token bucket license scheduler with human buffer gating.

Prevents interactive license starvation by reserving human buffer tokens, enforces
atomic multi-feature checkout, and tracks 300-second license lingering on crash.
Includes support for lmutil query, Sentinel LDK HASP port 1947 probe, and mock mode.
"""

from __future__ import annotations

import logging
import os
import re
import socket
import subprocess
import threading
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Dict, Generator, Iterable, List, Optional, Set, Tuple, Union

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class LicenseSchedulerError(Exception):
    """Base exception for license scheduler errors."""
    pass


class LicenseUnavailableError(LicenseSchedulerError):
    """Raised when requested license tokens are unavailable or violate human buffer."""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__(message)
        self.details = details


class LicenseAcquisitionTimeoutError(LicenseSchedulerError):
    """Raised when license acquisition times out in waiting mode."""
    pass


class FeatureInCooldownError(LicenseUnavailableError):
    """Raised when attempting to check out a feature currently in linger cooldown."""
    pass


class SentinelServiceUnavailableError(LicenseUnavailableError):
    """Raised when external Sentinel/FlexNet daemon cannot be contacted."""
    pass


class FeatureBalance(BaseModel):
    """Token balance descriptor for a single license feature."""
    feature_name: str
    total_tokens: int
    used_tokens: int = 0
    available_tokens: int = 0
    human_reserved: int = 1
    in_cooldown: bool = False
    cooldown_remaining_sec: float = 0.0
    source: str = "flexnet"
    raw_info: Optional[str] = None

    # Properties for compatibility
    @property
    def feature(self) -> str:
        return self.feature_name

    @property
    def total(self) -> int:
        return self.total_tokens

    @property
    def in_use(self) -> int:
        return self.used_tokens

    @property
    def available(self) -> int:
        return self.available_tokens


class LicenseLease(BaseModel):
    """Represents an active checked-out license lease."""
    lease_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    task_id: str
    features: Dict[str, int]
    acquired_at: float = Field(default_factory=time.time)
    expires_at: Optional[float] = None
    is_active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PreflightCheckResult(BaseModel):
    """Result of pre-dispatch license feasibility check."""
    can_proceed: bool
    reason: str
    balances: Dict[str, FeatureBalance] = Field(default_factory=dict)
    denied_features: List[str] = Field(default_factory=list)
    active_agent_tasks: Dict[str, int] = Field(default_factory=dict)
    human_buffers: Dict[str, int] = Field(default_factory=dict)
    cooldown_status: Dict[str, float] = Field(default_factory=dict)
    blocking_reasons: List[str] = Field(default_factory=list)

    @property
    def allowed(self) -> bool:
        return self.can_proceed

    @property
    def feature_balances(self) -> Dict[str, FeatureBalance]:
        return self.balances

    @property
    def is_in_cooldown(self) -> bool:
        return any(rem > 0 for rem in self.cooldown_status.values()) or any(
            b.in_cooldown for b in self.balances.values()
        )


class LicenseLingerRecord:
    """Tracks lingering license features after abnormal task termination."""

    def __init__(self, task_id: str, feature: str, expire_time: float, reason: str = "abnormal_exit") -> None:
        self.task_id = task_id
        self.feature = feature
        self.expire_time = expire_time
        self.reason = reason

    def is_active(self, current_time: Optional[float] = None) -> bool:
        now = time.time() if current_time is None else current_time
        return now < self.expire_time

    @property
    def remaining(self) -> float:
        return max(0.0, self.expire_time - time.time())


class TokenBucketLicenseScheduler:
    """Pre-check token bucket license scheduler with human priority buffering."""

    DEFAULT_OPTICAL_FEATURES: Set[str] = {
        "speos",
        "speos_optic",
        "speos_core",
        "opticstudio",
        "zemax",
        "zemax_opticstudio",
    }

    # Standard composite feature packages
    SPEOS_FEATURES: List[str] = ["spaceclaim", "speos_optic"]
    ROCKY_FEATURES: List[str] = ["rocky_prepost", "gpu_token"]

    def __init__(
        self,
        inventory: Optional[Dict[str, int]] = None,
        human_buffer: int = 1,
        linger_duration: float = 300.0,
        cooldown_duration: Optional[float] = None,
        mock_mode: bool = False,
        license_server: Optional[str] = None,
        lmutil_path: Optional[Union[str, Path]] = None,
        ansyslic_admin_path: Optional[Union[str, Path]] = None,
        sentinel_host: str = "127.0.0.1",
        sentinel_port: int = 1947,
        optical_features: Optional[Set[str]] = None,
    ) -> None:
        self.inventory: Dict[str, int] = dict(inventory or {})
        self.active_allocations: Dict[str, int] = {f: 0 for f in self.inventory}
        self.task_allocations: Dict[str, Dict[str, int]] = {}
        self.leases: Dict[str, LicenseLease] = {}
        self.human_buffer = max(0, int(human_buffer))

        cd = cooldown_duration if cooldown_duration is not None else linger_duration
        self.linger_duration = max(0.0, float(cd))
        self.cooldown_duration = self.linger_duration
        self.linger_records: Dict[str, LicenseLingerRecord] = {}

        self.mock_mode = mock_mode or (os.environ.get("ANSYS_MOCK_LICENSE", "0") in ("1", "true", "True"))
        self.license_server = license_server or os.environ.get("ANSYSLMD_LICENSE_FILE")
        self.lmutil_path = Path(lmutil_path) if lmutil_path else self._detect_lmutil()
        self.ansyslic_admin_path = Path(ansyslic_admin_path) if ansyslic_admin_path else self._detect_ansyslic_admin()

        self.sentinel_host = sentinel_host
        self.sentinel_port = int(sentinel_port)
        self.optical_features = set(optical_features) if optical_features is not None else set(self.DEFAULT_OPTICAL_FEATURES)

        self._lock = threading.RLock()
        self._mock_balances: Dict[str, Dict[str, int]] = {}
        self._mock_sentinel_status: Dict[Tuple[str, int], bool] = {}

    def _detect_lmutil(self) -> Optional[Path]:
        """Detect lmutil binary in standard ANSYS installation paths or PATH."""
        env_path = os.environ.get("ANSYS_LMUTIL_PATH")
        if env_path and Path(env_path).is_file():
            return Path(env_path)

        for root in [
            os.environ.get("AWP_ROOT251"),
            os.environ.get("AWP_ROOT242"),
            os.environ.get("AWP_ROOT241"),
            os.environ.get("ANSYS_SHARED_DIR", r"C:\Program Files\ANSYS Inc\Shared Files"),
        ]:
            if not root:
                continue
            candidate = Path(root) / "Licensing" / "winx64" / "lmutil.exe"
            if candidate.is_file():
                return candidate
            candidate_shared = Path(root) / "winx64" / "lmutil.exe"
            if candidate_shared.is_file():
                return candidate_shared

        import shutil
        found = shutil.which("lmutil")
        return Path(found) if found else None

    def _detect_ansyslic_admin(self) -> Optional[Path]:
        """Detect ansyslic_admin binary in standard ANSYS installation paths."""
        env_path = os.environ.get("ANSYS_ANSLIC_ADMIN_PATH")
        if env_path and Path(env_path).is_file():
            return Path(env_path)

        for root in [
            os.environ.get("AWP_ROOT251"),
            os.environ.get("AWP_ROOT242"),
            os.environ.get("ANSYS_SHARED_DIR", r"C:\Program Files\ANSYS Inc\Shared Files"),
        ]:
            if not root:
                continue
            candidate = Path(root) / "Licensing" / "winx64" / "ansyslic_admin.exe"
            if candidate.is_file():
                return candidate

        import shutil
        found = shutil.which("ansyslic_admin")
        return Path(found) if found else None

    # -------------------------------------------------------------------------
    # Inventory & Mock State Helpers
    # -------------------------------------------------------------------------

    def set_inventory(self, feature: str, total_tokens: int) -> None:
        """Configure installed token count for a feature."""
        f_norm = feature.strip().lower()
        with self._lock:
            self.inventory[f_norm] = int(total_tokens)
            if f_norm not in self.active_allocations:
                self.active_allocations[f_norm] = 0

    def set_mock_feature_balance(self, feature: str, total: int, in_use: int) -> None:
        """Set mock total and in_use balance for offline testing."""
        f_norm = feature.strip().lower()
        with self._lock:
            self.inventory[f_norm] = int(total)
            self._mock_balances[f_norm] = {
                "total": max(0, int(total)),
                "in_use": max(0, int(in_use)),
            }

    def set_mock_sentinel_status(self, host: str, port: int, is_reachable: bool) -> None:
        """Set mock reachability for Sentinel LDK HASP port."""
        with self._lock:
            self._mock_sentinel_status[(host, port)] = bool(is_reachable)

    def reset_mock_state(self) -> None:
        """Clear all mock configurations, inventory, and active leases."""
        with self._lock:
            self.inventory.clear()
            self._mock_balances.clear()
            self._mock_sentinel_status.clear()
            self.active_allocations.clear()
            self.task_allocations.clear()
            self.leases.clear()
            self.linger_records.clear()

    # -------------------------------------------------------------------------
    # Sentinel LDK HASP Port 1947 Probe
    # -------------------------------------------------------------------------

    def probe_sentinel_hasp(self, host: Optional[str] = None, port: Optional[int] = None, timeout: float = 1.5) -> bool:
        """Probe Sentinel LDK HASP Port 1947 for optical module licensing health."""
        target_host = host or self.sentinel_host
        target_port = port if port is not None else self.sentinel_port

        if self.mock_mode:
            with self._lock:
                return self._mock_sentinel_status.get((target_host, target_port), True)

        try:
            with socket.create_connection((target_host, target_port), timeout=timeout):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError) as exc:
            logger.warning("Sentinel LDK HASP probe failed for %s:%d - %s", target_host, target_port, exc)
            return False

    # -------------------------------------------------------------------------
    # Real-Time Feature Balance Query
    # -------------------------------------------------------------------------

    def query_feature_balance(self, feature: str) -> FeatureBalance:
        """Query real-time balance for a given license feature."""
        f_norm = feature.strip().lower()

        if self.mock_mode:
            with self._lock:
                mock_entry = self._mock_balances.get(f_norm)
                if mock_entry:
                    total = mock_entry["total"]
                    in_use = mock_entry["in_use"]
                    avail = max(0, total - in_use)
                    return FeatureBalance(
                        feature_name=f_norm,
                        total_tokens=total,
                        used_tokens=in_use,
                        available_tokens=avail,
                        human_reserved=self.human_buffer,
                        in_cooldown=self.is_in_linger(f_norm),
                        cooldown_remaining_sec=self.get_linger_remaining(f_norm),
                        source="mock",
                    )
                total = self.inventory.get(f_norm, 5)
                active = self.active_allocations.get(f_norm, 0)
                avail = max(0, total - active)
                return FeatureBalance(
                    feature_name=f_norm,
                    total_tokens=total,
                    used_tokens=active,
                    available_tokens=avail,
                    human_reserved=self.human_buffer,
                    in_cooldown=self.is_in_linger(f_norm),
                    cooldown_remaining_sec=self.get_linger_remaining(f_norm),
                    source="inventory",
                )

        # 1. Try lmutil
        if self.lmutil_path and self.lmutil_path.exists():
            cmd = [str(self.lmutil_path), "lmstat"]
            if self.license_server:
                cmd.extend(["-c", self.license_server])
            cmd.extend(["-f", f_norm])
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=False)
                parsed = self._parse_lmutil_output(f_norm, proc.stdout + "\n" + proc.stderr)
                if parsed is not None:
                    return parsed
            except Exception as exc:
                logger.warning("lmutil query failed for feature %s: %s", f_norm, exc)

        # 2. Try ansyslic_admin
        if self.ansyslic_admin_path and self.ansyslic_admin_path.exists():
            cmd = [str(self.ansyslic_admin_path), "-status"]
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=False)
                parsed = self._parse_lmutil_output(f_norm, proc.stdout + "\n" + proc.stderr)
                if parsed is not None:
                    return parsed
            except Exception as exc:
                logger.warning("ansyslic_admin query failed for feature %s: %s", f_norm, exc)

        # Fallback to configured inventory
        total = self.inventory.get(f_norm, 0)
        active = self.active_allocations.get(f_norm, 0)
        avail = max(0, total - active)
        return FeatureBalance(
            feature_name=f_norm,
            total_tokens=total,
            used_tokens=active,
            available_tokens=avail,
            human_reserved=self.human_buffer,
            in_cooldown=self.is_in_linger(f_norm),
            cooldown_remaining_sec=self.get_linger_remaining(f_norm),
            source="inventory_fallback",
        )

    @staticmethod
    def _parse_lmutil_output(feature: str, output: str) -> Optional[FeatureBalance]:
        """Parse lmutil stdout for license counts."""
        pattern = re.compile(
            rf"Users of {re.escape(feature)}:\s*\(Total of (?P<total>\d+) licenses? issued;\s*Total of (?P<used>\d+) licenses? in use\)",
            re.IGNORECASE,
        )
        match = pattern.search(output)
        if match:
            total = int(match.group("total"))
            used = int(match.group("used"))
            available = max(0, total - used)
            return FeatureBalance(
                feature_name=feature,
                total_tokens=total,
                used_tokens=used,
                available_tokens=available,
                source="flexnet",
                raw_info=output,
            )

        total_match = re.search(r"(\d+)\s+licenses?\s+issued", output, re.IGNORECASE)
        used_match = re.search(r"(\d+)\s+licenses?\s+in\s+use", output, re.IGNORECASE)
        if total_match and used_match:
            total = int(total_match.group(1))
            used = int(used_match.group(1))
            available = max(0, total - used)
            return FeatureBalance(
                feature_name=feature,
                total_tokens=total,
                used_tokens=used,
                available_tokens=available,
                source="flexnet_generic",
                raw_info=output,
            )

        return None

    # -------------------------------------------------------------------------
    # Linger & Cooldown Management
    # -------------------------------------------------------------------------

    def is_in_linger(self, feature: str, current_time: Optional[float] = None) -> bool:
        """Check if a feature is currently in linger cooldown blacklist."""
        f_norm = feature.strip().lower()
        with self._lock:
            rec = self.linger_records.get(f_norm)
            if not rec:
                return False
            if rec.is_active(current_time):
                return True
            del self.linger_records[f_norm]
            return False

    def is_in_cooldown(self, feature: str, current_time: Optional[float] = None) -> bool:
        """Alias for is_in_linger."""
        return self.is_in_linger(feature, current_time=current_time)

    def get_linger_remaining(self, feature: str, current_time: Optional[float] = None) -> float:
        """Get remaining linger cooldown in seconds for a feature."""
        f_norm = feature.strip().lower()
        with self._lock:
            rec = self.linger_records.get(f_norm)
            if not rec:
                return 0.0
            now = time.time() if current_time is None else current_time
            if rec.is_active(now):
                return max(0.0, rec.expire_time - now)
            del self.linger_records[f_norm]
            return 0.0

    def get_cooldown_remaining(self, feature: str, current_time: Optional[float] = None) -> float:
        """Alias for get_linger_remaining."""
        return self.get_linger_remaining(feature, current_time=current_time)

    def clear_linger(self, feature: Optional[str] = None) -> None:
        """Manually reset linger cooldown for a specific feature or all features."""
        with self._lock:
            if feature is not None:
                self.linger_records.pop(feature.strip().lower(), None)
            else:
                self.linger_records.clear()

    def clear_cooldown(self, feature: Optional[str] = None) -> None:
        """Alias for clear_linger."""
        self.clear_linger(feature)

    def mark_abnormal_termination(
        self,
        feature: str,
        duration: Optional[float] = None,
        task_id: str = "abnormal",
        current_time: Optional[float] = None,
    ) -> None:
        """Record abnormal termination and put feature in linger cooldown."""
        f_norm = feature.strip().lower()
        cd = float(duration) if duration is not None else self.linger_duration
        with self._lock:
            now = time.time() if current_time is None else current_time
            expire_at = now + cd
            self.linger_records[f_norm] = LicenseLingerRecord(
                task_id=task_id,
                feature=f_norm,
                expire_time=expire_at,
                reason="abnormal_task_termination",
            )
            logger.warning("Feature %s locked in linger cooldown until %f (%.1fs)", f_norm, expire_at, cd)

    # -------------------------------------------------------------------------
    # Pre-flight Verification & Human Buffer Constraint
    # -------------------------------------------------------------------------

    def _normalize_feature_specs(
        self, features: Union[str, Iterable[str], Dict[str, int]]
    ) -> Dict[str, int]:
        """Normalize feature argument into Dict[feature_name, count]."""
        if isinstance(features, str):
            return {features.strip().lower(): 1}
        elif isinstance(features, dict):
            return {str(k).strip().lower(): max(1, int(v)) for k, v in features.items()}
        elif isinstance(features, (list, tuple, set)):
            norm: Dict[str, int] = {}
            for item in features:
                k = str(item).strip().lower()
                norm[k] = norm.get(k, 0) + 1
            return norm
        raise ValueError(f"Invalid features specification type: {type(features)}")

    def preflight_check(
        self,
        features: Union[str, Iterable[str], Dict[str, int]],
        current_time: Optional[float] = None,
        human_buffer: Optional[int] = None,
    ) -> PreflightCheckResult:
        """Perform pre-dispatch license feasibility check across requested features."""
        feature_specs = self._normalize_feature_specs(features)
        h_buf = self.human_buffer if human_buffer is None else max(0, int(human_buffer))
        now = time.time() if current_time is None else current_time

        balances: Dict[str, FeatureBalance] = {}
        active_counts: Dict[str, int] = {}
        buffer_settings: Dict[str, int] = {}
        cooldowns: Dict[str, float] = {}
        denied_features: List[str] = []
        blocking_reasons: List[str] = []

        with self._lock:
            for feature, req_tokens in feature_specs.items():
                in_ling = self.is_in_linger(feature, current_time=now)
                ling_rem = self.get_linger_remaining(feature, current_time=now)
                cooldowns[feature] = ling_rem

                if in_ling:
                    reason = f"Feature '{feature}' is in anti-storm cooldown (license linger cooldown: {ling_rem:.1f}s remaining)"
                    blocking_reasons.append(reason)
                    denied_features.append(feature)

                if feature in self.optical_features:
                    if not self.probe_sentinel_hasp():
                        reason = f"Sentinel LDK HASP Port 1947 unreachable for optical feature '{feature}'"
                        blocking_reasons.append(reason)
                        denied_features.append(feature)

                bal = self.query_feature_balance(feature)
                balances[feature] = bal

                active = self.active_allocations.get(feature, 0)
                active_counts[feature] = active
                buffer_settings[feature] = h_buf

                avail = bal.available_tokens
                # Formula: Allowed = (Available_Tokens - Active_Agent_Tasks - (req_tokens - 1)) > Human_Buffer
                # Equivalent to: (avail - active) > h_buf when req_tokens = 1
                effective_free = avail - active
                if (effective_free - (req_tokens - 1)) <= h_buf:
                    reason = (
                        f"Human buffer violation: Available tokens ({avail}) for '{feature}' "
                        f"- Active agent tasks ({active}) <= Human_Buffer ({h_buf}). "
                        f"Human engineer priority policy reserves at least {h_buf} token(s)."
                    )
                    blocking_reasons.append(reason)
                    denied_features.append(feature)

        can_proceed = len(blocking_reasons) == 0
        summary_reason = "OK" if can_proceed else "; ".join(blocking_reasons)
        return PreflightCheckResult(
            can_proceed=can_proceed,
            reason=summary_reason,
            balances=balances,
            denied_features=denied_features,
            active_agent_tasks=active_counts,
            human_buffers=buffer_settings,
            cooldown_status=cooldowns,
            blocking_reasons=blocking_reasons,
        )

    def check_availability(
        self,
        features: Union[str, Iterable[str], Dict[str, int]],
        human_buffer: Optional[int] = None,
    ) -> PreflightCheckResult:
        """Alias for preflight_check."""
        return self.preflight_check(features, human_buffer=human_buffer)

    def can_acquire(
        self,
        features: Union[str, Iterable[str], Dict[str, int]],
        current_time: Optional[float] = None,
    ) -> Tuple[bool, str]:
        """Pre-check if requested feature tokens can be safely checked out."""
        result = self.preflight_check(features, current_time=current_time)
        return result.can_proceed, result.reason

    # -------------------------------------------------------------------------
    # Two-Phase Atomic Multi-Feature Checkout
    # -------------------------------------------------------------------------

    def acquire(
        self,
        arg1: Union[str, Iterable[str], Dict[str, int]],
        arg2: Optional[Union[Dict[str, int], str]] = None,
        job_id: Optional[str] = None,
        task_id: Optional[str] = None,
        wait: bool = False,
        timeout: float = 30.0,
        poll_interval: float = 1.0,
        current_time: Optional[float] = None,
        human_buffer: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Union[LicenseLease, bool]:
        """Atomically checkout multi-feature licenses (All-or-Nothing).

        Supports both standard call styles:
        - `scheduler.acquire(features, job_id=...)` -> returns LicenseLease (raises on error)
        - `scheduler.acquire(task_id, features)` -> returns bool for backwards compatibility
        """
        # Determine calling convention
        if isinstance(arg1, str) and isinstance(arg2, dict):
            # Legacy style: acquire(task_id, features)
            resolved_task_id = arg1
            resolved_features = self._normalize_feature_specs(arg2)
            legacy_mode = True
        else:
            resolved_features = self._normalize_feature_specs(arg1)
            resolved_task_id = str(job_id or task_id or f"job_{uuid.uuid4().hex[:8]}")
            legacy_mode = False

        deadline = time.time() + max(0.0, float(timeout))

        while True:
            with self._lock:
                check = self.preflight_check(resolved_features, current_time=current_time, human_buffer=human_buffer)
                if check.can_proceed:
                    # Phase 2: Atomic Commit
                    lease_id = f"lease_{uuid.uuid4().hex[:10]}"
                    for feat, count in resolved_features.items():
                        self.active_allocations[feat] = (
                            self.active_allocations.get(feat, 0) + count
                        )
                    lease = LicenseLease(
                        lease_id=lease_id,
                        task_id=resolved_task_id,
                        features=resolved_features,
                        acquired_at=time.time() if current_time is None else current_time,
                        metadata=dict(metadata or {}),
                    )
                    self.task_allocations[resolved_task_id] = dict(resolved_features)
                    self.leases[resolved_task_id] = lease
                    self.leases[lease_id] = lease
                    logger.info("Checked out features for task %s: %s", resolved_task_id, resolved_features)
                    return lease if not legacy_mode else True

            if not wait:
                if legacy_mode:
                    logger.warning("Checkout denied for task %s: %s", resolved_task_id, check.reason)
                    return False
                if check.is_in_cooldown:
                    raise FeatureInCooldownError(f"Atomic checkout failed: {check.reason}", details=check)
                raise LicenseUnavailableError(f"Atomic checkout failed: {check.reason}", details=check)

            now = time.time()
            if now >= deadline:
                raise LicenseAcquisitionTimeoutError(
                    f"Timed out after {timeout:.1f}s waiting for licenses: {check.reason}"
                )

            sleep_time = min(poll_interval, max(0.1, deadline - now))
            time.sleep(sleep_time)

    def release(
        self,
        task_or_lease: Union[LicenseLease, str],
        normal_exit: bool = True,
        abnormal: bool = False,
        current_time: Optional[float] = None,
    ) -> None:
        """Release checked out tokens. On abnormal exit, trigger 300s linger cooldown."""
        is_normal = normal_exit and (not abnormal)

        with self._lock:
            task_key = task_or_lease.task_id if isinstance(task_or_lease, LicenseLease) else str(task_or_lease)
            lease = self.leases.pop(task_key, None)
            if lease is not None:
                self.leases.pop(lease.lease_id, None)

            allocated = self.task_allocations.pop(task_key, None)
            if allocated is None and lease is not None:
                allocated = lease.features

            if not allocated:
                return

            now = time.time() if current_time is None else current_time

            for feature, count in allocated.items():
                current_active = self.active_allocations.get(feature, 0)
                self.active_allocations[feature] = max(0, current_active - count)

                if not is_normal:
                    self.mark_abnormal_termination(feature, duration=self.linger_duration, task_id=task_key, current_time=now)

    @contextmanager
    def lease_context(
        self,
        features: Union[str, Iterable[str], Dict[str, int]],
        job_id: Optional[str] = None,
        wait: bool = False,
        timeout: float = 30.0,
        poll_interval: float = 1.0,
        human_buffer: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Generator[LicenseLease, None, None]:
        """Context manager for safe, atomic license checkout and automatic release."""
        lease = self.acquire(
            arg1=features,
            job_id=job_id,
            wait=wait,
            timeout=timeout,
            poll_interval=poll_interval,
            human_buffer=human_buffer,
            metadata=metadata,
        )
        if not isinstance(lease, LicenseLease):
            raise LicenseUnavailableError("Failed to acquire lease in context manager")
        try:
            yield lease
        except Exception:
            self.release(lease, abnormal=True)
            raise
        else:
            self.release(lease, abnormal=False)

    # -------------------------------------------------------------------------
    # Introspection
    # -------------------------------------------------------------------------

    def get_available_tokens(self, feature: str) -> int:
        """Get total available unallocated tokens for a feature."""
        total = self.inventory.get(feature.strip().lower(), 0)
        active = self.active_allocations.get(feature.strip().lower(), 0)
        return max(0, total - active)

    def get_active_agent_tasks(self, feature: Optional[str] = None) -> Union[int, Dict[str, int]]:
        """Get current count of active agent tasks holding licenses."""
        with self._lock:
            if feature:
                return self.active_allocations.get(feature.strip().lower(), 0)
            return dict(self.active_allocations)

    def get_active_leases(self) -> List[LicenseLease]:
        """Return a snapshot of all currently active unique leases."""
        with self._lock:
            unique = {l.lease_id: l for l in self.leases.values()}
            return list(unique.values())


# Aliases for backwards and forward compatibility
TokenBucketScheduler = TokenBucketLicenseScheduler
