NEW

# Implementation Report — Dashboard Launcher Idempotence and PID Liveness Tracking (WI-3413)

bridge_kind: implementation_report
Document: gtkb-dashboard-launcher-idempotence-pid-tracking
Version: 003
Responds to: bridge/gtkb-dashboard-launcher-idempotence-pid-tracking-002.md (GO)
Author: Prime Builder (Claude, harness B; durable PB per harness-registry.json; session-stated PB via ::init gtkb pb)
Date: 2026-06-03 UTC
Recommended commit type: fix

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 45299969-65c1-495e-b4a7-1cecaa373ae1
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style, durable Prime Builder per harness-registry.json (B status=active role=[prime-builder]); /loop dynamic-mode iteration 5

Implements: SPEC-PROJECT-DASHBOARD-KPI-LINK-001; WI-3413
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3413
target_paths: ["groundtruth-kb/src/groundtruth_kb/dashboard.py", "groundtruth-kb/tests/test_dashboard.py"]

## Summary

The GO `-002` (Codex, 2026-06-01) authorized the bounded WI-3413 reliability fix to the dashboard launcher. This report records the completed implementation, the executed spec-derived tests, and the code-quality gate results.

Both IP-1 (idempotent launch + PID-liveness tracking + atomic PID write) and IP-2 (regression tests) are landed within the two GO-approved target paths. No CLI surface, public-API shape, or dependency was added; `start_dashboard` / `stop_dashboard` keep their signatures and return types.

**Bridge-INDEX recovery note:** the GO'd thread had been pruned from `bridge/INDEX.md` (now ~1471 lines, far past the ~200-line maintenance threshold) before implementation, stranding a valid GO. This session re-promoted the `gtkb-dashboard-launcher-idempotence-pid-tracking` entry (`GO: -002`, `NEW: -001`) to the top of the live INDEX before minting the implementation-start packet, then prepended this report's `NEW: -003` line. No prior version was deleted or rewritten (append-only preserved).

## Implementation-Start Authorization

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-dashboard-launcher-idempotence-pid-tracking
```

Observed: `latest_status: GO`; `go_file: bridge/gtkb-dashboard-launcher-idempotence-pid-tracking-002.md`; `packet_hash: sha256:f67156ba1b86bd763e7110bfe057efdcd16149539009c2005845ef0d51ba925b`; project authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` active, `work_item_id: WI-3413`, `requirement_sufficiency: sufficient`. Packet expires `2026-06-04T06:21:10Z`.

## IP-1 — Idempotent Launch + PID-Liveness Tracking (landed in dashboard.py)

Three coupled changes, all stdlib-only (`psutil` remains absent from the platform venv):

1. **`_pid_alive(pid: int) -> bool`** (new helper near the existing PID helpers): stdlib liveness probe. On win32 it queries `tasklist /FI "PID eq <pid>" /NH` (mirroring the existing win32 `taskkill` branch) and returns whether the PID appears as a standalone whitespace token; on POSIX it uses `os.kill(pid, 0)` (existence/permission probe, no signal delivered), returning `True` unless `ProcessLookupError`/`OSError` (and `True` on `PermissionError`, since a process owned by another user still exists). Returns `False` for `pid <= 0`.

2. **`_read_live_pid(pid_file: Path) -> int | None`** (new helper): reads and parses a PID file, returns the PID only if `_pid_alive(...)` is true, otherwise removes the stale file (`unlink(missing_ok=True)`) and returns `None`. Centralizes "is the tracked process actually running" plus stale-file cleanup. Missing file → `None`; unparseable content → file removed, `None`.

3. **`start_dashboard` made idempotent**: before each `subprocess.Popen` (refresh, then Grafana), the function consults `_read_live_pid(...)` for the corresponding PID file. When a live PID is tracked it is reused (no duplicate spawn, log handle not opened) and carried into the returned `DashboardProcessInfo`; only when no live process is tracked does it spawn and `_write_pid` the fresh PID. The no-live-process path is behavior-equivalent to the prior unconditional spawn (both processes spawned, both logs opened, both PIDs written).

4. **`_write_pid` made atomic**: writes to a uniquely-named temp file in the same directory via `tempfile.mkstemp(dir=pids_dir, ...)`, then `os.replace(...)` into the final path (atomic on the same filesystem). Eliminates the partial-write window; final content is identical (`"<pid>\n"`). On `OSError` the temp file is cleaned up (`contextlib.suppress(OSError)`) and the error re-raised.

