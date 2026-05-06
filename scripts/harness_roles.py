"""Single source of truth for GT-KB harness role assignment."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    from scripts.harness_identity import (
        DEFAULT_HARNESS_IDS as _DEFAULT_HARNESS_IDS,
    )
    from scripts.harness_identity import (
        normalize_harness_id,
        normalize_harness_name,
    )
    from scripts.harness_identity import (
        resolved_harness_id as _resolved_persistent_harness_id,
    )
except ImportError:  # pragma: no cover - direct script execution path
    from harness_identity import (  # type: ignore[no-redef]
        DEFAULT_HARNESS_IDS as _DEFAULT_HARNESS_IDS,
    )
    from harness_identity import (
        normalize_harness_id,
        normalize_harness_name,
    )
    from harness_identity import (
        resolved_harness_id as _resolved_persistent_harness_id,
    )

ROLE_PRIME_BUILDER = "prime-builder"
ROLE_LOYAL_OPPOSITION = "loyal-opposition"
ROLE_ACTING_PRIME_BUILDER = "acting-prime-builder"
VALID_ROLES = {
    ROLE_PRIME_BUILDER,
    ROLE_LOYAL_OPPOSITION,
    ROLE_ACTING_PRIME_BUILDER,
}

ROLE_ASSIGNMENTS_RELATIVE_PATH = Path("harness-state") / "role-assignments.json"
DEFAULT_HARNESS_IDS = _DEFAULT_HARNESS_IDS


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def resolved_harness_id(
    project_root: Path | None = None,
    *,
    harness_id: str | None = None,
    harness_name: str | None = None,
) -> str | None:
    return _resolved_persistent_harness_id(
        project_root,
        harness_id=harness_id,
        harness_name=harness_name,
        bootstrap_missing=True,
    )


def role_assignments_path(project_root: Path, override: Path | None = None) -> Path:
    if override is not None:
        return override.expanduser().resolve()
    env_override = os.environ.get("GTKB_ROLE_ASSIGNMENTS_PATH")
    if env_override:
        return Path(env_override).expanduser().resolve()
    return project_root.resolve() / ROLE_ASSIGNMENTS_RELATIVE_PATH


def _empty_document(project_root: Path) -> dict[str, Any]:
    _ = project_root
    return {
        "schema_version": 1,
        "source_of_truth": "GT-KB harness role assignments",
        "description": (
            "Maps durable harness installation IDs to operating roles. "
            "Harness IDs are defined by harness-state/harness-identities.json."
        ),
        "updated_at": _now_iso(),
        "harnesses": {},
    }


def _normalize_document(raw: Any, project_root: Path) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raw = {}
    document = _empty_document(project_root)
    document.update({key: value for key, value in raw.items() if key != "harnesses"})
    harnesses = raw.get("harnesses")
    normalized_harnesses: dict[str, dict[str, Any]] = {}
    if isinstance(harnesses, dict):
        for raw_id, raw_record in harnesses.items():
            harness_id = normalize_harness_id(str(raw_id))
            if not harness_id or not isinstance(raw_record, dict):
                continue
            role = str(raw_record.get("role") or "").strip().lower()
            if role not in VALID_ROLES:
                continue
            normalized_harnesses[harness_id] = dict(raw_record)
            normalized_harnesses[harness_id]["role"] = role
    if normalized_harnesses:
        document["harnesses"] = normalized_harnesses
    return document


def load_role_assignments(project_root: Path, assignment_path: Path | None = None) -> dict[str, Any]:
    path = role_assignments_path(project_root, assignment_path)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        raw = {}
    return _normalize_document(raw, project_root)


def write_role_assignments(project_root: Path, document: dict[str, Any], assignment_path: Path | None = None) -> Path:
    path = role_assignments_path(project_root, assignment_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp.{os.getpid()}")
    tmp.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return path


def _ensure_record(
    document: dict[str, Any],
    harness_id: str,
    *,
    harness_name: str | None = None,
) -> dict[str, Any]:
    harnesses = document.setdefault("harnesses", {})
    record = harnesses.setdefault(harness_id, {})
    normalized_name = normalize_harness_name(harness_name)
    if normalized_name:
        record.setdefault("harness_type", normalized_name)
    record.setdefault("role", ROLE_LOYAL_OPPOSITION)
    return record


def current_prime_ids(document: dict[str, Any]) -> list[str]:
    harnesses = document.get("harnesses")
    if not isinstance(harnesses, dict):
        return []
    return [
        str(harness_id)
        for harness_id, record in harnesses.items()
        if isinstance(record, dict) and record.get("role") == ROLE_PRIME_BUILDER
    ]


def role_for_harness(
    project_root: Path,
    *,
    harness_id: str | None = None,
    harness_name: str | None = None,
    assignment_path: Path | None = None,
    ensure_prime_on_startup: bool = True,
) -> tuple[str, dict[str, Any], Path]:
    resolved_id = resolved_harness_id(project_root, harness_id=harness_id, harness_name=harness_name)
    path = role_assignments_path(project_root, assignment_path)
    document = load_role_assignments(project_root, assignment_path)
    if resolved_id is None:
        return ROLE_PRIME_BUILDER, document, path

    record = _ensure_record(document, resolved_id, harness_name=harness_name)
    changed = False
    if ensure_prime_on_startup and not current_prime_ids(document):
        for other_id, other_record in document.get("harnesses", {}).items():
            if other_id != resolved_id and isinstance(other_record, dict):
                other_record["role"] = ROLE_LOYAL_OPPOSITION
        record["role"] = ROLE_PRIME_BUILDER
        record["assigned_reason"] = "startup-self-correction-no-prime-builder"
        changed = True
    role = str(record.get("role") or ROLE_PRIME_BUILDER).lower()
    if role not in VALID_ROLES:
        role = ROLE_PRIME_BUILDER
        record["role"] = role
        changed = True
    if changed or (ensure_prime_on_startup and not path.is_file()):
        document["updated_at"] = _now_iso()
        write_role_assignments(project_root, document, assignment_path)
    return role, document, path


def set_harness_role(
    project_root: Path,
    role: str,
    *,
    harness_id: str | None = None,
    harness_name: str | None = None,
    assignment_path: Path | None = None,
) -> tuple[str, dict[str, Any], Path]:
    requested_role = str(role or "").strip().lower()
    if requested_role not in {ROLE_PRIME_BUILDER, ROLE_LOYAL_OPPOSITION}:
        raise ValueError(f"Unsupported next-session role: {role}")
    resolved_id = resolved_harness_id(project_root, harness_id=harness_id, harness_name=harness_name)
    if resolved_id is None:
        raise ValueError("Cannot set harness role without a durable harness ID.")

    document = load_role_assignments(project_root, assignment_path)
    record = _ensure_record(document, resolved_id, harness_name=harness_name)
    record["role"] = requested_role
    record["assigned_at"] = _now_iso()
    record["assigned_by"] = "harness-role-command"
    if requested_role == ROLE_PRIME_BUILDER:
        for other_id, other_record in document.get("harnesses", {}).items():
            if other_id != resolved_id and isinstance(other_record, dict):
                other_record["role"] = ROLE_LOYAL_OPPOSITION
    document["updated_at"] = _now_iso()
    path = write_role_assignments(project_root, document, assignment_path)
    return requested_role, document, path
