#!/usr/bin/env python3
"""Product-controlled operation registry for the GT-KB dashboard control plane.

Phase 5 first slice (GTKB-ISOLATION-005): three operations only —
``dashboard.read``, ``dashboard.refresh``, and ``control_plane.status``.
The registry is the sole handler-lookup path. Unknown operation IDs fail
closed. Caller input may not override project root, dashboard DB path, or
handler target path; those originate in :class:`OperationContext`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

FORBIDDEN_OVERRIDES: frozenset[str] = frozenset(
    {"project_root", "dashboard_db", "target_path", "script", "command"}
)


@dataclass(frozen=True)
class OperationDescriptor:
    operation_id: str
    display_name: str
    allowed_subjects: tuple[str, ...]
    required_role_slots: tuple[str, ...]
    target_root_policy: str
    effective_timing: str
    supports_dry_run: bool


@dataclass(frozen=True)
class OperationContext:
    """Service-provided context. Paths originate here, never from caller input."""

    project_root: Path
    dashboard_db: Path
    subject: str
    apply_operation: Callable[[str], Mapping[str, Any]]
    read_state: Callable[[], Mapping[str, Any]]


class RegistryError(Exception):
    """Base class for control-plane registry errors."""


class UnknownOperationError(RegistryError):
    """Raised when a caller supplies an operation_id the registry does not know."""


class InvalidRequestError(RegistryError):
    """Raised when the request body violates a registry guard rule."""


def _typed_envelope(
    descriptor: OperationDescriptor,
    context: OperationContext,
    *,
    status: str,
    dry_run: bool,
    details: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "operation_id": descriptor.operation_id,
        "status": status,
        "effective_timing": descriptor.effective_timing,
        "subject": context.subject,
        "project_root": str(context.project_root),
        "dashboard_db": str(context.dashboard_db),
        "dry_run": dry_run,
        "details": dict(details),
    }


def _dashboard_read_handler(
    descriptor: OperationDescriptor,
    request: Mapping[str, Any],
    context: OperationContext,
) -> dict[str, Any]:
    snapshot = dict(context.read_state())
    return _typed_envelope(
        descriptor,
        context,
        status="ok",
        dry_run=False,
        details={
            "last_result": snapshot.get("last_result"),
            "last_error": snapshot.get("last_error", ""),
            "refreshing": snapshot.get("refreshing", False),
            "token_configured": snapshot.get("token_configured", False),
            "interval_seconds": snapshot.get("interval_seconds"),
        },
    )


def _dashboard_refresh_handler(
    descriptor: OperationDescriptor,
    request: Mapping[str, Any],
    context: OperationContext,
) -> dict[str, Any]:
    dry_run = bool(request.get("dry_run", False))
    if dry_run:
        snapshot = dict(context.read_state())
        return _typed_envelope(
            descriptor,
            context,
            status="dry_run",
            dry_run=True,
            details={
                "would_refresh": True,
                "token_configured": bool(snapshot.get("token_configured", False)),
                "target_root_policy": descriptor.target_root_policy,
            },
        )
    result = dict(context.apply_operation(descriptor.operation_id))
    return _typed_envelope(
        descriptor,
        context,
        status=str(result.get("status", "unknown")),
        dry_run=False,
        details=result,
    )


def _control_plane_status_handler(
    descriptor: OperationDescriptor,
    request: Mapping[str, Any],
    context: OperationContext,
) -> dict[str, Any]:
    operations = [
        {
            "operation_id": d.operation_id,
            "display_name": d.display_name,
            "allowed_subjects": list(d.allowed_subjects),
            "required_role_slots": list(d.required_role_slots),
            "target_root_policy": d.target_root_policy,
            "effective_timing": d.effective_timing,
            "supports_dry_run": d.supports_dry_run,
        }
        for d in OPERATION_DESCRIPTORS.values()
    ]
    return _typed_envelope(
        descriptor,
        context,
        status="ok",
        dry_run=False,
        details={"operations": operations},
    )


OPERATION_DESCRIPTORS: Mapping[str, OperationDescriptor] = {
    "dashboard.read": OperationDescriptor(
        operation_id="dashboard.read",
        display_name="Read dashboard state",
        allowed_subjects=("dashboard",),
        required_role_slots=(),
        target_root_policy="app_local",
        effective_timing="immediate",
        supports_dry_run=False,
    ),
    "dashboard.refresh": OperationDescriptor(
        operation_id="dashboard.refresh",
        display_name="Refresh dashboard runtime DB",
        allowed_subjects=("dashboard",),
        required_role_slots=("dashboard-refresh-token",),
        target_root_policy="app_local",
        effective_timing="immediate",
        supports_dry_run=True,
    ),
    "control_plane.status": OperationDescriptor(
        operation_id="control_plane.status",
        display_name="Report control-plane registry status",
        allowed_subjects=("control_plane",),
        required_role_slots=(),
        target_root_policy="none",
        effective_timing="immediate",
        supports_dry_run=False,
    ),
}

_HANDLERS: Mapping[
    str,
    Callable[[OperationDescriptor, Mapping[str, Any], OperationContext], dict[str, Any]],
] = {
    "dashboard.read": _dashboard_read_handler,
    "dashboard.refresh": _dashboard_refresh_handler,
    "control_plane.status": _control_plane_status_handler,
}


def list_operation_ids() -> list[str]:
    """Return the operation IDs the registry knows about, in insertion order."""
    return list(OPERATION_DESCRIPTORS.keys())


def get_descriptor(operation_id: str) -> OperationDescriptor:
    try:
        return OPERATION_DESCRIPTORS[operation_id]
    except KeyError as exc:
        raise UnknownOperationError(f"unknown operation_id: {operation_id!r}") from exc


def dispatch(request: Mapping[str, Any], context: OperationContext) -> dict[str, Any]:
    """Dispatch a control-plane request through the registry.

    Raises :class:`UnknownOperationError` for unknown ``operation_id`` values
    and :class:`InvalidRequestError` for requests that violate guard rules
    (missing ID, forbidden path override, non-boolean ``dry_run``, or
    ``dry_run`` requested on an operation that does not support it).
    """
    operation_id = request.get("operation_id")
    if not isinstance(operation_id, str) or not operation_id:
        raise InvalidRequestError("operation_id is required")

    supplied_overrides = set(request.keys()) & FORBIDDEN_OVERRIDES
    if supplied_overrides:
        raise InvalidRequestError(
            f"request may not override service-owned fields: {sorted(supplied_overrides)}"
        )

    descriptor = get_descriptor(operation_id)

    dry_run = request.get("dry_run", False)
    if not isinstance(dry_run, bool):
        raise InvalidRequestError("dry_run must be a boolean")
    if dry_run and not descriptor.supports_dry_run:
        raise InvalidRequestError(
            f"operation_id {operation_id!r} does not support dry_run"
        )

    return _HANDLERS[operation_id](descriptor, request, context)
