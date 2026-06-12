#!/usr/bin/env python
"""FAB-11 stale Agent Red assertion remediation.

Repairs the false regression signal caused by Agent Red assertions that still
point at pre-isolation paths such as ``src/...``. Critical specs are rewritten to
``applications/Agent_Red/...`` when the moved file exists. Non-critical
requirement-era specs are retired as app-scoped history and their machine
assertions are cleared so future assertion sweeps stop counting them as live
platform failures.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from copy import deepcopy
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GTKB_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(GTKB_SRC) not in sys.path:
    sys.path.insert(0, str(GTKB_SRC))

from groundtruth_kb.assertions import run_all_assertions  # noqa: E402
from groundtruth_kb.db import KnowledgeDB  # noqa: E402

BRIDGE_ID = "gtkb-fab-11-regression-signal-revival"
CHANGED_BY = "prime-builder/codex"
OLD_PREFIXES = ("src/", "admin/", "widget/", "tests/", "docs-site/", "docs/", "branding/")
APP_PREFIX = "applications/Agent_Red/"
HISTORY_TAG = "fab11-app-scoped-history"
CRITICAL_SPEC_ID = "SPEC-1534"


@dataclass(frozen=True)
class Candidate:
    spec_id: str
    spec_version: int
    title: str
    status: str
    spec_type: str
    missing_paths: tuple[str, ...]
    action: str
    unresolved_paths: tuple[str, ...] = ()


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _load_json(value: str | None, fallback: Any) -> Any:
    if not value:
        return fallback
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return fallback


def _walk_values(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for nested in value.values():
            found.extend(_walk_values(nested))
    elif isinstance(value, list):
        for nested in value:
            found.extend(_walk_values(nested))
    elif isinstance(value, str):
        found.append(value)
    return found


def _extract_file_not_found_paths(results: Any) -> tuple[str, ...]:
    paths: set[str] = set()
    for text in _walk_values(results):
        marker = "File not found:"
        if marker not in text:
            continue
        tail = text.split(marker, 1)[1].strip()
        path = tail.splitlines()[0].strip().strip("'\"")
        if path.startswith(OLD_PREFIXES):
            paths.add(path)
    return tuple(sorted(paths))


def _is_critical(row: sqlite3.Row) -> bool:
    return row["id"] == CRITICAL_SPEC_ID or row["type"] == "protected_behavior" or row["status"] == "verified"


def _current_assertion_targets(assertions: Any) -> set[str]:
    targets: set[str] = set()
    if not isinstance(assertions, list):
        return targets
    for assertion in assertions:
        if not isinstance(assertion, dict):
            continue
        assertion_type = assertion.get("type")
        if assertion_type == "glob":
            value = assertion.get("pattern")
            if isinstance(value, str):
                targets.add(value)
            continue
        if assertion_type == "json_path":
            value = assertion.get("file")
            if isinstance(value, str):
                targets.add(value)
            continue
        for key in ("file", "file_pattern", "target", "path", "expected"):
            value = assertion.get(key)
            if isinstance(value, str):
                targets.add(value)
    return targets


def _find_candidates(db_path: Path, project_root: Path) -> list[Candidate]:
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            """WITH latest AS (
                   SELECT ar.*
                   FROM assertion_runs ar
                   INNER JOIN (
                       SELECT spec_id, MAX(rowid) AS max_rowid
                       FROM assertion_runs
                       GROUP BY spec_id
                   ) m ON ar.spec_id = m.spec_id AND ar.rowid = m.max_rowid
               )
               SELECT s.id, s.version, s.title, s.status, s.type, s.assertions, latest.results
               FROM current_specifications s
               INNER JOIN latest ON latest.spec_id = s.id
               WHERE latest.overall_passed = 0
               ORDER BY s.id"""
        ).fetchall()
    finally:
        conn.close()

    candidates: list[Candidate] = []
    for row in rows:
        missing = _extract_file_not_found_paths(_load_json(row["results"], []))
        if not missing:
            continue
        current_targets = _current_assertion_targets(_load_json(row["assertions"], []))
        active_missing = tuple(path for path in missing if path in current_targets)
        if not active_missing:
            continue
        if _is_critical(row):
            unresolved = tuple(p for p in active_missing if not (project_root / APP_PREFIX / p).exists())
            action = "unresolved" if unresolved else "rewrite"
        else:
            unresolved = ()
            action = "retire"
        candidates.append(
            Candidate(
                spec_id=row["id"],
                spec_version=row["version"],
                title=row["title"],
                status=row["status"],
                spec_type=row["type"],
                missing_paths=active_missing,
                action=action,
                unresolved_paths=unresolved,
            )
        )
    return candidates


def _rewrite_value(value: Any, missing_paths: set[str]) -> tuple[Any, bool]:
    if not isinstance(value, str) or value not in missing_paths:
        return value, False
    return f"{APP_PREFIX}{value}", True


def _rewrite_assertion(assertion: dict[str, Any], missing_paths: set[str]) -> tuple[dict[str, Any], bool]:
    updated = deepcopy(assertion)
    assertion_type = updated.get("type")
    changed = False

    if assertion_type == "glob":
        new_value, changed = _rewrite_value(updated.get("pattern"), missing_paths)
        if changed:
            updated["pattern"] = new_value
        return updated, changed

    if assertion_type == "json_path":
        new_value, changed = _rewrite_value(updated.get("file"), missing_paths)
        if changed:
            updated["file"] = new_value
        return updated, changed

    keys = ("file", "file_pattern", "target", "path", "expected")
    for key in keys:
        new_value, field_changed = _rewrite_value(updated.get(key), missing_paths)
        if field_changed:
            updated[key] = new_value
            changed = True
    return updated, changed


def rewrite_assertions(
    assertions: list[dict[str, Any]], missing_paths: tuple[str, ...]
) -> tuple[list[dict[str, Any]], int]:
    missing = set(missing_paths)
    rewritten: list[dict[str, Any]] = []
    changed_count = 0
    for assertion in assertions:
        updated, changed = _rewrite_assertion(assertion, missing)
        rewritten.append(updated)
        if changed:
            changed_count += 1
    return rewritten, changed_count


def _append_history_note(description: str | None, note: str) -> str:
    base = (description or "").rstrip()
    if note in base:
        return base
    return f"{base}\n\n{note}".strip()


def _append_tag(tags: Any, tag: str) -> list[str]:
    if isinstance(tags, str):
        parsed = _load_json(tags, [])
    else:
        parsed = tags or []
    result = [str(item) for item in parsed if str(item).strip()]
    if tag not in result:
        result.append(tag)
    return result


def _summary(candidates: list[Candidate]) -> dict[str, Any]:
    counts = {"rewrite": 0, "retire": 0, "unresolved": 0}
    for candidate in candidates:
        counts[candidate.action] += 1
    return {
        "bridge_id": BRIDGE_ID,
        "candidates": len(candidates),
        "rewrite_planned": counts["rewrite"],
        "retire_planned": counts["retire"],
        "unresolved": counts["unresolved"],
        "missing_paths": sum(len(candidate.missing_paths) for candidate in candidates),
        "unresolved_paths": sorted({p for c in candidates for p in c.unresolved_paths}),
    }


def apply_actions(
    db_path: Path,
    project_root: Path,
    *,
    max_actions: int | None = None,
    allow_unresolved: bool = False,
) -> dict[str, Any]:
    candidates = _find_candidates(db_path, project_root)
    if not allow_unresolved:
        unresolved = [c for c in candidates if c.action == "unresolved"]
        if unresolved:
            return {
                **_summary(candidates),
                "applied": False,
                "error": "critical_rewrite_paths_missing",
                "unresolved_specs": [asdict(c) for c in unresolved],
            }

    db = KnowledgeDB(db_path=db_path)
    applied = {"rewritten": 0, "retired": 0, "skipped": 0}
    acted = 0
    try:
        for candidate in candidates:
            if candidate.action == "unresolved":
                applied["skipped"] += 1
                continue
            if max_actions is not None and acted >= max_actions:
                break
            spec = db.get_spec(candidate.spec_id)
            if spec is None:
                applied["skipped"] += 1
                continue
            if candidate.action == "rewrite":
                assertions = spec.get("assertions_parsed") or []
                rewritten, changed_count = rewrite_assertions(assertions, candidate.missing_paths)
                if changed_count == 0:
                    applied["skipped"] += 1
                    continue
                db.update_spec(
                    candidate.spec_id,
                    changed_by=CHANGED_BY,
                    change_reason=f"{BRIDGE_ID}: rewrite Agent Red assertion paths to applications/Agent_Red",
                    assertions=rewritten,
                    validate_assertions=True,
                )
                applied["rewritten"] += 1
            elif candidate.action == "retire":
                note = (
                    "FAB-11 app-scoped history: retired stale Agent Red requirement-era "
                    "assertions after Agent Red isolation moved the referenced files under "
                    "applications/Agent_Red/."
                )
                db.update_spec(
                    candidate.spec_id,
                    changed_by=CHANGED_BY,
                    change_reason=f"{BRIDGE_ID}: retire stale Agent Red assertion history",
                    status="retired",
                    assertions=[],
                    description=_append_history_note(spec.get("description"), note),
                    tags=_append_tag(spec.get("tags_parsed"), HISTORY_TAG),
                    validate_assertions=False,
                )
                applied["retired"] += 1
            acted += 1
    finally:
        db.close()

    return {**_summary(candidates), **applied, "applied": True, "max_actions": max_actions}


def run_assertions(db_path: Path, project_root: Path, *, spec_id: str | None = None) -> dict[str, Any]:
    db = KnowledgeDB(db_path=db_path)
    try:
        summary = run_all_assertions(db, project_root, triggered_by=f"{BRIDGE_ID}:verification", spec_id=spec_id)
    finally:
        db.close()
    return {
        "total_specs": summary.get("total_specs"),
        "specs_with_assertions": summary.get("specs_with_assertions"),
        "passed": summary.get("passed"),
        "failed": summary.get("failed"),
        "skipped": summary.get("skipped"),
        "triggered_by": summary.get("triggered_by"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=PROJECT_ROOT / "groundtruth.db")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--max-actions", type=int)
    parser.add_argument("--allow-unresolved", action="store_true")
    parser.add_argument("--run-assertions", action="store_true")
    parser.add_argument("--spec-id")
    parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args()

    if args.run_assertions:
        result = run_assertions(args.db, args.project_root, spec_id=args.spec_id)
    elif args.apply:
        result = apply_actions(
            args.db,
            args.project_root,
            max_actions=args.max_actions,
            allow_unresolved=args.allow_unresolved,
        )
        if result.get("error") and not args.allow_unresolved:
            print(json.dumps(result, indent=2, sort_keys=True))
            return 2
    else:
        candidates = _find_candidates(args.db, args.project_root)
        result = {**_summary(candidates), "details": [asdict(c) for c in candidates]}

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
