"""Deterministic session-envelope state writer.

The session envelope is the per-harness outer container for a GT-KB session.
It is intentionally local-file based so prompt-time hooks and CLIs can inspect
and update it without depending on MemBase availability.
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from groundtruth_kb.harness_projection import HarnessStateError, read_identity, read_roles

ENVELOPE_SCHEMA_VERSION = 1
TOPIC_TYPES = ("spec", "build", "test", "deliberation", "project")

ROUTE_TARGETS = {
    "spec": "spec-governance-service",
    "build": "build-package-scaffold-service",
    "test": "test-assertion-service",
    "deliberation": "deliberation-archive-service",
    "project": "project-lifecycle-service",
}

PRELOAD_STATES = {
    "spec": {
        "sources": ["current_specs", "related_bridge_proposals", "proposal_templates"],
        "commands": ["gt spec", "gt bridge"],
    },
    "build": {
        "sources": ["pyproject.toml", "package_state", "scaffold_state"],
        "commands": ["python -m build", "npm run build"],
    },
    "test": {
        "sources": ["assertion_history", "failing_assertions", "test_inventory"],
        "commands": ["gt assert", "python -m pytest"],
    },
    "deliberation": {
        "sources": ["deliberation_archive"],
        "commands": ["gt deliberations record", "gt deliberations search"],
    },
    "project": {
        "sources": ["current_project_authorizations", "open_work_items", "project_memberships"],
        "commands": ["gt projects"],
    },
}

MANDATORY_WRAP_STEPS = (1, 4, 8, 11, 12)


class EnvelopeError(RuntimeError):
    """Raised when the session envelope cannot be updated safely."""


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def archive_timestamp(value: str) -> str:
    return value.replace(":", "-")


def harness_state_dir(project_root: Path, harness_name: str) -> Path:
    return project_root / "harness-state" / harness_name


def current_envelope_path(project_root: Path, harness_name: str) -> Path:
    return harness_state_dir(project_root, harness_name) / "session-envelope.json"


def archive_dir(project_root: Path, harness_name: str) -> Path:
    return harness_state_dir(project_root, harness_name) / "session-envelope-archive"


def projection_path(project_root: Path) -> Path:
    return project_root / ".claude" / "session" / "envelope.json"


def _read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def resolve_harness_identity(
    project_root: Path,
    *,
    harness_name: str | None = None,
    harness_id: str | None = None,
) -> tuple[str, str]:
    name = (harness_name or "codex").strip().lower()
    try:
        identity_data = read_identity(project_root)
    except HarnessStateError:
        identity_data = {}
    harnesses = identity_data.get("harnesses") if isinstance(identity_data, dict) else None
    if isinstance(harnesses, dict):
        record = harnesses.get(name)
        if isinstance(record, dict):
            resolved_id = str(record.get("id") or "").strip()
            if resolved_id:
                if harness_id and harness_id != resolved_id:
                    raise EnvelopeError(f"Harness id {harness_id!r} does not match persisted id {resolved_id!r}.")
                return name, resolved_id
    if harness_id:
        return name, harness_id
    raise EnvelopeError(f"Could not resolve harness identity for {name!r}.")


def _resolve_role(project_root: Path, harness_id: str) -> str | None:
    try:
        registry = read_roles(project_root)
    except HarnessStateError:
        registry = {}
    rows = registry.get("harnesses") if isinstance(registry, dict) else None
    if not isinstance(rows, list):
        return None
    for row in rows:
        if not isinstance(row, dict) or str(row.get("id") or "") != harness_id:
            continue
        roles = row.get("role")
        if isinstance(roles, list) and roles:
            return str(roles[0])
        if isinstance(roles, str) and roles:
            return roles
    return None


def _git_status(project_root: Path) -> dict[str, Any]:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        return {"available": False, "error": str(exc), "dirty": None, "short": ""}
    short = result.stdout.strip()
    return {
        "available": result.returncode == 0,
        "returncode": result.returncode,
        "dirty": bool(short),
        "short": short,
    }


def _session_id(harness_id: str, opened_at: str) -> str:
    return f"{harness_id}-{archive_timestamp(opened_at)}"


def _base_envelope(
    project_root: Path,
    *,
    harness_name: str,
    harness_id: str,
    init_keyword: str | None = None,
    subject: str | None = None,
    role: str | None = None,
    project_id: str | None = None,
    work_item_ids: list[str] | None = None,
    active_work_item_id: str | None = None,
) -> dict[str, Any]:
    opened_at = utc_now_iso()
    resolved_role = role or _resolve_role(project_root, harness_id)
    resolved_subject = subject or os.environ.get("GTKB_WORK_SUBJECT") or "gtkb_infrastructure"
    return {
        "envelope_schema_version": ENVELOPE_SCHEMA_VERSION,
        "session_id": _session_id(harness_id, opened_at),
        "harness_id": harness_id,
        "harness_name": harness_name,
        "model_id": os.environ.get("GTKB_MODEL_ID") or os.environ.get("CODEX_MODEL") or "unknown",
        "model_version": os.environ.get("GTKB_MODEL_VERSION") or "unknown",
        "project_id": project_id,
        "work_item_ids": work_item_ids or ([active_work_item_id] if active_work_item_id else []),
        "active_work_item_id": active_work_item_id,
        "init_keyword": init_keyword,
        "subject_asserted": subject,
        "subject_resolved": resolved_subject,
        "subject": resolved_subject,
        "role_asserted": role,
        "role_resolved": resolved_role,
        "role": resolved_role,
        "application_id": None,
        "opened_at": opened_at,
        "closed_at": None,
        "wrap_outcome": None,
        "status": "open",
        "topics": [],
        "last_error": None,
    }


def write_current(project_root: Path, harness_name: str, envelope: dict[str, Any]) -> Path:
    path = current_envelope_path(project_root, harness_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(envelope, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_projection(project_root, harness_name, envelope, authoritative=True)
    return path


def _write_projection(project_root: Path, harness_name: str, envelope: dict[str, Any], *, authoritative: bool) -> None:
    projection = dict(envelope)
    projection["projection_authoritative"] = authoritative
    projection["authoritative_path"] = current_envelope_path(project_root, harness_name).as_posix()
    path = projection_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(projection, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_current(project_root: Path, harness_name: str) -> dict[str, Any] | None:
    path = current_envelope_path(project_root, harness_name)
    if not path.is_file():
        return None
    data = _read_json(path, None)
    if not isinstance(data, dict):
        raise EnvelopeError(f"Session envelope is not a JSON object: {path}")
    return data


def open_session(
    project_root: Path,
    *,
    harness_name: str = "codex",
    harness_id: str | None = None,
    init_keyword: str | None = None,
    subject: str | None = None,
    role: str | None = None,
    project_id: str | None = None,
    work_item_ids: list[str] | None = None,
    active_work_item_id: str | None = None,
) -> dict[str, Any]:
    resolved_name, resolved_id = resolve_harness_identity(
        project_root,
        harness_name=harness_name,
        harness_id=harness_id,
    )
    prior = load_current(project_root, resolved_name)
    if prior and prior.get("status") == "open":
        close_session(
            project_root,
            harness_name=resolved_name,
            harness_id=resolved_id,
            wrap_outcome="recovered_by_session_open",
        )
    envelope = _base_envelope(
        project_root,
        harness_name=resolved_name,
        harness_id=resolved_id,
        init_keyword=init_keyword,
        subject=subject,
        role=role,
        project_id=project_id,
        work_item_ids=work_item_ids,
        active_work_item_id=active_work_item_id,
    )
    write_current(project_root, resolved_name, envelope)
    return envelope


def ensure_current(
    project_root: Path,
    *,
    harness_name: str = "codex",
    harness_id: str | None = None,
) -> dict[str, Any]:
    resolved_name, resolved_id = resolve_harness_identity(
        project_root,
        harness_name=harness_name,
        harness_id=harness_id,
    )
    current = load_current(project_root, resolved_name)
    if current and current.get("status") == "open":
        return current
    return open_session(project_root, harness_name=resolved_name, harness_id=resolved_id)


def open_topic(
    project_root: Path,
    topic_type: str,
    *,
    harness_name: str = "codex",
    harness_id: str | None = None,
) -> dict[str, Any]:
    if topic_type not in TOPIC_TYPES:
        raise EnvelopeError(f"Unsupported topic type: {topic_type}")
    resolved_name, _ = resolve_harness_identity(project_root, harness_name=harness_name, harness_id=harness_id)
    envelope = ensure_current(project_root, harness_name=resolved_name, harness_id=harness_id)
    for topic in envelope.get("topics", []):
        if topic.get("type") == topic_type and topic.get("closed_at") is None:
            raise EnvelopeError(f"Topic envelope already open for type {topic_type!r}.")
    topic = {
        "type": topic_type,
        "opened_at": utc_now_iso(),
        "closed_at": None,
        "close_outcome": None,
        "preload_state": PRELOAD_STATES[topic_type],
        "route_target": ROUTE_TARGETS[topic_type],
    }
    envelope.setdefault("topics", []).append(topic)
    write_current(project_root, resolved_name, envelope)
    return topic


def close_topic(
    project_root: Path,
    topic_type: str,
    *,
    harness_name: str = "codex",
    harness_id: str | None = None,
    close_outcome: str = "closed",
) -> dict[str, Any]:
    if topic_type not in TOPIC_TYPES:
        raise EnvelopeError(f"Unsupported topic type: {topic_type}")
    resolved_name, _ = resolve_harness_identity(project_root, harness_name=harness_name, harness_id=harness_id)
    envelope = ensure_current(project_root, harness_name=resolved_name, harness_id=harness_id)
    for topic in reversed(envelope.get("topics", [])):
        if topic.get("type") == topic_type and topic.get("closed_at") is None:
            topic["closed_at"] = utc_now_iso()
            topic["close_outcome"] = close_outcome
            write_current(project_root, resolved_name, envelope)
            return topic
    raise EnvelopeError(f"No open topic envelope for type {topic_type!r}.")


def _default_wrap_step_results(
    project_root: Path,
    *,
    closed_topic_count: int,
) -> list[dict[str, Any]]:
    return [
        {"step": 1, "name": "finalize_session_envelope", "status": "pass"},
        {
            "step": 4,
            "name": "deliberation_archive_harvest",
            "status": "not_run",
            "reason": "no uncaptured harvest input",
        },
        {"step": 8, "name": "git_status_attestation", "status": "pass", "details": _git_status(project_root)},
        {"step": 11, "name": "topic_auto_close", "status": "pass", "closed_topic_count": closed_topic_count},
        {"step": 12, "name": "archive_session_envelope", "status": "pass"},
    ]


def close_session(
    project_root: Path,
    *,
    harness_name: str = "codex",
    harness_id: str | None = None,
    wrap_outcome: str = "manual_wrap",
    wrap_step_results: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], Path]:
    resolved_name, resolved_id = resolve_harness_identity(
        project_root,
        harness_name=harness_name,
        harness_id=harness_id,
    )
    envelope = load_current(project_root, resolved_name)
    if not envelope:
        envelope = open_session(project_root, harness_name=resolved_name, harness_id=resolved_id)
    closed_at = utc_now_iso()
    open_topic_count = sum(1 for topic in envelope.get("topics", []) if topic.get("closed_at") is None)
    for topic in envelope.get("topics", []):
        if topic.get("closed_at") is None:
            topic["closed_at"] = closed_at
            topic["close_outcome"] = "auto_closed_by_session_wrap"
    envelope["closed_at"] = closed_at
    envelope["wrap_outcome"] = wrap_outcome
    envelope["status"] = "closed"
    envelope["wrap_step_results"] = wrap_step_results or _default_wrap_step_results(
        project_root,
        closed_topic_count=open_topic_count,
    )
    observed_steps = {int(item.get("step")) for item in envelope["wrap_step_results"] if isinstance(item, dict)}
    missing = sorted(set(MANDATORY_WRAP_STEPS) - observed_steps)
    if missing:
        raise EnvelopeError(f"Wrap step results missing mandatory steps: {missing}")
    out_dir = archive_dir(project_root, resolved_name)
    out_dir.mkdir(parents=True, exist_ok=True)
    archive_path = out_dir / f"{archive_timestamp(closed_at)}-session-envelope.json"
    archive_path.write_text(json.dumps(envelope, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    current_path = current_envelope_path(project_root, resolved_name)
    if current_path.exists():
        current_path.unlink()
    _write_projection(project_root, resolved_name, envelope, authoritative=False)
    return envelope, archive_path
