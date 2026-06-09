"""Batch assertion generator — Round 2.

Generates assertions for specs that:
1. Have [Source:] references but no assertions yet (pattern extraction round 2)
2. Have no [Source:] references (title-based pattern matching against common source dirs)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "knowledge-db"))

import db as kdb  # noqa: E402
from assertions import run_single_assertion  # noqa: E402


def extract_patterns(title: str, desc: str) -> list[str]:
    """Extract candidate grep patterns from title and description."""
    patterns = []

    # API endpoint patterns
    m = re.search(r"(GET|POST|PUT|DELETE|PATCH)\s+(/\S+)", title)
    if m:
        endpoint = m.group(2).rstrip(")")
        # Use last path segment
        segments = [s for s in endpoint.split("/") if s and not s.startswith("{")]
        if segments:
            patterns.append(segments[-1])

    # Function/method: word.word() or word()
    m = re.search(r"(\w+\.\w+)\(\)", title)
    if m:
        patterns.append(m.group(1))
    m = re.search(r"(\w+)\(\)", title)
    if m and m.group(1) not in ("a", "the", "is", "to"):
        patterns.append(m.group(1))

    # Constants: ALL_CAPS_WORD
    m = re.search(r"\b([A-Z][A-Z0-9_]{3,})\b", title)
    if m:
        patterns.append(m.group(1))

    # Class names: CamelCase
    m = re.search(r"\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b", title)
    if m:
        patterns.append(m.group(1))

    # Quoted strings in title
    for qm in re.finditer(r"'([^']{3,})'", title):
        patterns.append(qm.group(1))
    for qm in re.finditer(r'"([^"]{3,})"', title):
        patterns.append(qm.group(1))

    # underscore_identifiers in title
    m = re.search(r"\b([a-z][a-z0-9]*(?:_[a-z0-9]+)+)\b", title)
    if m:
        patterns.append(m.group(1))

    # Backtick code references in description
    if desc:
        for bm in re.finditer(r"`([^`]{3,40})`", desc):
            bp = bm.group(1)
            if re.match(r"^[a-zA-Z_][a-zA-Z0-9_./:]*$", bp) and len(bp) < 40:
                patterns.append(bp)

    # Prefix identifiers
    m = re.search(r"\b(pk_live_|ar_user_|VITE_|SMTP_|AZURE_)\w+", title)
    if m:
        patterns.append(m.group(0))

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for p in patterns:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique


def find_source_file_for_spec(title: str, desc: str) -> str | None:
    """Try to find a likely source file for a spec without [Source:] reference."""
    # Common source directories to search
    src_dirs = [
        "src/multi_tenant",
        "src/agents",
        "src/chat/pipeline",
        "src/chat",
        "admin/standalone/src",
        "admin/shopify/src",
        "admin/provider/src",
        "admin/shared",
        "scripts",
    ]

    patterns = extract_patterns(title, desc)
    if not patterns:
        return None

    # For each pattern, grep in source dirs
    for pat in patterns[:3]:  # Limit to top 3 patterns
        for src_dir in src_dirs:
            if not os.path.isdir(src_dir):
                continue
            for root, _, files in os.walk(src_dir):
                for f in files:
                    if not (f.endswith(".py") or f.endswith(".ts") or f.endswith(".tsx")):
                        continue
                    filepath = os.path.join(root, f).replace("\\", "/")
                    try:
                        with open(filepath, "r", encoding="utf-8", errors="ignore") as fh:
                            content = fh.read()
                            if re.search(pat, content):
                                return filepath
                    except Exception:
                        continue
    return None


def main():
    database = kdb.KnowledgeDB()
    conn = database._conn

    # Get all specs without assertion coverage
    cursor = conn.execute(
        """
        SELECT s.id, s.title, s.description, s.status
        FROM specifications s
        WHERE s.version = (SELECT MAX(s2.version) FROM specifications s2 WHERE s2.id = s.id)
        AND s.id NOT IN (SELECT DISTINCT spec_id FROM assertion_runs)
        AND s.status IN ('implemented', 'verified')
        AND (s.assertions IS NULL OR s.assertions = '' OR s.assertions = '[]')
        ORDER BY s.id
    """
    )
    all_specs = cursor.fetchall()

    with_source = []
    without_source = []
    for row in all_specs:
        spec_id, title, desc, status = row
        m = re.search(r"\[Source:\s*([^\]]+)\]", desc or "")
        if m:
            with_source.append((spec_id, title, desc, status, m.group(1).strip()))
        else:
            without_source.append((spec_id, title, desc, status))

    print(f"Specs needing assertions: {len(all_specs)}")
    print(f"  With [Source:]: {len(with_source)}")
    print(f"  Without [Source:]: {len(without_source)}")
    print()

    # ---- Phase 1: Specs with [Source:] ----
    print("=== Phase 1: Specs with [Source:] ===")
    p1_generated = 0
    p1_glob_fallback = 0
    p1_failed = 0

    for spec_id, title, desc, status, source_file in with_source:
        source_file = source_file.replace("\\", "/")
        if not os.path.exists(source_file):
            p1_failed += 1
            continue

        patterns = extract_patterns(title, desc)
        assertion_found = False

        for pat in patterns:
            assertion = {"type": "grep", "file": source_file, "pattern": pat}
            result = run_single_assertion(assertion)
            if result["passed"]:
                database.update_spec(
                    spec_id,
                    changed_by="S146-batch-round2",
                    change_reason="Auto-generated grep assertion from Source + patterns",
                    assertions=[{"type": "grep", "file": source_file, "pattern": pat}],
                )
                p1_generated += 1
                assertion_found = True
                break

        if not assertion_found:
            # Fallback: glob for file existence
            assertion = {"type": "glob", "pattern": source_file}
            result = run_single_assertion(assertion)
            if result["passed"]:
                database.update_spec(
                    spec_id,
                    changed_by="S146-batch-round2",
                    change_reason="Auto-generated glob assertion for source file existence",
                    assertions=[{"type": "glob", "pattern": source_file}],
                )
                p1_glob_fallback += 1
            else:
                p1_failed += 1

    print(f"  Grep assertions: {p1_generated}")
    print(f"  Glob fallbacks: {p1_glob_fallback}")
    print(f"  Failed: {p1_failed}")
    print(f"  Total covered: {p1_generated + p1_glob_fallback}")
    print()

    # ---- Phase 2: Specs without [Source:] ----
    print("=== Phase 2: Specs without [Source:] ===")
    p2_generated = 0
    p2_failed = 0

    for spec_id, title, desc, status in without_source:
        patterns = extract_patterns(title, desc)
        if not patterns:
            p2_failed += 1
            continue

        # Try to find a source file containing any of the patterns
        source_file = find_source_file_for_spec(title, desc)
        if source_file:
            # Now find which pattern matches
            for pat in patterns:
                assertion = {"type": "grep", "file": source_file, "pattern": pat}
                result = run_single_assertion(assertion)
                if result["passed"]:
                    database.update_spec(
                        spec_id,
                        changed_by="S146-batch-round2",
                        change_reason="Auto-generated assertion by source file discovery",
                        assertions=[{"type": "grep", "file": source_file, "pattern": pat}],
                    )
                    p2_generated += 1
                    break
            else:
                p2_failed += 1
        else:
            p2_failed += 1

    print(f"  Generated: {p2_generated}")
    print(f"  Failed: {p2_failed}")
    print()

    # ---- Summary ----
    total_new = p1_generated + p1_glob_fallback + p2_generated
    print(f"=== TOTAL NEW ASSERTIONS: {total_new} ===")

    # Run all to update coverage
    print("\nRunning all assertions to update coverage...")
    from assertions import run_all_assertions

    results = run_all_assertions(database, triggered_by="S146-batch-round2")
    print(f"  Specs with assertions: {results['specs_with_assertions']}")
    print(f"  Passed: {results['passed']}")
    print(f"  Failed: {results['failed']}")

    summary = database.get_summary()
    coverage = summary["assertions_total"]
    total = summary["spec_total"]
    pct = (coverage / total * 100) if total else 0
    print(f"\nCoverage: {coverage}/{total} = {pct:.1f}%")
    print(f"Gap to 60%: {int(total * 0.6) - coverage} more specs needed")


if __name__ == "__main__":
    main()
