NEW

# Repair Dashboard Launcher Idempotence and PID Liveness Tracking (WI-3413)

bridge_kind: prime_proposal
Document: gtkb-dashboard-launcher-idempotence-pid-tracking
Version: 001 (NEW; reliability fast-lane defect fix)
Author: Prime Builder (Claude, harness B)
Date: 2026-06-01 UTC
Implements: SPEC-PROJECT-DASHBOARD-KPI-LINK-001; WI-3413
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3413
target_paths: ["groundtruth-kb/src/groundtruth_kb/dashboard.py", "groundtruth-kb/tests/test_dashboard.py"]
Recommended commit type: fix:
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 86d7f8a9-b8da-4284-b937-60eb056adda0
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context

## Claim

The local operations dashboard launcher (`groundtruth-kb/src/groundtruth_kb/dashboard.py`) has two coupled reliability defects: it is not idempotent, and it does not track PID liveness. Re-running `gt dashboard start` spawns duplicate processes and orphans the previously-tracked PIDs; `gt dashboard stop` and the start path both treat a stale PID of a dead process as if it referenced a live one.

Evidence (defect 1 — non-idempotent launch, no pre-spawn liveness check):

- `start_dashboard` at `groundtruth-kb/src/groundtruth_kb/dashboard.py:557-623` unconditionally spawns the refresh service via `subprocess.Popen(...)` at line 576 and Grafana via `subprocess.Popen(...)` at line 609 every time it is called. It never reads the existing PID files (`paths.pids_dir / "refresh-service.pid"` and `paths.pids_dir / "grafana.pid"`) before spawning, so it cannot detect an already-running instance.
- `_write_pid` at lines 616-617 then overwrites the prior PID with the newly-spawned PID. If a live instance was already running, its PID is silently lost from tracking, the process is orphaned (a `gt dashboard stop` will no longer find it), and a second Grafana/refresh process competes for the same port.

Evidence (defect 2 — PID tracking: non-atomic write, no liveness validation, stale-PID mishandling):

- `_write_pid` at `groundtruth-kb/src/groundtruth_kb/dashboard.py:1212-1213` writes the PID file directly (`path.write_text(f"{pid}\n", ...)`) with no atomic temp-file-plus-replace, leaving a partial-write window.
- `stop_dashboard` at lines 626-640 reads each PID file (line 633), and if it parses to an int it calls `_terminate_pid(pid)` (line 637) and reports the PID as "stopped" (line 638) without first checking whether the PID refers to a live process. A stale PID left behind from a previous (already-dead) process — or, worse, a PID number reused by an unrelated OS process — is acted on as if it were the dashboard. There is no liveness predicate anywhere in the module; the only PID-facing helpers are `_write_pid` (1212-1213) and `_terminate_pid` (1216-1224).
- `_terminate_pid` (1216-1224) signals the PID unconditionally (`taskkill /PID ... /T /F` on win32 at line 1219; `os.kill(pid, 15)` otherwise at line 1221). Combined with the missing liveness gate in `stop_dashboard`, a reused PID can be force-killed.

`psutil` is not available in the platform venv (confirmed: `import psutil` raises `ImportError`), so the fix uses stdlib only — consistent with the module's existing win32 `taskkill` / POSIX `os.kill` branch and its already-imported `os`, `subprocess`, and `sys`. The fix adds a liveness predicate, consults the existing PID files before spawning (idempotent launch), and writes PID files atomically — a genuine small single-concern defect repair with no new CLI surface, no new public API shape, and no new requirement.

## Specification Links

- SPEC-PROJECT-DASHBOARD-KPI-LINK-001 (verified, v2) — requires startup to display a live project dashboard link backed by a running dashboard. A launcher that spawns duplicate competing processes on the same port and orphans its own PID tracking undermines the "live dashboard" guarantee this spec depends on. This is the WI-3413 governing specification.
- GOV-RELIABILITY-FAST-LANE-001 — governs small single-concern defect fixes with no new behavior; this proposal claims fast-lane eligibility and maps the four criteria in the Fast-Lane Eligibility section.
- GOV-FILE-BRIDGE-AUTHORITY-001 — the change is filed through the bridge protocol (NEW -> Codex review -> GO/NO-GO -> implement -> post-impl -> VERIFIED); `bridge/INDEX.md` remains canonical workflow state.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — durable artifact preservation across proposal, deliberation, and report; this proposal and its report are the audit trail for the fix.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation; the Spec-To-Test Mapping carries this forward.

