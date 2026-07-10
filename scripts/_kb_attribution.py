"""Document-authoritative ``changed_by`` resolution for canonical backlog writers.

Roles for non-dispatcher behavior never come from the durable harness registry,
shared markers, dispatcher selection, or vendor identity. A worker session must
first carry validated ``worker_role_provenance`` in its own open session document.
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
        raise RuntimeError("resolve_changed_by: current session id is missing; worker role provenance is required.")
    return session_id


def resolve_changed_by(
    *,
    project_root: Path | str | None = None,
    harness_name: str | None = None,
) -> str:
    """Return ``<document-role>/<document-harness>`` or fail before mutation."""
    from groundtruth_kb.session.envelope import EnvelopeError, resolve_worker_role_provenance

    resolved_project_root = PROJECT_ROOT if project_root is None else Path(project_root)
    try:
        provenance = resolve_worker_role_provenance(
            resolved_project_root,
            current_session_id=_current_session_id(),
            harness_name=_expected_harness_name(harness_name),
        )
    except EnvelopeError as exc:
        raise RuntimeError(f"resolve_changed_by: {exc}") from exc
    return f"{provenance['role']}/{provenance['harness_name']}"


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
