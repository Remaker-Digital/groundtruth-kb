"""Export/import the MemBase records that CI tests require.

This script bridges the gap created by the 2026-04-24 owner decision (commit
``23a54af3``) that untracked ``groundtruth.db``. The Slice 8.6 -003 GO'd plan
plus the S330 Phase 1.5 owner decision (Option A) requires CI to seed the
records governance_adoption tests assert before pytest runs.

Two modes:

* ``--export``: read the listed spec/deliberation IDs from the local
  ``groundtruth.db`` and write a JSON fixture at
  ``tests/fixtures/ci_membase_seed.json``. Run this locally when records
  change; commit the fixture so CI sees the update.
* ``--seed``: read the JSON fixture and insert the records into the target
  database (default: repo-root ``groundtruth.db``). Idempotent — skips
  records that already exist at the same version.

The list of IDs is auto-derived from the failing tests' ``db.get_spec(...)``
and ``db.get_deliberation(...)`` calls so the fixture stays in sync with
test expectations.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO_ROOT / "groundtruth.db"
DEFAULT_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "ci_membase_seed.json"
TEST_FILES = (
    REPO_ROOT / "tests" / "scripts" / "test_groundtruth_governance_adoption.py",
    REPO_ROOT / "tests" / "scripts" / "test_standing_backlog_harvest.py",
)

SPEC_ID_PREFIXES = ("GOV-", "PB-", "ADR-", "DCL-", "SPEC-", "REQ-")


def _ensure_groundtruth_kb_on_path() -> None:
    src = REPO_ROOT / "groundtruth-kb" / "src"
    if src.is_dir() and str(src) not in sys.path:
        sys.path.insert(0, str(src))


def discover_required_ids(test_files: tuple[Path, ...] = TEST_FILES) -> tuple[list[str], list[str]]:
    """Scan test files for db.get_spec / db.get_deliberation calls.

    Returns (spec_ids, deliberation_ids), each sorted and deduplicated. Scans
    every file in ``test_files`` so a single fixture covers multiple test
    modules (governance_adoption + standing_backlog_harvest, currently).
    """
    ids_in_calls: set[str] = set()
    ids_in_dicts: set[str] = set()
    delib_ids: set[str] = set()
    for test_file in test_files:
        if not test_file.is_file():
            continue
        content = test_file.read_text(encoding="utf-8")
        ids_in_calls.update(re.findall(r'(?:get_spec|get_deliberation)\("([A-Z][A-Z0-9_-]+)"\)', content))
        ids_in_dicts.update(re.findall(r'"([A-Z]+-[A-Z0-9-]+-\d+)"\s*:', content))
        delib_ids.update(re.findall(r'"(DELIB-[A-Z0-9-]+)"', content))
    all_ids = ids_in_calls | ids_in_dicts | delib_ids
    spec_ids = sorted(i for i in all_ids if i.startswith(SPEC_ID_PREFIXES))
    deliberation_ids = sorted(i for i in delib_ids)
    return spec_ids, deliberation_ids


def export_records(db_path: Path, fixture_path: Path) -> dict[str, int]:
    _ensure_groundtruth_kb_on_path()
    from groundtruth_kb.db import KnowledgeDB

    spec_ids, deliberation_ids = discover_required_ids()
    db = KnowledgeDB(db_path)
    try:
        specs = []
        missing_specs = []
        for sid in spec_ids:
            spec = db.get_spec(sid)
            if spec is None:
                missing_specs.append(sid)
                continue
            specs.append(_clean_spec(spec))

        deliberations = []
        missing_delibs = []
        for did in deliberation_ids:
            delib = db.get_deliberation(did)
            if delib is None:
                missing_delibs.append(did)
                continue
            deliberations.append(_clean_delib(delib))
    finally:
        db.close()

    if missing_specs or missing_delibs:
        print(
            f"WARN: missing in source db — specs: {missing_specs}; deliberations: {missing_delibs}",
            file=sys.stderr,
        )

    fixture = {
        "schema_version": 1,
        "source_db": str(db_path.resolve()),
        "specifications": specs,
        "deliberations": deliberations,
    }
    fixture_path.parent.mkdir(parents=True, exist_ok=True)
    fixture_path.write_text(json.dumps(fixture, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"specs_written": len(specs), "deliberations_written": len(deliberations)}


def _clean_spec(spec: dict[str, Any]) -> dict[str, Any]:
    keep = {
        "id",
        "title",
        "description",
        "priority",
        "scope",
        "section",
        "handle",
        "status",
        "type",
        "authority",
        "provisional_until",
        "testability",
    }
    out: dict[str, Any] = {k: spec.get(k) for k in keep if spec.get(k) is not None}
    if spec.get("tags"):
        try:
            out["tags"] = json.loads(spec["tags"]) if isinstance(spec["tags"], str) else spec["tags"]
        except (TypeError, json.JSONDecodeError):
            pass
    if spec.get("assertions"):
        try:
            out["assertions"] = (
                json.loads(spec["assertions"]) if isinstance(spec["assertions"], str) else spec["assertions"]
            )
        except (TypeError, json.JSONDecodeError):
            pass
    if spec.get("constraints"):
        try:
            out["constraints"] = (
                json.loads(spec["constraints"]) if isinstance(spec["constraints"], str) else spec["constraints"]
            )
        except (TypeError, json.JSONDecodeError):
            pass
    if spec.get("affected_by"):
        try:
            out["affected_by"] = (
                json.loads(spec["affected_by"]) if isinstance(spec["affected_by"], str) else spec["affected_by"]
            )
        except (TypeError, json.JSONDecodeError):
            pass
    if spec.get("source_paths"):
        try:
            out["source_paths"] = (
                json.loads(spec["source_paths"]) if isinstance(spec["source_paths"], str) else spec["source_paths"]
            )
        except (TypeError, json.JSONDecodeError):
            pass
    return out


def _clean_delib(delib: dict[str, Any]) -> dict[str, Any]:
    keep = {
        "id",
        "title",
        "summary",
        "content",
        "source_type",
        "source_ref",
        "spec_id",
        "work_item_id",
        "outcome",
        "session_id",
        "sensitivity",
        "origin_project",
        "origin_repo",
    }
    out: dict[str, Any] = {k: delib.get(k) for k in keep if delib.get(k) is not None}
    if delib.get("participants"):
        try:
            out["participants"] = (
                json.loads(delib["participants"])
                if isinstance(delib["participants"], str)
                else delib["participants"]
            )
        except (TypeError, json.JSONDecodeError):
            pass
    return out


def seed_records(db_path: Path, fixture_path: Path) -> dict[str, int]:
    _ensure_groundtruth_kb_on_path()
    from groundtruth_kb.db import KnowledgeDB

    if not fixture_path.is_file():
        raise FileNotFoundError(f"Fixture not found: {fixture_path}")

    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    specs = fixture.get("specifications", [])
    deliberations = fixture.get("deliberations", [])

    db = KnowledgeDB(db_path)
    inserted = {"specs_inserted": 0, "specs_skipped": 0, "delibs_inserted": 0, "delibs_skipped": 0}
    try:
        for spec in specs:
            sid = spec["id"]
            if db.get_spec(sid) is not None:
                inserted["specs_skipped"] += 1
                continue
            kwargs: dict[str, Any] = {
                "id": sid,
                "title": spec["title"],
                "status": spec.get("status", "specified"),
                "changed_by": "ci-seed/membase_ci_seed.py",
                "change_reason": "CI seed of records required by governance_adoption tests "
                "(per DELIB-S330-SLICE-8-6-PHASE-1-5-CI-DB-SEED-CHOICE Option A)",
                "description": spec.get("description"),
                "priority": spec.get("priority"),
                "scope": spec.get("scope"),
                "section": spec.get("section"),
                "handle": spec.get("handle"),
                "tags": spec.get("tags"),
                "assertions": spec.get("assertions"),
                "type": spec.get("type", "requirement"),
                "validate_assertions": False,
                "provisional_until": spec.get("provisional_until"),
                "constraints": spec.get("constraints"),
                "affected_by": spec.get("affected_by"),
                "testability": spec.get("testability"),
                "source_paths": spec.get("source_paths"),
            }
            if spec.get("authority") is not None:
                kwargs["authority"] = spec["authority"]
            db.insert_spec(**{k: v for k, v in kwargs.items() if v is not None or k == "validate_assertions"})
            inserted["specs_inserted"] += 1

        for delib in deliberations:
            did = delib["id"]
            if db.get_deliberation(did) is not None:
                inserted["delibs_skipped"] += 1
                continue
            db.insert_deliberation(
                id=did,
                source_type=delib.get("source_type", "owner_conversation"),
                title=delib["title"],
                summary=delib.get("summary", ""),
                content=delib.get("content", ""),
                changed_by="ci-seed/membase_ci_seed.py",
                change_reason="CI seed of records required by governance_adoption tests "
                "(per DELIB-S330-SLICE-8-6-PHASE-1-5-CI-DB-SEED-CHOICE Option A)",
                spec_id=delib.get("spec_id"),
                work_item_id=delib.get("work_item_id"),
                source_ref=delib.get("source_ref"),
                participants=delib.get("participants"),
                outcome=delib.get("outcome"),
                session_id=delib.get("session_id"),
                sensitivity=delib.get("sensitivity", "normal"),
                origin_project=delib.get("origin_project"),
                origin_repo=delib.get("origin_repo"),
            )
            inserted["delibs_inserted"] += 1
    finally:
        db.close()
    return inserted


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    p_export = sub.add_parser("export", help="Dump records from local DB to fixture JSON")
    p_export.add_argument("--db", type=Path, default=DEFAULT_DB)
    p_export.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    p_seed = sub.add_parser("seed", help="Insert records from fixture JSON into target DB")
    p_seed.add_argument("--db", type=Path, default=DEFAULT_DB)
    p_seed.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    args = parser.parse_args(argv)

    if args.mode == "export":
        result = export_records(args.db, args.fixture)
        print(f"Exported {result['specs_written']} specs + {result['deliberations_written']} deliberations to {args.fixture}")
        return 0
    if args.mode == "seed":
        result = seed_records(args.db, args.fixture)
        print(
            f"Seeded {result['specs_inserted']} new specs ({result['specs_skipped']} skipped), "
            f"{result['delibs_inserted']} new deliberations ({result['delibs_skipped']} skipped) into {args.db}"
        )
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
