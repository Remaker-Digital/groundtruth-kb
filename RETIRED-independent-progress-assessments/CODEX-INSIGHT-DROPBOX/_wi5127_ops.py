"""Read-only: per-table diff of working groundtruth.db vs HEAD to characterize
exactly what a `git add groundtruth.db` finalization commit would capture."""
import subprocess
import sqlite3
import tempfile
import os
import hashlib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WORK_DB = os.path.join(ROOT, "groundtruth.db")

head_bytes = subprocess.check_output(["git", "cat-file", "-p", "HEAD:groundtruth.db"], cwd=ROOT)
tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
tmp.write(head_bytes)
tmp.close()
HEAD_DB = tmp.name


def tnames(db):
    con = sqlite3.connect(db)
    try:
        return [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    finally:
        con.close()


def table_fingerprint(db, table):
    """Return (rowcount, set-of-row-hashes) for content-level diff."""
    con = sqlite3.connect(db)
    try:
        cur = con.execute(f"SELECT * FROM {table}")
        hashes = set()
        n = 0
        for row in cur:
            n += 1
            hashes.add(hashlib.sha1(repr(row).encode("utf-8", "replace")).hexdigest())
        return n, hashes
    except Exception as e:
        return None, str(e)
    finally:
        con.close()


work_tables = set(tnames(WORK_DB))
head_tables = set(tnames(HEAD_DB))
print(f"tables only in working: {sorted(work_tables - head_tables)}")
print(f"tables only in HEAD   : {sorted(head_tables - work_tables)}")

common = sorted(work_tables & head_tables)
print("\n=== per-table content diff (only tables that differ) ===")
changed_any = False
for t in common:
    hn, hh = table_fingerprint(HEAD_DB, t)
    wn, wh = table_fingerprint(WORK_DB, t)
    if isinstance(hh, str) or isinstance(wh, str):
        print(f"  {t}: ERROR head={hh if isinstance(hh,str) else ''} work={wh if isinstance(wh,str) else ''}")
        continue
    added = len(wh - hh)
    removed = len(hh - wh)
    if added or removed or hn != wn:
        changed_any = True
        print(f"  {t}: rows {hn}->{wn} (delta {wn-hn}); rows_added={added} rows_removed={removed}")

if not changed_any:
    print("  (no table differs)")

# Detail: which work_items rows are new
print("\n=== new work_items rows (by all columns) ===")
con_h = sqlite3.connect(HEAD_DB); con_h.row_factory = sqlite3.Row
con_w = sqlite3.connect(WORK_DB); con_w.row_factory = sqlite3.Row
cols = [c["name"] for c in con_w.execute("PRAGMA table_info(work_items)")]
keyc = "id" if "id" in cols else cols[0]
verc = "version" if "version" in cols else None
head_keys = set()
for r in con_h.execute("SELECT * FROM work_items"):
    head_keys.add((r[keyc], r[verc] if verc else None, hashlib.sha1(repr(tuple(r)).encode("utf-8","replace")).hexdigest()))
head_hashes = {h for (_, _, h) in head_keys}
show = [c for c in (keyc, verc, "stage", "lifecycle_state", "status", "changed_by", "changed_at", "title", "description") if c and c in cols]
for r in con_w.execute("SELECT * FROM work_items"):
    h = hashlib.sha1(repr(tuple(r)).encode("utf-8","replace")).hexdigest()
    if h not in head_hashes:
        vals = []
        for c in show:
            v = r[c]
            if isinstance(v, str) and len(v) > 60:
                v = v[:60] + "..."
            vals.append(f"{c}={v}")
        print("  " + " | ".join(vals))
con_h.close(); con_w.close()

os.unlink(HEAD_DB)
print("\n=== done ===")