## Fast-Lane Eligibility

This thread claims eligibility under GOV-RELIABILITY-FAST-LANE-001 and the standing authorization PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING (covers-by-membership: WI-3413 is an active member of PROJECT-GTKB-RELIABILITY-FIXES, confirmed live in the `work_items` table — `origin=defect`, `priority=P2`, `project_name=PROJECT-GTKB-RELIABILITY-FIXES`, `resolution_status=open`, title "Dashboard launcher idempotence and PID tracking defects"). The four eligibility criteria:

1. Origin defect/regression — met. WI-3413 has `origin=defect`; the non-idempotent launch and stale-PID mishandling are defects against the "live dashboard" guarantee of SPEC-PROJECT-DASHBOARD-KPI-LINK-001, evidenced at the file:line references above.
2. No new API/CLI/behavior beyond removing the defect — met. No new CLI command, option, or flag is added; `gt dashboard start` / `gt dashboard stop` keep their signatures. `start_dashboard` and `stop_dashboard` keep their signatures and return types (`DashboardProcessInfo` / `list[int]`). The only behavioral change is the removal of the defect: a start that finds a live tracked process reuses it instead of spawning a duplicate, and a stop/start that finds a stale (dead) PID treats it as not-running instead of acting on it. The happy path (no existing process) is byte-equivalent to today.
3. No new requirement — met. SPEC-PROJECT-DASHBOARD-KPI-LINK-001 already requires a live, single dashboard; the defects are non-compliance with that existing requirement. No new GOV/SPEC/PB/ADR/DCL artifact is created.
4. Small single-concern scope — met. One concern: dashboard launcher idempotence and PID-liveness tracking. One source module (`dashboard.py`) plus its existing test file; no cross-cutting change.

## Prior Deliberations

- `bridge/gtkb-startup-dashboard-reachability-probe-001.md` (NEW) adds a SessionStart HTTP reachability probe of the *running* dashboard URL to `scripts/session_self_initialization.py`. That thread concerns whether the dashboard is *reachable* from the startup payload; it does NOT touch the launcher's spawn idempotence or PID tracking in `dashboard.py`. This proposal is complementary and non-overlapping — it fixes the launcher so a single, correctly-tracked instance is what the probe would find.
- `bridge/gtkb-cross-harness-trigger-import-repair-001.md` is the structural exemplar for a reliability-fast-lane defect fix under the same standing authorization; this proposal mirrors its scope discipline (one concern, one source file plus tests, no new behavior).
- The reliability fast-lane (GOV-RELIABILITY-FAST-LANE-001, PROJECT-GTKB-RELIABILITY-FIXES, PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING) is VERIFIED at `bridge/gtkb-reliability-fast-lane-006.md`; its owner-decision record is `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`. This proposal uses that standing authorization.

## Owner Decisions / Input

No owner decision required — standing fast-lane authorization PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING covers this by active project membership; no AskUserQuestion needed.

## Requirement Sufficiency

Existing requirements sufficient. SPEC-PROJECT-DASHBOARD-KPI-LINK-001 already requires a single live dashboard backing the startup link; the non-idempotent launch and stale-PID mishandling are non-compliance with that existing requirement. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a scoped reliability defect fix to one launcher source module plus its regression tests. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for a bulk action — is not applicable. The single work item cited (WI-3413) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## Scope

### IP-1: Idempotent launch with PID-liveness tracking (defect fix)

Three coupled changes within `groundtruth-kb/src/groundtruth_kb/dashboard.py`, all stdlib-only:

1. Add a private liveness predicate `_pid_alive(pid: int) -> bool` near the existing `_write_pid` / `_terminate_pid` helpers (around lines 1212-1224). On win32 it queries `tasklist /FI "PID eq <pid>" /NH` (via `subprocess.run(..., capture_output=True)`, mirroring the existing win32 `taskkill` branch) and returns whether the PID appears in the output. On POSIX it uses `os.kill(pid, 0)` and returns `True` unless `ProcessLookupError`/`OSError` (no signal sent; signal `0` is the standard liveness probe). No new dependency is introduced; `os` and `subprocess` are already imported.

