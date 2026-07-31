import sqlite3

con = sqlite3.connect(r"E:\GT-KB\groundtruth.db")
con.row_factory = sqlite3.Row
cols = [r[1] for r in con.execute("PRAGMA table_info(current_specifications)").fetchall()]
print("COLUMNS:", cols)
r = con.execute(
    "SELECT * FROM current_specifications WHERE id = ?",
    ("SPEC-DISPATCHER-IDENTITY-RUNTIME-KIND-SEPARATION-001",),
).fetchone()
for k in r.keys():
    v = r[k]
    if isinstance(v, str) and len(v) > 100:
        print(f"\n--- {k} ---")
        print(v)
    else:
        print(f"{k}: {v!r}")
con.close()
