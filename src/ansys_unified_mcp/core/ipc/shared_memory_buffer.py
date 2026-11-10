# Strictly ASCII English Comments
"""Zero-copy SharedMemory buffer for high-throughput cross-process array transport.

Provides sub-millisecond zero-copy serialization/deserialization of large NumPy
arrays (field variables, nodal displacements, mesh point clouds, S-parameter matrices)
across sub-virtual environment boundaries.
"""

from __future__ import annotations

import hashlib
import logging
from multiprocessing import shared_memory
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple, Union
import uuid

import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Process-local cache of open shared memory handles to prevent GC closing on Windows
_OPEN_SEGMENTS: Dict[str, shared_memory.SharedMemory] = {}


class SharedMemoryBufferError(Exception):
    """Base exception for shared memory buffer operations."""


class SharedMemoryMetadata(BaseModel):
    """Metadata descriptor for an array stored in shared memory."""

    name: str = Field(description="Unique identifier of the shared memory segment")
    shape: List[int] = Field(description="Shape of the stored array")
    dtype: str = Field(description="NumPy dtype string, e.g. float64, float32")
    size_bytes: int = Field(description="Total byte length of array data")
    sha256: str = Field(default="", description="SHA-256 hash of buffer for integrity check")
    offset: int = Field(default=0, description="Byte offset where payload begins")
    order: str = Field(default="C", description="Memory layout order: 'C' or 'F'")


def _compute_sha256(buf: memoryview) -> str:
    """Compute SHA-256 hash string from a memoryview without full-copy."""
    hasher = hashlib.sha256()
    hasher.update(buf)
    return hasher.hexdigest()


class SharedMemoryBuffer:
    """Manager for zero-copy numpy array shared memory segments."""

    @staticmethod
    def write_array(
        arr: np.ndarray,
        name: Optional[str] = None,
        compute_sha256: bool = True,
    ) -> Tuple[shared_memory.SharedMemory, SharedMemoryMetadata]:
        """Write a NumPy array to a new shared memory segment.

        Returns both the opened SharedMemory object and its metadata.
        """
        if not isinstance(arr, np.ndarray):
            arr = np.asarray(arr)

        if not arr.flags.c_contiguous:
            arr = np.ascontiguousarray(arr)

        size_bytes = int(arr.nbytes)
        alloc_bytes = max(1, size_bytes)

        if name is None or not name.strip():
            name = f"ansys_shm_{uuid.uuid4().hex[:12]}"

        # If a segment with the same name is already tracked locally, clean it first
        if name in _OPEN_SEGMENTS:
            SharedMemoryBuffer.cleanup_shm(name)

        try:
            shm = shared_memory.SharedMemory(create=True, size=alloc_bytes, name=name)
        except FileExistsError:
            # Segment exists in OS from a crashed previous process, attempt cleanup & retry
            try:
                old_shm = shared_memory.SharedMemory(name=name, create=False)
                old_shm.close()
                old_shm.unlink()
            except Exception:
                pass
            shm = shared_memory.SharedMemory(create=True, size=alloc_bytes, name=name)

        _OPEN_SEGMENTS[name] = shm

        # Copy array bytes into shared buffer
        if size_bytes > 0:
            shm.buf[:size_bytes] = memoryview(arr).cast("B")

        digest = ""
        if compute_sha256 and size_bytes > 0:
            digest = _compute_sha256(shm.buf[:size_bytes])

        metadata = SharedMemoryMetadata(
            name=name,
            shape=list(arr.shape),
            dtype=str(arr.dtype),
            size_bytes=size_bytes,
            sha256=digest,
            offset=0,
            order="C",
        )
        return shm, metadata

    @staticmethod
    def read_array(
        metadata: Union[SharedMemoryMetadata, Dict[str, Any]],
        copy: bool = False,
        verify_sha256: bool = True,
    ) -> Tuple[shared_memory.SharedMemory, np.ndarray]:
        """Read a NumPy array from an existing shared memory segment.

        If copy is False, returns a true zero-copy ndarray pointing directly into shm.buf.
        """
        if isinstance(metadata, dict):
            name = str(metadata.get("shm_name") or metadata.get("name"))
            shape = tuple(metadata["shape"])
            dtype = np.dtype(metadata["dtype"])
            size_bytes = int(metadata.get("nbytes", metadata.get("size_bytes", 0)))
            sha256_hash = str(metadata.get("sha256", ""))
            offset = int(metadata.get("offset", 0))
            order = str(metadata.get("order", "C"))
        else:
            name = metadata.name
            shape = tuple(metadata.shape)
            dtype = np.dtype(metadata.dtype)
            size_bytes = metadata.size_bytes
            sha256_hash = metadata.sha256
            offset = metadata.offset
            order = metadata.order

        if name in _OPEN_SEGMENTS:
            shm = _OPEN_SEGMENTS[name]
        else:
            try:
                shm = shared_memory.SharedMemory(name=name, create=False)
                _OPEN_SEGMENTS[name] = shm
            except FileNotFoundError as err:
                raise SharedMemoryBufferError(f"Shared memory segment '{name}' not found: {err}") from err

        if size_bytes == 0 or np.prod(shape) == 0:
            empty_arr = np.empty(shape, dtype=dtype)
            return shm, empty_arr

        target_slice = shm.buf[offset : offset + size_bytes]

        if verify_sha256 and sha256_hash:
            actual_hash = _compute_sha256(target_slice)
            if actual_hash != sha256_hash:
                raise ValueError(
                    f"SHA-256 integrity check failed for shm segment '{name}': "
                    f"expected {sha256_hash}, got {actual_hash}"
                )

        array_view = np.ndarray(
            shape=shape,
            dtype=dtype,
            buffer=target_slice,
            order=order,
        )

        if copy:
            copied = array_view.copy()
            return shm, copied

        # Zero-copy view: keep shm handle referenced on the array object
        try:
            array_view._shm = shm  # type: ignore[attr-defined]
        except AttributeError:
            pass

        return shm, array_view

    @staticmethod
    def cleanup_shm(shm_or_name: Union[str, shared_memory.SharedMemory]) -> None:
        """Close and unlink a shared memory segment safely."""
        name = shm_or_name if isinstance(shm_or_name, str) else shm_or_name.name
        shm = _OPEN_SEGMENTS.pop(name, None)

        if shm is None:
            try:
                shm = shared_memory.SharedMemory(name=name, create=False)
            except Exception:
                shm = None

        if shm is not None:
            try:
                shm.close()
            except Exception as e:
                logger.debug("Error closing shm %s: %s", name, e)
            try:
                shm.unlink()
            except (FileNotFoundError, OSError):
                pass

    @staticmethod
    def cleanup_all() -> None:
        """Close and unlink all tracked shared memory segments."""
        names = list(_OPEN_SEGMENTS.keys())
        for name in names:
            SharedMemoryBuffer.cleanup_shm(name)


