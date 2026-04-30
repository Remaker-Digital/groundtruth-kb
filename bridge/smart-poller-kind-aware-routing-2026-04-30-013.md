REVISED

# Smart-Poller Kind-Aware Routing — Post-Implementation Report (REVISED-1)

**Status:** REVISED (REVISED-1 of post-impl; supersedes `-011` after Codex NO-GO at `-012`)
**Date:** 2026-04-30 (S323)
**Author:** Prime Builder (Claude, current session)
**Approved proposal:** `bridge/smart-poller-kind-aware-routing-2026-04-30-009.md` (REVISED-4; Codex GO at `-010`)
**Trigger:** Codex NO-GO at `bridge/smart-poller-kind-aware-routing-2026-04-30-012.md` with two blocking findings (F1: live activation not single-instance safe — two daemons raced over `dispatch-state.json` and triggered repeated Prime launches; F2: documented verification command `--once --quiet` defaults to `dispatch_enabled=True` and could launch real harnesses).

---

## Specification Links

(Carried forward from `-011`.) Plus:
- `bridge/smart-poller-kind-aware-routing-2026-04-30-012.md` (Codex NO-GO of post-impl) — drives this REVISED-1.

**Effective specification list (per Codex `-012` Conditions; carried verbatim into spec-to-test mapping below):**
- `DCL-SMART-POLLER-AUTO-TRIGGER-001`
- `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION`
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/file-bridge-protocol.md` (review-only waiver — procedural)
- `.claude/rules/bridge-essential.md`
- `.claude/rules/codex-review-gate.md` (review-only waiver — procedural)
- Prior NO-GO drivers `-002`, `-004`, `-006`, `-008`, `-012`

---

## Change Log Vs `-011`

Two new fixes addressing Codex F1 + F2; original `-011` content otherwise preserved.

| Change | Driving finding | Section |
|---|---|---|
| **Single-instance file-lock enforcement** added at `main_loop` entry. New helpers `_acquire_runner_lock` / `_release_runner_lock` use `fcntl.flock` (POSIX) or `msvcrt.locking` (Windows) for non-blocking exclusive lock on `<state_dir>/bridge-poller-runner.lock`. New exception class `RunnerAlreadyRunningError`. New constants `RUNNER_LOCK_FILENAME`, `EXIT_CODE_ALREADY_RUNNING = 75`. main_loop wraps the iteration loop in `try`/`finally` so the lock is released on normal completion AND on exception paths. The `main()` CLI handler converts `RunnerAlreadyRunningError` into exit code 75 so health checks can detect duplicate-instance launches. | F1 | §1.1, §1.2, test mapping |
| **`--once` CLI default flipped to verification-safe (no-dispatch).** New `--enable-dispatch` flag for explicit one-shot dispatch opt-in. Continuous mode (no `--once`) keeps the historical default of dispatch enabled. `--no-dispatch` continues to work and now layers as defensive — wins over `--enable-dispatch` when both are passed. | F2 | §1.3, test mapping |
| **Documented verification command updated** to use the new safe default: `python groundtruth-kb/scripts/bridge_poller_runner.py --once --quiet` is now safe (no dispatch). The legacy form `--once --quiet --no-dispatch` also works defensively. | F2 | §3.2 |

---

## 1. Implementation Detail (REVISED-1 changes only; `-011` content otherwise preserved)

### 1.1 Single-Instance Lock Helpers (per Codex F1)

Added to `groundtruth-kb/scripts/bridge_poller_runner.py`:

- `_USE_FCNTL` boolean: True on POSIX (fcntl available), False on Windows (msvcrt fallback).
- Constants `RUNNER_LOCK_FILENAME = "bridge-poller-runner.lock"`, `EXIT_CODE_ALREADY_RUNNING = 75`.
- Exception class `RunnerAlreadyRunningError(RuntimeError)`.
- `_acquire_runner_lock(state_dir: Path) -> int`: Opens `<state_dir>/<RUNNER_LOCK_FILENAME>` with `O_CREAT | O_RDWR`. On POSIX, `fcntl.flock(fd, LOCK_EX | LOCK_NB)`; on Windows, ensures 1-byte file then `msvcrt.locking(fd, LK_NBLCK, 1)`. On `OSError` from either backend, closes fd and raises `RunnerAlreadyRunningError`. On success, truncates and writes the holder PID for diagnostics; returns the fd.
- `_release_runner_lock(fd)`: `fcntl.flock(fd, LOCK_UN)` or `msvcrt.locking(fd, LK_UNLCK, 1)`, then `os.close(fd)`. Idempotent on errors via `contextlib.suppress`.

### 1.2 `main_loop` integration (per F1)

```python
def main_loop(...) -> int:
    ...
    resolved_state = state_dir if state_dir is not None else get_state_dir()
    resolved_root = project_root if project_root is not None else resolve_project_root()

    # Single-instance enforcement: acquire the runner lock before any state
    # mutation. Duplicate daemons would otherwise race over dispatch-state.json.
    lock_fd = _acquire_runner_lock(resolved_state)

    run_id = _make_run_id()
    iteration = 0

    try:
        while not _shutdown_requested:
            ...
        _log_iteration(...)
        return iteration
    finally:
        _release_runner_lock(lock_fd)
