# -*- coding: utf-8 -*-
"""Tool annotations helper and flat Pydantic schema validation decorator.

Provides:
- ToolAnnotations: 4-key MCP behavioral hints builder.
- validate_flat_pydantic: Decorator maintaining flat parameter signatures for FastMCP
  while strictly validating inputs against Pydantic models with extra='forbid'.

All comments and docstrings in this module strictly use ASCII English.
"""

from __future__ import annotations

import functools
import inspect
from typing import Any, Callable, Dict, Optional, Type, TypeVar
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ansys_unified_mcp.schemas.common_envelope import create_error_envelope

F = TypeVar("F", bound=Callable[..., Any])
M = TypeVar("M", bound=BaseModel)


class ToolAnnotations(BaseModel):
    """MCP 4-Key Tool Annotations representing standard behavioral hints."""

    model_config = ConfigDict(extra="forbid")

    readOnlyHint: bool = Field(
        default=False,
        description="Indicates whether the tool does not modify system state or environment.",
    )
    destructiveHint: bool = Field(
        default=False,
        description="Indicates whether the tool performs irreversible actions or deletes data.",
    )
    idempotentHint: bool = Field(
        default=False,
        description="Indicates whether repeated executions with the same arguments produce identical results.",
    )
    openWorldHint: bool = Field(
        default=False,
        description="Indicates whether the tool interacts with external open-world systems or networks.",
    )

    @classmethod
    def create(
        cls,
        read_only: bool = False,
        destructive: bool = False,
        idempotent: bool = False,
        open_world: bool = False,
    ) -> "ToolAnnotations":
        """Factory method to construct 4-key ToolAnnotations."""
        return cls(
            readOnlyHint=read_only,
            destructiveHint=destructive,
            idempotentHint=idempotent,
            openWorldHint=open_world,
        )

    @classmethod
    def read_only(cls) -> "ToolAnnotations":
        """Construct annotations for safe query and inspection tools."""
        return cls(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )

    @classmethod
    def mutation(cls, destructive: bool = False, idempotent: bool = False) -> "ToolAnnotations":
        """Construct annotations for internal state mutation tools."""
        return cls(
            readOnlyHint=False,
            destructiveHint=destructive,
            idempotentHint=idempotent,
            openWorldHint=False,
        )

    @classmethod
    def external(cls, destructive: bool = False, idempotent: bool = False) -> "ToolAnnotations":
        """Construct annotations for external simulator or solver invocation tools."""
        return cls(
            readOnlyHint=False,
            destructiveHint=destructive,
            idempotentHint=idempotent,
            openWorldHint=True,
        )

    def to_dict(self) -> dict[str, bool]:
        """Export annotations as a dictionary for FastMCP tool registration."""
        return self.model_dump()


def create_tool_annotations(
    read_only: bool = False,
    destructive: bool = False,
    idempotent: bool = False,
    open_world: bool = False,
) -> dict[str, bool]:
    """Helper function to create a 4-key annotations dictionary."""
    return ToolAnnotations.create(
        read_only=read_only,
        destructive=destructive,
        idempotent=idempotent,
        open_world=open_world,
    ).to_dict()


def _ensure_extra_forbid(schema_cls: Type[BaseModel]) -> Type[BaseModel]:
    """Ensure that the schema class enforces extra='forbid'."""
    extra_setting = getattr(schema_cls, "model_config", {}).get("extra", None)
    if extra_setting == "forbid":
        return schema_cls

    # Create a dynamic subclass with extra='forbid'
    cloned_config = dict(schema_cls.model_config)
    cloned_config["extra"] = "forbid"
    return type(
        schema_cls.__name__,
        (schema_cls,),
        {"model_config": ConfigDict(**cloned_config)},
    )


def validate_flat_pydantic(schema_cls: Type[BaseModel]) -> Callable[[F], F]:
    """Decorator to enforce strict Pydantic validation on flat MCP tool parameters.

    Features:
    - Maintains flat parameter signatures on the outer function so FastMCP
      and MCP clients recognize standard JSON parameters without nesting.
    - Inside the wrapper, combines positional arguments and keyword arguments,
      validating them strictly against schema_cls with extra='forbid'.
    - If validation fails, catches ValidationError and returns an ASD-STE100
      compliant error envelope detailing all parameter errors.
    - If validation succeeds, feeds validated, type-coerced values and defaults
      to the underlying function.
    - Transparently supports both synchronous and asynchronous functions.

    Parameters:
        schema_cls: Pydantic model class defining parameter types and constraints.
    """
    strict_schema = _ensure_extra_forbid(schema_cls)

    def decorator(fn: F) -> F:
        sig = inspect.signature(fn)
        param_names = list(sig.parameters.keys())
        has_var_kwargs = any(
            p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
        )

        def _prepare_call_kwargs(args: tuple[Any, ...], kwargs: dict[str, Any]) -> tuple[Optional[dict[str, Any]], Optional[dict[str, Any]]]:
            # Map positional arguments to parameter names
            combined: dict[str, Any] = {}
            for i, val in enumerate(args):
                if i < len(param_names):
                    combined[param_names[i]] = val
            combined.update(kwargs)

            try:
                validated_model = strict_schema(**combined)
            except ValidationError as exc:
                error_lines = []
                for err in exc.errors():
                    field_loc = ".".join(str(elem) for elem in err.get("loc", []))
                    err_msg = err.get("msg", "Invalid value")
                    error_lines.append(f"Field '{field_loc}': {err_msg}")
                detail = "; ".join(error_lines)
                err_env = create_error_envelope(
                    status="error",
                    error_code="VALIDATION_ERROR",
                    message=f"Parameter validation failed for {fn.__name__}: {detail}",
                    recovery_action=f"Ensure inputs match the schema of {strict_schema.__name__} without extra fields.",
                )
                return None, err_env

            dumped = validated_model.model_dump()
            if has_var_kwargs:
                return dumped, None
            # Filter dumped fields to only include declared function parameters
            filtered = {k: v for k, v in dumped.items() if k in param_names}
            return filtered, None

        if inspect.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                call_kwargs, err_env = _prepare_call_kwargs(args, kwargs)
                if err_env is not None:
                    return err_env
                return await fn(**call_kwargs)  # type: ignore

            async_wrapper.__pydantic_schema__ = strict_schema  # type: ignore
            return async_wrapper  # type: ignore
        else:
            @functools.wraps(fn)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                call_kwargs, err_env = _prepare_call_kwargs(args, kwargs)
                if err_env is not None:
                    return err_env
                return fn(**call_kwargs)

            sync_wrapper.__pydantic_schema__ = strict_schema  # type: ignore
            return sync_wrapper  # type: ignore

    return decorator
