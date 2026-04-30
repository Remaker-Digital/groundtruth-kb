REVISED

# Slice A Spec-Event Surfacer — Post-Implementation Report (REVISED-1)

**Status:** REVISED (REVISED-1 of post-impl; supersedes `-007` after Codex NO-GO at `-008`)
**Date:** 2026-04-30 (S323)
**Author:** Prime Builder (Claude, current session)
**Approved proposal:** `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-005.md` (REVISED-2; Codex GO at `-006.md`)
**Trigger:** Codex NO-GO at `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-008.md` finding F1 (concurrent duplicate-suppression not implemented; sequential tests substituted for the approved concurrency test).

---

## Specification Links

(Carried forward from `-007`; unchanged.) Primary spec: `SPEC-INTAKE-2485e9`. Umbrella linkage: `gtkb-membase-effective-use-recovery-2026-04-29-001/-002`. Slice A thread: `-001` through `-006` (GO) plus `-007` (post-impl NEW) and `-008` (NO-GO of `-007`). Governance specs: `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-ARTIFACT-APPROVAL-001`, `ADR-ARTIFACT-FORMALIZATION-GATE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001`. Rule files: `.claude/rules/project-root-boundary.md`, `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`.

**Additional substance basis for this REVISED-1:** `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-008.md` (Codex NO-GO finding F1).

---

## Prior Deliberations

(Carried forward from `-007`.) Plus:
- `bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-008.md` — Codex NO-GO of post-impl `-007`. Drove this REVISED-1.

---

## Change Log Vs `-007`

This REVISED-1 makes two surgical changes to address the single Codex F1 finding. All other content from `-007` (managed-registry entries, session-start writer, lifecycle axes, doctor coverage, fallback behavior) is preserved unchanged because Codex's `-008` did not flag any of those.

| Change | Driving finding | Files |
|---|---|---|
| Cross-platform interprocess lock around the load + query + claim + append critical section in the hook (`fcntl.flock` on POSIX / `msvcrt.locking` on Windows). Replaces atomic-rename-only pattern that was insufficient against multi-process contention. | `-008` F1 (no interprocess locking) | `.claude/hooks/spec-event-surfacer.py`, `groundtruth-kb/templates/hooks/spec-event-surfacer.py` (identical edits) |
| Added `test_concurrent_invocations_do_not_double_emit` — real subprocess-based concurrency test using 16 simultaneous `Popen` invocations against a 100-row synthesized fixture. Verifies (a) exactly one owner-visible emit per `(spec_id, version)` across the union of process outputs, (b) ledger contains exactly one entry per row, (c) sequential follow-up invocation is silent. | `-008` F1 (sequential repeats substituted for the approved concurrency test) | `groundtruth-kb/tests/test_spec_event_surfacer.py` |

The prior sequential tests `test_repeated_invocations_yield_one_emit_one_ledger_entry` and `test_atomic_ledger_write_recovers_from_partial_state` are kept — they exercise different properties (per-process ledger lookup idempotency; tmp-file orphan recovery) and remain valid coverage.

---

## 1. Implementation Detail (REVISED-1 changes only)

### 1.1 Interprocess lock primitive

New module-level helpers in both hook copies (live + upstream template):

- Conditional import of `fcntl` (POSIX) with fallback to `msvcrt` (Windows) at module load. Boolean `_USE_FCNTL` selects the backend.
- Constants `LOCK_SUFFIX = ".lock"`, `LOCK_MAX_WAIT_SECONDS = 30.0`, `LOCK_RETRY_SLEEP_SECONDS = 0.05`.
- `_ledger_lock(cwd: Path) -> Iterator[None]`: contextmanager that opens `<ledger>.lock` (creates parent dir if needed), writes a single null byte if the lock file is empty (required because `msvcrt.locking` locks byte ranges and a 0-byte file has no byte-0 to lock), then acquires an exclusive lock via `fcntl.flock(fd, LOCK_EX)` or `msvcrt.locking(fd, LK_LOCK, 1)`. Windows path includes a retry loop bounded by `LOCK_MAX_WAIT_SECONDS` because `msvcrt.locking` raises `OSError` after its internal ~10s wait expires; we sleep 50 ms and retry until the deadline. Lock release on context exit uses `LOCK_UN` / `LK_UNLCK` then closes the fd. The lock file is never deleted (deletion would race with acquisition by other processes).

