"""Analyze test artifact file paths to determine phase assignment rules."""

import sys, io, json, re
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, "tools/knowledge-db")
import db

kdb = db.KnowledgeDB()
conn = kdb._get_conn()

# Get all current test artifacts
rows = conn.execute(
    "SELECT t.id, t.title, t.spec_id, t.test_type, t.test_file, t.test_class, t.test_function "
    "FROM tests t "
    "INNER JOIN (SELECT id, MAX(version) as max_v FROM tests GROUP BY id) m "
    "ON t.id = m.id AND t.version = m.max_v "
    "ORDER BY t.id"
).fetchall()

tests = [dict(r) for r in rows]
print(f"Total test artifacts: {len(tests)}")

# Group by top-level directory
dir_counter = Counter()
for t in tests:
    f = t.get("test_file") or "unknown"
    parts = f.replace("\\", "/").split("/")
    if len(parts) >= 2:
        dir_counter[parts[1]] += 1  # tests/<subdir>/...
    else:
        dir_counter["root"] += 1

print("\n=== BY DIRECTORY (tests/<subdir>) ===")
for d, c in dir_counter.most_common():
    print(f"  {d}: {c}")

# Group by file
file_counter = Counter()
for t in tests:
    f = t.get("test_file") or "unknown"
    file_counter[f] += 1

print(f"\n=== UNIQUE TEST FILES: {len(file_counter)} ===")
for f, c in file_counter.most_common(30):
    print(f"  {c:4d}  {f}")

# Group by test_type
type_counter = Counter()
for t in tests:
    type_counter[t["test_type"]] += 1

print("\n=== BY TEST TYPE ===")
for tp, c in type_counter.most_common():
    print(f"  {tp}: {c}")

# Look for keyword patterns in file paths to identify phase-relevant tests
print("\n=== KEYWORD SCAN (file path patterns) ===")
keywords = {
    "security": [],
    "rate_limit": [],
    "tenant": [],
    "isolation": [],
    "regression": [],
    "url": [],
    "reachab": [],
    "load": [],
    "performance": [],
    "quality": [],
    "conversation": [],
    "ui": [],
    "e2e": [],
    "widget": [],
    "critical": [],
    "upgrade": [],
    "preflight": [],
    "pre_flight": [],
    "seed": [],
    "verification": [],
    "provision": [],
    "manual": [],
    "visual": [],
    "data_integrity": [],
    "backup": [],
    "resilience": [],
    "failover": [],
}
for t in tests:
    f = (t.get("test_file") or "").lower()
    title = (t.get("title") or "").lower()
    combined = f + " " + title
    for kw in keywords:
        if kw in combined:
            keywords[kw].append(t["id"])

for kw, ids in sorted(keywords.items()):
    if ids:
        print(f"  '{kw}': {len(ids)} tests (e.g. {ids[:3]})")

kdb.close()