5. **`stop_dashboard` gated on liveness**: only PIDs confirmed live (`_pid_alive(pid)`) are `_terminate_pid`'d and reported; stale (dead) or unparseable PID files are cleaned up without signalling, so a reused PID number belonging to an unrelated OS process is not force-killed. The PID file is removed in every branch (unparseable, dead, live-and-terminated).

New imports: `contextlib` (for the temp-file cleanup suppress) and `tempfile` (for the atomic write) — both stdlib; no new third-party dependency.

## IP-2 — Regression Tests (landed in test_dashboard.py)

12 new tests added to the existing dashboard test module:

- `test_pid_alive_true_for_current_process` — `_pid_alive(os.getpid())` is `True`.
- `test_pid_alive_nonpositive_returns_false` — `_pid_alive(0)` / `_pid_alive(-1)` are `False`.
- `test_pid_alive_win32_branch_parses_tasklist` — monkeypatched `tasklist` output: a match row → `True`; an "INFO: No tasks..." line → `False`.
- `test_pid_alive_posix_branch_uses_signal_zero` — monkeypatched `os.kill`: no-raise → `True`; `ProcessLookupError` → `False`.
- `test_write_pid_is_atomic_and_wellformed` — final content `"4321\n"`; no `.tmp` leftover.
- `test_read_live_pid_returns_pid_when_alive` — live PID returned, file preserved.
- `test_read_live_pid_clears_stale_dead_pid` — dead PID → `None`, file removed.
- `test_read_live_pid_unparseable_returns_none` — bad content → `None`, file removed.
- `test_read_live_pid_missing_file_returns_none` — missing file → `None`.
- `test_start_dashboard_idempotent_reuses_live_pids` — both tracked PIDs live → `subprocess.Popen` NOT called; returned `DashboardProcessInfo` carries the preserved PIDs; PID files unchanged.
- `test_start_dashboard_spawns_when_pids_stale` — both tracked PIDs dead → `Popen` called twice; fresh PIDs written.
- `test_stop_dashboard_skips_dead_pid_and_cleans_file` — dead PIDs never signalled; both PID files removed.
- `test_stop_dashboard_terminates_live_pid_and_cleans_file` — live PID terminated and reported; PID file removed.

The tests monkeypatch the platform-specific liveness mechanism and `subprocess.Popen` for platform-deterministic, side-effect-free execution (no real processes spawned).

## Specification Links

Carried forward from `-001`; all governing specifications are cited concretely below.

- `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` (verified, v2) — the WI-3413 governing specification; a launcher that spawns duplicate competing processes and orphans its PID tracking undermines the "live dashboard" guarantee.
- `GOV-RELIABILITY-FAST-LANE-001` — governs small single-concern defect fixes with no new behavior.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol; `bridge/INDEX.md` canonical workflow state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable artifact preservation across proposal + report.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every relevant governing specification is cited in this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification is derived from the linked specifications and executed against the implementation (spec-to-test mapping below).

## Prior Deliberations

Carried forward from the `-001` proposal:

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — owner-decision record establishing the reliability fast lane (PROJECT-GTKB-RELIABILITY-FIXES + the standing authorization + GOV-RELIABILITY-FAST-LANE-001) under which this fix is routed.
- Bridge thread `gtkb-startup-dashboard-reachability-probe-001` — complementary, non-overlapping: it probes whether the running dashboard is reachable from the startup payload; this fix ensures a single, correctly-tracked instance is what the probe would find.
- Bridge thread `gtkb-cross-harness-trigger-import-repair-001` — structural exemplar for a reliability-fast-lane defect fix under the same standing authorization (one concern, one source file plus tests, no new behavior).
- `gt deliberations search "WI-3413 dashboard launcher idempotence"` returned `[]` at GO time (per `-002`); the proposal cites the relevant fast-lane and dashboard bridge history directly.

## Owner Decisions / Input

No owner decision required. The standing fast-lane authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) covers WI-3413 by active project membership; per `GOV-RELIABILITY-FAST-LANE-001` no per-fix deliberation or formal-artifact-approval packet is required. The bridge GO `-002` and this report's verification remain the governing controls. Codex confirmed "Owner Action Required: None" in `-002`.

## Spec-To-Test Mapping

Executed spec-derived verification per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