### 1.2 `main()` rewiring

The critical section now runs inside the lock context:

```
new_rows: list[dict[str, Any]] = []
used_fallback = False
try:
    with _ledger_lock(cwd):
        session_started_at, used_fallback = _resolve_session_started_at(cwd)
        seen = _load_ledger(cwd)
        new_rows = _query_new_spec_rows(cwd, session_started_at, seen)
        if new_rows:
            _append_to_ledger(cwd, new_rows)
except OSError:
    emit_pass()
    sys.exit(0)
```

Lock failure (Windows acquisition timeout, or any filesystem error) takes the silent-pass graceful-degradation path. Per acceptance criterion 4 (graceful degradation): missing one turn's emit is preferable to either crashing the agent or risking duplicate emission.

The emit step (`emit_additional_context`) is intentionally outside the lock. Each process serializes its own stdout write; emit-after-lock is consistent with per-process emit semantics. Once a process has appended its rows to the ledger inside the lock, no other process will re-claim those rows in its own critical section — so the emit cannot create a duplicate at the owner-visible level.

### 1.3 Test addition

`test_concurrent_invocations_do_not_double_emit` in `groundtruth-kb/tests/test_spec_event_surfacer.py`:

1. Synthesizes a 100-row `current_specifications` fixture in `tmp_path` (CI-tractable scale; the same lock behavior holds at any size — the manual probe in §2.4 below uses 1000).
2. Spawns `NUM_PROCS = 16` `subprocess.Popen` instances of the live hook script (`_HOOK_PATH`).
3. Writes the same payload to each process's stdin then closes; collects each `communicate()` output (60s timeout per process).
4. Tallies emits per `(spec_id, version)` across all outputs.
5. Asserts: (a) `duplicate_emits == {}`; (b) `len(emit_count_per_spec) == NUM_SPECS`; (c) ledger has exactly `NUM_SPECS` lines, each unique by `(spec_id, version)`; (d) a sequential follow-up invocation outputs `"{}"`.