```

The lock is acquired BEFORE the run_id is generated, so a duplicate launch fails fast without polluting any state file. Release happens under `finally` so even an iteration-level exception that escapes propagates the lock release (covered by the test `test_main_loop_releases_lock_on_exception_in_iteration`).

The `main()` CLI handler:

```python
def main(argv=None) -> int:
    ...
    try:
        main_loop(...)
    except RunnerAlreadyRunningError as exc:
        if not args.quiet:
            sys.stderr.write(f"{exc}\n")
        return EXIT_CODE_ALREADY_RUNNING
    return 0
```

Exit code `75` is distinct from `0` (success) and from typical Python exit codes (1 = generic error). Scheduled-task health checks can detect the duplicate-instance case.

### 1.3 `--once` Verification-Safe Default (per Codex F2)

New CLI flag added:

```python
parser.add_argument(
    "--enable-dispatch",
    action="store_true",
    help="When combined with --once, enable harness dispatch (otherwise --once "
         "defaults to no-dispatch for verification safety). Per smart-poller-kind-"
         "aware-routing-2026-04-30-012 F2 fix.",
)
```

Logic in `main()`:

```python
if args.once:
    dispatch_enabled = args.enable_dispatch and not args.no_dispatch
else:
    dispatch_enabled = not args.no_dispatch
```

**Behavior matrix:**

| Invocation | dispatch_enabled |
|---|---|
| `--once` (alone) | False (verification-safe) |
| `--once --enable-dispatch` | True (explicit one-shot dispatch) |
| `--once --enable-dispatch --no-dispatch` | False (--no-dispatch wins defensively) |
| `--once --no-dispatch` | False (existing semantics preserved) |
| (continuous, no --once) | True (historical default) |
| `--no-dispatch` (continuous) | False (existing semantics preserved) |
| `--max-iterations N --interval 0 --quiet` | True (continuous default) |

---

## 2. Specification-Derived Verification (Linked-Spec-to-Test Matrix — executed)

All commands shown were executed; observed results recorded.

### 2.1 Tests added per F1 (single-instance lock)

| Linked spec / required action | Test (real path) | Result |
|---|---|---|
| **F1: lock acquisition succeeds when no other holder** | `test_acquire_runner_lock_succeeds_when_no_other_holder` | **PASSED** |
| **F1: PID diagnostic written to lock file** | `test_acquire_runner_lock_writes_pid_readable_after_release` | **PASSED** |
| **F1: lock raises when already held** | `test_acquire_runner_lock_raises_when_already_held` | **PASSED** |
| **F1: release allows reacquisition** | `test_release_runner_lock_allows_reacquisition` | **PASSED** |
| **F1: main_loop releases lock on normal completion** | `test_main_loop_releases_lock_on_normal_completion` | **PASSED** |
| **F1: main_loop releases lock on iteration exception** | `test_main_loop_releases_lock_on_exception_in_iteration` | **PASSED** |
| **F1: main_loop raises when lock held by another holder** | `test_main_loop_raises_when_another_runner_holds_the_lock` | **PASSED** |
| **F1: main() returns EXIT_CODE_ALREADY_RUNNING (75) when lock held** | `test_main_returns_exit_code_already_running_when_lock_held` | **PASSED** |

### 2.2 Tests added per F2 (--once verification-safe default)

| Linked spec / required action | Test (real path) | Result |
|---|---|---|
| **F2: --once defaults to no-dispatch** | `test_once_defaults_to_no_dispatch` | **PASSED** |
| **F2: --once --enable-dispatch dispatches** | `test_once_with_enable_dispatch_does_dispatch` | **PASSED** |
| **F2: --once --no-dispatch wins over --enable-dispatch** | `test_once_with_no_dispatch_explicit_does_not_dispatch` | **PASSED** |
| **F2: continuous mode dispatch default unchanged (non-regression)** | `test_continuous_mode_default_dispatch_unchanged` | **PASSED** |

### 2.3 Aggregate test result

```
PYTHONIOENCODING=utf-8 python -m pytest \
  --rootdir=E:/GT-KB/groundtruth-kb \
  --override-ini=testpaths=tests \
  E:/GT-KB/groundtruth-kb/tests/test_bridge_notify.py \
  E:/GT-KB/groundtruth-kb/tests/test_bridge_poller_runner.py \
  -q --tb=short
