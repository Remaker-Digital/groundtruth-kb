# WI-3168: Migrate knowledge.db to groundtruth.db at repo root (REVISED v11)

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-13
**Work Item:** WI-3168
**Source Spec:** SPEC-2098
**Priority:** P3
**Revision:** Addresses 1 finding in `bridge/groundtruth-db-migration-022.md` (Codex NO-GO #11)

## NO-GO #11 Response

| # | Finding | Severity | Resolution |
|---|---------|----------|------------|
| 1 | Checkpoint result discarded; deletion unconditional; no file-size gate | P1 | Phase 1i rewritten: fetches checkpoint result tuple, asserts busy=0, verifies WAL is 0 bytes post-checkpoint, fails closed on any contention. Deletion conditional on all checks passing. |

## Scope

**Implementation scope identical to v015/v017.** Only Phase 1i and V8 updated.

For full scope: see `bridge/groundtruth-db-migration-015.md`.

### Phase 1i. SQLite sidecar disposition (rewritten — fail-closed)

```python
python -c "
import os
import sqlite3
import sys

db_path = 'tools/knowledge-db/knowledge.db'
shm_path = db_path + '-shm'
wal_path = db_path + '-wal'

# Step 1: Open exclusive connection and checkpoint
conn = sqlite3.connect(db_path)
result = conn.execute('PRAGMA wal_checkpoint(TRUNCATE)').fetchone()
conn.close()

# Result tuple: (busy, log_frames, checkpointed_frames)
busy, log_frames, checkpointed_frames = result
print(f'Checkpoint result: busy={busy}, log={log_frames}, checkpointed={checkpointed_frames}')

# Step 2: Assert checkpoint completed without contention
if busy != 0:
    print('FAIL: checkpoint reported busy — another process has the DB open')
    print('ACTION: close all DB consumers and retry, or request owner decision')
    sys.exit(1)

# Step 3: Verify WAL is 0 bytes after checkpoint
if os.path.exists(wal_path):
    wal_size = os.path.getsize(wal_path)
    print(f'WAL size after checkpoint: {wal_size} bytes')
    if wal_size > 0:
        print('FAIL: WAL is non-zero after checkpoint — data may not be fully written')
        print('ACTION: investigate, close DB consumers and retry, or request owner decision')
        sys.exit(1)
else:
    print('WAL file absent after checkpoint (expected for TRUNCATE mode)')
    wal_size = 0

# Step 4: All checks passed — safe to proceed
print(f'PASS: checkpoint clean (busy=0, wal={wal_size} bytes). Sidecars safe to delete.')
"
```

**Only after the above script prints PASS and exits 0:**

```bash
# Phase 1a: Move the main database
git mv tools/knowledge-db/knowledge.db groundtruth.db

# Phase 1i continued: Delete orphaned sidecars
rm -f tools/knowledge-db/knowledge.db-shm tools/knowledge-db/knowledge.db-wal
```

**If the checkpoint script exits non-zero:** STOP. Do not move the DB or delete sidecars. Close all DB consumers (web UI, hooks, other Python processes), then rerun the checkpoint. If contention persists, request owner decision.

**Owner-safety basis:**
1. Checkpoint result is fetched, inspected, and recorded
2. Busy flag must be 0 (no contention)
3. WAL must be 0 bytes post-checkpoint (no pending data)
4. Deletion is conditional on all checks passing
5. Sidecars are auto-generated, gitignored, and orphaned after the main DB moves

## Verification Plan

### V1–V7, V9–V11. Unchanged from v015/v017/v019

### V8. Directory audit (updated — records checkpoint evidence)

```bash
# No stale knowledge.db artifacts (main DB, sidecars, backups)
ls tools/knowledge-db/knowledge.db* 2>/dev/null && echo "BLOCKER" || echo "OK: no stale knowledge.db artifacts"

# No nested groundtruth.db
ls tools/knowledge-db/groundtruth.db* 2>/dev/null && echo "BLOCKER" || echo "OK: no nested groundtruth.db"

# No stale ChromaDB
ls -d tools/knowledge-db/.groundtruth-chroma 2>/dev/null && echo "BLOCKER" || echo "OK: no stale chroma"

# No unexpected DB files (only bridge.db allowed)
ls tools/knowledge-db/*.db 2>/dev/null | grep -v bridge.db && echo "BLOCKER" || echo "OK"

# Confirm sidecars gone
git status --short --ignored -- tools/knowledge-db/knowledge.db-shm tools/knowledge-db/knowledge.db-wal
# Expected: no output
```

**Post-implementation report must record:**
- Checkpoint result tuple (busy, log_frames, checkpointed_frames)
- WAL size after checkpoint (bytes)
- Whether the checkpoint script exited 0
