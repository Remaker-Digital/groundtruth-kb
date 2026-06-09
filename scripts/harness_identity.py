"""Persistent workstation identity for GT-KB harness installations."""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    from scripts.harness_projection_reader import load_harness_projection
except ImportError:  # pragma: no cover - direct script execution path
    from harness_projection_reader import (  # type: ignore[no-redef]
        load_harness_projection,
    )

HARNESS_IDENTITIES_RELATIVE_PATH = Path("harness-state") / "harness-identities.json"
DEFAULT_HARNESS_IDS = {
    "codex": "A",
    "claude": "B",
}


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_harness_name(value: str | None) -> str | None:
    normalized = str(value or "").strip().lower().replace("_", "-")
    return normalized or None


def normalize_harness_id(value: str | None) -> str | None:
    normalized = str(value or "").strip().upper()
    return normalized if re.fullmatch(r"[A-Z][A-Z0-9-]*", normalized) else None


def harness_identities_path(project_root: Path, override: Path | None = None) -> Path:
    if override is not None:
        return override.expanduser().resolve()
    env_override = os.environ.get("GTKB_HARNESS_IDENTITIES_PATH")
    if env_override:
        return Path(env_override).expanduser().resolve()
    return project_root.resolve() / HARNESS_IDENTITIES_RELATIVE_PATH


def _empty_document() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "source_of_truth": "GT-KB harness installation identities",
        "description": (
            "Maps host-local harness installation names to durable unique IDs. "
            "IDs must not change after assignment except by explicit owner-requested identity change."
        ),
        "updated_at": _now_iso(),
        "harnesses": {},
    }