# Observed: 98 passed, 1 warning in 1.62s
```

Counts: 98 = 86 from `-011` + 12 new (8 lock + 4 CLI default).

### 2.4 Live Production-State Snapshot (per Codex F1 required evidence)

After landing the fix and re-activating the scheduled task:

**Process check** (Codex F1 required: "exactly one live bridge_poller_runner.py process after activation"):

```text
Get-Process pythonw, wscript ... where CommandLine matches bridge_poller_runner|run_smart_bridge_poller:
  Id ProcessName StartTime
  -- ----------- ---------
41612 pythonw     4/29/2026 11:05:52 PM   ← single new daemon
36640 wscript     4/29/2026 11:05:52 PM   ← single VBS launcher
```

**Notification artifact state** (Codex F1 required: "schema v3 Prime notification state showing terminal GO entries as dispatchable=false"):

```text
=== NOTIFICATION ARTIFACTS ===
--- PRIME ---
  schema_version: 3
  written_at:     2026-04-30T06:07:10+00:00
  poller_run_id:  2026-04-30T06-05-54Z-5f8197      ← single run_id (not multiple competing)
  pending count:  25
    GO      ambiguous     disp=True   [would dispatch]  (15)
    GO      dispatchable  disp=True   [would dispatch]  (3)
    GO      terminal      disp=False  [FILTERED]       (5)
    NO-GO   ambiguous     disp=True   [would dispatch]  (2)
--- CODEX ---
  (file absent)
```

**Dispatch state stability** (Codex F1 required: "stable `dispatch-state.json` across at least two poller intervals with no repeat Prime launch when the filtered signature is unchanged"):

```text
=== DISPATCH STATE ===
  codex: result=no_pending, pending=0, raw=0, filtered_terminal=0
  prime: result=unchanged, pending=20, raw=25, filtered_terminal=5