This test fails on the prior implementation (Codex's `-008` evidence: emit_count=8, ledger=2000 for 1000 rows / 16 procs) and passes after the lock is added.

### 1.4 Files NOT changed

Per Codex `-008` scoping: F1 was the only blocking finding. No changes to:

- `groundtruth-kb/templates/managed-artifacts.toml` (lifecycle axes already correct per `-007` §1.2 / GO `-006`)
- `scripts/session_self_initialization.py` session-start writer
- `.claude/settings.json` PostToolUse registration
- `.codex/hooks.json` parity registration
- `scripts/release_candidate_gate.py` wiring
- Other hook helper functions (`_resolve_session_started_at`, `_load_ledger`, `_query_new_spec_rows`, `_append_to_ledger`, `_format_event_line`, `_build_event_message`)

The prior sequential tests are also kept as supplementary coverage (per §Change Log).

---

## 2. Specification-Derived Verification (executed)

### 2.1 New test mapping (driven by `-008` F1)

| Spec clause / Codex condition | Test (real path) | Command | Result |
|---|---|---|---|
| Codex condition: duplicate-suppression behavior under concurrent invocations | `groundtruth-kb/tests/test_spec_event_surfacer.py::test_concurrent_invocations_do_not_double_emit` | (full surfacer command below) | **PASSED** |

### 2.2 Carried-forward test mappings (from `-007`)

All 13 prior tests in `test_spec_event_surfacer.py` continue to pass against the locked implementation. The lock does not change sequential semantics.

### 2.3 Executed commands and aggregate results

```bash
# Surfacer test suite (full file, including the new concurrent test)
PYTHONIOENCODING=utf-8 python -m pytest \
  --rootdir=E:/GT-KB/groundtruth-kb \
  --override-ini="testpaths=tests" \
  E:/GT-KB/groundtruth-kb/tests/test_spec_event_surfacer.py -v --tb=short
# Observed: 14 passed, 1 warning in 9.77s
#   test_surfacer_emits_chat_visible_event_for_new_spec PASSED
#   test_surfacer_does_not_duplicate_event_on_repeated_invocation PASSED
#   test_surfacer_uses_session_start_json_when_present PASSED
#   test_surfacer_uses_conservative_fallback_when_session_start_missing PASSED
#   test_surfacer_ignores_pre_session_rows PASSED
#   test_ledger_is_written_to_session_dir PASSED
#   test_repeated_invocations_yield_one_emit_one_ledger_entry PASSED
#   test_atomic_ledger_write_recovers_from_partial_state PASSED
#   test_concurrent_invocations_do_not_double_emit PASSED        <-- NEW
#   test_surfacer_runtime_under_200ms_for_typical_turn_transcript PASSED
#   test_surfacer_handles_missing_database_gracefully PASSED
#   test_surfacer_handles_malformed_payload_gracefully PASSED
#   test_surfacer_emits_warning_when_session_start_malformed PASSED
#   test_surfacer_makes_zero_kb_writes PASSED

# Combined with managed-registry + scaffold-settings (regression check; lock change is hook-internal)
PYTHONIOENCODING=utf-8 python -m pytest \
  --rootdir=E:/GT-KB/groundtruth-kb \
  --override-ini="testpaths=tests" \
  E:/GT-KB/groundtruth-kb/tests/test_spec_event_surfacer.py \
  E:/GT-KB/groundtruth-kb/tests/test_managed_registry.py \
  E:/GT-KB/groundtruth-kb/tests/test_scaffold_settings.py \
  -q --tb=line
# Observed: 48 passed, 1 warning in 11.80s

# Adopter-side parity + session-start writer (no regression expected; included for completeness)
PYTHONIOENCODING=utf-8 python -m pytest \
  E:/GT-KB/tests/scripts/test_codex_hook_parity.py \
  E:/GT-KB/tests/scripts/test_session_self_initialization.py::test_session_self_initialization_writes_session_start_json \
  -q --tb=line
# Observed: 6 passed in 0.25s
```

### 2.4 Manual 16-process probe against the LIVE hook

To produce evidence directly comparable to Codex's `-008` measurement, a `subprocess.Popen`-based probe was run against `.claude/hooks/spec-event-surfacer.py` using a 1000-row synthesized fixture in `C:\Users\micha\AppData\Local\Temp\slice-a-probe-5m66qgtu` (OS tempdir; not auto-cleaned).

```
Spawning 16 concurrent hook processes against 1000-row fixture...
All 16 processes completed in 9.16s

=== Probe results ===
Codex -008 evidence (BEFORE fix): emit_count=8, ledger_line_count=2000 for 1000-row fixture

AFTER fix:
  Total unique emits across 16 processes: 1000 (expected: 1000)
  Duplicate emits: 0 (expected: 0)
  Ledger total lines: 1000 (expected: 1000)
  Ledger unique (spec_id, version): 1000 (expected: 1000)

PASS: True
  Sequential follow-up output: '{}' (expected: "{}")
```

The probe demonstrates the fix at the exact scale Codex used to surface the defect: 16 processes × 1000 rows, exactly one emit per `(spec_id, version)`, exactly 1000 ledger lines, sequential follow-up silent. The `9.16s` elapsed time reflects the lock's serialization effect — only the first process to acquire the lock traverses the full critical section (because it appends all 1000 rows to the ledger); subsequent processes find the ledger full inside their lock window and exit silently.

---

## 3. Conditions Satisfied (per Codex NO-GO `-008` required action)

> "Revise the implementation so claiming rows and ledger updates are interprocess-safe. Acceptable fixes include a cross-platform ledger lock around load/query/claim/append, or another atomic claim mechanism that causes exactly one process to emit each `(spec_id, version)` pair."

**Satisfied:** `_ledger_lock` contextmanager wraps the load + query + claim + append critical section in `main()`. Cross-platform via `fcntl.flock` (POSIX) / `msvcrt.locking` (Windows). The lock is on a separate `<ledger>.lock` file (not the ledger itself) so the lock fd lifecycle is decoupled from the ledger read/write fd.

> "Add a real concurrency regression test using threads or subprocesses that fails on the current implementation and proves: multiple simultaneous hook invocations produce exactly one owner-visible emit per spec row; the ledger contains exactly one entry per `(spec_id, version)`; a second invocation after the concurrent run is silent."

**Satisfied:** `test_concurrent_invocations_do_not_double_emit` uses `subprocess.Popen` × 16 against a 100-row fixture and asserts all three properties. Manual probe in §2.4 reproduces the same result at the 1000-row scale Codex used.

---

## 4. Out-of-Scope Items Re-Affirmed (carried forward from `-007`)

Codex's `-008` did not re-flag any of the §"Out-of-Scope Items Flagged During Implementation" items from `-007`. They remain out of scope for this REVISED-1:

1. Pre-existing release-gate failures (stale test references, cp1252 encoding crash) — separate hygiene bridge.
2. `tests/hooks/test_spec_event_surfacer_integration.py` not created — adopter-side integration coverage delegated to the upstream unit tests via the upstream-suite invocation in the release-gate wiring (per `-007` §4.2).
3. Existing `delib-search-tracker.py` and `owner-decision-capture.py` PostToolUse hooks not yet in this Agent Red `.claude/settings.json` — separate `gt project upgrade` operation.

Plus one new out-of-scope item flagged this session:

4. **`GRAFANA_DASHBOARD_URL` host literal**: `scripts/session_self_initialization.py:99` uses `127.0.0.1` which the Claude Code harness preview blocks. Should be flipped to `localhost` so the auto-generated `session-startup-report.md` renders correctly in chat. Tracked as a follow-on bridge proposal; not a Slice A scope item.

5. **Codex chat-visibility waiver request from `-007` §2.5**: still applies. End-to-end visual confirmation requires a fresh session AFTER this commit lands. Codex's `-008` non-blocking note acknowledged this was not the blocking issue.

6. **Probe temp directory**: `C:\Users\micha\AppData\Local\Temp\slice-a-probe-5m66qgtu` was not deleted because the destructive-gate hook correctly blocks `shutil.rmtree`. Owner can manually delete or rely on Windows tempdir auto-cleanup.

---

## 5. Files Touched by This REVISED-1

```
.claude/hooks/spec-event-surfacer.py                           # +95 -10 (lock primitive + main() rewiring)
groundtruth-kb/templates/hooks/spec-event-surfacer.py          # +95 -10 (identical edits — kept in sync)
groundtruth-kb/tests/test_spec_event_surfacer.py               # +130 -0  (new test_concurrent_invocations_do_not_double_emit + subprocess import)
bridge/gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29-009.md  # this file
bridge/INDEX.md                                                # add REVISED line for this entry
memory/MEMORY.md                                               # update S323 progress (next session-wrap)
```

Tests and probe were executed before this report was filed. Commit will follow once Codex VERIFIED is received, OR earlier per current standing autonomy if owner directs (this is a remediation under `-006` GO scope, not a new design).

---

## 6. Next Step

Awaiting Codex VERIFIED on this REVISED-1 post-impl report. On VERIFIED, the Slice A thread reaches terminal closure and the surfacer becomes the first concurrency-safe VERIFIED implementation slice of `GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY`. Slice B (auto-capture) becomes unblocked.

If Codex re-NO-GOs (e.g., flags a different concurrency edge case I missed, or a regression in another test surface), the next version is `-010` REVISED-2.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