def _normalize_document(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raw = {}
    document = _empty_document()
    document.update({key: value for key, value in raw.items() if key != "harnesses"})
    harnesses = raw.get("harnesses")
    normalized_harnesses: dict[str, dict[str, Any]] = {}
    if isinstance(harnesses, dict):
        for raw_name, raw_record in harnesses.items():
            harness_name = normalize_harness_name(str(raw_name))
            if not harness_name or not isinstance(raw_record, dict):
                continue
            harness_id = normalize_harness_id(str(raw_record.get("id") or ""))
            if not harness_id:
                continue
            normalized_harnesses[harness_name] = dict(raw_record)
            normalized_harnesses[harness_name]["id"] = harness_id
    document["harnesses"] = normalized_harnesses
    return document


def load_harness_identities(project_root: Path, identity_path: Path | None = None) -> dict[str, Any]:
    """Load harness identities from the registry projection (WI-3342 IP-3).

    Migrated from reading ``harness-state/harness-identities.json`` directly to
    reading the DB-backed registry projection
    (``harness-state/harness-registry.json``) via
    ``scripts/harness_projection_reader.load_harness_projection``. The
    ``identity_path`` parameter is retained for signature compatibility
    (positional callers) and for the writer path
    (``write_harness_identities``); readers resolve identity state from the
    projection. Fail-soft: a missing or malformed projection yields an empty
    document, never an exception.
    """
    _ = identity_path  # retained for signature + writer-path compatibility
    document = _empty_document()
    harnesses: dict[str, dict[str, Any]] = {}
    for record in load_harness_projection(project_root).get("harnesses", []):
        if not isinstance(record, dict):
            continue
        harness_name = normalize_harness_name(str(record.get("harness_name") or ""))
        harness_id = normalize_harness_id(str(record.get("id") or ""))
        if not harness_name or not harness_id:
            continue
        harnesses[harness_name] = {"id": harness_id}
    document["harnesses"] = harnesses
    return document


def write_harness_identities(project_root: Path, document: dict[str, Any], identity_path: Path | None = None) -> Path:
    path = harness_identities_path(project_root, identity_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp.{os.getpid()}")
    tmp.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return path


def _decode_harness_json_field(raw: Any) -> Any:
    """Decode a harnesses-table JSON-text column value (role / invocation_surfaces).

    ``KnowledgeDB.get_harness`` returns these columns as raw JSON text (or
    ``None``). Decoding is required before the value is round-tripped back
    through ``insert_harness``, which JSON-encodes its inputs."""
    if raw is None or raw == "":
        return None
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None
    return raw


def _mirror_identities_to_registry(project_root: Path, document: dict[str, Any]) -> None:
    """Write harness identities to the DB ``harnesses`` registry table and
    regenerate the hot-path projection.

    WI-3342 IP-5: this is the AUTHORITATIVE identity write — the transitional
    ``harness-identities.json`` write was removed, so the DB-backed registry
    and its projection are the sole authoritative identity surface.

    For each identity whose ``harness_name`` differs from its current DB row, an
    append-only ``insert_harness`` version corrects the name (every other field,
    including the role set, forwarded from the current row). A harness with no
    current DB row, or whose current row carries no role set, is skipped —
    first-version creation belongs to the registry seed / new-harness
    registration flow, not this update mirror.

    SessionStart-safe: this module is stdlib-only, so the ``groundtruth_kb``
    import is function-local. A missing ``groundtruth.db`` (e.g. a DB-less test
    fixture) or an unavailable ``groundtruth_kb`` package is a graceful no-op;
    any other DB error is raised, so a registry-write failure surfaces rather
    than silently losing the identity write."""
    db_path = project_root / "groundtruth.db"
    if not db_path.is_file():
        return
    try:
        from groundtruth_kb.db import KnowledgeDB
        from groundtruth_kb.harness_projection import generate_harness_projection
    except Exception:
        return
    harnesses = document.get("harnesses")
    if not isinstance(harnesses, dict):
        return
    try:
        db = KnowledgeDB(db_path=db_path)
        changed = False
        for harness_name, record in harnesses.items():
            if not isinstance(record, dict):
                continue
            harness_id = normalize_harness_id(str(record.get("id") or ""))
            if not harness_id:
                continue
            current = db.get_harness(harness_id)
            if current is None:
                continue
            if str(current.get("harness_name") or "") == str(harness_name):
                continue
            current_role = _decode_harness_json_field(current.get("role"))
            if not isinstance(current_role, list) or not current_role:
                continue
            db.insert_harness(
                id=harness_id,
                harness_name=str(harness_name),
                harness_type=str(current.get("harness_type") or harness_name),
                role=[str(r) for r in current_role],
                changed_by="harness-identity-write",
                change_reason="WI-3342 harness identity write",
                status=str(current.get("status") or "registered"),
                reviewer_precedence=current.get("reviewer_precedence"),
                invocation_surfaces=_decode_harness_json_field(current.get("invocation_surfaces")),
                capabilities_ref=current.get("capabilities_ref"),
            )
            changed = True
        if changed:
            generate_harness_projection(db, project_root)
    except Exception as exc:
        # WI-3342 IP-5: the DB-backed registry is the sole authoritative
        # identity surface (the transitional harness-identities.json write was
        # removed), so a registry-write failure must surface rather than
        # silently lose the identity write.
        raise RuntimeError(f"harness registry identity write failed: {exc}") from exc


def validate_unique_harness_ids(document: dict[str, Any]) -> list[str]:
    seen: dict[str, str] = {}
    errors: list[str] = []
    harnesses = document.get("harnesses")
    if not isinstance(harnesses, dict):
        return errors
    for harness_name, record in harnesses.items():
        if not isinstance(record, dict):
            continue
        harness_id = normalize_harness_id(str(record.get("id") or ""))
        if not harness_id:
            continue
        prior = seen.get(harness_id)
        if prior and prior != harness_name:
            errors.append(f"harness ID {harness_id} is assigned to both {prior} and {harness_name}")
        seen[harness_id] = str(harness_name)
    return errors


def _used_ids(document: dict[str, Any]) -> set[str]:
    harnesses = document.get("harnesses")
    if not isinstance(harnesses, dict):
        return set()
    return {
        harness_id
        for record in harnesses.values()
        if isinstance(record, dict)
        for harness_id in [normalize_harness_id(str(record.get("id") or ""))]
        if harness_id
    }


def _next_available_id(document: dict[str, Any]) -> str:
    used = _used_ids(document)
    for codepoint in range(ord("A"), ord("Z") + 1):
        candidate = chr(codepoint)
        if candidate not in used:
            return candidate
    suffix = 1
    while True:
        candidate = f"H{suffix}"
        if candidate not in used:
            return candidate
        suffix += 1


def _assert_unique(document: dict[str, Any]) -> None:
    errors = validate_unique_harness_ids(document)
    if errors:
        raise ValueError("; ".join(errors))


def resolve_harness_identity(
    project_root: Path,
    *,
    harness_name: str | None = None,
    asserted_harness_id: str | None = None,
    identity_path: Path | None = None,
    bootstrap_missing: bool = True,
) -> tuple[str | None, dict[str, Any], Path]:
    """Resolve a durable harness ID from the persistent identity artifact.

    ``asserted_harness_id`` is a consistency check. Once an identity is recorded,
    a different asserted value raises instead of changing the artifact.
    """

    path = harness_identities_path(project_root, identity_path)
    document = load_harness_identities(project_root, identity_path)
    _assert_unique(document)

    normalized_name = normalize_harness_name(harness_name) or normalize_harness_name(
        os.environ.get("GTKB_HARNESS_NAME")
    )
    asserted_id = normalize_harness_id(asserted_harness_id) or normalize_harness_id(os.environ.get("GTKB_HARNESS_ID"))
    if not normalized_name:
        return asserted_id, document, path

    harnesses = document.setdefault("harnesses", {})
    record = harnesses.get(normalized_name)
    if isinstance(record, dict):
        existing_id = normalize_harness_id(str(record.get("id") or ""))
        if existing_id:
            if asserted_id and asserted_id != existing_id:
                raise ValueError(
                    f"harness {normalized_name} is persistently identified as {existing_id}, "
                    f"but startup asserted {asserted_id}; use an explicit owner-requested identity change operation"
                )
            return existing_id, document, path

    if not bootstrap_missing:
        return asserted_id, document, path

    used = _used_ids(document)
    assigned_id = asserted_id or DEFAULT_HARNESS_IDS.get(normalized_name)
    if assigned_id and assigned_id in used:
        assigned_id = None
    if not assigned_id:
        assigned_id = _next_available_id(document)
    harnesses[normalized_name] = {
        "id": assigned_id,
        "assigned_at": _now_iso(),
        "assigned_by": "initial-installation-bootstrap",
    }
    document["updated_at"] = _now_iso()
    # WI-3342 IP-5: the transitional harness-identities.json write is removed;
    # _mirror_identities_to_registry is the authoritative identity write. It
    # skips harnesses with no current DB row, so a genuinely-new harness
    # bootstrapped here is not persisted by this path — new-harness registry
    # registration is a separate flow.
    _mirror_identities_to_registry(project_root, document)
    return assigned_id, document, path


def resolved_harness_id(
    project_root: Path | None = None,
    *,
    harness_id: str | None = None,
    harness_name: str | None = None,
    identity_path: Path | None = None,
    bootstrap_missing: bool = True,
) -> str | None:
    root = (project_root or Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())).resolve()
    resolved_id, _document, _path = resolve_harness_identity(
        root,
        harness_name=harness_name,
        asserted_harness_id=harness_id,
        identity_path=identity_path,
        bootstrap_missing=bootstrap_missing,
    )
    return resolved_id


def set_harness_identity(
    project_root: Path,
    *,
    harness_name: str,
    harness_id: str,
    owner_requested: bool = False,
    identity_path: Path | None = None,
) -> tuple[str, dict[str, Any], Path]:
    if not owner_requested:
        raise ValueError("Harness identity changes require an explicit owner-requested operation.")
    normalized_name = normalize_harness_name(harness_name)
    normalized_id = normalize_harness_id(harness_id)
    if not normalized_name or not normalized_id:
        raise ValueError("Harness identity change requires a valid harness name and ID.")

    document = load_harness_identities(project_root, identity_path)
    _assert_unique(document)
    harnesses = document.setdefault("harnesses", {})
    for other_name, record in harnesses.items():
        if other_name == normalized_name or not isinstance(record, dict):
            continue
        if normalize_harness_id(str(record.get("id") or "")) == normalized_id:
            raise ValueError(f"harness ID {normalized_id} is already assigned to {other_name}")

    record = harnesses.setdefault(normalized_name, {})
    existing_id = normalize_harness_id(str(record.get("id") or ""))
    if existing_id and existing_id != normalized_id:
        record["previous_id"] = existing_id
    record["id"] = normalized_id
    record["assigned_at"] = _now_iso()
    record["assigned_by"] = "explicit-owner-requested-identity-change"
    document["updated_at"] = _now_iso()
    # WI-3342 IP-5: the transitional harness-identities.json write is removed;
    # _mirror_identities_to_registry below is the authoritative identity write.
    # ``path`` is resolved (not written) to preserve the return contract.
    path = harness_identities_path(project_root, identity_path)
    _mirror_identities_to_registry(project_root, document)
    return normalized_id, document, path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    subparsers = parser.add_subparsers(dest="command", required=True)

    resolve_parser = subparsers.add_parser("resolve")
    resolve_parser.add_argument("--harness-name", required=True)
    resolve_parser.add_argument("--harness-id", default=None)

    set_parser = subparsers.add_parser("set")
    set_parser.add_argument("--harness-name", required=True)
    set_parser.add_argument("--harness-id", required=True)
    set_parser.add_argument("--owner-requested", action="store_true")

    args = parser.parse_args(argv)
    project_root = args.project_root.resolve()
    if args.command == "resolve":
        harness_id = resolved_harness_id(
            project_root,
            harness_name=args.harness_name,
            harness_id=args.harness_id,
            bootstrap_missing=True,
        )
        print(harness_id or "")
        return 0
    if args.command == "set":
        harness_id, _document, _path = set_harness_identity(
            project_root,
            harness_name=args.harness_name,
            harness_id=args.harness_id,
            owner_requested=args.owner_requested,
        )
        print(harness_id)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
