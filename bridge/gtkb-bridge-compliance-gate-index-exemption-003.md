NEW

# Implementation Report - Bridge Compliance Gate INDEX Exemption (GTKB-BRIDGE-COMPLIANCE-GATE-INDEX-EXEMPTION)

bridge_kind: prime_proposal
Document: gtkb-bridge-compliance-gate-index-exemption
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-16 UTC
Session: S354

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3334

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py"]

## Summary

Post-implementation report for the GO'd proposal (Codex GO at `-002`). The `bridge/INDEX.md` exemption is implemented in both hook copies and covered by a new parametrized regression test. All seven GO Conditions are evidenced below.

## In-Root Placement Evidence

All three changed files are in-root under `E:\GT-KB`: `.claude/hooks/bridge-compliance-gate.py`, `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`, and `platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py`. No output path is outside the project root.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - `bridge/INDEX.md` is the canonical workflow state; clause CLAUSE-INDEX-IS-CANONICAL is the governing authority for exempting index edits from the implementation checkpoint.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this report carries concrete specification links.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - this report carries a spec-to-test mapping and executed test command evidence.
- GOV-RELIABILITY-FAST-LANE-001 - a small, single-concern defect fix delivered through the reliability fast-lane.
- GOV-STANDING-BACKLOG-001 - WI-3334 is tracked in the MemBase backlog under PROJECT-GTKB-RELIABILITY-FIXES.
- SPEC-AUQ-POLICY-ENGINE-001 - the bridge-compliance-gate participates in the deterministic policy engine; the fix keeps the checkpoint deterministic.
- SPEC-AUQ-NO-LLM-CLASSIFIER-001 - the exemption is a deterministic path comparison with no LLM classification.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all changed files are in-root under `E:\GT-KB`.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the defect and fix are preserved as durable artifacts (WI-3334, this thread).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix preserves traceability across the work item, proposal, test, and report.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3334 moves through backlogged, in-progress, and verified lifecycle states.

## Prior Deliberations

A Deliberation Archive search ("bridge compliance gate INDEX target paths pending proposal ask exemption") returned no prior decision on exempting `bridge/INDEX.md` from the target-path checkpoint. The nearest related record is DELIB-1637 (Codex Bridge-Compliance-Gate Hook Parity REVISED-3, GO) - a distinct Codex-parity concern that did not touch the target-path loop. No prior deliberation rejected or addressed this exemption.

## Owner Decisions / Input

- 2026-05-16 UTC, S354: the owner observed the bridge-compliance-gate prompting on every `bridge/INDEX.md` edit and directed Prime Builder to route a fix through the bridge protocol, obtain a Codex GO, then implement including a regression test. The proposal received Codex GO at `-002`; this report covers the implementation under that GO and the standing reliability-fast-lane authorization (PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING). No further owner decision is pending.

## Requirement Sufficiency

Existing requirements sufficient. GOV-FILE-BRIDGE-AUTHORITY-001 and clause CLAUSE-INDEX-IS-CANONICAL already establish `bridge/INDEX.md` as the canonical, continuously-edited workflow state. No new or revised requirement was needed.

## Clause Scope Clarification (Not a Bulk Operation)

This is not a bulk standing-backlog operation. It is a single-concern defect fix tracked by exactly one work item, WI-3334, an active member of PROJECT-GTKB-RELIABILITY-FIXES. No work-item state inventory, bulk transition, or backlog cleanup was performed. The reliability fast-lane (GOV-RELIABILITY-FAST-LANE-001) covers the fix through active project membership under PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING; that governance requires no per-fix formal-artifact-approval packet.

## Bridge INDEX Update Evidence

A NEW line for this report (`-003`) is inserted at the top of this thread's version list in `bridge/INDEX.md`, above the existing GO (`-002`) and NEW (`-001`) lines. No prior bridge file and no prior INDEX entry is deleted or rewritten; the append-only audit trail is preserved.

## Implementation Summary

The implementation matches the GO'd `-001` proposal scope.

### IP-1 and IP-2: INDEX exemption in both hook copies

Both `.claude/hooks/bridge-compliance-gate.py` and `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` received the byte-identical change:

- Two new pure helper functions were added after `_read_proposal_target_paths`: `_is_bridge_index_file(file_path)` returns True when the path is the canonical bridge index, using the leading-slash convention `f"/{normalized}".endswith("/bridge/INDEX.md")` already used by `_is_bridge_markdown_file`; `_pending_proposal_ask_reason(index_path, file_path)` carries the former inline `main()` loop with an `_is_bridge_index_file` short-circuit returning None at the top.
- `main()` replaced its inline `doc_statuses` / `file_path_normalized` locals and the target-path loop with a single `_pending_proposal_ask_reason(index_path, file_path)` call.
- The two `ask` message strings (NO-GO and pending) are carried over verbatim; behavior for non-INDEX files is unchanged.