| Spec / governing surface | Verification | Command | Observed |
|---|---|---|---|
| SPEC-PROJECT-DASHBOARD-KPI-LINK-001 (idempotent launch) | `start_dashboard` reuses a live tracked PID, no duplicate spawn, PID preserved | `python -m pytest groundtruth-kb/tests/test_dashboard.py -q` | `test_start_dashboard_idempotent_reuses_live_pids` PASS |
| SPEC-PROJECT-DASHBOARD-KPI-LINK-001 (PID liveness / stale handling) | dead PID treated as not-running by both start and stop; `_pid_alive` correct | same | `test_start_dashboard_spawns_when_pids_stale`, `test_stop_dashboard_skips_dead_pid_and_cleans_file`, `test_pid_alive_*` PASS |
| SPEC-PROJECT-DASHBOARD-KPI-LINK-001 (atomic PID write) | `_write_pid` temp-file-plus-`os.replace`; final content `"<pid>\n"`; no leftover | same | `test_write_pid_is_atomic_and_wellformed` PASS |
| GOV-RELIABILITY-FAST-LANE-001 | no new CLI/API/dependency; signatures unchanged | code review + `ruff` | confirmed; `start_dashboard`/`stop_dashboard` signatures unchanged |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | this report carries executed commands + observed results | this section | satisfied |
| GOV-FILE-BRIDGE-AUTHORITY-001 | filed/verified through bridge; INDEX canonical | INDEX re-promotion + this report | satisfied |

## Executed Verification Commands + Observed Results

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_dashboard.py -q -p no:cacheprovider
# 17 passed in 2.73s  (5 pre-existing + 12 new)

groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/dashboard.py groundtruth-kb/tests/test_dashboard.py
# All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/dashboard.py groundtruth-kb/tests/test_dashboard.py
# 2 files already formatted
```

Both code-quality gates (lint AND format) were run separately per `.claude/rules/file-bridge-protocol.md` § Pre-File Code-Quality Gates.

## PID-Reuse Caveat (per GO -002 Implementation Discipline item 4)

PID liveness does not prove process identity. The OS can reuse a PID number for an unrelated process; `_pid_alive` reports such a reused PID as alive. This fix **narrows** the stale-dead-PID failure mode (a dead PID is no longer signalled or treated as running) and prevents duplicate tracked starts, but it does not fully solve PID reuse, which would require stronger process-identity tracking (e.g., creation-time or a cookie file) that is out of WI-3413's single-concern scope. `stop_dashboard` still scopes termination to the recorded PID files, so the blast radius is strictly reduced versus the prior unconditional-signal behavior.

## Acceptance Criteria Status

- [x] Loyal Opposition returned GO on the proposal (-002).
- [x] `start_dashboard` idempotent: live tracked PID reused, no duplicate spawn, PID preserved — test covered.
- [x] Stale (dead) PID treated as not-running by start and stop; file cleaned — tests covered.
- [x] `_pid_alive` correct for live current PID and dead PID — tests covered (both branches).
- [x] `_write_pid` atomic (temp-file-plus-`os.replace`), well-formed content — test covered.
- [x] No new CLI command/option, no new public-API shape, no new dependency; signatures unchanged.
- [x] `ruff check` and `ruff format --check` pass on both changed files.
- [x] This report carries observed command results.
- [ ] Loyal Opposition returns VERIFIED (pending this report's review).

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/dashboard.py` — `+contextlib`, `+tempfile` imports; new `_pid_alive` + `_read_live_pid` helpers; atomic `_write_pid`; idempotent `start_dashboard`; liveness-gated `stop_dashboard`.
- `groundtruth-kb/tests/test_dashboard.py` — 12 new regression tests + test doubles (`_RecordingPopen`, `_FakeProc`, `_make_paths`, `_stub_launch_environment`).
- `bridge/INDEX.md` — re-promoted the pruned thread entry; prepended `NEW: -003`.

## Bridge INDEX Update Evidence

The `gtkb-dashboard-launcher-idempotence-pid-tracking` entry was re-promoted to the top of `bridge/INDEX.md` with its true prior state (`GO: -002`, `NEW: -001`), then `NEW: bridge/gtkb-dashboard-launcher-idempotence-pid-tracking-003.md` prepended for this report. Append-only preserved; `bridge/INDEX.md` remains canonical per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` — repairs broken launcher behavior (non-idempotent spawn, stale-PID mishandling) with no new capability surface. Net diff is a defect repair plus its regression tests.

## Next Steps for Loyal Opposition

Verify this report against GO `-002`. Re-run the applicability + clause preflights against `-003`, the dashboard test suite, and both ruff gates; confirm the PID-reuse caveat is documented (it is, above).

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
