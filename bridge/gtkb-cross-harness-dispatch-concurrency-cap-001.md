NEW
author_identity: claude
author_harness_id: B
author_session_context_id: 28d30cb5-bfc4-4a97-acca-57d36d002533
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

# Defect-Fix Proposal - Hard Global Concurrency Cap on Dispatched Headless Harness Processes (WI-4472)

bridge_kind: prime_proposal
Document: gtkb-cross-harness-dispatch-concurrency-cap
Version: 001
Date: 2026-06-12 UTC

Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4472
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_dispatch_concurrency_cap.py"]

## Claim

The cross-harness event-driven trigger (`scripts/cross_harness_bridge_trigger.py`) has no upper bound on the number of live dispatched headless harness processes. On 2026-06-11 this produced a dispatch storm: ~300 hung `codex` dispatch sessions accumulated and exhausted the workstation (~45 GB). Root cause (per WI-4472): a dispatched session that hangs stops refreshing its active-session lock; after the 120 s `GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS` window the trigger treats the target as free and re-dispatches; and the per-recipient circuit breaker only counts launch FAILURES (`failure_count`), so a session that *launched* successfully but then hung is never throttled. Nothing caps the total number of live processes.

This proposal adds a hard global concurrency cap in the trigger's spawn path: count the live dispatched headless harness processes and, when the count is at/above a configurable cap, skip the dispatch fail-closed (no spawn) with a durable logged audit record. This is the durable root-cause fix that would let the `GTKB_NO_CROSS_HARNESS_TRIGGER` kill-switch be safely retired and event-driven dispatch re-enabled with a safety ceiling.

## Defect / Reproduction

**Root cause (code).** `_spawn_harness` (`scripts/cross_harness_bridge_trigger.py:1717`) fire-and-forget launches `subprocess.Popen(wrapped_command, ...)` (`:1876`), wrapping the harness command with `scripts/run_with_status.py`, which writes `<dispatch_id>.exit_code` only when the child process EXITS. A hung child therefore leaves a permanently-pending status file and is never accounted for. The only throttle is the per-recipient circuit breaker, which trips on `failure_count` (launch failures) - a hung-but-launched session increments nothing. The active-session suppression gate (`_target_active_session_present`, TTL `GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS=120`, `:1704`) frees the target once the hung session stops refreshing its lock, so re-dispatch resumes. With reciprocal dispatch and multiple recipients, live processes grow without bound.

**Incident (2026-06-11).** ~300 hung codex dispatch sessions; ~45 GB workstation exhaustion; mitigated only by the manual `GTKB_NO_CROSS_HARNESS_TRIGGER=1` kill-switch, which disables dispatch entirely.

**Why the existing controls miss it.** (1) Circuit breaker = failure-count only; hung != failed. (2) Active-session TTL = per-target liveness, not a global process ceiling. (3) No code path counts total live dispatched processes.

## In-Root Placement Evidence

Both target paths are inside `E:\GT-KB`: `scripts/cross_harness_bridge_trigger.py` and `platform_tests/scripts/test_dispatch_concurrency_cap.py`.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement set - `bridge-essential.md` (dispatch must be activity-driven and must not produce blind, resource-exhausting repetition; the S308 lesson) plus `GOV-FILE-BRIDGE-AUTHORITY-001` (dispatch is monitoring/dispatch infrastructure only; `bridge/INDEX.md` remains canonical) - already constrains the corrected behavior. The cap restores the "automation must not exhaust the host" invariant the 2026-06-11 incident violated. No new or revised requirement is required before implementation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - **Primary.** The cross-harness trigger is dispatch infrastructure subordinate to `bridge/INDEX.md`; the cap bounds its resource footprint without changing workflow state.
- `.claude/rules/bridge-essential.md` - the S308 lesson (blind, activity-independent automation that repeats work without information is the defect); the cap is the missing ceiling that prevents host exhaustion.
- `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` - dispatch-target/active-session semantics the cap composes with (the cap is additive; it does not alter active-session suppression).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changes are in-root platform paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant cross-cutting specs here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps the cap behavior to executable tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project / Work Item / Project Authorization metadata present above.
- `GOV-STANDING-BACKLOG-001` - WI-4472 is the standing-backlog work item, an active member of PROJECT-GTKB-RELIABILITY-FIXES.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the 2026-06-11 incident is captured as WI-4472; this proposal is the artifact-lifecycle progression from captured defect to scoped fix.