def write_numpy_to_shm(
    name: Optional[Union[str, np.ndarray]] = None,
    arr: Optional[np.ndarray] = None,
    compute_sha256: bool = True,
) -> Dict[str, Any]:
    """Write a NumPy array to shared memory and return a metadata dictionary.

    Supports both write_numpy_to_shm('name', arr) and write_numpy_to_shm(arr).
    """
    if arr is None and isinstance(name, np.ndarray):
        arr = name
        actual_name = None
    elif isinstance(name, str):
        actual_name = name
    else:
        actual_name = None

    if arr is None:
        raise ValueError("Array must be provided to write_numpy_to_shm")

    shm, meta = SharedMemoryBuffer.write_array(
        arr=arr,
        name=actual_name,
        compute_sha256=compute_sha256,
    )
    return {
        "shm_name": meta.name,
        "name": meta.name,
        "shape": meta.shape,
        "dtype": meta.dtype,
        "nbytes": meta.size_bytes,
        "size_bytes": meta.size_bytes,
        "sha256": meta.sha256,
        "offset": meta.offset,
        "order": meta.order,
        "timestamp": time.time(),
    }


def read_numpy_from_shm(
    meta: Union[Dict[str, Any], SharedMemoryMetadata],
    verify_hash: bool = True,
    copy: bool = False,
) -> np.ndarray:
    """Read a NumPy array from shared memory given a metadata dictionary or object.

    Defaults to zero-copy view unless copy=True is specified.
    """
    _, arr = SharedMemoryBuffer.read_array(
        metadata=meta,
        copy=copy,
        verify_sha256=verify_hash,
    )
    return arr


def cleanup_shm(name_or_shm: Union[str, shared_memory.SharedMemory]) -> None:
    """Close and release shared memory by segment name or SharedMemory instance."""
    SharedMemoryBuffer.cleanup_shm(name_or_shm)


def cleanup_all_shm() -> None:
    """Close and release all currently opened shared memory segments."""
    SharedMemoryBuffer.cleanup_all()


def write_shared_array(
    arr: np.ndarray,
    name: Optional[str] = None,
    compute_sha256: bool = True,
) -> Tuple[shared_memory.SharedMemory, SharedMemoryMetadata]:
    """Backward-compatible helper returning (shm, metadata)."""
    return SharedMemoryBuffer.write_array(arr, name=name, compute_sha256=compute_sha256)


def read_shared_array(
    metadata: SharedMemoryMetadata,
    copy: bool = False,
    verify_sha256: bool = False,
) -> Tuple[shared_memory.SharedMemory, np.ndarray]:
    """Backward-compatible helper returning (shm, array)."""
    return SharedMemoryBuffer.read_array(metadata, copy=copy, verify_sha256=verify_sha256)
