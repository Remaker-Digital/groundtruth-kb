#!/usr/bin/env python3
"""Dry-run-first Agent Red application-scope partition helper."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.application_scope import (
    AGENT_RED_APPLICATION_SCOPE,
    classify_application_scope,
    scope_path_violations,
)

DEFAULT_DB_PATH = Path("groundtruth.db")
DEFAULT_CHANGED_BY = "prime-builder/codex"
DEFAULT_CHANGE_REASON = "Agent Red readiness Phase 1.4 partition-in-place application_scope update"
MAX_MUTATIONS = 50


def _spec_paths(row: dict[str, Any]) -> list[str]:
    parsed = row.get("source_paths_parsed")
    if isinstance(parsed, list):
        return [path for path in parsed if isinstance(path, str)]
    return []


def _test_paths(row: dict[str, Any]) -> list[str]:
    test_file = row.get("test_file")
    return [test_file] if isinstance(test_file, str) and test_file.strip() else []


def _row_manifest(kind: str, row: dict[str, Any], paths: list[str]) -> dict[str, Any]:
    classification = classify_application_scope(str(row.get("id") or ""), row.get("title"), paths)
    current_scope = row.get("application_scope")
    violations = scope_path_violations(current_scope, paths)
    needs_scope_update = bool(
        classification.proposed_scope and classification.proposed_scope != (current_scope or None)
    )
    needs_repath = classification.proposed_paths != classification.normalized_paths
    action = "none"
    if violations:
        action = "violation"
    elif classification.ambiguous:
        action = "ambiguous"
    elif needs_scope_update or needs_repath:
        action = "update"

    return {
        "kind": kind,
        "id": row.get("id"),
        "version": row.get("version"),
        "title": row.get("title"),
        "current_scope": current_scope,
        "proposed_scope": classification.proposed_scope,
        "current_paths": classification.normalized_paths,
        "proposed_paths": classification.proposed_paths,
        "action": action,
        "reasons": classification.reasons,
        "violations": violations,
    }


def build_manifest(db: KnowledgeDB) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for spec in db.list_specs():
        rows.append(_row_manifest("spec", spec, _spec_paths(spec)))
    for test in db.list_tests():
        rows.append(_row_manifest("test", test, _test_paths(test)))

    actions = [row for row in rows if row["action"] == "update"]
    ambiguous = [row for row in rows if row["action"] == "ambiguous"]
    violations = [row for row in rows if row["action"] == "violation"]
    return {
        "schema_version": 1,
        "scope": AGENT_RED_APPLICATION_SCOPE,
        "max_mutations": MAX_MUTATIONS,
        "action_count": len(actions),
        "ambiguous_count": len(ambiguous),
        "violation_count": len(violations),
        "actions": actions,
        "ambiguous": ambiguous,
        "violations": violations,
    }


def apply_manifest(
    db: KnowledgeDB,
    manifest: dict[str, Any],
    *,
    changed_by: str,
    change_reason: str,
    max_mutations: int,
) -> list[dict[str, Any]]:
    actions = list(manifest["actions"])
    if len(actions) > max_mutations:
        raise SystemExit(f"refusing to mutate {len(actions)} rows; maximum per execute run is {max_mutations}")

    applied: list[dict[str, Any]] = []
    for action in actions:
        fields: dict[str, Any] = {"application_scope": action["proposed_scope"]}
        if action["proposed_paths"] != action["current_paths"]:
            if action["kind"] == "spec":
                fields["source_paths"] = action["proposed_paths"]
            elif action["kind"] == "test" and len(action["proposed_paths"]) == 1:
                fields["test_file"] = action["proposed_paths"][0]
        if action["kind"] == "spec":
            updated = db.update_spec(
                str(action["id"]),
                changed_by=changed_by,
                change_reason=change_reason,
                **fields,
            )
        elif action["kind"] == "test":
            updated = db.update_test(
                str(action["id"]),
                changed_by=changed_by,
                change_reason=change_reason,
                **fields,
            )
        else:  # pragma: no cover - impossible from build_manifest
            raise SystemExit(f"unknown action kind: {action['kind']}")
        applied.append(
            {
                "kind": action["kind"],
                "id": action["id"],
                "from_version": action["version"],
                "to_version": updated["version"] if updated else None,
                "fields": sorted(fields),
            }
        )
    return applied


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="Path to groundtruth.db")
    parser.add_argument("--execute", action="store_true", help="Apply up to 50 append-only row updates")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--changed-by", default=DEFAULT_CHANGED_BY)
    parser.add_argument("--change-reason", default=DEFAULT_CHANGE_REASON)
    parser.add_argument("--max-mutations", type=int, default=MAX_MUTATIONS)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    db = KnowledgeDB(db_path=args.db)
    try:
        manifest = build_manifest(db)
        applied: list[dict[str, Any]] = []
        if args.execute:
            applied = apply_manifest(
                db,
                manifest,
                changed_by=args.changed_by,
                change_reason=args.change_reason,
                max_mutations=args.max_mutations,
            )
            manifest = build_manifest(db)
        result = {
            "executed": bool(args.execute),
            "db_path": str(args.db),
            "applied": applied,
            "manifest": manifest,
        }
    finally:
        db.close()

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        mode = "execute" if args.execute else "dry-run"
        print(
            f"{mode}: {len(applied)} applied, {manifest['action_count']} remaining action(s), "
            f"{manifest['ambiguous_count']} ambiguous, {manifest['violation_count']} violation(s)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