2. Add a private helper `_read_live_pid(pid_file: Path) -> int | None` that reads a PID file, parses it, returns the PID only if `_pid_alive(...)` is true, and otherwise removes the stale file (`pid_file.unlink(missing_ok=True)`) and returns `None`. This centralizes "is the tracked process actually running" and stale-file cleanup.

3. Make `start_dashboard` (lines 557-623) idempotent: before each `subprocess.Popen` (refresh at 576, Grafana at 609), consult `_read_live_pid(...)` for the corresponding PID file. If a live PID is found, reuse it (do not spawn a duplicate) and carry that PID into the returned `DashboardProcessInfo`; only spawn when no live process is tracked. Make `_write_pid` (1212-1213) write atomically: write to a temp file in the same directory (`pids_dir`) then `os.replace(...)` into the final path, eliminating the partial-write window. Make `stop_dashboard` (626-640) call `_read_live_pid(...)` and only `_terminate_pid` / report PIDs that are confirmed live, while still cleaning up the PID file in every branch (live, dead, or unparseable) so stale files never linger.

The exact placement of the new helpers and the precise idempotence wiring inside `start_dashboard` (e.g., whether the live-reuse check is inlined or factored into a small per-process helper) will be finalized at implementation time within `dashboard.py`; the function signatures and return types of `start_dashboard` and `stop_dashboard` are unchanged.

### IP-2: Regression tests

Add tests to `groundtruth-kb/tests/test_dashboard.py` (the existing dashboard test module, which already exercises `gt dashboard start`/`stop` paths) covering:

- `_pid_alive` returns `True` for the current process PID (`os.getpid()`) and `False` for a PID known to be dead (a just-reaped child or a synthetic unused PID), monkeypatching the win32 `tasklist` call where needed so the test is platform-deterministic.
- `start_dashboard` is idempotent: when a live PID is already tracked in `refresh-service.pid` / `grafana.pid` (monkeypatched `_pid_alive` returns `True`), a second call does NOT spawn a new process (monkeypatched `subprocess.Popen` is asserted not called for the already-live process) and the tracked PID is preserved (not overwritten).
- Stale-PID handling: a PID file containing a dead PID (monkeypatched `_pid_alive` returns `False`) is treated as not-running — `start_dashboard` spawns a fresh process, and `stop_dashboard` does NOT call `_terminate_pid` for the dead PID but still removes the stale PID file.
- Atomic write: `_write_pid` produces a well-formed PID file via temp-file-plus-`os.replace`, and the final file content is the expected `"<pid>\n"`.

## Out Of Scope

