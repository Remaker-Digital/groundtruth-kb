NEW

# Implementation Proposal - Bridge Compliance Gate INDEX Exemption (GTKB-BRIDGE-COMPLIANCE-GATE-INDEX-EXEMPTION)

bridge_kind: prime_proposal
Document: gtkb-bridge-compliance-gate-index-exemption
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-16 UTC
Session: S354

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3334

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py"]

## Problem

The bridge-compliance-gate PreToolUse hook contains a target-path checkpoint in `main()`. After the content-deny checks clear, `main()` parses `bridge/INDEX.md`, and for every document at status `NEW`, `REVISED`, or `NO-GO` it reads that proposal's `target_paths` and, when the file being written matches one of them, emits an `ask` permission checkpoint ("wait for GO before implementing").

`bridge/INDEX.md` is itself a legitimate `target_path`. The pending proposal `gtkb-bridge-index-role-intent-sentinel` (currently `REVISED` in `bridge/INDEX.md`) adds a role-intent sentinel block to `bridge/INDEX.md`, so its proposal file correctly declares `target_paths: ["bridge/INDEX.md", ...]` (see `bridge/gtkb-bridge-index-role-intent-sentinel-001.md` line 16).

But `bridge/INDEX.md` is also the canonical bridge queue. It is edited on every proposal filing, every verdict, and every status transition - that is intrinsic bridge protocol, not "implementation" of any one proposal. The target-path checkpoint has no exemption for it, so it cannot distinguish a normal protocol status-line insertion from premature implementation of the sentinel block. While a proposal listing `bridge/INDEX.md` in `target_paths` sits at `NEW`, `REVISED`, or `NO-GO`, every edit to `bridge/INDEX.md` triggers an owner approval prompt. The owner observed exactly this over-firing.

This is an `ask` (a soft checkpoint), not a hard `deny`, so work is not blocked - but prompt fatigue trains owners to reflexively approve, which erodes the checkpoint's value.

Current state: the defect is presently dormant for the `gtkb-bridge-index-role-intent-sentinel` thread only because that thread's latest `bridge/INDEX.md`-referenced version (`-003`) is a not-yet-written `REVISED` file; `_read_proposal_target_paths` hits an `OSError` reading the missing file and returns an empty list. The `ask` fired while the thread sat at `NEW` (`-001`, which declares `bridge/INDEX.md`), and re-arms the moment the `REVISED` `-003` proposal file is written. The defect is a live latent over-fire independent of that thread's transient state.

The scaffold template copy `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` is byte-identical to the live hook and carries the same defect, so adopter projects scaffolded from the template inherit it.

## Claim

Exempt `bridge/INDEX.md` from the target-path-pending-proposal checkpoint in both the live hook and the scaffold template. Edits to the canonical bridge index are intrinsic bridge protocol and are never the gated "implementation" this checkpoint exists to catch - even when a proposal legitimately lists `bridge/INDEX.md` in its `target_paths`. Add a regression test in the platform test lane.

This narrows one over-firing checkpoint. It removes no governance coverage: the content-deny checks in `_deny_reason_for_content` (spec linkage, owner decisions, project metadata, applicability preflight) are unchanged, and the target-path checkpoint continues to fire for every non-INDEX file.

## In-Root Placement Evidence

