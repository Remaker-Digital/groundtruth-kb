"""Exact-init ``changed_by`` resolution for canonical backlog writers.

Role is an immutable property of the invoking session context. Harness identity
is attribution only and never supplies role authority.
"""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_VAR_HARNESS_NAME = "GTKB_HARNESS_NAME"


def _expected_harness_name(harness_name: str | None) -> str | None:
    """Return a document selector only; it is never role authority."""
    if harness_name:
        return harness_name.strip() or None
    configured = os.environ.get(ENV_VAR_HARNESS_NAME, "").strip()
    if configured:
        return configured
    if os.environ.get("CLAUDECODE") or os.environ.get("CLAUDE_CODE_SESSION_ID"):
        return "claude"
    if os.environ.get("CODEX_HOME") or os.environ.get("CODEX_THREAD_ID"):
        return "codex"
    return None


def _current_session_id() -> str:
    from scripts.gtkb_session_id import BRIDGE_WORK_INTENT_ORDER, resolve_session_id

    session_id = resolve_session_id(order=BRIDGE_WORK_INTENT_ORDER)
    if not session_id:
        raise RuntimeError("resolve_changed_by: current session id is missing; exact-init role authority is required.")
    return session_id


def _resolve_harness_attribution(project_root: Path, harness_name: str | None) -> str:
    """Resolve and cross-check the acting harness without reading a role field."""

    selected_name = _expected_harness_name(harness_name)
    if not selected_name:
        raise RuntimeError("resolve_changed_by: acting harness identity is unavailable.")

    from groundtruth_kb.session.envelope import (
        EnvelopeError,
        resolve_acting_harness_identity,
        resolve_harness_identity,
    )

    try:
        durable_name, durable_id = resolve_harness_identity(
            project_root,
            harness_name=selected_name,
        )
        acting_name, _acting_id = resolve_acting_harness_identity(
            project_root,
            harness_name=durable_name,
            harness_id=durable_id,
        )
    except EnvelopeError as exc:
        raise RuntimeError(f"resolve_changed_by: {exc}") from exc
    return acting_name


def resolve_changed_by(
    *,
    project_root: Path | str | None = None,
    harness_name: str | None = None,
) -> str:
    """Return ``<role>/<harness>`` or fail before mutation.

    The invoking session context must resolve to its immutable exact-init
    binding and initial role attestation. Worker-session documents, harness
    role registries, dispatcher selection, markers, and role environment values
    are never fallback authority.
    """
    resolved_project_root = PROJECT_ROOT if project_root is None else Path(project_root)
    session_id = _current_session_id()
    resolved_harness = _resolve_harness_attribution(resolved_project_root, harness_name)

    from groundtruth_kb.session.attestation import (
        RoleAttestationError,
        binding_for_context,
    )

    try:
        binding = binding_for_context(
            resolved_project_root / "groundtruth.db",
            session_id,
        )
    except RoleAttestationError as exc:
        raise RuntimeError(f"resolve_changed_by: {exc}") from exc
    if binding.role not in {"prime-builder", "loyal-opposition"}:
        raise RuntimeError(f"resolve_changed_by: unsupported exact-init role {binding.role!r}")
    return f"{binding.role}/{resolved_harness}"


def resolve_changed_by_or_none(
    *,
    project_root: Path | str | None = None,
    harness_name: str | None = None,
) -> str | None:
    """Read-only convenience variant; mutating writers must use ``resolve_changed_by``."""
    try:
        return resolve_changed_by(project_root=project_root, harness_name=harness_name)
    except RuntimeError:
        return None
