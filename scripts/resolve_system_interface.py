#!/usr/bin/env python3
"""Resolve GT-KB system/interface terms against the governed map."""

from __future__ import annotations

import argparse
import json
import tomllib
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = PROJECT_ROOT / "config" / "agent-control" / "system-interface-map.toml"
REQUIRED_SYSTEM_FIELDS = (
    "id",
    "canonical_name",
    "accepted_aliases",
    "discouraged_aliases",
    "forbidden_aliases",
    "concept_vs_artifact",
    "authoritative_source",
    "generated_or_authoritative",
    "read_method",
    "mutation_method",
    "role_permissions",
    "startup_visibility",
    "dashboard_visibility",
    "harness_caveats",
    "verification_method",
    "lifecycle_state",
    "related_specs",
    "related_deliberations",
)
REQUIRED_SEED_IDS = {
    "backlog",
    "work-item",
    "membase",
    "deliberation-archive",
    "memory-md",
    "canonical-glossary",
    "operating-model",
    "file-bridge",
    "bridge-queue",
    "bridge-dispatch",
    "monitor-gt-kb-bridge-codex-thread",
    "smart-poller",
    "retired-os-poller",
    "dashboard",
    "release-readiness",
    "release-gate",
    "doctor-check",
    "startup-disclosure",
    "session-focus",
    "work-subject",
    "role-assignment-record",
    "harness-identity-record",
    "skill",
    "hook",
    "plugin-app-capability",
    "mcp-server",
    "resource-alias-registry",
}
BACKLOG_REQUIRED_TOKENS = ("current_work_items", "work_items", "memory/work_list.md", "bridge/INDEX.md", "dashboard")


def load_map(path: Path = MAP_PATH) -> dict[str, Any]:
    """Load the governed system/interface map."""
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    if not isinstance(data, dict):
        raise ValueError("system map root must be a TOML table")
    return data


def system_rows(system_map: dict[str, Any]) -> list[dict[str, Any]]:
    rows = system_map.get("systems", [])
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def validate_map(system_map: dict[str, Any], *, project_root: Path = PROJECT_ROOT) -> list[str]:
    """Validate schema, seed coverage, alias uniqueness, and the backlog case."""
    errors: list[str] = []
    if system_map.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    rows = system_rows(system_map)
    if not rows:
        errors.append("at least one [[systems]] row is required")
        return errors

    seen_ids: set[str] = set()
    alias_owner: dict[str, str] = {}
    for index, row in enumerate(rows, start=1):
        row_id = str(row.get("id") or f"row-{index}")
        if row_id in seen_ids:
            errors.append(f"{row_id}: duplicate system id")
        seen_ids.add(row_id)
        for field in REQUIRED_SYSTEM_FIELDS:
            if field not in row:
                errors.append(f"{row_id}: missing required field {field}")
        aliases = row.get("accepted_aliases")
        if not isinstance(aliases, list) or not aliases or not all(isinstance(alias, str) for alias in aliases):
            errors.append(f"{row_id}: accepted_aliases must be a non-empty string list")
        else:
            for alias in aliases:
                normalized = _normalize(alias)
                previous = alias_owner.setdefault(normalized, row_id)
                if previous != row_id:
                    errors.append(f"alias {alias!r} maps to both {previous} and {row_id}")
        for list_field in ("discouraged_aliases", "forbidden_aliases", "related_specs", "related_deliberations"):
            if list_field in row and not isinstance(row[list_field], list):
                errors.append(f"{row_id}: {list_field} must be a list")
        source = str(row.get("authoritative_source") or "")
        if _looks_like_project_path(source) and not (project_root / source).exists():
            errors.append(f"{row_id}: authoritative_source does not exist: {source}")

    missing_seed_ids = sorted(REQUIRED_SEED_IDS - seen_ids)
    if missing_seed_ids:
        errors.append("missing required seed systems: " + ", ".join(missing_seed_ids))

    backlog = next((row for row in rows if row.get("id") == "backlog"), None)
    if backlog is None:
        errors.append("backlog reconciliation row is missing")
    else:
        combined = " ".join(str(backlog.get(field) or "") for field in REQUIRED_SYSTEM_FIELDS)
        for token in BACKLOG_REQUIRED_TOKENS:
            if token not in combined:
                errors.append(f"backlog row must mention {token}")
    return errors


