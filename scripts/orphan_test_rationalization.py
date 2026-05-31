"""Rationalize POR 16.D residual orphan tests.

This script consumes the verified POR 16.D Phase 2 classification artifact and
adds a disposition suggestion for each remaining Class B/C/D orphan test. It is
read-only against MemBase: the only write is the JSONL inventory output.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

EXPECTED_POST_PHASE2_ORPHANS = 2189
SOURCE_BRIDGE_THREAD = "gtkb-por-step-16-d-orphan-test-rationalization"
DEFAULT_CLASSIFICATION_PATH = Path(".groundtruth") / "por-16d-phase2-classification.json"
DEFAULT_DB_PATH = Path("groundtruth.db")
DEFAULT_OUTPUT_DIR = Path(".gtkb-state") / "orphan-test-rationalization"
RESIDUAL_BUCKETS = ("B_file_bucket", "C_fully_orphaned_file", "D_null_or_missing")

NUMERIC_SPEC_ID_RE = re.compile(r"(?<![A-Z0-9])(?:SPEC|GOV|ADR|DCL|PB)[-_]\d+(?!\d)", re.IGNORECASE)
SPEC_ID_RE = re.compile(
    r"(?<![A-Z0-9])(?:SPEC|GOV|ADR|DCL|PB)[-_][A-Z0-9]+(?:[-_][A-Z0-9]+)*(?![A-Z0-9])",
    re.IGNORECASE,
)
RETIRE_TOKENS = ("obsolete", "dead", "unused", "abandoned", "retire", "remove")
MIGRATE_TOKENS = ("deprecated", "legacy", "superseded", "replacement", "old_")
TEST_FIELDS = (
    "test_id",
    "title",
    "test_type",
    "test_file",
    "test_class",
    "test_function",
    "last_result",
    "last_executed_at",
)


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _resolve_path(project_root: Path, path: Path) -> Path:
    return path if path.is_absolute() else project_root / path


def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any]:
    if row is None:
        return {}
    data = dict(row)
    if "id" in data and "test_id" not in data:
        data["test_id"] = data["id"]
    return data


def _text_blob(record: dict[str, Any]) -> str:
    parts = []
    for key in ("test_id", "title", "test_file", "test_class", "test_function", "reason"):
        value = record.get(key)
        if value is not None:
            parts.append(str(value))
    return " ".join(parts)


def _normalize_spec_id(value: str) -> str:
    prefix, _, suffix = value.partition("-") if "-" in value else value.partition("_")
    return f"{prefix.upper()}-{suffix.replace('_', '-').upper()}"


def _find_spec_id(text: str) -> str | None:
    numeric_match = NUMERIC_SPEC_ID_RE.search(text)
    if numeric_match:
        return _normalize_spec_id(numeric_match.group(0))
    spec_match = SPEC_ID_RE.search(text)
    if spec_match:
        return _normalize_spec_id(spec_match.group(0))
    return None


def load_classification(path: Path) -> dict[str, Any]:
    """Load and validate the verified POR 16.D Phase 2 classification artifact."""
    if not path.exists():
        raise FileNotFoundError(
            "Missing POR 16.D Phase 2 classification artifact: "
            f"{path}. Restore or regenerate .groundtruth/por-16d-phase2-classification.json "
            "before running rationalization."
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    missing = [bucket for bucket in RESIDUAL_BUCKETS if bucket not in data]
    if missing:
        raise ValueError(f"Phase 2 classification artifact is missing required buckets: {', '.join(missing)}")
    return data


def classify_orphan(record: dict[str, Any]) -> dict[str, str | None]:
    """Suggest adopt/migrate/retire/review for one orphan test record."""
    text = _text_blob(record)
    normalized = text.lower()
    spec_id = _find_spec_id(text)
    if spec_id:
        return {
            "disposition": "adopt",
            "suggested_spec_id": spec_id,
            "rationale": "test metadata names a candidate specification id",
        }
    if any(token in normalized for token in RETIRE_TOKENS):
        return {
            "disposition": "retire",
            "suggested_spec_id": None,
            "rationale": "test metadata indicates obsolete or removable coverage",
        }
    if any(token in normalized for token in MIGRATE_TOKENS):
        return {
            "disposition": "migrate",
            "suggested_spec_id": None,
            "rationale": "test metadata indicates legacy or deprecated coverage",
        }
    if record.get("source_class") == "D_null_or_missing" or not record.get("test_file"):
        return {
            "disposition": "retire",
            "suggested_spec_id": None,
            "rationale": "test lacks enough file/function metadata for governed adoption",
        }
    return {
        "disposition": "review",
        "suggested_spec_id": None,
        "rationale": "no deterministic adoption, migration, or retirement signal found",
    }


def connect_read_only(db_path: Path) -> sqlite3.Connection:
    """Open the SQLite DB in read-only mode when possible."""
    uri = f"file:{db_path.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def count_orphan_tests(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM current_tests
        WHERE spec_id IS NULL OR TRIM(spec_id) = ''
        """
    ).fetchone()
    return int(row["count"])


