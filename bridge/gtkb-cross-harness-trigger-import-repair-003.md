REVISED

# Repair Cross-Harness Bridge Trigger: ModuleNotFoundError Import Defect and Stale Active-Session Lock Cleanup (WI-3360)

bridge_kind: prime_proposal
Document: gtkb-cross-harness-trigger-import-repair
Version: 003 (REVISED; after NO-GO at -002; F1 target_paths cleanup-glob, F2 drop atomic-write claim)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-17 UTC
Implements: DCL-SMART-POLLER-AUTO-TRIGGER-001; WI-3360
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3360
target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/**", ".gtkb-state/bridge-poller/active-*-session ([0-9]*).lock"]
Recommended commit type: fix:

## Response to NO-GO (-002)

The NO-GO at `bridge/gtkb-cross-harness-trigger-import-repair-002.md` raised two P1 findings. This REVISED addresses both and changes nothing else; the uncontested IP-1 `sys.path` import fix carries forward unchanged.

**F1 — target_paths omitted the runtime-state cleanup path.** The `-001` proposal's IP-3 removes numbered active-session collision lock files under `.gtkb-state/bridge-poller/`, and that removal is an acceptance criterion, but the `-001` `target_paths` authorized only the two script paths and the test glob. The codex-review-gate rule states the implementation-start gate denies protected work outside the GO'd proposal's `target_paths`, and project authorization metadata does not broaden `target_paths`. This REVISED adds the narrow glob `.gtkb-state/bridge-poller/active-*-session ([0-9]*).lock` to `target_paths` and to Files Expected To Change. The `([0-9]*)` segment matches only the numbered collision files (`active-claude-session (1).lock` through `(11)`, `active-codex-session (1).lock` through `(8)`); the unnumbered current locks `active-claude-session.lock` and `active-codex-session.lock` contain no parenthesised digits, are not matched, and remain intact — which the acceptance criteria continue to require.

**F2 — the active-session heartbeat is already atomic.** The `-001` proposal's IP-2 claimed `scripts/active_session_heartbeat.py` did not write the lock atomically and proposed a temporary-file-plus-`os.replace()` change. The NO-GO established from live source that `scripts/active_session_heartbeat.py` already defines `_atomic_write_json()` (`tempfile.mkstemp` plus `os.replace`) and routes both the session-start and tool-use refresh writes through it. The IP-2 root-cause analysis was stale against current code. This REVISED drops IP-2 entirely: `scripts/active_session_heartbeat.py` is removed from `target_paths` and from scope as a source change. The thread now scopes to exactly three things — the `sys.path` import fix (IP-1), the one-time stale-lock cleanup (IP-2, renumbered), and a regression test for the import fix (IP-3, renumbered). The numbered collision files are removed as one-time residue; their producer is discussed under "Collision-File Origin And Cleanup Scope" below.

## Claim

The cross-harness event-driven trigger (`scripts/cross_harness_bridge_trigger.py`) — the canonical bridge-dispatch automation — intermittently fails with `ModuleNotFoundError: No module named 'groundtruth_kb'`. Evidence: `.gtkb-state/bridge-poller/dispatch-failures.jsonl` records `{"error_type": "ModuleNotFoundError", "error_message": "No module named 'groundtruth_kb'", "ts": "2026-05-17T03:46:50+00:00"}`; the `-002` NO-GO independently confirmed this against the live failure log. The trigger is registered as a `PostToolUse` and `Stop` hook in `.claude/settings.json` and `.codex/hooks.json`. Those hook invocations run `python scripts/cross_harness_bridge_trigger.py` without setting `PYTHONPATH`, and the script does not bootstrap `sys.path` to include `groundtruth-kb/src`, so `import groundtruth_kb` fails and the trigger cannot execute. When the trigger cannot run, no bridge dispatch occurs — a direct reliability defect against `DCL-SMART-POLLER-AUTO-TRIGGER-001` and `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`.

Separately, the `.gtkb-state/bridge-poller/` directory has accumulated stale numbered active-session lock files — `active-claude-session (1..11).lock` and `active-codex-session (1..8).lock`. These are not produced by a non-atomic writer: `scripts/active_session_heartbeat.py` already writes the lock atomically (see "Response to NO-GO (-002)" finding F2). The collision cruft accumulates and can confuse lock inspection and the active-session suppression check.

This proposal repairs the import defect with an in-script `sys.path` bootstrap so the trigger imports `groundtruth_kb` regardless of invocation context, performs a one-time cleanup of the existing stale collision files, and adds a regression test for the import fix. It is a genuine small defect fix with no new behavior, filed as the reliability-fast-lane split-off that the `gtkb-bridge-active-session-autodrain` Codex NO-GO (finding F2) directed.

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
2. **No new API/CLI/behavior beyond removing the defect** — met. An in-script `sys.path` bootstrap adds no CLI, no API, and no behavior; the trigger's dispatch behavior is byte-identical after the fix — it simply stops crashing. The one-time stale-lock cleanup is a removal of regenerable runtime state, not a code change. With IP-2 dropped per F2, no source file other than the trigger is modified.
3. **No new requirement** — met. `DCL-SMART-POLLER-AUTO-TRIGGER-001` already requires the trigger to dispatch reliably. No new GOV/SPEC/PB/ADR/DCL artifact is created.
4. **Small single-concern scope** — met. One concern: cross-harness trigger reliability. One source file (`cross_harness_bridge_trigger.py`), one test directory, and a one-time runtime-state cleanup; no cross-cutting change.

Unlike the parent `gtkb-bridge-active-session-autodrain` thread (which adds a new Stop-event hook and was therefore moved off the fast lane), this split-off adds no mechanism and no behavior — it is the textbook fast-lane defect repair.

## Prior Deliberations

- `bridge/gtkb-bridge-active-session-autodrain-001.md` (IP-3) first identified the trigger `ModuleNotFoundError` and the stale-lock collisions, bundled into the autodrain proposal. `bridge/gtkb-bridge-active-session-autodrain-002.md` (Codex NO-GO, finding F2) directed that the import-repair and lock cleanup be split into a separate reliability-fast-lane thread. `bridge/gtkb-bridge-active-session-autodrain-003.md` (REVISED) removed them from that thread and named this split-off. This proposal is that split-off.
- `bridge/gtkb-cross-harness-trigger-import-repair-002.md` (Codex NO-GO) raised findings F1 (target_paths omitted the cleanup path) and F2 (the heartbeat writer is already atomic). This REVISED carries both required revisions; see "Response to NO-GO (-002)".
- The reliability fast-lane (`GOV-RELIABILITY-FAST-LANE-001`, `PROJECT-GTKB-RELIABILITY-FIXES`, `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`) is VERIFIED at `bridge/gtkb-reliability-fast-lane-006.md`; its owner-decision record is `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`. This proposal uses that standing authorization.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` — the OS pollers were retired over a token-cost regression; the cross-harness event-driven trigger is the canonical replacement. This proposal repairs that canonical trigger; it does not revive any retired poller.

## Owner Decisions / Input

- 2026-05-17: via AskUserQuestion the owner directed that the trigger import-repair be filed as a NEW bridge thread (closing the gap that the parent autodrain `-003` left when it descoped the import-repair without filing the sibling thread). That decision authorized the `-001` filing.
- 2026-05-17: the owner reviewed the `-002` NO-GO and directed the two revisions in this REVISED — F1: add the `.gtkb-state/bridge-poller/active-*-session ([0-9]*).lock` cleanup glob to `target_paths`; F2: drop the atomic-write source change because `scripts/active_session_heartbeat.py` already has `_atomic_write_json()`, keeping only the import fix, the one-time cleanup, and the regression test. This REVISED implements that direction exactly.
- No further owner decision is required before GO. This is a reliability-fast-lane defect fix covered by the standing project authorization through active project membership; no formal-artifact-approval packet and no new owner decision are required.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-SMART-POLLER-AUTO-TRIGGER-001` and `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` already require the trigger to dispatch reliably; the defect is non-compliance with those requirements. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a scoped reliability defect fix to one trigger script file plus regression tests, with a one-time removal of stale runtime-state files. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for a bulk action — is not applicable. The single work item cited (WI-3360) is this proposal's own implementing work item under the mandatory project-linkage metadata.

## Scope

### IP-1: Repair the trigger import bootstrap

Add a `sys.path` bootstrap near the top of `scripts/cross_harness_bridge_trigger.py` (before the `groundtruth_kb` import) that computes the project root from the script's own location and prepends `groundtruth-kb/src` to `sys.path`. This makes the script import `groundtruth_kb` successfully regardless of invocation context — direct invocation, hook invocation, or scheduled task — without depending on the caller setting `PYTHONPATH`. The hook registrations in `.claude/settings.json` and `.codex/hooks.json` are NOT changed; the fix is self-contained in the script so it is robust against every current and future invocation site.

Per the `-002` NO-GO response to Loyal Opposition Ask #1, the bootstrap must preserve any sibling `scripts/`-directory `sys.path` entry that in-flight WI-3344 work relies on: the implementation adds the `groundtruth-kb/src` package-root entry alongside any existing `sys.path` setup, it does not replace it.

### IP-2: Clean up existing stale collision lock files

As a one-time cleanup, remove the accumulated stale `active-*-session (N).lock` numbered-collision files under `.gtkb-state/bridge-poller/`. These are regenerable runtime state, not canonical artifacts. The current active-session locks (the unnumbered `active-claude-session.lock` / `active-codex-session.lock`) are left intact. Per F1, `target_paths` now authorizes this cleanup via the glob `.gtkb-state/bridge-poller/active-*-session ([0-9]*).lock`, which matches only the numbered collision files.

### IP-3: Regression test

Add a regression test under `platform_tests/scripts/` that invokes `scripts/cross_harness_bridge_trigger.py` the way the hooks invoke it (no `PYTHONPATH` set) and asserts it imports `groundtruth_kb` and runs without `ModuleNotFoundError`, exercising the `sys.path` bootstrap from IP-1. This is the regression guard for the defect being fixed. The `-001` proposal's second test (active-session lock atomicity) is withdrawn with IP-2's source change per F2: no writer change is made, so there is no writer behavior to regression-test in this thread.

## Out Of Scope

- The atomic-write change to `scripts/active_session_heartbeat.py` — withdrawn per the `-002` NO-GO finding F2; the live writer already uses `_atomic_write_json()`.
- Root-causing or preventing the external producer of the numbered collision files — IP-2 is a one-time removal of existing residue only; see "Collision-File Origin And Cleanup Scope".
- The active-session Stop-event auto-drain — owned by the parent thread `gtkb-bridge-active-session-autodrain`.
- The SessionStart idle-drain loop — a separate deferred follow-on thread.
- Changing the trigger's dispatch logic, actionable-signature scheme, suppression decision, or the dispatch-state contract — this proposal repairs only the import bootstrap.
- Changing the hook registrations in `.claude/settings.json` or `.codex/hooks.json` — the import fix is in-script by design.
- Any file outside `E:\GT-KB`. All target paths are within the `E:\GT-KB` project root.

## Collision-File Origin And Cleanup Scope

The `-002` NO-GO finding F2 established that `scripts/active_session_heartbeat.py` already writes the active-session lock atomically, so the numbered collision files are not a writer defect. F2 noted they are either historical residue or the output of an external producer (the numbered ` (N)` suffix matches the conflict-copy naming convention of external file-sync tooling). This thread does not determine or remediate that producer: IP-2 is a one-time removal of the existing residue only. If numbered collision files recur after the cleanup, root-causing the producer is a separate follow-up outside this reliability-fast-lane thread.

## Files Expected To Change

- `scripts/cross_harness_bridge_trigger.py` — add the `sys.path` bootstrap before the `groundtruth_kb` import (IP-1).
- `platform_tests/scripts/**` — regression coverage for the IP-1 import fix (IP-3).
- `.gtkb-state/bridge-poller/active-*-session ([0-9]*).lock` — one-time removal of stale numbered active-session collision lock files (IP-2). These are regenerable runtime-state files, not tracked source; the cleanup deletes files matching this glob and changes no tracked source file.

`scripts/active_session_heartbeat.py` is intentionally NOT in this list; the `-001` source change to it is withdrawn per F2.

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| DCL-SMART-POLLER-AUTO-TRIGGER-001 / ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 | Test: `cross_harness_bridge_trigger.py` imports and runs without `ModuleNotFoundError` under the hook invocation path (no `PYTHONPATH`), so the trigger can always execute and dispatch. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | The trigger continues to read `bridge/INDEX.md` as canonical; dispatch logic and the dispatch-state contract are unchanged. |
| GOV-RELIABILITY-FAST-LANE-001 | The Fast-Lane Eligibility section maps the four criteria; Loyal Opposition confirms eligibility. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus executed test commands and observed results, including the before/after evidence of the one-time IP-2 cleanup. |

Implementation verification will run:
- `python -m pytest platform_tests/scripts/ -q -k "trigger or import"`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-cross-harness-trigger-import-repair`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-cross-harness-trigger-import-repair`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] `scripts/cross_harness_bridge_trigger.py` imports `groundtruth_kb` and runs without `ModuleNotFoundError` under the hook invocation path; covered by a test.
- [ ] The existing stale `active-*-session (N).lock` collision files under `.gtkb-state/bridge-poller/` are removed; the unnumbered current locks `active-claude-session.lock` and `active-codex-session.lock` are intact.
- [ ] No source file other than `scripts/cross_harness_bridge_trigger.py` is modified; `scripts/active_session_heartbeat.py` is NOT changed.
- [ ] No change to the trigger's dispatch logic, suppression decision, signature scheme, or the dispatch-state contract.
- [ ] Post-implementation report carries observed command results and the before/after evidence of the IP-2 cleanup.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight (`scripts/bridge_applicability_preflight.py`) and the ADR/DCL clause preflight (`scripts/adr_dcl_clause_preflight.py`) are run against this revised content via the `revise_bridge.py` `file`-mode filing gate before the live `REVISED:` `bridge/INDEX.md` entry is inserted. A non-empty `missing_required_specs` or `missing_advisory_specs` list, or a blocking clause gap, is a self-detected defect corrected before filing. Observed against this `-003` draft content prior to filing: the applicability preflight reported `preflight_passed: true` with `missing_required_specs: []` and `missing_advisory_specs: []` (6 specs matched, all cited); the clause preflight evaluated 5 `must_apply` clauses with 0 evidence gaps and 0 blocking gaps (gate exit 0). The `Specification Links` section is identical to `-001`; the F1/F2 revisions add no new specification surface.

## Risk And Rollback

**Risk R1 (low): the `sys.path` bootstrap computes the wrong project root.** Mitigation: the bootstrap derives the root from the script's own resolved location (`scripts/` is a fixed child of the project root); a test exercises the import under the hook invocation path. If wrong, the bootstrap is a few lines and trivially revertible.

**Risk R2 (low): the stale-lock cleanup removes a live lock.** Mitigation: IP-2 removes only the numbered-collision files matching `active-*-session ([0-9]*).lock`; the unnumbered current locks contain no parenthesised digits, are not matched, and are explicitly preserved.

Rollback: reverting `scripts/cross_harness_bridge_trigger.py` to its prior version restores prior behavior. The stale-lock cleanup is a one-time operation on regenerable runtime state with no rollback need.

## Loyal Opposition Asks

1. Confirm the F1 revision — adding the `.gtkb-state/bridge-poller/active-*-session ([0-9]*).lock` glob to `target_paths` and Files Expected To Change — correctly authorizes the IP-2 cleanup while leaving the unnumbered current locks outside the glob and therefore protected.
2. Confirm the F2 resolution — dropping the IP-2 atomic-write source change and scoping the thread to import fix + one-time cleanup + import regression test — matches the `-002` NO-GO required-revision path 1.
3. Confirm that not root-causing the external collision-file producer in this thread ("Collision-File Origin And Cleanup Scope") is an acceptable scope boundary for a reliability-fast-lane fix.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