All three `target_paths` are in-root under `E:\GT-KB`: `.claude/hooks/`, `groundtruth-kb/templates/hooks/`, and `platform_tests/hooks/`. The bridge proposal file resides under `E:\GT-KB\bridge\`. No output path is outside the project root.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - `bridge/INDEX.md` is the canonical workflow state; clause CLAUSE-INDEX-IS-CANONICAL establishes that editing the index is intrinsic protocol, the direct governing authority for exempting it from the implementation checkpoint.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal carries concrete specification links.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the post-implementation report will carry a spec-to-test mapping and executed test command evidence.
- GOV-RELIABILITY-FAST-LANE-001 - a small, single-concern defect fix filed through the reliability fast-lane under the standing project and standing authorization.
- GOV-STANDING-BACKLOG-001 - WI-3334 is tracked in the MemBase backlog under PROJECT-GTKB-RELIABILITY-FIXES.
- SPEC-AUQ-POLICY-ENGINE-001 - the bridge-compliance-gate participates in the deterministic policy engine; the fix keeps the checkpoint deterministic.
- SPEC-AUQ-NO-LLM-CLASSIFIER-001 - the exemption is a deterministic path comparison with no LLM classification.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target files are in-root under `E:\GT-KB`.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the defect and fix are preserved as durable artifacts (WI-3334, this proposal).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix preserves traceability across the work item, proposal, test, and report.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3334 moves through backlogged, in-progress, and verified lifecycle states.

## Prior Deliberations

A Deliberation Archive search ("bridge compliance gate INDEX target paths pending proposal ask exemption") returned no prior decision on exempting `bridge/INDEX.md` from the target-path checkpoint. The nearest related record is DELIB-1637 (Loyal Opposition Review - Codex Bridge-Compliance-Gate Hook Parity REVISED-3, GO), which reviewed the same hook for Codex-side parity - a distinct concern that did not touch the target-path loop. No prior deliberation rejected or addressed this exemption.

## Owner Decisions / Input

- 2026-05-16 UTC, S354: the owner observed the bridge-compliance-gate prompting on every `bridge/INDEX.md` edit and directed Prime Builder to route a fix through the bridge protocol - file a proposal with specification links, prior deliberations, project-linkage metadata, and a spec-derived test plan; obtain a Codex GO; then implement, including a regression test. This proposal executes that directive. No further owner decision is pending for the fix itself; implementation proceeds on Codex GO under the standing reliability-fast-lane authorization (PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING).

## Requirement Sufficiency

Existing requirements sufficient. GOV-FILE-BRIDGE-AUTHORITY-001 and its clause CLAUSE-INDEX-IS-CANONICAL already establish `bridge/INDEX.md` as the canonical, continuously-edited workflow state; the fix aligns the hook with that existing requirement. No new or revised requirement is needed.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk standing-backlog operation. It is a single-concern defect fix tracked by exactly one work item, WI-3334, an active member of PROJECT-GTKB-RELIABILITY-FIXES. No work-item state inventory, bulk transition, or backlog cleanup is performed. The reliability fast-lane (GOV-RELIABILITY-FAST-LANE-001) covers this fix through active project membership under PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING; that governance requires no per-fix formal-artifact-approval packet.

## Bridge INDEX Update Evidence

A NEW entry for `gtkb-bridge-compliance-gate-index-exemption` is inserted at the top of `bridge/INDEX.md`, below the header comments and above the first existing Document entry. No prior bridge file and no prior INDEX entry is deleted or rewritten; the append-only audit trail is preserved.

## Proposed Scope

### IP-1: Exempt bridge/INDEX.md in the live hook

In `.claude/hooks/bridge-compliance-gate.py`, extract the inline target-path loop from `main()` into two pure, importable helper functions and add the INDEX exemption:

```python
def _is_bridge_index_file(file_path: str) -> bool:
    """True when file_path points at the canonical bridge index.

    Edits to bridge/INDEX.md are intrinsic bridge protocol (every proposal
    filing, verdict, and status transition edits it) and are never the gated
    "implementation" of a pending proposal - even when a proposal legitimately
    lists bridge/INDEX.md in its target_paths.
    """
    normalized = file_path.replace("\\", "/")
    return f"/{normalized}".endswith("/bridge/INDEX.md")


def _pending_proposal_ask_reason(index_path: Path, file_path: str) -> str | None:
    """Return an ask-checkpoint reason when file_path matches a pending
    proposal's target_paths, or None. bridge/INDEX.md is always exempt."""
    if _is_bridge_index_file(file_path):
        return None
    doc_statuses = _parse_bridge_index(index_path)
    file_path_normalized = file_path.replace("\\", "/")
    for doc_name, status in doc_statuses.items():
        if status not in ("NEW", "REVISED", "NO-GO"):
            continue
        for tp in _read_proposal_target_paths(index_path, doc_name):
            tp_norm = tp.replace("\\", "/")
            if file_path_normalized.endswith(tp_norm) or tp_norm == file_path_normalized:
                if status == "NO-GO":
                    return (
                        "[Governance] Bridge proposal for this module has NO-GO status. "
                        f"Review Codex findings at bridge/{doc_name} before implementing."
                    )
                return (
                    f"[Governance] Bridge proposal for {doc_name} is pending Codex review ({status}). "
                    "Wait for GO verdict before implementing."
                )
    return None
```

`main()` then drops its now-unused `doc_statuses` and `file_path_normalized` locals (the helper computes them) and replaces the inline loop plus trailing pass with:

```python
ask_reason = _pending_proposal_ask_reason(index_path, file_path)
if ask_reason:
    emit_ask("PreToolUse", ask_reason)
    sys.exit(0)

