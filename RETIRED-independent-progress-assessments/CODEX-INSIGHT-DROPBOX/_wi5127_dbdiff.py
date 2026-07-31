"""Read-only ownership map: diff working groundtruth.db vs HEAD:groundtruth.db.

Determines whether the db's uncommitted changes are WI-5127-only (the three DCL
carriers) or commingled with other parallel-session writes. No mutation.
"""
import subprocess
import sqlite3
import tempfile
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WORK_DB = os.path.join(ROOT, "groundtruth.db")

# Dump HEAD:groundtruth.db to a temp file (read-only).
head_bytes = subprocess.check_output(
    ["git", "cat-file", "-p", "HEAD:groundtruth.db"], cwd=ROOT
)
tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
tmp.write(head_bytes)
tmp.close()
HEAD_DB = tmp.name


def rows(db, sql):
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in con.execute(sql).fetchall()]
    finally:
        con.close()


def keyset(db, table, keycols):
    cols = ", ".join(keycols)
    return {tuple(r[c] for c in keycols): r for r in rows(db, f"SELECT {cols} FROM {table}")}


def tables(db):
    return [r["name"] for r in rows(db, "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]


print("=== tables present (working) ===")
wt = tables(WORK_DB)
print(", ".join(wt))

# specifications diff by (id, version)
print("\n=== NEW specification rows in working (not in HEAD), by (id,version) ===")
try:
    head_spec = keyset(HEAD_DB, "specifications", ["id", "version"])
    work_spec = keyset(WORK_DB, "specifications", ["id", "version"])
    new_specs = [k for k in work_spec if k not in head_spec]
    print(f"count new spec rows: {len(new_specs)}")
    # pull richer detail for the new ones
    con = sqlite3.connect(WORK_DB)
    con.row_factory = sqlite3.Row
    for sid, ver in sorted(new_specs):
        r = con.execute(
            "SELECT id, version, type, status, changed_by, changed_at FROM specifications WHERE id=? AND version=?",
            (sid, ver),
        ).fetchone()
        print(f"  {r['id']} v{r['version']} type={r['type']} status={r['status']} by={r['changed_by']} at={r['changed_at']}")
    con.close()
except Exception as e:
    print("spec diff error:", e)

# deliberations diff
print("\n=== NEW deliberation rows in working (not in HEAD) ===")
for delib_table, key in [("deliberations", "deliberation_id"), ("deliberations", "id")]:
    try:
        cols = [c["name"] for c in rows(WORK_DB, "PRAGMA table_info(deliberations)")]
        keycol = "deliberation_id" if "deliberation_id" in cols else ("id" if "id" in cols else cols[0])
        head_d = keyset(HEAD_DB, "deliberations", [keycol])
        work_d = keyset(WORK_DB, "deliberations", [keycol])
        new_d = [k for k in work_d if k not in head_d]
        print(f"keycol={keycol}; count new delib rows: {len(new_d)}")
        con = sqlite3.connect(WORK_DB)
        con.row_factory = sqlite3.Row
        pick = [c for c in (keycol, "source_type", "outcome", "created_at", "session_id") if c in cols]
        for (kv,) in sorted(new_d):
            sel = ", ".join(pick)
            r = con.execute(f"SELECT {sel} FROM deliberations WHERE {keycol}=?", (kv,)).fetchone()
            print("  " + " | ".join(f"{c}={r[c]}" for c in pick))
        con.close()
        break
    except Exception as e:
        print("delib diff error:", e)

# work_items diff (by id + any version/updated marker)
print("\n=== work_items row count HEAD vs working ===")
try:
    hc = rows(HEAD_DB, "SELECT COUNT(*) n FROM work_items")[0]["n"]
    wc = rows(WORK_DB, "SELECT COUNT(*) n FROM work_items")[0]["n"]
    print(f"HEAD work_items rows: {hc}; working: {wc}; delta: {wc - hc}")
except Exception as e:
    print("work_items diff error:", e)

os.unlink(HEAD_DB)
print("\n=== done ===")
