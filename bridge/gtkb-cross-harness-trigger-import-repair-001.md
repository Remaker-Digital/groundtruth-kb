NEW

# Repair Cross-Harness Bridge Trigger: ModuleNotFoundError Import Defect and Stale Active-Session Lock Cleanup (WI-3360)

bridge_kind: prime_proposal
Document: gtkb-cross-harness-trigger-import-repair
Version: 001 (NEW; reliability fast-lane defect fix; split-off from gtkb-bridge-active-session-autodrain per NO-GO F2)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-17 UTC
Implements: DCL-SMART-POLLER-AUTO-TRIGGER-001; WI-3360
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3360
target_paths: ["scripts/cross_harness_bridge_trigger.py", "scripts/active_session_heartbeat.py", "platform_tests/scripts/**"]
Recommended commit type: fix:

## Claim

The cross-harness event-driven trigger (`scripts/cross_harness_bridge_trigger.py`) — the canonical bridge-dispatch automation — intermittently fails with `ModuleNotFoundError: No module named 'groundtruth_kb'`. Evidence: `.gtkb-state/bridge-poller/dispatch-failures.jsonl` records `{"error_type": "ModuleNotFoundError", "error_message": "No module named 'groundtruth_kb'", "ts": "2026-05-17T03:46:50+00:00"}`. The trigger is registered as a `PostToolUse` and `Stop` hook in `.claude/settings.json` and `.codex/hooks.json`. Those hook invocations run `python scripts/cross_harness_bridge_trigger.py` without setting `PYTHONPATH`, and the script does not bootstrap `sys.path` to include `groundtruth-kb/src`, so `import groundtruth_kb` fails and the trigger cannot execute. When the trigger cannot run, no bridge dispatch occurs — a direct reliability defect against `DCL-SMART-POLLER-AUTO-TRIGGER-001` and `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`.

Separately, the active-session lock under `.gtkb-state/bridge-poller/` is not written atomically. Concurrent writers produce stale numbered-collision files — `.gtkb-state/bridge-poller/` currently holds `active-claude-session (1..11).lock` and `active-codex-session (1..8).lock`. The collision cruft accumulates and can confuse lock inspection and the active-session suppression check.

This proposal repairs both defects: an in-script `sys.path` bootstrap so the trigger imports `groundtruth_kb` regardless of invocation context, and an atomic active-session lock write, plus a one-time cleanup of the existing stale collision files. It is a genuine small defect fix with no new behavior, filed as the reliability-fast-lane split-off that the `gtkb-bridge-active-session-autodrain` Codex NO-GO (finding F2) directed.

## Specification Links