emit_pass()
sys.exit(0)
```

The `ask` message strings are carried over verbatim. Behavior for non-INDEX files is unchanged: same statuses (`NEW`/`REVISED`/`NO-GO`), same match expression, same newest-first first-match order, same NO-GO vs pending message split.

### IP-2: Identical fix in the scaffold template

Apply the byte-identical change to `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` so adopter projects scaffolded from the template do not inherit the defect. The two files remain byte-identical after the fix.

### IP-3: Regression test

Add `platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py`, parametrized over both hook copies (live + template), covering:

- `_is_bridge_index_file` is True for `bridge/INDEX.md` in absolute and relative forms and False for a regular bridge proposal file and a decoy path such as `notbridge/INDEX.md`.
- `_pending_proposal_ask_reason` returns `None` when the edited file is `bridge/INDEX.md` while a pending `NEW`/`REVISED` proposal lists `bridge/INDEX.md` in its `target_paths` (the core regression).
- `_pending_proposal_ask_reason` still returns an `ask` reason for a non-INDEX file matching a pending proposal's `target_paths` (the checkpoint is not disabled).
- `_pending_proposal_ask_reason` returns the NO-GO-specific reason for a non-INDEX file matched by a `NO-GO` proposal.

Tests use `pytest`'s `tmp_path` to build a fixture `bridge/INDEX.md` plus a fixture proposal file declaring `target_paths`, and import the hyphenated hook modules by path (the pattern already used by `test_bridge_compliance_gate_project_metadata.py`).

## Specification-Derived Verification Plan

| Specification | Behavior verified | Test |
|---|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 / CLAUSE-INDEX-IS-CANONICAL | Editing `bridge/INDEX.md` while a pending proposal targets it does not emit `ask` | test_index_edit_with_pending_proposal_targeting_index_is_exempt |
| GOV-FILE-BRIDGE-AUTHORITY-001 | `_is_bridge_index_file` recognizes the index in absolute and relative forms | test_is_bridge_index_file_recognizes_index |
| GOV-FILE-BRIDGE-AUTHORITY-001 | `_is_bridge_index_file` rejects a regular bridge file and a decoy path | test_is_bridge_index_file_rejects_decoys |
| GOV-FILE-BRIDGE-AUTHORITY-001 | The checkpoint still fires for a non-INDEX file matching a pending proposal | test_non_index_target_still_triggers_ask |
| GOV-FILE-BRIDGE-AUTHORITY-001 | A NO-GO proposal still produces the NO-GO-specific reason for a non-INDEX file | test_no_go_proposal_non_index_target_triggers_no_go_reason |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Both hook copies carry the fix | all tests, parametrized over the live and template hooks |

Execution command:

`python -m pytest platform_tests/hooks/test_bridge_compliance_gate_index_exemption.py -v`

The post-implementation report will also re-run the existing bridge-compliance-gate tests (`test_bridge_compliance_gate_project_metadata.py`, `test_bridge_compliance_gate_wi_project_membership.py`, `test_bridge_compliance_gate_hard_block_workspace.py`) to confirm no regression, and `ruff` over the changed files.

## Acceptance Criteria

- IP-1, IP-2, and IP-3 landed.
- Editing `bridge/INDEX.md` no longer emits an `ask` when a pending proposal lists `bridge/INDEX.md` in `target_paths`.
- The target-path checkpoint still fires for non-INDEX implementation files (gate coverage preserved).
- The live hook and the scaffold template copy remain byte-identical.
- The new test file passes; existing bridge-compliance-gate tests still pass; `ruff` is clean over the changed files.
- Both bridge preflights pass on the post-implementation report.

## Option Rationale

Two implementation options were considered.

Option A (selected): extract the target-path loop into pure helpers `_is_bridge_index_file` and `_pending_proposal_ask_reason`, with the INDEX exemption inside the helper. Rationale: the existing bridge-compliance-gate test suite imports and calls helper functions directly (`_deny_reason_for_content`); a pure helper is testable as a unit with the same pattern, giving a precise regression test for the exemption. The extraction is internal only - both helpers are underscore-prefixed private functions, and the hook's external behavior changes solely by the INDEX exemption.

Option B (rejected): a minimal inline guard in `main()` that skips the loop when the file is `bridge/INDEX.md`. Rejected because the loop would remain inside `main()`, which reads stdin and calls `sys.exit`; the only available regression test would be a subprocess integration test with temp-directory fixture setup, which is heavier and less precise than a unit test and diverges from the existing test pattern for this hook.

## Risks / Rollback

- Risk: the exemption is too broad and lets premature implementation of an actual INDEX-targeting proposal through. Mitigation: `bridge/INDEX.md` content is exclusively bridge protocol state (Document and status lines); there is no "implementation" of `bridge/INDEX.md` distinct from protocol edits. The role-intent sentinel proposal's substantive work is the sentinel comment block, governed by Codex review of that thread, not by this checkpoint.
- Risk: the helper extraction changes behavior for non-INDEX files. Mitigation: the helper carries the loop logic verbatim - same statuses, same match expression, same newest-first first-match order, same two message strings; covered by test_non_index_target_still_triggers_ask and test_no_go_proposal_non_index_target_triggers_no_go_reason.
- Rollback: revert the three files; the change is self-contained with no schema, configuration, or data migration.

## Recommended Commit Type

`fix` - repairs broken hook behavior (an over-firing checkpoint) with no new capability surface. The helper extraction is an internal refactor in service of the fix and of testability, not a new public interface.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
