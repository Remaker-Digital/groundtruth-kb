#!/usr/bin/env python3
"""S151: Analyze specified specs with passing assertions for status promotion.

(C) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
import sqlite3, json, os

db_path = os.path.join(os.path.dirname(__file__), '..', 'tools', 'knowledge-db', 'knowledge.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Get all specified specs with assertions
c.execute("""
    SELECT s.id, s.title, s.assertions, s.type
    FROM specifications s
    INNER JOIN (SELECT id, MAX(version) as mv FROM specifications GROUP BY id) l
        ON s.id = l.id AND s.version = l.mv
    WHERE s.status = 'specified'
    AND s.assertions IS NOT NULL AND s.assertions != '[]'
    ORDER BY s.id
""")
specs = c.fetchall()

# Check which have passing assertion runs
passing_specs = []
for s in specs:
    c.execute("""
        SELECT overall_passed FROM assertion_runs
        WHERE spec_id = ? ORDER BY rowid DESC LIMIT 1
    """, (s["id"],))
    ar = c.fetchone()
    if ar and ar["overall_passed"] == 1:
        passing_specs.append(s)

print(f"Total specified specs with assertions: {len(specs)}")
print(f"With PASSING assertions: {len(passing_specs)}")

# Breakdown by type
types = {}
for s in passing_specs:
    t = s["type"] or "requirement"
    types[t] = types.get(t, 0) + 1
print(f"\nBy type:")
for t, cnt in sorted(types.items(), key=lambda x: -x[1]):
    print(f"  {t}: {cnt}")

# Sample per type
print(f"\nSamples:")
for s in passing_specs[:15]:
    a = json.loads(s["assertions"]) if s["assertions"] else []
    f = a[0].get("file","") if a else ""
    pat = a[0].get("pattern","") if a else ""
    print(f"  {s['id']} [{s['type']}]: \"{pat}\" in {f}")
    print(f"    {s['title'][:80]}")

# Are ANY of these specs about features NOT yet implemented?
# Check if assertion file exists and pattern matches
import re
verified_impl = 0
questionable = []
for s in passing_specs:
    a = json.loads(s["assertions"]) if s["assertions"] else []
    if not a:
        continue
    f = a[0].get("file", "")
    pat = a[0].get("pattern", "")
    target = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', f))
    if os.path.exists(target):
        try:
            with open(target, 'r', encoding='utf-8', errors='replace') as fp:
                content = fp.read()
            if re.search(pat, content):
                verified_impl += 1
            else:
                questionable.append((s["id"], f, pat, "pattern not found"))
        except Exception as e:
            questionable.append((s["id"], f, pat, str(e)))
    else:
        questionable.append((s["id"], f, pat, "file not found"))

print(f"\nFile+pattern verification:")
print(f"  Verified (code exists): {verified_impl}")
print(f"  Questionable: {len(questionable)}")
for q in questionable[:10]:
    print(f"    {q[0]}: {q[3]} — {q[1]} '{q[2]}'")

conn.close()