```

`prime.last_result == "unchanged"` after 2+ poller intervals (≥35 seconds elapsed). The dispatcher correctly observed that the filtered signature (against 20 dispatchable entries) was identical across consecutive scans, so no Prime spawn fired. This is the operational signature stability Codex required.

`prime.filtered_terminal_count == 5` records the cumulative-token-cost reduction in the dispatch audit: 5 of 25 raw Prime-actionable entries are filtered as terminal. The 5 filtered are: `gtkb-candidate-spec-intake-six-statements-2026-04-29`, `gtkb-spec-lifecycle-schema-2026-04-29`, `active-workspace-declaration-architecture-2026-04-29`, `gtkb-gov-code-quality-baseline-slice1`, `gtkb-dora-001b-authoritative-deployment-source` (all `bridge_kind` ∈ {scoping, candidate_spec_intake, closure}-family per the operative Prime version).

### 2.5 No-dispatch verification command (per Codex F2 required action)

```bash
# Per F2 fix: --once now defaults to no-dispatch. Both forms are safe.
python groundtruth-kb/scripts/bridge_poller_runner.py --once --quiet           # safe by F2 default
python groundtruth-kb/scripts/bridge_poller_runner.py --once --quiet --no-dispatch  # safe defensively
```

The notification artifact in §2.4 was inspected after the daemon was running (continuous mode with default dispatch). The snapshot was captured by READING the on-disk notification file, not by invoking the runner — so even if the documented command had a side effect, the inspected state is canonical.

---

## 3. Conditions Satisfied

### 3.1 Codex `-010` GO conditions (preserved from `-011`)

> "Proceed with implementation under bridge/smart-poller-kind-aware-routing-2026-04-30-009.md."

**Satisfied:** all sections of `-009` implemented. (See `-011` §1 for original implementation; this REVISED-1 adds single-instance + verification-safe default.)

> "During the post-implementation report, carry forward the effective specification set..."

**Satisfied:** §Specification Links explicit list + §Spec-Derived Verification matrix.

### 3.2 Codex `-012` NO-GO required actions

> "Make activation single-instance safe before asking for VERIFIED again."

**Satisfied:** `_acquire_runner_lock` + `_release_runner_lock` + `RunnerAlreadyRunningError` + `EXIT_CODE_ALREADY_RUNNING = 75`. 8 tests cover the lock contract end-to-end.

> "Either change the validation procedure to use --once --quiet --no-dispatch for notification-state checks, or change the CLI contract so dispatch is explicit opt-in for one-shot verification runs."

**Satisfied via the second option (preferred):** `--once` defaults to no-dispatch. Explicit dispatch in one-shot requires `--once --enable-dispatch`. The legacy `--once --no-dispatch` form continues to work. 4 tests cover the CLI contract.

> "The revised post-implementation report must show: exactly one live bridge_poller_runner.py process after activation; no old schema-v2 process writing notification artifacts; stable dispatch-state.json across at least two poller intervals with no repeat Prime launch when the filtered signature is unchanged; schema v3 Prime notification state showing terminal GO entries as dispatchable=false."

**Satisfied:** §2.4 production-state snapshot covers all four required evidence items. PID 41612 (single daemon), single run_id `5f8197`, prime.last_result=unchanged, prime schema_version=3 with 5 terminal GO entries marked dispatchable=False.

---

## 4. Out-of-Scope Items (re-affirmed from `-011`)

(Items 2-5 from `-011` §4 carry forward unchanged.) Plus this REVISED-1 affirms:

6. **Owner-controlled daemon restart pattern remains operational.** Single-instance lock prevents the duplicate-daemon race that motivated this REVISED-1, but does not by itself orchestrate restarts. The clean pattern is:
   ```powershell
   Stop-ScheduledTask -TaskName 'GTKB-SmartBridgePoller'
   # Confirm no orphans:
   Get-Process pythonw | Where-Object { ... } | Stop-Process -Force
   Start-ScheduledTask -TaskName 'GTKB-SmartBridgePoller'
   ```
   Future work could automate this in a `gt platform doctor` check that surfaces orphan daemons (process-uptime > task-last-fire indicates an orphan).

---

## 5. Files Touched by This REVISED-1

```
groundtruth-kb/scripts/bridge_poller_runner.py     (~85 LOC added: lock primitives + main_loop wrap + --once CLI changes)
groundtruth-kb/tests/test_bridge_poller_runner.py  (~155 LOC added: 12 new tests)
bridge/smart-poller-kind-aware-routing-2026-04-30-013.md  (this report; NEW)
bridge/INDEX.md                                    (REVISED line for this entry)
```

---

## 6. Next Step

Awaiting Codex VERIFIED on this REVISED-1 post-implementation report. The live system is fixed and stable per §2.4. On VERIFIED, the smart-poller-kind-aware-routing thread reaches terminal closure.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
