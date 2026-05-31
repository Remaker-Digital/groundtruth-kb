"""POR Step 16.E exit verification gate."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path("groundtruth.db")
MAX_UNTESTED_SPECS = 6
MAX_ORPHAN_TESTS = 100


def _resolve_db(project_root: Path, db_path: Path | None) -> Path:
    path = db_path or DEFAULT_DB_PATH
    return path if path.is_absolute() else project_root / path


def _connect_read_only(db_path: Path) -> sqlite3.Connection:
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


def count_implemented_or_verified_specs_without_tests(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM current_specifications s
        WHERE LOWER(COALESCE(s.status, '')) IN ('implemented', 'verified')
          AND NOT EXISTS (
              SELECT 1
              FROM current_tests t
              WHERE t.spec_id = s.id
          )
        """
    ).fetchone()
    return int(row["count"])


def evaluate_exit_thresholds(
    db_path: Path,
    *,
    max_untested_specs: int = MAX_UNTESTED_SPECS,
    max_orphan_tests: int = MAX_ORPHAN_TESTS,
) -> dict[str, Any]:
    conn = _connect_read_only(db_path)
    try:
        orphan_tests = count_orphan_tests(conn)
        untested_specs = count_implemented_or_verified_specs_without_tests(conn)
    finally:
        conn.close()

    checks = {
        "orphan_tests": {
            "observed": orphan_tests,
            "threshold": max_orphan_tests,
            "passed": orphan_tests <= max_orphan_tests,
        },
        "implemented_or_verified_specs_without_tests": {
            "observed": untested_specs,
            "threshold": max_untested_specs,
            "passed": untested_specs <= max_untested_specs,
        },
    }
    return {
        "passed": all(check["passed"] for check in checks.values()),
        "db_path": str(db_path),
        "checks": checks,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--max-untested-specs", type=int, default=MAX_UNTESTED_SPECS)
    parser.add_argument("--max-orphan-tests", type=int, default=MAX_ORPHAN_TESTS)
    parser.add_argument("--json", action="store_true", help="emit a machine-readable result")
    return parser


def _print_text_report(result: dict[str, Any]) -> None:
    status = "PASS" if result["passed"] else "FAIL"
    print(f"POR Step 16.E exit verification: {status}")
    for name, check in result["checks"].items():
        check_status = "PASS" if check["passed"] else "FAIL"
        print(f"- {name}: {check['observed']} <= {check['threshold']} [{check_status}]")


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    db_path = _resolve_db(args.project_root.resolve(), args.db)
    try:
        result = evaluate_exit_thresholds(
            db_path,
            max_untested_specs=args.max_untested_specs,
            max_orphan_tests=args.max_orphan_tests,
        )
    except sqlite3.Error as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        _print_text_report(result)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