def resolve_term(term: str, *, system_map: dict[str, Any] | None = None) -> dict[str, Any]:
    """Resolve an owner-facing system term to one map entry."""
    system_map = system_map or load_map()
    normalized = _normalize(term)
    matches = [row for row in system_rows(system_map) if normalized in _match_keys(row)]
    if not matches:
        return {"status": "not_found", "term": term, "message": "No system map row matched.", "candidates": []}
    if len(matches) > 1:
        return {
            "status": "ambiguous",
            "term": term,
            "message": "Term matched multiple system map rows.",
            "candidates": [_public_row(row) for row in matches],
        }
    return {"status": "resolved", "term": term, "message": "Term resolved.", "system": _public_row(matches[0])}


def compact_status(system_map: dict[str, Any] | None = None, *, project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Return startup/dashboard-safe map status."""
    system_map = system_map or load_map()
    errors = validate_map(system_map, project_root=project_root)
    rows = system_rows(system_map)
    companion = project_root / str(system_map.get("human_companion") or "")
    backlog = next((row for row in rows if row.get("id") == "backlog"), {})
    return {
        "status": "pass" if not errors else "fail",
        "schema_version": system_map.get("schema_version"),
        "systems": len(rows),
        "human_companion": str(companion),
        "human_companion_exists": companion.exists(),
        "first_reconciliation_case": "backlog",
        "backlog_authoritative_source": backlog.get("authoritative_source"),
        "errors": errors,
    }


def _public_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row.get("id"),
        "canonical_name": row.get("canonical_name"),
        "authoritative_source": row.get("authoritative_source"),
        "generated_or_authoritative": row.get("generated_or_authoritative"),
        "startup_visibility": row.get("startup_visibility"),
        "dashboard_visibility": row.get("dashboard_visibility"),
        "lifecycle_state": row.get("lifecycle_state"),
    }


def _match_keys(row: dict[str, Any]) -> set[str]:
    keys = {_normalize(str(row.get("id") or "")), _normalize(str(row.get("canonical_name") or ""))}
    keys.update(_normalize(alias) for alias in row.get("accepted_aliases", []) if isinstance(alias, str))
    keys.discard("")
    return keys


def _looks_like_project_path(source: str) -> bool:
    if (
        not source
        or ":" in source
        or " and " in source
        or source.startswith("session ")
        or source.startswith("AGENTS.md and")
    ):
        return False
    return (
        any(
            source.startswith(prefix)
            for prefix in (
                ".claude/",
                ".codex/",
                ".githooks/",
                "bridge/",
                "config/",
                "docs/",
                "groundtruth-kb/",
                "harness-state/",
                "independent-progress-assessments/",
                "memory/",
                "scripts/",
            )
        )
        or source == "groundtruth.db"
    )


def _normalize(value: str) -> str:
    return " ".join(value.strip().lower().split())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve GT-KB system/interface terms.")
    parser.add_argument("term", nargs="?", help="System/interface term to resolve.")
    parser.add_argument("--map", dest="map_path", type=Path, default=MAP_PATH, help="System map TOML path.")
    parser.add_argument("--status", action="store_true", help="Emit compact map status.")
    parser.add_argument("--json", dest="json_output", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)

    try:
        system_map = load_map(args.map_path)
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        result: dict[str, Any] = {"status": "error", "message": str(exc), "map": str(args.map_path)}
        _emit(result, json_output=args.json_output)
        return 1

    if args.status:
        result = compact_status(system_map)
        _emit(result, json_output=args.json_output)
        return 0 if result["status"] == "pass" else 1

    errors = validate_map(system_map)
    if errors:
        result = {"status": "invalid_map", "errors": errors}
        _emit(result, json_output=args.json_output)
        return 1

    if not args.term:
        parser.error("term is required unless --status is used")
    result = resolve_term(args.term, system_map=system_map)
    _emit(result, json_output=args.json_output)
    return 0 if result["status"] == "resolved" else 1


def _emit(result: dict[str, Any], *, json_output: bool) -> None:
    if json_output:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    print(f"{result.get('status')}: {result.get('message', '')}")
    if "system" in result:
        system = result["system"]
        print(f"  {system.get('id')} -> {system.get('authoritative_source')}")
    for candidate in result.get("candidates", []):
        print(f"  candidate: {candidate.get('id')} -> {candidate.get('authoritative_source')}")
    for error in result.get("errors", []):
        print(f"  error: {error}")


if __name__ == "__main__":
    raise SystemExit(main())
