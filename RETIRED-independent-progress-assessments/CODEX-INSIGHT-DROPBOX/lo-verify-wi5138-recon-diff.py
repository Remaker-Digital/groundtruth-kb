import sqlite3

TARGET = ".gtkb-state/modernization-db-reconstruction-001/groundtruth.db"
BASELINE = ".gtkb-state/modernization-db-reconstruction-001/baseline/groundtruth.db"
CURRENT = "groundtruth.db"

conn = sqlite3.connect(f"file:{TARGET}?mode=ro", uri=True)
conn.execute("ATTACH DATABASE ? AS cur", (f"file:{CURRENT}?mode=ro",))
conn.execute("ATTACH DATABASE ? AS base", (f"file:{BASELINE}?mode=ro",))


def cols(schema, table):
    return [r[1] for r in conn.execute(f'PRAGMA {schema}.table_info("{table}")')]


selections = {
    "projects": ("id IN ('PROJECT-GTKB-PLATFORM-MODERNIZATION')", ()),
    "work_items": ("id IN ('WI-5137','WI-5138')", ()),
    "deliberations": (
        "id IN ('DELIB-20260710-GTKB-MODERNIZATION-GATE-0-AUTHORIZATION',"
        "'DELIB-20260710-GTKB-MODERNIZATION-GATE-0-HANDLE-MAP',"
        "'DELIB-20260713-MODERNIZATION-BOUNDED-IMPLEMENTATION-AUTHORITY',"
        "'DELIB-20260713-MODERNIZATION-STRICT-BRIDGE-PROTOCOL')",
        (),
    ),
    "specifications": (
        "id IN ('GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001','DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001',"
        "'DCL-PROJECT-AUTHORIZATION-ENVELOPE-001','GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001',"
        "'PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001','GOV-FILE-BRIDGE-AUTHORITY-001',"
        "'DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001','DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001',"
        "'GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001','DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001',"
        "'DCL-PROJECT-DEPENDENCY-ORDERING-001','DCL-GIT-BRANCH-BINDING-PROMOTION-001',"
        "'ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001','DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001',"
        "'GOV-ARTIFACT-ORIENTED-GOVERNANCE-001','DCL-NO-ACTION-STATUS-SEMANTICS-001',"
        "'GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001')",
        (),
    ),
    "project_work_item_memberships": (
        "id IN ('PWM-PROJECT-GTKB-PLATFORM-MODERNIZATION-WI-5137','PWM-PROJECT-GTKB-PLATFORM-MODERNIZATION-WI-5138')",
        (),
    ),
    "project_authorizations": (
        "id = 'PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-WI-5138-TRUST-ENFORCEMENT-20260713'",
        (),
    ),
}

print("=== Row-exact comparison: target (main) vs live (cur) ===")
all_ok = True
for table, (where, params) in selections.items():
    c = cols("main", table)
    col_sql = ", ".join(f'"{c_}"' for c_ in c)
    target_rows = list(conn.execute(f"SELECT {col_sql} FROM main.\"{table}\" WHERE {where} ORDER BY rowid", params))
    live_rows = list(conn.execute(f"SELECT {col_sql} FROM cur.\"{table}\" WHERE {where} ORDER BY rowid", params))
    match = target_rows == live_rows
    all_ok = all_ok and match
    print(f"{table}: target_n={len(target_rows)} live_n={len(live_rows)} exact_match={match}")
    if not match:
        print("  MISMATCH DETECTED")

print()
print("=== Tables NOT in the selection dict: verify byte-identical to baseline (row counts) ===")
all_tables = [
    r[0]
    for r in conn.execute(
        "SELECT name FROM main.sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )
]
for t in all_tables:
    if t in selections:
        continue
    main_n = conn.execute(f'SELECT COUNT(*) FROM main."{t}"').fetchone()[0]
    base_n = conn.execute(f'SELECT COUNT(*) FROM base."{t}"').fetchone()[0]
    if main_n != base_n:
        print(f"UNEXPECTED COUNT DELTA outside selection dict: {t} main={main_n} base={base_n}")
        all_ok = False
print("No unexpected count deltas outside the 6 selected tables." if all_ok else "SEE ABOVE — deltas found")

print()
print("=== PAUTH row identity check ===")
row = conn.execute(
    "SELECT rowid, id, version, status FROM main.project_authorizations "
    "WHERE id = 'PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-WI-5138-TRUST-ENFORCEMENT-20260713'"
).fetchone()
print("target PAUTH row:", row)

print()
print("=== integrity_check on target ===")
print(conn.execute("PRAGMA main.integrity_check").fetchone()[0])

print()
print("OVERALL:", "PASS" if all_ok else "FAIL")