- The SessionStart dashboard reachability probe in `scripts/session_self_initialization.py` — owned by `gtkb-startup-dashboard-reachability-probe`.
- The dashboard refresh service itself (`groundtruth-kb/src/groundtruth_kb/dashboard_service.py`), the Grafana asset generation, and the dashboard SQLite refresh logic — unchanged; this proposal touches only the launcher's spawn/stop/PID handling.
- Adding any new CLI command, option, or flag to `gt dashboard` — the fix is internal to `start_dashboard` / `stop_dashboard` / the PID helpers.
- Adding `psutil` or any new dependency — the liveness predicate is stdlib-only by design.
- Cross-host / multi-machine PID coordination — out of scope; the launcher is a single-host local tool.
- Any file outside `E:\GT-KB`. All target paths are within the `E:\GT-KB` project root.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/dashboard.py` — add `_pid_alive` and `_read_live_pid` helpers; make `start_dashboard` idempotent (pre-spawn live-PID check), make `_write_pid` atomic, and gate `stop_dashboard` on PID liveness with stale-file cleanup (IP-1).
- `groundtruth-kb/tests/test_dashboard.py` — regression coverage for idempotent launch, stale-PID handling, liveness predicate, and atomic PID write (IP-2).

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| SPEC-PROJECT-DASHBOARD-KPI-LINK-001 (idempotent launch) | Test: when a live PID is already tracked, `start_dashboard` does not spawn a duplicate and preserves the tracked PID, so a single live dashboard backs the startup link. |
| SPEC-PROJECT-DASHBOARD-KPI-LINK-001 (PID liveness / stale handling) | Test: a dead PID in the PID file is treated as not-running — `stop_dashboard` does not signal it and removes the stale file; `start_dashboard` spawns a fresh process. Test: `_pid_alive` is `True` for the live current PID and `False` for a dead PID. |
| SPEC-PROJECT-DASHBOARD-KPI-LINK-001 (atomic PID write) | Test: `_write_pid` writes via temp-file-plus-`os.replace` and the final file content is `"<pid>\n"`. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | The change is filed and verified through the bridge protocol; `bridge/INDEX.md` remains canonical. |
| GOV-RELIABILITY-FAST-LANE-001 | The Fast-Lane Eligibility section maps the four criteria; Loyal Opposition confirms eligibility. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus executed test commands and observed results. |

Implementation verification will run:
- `python -m pytest groundtruth-kb/tests/test_dashboard.py -q --tb=short`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dashboard-launcher-idempotence-pid-tracking`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dashboard-launcher-idempotence-pid-tracking`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] `start_dashboard` is idempotent: when a live PID is already tracked, no duplicate process is spawned and the tracked PID is preserved; covered by a test.
- [ ] A stale (dead) PID is treated as not-running: `stop_dashboard` does not signal it and cleans up the file; `start_dashboard` spawns a fresh process; covered by tests.
- [ ] `_pid_alive` correctly reports a live current PID as alive and a dead PID as not alive; covered by a test.
- [ ] `_write_pid` writes the PID file atomically (temp-file-plus-`os.replace`) with well-formed content; covered by a test.
- [ ] No new CLI command/option, no new public-API shape, and no new dependency (`psutil` not introduced); `start_dashboard` / `stop_dashboard` signatures and return types unchanged.
- [ ] `ruff check` and `ruff format --check` pass on the changed files.
- [ ] Post-implementation report carries observed command results.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Risk And Rollback

Risk R1 (low): the liveness predicate misreports a live process as dead (false negative), causing a duplicate spawn. Mitigation: `_pid_alive` uses the standard probes (`os.kill(pid, 0)` on POSIX; `tasklist` PID filter on win32, mirroring the existing `taskkill` branch); a dedicated test asserts the live current PID reads as alive. A false negative degrades to today's behavior (a spawn), never worse.

Risk R2 (low): the liveness predicate misreports a dead PID as live (false positive) because the OS reused the PID number for an unrelated process. Mitigation: PID reuse is a pre-existing, inherent limitation of PID-file tracking that this fix narrows rather than introduces — today `stop_dashboard` already signals any parseable PID with no liveness gate at all. The gate strictly reduces the blast radius (it only acts on PIDs that at least appear live), and `stop_dashboard` still scopes termination to the recorded PID files. No new failure mode is created.

Risk R3 (low): the atomic `os.replace` changes PID-file write semantics. Mitigation: `os.replace` is atomic on the same filesystem (`pids_dir`) and produces the identical final file content; only the partial-write window is removed. A test asserts the final content.

Risk R4 (low): the idempotence change alters the `DashboardProcessInfo` returned when an existing live process is reused. Mitigation: the reused branch returns the already-tracked PID(s) in the same `DashboardProcessInfo` shape; the dataclass and field set (`grafana_pid`, `refresh_pid`, `grafana_url`, `refresh_url`) are unchanged. A test asserts the reuse path returns the preserved PID.

Rollback: the change is contained to `dashboard.py` plus the test file. Reverting `groundtruth-kb/src/groundtruth_kb/dashboard.py` to its prior version restores the prior non-idempotent behavior; the new helpers are additive and independently revertible. No data migration and no canonical-artifact mutation are involved.

## Loyal Opposition Asks

1. Confirm the stdlib-only liveness predicate (`os.kill(pid, 0)` on POSIX; `tasklist` PID filter on win32) is the right structural choice versus adding `psutil`, given `psutil` is absent from the platform venv and the module already uses the win32 `taskkill` / POSIX `os.kill` pattern.
2. Confirm the fast-lane eligibility claim — that adding a liveness gate, a pre-spawn live-PID check, and an atomic PID write removes the defect without adding new behavior (the happy path stays byte-equivalent; `start_dashboard` / `stop_dashboard` signatures and return types are unchanged).
3. Confirm the scope boundary — that bundling idempotent launch and PID-liveness tracking in one thread (both being launcher reliability defects in the same module, and the substance of WI-3413's title) is the correct single-concern boundary, leaving the reachability probe and the refresh service untouched.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