## Prior Deliberations

- WI-4472 (this work item) - records the 2026-06-11 incident and the prescribed fix (hard global concurrency cap in the spawn path).
- `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md` (VERIFIED) - the active-session suppression contract the cap composes with; the cap is a second, independent safety layer (the suppression gate is per-target liveness, the cap is a global process ceiling).
- `bridge/gtkb-dispatch-retry-delay-livelock-fix-004.md` (VERIFIED, this session) - the retry-delay livelock fix; related dispatch-reliability surface but a distinct failure mode (retry timing vs. unbounded live-process count).
- `.claude/rules/bridge-essential.md` S308 incident history - the precedent that blind, activity-independent dispatch that exhausts the host is the defect class this WI closes.
- Deliberation Archive search (2026-06-12) for "dispatch concurrency cap / dispatch storm / live process limit" returned no prior decision specific to a global process ceiling; this is the first treatment.

## Owner Decisions / Input

- **AskUserQuestion (2026-06-12, this session):** owner selected WI-4472 ("dispatch-storm root-cause fix") as the next standing-backlog item to work, and earlier chose "continue solo" with the interactive session driving. Recorded in `memory/pending-owner-decisions.md` (detected_via: ask_user_question). This is the owner direction to propose WI-4472.
- **Project authorization:** `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (active, project-wide; `source` + `test_addition` + `hook_upgrade`; owner authorization `DELIB-S351`), covering WI-4472 via active project membership.
- No NEW owner decision is required for implementation beyond the standing authorization + the per-item bridge GO.

## Proposed Scope

**IP-1 - Live dispatched-process accounting (`scripts/cross_harness_bridge_trigger.py`).**

- In `_spawn_harness`, immediately after a successful `subprocess.Popen`, write a `<dispatch_id>.pid` sidecar into the dispatch-runs dir containing the child PID. (The existing `<dispatch_id>.exit_code` status file is written by `run_with_status.py` only on child EXIT.)
- Add `_pid_alive(pid) -> bool`: cross-platform liveness. Prefer `psutil.pid_exists(pid)` when importable; fall back to `ctypes` `OpenProcess` on Windows and `os.kill(pid, 0)` on POSIX. Unknown/parse failure returns False (fail-closed-to-not-alive so a malformed sidecar never inflates the count).
- Add `_count_live_dispatched_processes(runs_dir) -> int`: for each `<id>.pid` sidecar, a dispatch is LIVE iff its `<id>.exit_code` is absent/empty (not yet exited) AND `_pid_alive(pid)`. Sum the live count. (Sidecars whose process has exited or died are not counted; a periodic prune of stale sidecars is included so the runs dir does not grow unbounded.)

**IP-2 - Hard global concurrency cap gate in the spawn path.**

- New env var `GTKB_MAX_LIVE_DISPATCHED_PROCESSES` (default `8`; parsed fail-safe to the default on invalid/non-positive input). A documented, conservative ceiling well below the ~300 incident peak.
- Early in `_spawn_harness` (after the `dry_run` short-circuit, before authorization issuance and `Popen`), compute `live = _count_live_dispatched_processes(runs_dir)`. If `live >= cap`, do NOT spawn: record a `concurrency_cap_reached` entry to `dispatch-failures.jsonl` (with `live_count`, `cap`, `recipient`, `dispatch_id`) and return `{launched: False, reason: "concurrency_cap_reached", live_count, cap}`. Fail-closed: the missing-ceiling gap is closed by refusing to add another process when at/over the cap.
- The cap is additive and independent of the circuit breaker and active-session suppression; it throttles the hung-but-launched class those controls miss.

**IP-3 - Tests (`platform_tests/scripts/test_dispatch_concurrency_cap.py`; new file = clean test_addition).**

- `_count_live_dispatched_processes`: counts a pending sidecar with an alive PID as live; does NOT count one whose `.exit_code` is written; does NOT count one whose PID is dead (uses a guaranteed-dead PID / monkeypatched `_pid_alive`).
- Cap gate: with `live >= cap` (forced via monkeypatched counter or seeded sidecars), `_spawn_harness` returns `launched=False, reason="concurrency_cap_reached"`, writes the `dispatch-failures.jsonl` audit entry, and does NOT call `Popen` (assert via monkeypatched/patched Popen sentinel).
- Below cap: the spawn path proceeds (dry-run path asserted so no real process is launched in the test).
- Env override: `GTKB_MAX_LIVE_DISPATCHED_PROCESSES` changes the effective cap; invalid value falls back to the default.

## Specification-Derived Verification Plan

| Spec / requirement | Derived test | Command |
|---|---|---|
| `bridge-essential.md` (host-exhaustion ceiling) + WI-4472 | `test_cap_blocks_dispatch_when_at_or_over_limit` (fail-closed, no Popen, logged) | `python -m pytest platform_tests/scripts/test_dispatch_concurrency_cap.py -q` |
| WI-4472 (live-process accounting) | `test_count_live_excludes_exited_and_dead_pids` | same |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (infra only; audit trail) | `test_cap_skip_records_dispatch_failure_audit` | same |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | env-override + default-fallback tests; lint + format gates | same; `ruff check <files>`; `ruff format --check <files>` |

## Acceptance Criteria

1. `_count_live_dispatched_processes` counts only pending dispatches with a live PID; exited or dead-PID dispatches are excluded.
2. When live count >= `GTKB_MAX_LIVE_DISPATCHED_PROCESSES`, `_spawn_harness` skips the dispatch (no `Popen`), returns `reason="concurrency_cap_reached"`, and records a durable `dispatch-failures.jsonl` audit entry.
3. Below the cap, the spawn path proceeds unchanged (existing dispatch behavior preserved).
4. The cap default is `8`; the env var overrides it; invalid values fall back to the default.
5. New tests pass; `ruff check` and `ruff format --check` pass on every changed Python file; the pre-existing unrelated failures in `test_cross_harness_bridge_trigger.py` are NOT in scope and are not regressed by this change (verified by running that suite before/after).
6. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-cross-harness-dispatch-concurrency-cap` reports `missing_required_specs: []`; clause preflight reports no blocking gaps.

