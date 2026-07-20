"""Read-only LO review evidence gathering for gtkb-wi5185. Scratch; deletable."""

import sqlite3
import sys
from pathlib import Path

ROOT = Path(r"E:\GT-KB")
DB = ROOT / "groundtruth.db"

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row

# 1. Spec
try:
    r = con.execute(
        "SELECT id, version, status, title FROM current_specifications WHERE id = ?",
        ("SPEC-DISPATCHER-IDENTITY-RUNTIME-KIND-SEPARATION-001",),
    ).fetchone()
    print("=" * 72)
    print("SPEC meta:", dict(r) if r else "<MISSING>")
    r2 = con.execute(
        "SELECT content FROM current_specifications WHERE id = ?",
        ("SPEC-DISPATCHER-IDENTITY-RUNTIME-KIND-SEPARATION-001",),
    ).fetchone()
    print("SPEC CONTENT:\n")
    print(r2["content"] if r2 else "<missing>")
except Exception as exc:  # noqa: BLE001
    print("SPEC query error:", exc)

# 2. PAUTH
try:
    r = con.execute(
        "SELECT * FROM current_project_authorizations WHERE id = ?",
        ("PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5185-DISPATCHER-IDENTITY-RUNTIME-KIND-20260711",),
    ).fetchone()
    print("=" * 72)
    print("PAUTH")
    if r is None:
        print("  <PAUTH NOT FOUND>")
    else:
        for k in r.keys():
            print(f"  {k}: {r[k]!r}")
except Exception as exc:  # noqa: BLE001
    print("PAUTH query error:", exc)

# 3. DELIB
try:
    r = con.execute(
        "SELECT id, title, summary, source_type, outcome FROM current_deliberations WHERE id = ?",
        ("DELIB-202666084",),
    ).fetchone()
    print("=" * 72)
    print("DELIB-202666084")
    if r is None:
        print("  <DELIB NOT FOUND>")
    else:
        for k in r.keys():
            print(f"  {k}: {r[k]!r}")
except Exception as exc:  # noqa: BLE001
    print("DELIB query error:", exc)

# 4. Cited spec existence
cited = [
    "SPEC-DISPATCHER-IDENTITY-RUNTIME-KIND-SEPARATION-001",
    "DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001",
    "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",
    "GOV-FILE-BRIDGE-AUTHORITY-001",
    "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
    "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
    "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
    "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
    "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
    "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
]
print("=" * 72)
print("CITED SPEC EXISTENCE")
for sid in cited:
    row = con.execute("SELECT id, status FROM current_specifications WHERE id = ?", (sid,)).fetchone()
    print(f"  {sid}: {('FOUND ' + str(row['status'])) if row else 'MISSING'}")

con.close()

# 5. Harness projection record for H / alibaba
sys.path.insert(0, str(ROOT / "scripts"))
try:
    from harness_projection_reader import load_harness_projection

    proj = load_harness_projection(ROOT)
    print("=" * 72)
    print("HARNESS PROJECTION (id, harness_name, harness_type, role, status)")
    for rec in proj.get("harnesses", []):
        print(
            f"  id={rec.get('id')!r} name={rec.get('harness_name')!r} "
            f"type={rec.get('harness_type')!r} role={rec.get('role')!r} status={rec.get('status')!r}"
        )
except Exception as exc:  # noqa: BLE001
    print("projection error:", exc)
