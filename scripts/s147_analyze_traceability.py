#!/usr/bin/env python3
"""S147: Analyze test traceability gap."""
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "tools" / "knowledge-db" / "knowledge.db"
conn = sqlite3.connect(str(DB))
conn.row_factory = sqlite3.Row

# Counts
with_file = conn.execute(
    "SELECT COUNT(*) as c FROM current_tests WHERE test_file IS NOT NULL AND test_file <> ''"
).fetchone()["c"]
without_file = conn.execute(
    "SELECT COUNT(*) as c FROM current_tests WHERE test_file IS NULL OR test_file = ''"
).fetchone()["c"]
with_both = conn.execute(
    "SELECT COUNT(*) as c FROM current_tests WHERE test_file IS NOT NULL AND test_file <> '' AND test_function IS NOT NULL AND test_function <> ''"
).fetchone()["c"]
traced = conn.execute(
    "SELECT COUNT(*) as c FROM current_tests WHERE last_result IS NOT NULL"
).fetchone()["c"]

print(f"KB artifacts with test_file: {with_file}")
print(f"KB artifacts without test_file: {without_file}")
print(f"Total: {with_file + without_file}")
print(f"KB artifacts with both file+function: {with_both}")
print(f"Already traced (last_result set): {traced}")

# Distribution by category
rows = conn.execute("""
    SELECT CASE
        WHEN test_file LIKE 'tests/e2e_live/%' THEN 'e2e_live'
        WHEN test_file LIKE 'tests/unit/%' THEN 'unit'
        WHEN test_file LIKE 'tests/multi_tenant/%' THEN 'multi_tenant'
        WHEN test_file LIKE 'tests/agents/%' THEN 'agents'
        WHEN test_file LIKE 'tests/integrations/%' THEN 'integrations'
        WHEN test_file LIKE 'tests/widget/%' THEN 'widget'
        WHEN test_file IS NULL OR test_file = '' THEN '(no file)'
        ELSE 'other: ' || substr(test_file, 1, 30)
    END as category,
    COUNT(*) as c
    FROM current_tests
    GROUP BY category
    ORDER BY c DESC
""").fetchall()
print("\nDistribution by test_file category:")
for r in rows:
    print(f"  {r['category']:30s}: {r['c']}")

# Unmatched pytest tests sample — what file patterns aren't in KB?
import xml.etree.ElementTree as ET
xml_files = [
    "tests/results/unit-results.xml",
    "tests/results/multi_tenant-results.xml",
    "tests/results/agents-results.xml",
    "tests/results/integrations-results.xml",
    "tests/results/widget-results.xml",
]
xml_files_by_dir = {}
for xf in xml_files:
    p = Path(__file__).resolve().parent.parent / xf
    if not p.exists():
        continue
    tree = ET.parse(str(p))
    for tc in tree.getroot().iter("testcase"):
        cn = tc.get("classname", "")
        parts = cn.split(".")
        module_parts = []
        for i, part in enumerate(parts):
            if part and part[0].isupper() and i > 0:
                break
            module_parts.append(part)
        file_path = "/".join(module_parts) + ".py" if module_parts else ""
        name = tc.get("name", "")
        key = (file_path, name)
        # Check if in KB
        found = conn.execute(
            "SELECT COUNT(*) as c FROM current_tests WHERE test_file = ? AND test_function = ?",
            (file_path, name)
        ).fetchone()["c"]
        if found == 0:
            dir_key = "/".join(file_path.split("/")[:2]) if "/" in file_path else file_path
            xml_files_by_dir[dir_key] = xml_files_by_dir.get(dir_key, 0) + 1

print("\nUnmatched pytest tests by directory:")
for d, c in sorted(xml_files_by_dir.items(), key=lambda x: -x[1]):
    print(f"  {d:40s}: {c}")

conn.close()