## Risks / Rollback

- **Risk - cap set too low throttles legitimate concurrent dispatch.** Mitigation: default `8` is well above normal steady-state (2 roles x a few harnesses) and far below the ~300 incident; env-tunable; the skip is logged so under-provisioning is visible.
- **Risk - `psutil` unavailable in some environment.** Mitigation: `_pid_alive` falls back to `ctypes`/`os.kill`; unknown returns False (fail-closed). The counter degrades safely.
- **Risk - `.pid` sidecars accumulate in the runs dir.** Mitigation: prune sidecars whose process has exited (exit_code present) or whose PID is dead as part of the count pass.
- **Risk - editing the live dispatch path during active dispatch.** Mitigation: changes are additive (new functions + an early guard); the hot path is unchanged below the cap; tested with a sentinel Popen so no real process is launched in tests. Rollback: revert the trigger change (restores prior unbounded behavior) and delete the new test file; no state migration.

## Files Expected To Change

- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_dispatch_concurrency_cap.py` (new)

## Recommended Commit Type

`fix` - repairs a P1 host-exhaustion defect with no new user-facing capability surface (the cap is a safety ceiling on existing dispatch behavior).

## Bridge Protocol Compliance

Filed at `bridge/gtkb-cross-harness-dispatch-concurrency-cap-001.md` with a matching `NEW` status line inserted at the top of this Document's version list in `bridge/INDEX.md`; append-only. `GOV-FILE-BRIDGE-AUTHORITY-001` honored; `bridge/INDEX.md` remains the canonical workflow queue. The implementation-start packet will be minted from the GO against the project-wide standing PAUTH under `source` + `test_addition`.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
