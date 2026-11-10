"""DAMG causal precondition enforcement and invalidation decorators.

Enforces zero-latency gatekeeper interception on physics MCP tools when
upstream graph requirements are unsatisfied or marked dirty.
All code comments follow ASD-STE100 and ASCII safety standards.
"""

from __future__ import annotations

import functools
import inspect
import logging
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

from ansys_unified_mcp.core.damg.damg_state_machine import DAMGStateMachine

logger = logging.getLogger(__name__)

DAMG_ERROR_CODE_PRECONDITION_VIOLATION = "DAMG_PRECONDITION_VIOLATION"


def _extract_session_id(
    args: tuple,
    kwargs: Dict[str, Any],
    func: Callable,
    session_param: str,
    fallback_session_id: str,
) -> str:
    """Extract session identifier from function keyword or positional arguments."""
    # 1. Direct kwargs check
    if session_param in kwargs and kwargs[session_param]:
        return str(kwargs[session_param])

    for alias in ("session_id", "session", "project_id", "workspace_id"):
        if alias in kwargs and kwargs[alias]:
            return str(kwargs[alias])

    # 2. Inspect signature to find positional argument matching session parameter
    try:
        sig = inspect.signature(func)
        bound = sig.bind_partial(*args, **kwargs)
        for name, val in bound.arguments.items():
            if name in (session_param, "session_id", "session", "project_id"):
                if val:
                    return str(val)
    except Exception:
        pass

    return fallback_session_id


def build_precondition_violation_envelope(
    target_node: str,
    missing_prerequisites: List[str],
    state_machine: DAMGStateMachine,
) -> Dict[str, Any]:
    """Construct ASD-STE100 compliant structured error response envelope."""
    details = state_machine.get_missing_prerequisites_details(
        missing_prerequisites
    )
    suggested_actions: List[str] = []

    for item in details:
        recovery = item.get("suggested_recovery")
        if recovery:
            suggested_actions.append(recovery)
        else:
            suggested_actions.append(
                f"Execute upstream tools to satisfy requirement '{item['node']}'."
            )

    msg = (
        f"DAMG precondition check failed for target node '{target_node}'. "
        f"Missing or dirty prerequisite nodes: {', '.join(missing_prerequisites)}."
    )

    return {
        "ok": False,
        "error_code": DAMG_ERROR_CODE_PRECONDITION_VIOLATION,
        "error": msg,
        "target_node": target_node,
        "missing_prerequisites": missing_prerequisites,
        "details": details,
        "suggested_actions": suggested_actions,
        "remediation": (
            "Execute the required upstream physics operations to satisfy dependencies "
            "before executing this step."
        ),
    }


def enforce_damg_precondition(
    required_nodes: Sequence[str],
    target_node: str,
    session_id: Optional[str] = None,
    session_param: str = "session_id",
    state_machine: Optional[DAMGStateMachine] = None,
) -> Callable:
    """Decorator to enforce DAMG causal prerequisites before tool execution.

    If any prerequisite in required_nodes is UNSATISFIED or DIRTY:
    - Intercepts call with 0-second latency.
    - Prevents target tool execution.
    - Returns structured ASD-STE100 error envelope with remediation advice.

    If all prerequisites are satisfied:
    - Executes the decorated function.
    - If execution succeeds (and envelope ok is not False), automatically marks
      target_node as SATISFIED.
    """
    req_list = [str(r).strip().upper() for r in required_nodes]
    tgt_node = str(target_node).strip().upper()

    def decorator(func: Callable) -> Callable:
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                sm = state_machine
                if sm is None:
                    sid = _extract_session_id(
                        args, kwargs, func, session_param, session_id or "default"
                    )
                    sm = DAMGStateMachine.get_instance(sid)

                missing = sm.check_prerequisites(req_list)
                if missing:
                    logger.warning(
                        "DAMG precondition blocked call to '%s'. Target '%s' missing: %s",
                        func.__name__,
                        tgt_node,
                        missing,
                    )
                    return build_precondition_violation_envelope(
                        tgt_node, missing, sm
                    )

                result = await func(*args, **kwargs)

                # Do not mark satisfied if result indicates explicit failure
                if isinstance(result, dict) and result.get("ok") is False:
                    return result

                sm.mark_node_satisfied(
                    tgt_node,
                    metadata={"invoked_tool": func.__name__, "mode": "async"},
                )
                return result

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                sm = state_machine
                if sm is None:
                    sid = _extract_session_id(
                        args, kwargs, func, session_param, session_id or "default"
                    )
                    sm = DAMGStateMachine.get_instance(sid)

                missing = sm.check_prerequisites(req_list)
                if missing:
                    logger.warning(
                        "DAMG precondition blocked call to '%s'. Target '%s' missing: %s",
                        func.__name__,
                        tgt_node,
                        missing,
                    )
                    return build_precondition_violation_envelope(
                        tgt_node, missing, sm
                    )

                result = func(*args, **kwargs)

                # Do not mark satisfied if result indicates explicit failure
                if isinstance(result, dict) and result.get("ok") is False:
                    return result

                sm.mark_node_satisfied(
                    tgt_node,
                    metadata={"invoked_tool": func.__name__, "mode": "sync"},
                )
                return result

            return sync_wrapper

    return decorator


def invalidate_damg_on_change(
    dirty_nodes: Sequence[str],
    session_id: Optional[str] = None,
    session_param: str = "session_id",
    state_machine: Optional[DAMGStateMachine] = None,
) -> Callable:
    """Decorator to trigger downstream dirty invalidation upon tool modification.

    When an upstream modification tool succeeds, cascades DIRTY status along
    DAG downstream edges for each node in dirty_nodes.
    """
    nodes_to_dirty = [str(n).strip().upper() for n in dirty_nodes]

    def decorator(func: Callable) -> Callable:
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                result = await func(*args, **kwargs)
                if isinstance(result, dict) and result.get("ok") is False:
                    return result

                sm = state_machine
                if sm is None:
                    sid = _extract_session_id(
                        args, kwargs, func, session_param, session_id or "default"
                    )
                    sm = DAMGStateMachine.get_instance(sid)

                for node in nodes_to_dirty:
                    sm.invalidate_node_and_downstream(node)

                return result

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                result = func(*args, **kwargs)
                if isinstance(result, dict) and result.get("ok") is False:
                    return result

                sm = state_machine
                if sm is None:
                    sid = _extract_session_id(
                        args, kwargs, func, session_param, session_id or "default"
                    )
                    sm = DAMGStateMachine.get_instance(sid)

                for node in nodes_to_dirty:
                    sm.invalidate_node_and_downstream(node)

                return result

            return sync_wrapper

    return decorator
