import sqlite3

LIVE = "groundtruth.db"
TARGET = ".gtkb-state/modernization-db-reconstruction-001/groundtruth.db"


def report(label, path):
    print(f"=== {label} ({path}) ===")
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row

    print("-- deliberations.work_item_id for the two owner DELIBs --")
    for r in conn.execute(
        "SELECT id, version, work_item_id, spec_id FROM deliberations "
        "WHERE id IN ('DELIB-20260713-MODERNIZATION-STRICT-BRIDGE-PROTOCOL',"
        "'DELIB-20260713-MODERNIZATION-BOUNDED-IMPLEMENTATION-AUTHORITY') ORDER BY id, version"
    ):
        print(dict(r))

    print("-- work_items WI-5138 source_spec_id / source_owner_directive --")
    for r in conn.execute(
        "SELECT id, version, source_spec_id, source_owner_directive, source_deliberation_query, "
        "related_deliberation_ids, related_spec_ids_at_creation FROM work_items WHERE id = 'WI-5138' ORDER BY version"
    ):
        print(dict(r))

    print("-- work_items WI-5137 source_spec_id / source_owner_directive (for comparison) --")
    for r in conn.execute(
        "SELECT id, version, source_spec_id, source_owner_directive, source_deliberation_query, "
        "related_deliberation_ids, related_spec_ids_at_creation FROM work_items WHERE id = 'WI-5137' ORDER BY version"
    ):
        print(dict(r))

    print("-- project_work_item_memberships WI-5137 and WI-5138, all versions --")
    for r in conn.execute(
        "SELECT id, version, project_id, work_item_id, source, change_reason FROM project_work_item_memberships "
        "WHERE id IN ('PWM-PROJECT-GTKB-PLATFORM-MODERNIZATION-WI-5137','PWM-PROJECT-GTKB-PLATFORM-MODERNIZATION-WI-5138') "
        "ORDER BY id, version"
    ):
        print(dict(r))

    print()
    conn.close()


report("LIVE", LIVE)
report("RECONSTRUCTED TARGET", TARGET)
