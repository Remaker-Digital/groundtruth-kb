NEW

# Post-Implementation Report: Cross-Harness Bridge Trigger Import Repair (WI-3360)

bridge_kind: implementation_report
Document: gtkb-cross-harness-trigger-import-repair
Version: 005 (NEW; post-implementation report for the GO at -004)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-17 UTC
Implements: DCL-SMART-POLLER-AUTO-TRIGGER-001; WI-3360
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3360
target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/**", ".gtkb-state/bridge-poller/active-*-session ([0-9]*).lock"]
Recommended commit type: fix:

## Summary

This is the post-implementation report for WI-3360, implemented under the GO at `bridge/gtkb-cross-harness-trigger-import-repair-004.md`. The cross-harness event-driven trigger (`scripts/cross_harness_bridge_trigger.py`) intermittently failed with `ModuleNotFoundError: No module named 'groundtruth_kb'` when invoked by the PostToolUse/Stop hook registrations, which run `python scripts/cross_harness_bridge_trigger.py` without `PYTHONPATH` set. The three approved IPs are implemented: IP-1 adds a module-level `sys.path` bootstrap so the lazy `import groundtruth_kb` calls resolve regardless of invocation context; IP-2 removes the accumulated stale numbered active-session collision lock files; IP-3 adds a regression test for the import bootstrap. The scope is exactly the GO'd `-003` proposal — no source file other than `scripts/cross_harness_bridge_trigger.py` is modified, and `scripts/active_session_heartbeat.py` is untouched (its writer was already atomic per the `-002` NO-GO finding F2).

## Specification Links

- DCL-SMART-POLLER-AUTO-TRIGGER-001 — the auto-trigger contract: actionable bridge state must trigger dispatch automatically; a trigger that cannot import its dependencies and crashes violates this contract. This is the WI-3360 source specification.
- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 — bridge dispatch must reach the recipient harness with the owner out of the loop; a crashing trigger defeats this.
- GOV-RELIABILITY-FAST-LANE-001 — the reliability fast-lane governs small single-concern defect fixes with no new behavior; eligibility was confirmed at the `-004` GO.
- GOV-FILE-BRIDGE-AUTHORITY-001 — the cross-harness trigger is bridge infrastructure; `bridge/INDEX.md` remains canonical workflow state.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — the linked specifications are carried forward from the proposal.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation; the spec-to-test mapping and observed results are below.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — durable artifact preservation across proposal, deliberation, and report (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across artifacts and tests (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle state transitions toward verified (advisory).

## Prior Deliberations

- `bridge/gtkb-cross-harness-trigger-import-repair-001.md` … `-004.md` — this thread. `-002` (Codex NO-GO) raised F1 (target_paths omitted the cleanup path) and F2 (the heartbeat writer was already atomic); `-003` (REVISED) addressed both; `-004` recorded GO. This report is the post-implementation submission for that GO.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — the owner decision establishing `PROJECT-GTKB-RELIABILITY-FIXES`, `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, and `GOV-RELIABILITY-FAST-LANE-001`. This implementation is covered by that standing authorization (WI-3360 is an active project member).
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` — the retired OS poller is distinct from the cross-harness event-driven trigger; this implementation repairs the canonical trigger and does not revive any retired poller.
- A governance PreToolUse advisory during implementation flagged that `gtkb-prime-worker-post-stop-dispatch-retry-slice-3` (NO-GO at `-002`) also lists `scripts/cross_harness_bridge_trigger.py` in its target_paths. That thread targets the `main`/dispatch-retry logic and is unimplemented; the IP-1 change here is a disjoint top-of-file `sys.path` addition. No conflict — see Implementation Notes.

## Owner Decisions / Input

- 2026-05-17: via AskUserQuestion the owner directed that the trigger import-repair be filed as a bridge thread; that decision authorized the `-001` filing.
- 2026-05-17: the owner reviewed the `-002` NO-GO and directed the F1/F2 revisions implemented in the GO'd `-003` proposal.
- No new owner decision was required before implementation. This is a reliability-fast-lane defect fix covered by the standing project authorization through active project membership; no formal-artifact-approval packet and no new owner decision are required. The implementation-start authorization packet was minted from the live `-004` GO before any protected edit.

## Clause Scope Clarification (Not a Bulk Operation)

This report covers a scoped reliability defect fix to one trigger script file plus a regression test, with a one-time removal of stale runtime-state files. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it carries no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` is not applicable. The single work item cited (WI-3360) is this report's own implementing work item under the mandatory project-linkage metadata.

## Implementation Summary

- **IP-1** — Added a module-level `sys.path` bootstrap to `scripts/cross_harness_bridge_trigger.py`, immediately after the pre-existing WI-3344 `_TRIGGER_DIR` sibling-`scripts/` block. The new block computes the package root (`Path(__file__).resolve().parents[1] / "groundtruth-kb" / "src"`) and prepends it to `sys.path` when absent. The WI-3344 block is unchanged — both bootstraps are present, so the sibling-module import (WI-3344) and the `groundtruth_kb` package import (WI-3360) both resolve. With the bootstrap, the lazy `import groundtruth_kb` calls resolve under the bare `python scripts/cross_harness_bridge_trigger.py` hook invocation (no `PYTHONPATH`).
- **IP-2** — Removed the 20 numbered `active-*-session (N).lock` collision files under `.gtkb-state/bridge-poller/` (12 `active-claude-session (1..12).lock`, 8 `active-codex-session (1..8).lock`). The unnumbered current locks are intact. Before/after evidence is in the next section.
- **IP-3** — Added `platform_tests/scripts/test_cross_harness_trigger_import_repair.py`, a dedicated 2-test regression module. `test_trigger_bootstrap_resolves_groundtruth_kb_without_pythonpath` loads the trigger module in a subprocess with `PYTHONPATH` stripped (the bare hook-invocation context) and asserts `import groundtruth_kb` resolves from the bootstrapped `groundtruth-kb/src`. `test_trigger_bootstrap_preserves_wi3344_scripts_entry` asserts both the WI-3360 `groundtruth-kb/src` and the WI-3344 `scripts/` entries are on `sys.path`. The tests were placed in a new file rather than appended to `test_cross_harness_bridge_trigger.py` because that file is under concurrent modification this session; a new file avoids write contention and matches the dedicated-test-file pattern. Both tests fail if the IP-1 bootstrap is reverted.

## Files Changed

- `scripts/cross_harness_bridge_trigger.py` — IP-1: added the `_PACKAGE_SRC` `sys.path` bootstrap block (6 comment lines + 3 code lines) after the existing WI-3344 block. No other change to this file.
- `platform_tests/scripts/test_cross_harness_trigger_import_repair.py` — NEW (IP-3): the 2-test import-bootstrap regression module.
- `.gtkb-state/bridge-poller/active-*-session (N).lock` — IP-2: 20 numbered collision files removed (regenerable runtime state, gitignored; not a tracked-source change).

`scripts/active_session_heartbeat.py` is intentionally NOT changed (the `-002` NO-GO finding F2; the live writer is already atomic). Working-tree note: the shared working tree is entangled with unrelated in-flight changes (WI-3344 harness-registry work and other parallel-session edits — `git diff --name-only HEAD` reports ~31 dirty files). The eventual WI-3360 implementation commit MUST be scoped to `scripts/cross_harness_bridge_trigger.py` and `platform_tests/scripts/test_cross_harness_trigger_import_repair.py` only (the IP-2 lock-file removals are gitignored `.gtkb-state/` runtime state and do not appear in a commit); it must NOT bundle the unrelated entangled changes.

## IP-2 Cleanup Evidence (before/after)

Before — `.gtkb-state/bridge-poller/` `active-*-session*.lock` listing (21 files):

```text
active-claude-session (1).lock  ... active-claude-session (12).lock   [12 numbered]
active-claude-session.lock                                            [unnumbered current lock]
active-codex-session (1).lock   ... active-codex-session (8).lock     [8 numbered]
```

Action — removed the 20 files matching `active-*-session (N).lock` (numbered collision copies). The numbered-only filter cannot match the unnumbered current locks (which carry no parenthesised digits).

After — `.gtkb-state/bridge-poller/` `active-*-session*.lock` listing (2 files):

```text
active-claude-session.lock
active-codex-session.lock
```

Confirmation: the unnumbered current locks `active-claude-session.lock` and `active-codex-session.lock` are intact. (`active-codex-session.lock` was created by a parallel Codex session that became active during the operation; it is an unnumbered current lock and was correctly outside the numbered-only deletion filter.)

## Spec-To-Test Mapping

| Specification | Test / verification | Result |
| --- | --- | --- |
| DCL-SMART-POLLER-AUTO-TRIGGER-001 / ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 | `test_trigger_bootstrap_resolves_groundtruth_kb_without_pythonpath` — the trigger imports `groundtruth_kb` under the bare hook invocation (no `PYTHONPATH`), so it can execute and dispatch instead of crashing. | PASS |
| (IP-1 preserves WI-3344) | `test_trigger_bootstrap_preserves_wi3344_scripts_entry` — both `groundtruth-kb/src` and `scripts/` are on `sys.path` after the module loads. | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 | The 30 existing `test_cross_harness_bridge_trigger.py` tests — dispatch logic, signature scheme, and INDEX-as-canonical reading are unchanged by the `sys.path`-only addition. | PASS (no regression) |
| GOV-RELIABILITY-FAST-LANE-001 | Fast-lane eligibility (four criteria) confirmed at the `-004` GO. | Confirmed |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | This report carries the spec-to-test mapping plus the executed commands and observed results below. | — |

## Verification Commands And Observed Results

- `python -m py_compile scripts/cross_harness_bridge_trigger.py` — clean (IP-1 introduces no syntax error).
- `python -m py_compile platform_tests/scripts/test_cross_harness_trigger_import_repair.py` — clean.
- `python -m pytest platform_tests/scripts/test_cross_harness_trigger_import_repair.py -q` — `2 passed in 0.47s` (the IP-3 module: `test_trigger_bootstrap_resolves_groundtruth_kb_without_pythonpath`, `test_trigger_bootstrap_preserves_wi3344_scripts_entry`).
- `python -m pytest platform_tests/scripts/ -q -k "trigger or import"` — `82 passed, 1644 deselected in 15.27s`. This includes all 30 tests in the existing `test_cross_harness_bridge_trigger.py` (no regression from IP-1) plus the 2 new IP-3 tests; 0 failed.

## Acceptance Criteria

- [x] Loyal Opposition returned GO on the proposal (`-004`).
- [x] `scripts/cross_harness_bridge_trigger.py` imports `groundtruth_kb` and runs without `ModuleNotFoundError` under the hook invocation path; covered by `test_trigger_bootstrap_resolves_groundtruth_kb_without_pythonpath`.
- [x] The existing stale `active-*-session (N).lock` collision files under `.gtkb-state/bridge-poller/` are removed (20 files); the unnumbered current locks `active-claude-session.lock` and `active-codex-session.lock` are intact (see IP-2 Cleanup Evidence).
- [x] No source file other than `scripts/cross_harness_bridge_trigger.py` is modified; `scripts/active_session_heartbeat.py` is unchanged. The only other file added is the IP-3 regression test `platform_tests/scripts/test_cross_harness_trigger_import_repair.py` (a new test file, per IP-3 and the `platform_tests/scripts/**` target glob).
- [x] No change to the trigger's dispatch logic, suppression decision, signature scheme, or the dispatch-state contract — IP-1 is a `sys.path`-only addition, and the 30 existing trigger tests pass unchanged.
- [x] This post-implementation report carries observed command results and the before/after evidence of the IP-2 cleanup.
- [ ] Loyal Opposition returns VERIFIED.

## Recommended Commit Type

`fix:` — WI-3360 repairs a defect (the `ModuleNotFoundError` crash that prevented the trigger from dispatching). It adds no new capability surface: IP-1 is a `sys.path` bootstrap, IP-2 is a one-time runtime-state cleanup, IP-3 is a regression test. Consistent with the `-003` proposal's recommended type.

## Implementation Notes

- Implementation-start authorization: the packet was minted from the live `-004` GO (`python scripts/implementation_authorization.py begin --bridge-id gtkb-cross-harness-trigger-import-repair`) before any protected edit; `latest_status` was `GO` and the packet covered all three target globs.
- Co-targeting thread: a governance PreToolUse advisory flagged `gtkb-prime-worker-post-stop-dispatch-retry-slice-3` (NO-GO at `-002`) as also listing `scripts/cross_harness_bridge_trigger.py` in target_paths. Its `-001`/`-002` were read: that thread adds a post-Stop dispatch-retry pass to the `main`/dispatch logic (lines ~1042-1330) and is unimplemented (NO-GO). The IP-1 change here is a disjoint top-of-file `sys.path` addition (~line 72). No textual or semantic conflict; the import fix is, if anything, a prerequisite the retry-pass thread benefits from.
- The collision-file count grew from 11 (Claude) at `-001` drafting to 12 at implementation — consistent with the `-003` "Collision-File Origin And Cleanup Scope" framing that an external file-sync producer continues to generate conflict copies; root-causing that producer remains out of scope for this fast-lane thread.

## Pre-Filing Preflight Subsection

The applicability preflight (`scripts/bridge_applicability_preflight.py`) and the ADR/DCL clause preflight (`scripts/adr_dcl_clause_preflight.py`) were run against this report content with `--content-file` before the live `NEW` `bridge/INDEX.md` entry was inserted. Observed results: the applicability preflight reported `preflight_passed: true` with `missing_required_specs: []` and `missing_advisory_specs: []` (6 specs matched, all cited); the clause preflight evaluated 5 clauses (4 `must_apply`, 1 `may_apply`) with 0 evidence gaps and 0 blocking gaps (gate exit 0).

## Loyal Opposition Asks

1. Confirm the IP-1 `sys.path` bootstrap resolves the `ModuleNotFoundError` for the bare hook invocation while preserving the WI-3344 sibling-`scripts/` entry, as proven by the two IP-3 tests.
2. Confirm the IP-2 before/after evidence demonstrates the numbered collision files were removed and the unnumbered current locks remain intact.
3. Confirm the 82-test `-k "trigger or import"` run (including the 30 unchanged `test_cross_harness_bridge_trigger.py` tests) is sufficient evidence that IP-1 caused no dispatch-logic regression.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
