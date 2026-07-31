"""Deterministic session-envelope state writer.

The session envelope is local-file based so prompt-time hooks and CLIs can
inspect and update it without depending on MemBase availability. Each worker
session has its own authoritative document; the per-harness current envelope is
only a compatibility projection for lifecycle consumers.

Activity-specific terminology and skill advisories are not part of the base
envelope; they load when ``::open <activity>`` is accepted (SPEC-INTAKE-46594e).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from groundtruth_kb.context.resource_routing import (
    canonical_resource_contract,
    dispatch_resource_selection,
    resolve_resource_selection,
)
from groundtruth_kb.harness_projection import HarnessStateError, read_identity, read_roles

ENVELOPE_SCHEMA_VERSION = 1
WORKER_ROLE_PROVENANCE_SCHEMA_VERSION = 1
TOPIC_TYPES = ("ops", "deliberation", "build", "test", "spec", "project")
GIT_STATUS_SHORT_LINE_LIMIT = 80
GIT_PROBE_TIMEOUT_SECONDS = 5
WORKER_ROLES = frozenset({"prime-builder", "loyal-opposition"})
_SAFE_SESSION_DOCUMENT_ID = re.compile(r"^[A-Za-z0-9._-]+$")
_CANONICAL_INIT_KEYWORD = re.compile(r"::init (gtkb|application)(?: (pb|lo))?")
_CANONICAL_ROLE_BY_TOKEN = {
    "pb": "prime-builder",
    "lo": "loyal-opposition",
}

ROUTE_TARGETS = {
    "ops": "operations-status-decision-service",
    "deliberation": "deliberation-archive-service",
    "build": "build-package-scaffold-service",
    "test": "test-assertion-service",
    "spec": "spec-governance-service",
    "project": "project-lifecycle-service",
}

PRELOAD_STATES = {
    "ops": {
        "sources": ["operations_status", "support_user_activity", "ops_feedback_inputs"],
        "commands": ["gt projects", "gt backlog"],
    },
    "deliberation": {
        "sources": [
            "deliberation_archive",
            "Advisory Proposals are governed bridge artifacts",
            "ADVISORY entries are non-dispatchable and not implementation approval",
            "ADVISORY bridge entries via bridge/TAFE/dispatcher status surfaces",
            "status-bearing versioned files under bridge/",
            "Advisory Proposal is the primary Loyal Opposition mechanism for future-work initiation",
            "interactive workers progress advisories through governed advisory intake/disposition",
            "CODEX-INSIGHT-DROPBOX and independent-progress-assessments dropbox files are "
            "non-canonical session evidence only",
        ],
        "commands": [
            "gt deliberations record",
            "gt deliberations search",
            "gt bridge show <advisory-slug>",
            "gt bridge dispatch report --json --compact",
        ],
    },
    "build": {
        "sources": [
            "selected_resource evidence from the current owner prompt",
            "backlog authority: MemBase current_work_items",
            "bridge queue authority: TAFE/dispatcher state plus status-bearing bridge/ files",
            "active PAUTH and implementation-start authorization",
            "Advisory Proposals are governed bridge artifacts",
            "ADVISORY bridge entries are non-dispatchable and not implementation approval",
            "ADVISORY access through bridge/TAFE/dispatcher status surfaces and status-bearing bridge/ files",
            "Advisory Proposal is the primary Loyal Opposition mechanism for future-work initiation",
            "Advisory Proposal future-work initiation through governed advisory intake/disposition",
            "CODEX-INSIGHT-DROPBOX and independent-progress-assessments dropbox files are "
            "non-canonical session evidence only",
        ],
        "commands": [
            "gt backlog list",
            "gt bridge state-report",
            "gt bridge show <advisory-slug>",
            "gt bridge dispatch report --json --compact",
        ],
    },
    "test": {
        "sources": ["assertion_history", "failing_assertions", "test_inventory"],
        "commands": ["gt assert", "python -m pytest"],
    },
    "spec": {
        "sources": ["current_specs", "related_bridge_proposals", "proposal_templates"],
        "commands": ["gt spec", "gt bridge"],
    },
    "project": {
        "sources": ["current_project_authorizations", "open_work_items", "project_memberships"],
        "commands": ["gt projects"],
    },
}

MANDATORY_WRAP_STEPS = (1, 4, 8, 11, 12)


class EnvelopeError(RuntimeError):
    """Raised when the session envelope cannot be updated safely."""


def parse_canonical_init_keyword(value: str | None) -> dict[str, str | None] | None:
    """Parse the exact canonical session-init grammar without normalization."""
    if not isinstance(value, str):
        return None
    match = _CANONICAL_INIT_KEYWORD.fullmatch(value)
    if match is None:
        return None
    subject, role_token = match.groups()
    return {
        "subject": subject,
        "role": _CANONICAL_ROLE_BY_TOKEN.get(role_token),
    }


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def archive_timestamp(value: str) -> str:
    return value.replace(":", "-")


def harness_state_dir(project_root: Path, harness_name: str) -> Path:
    return project_root / "harness-state" / harness_name


def current_envelope_path(project_root: Path, harness_name: str) -> Path:
    return harness_state_dir(project_root, harness_name) / "session-envelope.json"


def worker_session_envelope_dir(project_root: Path, harness_name: str) -> Path:
    """Return the directory containing authoritative per-session documents."""
    return harness_state_dir(project_root, harness_name) / "session-envelopes"


def _worker_session_document_filename(session_id: str) -> str:
    session_token = str(session_id).strip()
    if not session_token or session_token in {".", ".."} or _SAFE_SESSION_DOCUMENT_ID.fullmatch(session_token) is None:
        raise EnvelopeError("Worker session id is not safe for a session-envelope document path.")
    return f"{session_token}.json"


def worker_session_envelope_path(project_root: Path, harness_name: str, session_id: str) -> Path:
    """Return the authoritative document path for one worker session."""
    return worker_session_envelope_dir(project_root, harness_name) / _worker_session_document_filename(session_id)


def archive_dir(project_root: Path, harness_name: str) -> Path:
    return harness_state_dir(project_root, harness_name) / "session-envelope-archive"


def projection_path(project_root: Path) -> Path:
    return project_root / ".claude" / "session" / "envelope.json"


def _read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def _write_envelope_document(path: Path, envelope: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(envelope, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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


def _role_resolution(
    project_root: Path,
    harness_id: str,
    *,
    role: str | None,
    role_source: str | None = None,
) -> dict[str, str | None]:
    durable_role = _resolve_role(project_root, harness_id)
    resolved_role = role or durable_role
    transcript_source = role_source == "transcript_init_keyword" or (role_source is None and role is not None)
    if transcript_source:
        return {
            "interactive_resolved_role": resolved_role,
            "interactive_role_source": "transcript_init_keyword",
            "durable_registry_role": durable_role,
            "durable_registry_authority": (
                "headless dispatch routing and interactive fallback only; non-overriding when "
                "a transcript-defined interactive role is present"
            ),
            "authority_mode": "interactive_transcript",
        }
    if role_source is not None:
        return {
            "interactive_resolved_role": resolved_role,
            "interactive_role_source": None,
            "durable_registry_role": durable_role,
            "durable_registry_authority": "dispatcher routing and audit only; worker behavior comes from this document",
            "authority_mode": "worker_session_document",
        }
    return {
        "interactive_resolved_role": resolved_role,
        "interactive_role_source": None,
        "durable_registry_role": durable_role,
        "durable_registry_authority": (
            "headless dispatch routing and interactive fallback only; non-overriding when "
            "a transcript-defined interactive role is present"
        ),
        "authority_mode": "durable_registry_fallback",
    }


def _normalized_path(value: Path) -> str:
    try:
        resolved = value.resolve()
    except OSError:
        resolved = value.absolute()
    return os.path.normcase(str(resolved))


def _git_unavailable(
    reason: str,
    *,
    error: str | None = None,
    returncode: int | None = None,
    top_level: str | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "available": False,
        "reason": reason,
        "dirty": None,
        "short": "",
    }
    if error is not None:
        result["error"] = error
    if returncode is not None:
        result["returncode"] = returncode
    if top_level is not None:
        result["top_level"] = top_level
    return result


def _git_status(project_root: Path) -> dict[str, Any]:
    expected_root = _normalized_path(project_root)
    try:
        top_level_result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
            timeout=GIT_PROBE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return _git_unavailable("git_top_level_timeout")
    except OSError as exc:
        return _git_unavailable("git_top_level_unavailable", error=str(exc))

    if top_level_result.returncode != 0:
        return _git_unavailable(
            "git_top_level_failed",
            error=(top_level_result.stderr or top_level_result.stdout).strip(),
            returncode=top_level_result.returncode,
        )

    top_level = top_level_result.stdout.strip()
    if not top_level:
        return _git_unavailable("git_top_level_empty")
    actual_root = _normalized_path(Path(top_level))
    if actual_root != expected_root:
        return _git_unavailable("git_top_level_mismatch", top_level=top_level)

    try:
        status_result = subprocess.run(
            ["git", "status", "--short"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
            timeout=GIT_PROBE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return _git_unavailable("git_status_timeout", top_level=top_level)
    except OSError as exc:
        return _git_unavailable("git_status_unavailable", error=str(exc), top_level=top_level)

    if status_result.returncode != 0:
        return _git_unavailable(
            "git_status_failed",
            error=(status_result.stderr or status_result.stdout).strip(),
            returncode=status_result.returncode,
            top_level=top_level,
        )

    lines = [line for line in status_result.stdout.splitlines() if line.strip()]
    shown = lines[:GIT_STATUS_SHORT_LINE_LIMIT]
    short = "\n".join(shown)
    return {
        "available": True,
        "returncode": status_result.returncode,
        "top_level": top_level,
        "exact_root": True,
        "dirty": bool(lines),
        "short": short,
        "short_line_count": len(lines),
        "short_line_limit": GIT_STATUS_SHORT_LINE_LIMIT,
        "short_truncated": len(lines) > GIT_STATUS_SHORT_LINE_LIMIT,
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
    session_id: str | None = None,
) -> dict[str, Any]:
    opened_at = utc_now_iso()
    resolved_subject = subject or os.environ.get("GTKB_WORK_SUBJECT") or "gtkb_infrastructure"
    role_resolution = _role_resolution(project_root, harness_id, role=role)
    resolved_role = role_resolution["interactive_resolved_role"]
    return {
        "envelope_schema_version": ENVELOPE_SCHEMA_VERSION,
        "session_id": session_id or _session_id(harness_id, opened_at),
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
        "role_resolution": role_resolution,
        "application_id": None,
        "resource_contract": canonical_resource_contract(),
        "resource_selection": resolve_resource_selection("", selection_source="session_initialization"),
        "opened_at": opened_at,
        "closed_at": None,
        "wrap_outcome": None,
        "status": "open",
        "topics": [],
        "last_error": None,
    }


def _require_nonempty_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EnvelopeError(f"Worker role provenance field {field!r} must be a non-empty string.")
    return value.strip()


def _worker_role_provenance(
    envelope: dict[str, Any],
    *,
    role: str,
    role_source: str,
    dispatch_run_id: str | None,
) -> dict[str, Any]:
    if role not in WORKER_ROLES:
        raise EnvelopeError(f"Worker role provenance role must be one of {sorted(WORKER_ROLES)}.")
    return {
        "schema_version": WORKER_ROLE_PROVENANCE_SCHEMA_VERSION,
        "session_id": envelope["session_id"],
        "harness_id": envelope["harness_id"],
        "harness_name": envelope["harness_name"],
        "role": role,
        "role_resolution_source": _require_nonempty_string(role_source, "role_resolution_source"),
        "dispatch_run_id": dispatch_run_id,
        "issued_at": utc_now_iso(),
    }


def _validate_worker_role_provenance(
    envelope: dict[str, Any],
    *,
    current_session_id: str,
    expected_harness_name: str | None = None,
) -> dict[str, str | int | None]:
    """Validate the explicit worker-role authority carried by one open envelope."""
    if envelope.get("status") != "open":
        raise EnvelopeError("Worker role provenance requires an open session envelope.")
    provenance = envelope.get("worker_role_provenance")
    if not isinstance(provenance, dict):
        raise EnvelopeError("Worker role provenance is missing from the session envelope.")
    if provenance.get("schema_version") != WORKER_ROLE_PROVENANCE_SCHEMA_VERSION:
        raise EnvelopeError("Worker role provenance schema version is missing or unsupported.")

    session_id = _require_nonempty_string(envelope.get("session_id"), "session_id")
    harness_id = _require_nonempty_string(envelope.get("harness_id"), "harness_id")
    harness_name = _require_nonempty_string(envelope.get("harness_name"), "harness_name")
    if session_id != current_session_id:
        raise EnvelopeError("Worker role provenance session id does not match the current session.")
    if expected_harness_name is not None and harness_name != expected_harness_name:
        raise EnvelopeError("Worker role provenance harness name does not match the expected worker.")

    result: dict[str, str | int | None] = {"schema_version": WORKER_ROLE_PROVENANCE_SCHEMA_VERSION}
    for field, expected in (("session_id", session_id), ("harness_id", harness_id), ("harness_name", harness_name)):
        actual = _require_nonempty_string(provenance.get(field), field)
        if actual != expected:
            raise EnvelopeError(f"Worker role provenance {field} conflicts with its session envelope.")
        result[field] = actual

    role = _require_nonempty_string(provenance.get("role"), "role")
    if role not in WORKER_ROLES:
        raise EnvelopeError(f"Worker role provenance role must be one of {sorted(WORKER_ROLES)}.")
    for envelope_role_field in ("role", "role_resolved", "role_asserted"):
        envelope_role = envelope.get(envelope_role_field)
        if envelope_role is None:
            continue
        if _require_nonempty_string(envelope_role, envelope_role_field) != role:
            raise EnvelopeError(f"Worker role provenance role conflicts with envelope {envelope_role_field}.")
    result["role"] = role
    role_source = _require_nonempty_string(provenance.get("role_resolution_source"), "role_resolution_source")
    result["role_resolution_source"] = role_source
    role_resolution = envelope.get("role_resolution")
    if isinstance(role_resolution, dict):
        interactive_role = role_resolution.get("interactive_resolved_role")
        if (
            interactive_role is not None
            and _require_nonempty_string(interactive_role, "interactive_resolved_role") != role
        ):
            raise EnvelopeError("Worker role provenance role conflicts with envelope role_resolution.")
        interactive_source = role_resolution.get("interactive_role_source")
        authority_mode = role_resolution.get("authority_mode")
        if role_source == "transcript_init_keyword":
            if interactive_source != "transcript_init_keyword" or authority_mode != "interactive_transcript":
                raise EnvelopeError(
                    "Transcript init-keyword worker provenance requires transcript role_resolution metadata."
                )
        elif interactive_source == "transcript_init_keyword":
            raise EnvelopeError(
                "Session envelope claims transcript role resolution but worker provenance is not transcript-derived."
            )
    result["issued_at"] = _require_nonempty_string(provenance.get("issued_at"), "issued_at")
    dispatch_run_id = provenance.get("dispatch_run_id")
    if dispatch_run_id is not None:
        result["dispatch_run_id"] = _require_nonempty_string(dispatch_run_id, "dispatch_run_id")
    else:
        result["dispatch_run_id"] = None
    return result


def _load_worker_document(path: Path) -> dict[str, Any]:
    envelope = _read_json(path, None)
    if not isinstance(envelope, dict):
        raise EnvelopeError(f"Worker session envelope is malformed: {path}")
    return envelope


def resolve_worker_role_provenance(
    project_root: Path,
    *,
    current_session_id: str,
    harness_name: str | None = None,
) -> dict[str, str | int | None]:
    """Return the validated, document-authoritative actor for one worker session.

    The optional harness name selects a document only. It never contributes role
    authority; roles come exclusively from ``worker_role_provenance``.
    """
    current_session_id = _require_nonempty_string(current_session_id, "current_session_id")
    if harness_name is not None:
        expected_harness_name = _require_nonempty_string(harness_name, "harness_name")
        path = worker_session_envelope_path(project_root, expected_harness_name, current_session_id)
        if not path.is_file():
            # Existing installations may still have exactly one session document
            # in the legacy projection path. It is acceptable only when its own
            # session id validates; it can never authorize another session.
            path = current_envelope_path(project_root, expected_harness_name)
        if not path.is_file():
            if any(worker_session_envelope_dir(project_root, expected_harness_name).glob("*.json")):
                raise EnvelopeError("Worker role provenance session id does not match the current session.")
            raise EnvelopeError("Worker role provenance is missing for the current session.")
        envelope = _load_worker_document(path)
        return _validate_worker_role_provenance(
            envelope,
            current_session_id=current_session_id,
            expected_harness_name=expected_harness_name,
        )

    state_root = project_root / "harness-state"
    document_name = _worker_session_document_filename(current_session_id)
    matched: list[tuple[dict[str, Any], str]] = []
    session_document_harnesses: set[str] = set()
    for path in sorted(state_root.glob(f"*/session-envelopes/{document_name}")):
        if not path.is_file():
            continue
        harness = path.parent.parent.name
        session_document_harnesses.add(harness)
        matched.append((_load_worker_document(path), harness))

    # Retain a narrow read-only migration path for a legacy document, but never
    # let a shared per-harness projection compete with an exact session document.
    for path in sorted(state_root.glob("*/session-envelope.json")):
        harness = path.parent.name
        if harness in session_document_harnesses or not path.is_file():
            continue
        envelope = _read_json(path, None)
        if not isinstance(envelope, dict):
            continue
        provenance = envelope.get("worker_role_provenance")
        if isinstance(provenance, dict) and provenance.get("session_id") == current_session_id:
            matched.append((envelope, harness))

    if not matched:
        raise EnvelopeError("Worker role provenance is missing for the current session.")
    if len(matched) != 1:
        raise EnvelopeError("Worker role provenance is ambiguous across session envelopes.")
    envelope, expected_harness_name = matched[0]
    return _validate_worker_role_provenance(
        envelope,
        current_session_id=current_session_id,
        expected_harness_name=expected_harness_name,
    )


def write_current(project_root: Path, harness_name: str, envelope: dict[str, Any]) -> Path:
    session_id = _require_nonempty_string(envelope.get("session_id"), "session_id")
    authoritative_path = worker_session_envelope_path(project_root, harness_name, session_id)
    _write_envelope_document(authoritative_path, envelope)
    path = current_envelope_path(project_root, harness_name)
    _write_envelope_document(path, envelope)
    _write_projection(
        project_root,
        harness_name,
        envelope,
        authoritative=True,
        authoritative_path=authoritative_path,
    )
    return path


def _write_projection(
    project_root: Path,
    harness_name: str,
    envelope: dict[str, Any],
    *,
    authoritative: bool,
    authoritative_path: Path | None = None,
) -> None:
    projection = dict(envelope)
    projection["projection_authoritative"] = authoritative
    projection["authoritative_path"] = (
        authoritative_path or current_envelope_path(project_root, harness_name)
    ).as_posix()
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


def load_worker_session(project_root: Path, harness_name: str, session_id: str) -> dict[str, Any] | None:
    """Load one authoritative session document without consulting the projection."""
    path = worker_session_envelope_path(project_root, harness_name, session_id)
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
    session_id: str | None = None,
    worker_role_source: str | None = None,
    dispatch_run_id: str | None = None,
) -> dict[str, Any]:
    resolved_name, resolved_id = resolve_harness_identity(
        project_root,
        harness_name=harness_name,
        harness_id=harness_id,
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
        session_id=session_id,
    )
    if worker_role_source is not None:
        if role is None:
            raise EnvelopeError("Worker role provenance requires an explicit resolved role.")
        envelope["role_resolution"] = _role_resolution(
            project_root,
            resolved_id,
            role=role,
            role_source=worker_role_source,
        )
        envelope["worker_role_provenance"] = _worker_role_provenance(
            envelope,
            role=role,
            role_source=worker_role_source,
            dispatch_run_id=dispatch_run_id,
        )
    dispatch_selection = dispatch_resource_selection(dispatch_run_id)
    if dispatch_selection["selected_resources"]:
        envelope["resource_selection"] = dispatch_selection
    write_current(project_root, resolved_name, envelope)
    return envelope


# DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001 (CLAUSE-PERSISTENCE-ACROSS-BOUNDARIES).
# Deliberately self-contained: these sets are read only by the persistence resolver
# below so the clause stays satisfied independently of neighbouring role-source work.
PERSISTED_TRANSCRIPT_ROLE_SOURCE = "transcript_init_keyword"
# Worker-document provenance values that already carry owner-declared interactive authority.
TRANSCRIPT_ROLE_SOURCES = frozenset(
    {
        "interactive_transcript_explicit",
        "owner_init_keyword",
        "transcript_init_keyword",
    }
)
# Per-session role-marker ``source`` labels written by the init-keyword surfaces.
TRANSCRIPT_MARKER_SOURCES = frozenset(
    {
        "init_keyword",
        "owner_init_keyword",
        "session_self_initialization",
        "transcript_init_keyword",
    }
)
# Role sources that carry no owner direction; only these defer to a prior transcript role.
REGISTRY_FALLBACK_ROLE_SOURCES = frozenset({"session_resolver_fallback"})
_UNSAFE_MARKER_SESSION_ID_CHARS = re.compile(r"[^A-Za-z0-9._-]+")


def _per_session_role_marker_path(project_root: Path, session_id: str) -> Path:
    """Return the per-session role-marker path, mirroring the canonical builder."""
    try:  # pragma: no cover - import shape varies by entrypoint
        from scripts.gtkb_session_id import per_session_role_marker_path  # noqa: PLC0415
    except ImportError:  # pragma: no cover - direct-script sys.path shape
        try:
            from gtkb_session_id import (  # type: ignore[no-redef]  # noqa: PLC0415
                per_session_role_marker_path,
            )
        except ImportError:
            sanitized = _UNSAFE_MARKER_SESSION_ID_CHARS.sub("-", str(session_id)).strip("-.") or "unknown"
            return Path(project_root) / ".claude" / "session" / f"role-{sanitized[:128]}.json"
    return per_session_role_marker_path(project_root, session_id)


def transcript_declared_role(
    project_root: Path,
    session_id: str,
    *,
    envelope: dict[str, Any] | None = None,
) -> tuple[str, str] | None:
    """Return ``(role, role_source)`` when this session context already carries an
    owner-declared interactive role, else ``None``.

    Implements ``DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001``
    ``CLAUSE-PERSISTENCE-ACROSS-BOUNDARIES``: an explicit-direction role established
    in an interactive transcript must survive compaction, resume, and contiguous
    SessionStart-like boundaries, changing only when the owner explicitly changes it.
    Two evidence surfaces are consulted, in order: a prior worker session document
    whose ``role_resolution_source`` is interactive, then the per-session role marker
    written by the init-keyword surfaces. The marker is what makes the role survive a
    boundary that re-creates (or has already overwritten) the worker document.

    The durable registry is never read or written here: it stays the caller's fallback
    and is never mutated (``CLAUSE-NO-DURABLE-REGISTRY-MUTATION``).

    Fail-safe: any unexpected read or parse error yields ``None`` so callers fall back
    to registry-derived behavior. A role-resolution repair must never make a session
    unstartable.
    """
    try:
        if isinstance(envelope, dict):
            provenance = envelope.get("worker_role_provenance")
            if isinstance(provenance, dict):
                prior_source = provenance.get("role_resolution_source")
                prior_role = provenance.get("role")
                if (
                    isinstance(prior_source, str)
                    and prior_source in TRANSCRIPT_ROLE_SOURCES
                    and isinstance(prior_role, str)
                    and prior_role in WORKER_ROLES
                ):
                    return prior_role, prior_source

        marker = _read_json(_per_session_role_marker_path(project_root, session_id), None)
        if isinstance(marker, dict):
            marker_session_id = marker.get("session_id")
            if isinstance(marker_session_id, str) and marker_session_id and marker_session_id != session_id:
                return None
            marker_source = marker.get("source")
            marker_role = marker.get("role")
            if (
                isinstance(marker_source, str)
                and marker_source in TRANSCRIPT_MARKER_SOURCES
                and isinstance(marker_role, str)
                and marker_role in WORKER_ROLES
            ):
                return marker_role, PERSISTED_TRANSCRIPT_ROLE_SOURCE
    except Exception:  # noqa: BLE001 - role resolution must never make a session unstartable
        return None
    return None


def ensure_worker_session(
    project_root: Path,
    *,
    harness_name: str,
    session_id: str,
    role: str,
    role_source: str,
    harness_id: str | None = None,
    init_keyword: str | None = None,
    dispatch_run_id: str | None = None,
) -> dict[str, Any]:
    """Create or refresh one session-keyed document used for worker authority."""
    resolved_name, resolved_id = resolve_harness_identity(
        project_root,
        harness_name=harness_name,
        harness_id=harness_id,
    )
    current = load_worker_session(project_root, resolved_name, session_id)

    # DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001 (CLAUSE-PERSISTENCE-ACROSS-BOUNDARIES,
    # CLAUSE-AGENT-HINT-NOT-LOCK): a registry-derived fallback is a hint, not authority.
    # When this session context already carries an owner-declared interactive role, the
    # fallback defers to it -- including when the document is being re-created at a
    # SessionStart-like boundary, which is the case a document-only guard cannot see.
    # Explicit new owner direction and dispatcher composition
    # (CLAUSE-DISPATCHER-SOT-FOR-DISPATCH) are untouched; only the fallback defers.
    if role_source in REGISTRY_FALLBACK_ROLE_SOURCES:
        persisted = transcript_declared_role(project_root, session_id, envelope=current)
        if persisted is not None:
            role, role_source = persisted

    if current is None or current.get("status") != "open" or current.get("session_id") != session_id:
        return open_session(
            project_root,
            harness_name=resolved_name,
            harness_id=resolved_id,
            init_keyword=init_keyword,
            role=role,
            session_id=session_id,
            worker_role_source=role_source,
            dispatch_run_id=dispatch_run_id,
        )

    current["role_asserted"] = role
    current["role_resolved"] = role
    current["role"] = role
    if init_keyword is not None:
        current["init_keyword"] = init_keyword
    current["role_resolution"] = _role_resolution(
        project_root,
        resolved_id,
        role=role,
        role_source=role_source,
    )
    current["worker_role_provenance"] = _worker_role_provenance(
        current,
        role=role,
        role_source=role_source,
        dispatch_run_id=dispatch_run_id,
    )
    dispatch_selection = dispatch_resource_selection(dispatch_run_id)
    if dispatch_selection["selected_resources"]:
        current["resource_contract"] = canonical_resource_contract()
        current["resource_selection"] = dispatch_selection
    write_current(project_root, resolved_name, current)
    return current


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


def route_prompt_resources(
    project_root: Path,
    prompt: str,
    *,
    harness_name: str = "codex",
    harness_id: str | None = None,
) -> dict[str, Any]:
    """Apply explicit current-prompt resource and work-item evidence to an envelope."""

    resolved_name, _ = resolve_harness_identity(
        project_root,
        harness_name=harness_name,
        harness_id=harness_id,
    )
    envelope = ensure_current(project_root, harness_name=resolved_name, harness_id=harness_id)
    selection = resolve_resource_selection(prompt)
    prompt_work_items = selection["work_item_ids"]
    if not selection["explicit_resource_terms"] and not prompt_work_items:
        return selection

    envelope["resource_contract"] = canonical_resource_contract()
    if selection["explicit_resource_terms"]:
        envelope["resource_selection"] = selection

    existing_work_items = [
        value for value in envelope.get("work_item_ids", []) if isinstance(value, str) and value.strip()
    ]
    envelope["work_item_ids"] = list(dict.fromkeys([*existing_work_items, *prompt_work_items]))
    if len(prompt_work_items) == 1:
        envelope["active_work_item_id"] = prompt_work_items[0]
    elif len(prompt_work_items) > 1:
        envelope["active_work_item_id"] = None
    write_current(project_root, resolved_name, envelope)
    return selection


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
    # Single-active invariant (SPEC-TOPIC-ENVELOPE-ROUTER-001 v3 / WI-4685): at
    # most one topic envelope may be open at a time. Opening a new topic closes
    # the currently-open topic (auto-close + dispatch) before opening the new one.
    for existing in envelope.get("topics", []):
        if existing.get("closed_at") is None:
            existing["closed_at"] = utc_now_iso()
            existing["close_outcome"] = "auto_closed_by_open_supplant"
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


def _close_open_topic(
    envelope: dict[str, Any],
    *,
    expected_type: str | None,
    close_outcome: str,
) -> dict[str, Any] | None:
    """Close the single currently-open topic in ``envelope`` (single-active).

    Returns the closed topic dict, or ``None`` when no topic is open (an
    idempotent no-op per SPEC-TOPIC-ENVELOPE-ROUTER-001 v3). When
    ``expected_type`` is given and the open topic is a different type, raises
    :class:`EnvelopeError` (a guidance error) rather than silently closing the
    wrong envelope.
    """
    open_topics = [t for t in envelope.get("topics", []) if t.get("closed_at") is None]
    if not open_topics:
        return None
    current = open_topics[-1]
    if expected_type is not None and current.get("type") != expected_type:
        raise EnvelopeError(
            f"::close {expected_type} but the open topic envelope is "
            f"{current.get('type')!r}; close it with bare ::close or "
            f"::close {current.get('type')}."
        )
    current["closed_at"] = utc_now_iso()
    current["close_outcome"] = close_outcome
    return current


def close_topic(
    project_root: Path,
    topic_type: str,
    *,
    harness_name: str = "codex",
    harness_id: str | None = None,
    close_outcome: str = "closed",
) -> dict[str, Any] | None:
    """Close the currently-open topic, asserting it is ``topic_type``.

    Single-active invariant (WI-4685): at most one topic envelope is open.
    ``::close <type>`` closes it when the open topic is ``topic_type``; a
    type mismatch is a guidance error; nothing open is an idempotent no-op
    (returns ``None``).
    """
    if topic_type not in TOPIC_TYPES:
        raise EnvelopeError(f"Unsupported topic type: {topic_type}")
    resolved_name, _ = resolve_harness_identity(project_root, harness_name=harness_name, harness_id=harness_id)
    envelope = ensure_current(project_root, harness_name=resolved_name, harness_id=harness_id)
    closed = _close_open_topic(envelope, expected_type=topic_type, close_outcome=close_outcome)
    if closed is None:
        return None
    write_current(project_root, resolved_name, envelope)
    return dict(closed)


def close_current_topic(
    project_root: Path,
    *,
    harness_name: str = "codex",
    harness_id: str | None = None,
    close_outcome: str = "closed",
) -> dict[str, Any] | None:
    """Close the single currently-open topic envelope (bare ``::close``).

    Single-active invariant (WI-4685): at most one topic is open. Returns the
    closed topic, or ``None`` if no topic is open (an idempotent no-op).
    """
    resolved_name, _ = resolve_harness_identity(project_root, harness_name=harness_name, harness_id=harness_id)
    envelope = ensure_current(project_root, harness_name=resolved_name, harness_id=harness_id)
    closed = _close_open_topic(envelope, expected_type=None, close_outcome=close_outcome)
    if closed is None:
        return None
    write_current(project_root, resolved_name, envelope)
    return dict(closed)


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
    observed_steps = {
        int(item.get("step"))  # type: ignore[arg-type]
        for item in envelope["wrap_step_results"]
        if isinstance(item, dict) and item.get("step") is not None
    }
    missing = sorted(set(MANDATORY_WRAP_STEPS) - observed_steps)
    if missing:
        raise EnvelopeError(f"Wrap step results missing mandatory steps: {missing}")
    out_dir = archive_dir(project_root, resolved_name)
    out_dir.mkdir(parents=True, exist_ok=True)
    archive_path = out_dir / f"{archive_timestamp(closed_at)}-session-envelope.json"
    archive_path.write_text(json.dumps(envelope, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    worker_path = worker_session_envelope_path(project_root, resolved_name, str(envelope["session_id"]))
    _write_envelope_document(worker_path, envelope)
    current_path = current_envelope_path(project_root, resolved_name)
    if current_path.exists():
        current_path.unlink()
    _write_projection(
        project_root,
        resolved_name,
        envelope,
        authoritative=False,
        authoritative_path=worker_path,
    )
    return envelope, archive_path
