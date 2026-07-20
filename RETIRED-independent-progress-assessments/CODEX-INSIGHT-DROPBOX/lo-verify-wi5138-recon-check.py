import sqlite3

conn = sqlite3.connect("file:groundtruth.db?mode=ro", uri=True)
conn.row_factory = sqlite3.Row


def cols(table):
    return [r[1] for r in conn.execute(f'PRAGMA table_info("{table}")')]


print("work_items cols:", cols("work_items"))
print("project_work_item_memberships cols:", cols("project_work_item_memberships"))
print()

print("--- WI-5137 ---")
for r in conn.execute(
    "SELECT rowid, id, version, title, stage, project_name, depends_on_work_items, blocks_work_items, related_deliberation_ids FROM work_items WHERE id = 'WI-5137' ORDER BY version"
):
    print(dict(r))

print("--- WI-5138 ---")
for r in conn.execute(
    "SELECT rowid, id, version, title, stage, project_name, depends_on_work_items, blocks_work_items, related_deliberation_ids FROM work_items WHERE id = 'WI-5138' ORDER BY version"
):
    print(dict(r))

print("--- Gate-0 DELIBs ---")
for did in (
    "DELIB-20260710-GTKB-MODERNIZATION-GATE-0-AUTHORIZATION",
    "DELIB-20260710-GTKB-MODERNIZATION-GATE-0-HANDLE-MAP",
):
    for r in conn.execute(
        "SELECT id, version, outcome, source_type FROM deliberations WHERE id = ? ORDER BY version",
        (did,),
    ):
        print(dict(r))

print("--- GOV-CROSS-CUTTING spec ---")
for r in conn.execute(
    "SELECT id, version, status, type FROM specifications WHERE id = 'GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001' ORDER BY version"
):
    print(dict(r))

print("--- memberships (WI-513x) ---")
for r in conn.execute(
    "SELECT * FROM project_work_item_memberships WHERE id LIKE 'PWM-PROJECT-GTKB-PLATFORM-MODERNIZATION-WI-513%'"
):
    print(dict(r))