def fetch_test_by_id(conn: sqlite3.Connection, test_id: str | None) -> dict[str, Any]:
    if not test_id:
        return {}
    row = conn.execute(
        """
        SELECT id, title, test_type, test_file, test_class, test_function, last_result, last_executed_at
        FROM current_tests
        WHERE id = ?
        """,
        (test_id,),
    ).fetchone()
    return _row_to_dict(row)


def fetch_orphan_tests_for_file(conn: sqlite3.Connection, test_file: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT id, title, test_type, test_file, test_class, test_function, last_result, last_executed_at
        FROM current_tests
        WHERE test_file = ?
          AND (spec_id IS NULL OR TRIM(spec_id) = '')
        ORDER BY id
        """,
        (test_file,),
    ).fetchall()
    return [_row_to_dict(row) for row in rows]


def _merge_test_record(source_class: str, phase2_record: dict[str, Any], db_record: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {"record_type": "inventory", "source_class": source_class}
    if "reason" in phase2_record:
        merged["phase2_reason"] = phase2_record["reason"]
    for field in TEST_FIELDS:
        value = phase2_record.get(field)
        if value is None or value == "":
            value = db_record.get(field)
        merged[field] = value
    if not merged.get("test_id") and db_record.get("id"):
        merged["test_id"] = db_record["id"]
    classification = classify_orphan(merged)
    merged.update(classification)
    return merged


def _add_entry(
    entries: list[dict[str, Any]],
    seen_ids: set[str],
    source_class: str,
    phase2_record: dict[str, Any],
    db_record: dict[str, Any],
) -> bool:
    entry = _merge_test_record(source_class, phase2_record, db_record)
    test_id = entry.get("test_id")
    if test_id and str(test_id) in seen_ids:
        return False
    if test_id:
        seen_ids.add(str(test_id))
    entries.append(entry)
    return True


def build_inventory(classification: dict[str, Any], db_path: Path) -> dict[str, Any]:
    """Build the inventory data structure without mutating MemBase."""
    conn = connect_read_only(db_path)
    try:
        observed_orphans = count_orphan_tests(conn)
        entries: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        duplicate_count = 0

        for item in classification.get("B_file_bucket", []):
            db_record = fetch_test_by_id(conn, item.get("test_id"))
            if not _add_entry(entries, seen_ids, "B_file_bucket", item, db_record):
                duplicate_count += 1

        for bucket in classification.get("C_fully_orphaned_file", []):
            test_file = bucket.get("test_file")
            rows = fetch_orphan_tests_for_file(conn, test_file) if test_file else []
            if rows:
                for row in rows:
                    if not _add_entry(entries, seen_ids, "C_fully_orphaned_file", bucket, row):
                        duplicate_count += 1
                continue
            for test_id in bucket.get("sample_test_ids", []):
                fallback_record = {"test_id": test_id, "test_file": test_file}
                db_record = fetch_test_by_id(conn, test_id)
                if not _add_entry(entries, seen_ids, "C_fully_orphaned_file", fallback_record, db_record):
                    duplicate_count += 1

        for item in classification.get("D_null_or_missing", []):
            db_record = fetch_test_by_id(conn, item.get("test_id"))
            if not _add_entry(entries, seen_ids, "D_null_or_missing", item, db_record):
                duplicate_count += 1
    finally:
        conn.close()

    source_counts = Counter(str(entry["source_class"]) for entry in entries)
    disposition_counts = Counter(str(entry["disposition"]) for entry in entries)
    return {
        "meta": {
            "record_type": "_meta",
            "schema_version": 1,
            "generated_at": _utc_now(),
            "source_bridge_thread": SOURCE_BRIDGE_THREAD,
            "expected_post_phase2_orphans": EXPECTED_POST_PHASE2_ORPHANS,
            "observed_orphan_tests": observed_orphans,
            "inventory_entries": len(entries),
            "duplicate_phase2_entries_skipped": duplicate_count,
            "phase2_phase": classification.get("phase"),
            "phase2_counts": classification.get("counts", {}),
            "source_counts": dict(sorted(source_counts.items())),
            "disposition_counts": dict(sorted(disposition_counts.items())),
        },
        "entries": entries,
    }


def write_inventory(output_path: Path, inventory: dict[str, Any]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(inventory["meta"], sort_keys=True) + "\n")
        for entry in inventory["entries"]:
            handle.write(json.dumps(entry, sort_keys=True) + "\n")


def default_output_path(project_root: Path) -> Path:
    return project_root / DEFAULT_OUTPUT_DIR / f"{datetime.now(UTC).date().isoformat()}.jsonl"


def generate_inventory(
    *,
    project_root: Path,
    classification_path: Path | None = None,
    db_path: Path | None = None,
    output_path: Path | None = None,
) -> dict[str, Any]:
    root = project_root.resolve()
    resolved_classification = _resolve_path(root, classification_path or DEFAULT_CLASSIFICATION_PATH)
    resolved_db = _resolve_path(root, db_path or DEFAULT_DB_PATH)
    resolved_output = _resolve_path(root, output_path) if output_path else default_output_path(root)

    classification = load_classification(resolved_classification)
    inventory = build_inventory(classification, resolved_db)
    inventory["meta"]["classification_path"] = str(resolved_classification)
    inventory["meta"]["db_path"] = str(resolved_db)
    inventory["meta"]["output_path"] = str(resolved_output)
    write_inventory(resolved_output, inventory)
    return inventory


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--classification", type=Path, default=None)
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--json", action="store_true", help="emit a machine-readable summary")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        inventory = generate_inventory(
            project_root=args.project_root,
            classification_path=args.classification,
            db_path=args.db,
            output_path=args.out,
        )
    except (FileNotFoundError, ValueError, sqlite3.Error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    summary = {
        "output_path": inventory["meta"]["output_path"],
        "expected_post_phase2_orphans": inventory["meta"]["expected_post_phase2_orphans"],
        "observed_orphan_tests": inventory["meta"]["observed_orphan_tests"],
        "inventory_entries": inventory["meta"]["inventory_entries"],
        "disposition_counts": inventory["meta"]["disposition_counts"],
    }
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"Wrote orphan-test rationalization inventory: {summary['output_path']}")
        print(
            "Observed orphan tests: "
            f"{summary['observed_orphan_tests']} "
            f"(expected post-Phase-2 baseline: {summary['expected_post_phase2_orphans']})"
        )
        print(f"Inventory entries: {summary['inventory_entries']}")
        print(f"Disposition counts: {json.dumps(summary['disposition_counts'], sort_keys=True)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