- DCL-SMART-POLLER-AUTO-TRIGGER-001 — the auto-trigger contract: actionable bridge state must trigger dispatch automatically; a trigger that cannot import its dependencies and crashes violates this contract. This is the WI-3360 source specification.
- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 — bridge dispatch must reach the recipient harness with the owner out of the loop; a crashing trigger defeats this.
- GOV-RELIABILITY-FAST-LANE-001 — the reliability fast-lane governs small single-concern defect fixes with no new behavior; this proposal claims fast-lane eligibility and maps the four criteria in the Fast-Lane Eligibility section.
- GOV-FILE-BRIDGE-AUTHORITY-001 — the cross-harness trigger is bridge infrastructure; `bridge/INDEX.md` remains canonical workflow state.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — durable artifact preservation across proposal, deliberation, and report (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across artifacts and tests (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle state transitions toward verified (advisory).

## Fast-Lane Eligibility

This thread claims eligibility under `GOV-RELIABILITY-FAST-LANE-001` and the standing authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (covers-by-membership: WI-3360 is an active member of `PROJECT-GTKB-RELIABILITY-FIXES`). The four eligibility criteria:

1. **Origin defect/regression** — met. WI-3360 has `origin=defect`; the `ModuleNotFoundError` is a defect against `DCL-SMART-POLLER-AUTO-TRIGGER-001`, observed in the live failure log.
2. **No new API/CLI/behavior beyond removing the defect** — met. An in-script `sys.path` bootstrap and an atomic lock write add no CLI, no API, and no behavior. The trigger's dispatch behavior is byte-identical after the fix; it simply stops crashing. The atomic lock write produces the same lock file, without collision cruft. The stale-lock cleanup is a one-time removal of regenerable runtime state.
3. **No new requirement** — met. `DCL-SMART-POLLER-AUTO-TRIGGER-001` already requires the trigger to dispatch reliably. No new GOV/SPEC/PB/ADR/DCL artifact is created.
4. **Small single-concern scope** — met. One concern: cross-harness trigger reliability. Two script files plus a test directory; no cross-cutting change.

Unlike the parent `gtkb-bridge-active-session-autodrain` thread (which adds a new Stop-event hook and was therefore moved off the fast lane), this split-off adds no mechanism and no behavior — it is the textbook fast-lane defect repair.

## Prior Deliberations

- `bridge/gtkb-bridge-active-session-autodrain-001.md` (IP-3) first identified the trigger `ModuleNotFoundError` and the stale-lock collisions, bundled into the autodrain proposal. `bridge/gtkb-bridge-active-session-autodrain-002.md` (Codex NO-GO, finding F2) directed that the import-repair and lock cleanup be split into a separate reliability-fast-lane thread. `bridge/gtkb-bridge-active-session-autodrain-003.md` (REVISED) removed them from that thread and named this split-off. This proposal is that split-off.
- The reliability fast-lane (`GOV-RELIABILITY-FAST-LANE-001`, `PROJECT-GTKB-RELIABILITY-FIXES`, `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`) is VERIFIED at `bridge/gtkb-reliability-fast-lane-006.md`; its owner-decision record is `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`. This proposal uses that standing authorization.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` — the OS pollers were retired over a token-cost regression; the cross-harness event-driven trigger is the canonical replacement. This proposal repairs that canonical trigger; it does not revive any retired poller.

## Owner Decisions / Input

- 2026-05-17: via AskUserQuestion the owner directed that the trigger import-repair be filed now as a NEW bridge thread, choosing the option "File import-repair now" (closing the gap that the parent autodrain `-003` left when it descoped the import-repair without filing the sibling thread).
- No further owner decision is required before GO. This is a reliability-fast-lane defect fix covered by the standing project authorization through active project membership; no formal-artifact-approval packet and no new owner decision are required.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-SMART-POLLER-AUTO-TRIGGER-001` and `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` already require the trigger to dispatch reliably; the defect is non-compliance with those requirements. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a scoped reliability defect fix to two trigger-related script files plus regression tests. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for a bulk action — is not applicable. The single work item cited (WI-3360) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## Scope

### IP-1: Repair the trigger import bootstrap

Add a `sys.path` bootstrap near the top of `scripts/cross_harness_bridge_trigger.py` (before the `groundtruth_kb` import) that computes the project root from the script's own location and prepends `groundtruth-kb/src` to `sys.path`. This makes the script import `groundtruth_kb` successfully regardless of invocation context — direct invocation, hook invocation, or scheduled task — without depending on the caller setting `PYTHONPATH`. The hook registrations in `.claude/settings.json` and `.codex/hooks.json` are NOT changed; the fix is self-contained in the script so it is robust against every current and future invocation site.

### IP-2: Atomic active-session lock write

Make the active-session lock writer (`scripts/active_session_heartbeat.py`, which writes `.gtkb-state/bridge-poller/active-<role>-session.lock` on its session-start / tool-use / session-stop modes) write the lock atomically: write to a temporary file in the same directory, then `os.replace()` into the final lock path. Atomic replace eliminates the partial-write window that produces numbered-collision files (`active-claude-session (N).lock`). The implementation will confirm the exact lock-writing call site at implementation time; `target_paths` covers both the trigger and the heartbeat script.

### IP-3: Clean up existing stale collision lock files

As a one-time cleanup, remove the accumulated stale `active-*-session (N).lock` numbered-collision files under `.gtkb-state/bridge-poller/`. These are regenerable runtime state, not canonical artifacts. The current active-session locks (the un-numbered `active-claude-session.lock` / `active-codex-session.lock`) are left intact.

### IP-4: Regression tests

Add tests under `platform_tests/scripts/`:
- `scripts/cross_harness_bridge_trigger.py` imports and runs without `ModuleNotFoundError` when invoked as the hooks invoke it (no `PYTHONPATH` set), exercising the `sys.path` bootstrap.
- The active-session lock write is atomic — a test simulating a concurrent/partial write confirms no numbered-collision file is produced and the final lock content is well-formed.

## Out Of Scope

- The active-session Stop-event auto-drain — owned by the parent thread `gtkb-bridge-active-session-autodrain` (REVISED at `-003`).
- The SessionStart idle-drain loop — a separate deferred follow-on thread.
- Changing the trigger's dispatch logic, actionable-signature scheme, suppression decision, or the dispatch-state contract — this proposal repairs only the import bootstrap and the lock-write atomicity.
- Changing the hook registrations in `.claude/settings.json` or `.codex/hooks.json` — the import fix is in-script by design.
- Any file outside `E:\GT-KB`. All target paths are within the `E:\GT-KB` project root.

## Files Expected To Change

- `scripts/cross_harness_bridge_trigger.py` — add the `sys.path` bootstrap before the `groundtruth_kb` import (IP-1).
- `scripts/active_session_heartbeat.py` — make the active-session lock write atomic via temp-file-plus-`os.replace` (IP-2).
- `platform_tests/scripts/**` — regression coverage for IP-1 and IP-2 (IP-4).

The IP-3 stale-lock cleanup removes regenerable files under `.gtkb-state/bridge-poller/`; it changes no tracked source file.

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| DCL-SMART-POLLER-AUTO-TRIGGER-001 / ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 | Test: `cross_harness_bridge_trigger.py` imports and runs without `ModuleNotFoundError` under the hook invocation path (no `PYTHONPATH`), so the trigger can always execute and dispatch. |
| DCL-SMART-POLLER-AUTO-TRIGGER-001 (lock atomicity) | Test: the active-session lock write is atomic; a simulated concurrent/partial write produces no numbered-collision file. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | The trigger continues to read `bridge/INDEX.md` as canonical; dispatch logic and the dispatch-state contract are unchanged. |
| GOV-RELIABILITY-FAST-LANE-001 | The Fast-Lane Eligibility section maps the four criteria; Loyal Opposition confirms eligibility. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus executed test commands and observed results. |

Implementation verification will run:
- `python -m pytest platform_tests/scripts/ -q -k "trigger or import or lock"`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-cross-harness-trigger-import-repair`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-cross-harness-trigger-import-repair`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] `scripts/cross_harness_bridge_trigger.py` imports `groundtruth_kb` and runs without `ModuleNotFoundError` under the hook invocation path; covered by a test.
- [ ] The active-session lock write is atomic; no numbered-collision file is produced under a concurrent/partial write; covered by a test.
- [ ] The existing stale `active-*-session (N).lock` collision files under `.gtkb-state/bridge-poller/` are removed; the un-numbered current locks are intact.
- [ ] No change to the trigger's dispatch logic, suppression decision, signature scheme, or the dispatch-state contract.
- [ ] Post-implementation report carries observed command results.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight (`scripts/bridge_applicability_preflight.py`) and the ADR/DCL clause preflight (`scripts/adr_dcl_clause_preflight.py`) are run against this content before the live `NEW` INDEX entry is inserted, and again by the propose helper as the filing gate. A non-empty `missing_required_specs` / `missing_advisory_specs` list, or a blocking clause gap, is a self-detected defect to correct before filing.

Observed results (run against this draft content prior to filing):

- Applicability preflight: `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`; packet_hash `sha256:2f436d33fe024c56fab9292a35ddc3e740d00e5709d89c251dac9afb87a96871`; 6 specs matched, all cited.
- Clause preflight: 5 clauses evaluated, all `must_apply`; 0 evidence gaps; 0 blocking gaps (gate exit 0).

## Risk And Rollback

**Risk R1 (low): the `sys.path` bootstrap computes the wrong project root.** Mitigation: the bootstrap derives the root from the script's own resolved location (`scripts/` is a fixed child of the project root); a test exercises the import under the hook invocation path. If wrong, the bootstrap is a few lines and trivially revertible.

**Risk R2 (low): the atomic lock write changes lock semantics.** Mitigation: `os.replace` is atomic on the same filesystem and produces the identical final lock file; only the partial-write collision window is removed. A test asserts the final lock content is well-formed.

**Risk R3 (low): the stale-lock cleanup removes a live lock.** Mitigation: IP-3 removes only the numbered-collision files (`active-*-session (N).lock`); the un-numbered current locks are explicitly preserved.

Rollback: each IP is independently revertible. Reverting `cross_harness_bridge_trigger.py` and `active_session_heartbeat.py` to their prior versions restores prior behavior; the stale-lock cleanup is a one-time operation with no rollback need (the files are regenerable runtime state).

## Loyal Opposition Asks

1. Confirm the in-script `sys.path` bootstrap (rather than patching `PYTHONPATH` into each hook registration) is the right structural choice for invocation-context robustness.
2. Confirm the fast-lane eligibility claim — that an import bootstrap and an atomic lock write add no new behavior.
3. Confirm that bundling the import repair and the lock-atomicity fix in one thread (both being cross-harness trigger reliability defects) is the correct scope boundary.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
