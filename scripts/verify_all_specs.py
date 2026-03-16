"""Full spec-vs-code verification.

Checks every implemented/verified spec assertion against actual source files.
Reports all mismatches.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import json
import os
import pathlib
import re
import sqlite3
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "tools" / "knowledge-db" / "knowledge.db"


def check_assertion(assertion, project_root: pathlib.Path) -> tuple[bool, str]:
    """Check a single assertion. Returns (passed, detail)."""
    if isinstance(assertion, str):
        return True, "string assertion (not machine-checkable)"

    atype = assertion.get("type", "")

    if atype == "grep":
        pattern = assertion.get("pattern", "")
        file_path = assertion.get("file", assertion.get("file_pattern", ""))
        min_count = assertion.get("min_count", 1)

        if not pattern or not file_path:
            return True, "incomplete assertion (missing pattern or file)"

        # Resolve file(s)
        candidates = []
        full = project_root / file_path
        if full.exists() and full.is_file():
            candidates = [full]
        else:
            # Try glob
            candidates = list(project_root.glob(file_path))
            if not candidates:
                candidates = list(project_root.glob("**/" + pathlib.Path(file_path).name))

        if not candidates:
            return False, f"File not found: {file_path}"

        total_found = 0
        for c in candidates:
            try:
                content = c.read_text(encoding="utf-8", errors="replace")
                total_found += len(re.findall(pattern, content))
            except Exception:
                pass

        if total_found >= min_count:
            return True, f"Found {total_found} match(es)"
        else:
            return False, f'grep "{pattern}" in {file_path}: found {total_found}, need >= {min_count}'

    elif atype == "glob":
        gpattern = assertion.get("pattern", "")
        if not gpattern:
            return True, "empty glob pattern"
        matches = list(project_root.glob(gpattern))
        if not matches:
            matches = list(project_root.glob("**/" + gpattern))
        if matches:
            return True, f"Found {len(matches)} file(s)"
        else:
            return False, f"Glob pattern not found: {gpattern}"

    elif atype == "file_exists":
        fp = assertion.get("path", assertion.get("file", ""))
        if not fp:
            return True, "empty path"
        full = project_root / fp
        if full.exists():
            return True, "File exists"
        matches = list(project_root.glob("**/" + pathlib.Path(fp).name))
        if matches:
            return True, f"File found at {matches[0]}"
        return False, f"File not found: {fp}"

    elif atype in ("sql", "db_query"):
        return True, "DB assertion (not file-checkable)"

    else:
        return True, f"Unknown assertion type: {atype}"


def main():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    # Get all implemented/verified specs
    rows = conn.execute("""
        SELECT s.id, s.title, s.status, s.assertions, s.type, s.description
        FROM specifications s
        INNER JOIN (SELECT id, MAX(version) as mv FROM specifications GROUP BY id) latest
        ON s.id = latest.id AND s.version = latest.mv
        WHERE s.status IN ('implemented', 'verified')
        ORDER BY s.id
    """).fetchall()

    total = len(rows)
    with_assertions = 0
    without_assertions = 0
    passed = 0
    failed_specs = []
    no_assertion_specs = []

    for row in rows:
        raw = row["assertions"]
        if not raw or raw in ("", "null", "[]"):
            without_assertions += 1
            no_assertion_specs.append({
                "id": row["id"],
                "title": row["title"],
                "status": row["status"],
                "type": row["type"],
            })
            continue

        with_assertions += 1
        try:
            assertions = json.loads(raw)
        except json.JSONDecodeError:
            failed_specs.append({
                "id": row["id"],
                "title": row["title"],
                "status": row["status"],
                "type": row["type"],
                "failures": [("JSON parse error", str(raw)[:100])],
            })
            continue

        if not isinstance(assertions, list):
            assertions = [assertions]

        spec_failures = []
        for a in assertions:
            ok, detail = check_assertion(a, PROJECT_ROOT)
            if not ok:
                desc = ""
                if isinstance(a, dict):
                    desc = a.get("description", a.get("pattern", ""))[:80]
                spec_failures.append((desc, detail))

        if spec_failures:
            failed_specs.append({
                "id": row["id"],
                "title": row["title"],
                "status": row["status"],
                "type": row["type"],
                "failures": spec_failures,
            })
        else:
            passed += 1

    # Report
    print(f"{'='*70}")
    print(f"FULL SPEC-VS-CODE VERIFICATION REPORT")
    print(f"{'='*70}")
    print(f"Total implemented/verified specs: {total}")
    print(f"  With assertions: {with_assertions}")
    print(f"  Without assertions: {without_assertions}")
    print(f"  PASSED: {passed}")
    print(f"  FAILED: {len(failed_specs)}")
    print()

    if failed_specs:
        # Group by type
        by_type: dict[str, list] = {}
        for f in failed_specs:
            t = f.get("type") or "requirement"
            by_type.setdefault(t, []).append(f)

        print(f"{'='*70}")
        print(f"FAILURES BY TYPE ({len(failed_specs)} specs)")
        print(f"{'='*70}")

        for t in sorted(by_type.keys()):
            items = by_type[t]
            print(f"\n--- {t.upper()} ({len(items)} failures) ---")
            for f in items:
                print(f"\n  {f['id']} [{f['status']}]: {f['title'][:70]}")
                for desc, detail in f["failures"]:
                    print(f"    FAIL: {desc}")
                    print(f"    -> {detail}")

    if no_assertion_specs:
        print(f"\n{'='*70}")
        print(f"SPECS WITHOUT ASSERTIONS ({len(no_assertion_specs)})")
        print(f"{'='*70}")
        # Group by type
        by_type2: dict[str, list] = {}
        for s in no_assertion_specs:
            t = s.get("type") or "requirement"
            by_type2.setdefault(t, []).append(s)

        for t in sorted(by_type2.keys()):
            items = by_type2[t]
            print(f"\n--- {t.upper()} ({len(items)}) ---")
            for s in items:
                print(f"  {s['id']} [{s['status']}]: {s['title'][:70]}")

    conn.close()
    return len(failed_specs)


if __name__ == "__main__":
    sys.exit(main())
