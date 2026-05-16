NEW

# Implementation Proposal - bridge-compliance-gate Work Item regex rejects spec-intake WI-AUTO-* ids (WI-3322)

bridge_kind: implementation_proposal
Document: gtkb-bridge-compliance-gate-wi-auto-regex-fix
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-16 UTC
Session: S354

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3322

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py", "platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py"]

## Summary

The bridge-compliance-gate hook rejects a legitimate class of Work Item id: the `WI-AUTO-<SPEC-ID>` ids that `groundtruth_kb.intake` (spec-intake confirm) auto-creates. The gate's project-linkage metadata regexes accept only `WI-` followed by digits, plus `GTKB-*` and `WORKLIST-*`. Consequently a bridge proposal whose work item is a spec-intake auto-WI cannot be filed at all: its `Work Item:` line fails the metadata-presence gate. This proposal widens the two regexes to also accept `WI-AUTO-[A-Z0-9-]+`. It does not change the spec-intake id scheme and does not change the gate's intent; it aligns the mechanization with the specification it enforces.

The defect was discovered during the S353 NO-GO bridge backlog drain: the thread `gtkb-bridge-mode-config-transactions-slice-1` cannot receive a REVISED proposal because its only work item is `WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` - a valid, project-homed work item (an active member of `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`) that the regex structurally cannot accept.

## Defect Detail

The active hook `.claude/hooks/bridge-compliance-gate.py` carries the alternation `WI-` digits, `GTKB-[A-Z0-9-]+`, `WORKLIST-[A-Z0-9-]+` in TWO regexes, consumed by two different checks:

- `WORK_ITEM_LINE_RE` (lines 101-103) - used by `_project_metadata_gaps()`. A `Work Item:` line whose id does not match is reported as a missing `Work Item:` line, hard-blocking the proposal. This is the mechanization of CLAUSE-PROJECT-METADATA-PRESENT of DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001.
- `WORK_ITEM_VALUE_RE` (lines 124-126) - used by `_extract_project_metadata()`, which captures the work-item id for the live MemBase membership check `_wi_project_membership_gap()`. This feeds CLAUSE-BRIDGE-WI-PROJECT-MEMBERSHIP of DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001.

Both regexes must be widened. Widening only `WORK_ITEM_LINE_RE` (the literal ask) would let a `WI-AUTO-*` proposal pass the presence gate, but `_extract_project_metadata()` would still fail to capture the id, return a `work_item_id` of `None`, and `_wi_project_membership_gap()` would short-circuit on its `if not (... work_item_id): return None` fail-open guard - silently SKIPPING the live work-item/project membership and authorization check for every `WI-AUTO-*` work item. The fail-open guard exists so the gate never blocks on infrastructure failure (missing DB, sqlite error); a regex capture-miss must not be allowed to ride that same path. Widening both regexes keeps the membership check engaged.

The same byte-identical regexes appear in the scaffold template `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` (lines 101-103, 124-126). The active hook is a scaffolded instance of that template. Fixing only the active hook would (a) introduce scaffold drift and (b) leave `gt project upgrade --apply` able to re-copy the un-widened template over the active hook, silently reverting the fix. Both files are therefore widened in lockstep.

## Scope Boundary - What Is NOT In This Proposal

`groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` (line 20-23) and `scripts/project_verified_completion_scanner.py` (line 33-36) carry a separate `_WORK_ITEM_LINE_RE` with the same digits-only `WI-` alternation, used to detect which work items reached VERIFIED by scanning bridge files. That is a distinct subsystem (project-completion detection) with a distinct failure mode, and it is NOT in this proposal's scope. It is recorded as a separate discovered defect for independent triage. This proposal is scoped to the bridge-compliance-gate control only, per the reliability fast-lane single-concern rule.

## In-Root Placement Evidence

All four target paths are in-root under `E:\GT-KB`: `.claude/hooks/bridge-compliance-gate.py`, `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`, `platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py`, and `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py`. No `applications/` paths; no paths outside `E:\GT-KB`. ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT satisfied.

## Specification Links

- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - the constraint `WORK_ITEM_LINE_RE` mechanizes (CLAUSE-PROJECT-METADATA-PRESENT). The constraint requires a proposal to carry a `Work Item:` line; it does not intend to exclude a legitimate id class. This fix aligns the regex with the constraint's intent.
- DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001 - the constraint the live membership check enforces (CLAUSE-BRIDGE-WI-PROJECT-MEMBERSHIP). `WORK_ITEM_VALUE_RE` feeds `_extract_project_metadata()` then `_wi_project_membership_gap()`. Widening `WORK_ITEM_VALUE_RE` keeps this check engaged for `WI-AUTO-*` ids instead of silently skipped.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the Specification-Derived Verification Plan below maps each linked constraint to a named regression test.
- GOV-FILE-BRIDGE-AUTHORITY-001 - the file-bridge authority; the bridge-compliance-gate is bridge-protocol infrastructure and this fix keeps the project-linkage gate behaving per specification.
- GOV-RELIABILITY-FAST-LANE-001 - WI-3322 is a defect-origin, single-concern, no-fresh-spec fix; it meets the fast-lane eligibility criteria and is filed through the standing reliability-fixes authorization.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the gate is a governed tooling artifact; this corrects its behavior without weakening it.
- GOV-STANDING-BACKLOG-001 - WI-3322 is tracked in the standing backlog as a member of PROJECT-GTKB-RELIABILITY-FIXES.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all four target paths are in-root (see In-Root Placement Evidence).
- `.claude/rules/file-bridge-protocol.md` - defines the project-linkage metadata the gate parses and the bridge protocol this proposal follows.
- `.claude/rules/codex-review-gate.md` - the counterpart-review gate; this hook change is filed for Codex GO before implementation per that rule.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - the cross-cutting constraint that every implementation proposal cite all relevant governing specifications. This Specification Links section is the proposal's compliance with that constraint.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - advisory; the change preserves traceability across the artifact graph - the WI-3322 defect, this bridge thread, and the IP-3/IP-4 regression tests are linked artifacts, not ad-hoc edits.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - advisory; the WI-3322 defect artifact proceeds through governed bridge lifecycle states (NEW, then GO, then implementation, then VERIFIED) rather than informal resolution.

## Prior Deliberations

- DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT - the owner directive that created the spec-to-project-to-WI-to-bridge mechanical-enforcement chain, including DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001, the `WORK_ITEM_LINE_RE` metadata gate (WI-3314), and the `WORK_ITEM_VALUE_RE`-fed membership check (WI-3315). This defect lives in that chain's own output: the regexes were authored with a digits-only `WI-` assumption and the spec-intake `WI-AUTO-*` id shape was not accounted for.
- Bridge thread `gtkb-codex-bridge-compliance-gate-parity` (VERIFIED) - prior bridge work on the same hook, addressing Codex-side audit parity. It did not touch `WORK_ITEM_LINE_RE` or `WORK_ITEM_VALUE_RE`; there is no overlap with this proposal.
- A `search_deliberations` scan for the work-item regex and the WI-AUTO rejection found no prior deliberation addressing this specific defect. WI-3322 is the first record of it.

## Owner Decisions / Input

- 2026-05-16 UTC, S354: the owner reported the WI-3322 defect (the bridge-compliance-gate Work Item regex rejecting spec-intake `WI-AUTO-*` ids) and directed Prime Builder to fix it through the bridge protocol - file a proposal, obtain Codex GO, then implement with a regression test. This proposal executes that directive.
- This work is filed through the reliability fast-lane: WI-3322 is an active member of PROJECT-GTKB-RELIABILITY-FIXES, covered by the standing authorization PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING (active, no expiry; allowed mutation classes include `source`, `test_addition`, and `hook_upgrade`; owner-decision basis DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION). No per-fix deliberation or new project authorization is created.

## Requirement Sufficiency

Existing requirements sufficient. DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 and DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001 are unchanged - the proposal corrects the regex mechanization to match those existing constraints. No new or revised requirement is created. The `WI-AUTO-<SPEC-ID>` id shape is an existing, observed output of `groundtruth_kb.intake`, not a new contract introduced here.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. This proposal covers one work item (WI-3322), a member of PROJECT-GTKB-RELIABILITY-FIXES. The change is a two-token regex widening in two byte-identical hook files plus two regression-test additions; it performs no inventory sweep, no batch promotion, and no multi-item standing-backlog mutation. GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS is not triggered.

## Proposed Scope

### IP-1: Widen the Work Item alternation in the active hook

In `.claude/hooks/bridge-compliance-gate.py`, insert `WI-AUTO-[A-Z0-9-]+` as a new alternative in both regexes:

- `WORK_ITEM_LINE_RE` (line 102): the alternation becomes `WI-` digits, then `WI-AUTO-[A-Z0-9-]+`, then `GTKB-[A-Z0-9-]+`, then `WORKLIST-[A-Z0-9-]+`.
- `WORK_ITEM_VALUE_RE` (line 125): the same alternation, inside its existing capturing group.

`WI-AUTO-[A-Z0-9-]+` is placed adjacent to the `WI-` digits alternative for readability. The two `WI-` alternatives are mutually exclusive (a `WI-` id continues with either a digit or the literal `AUTO-`), so alternation order does not affect matching. The new alternative uses the same `[A-Z0-9-]+` character class as the existing `GTKB-` and `WORKLIST-` alternatives, so `WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` and any future `WI-AUTO-<SPEC-ID>` id is accepted. The `^Work Item:\s*...\s*$` anchoring is unchanged, so the widening cannot over-match content outside a `Work Item:` metadata line.

### IP-2: Widen the byte-identical regexes in the scaffold template

