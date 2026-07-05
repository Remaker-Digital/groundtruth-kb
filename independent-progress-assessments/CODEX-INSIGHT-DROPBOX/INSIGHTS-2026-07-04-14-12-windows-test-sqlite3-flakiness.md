# Loyal Opposition Report: SQLite3 Connection Locking Flakiness on Windows

**Topic:** Windows Test SQLite3 Flakiness
**Date:** 2026-07-04
**Severity:** P2
**Harness ID:** C (Antigravity)

---

### 1. Observation
During test execution, specifically in `test_terminal_work_item_dispatch_residue_is_health_pass`, we encountered an intermittent failure where `status.health_status` returned `"WARN"` instead of the expected `"PASS"`. 
This failure was traced to a race condition caused by unclosed SQLite3 connections.
In the test file [test_bridge_dispatch_config.py](file:///E:/GT-KB/platform_tests/scripts/test_bridge_dispatch_config.py), the function `_write_current_work_items` creates a SQLite3 connection without closing it:
```python
def _write_current_work_items(root: Path, rows: dict[str, str]) -> None:
    with sqlite3.connect(root / "groundtruth.db") as con:
        con.execute("CREATE TABLE current_work_items (id TEXT PRIMARY KEY, resolution_status TEXT)")
        con.executemany(
            "INSERT INTO current_work_items (id, resolution_status) VALUES (?, ?)",
            sorted(rows.items()),
        )
```
In Python's `sqlite3` module, the `with sqlite3.connect(...)` context manager only manages transactions (committing on success, rolling back on exception). It **does not close** the database connection.
Simultaneously, in [bridge_dispatch_config.py](file:///E:/GT-KB/groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py), the function `_work_item_resolution_status` performs a read from the same database:
```python
def _work_item_resolution_status(project_root: Path, work_item_id: str) -> str | None:
    db_path = project_root / "groundtruth.db"
    if not db_path.is_file():
        return None
    try:
        with sqlite3.connect(db_path) as con:
            row = con.execute(
                "SELECT resolution_status FROM current_work_items WHERE id = ? LIMIT 1",
                (work_item_id,),
            ).fetchone()
...
```
Because the write connection remains open, Windows enforces strict file locks that prevent the read connection from accessing `groundtruth.db`, raising a `sqlite3.OperationalError` (database is locked). This exception is caught in the `try-except sqlite3.Error:` block, causing the function to silently return `None`. As a result, the terminal resolution status (`retired`) is not matched, the failure evidence is not marked as stale/neutral, and the health status upgrades to `"WARN"`.

### 2. Deficiency Rationale
- **Test Flakiness / CI Stability:** Unclosed connections leave locks in place, causing tests to depend heavily on the timing of Python's garbage collector. On Windows systems where file locking is strict, this results in flaky test runs.
- **Silent Failure Swallow:** Swallowing all `sqlite3.Error` without logging or telemetry makes diagnosis difficult when database access fails.

### 3. Proposed Solution/Enhancement
We recommend wrapping all SQLite3 connections in `contextlib.closing` or explicitly calling `.close()` in `finally` blocks to guarantee immediate connection release:
1. Refactor `_write_current_work_items` in [test_bridge_dispatch_config.py](file:///E:/GT-KB/platform_tests/scripts/test_bridge_dispatch_config.py):
   ```python
   from contextlib import closing
   # ...
   def _write_current_work_items(root: Path, rows: dict[str, str]) -> None:
       with closing(sqlite3.connect(root / "groundtruth.db")) as con:
           con.execute("CREATE TABLE current_work_items (id TEXT PRIMARY KEY, resolution_status TEXT)")
           con.executemany(
               "INSERT INTO current_work_items (id, resolution_status) VALUES (?, ?)",
               sorted(rows.items()),
           )
   ```
2. Refactor `_work_item_resolution_status` in [bridge_dispatch_config.py](file:///E:/GT-KB/groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py):
   ```python
   from contextlib import closing
   # ...
   def _work_item_resolution_status(project_root: Path, work_item_id: str) -> str | None:
       db_path = project_root / "groundtruth.db"
       if not db_path.is_file():
           return None
       try:
           with closing(sqlite3.connect(db_path)) as con:
               row = con.execute(
                   "SELECT resolution_status FROM current_work_items WHERE id = ? LIMIT 1",
                   (work_item_id,),
               ).fetchone()
       except sqlite3.Error:
           return None
       if row is None or row[0] is None:
           return None
       return str(row[0]).strip()
   ```

### 4. Option Rationale
Using `contextlib.closing` is the standard Python approach to ensure resource release for objects that support `.close()` but do not act as context managers that call close themselves (such as `sqlite3.Connection`). It avoids manual `try-finally` blocks and minimizes implementation footprint.

## Prime Builder Implementation Context
- **Objective:** Eliminate SQLite3 file locking race conditions in test suites and health checks.
- **Exact evidence paths and line references:** 
  - [bridge_dispatch_config.py](file:///E:/GT-KB/groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py#L1519-L1525)
  - [test_bridge_dispatch_config.py](file:///E:/GT-KB/platform_tests/scripts/test_bridge_dispatch_config.py#L60-L70)
- **Ordered implementation sequence:**
  - Import `closing` from `contextlib` in both files.
  - Wrap `sqlite3.connect(...)` statements with `closing()`.
  - Execute the full test suite (`pytest platform_tests/scripts/test_bridge_dispatch_config.py`) to verify health.

Skills applied: loyal-opposition-report, code-review-audit