The two hook copies remain byte-identical after the change (SHA256 `897CE6C802CC190077A0E236D7835770B5E82F1FB5CEEE522735EDDE9A1C72AE`). A concurrent parallel-session change (the sibling `gtkb-bridge-compliance-gate-wi-auto-regex-fix` thread, adding `WI-AUTO-*` to the work-item metadata regexes) landed in both copies during implementation; it occupies a different region and coexists cleanly. Both copies were re-verified byte-identical and compiling after that concurrent change.

### IP-3: Regression test

`platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py` was added. It imports both hook copies by path under distinct module names and exposes them through a `gate` fixture parametrized over `live` and `template`, so every behavioral test runs against both copies.

## GO Conditions - Evidence

| GO Condition | Evidence |
|---|---|
| Live hook and scaffold template receive the same INDEX exemption | Both copies edited with the byte-identical change (IP-1 and IP-2). |
| Remain byte-identical | SHA256 of both copies is `897CE6C802CC190077A0E236D7835770B5E82F1FB5CEEE522735EDDE9A1C72AE`. |
| Exempt only bridge/INDEX.md | `_is_bridge_index_file` matches only `/bridge/INDEX.md`; test_is_bridge_index_file_rejects_decoys proves a regular bridge file, `notbridge/INDEX.md`, and a `.claude/hooks` path are all rejected. |
| Preserve non-INDEX target-path protection | test_non_index_target_still_triggers_ask and test_no_go_proposal_non_index_target_triggers_no_go_reason confirm the checkpoint still fires (pending and NO-GO messages) for non-INDEX files. |
| Run the new regression test | `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py` produced 14 passed. |
| Run existing bridge-compliance-gate tests | test_bridge_compliance_gate_project_metadata.py, test_bridge_compliance_gate_wi_project_membership.py, test_bridge_compliance_gate_hard_block_workspace.py, and platform_tests/scripts/test_codex_bridge_compliance_gate.py all pass (60 passed total including the new file). |
| Clean relevant ruff results | `ruff check` on all three changed files reports All checks passed. `ruff format --check` on the new test file is clean. The two hook files carry pre-existing `ruff format` drift (three `re.compile` / SQL-string-wrapping hunks near lines 94, 117, and 330), confirmed pre-existing by `ruff format --check` on `HEAD` (exit 1); the change's own added code is `ruff format`-clean and was left untouched by `ruff format --diff`. |

## Specification-Derived Verification

| Specification | Behavior verified | Test | Result |
|---|---|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 / CLAUSE-INDEX-IS-CANONICAL | Editing `bridge/INDEX.md` while a pending NEW or REVISED proposal targets it does not emit `ask` | test_index_edit_with_pending_proposal_targeting_index_is_exempt (parametrized NEW and REVISED) | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 | `_is_bridge_index_file` recognizes the index in relative and absolute forms | test_is_bridge_index_file_recognizes_index | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 | `_is_bridge_index_file` rejects a regular bridge file and decoy paths | test_is_bridge_index_file_rejects_decoys | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 | The checkpoint still fires for a non-INDEX file matching a pending proposal | test_non_index_target_still_triggers_ask | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 | A NO-GO proposal still produces the NO-GO-specific reason for a non-INDEX file | test_no_go_proposal_non_index_target_triggers_no_go_reason | PASS |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Both hook copies carry the fix, with no false positive | all tests parametrized over the live and template hooks; test_unmatched_non_index_file_returns_none | PASS |

Executed commands and observed results:

```text
python -m pytest platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py -q
=> 14 passed

python -m pytest platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py \
  platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py \
  platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py \
  platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py \
  platform_tests/scripts/test_codex_bridge_compliance_gate.py -q
=> 60 passed

python -m ruff check .claude/hooks/bridge-compliance-gate.py \
  groundtruth-kb/templates/hooks/bridge-compliance-gate.py \
  platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py
=> All checks passed!
```

## Files Changed

- `.claude/hooks/bridge-compliance-gate.py` - added `_is_bridge_index_file` and `_pending_proposal_ask_reason`; `main()` calls the helper.
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` - byte-identical change.
- `platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py` - new regression test (14 parametrized cases).

## Recommended Commit Type

`fix` - repairs broken hook behavior (an over-firing checkpoint) with no new capability surface. The helper extraction is an internal refactor in service of the fix and of testability, not a new public interface.

## Risks / Rollback

- The exemption is a deterministic path comparison; non-INDEX behavior is unchanged and covered by regression tests.
- Rollback: revert the three files; the change is self-contained with no schema, configuration, or data migration.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
