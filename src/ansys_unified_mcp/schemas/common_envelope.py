# -*- coding: utf-8 -*-
"""Unified response envelope and pagination schemas.

Adheres to ASD-STE100 and Model Context Protocol (MCP) structured envelope standards.
All comments and docstrings in this module strictly use ASCII English.
"""

from __future__ import annotations

import time
from typing import Any, Generic, List, Optional, Sequence, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


def create_response_envelope(
    data: Any,
    summary: str,
    file_path: Optional[str] = None,
    sha256: Optional[str] = None,
    execution_time_ms: float = 0.0,
    **extra: Any,
) -> dict[str, Any]:
    """Create a standardized success response envelope for MCP tools.

    Parameters:
        data: The primary output data payload or structured dictionary.
        summary: Clear human-readable summary of the operation result.
        file_path: Optional path to an associated artifact or generated file.
        sha256: Optional SHA-256 checksum of generated file or payload.
        execution_time_ms: Total execution duration in milliseconds.
        extra: Additional custom metadata fields.

    Returns:
        Standard envelope dictionary with ok=True and status='success'.
    """
    envelope: dict[str, Any] = {
        "ok": True,
        "status": "success",
        "summary": summary,
        "data": data,
        "execution_time_ms": float(execution_time_ms),
    }

    if file_path is not None:
        envelope["file_path"] = str(file_path)

    if sha256 is not None:
        envelope["sha256"] = str(sha256)

    if extra:
        envelope.update(extra)

    return envelope


class PaginationParams(BaseModel):
    """Standard query parameters for paginated tool requests."""

    model_config = ConfigDict(extra="forbid")

    limit: int = Field(
        default=20,
        ge=1,
        le=1000,
        description="Maximum number of items to return in a single page.",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Zero-based index offset for pagination start.",
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard generic model for paginated collection responses."""

    model_config = ConfigDict(extra="forbid")

    items: List[T] = Field(
        default_factory=list,
        description="List of items for the requested page.",
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of items available across all pages.",
    )
    limit: int = Field(
        ...,
        ge=1,
        description="Page size limit applied to the query.",
    )
    offset: int = Field(
        ...,
        ge=0,
        description="Zero-based offset applied to the query.",
    )
    has_more: bool = Field(
        ...,
        description="Indicates whether more items exist beyond the current page.",
    )


def paginate_list(
    items: Sequence[T],
    limit: int = 20,
    offset: int = 0,
) -> PaginatedResponse[T]:
    """Slice an in-memory sequence into a PaginatedResponse.

    Parameters:
        items: Full sequence of items to paginate.
        limit: Maximum number of items per page.
        offset: Zero-based starting index.

    Returns:
        PaginatedResponse instance containing sliced items and pagination metadata.
    """
    total = len(items)
    clamped_offset = max(0, min(offset, total))
    clamped_limit = max(1, limit)
    page_items = list(items[clamped_offset : clamped_offset + clamped_limit])
    has_more = (clamped_offset + clamped_limit) < total

    return PaginatedResponse[T](
        items=page_items,
        total=total,
        limit=clamped_limit,
        offset=clamped_offset,
        has_more=has_more,
    )


def create_error_envelope(
    status: str = "error",
    error_code: str = "UNKNOWN_ERROR",
    message: str = "",
    recovery_action: Optional[str] = None,
    **extra: Any,
) -> dict[str, Any]:
    """Create an ASD-STE100 compliant structured error envelope.

    Adheres to Simplified Technical English principles:
    - Provides unambiguous error identification.
    - Specifies explicit, imperative recovery action instructions.
    - Maintains 100% backward compatibility with ok=False and error=message.

    Parameters:
        status: Status identifier (default 'error').
        error_code: Machine-readable uppercase category identifier.
        message: Direct descriptive error explanation.
        recovery_action: Clear, imperative recovery instructions for the caller.
        extra: Additional contextual debug metadata.

    Returns:
        Structured error envelope dictionary.
    """
    envelope: dict[str, Any] = {
        "ok": False,
        "status": status,
        "error_code": error_code,
        "message": message,
        "error": message,  # Backward compatibility with legacy callers
    }

    if recovery_action is not None:
        envelope["recovery_action"] = recovery_action
        envelope["suggested_actions"] = [recovery_action]

    if extra:
        envelope.update(extra)

    return envelope