Apply the identical two-token edit to `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` (`WORK_ITEM_LINE_RE` line 102, `WORK_ITEM_VALUE_RE` line 125). This keeps the template and the active hook byte-identical (no scaffold drift) and ensures newly scaffolded adopter projects, and any `gt project upgrade --apply` re-copy, receive the corrected regex.

### IP-3: Regression test for the presence gate (WORK_ITEM_LINE_RE)

In `platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py`, extend `test_bridge_proposal_metadata_accepts_wi_gtkb_worklist_id_formats` to also cover a `WI-AUTO-*` id (add `WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` to the parametrized id tuple), and add a focused test `test_bridge_proposal_metadata_accepts_wi_auto_id` asserting a NEW proposal whose `Work Item:` line carries a `WI-AUTO-*` id does not trip CLAUSE-PROJECT-METADATA-PRESENT. Derives from DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001/CLAUSE-PROJECT-METADATA-PRESENT.

### IP-4: Regression test for value capture and membership engagement (WORK_ITEM_VALUE_RE)

In `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py`, add tests that prove the membership check ENGAGES for a `WI-AUTO-*` id, not merely that a denial is absent:

- `test_extract_project_metadata_captures_wi_auto_id` - assert `_extract_project_metadata()` on a body whose `Work Item:` line carries a `WI-AUTO-*` id returns that id as a non-None capture.
- `test_wi_auto_id_membership_check_engages` - build a fixture DB where the `WI-AUTO-*` work item has NO membership row, and assert the proposal is BLOCKED with `wi-not-found-in-project`. This assertion fails against the un-widened `WORK_ITEM_VALUE_RE` (capture-miss yields a `None` work-item id, the membership check short-circuits on its fail-open guard, and no denial is produced) and passes only when the regex captures the id and the check runs. It therefore cannot be satisfied by the silent-skip path.
- `test_wi_auto_id_active_membership_passes` - a `WI-AUTO-*` work item with an active membership and an active, including authorization yields a passing proposal.

Derives from DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001/CLAUSE-BRIDGE-WI-PROJECT-MEMBERSHIP.

## Specification-Derived Verification Plan

| Linked spec / clause | Verification step | Expected result |
|---|---|---|
| DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 / CLAUSE-PROJECT-METADATA-PRESENT | IP-3 tests in test_bridge_compliance_gate_project_metadata.py | a WI-AUTO-* `Work Item:` line is accepted; the WI-digits, GTKB-, and WORKLIST- formats are still accepted (existing assertions unchanged) |
| DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001 / CLAUSE-BRIDGE-WI-PROJECT-MEMBERSHIP | IP-4 tests in test_bridge_compliance_gate_wi_project_membership.py | `_extract_project_metadata` captures the WI-AUTO id; the membership check engages - blocks on a missing membership, passes on an active membership |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | this table is the spec-to-test mapping; every regex change maps to a named test | each behavior is covered by a named test |
| GOV-FILE-BRIDGE-AUTHORITY-001 / CLAUSE-INDEX-IS-CANONICAL | this NEW entry is inserted at the top of its INDEX thread version list; no deletion or rewrite | confirmed at filing time |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 / CLAUSE-IN-ROOT | all four target paths are in-root | confirmed in In-Root Placement Evidence |

Commands at implementation time (executed after Codex GO):

1. `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py -q` - all new and existing tests PASS.
2. `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/scripts/test_codex_bridge_compliance_gate.py -q` - the remainder of the bridge-compliance-gate suite still PASSES (no regression).
3. `python -m ruff check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py` - zero new errors.
4. Drift check: confirm `.claude/hooks/bridge-compliance-gate.py` and `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` remain byte-identical after the edit.
5. Live evidence: a NEW or REVISED bridge proposal whose `Work Item:` line carries `WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` is no longer hard-blocked by the gate.

## Risks and Rollback

- Risk: the widening accepts a malformed `WI-AUTO-` id. Mitigation: `[A-Z0-9-]+` matches only uppercase letters, digits, and hyphen, identical to the existing `GTKB-` and `WORKLIST-` classes; the `^Work Item:\s*...\s*$` anchoring confines the match to a metadata line. There is no over-match surface.
- Risk: the active hook and the template drift apart. Mitigation: IP-2 applies the identical edit to both; verification step 4 confirms byte-identity.
- Risk: a downstream consumer outside scope (lifecycle.py, project_verified_completion_scanner.py) still mis-parses `WI-AUTO-*`. Mitigation: that subsystem is explicitly out of scope and is recorded as a separate discovered defect; this proposal does not claim to fix it.
- Rollback: revert the `WI-AUTO-[A-Z0-9-]+` alternative in both hook files and remove the IP-3 and IP-4 tests. The change is a pure additive alternation; rollback restores the prior behavior exactly.

## Recommended Commit Type

`fix` - corrects a defect in an existing governance hook (a regex narrower than the specification it enforces). A two-token regex widening in two files plus regression tests; no new capability surface, no spec promotion, no behavior change for genuine defects.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
