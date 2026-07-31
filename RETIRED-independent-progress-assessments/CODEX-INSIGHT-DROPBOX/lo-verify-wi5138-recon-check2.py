import sqlite3

conn = sqlite3.connect("file:groundtruth.db?mode=ro", uri=True)
conn.row_factory = sqlite3.Row


def cols(table):
    return [r[1] for r in conn.execute(f'PRAGMA table_info("{table}")')]


print("deliberations cols:", cols("deliberations"))
print()

for did in (
    "DELIB-20260710-GTKB-MODERNIZATION-GATE-0-AUTHORIZATION",
    "DELIB-20260710-GTKB-MODERNIZATION-GATE-0-HANDLE-MAP",
    "DELIB-20260713-MODERNIZATION-BOUNDED-IMPLEMENTATION-AUTHORITY",
    "DELIB-20260713-MODERNIZATION-STRICT-BRIDGE-PROTOCOL",
):
    for r in conn.execute(
        "SELECT id, version, content FROM deliberations WHERE id = ? ORDER BY version", (did,)
    ):
        content = r["content"] or ""
        has_cross_cutting = "GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001" in content
        has_wi5137 = "WI-5137" in content
        print(f"{did} v{r['version']}: len={len(content)} cites_cross_cutting={has_cross_cutting} cites_WI5137={has_wi5137}")

print()
print("--- project row ---")
pcols = cols("projects")
print("projects cols:", pcols)
for r in conn.execute(
    "SELECT * FROM projects WHERE id = 'PROJECT-GTKB-PLATFORM-MODERNIZATION' ORDER BY version"
):
    d = dict(r)
    print({k: (v[:200] if isinstance(v, str) and len(v) > 200 else v) for k, v in d.items()})
