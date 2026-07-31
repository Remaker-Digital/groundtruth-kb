NEW

# WI-5383: Require strict terminal evidence before VERIFIED backlog closure

bridge_kind: prime_proposal
Document: gtkb-wi5383-terminal-commit-closure-evidence
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-17T04:00:07Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-desktop-019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: desktop interactive Prime Builder A

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5383

target_paths: ["scripts/bridge_verified_backlog_reconciler.py", "platform_tests/scripts/test_bridge_verified_backlog_reconciler.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Repair the VERIFIED backlog reconciler so a terminal status token is necessary
but not sufficient evidence that implementation work is complete. The
reconciler must keep VERIFIED-on-NO-ACTION threads open, fail closed on malformed
approved `target_paths`, and require the terminal verdict plus every non-bridge
implementation target to be covered by the verdict's containing commit before
resolving a source-bearing work item.

A deliberately narrow by-reference exception remains available only when the
implementation report contains a dedicated
`## By-Reference Finalization Waiver` section and an anchored affirmative
owner-approved declaration carrying a `DELIB-*` reference. Broad
`## Owner Decisions / Input` prose, generic mentions, proposal-side references,
and negated statements such as "No owner-approved by-reference waiver exists"
must not activate the exception. WI-5426 and linked TEST-11537 record this
false-positive correction inside the same two-file transaction as WI-5383 so
the shared source does not acquire competing finalization owners.

The current dirty candidate is a pre-GO baseline, not an implementation-ready
byte image: it already contains the typed closure and commit-coverage behavior,
but its waiver detector still accepts negated or incidental prose. Independent
GO must authorize correcting that detector and adding the regression before an
implementation report may be filed.

| Current pre-GO path | Bytes | SHA-256 |
|---|---:|---|
| `scripts/bridge_verified_backlog_reconciler.py` | 46,097 | `77E3417FD4918AC055E2EF60953B97FBD61E81DE4403051396339343B3FF59E9` |
| `platform_tests/scripts/test_bridge_verified_backlog_reconciler.py` | 38,876 | `7D808DE1CE17CDAD9AB732E35A81098AAFFC891C7F41C17C07914B2A09381908` |

This proposal does not execute the live reconciler, change any live work-item
status, mutate `groundtruth.db`, inspect or rewrite a bridge thread, stage or
commit files, alter dispatcher/TAFE/harness state, or absorb any other dirty
path. The known full-audit Git fan-out/performance follow-up remains separately
tracked by WI-5397.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO and VERIFIED and preserves the numbered thread chain as workflow authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires the proposal to link every applicable governing requirement.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds this repair to WI-5383 and the active Tree Stabilization PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed requirement-to-test evidence before terminal verification.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - prevents project scope from substituting for bridge GO, claim, or implementation-start authority.
- `GOV-STANDING-BACKLOG-001` - governs WI-5383, WI-5426, and their linked tests.
- `DCL-VERIFIED-BRIDGE-HISTORY-001` - requires complete-thread evidence and makes a bare terminal token insufficient for implementation closure.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - keeps a verified operational no-action disposition distinct from completed implementation.
- `SPEC-DSI-COMMIT-GATE-001` - requires commit-time evidence to remain independently blocking.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires unambiguous, current, machine-evaluable closure and waiver evidence.
- `GOV-WORK-TREE-HYGIENE-001` - requires exact finalization without absorbing unrelated dirty content.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires before/after, rollback, and hard-invariant evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires closure, exception, and blocked states to remain durable and distinct.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - links source, tests, work items, proposal, verification, and commit evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires each evidence transition to retain its own lifecycle meaning.

## Prior Deliberations

- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` - established
  that independent VERIFIED normally retires its parent backlog item. WI-5383
  supplies the missing proof boundary: retirement follows only when that
  VERIFIED represents completed implementation and its terminal commit covers
  the approved targets.
- `DELIB-WI5116-PHASE1-SWEEP-DIAGNOSIS-20260709` - established that
  finalization decisions must expose exact metadata and scope evidence rather
  than infer completion from a token alone.
- `DELIB-202666274` - authorized project-scoped Tree Stabilization work while
  retaining independent GO, claim/start, VERIFIED, exact ownership, and
  separate Git-mechanic gates.

## Owner Decisions / Input

The owner has authorized the full modernization and Tree Stabilization project,
including hygiene-item creation and governed proposal filing. No new owner
decision is required to review this bounded source/test repair. Project
authorization does not authorize running the reconciler against live MemBase or
performing any Git finalization mechanic.

No owner-approved by-reference waiver exists for bypassing this proposal's own
implementation or finalization gates. That negative sentence is itself a
required regression example and must never be parsed as an affirmative waiver.

## Requirement Sufficiency

Existing requirements sufficient - complete bridge history, NO-ACTION
semantics, commit-gate evidence, artifact evaluability, worktree hygiene,
non-impairment, and bridge authority already define the needed fail-closed
behavior. The implementation only makes those requirements deterministic.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5383 and WI-5426 exact ownership audit at HEAD 42a252ab57b5a203e9406b626c741d897e8fb196",
  "canonical_authority": "The approved proposal target metadata, complete numbered bridge thread, explicit owner waiver record when one exists, and the terminal containing commit",
  "primary_route": "Classify verdict purpose, validate target metadata, then prove terminal commit coverage before resolving the work item",
  "before_behavior": "A terminal VERIFIED token can close unfinished or NO-ACTION work, and negated waiver prose can bypass missing target coverage",
  "after_behavior": "NO-ACTION and malformed metadata remain open, source-bearing work requires exact terminal commit coverage, and only a dedicated affirmative owner waiver declaration activates the exception",
  "self_descriptive_naming": "verified_thread_closure_evidence, no_action_verified, malformed_target_metadata, missing_implementation_commit_coverage, and an affirmative waiver declaration expose each decision",
  "obsolete_guidance_disposition": "Token-only terminality and keyword-presence waiver inference are rejected; no bridge history is rewritten",
  "history_preservation": "Every existing proposal, report, verdict, work-item version, and commit remains intact; the reconciler records classification rather than mutating evidence",
  "baseline": "Current two-file pre-GO candidate passes 41 focused tests but lacks the negated/incidental waiver regression and correction",
  "expected_result": "False closure and false waiver activation are blocked while focused commits, bridge-only legacy work, and structurally explicit affirmative waivers retain their governed behavior",
  "rollback": "A separately authorized exact rollback restores only the final WI-5383/WI-5426 source and test images without running the live reconciler or changing backlog state",
  "hard_invariants": "No direct harness contact, no dispatcher or TAFE mutation, no live bridge inspection or rewrite, no live reconciler execution, no groundtruth.db status mutation, no Git staging/commit/push, no unrelated path capture, and no token-only implementation closure",
  "fail_closed_conditions": "NO-ACTION predecessor, malformed or unsafe target metadata, untracked verdict, missing containing commit, omitted target, ambiguous or negated waiver text, hash drift, extra path, or test failure blocks closure",
  "essential_context_preservation": "The result retains verdict purpose, proposal targets, report provenance, waiver provenance, containing commit, changed paths, missing paths, and exact skip reason"
}
```

## Spec-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| Exact two-path scope; `GOV-WORK-TREE-HYGIENE-001` | Recompute both final file hashes; inspect `git diff --check` and target inventory | Only the reconciler and its focused test change, with no whitespace error or unrelated hunk. |
| NO-ACTION semantics; `DCL-NO-ACTION-STATUS-SEMANTICS-001` | `test_verified_on_no_action_is_not_implementation_closure` | Action is `skip`, reason is `no_action_verified`, and the work item remains open. |
| Strict proposal metadata; `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Malformed JSON, duplicate/unsafe metadata, and bridge-only/legacy fixture coverage | Malformed or unsafe declarations fail closed; valid bridge-only/legacy threads preserve established behavior. |
| Terminal commit gate; `SPEC-DSI-COMMIT-GATE-001`; `DCL-VERIFIED-BRIDGE-HISTORY-001` | Untracked verdict, no containing commit, commit omitting target, and focused commit fixtures in temporary repositories | Every missing evidence case skips with exact diagnostics; a focused commit covering verdict and all approved targets is closable. |
| Negation-safe waiver; WI-5426; TEST-11537 | Add report fixtures for the exact sentence in this proposal, incidental owner prose, malformed declarations, and the existing dedicated affirmative `DELIB-*` declaration | Negative/incidental/malformed text cannot bypass coverage; only the dedicated anchored affirmative declaration produces `mode=by_reference_waiver`. |
| Complete focused behavior | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_verified_backlog_reconciler.py -q --tb=short --timeout=300` | All tests pass, including the new waiver regression; the current pre-GO baseline is 41 passed. |
| Source/test quality | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/bridge_verified_backlog_reconciler.py platform_tests/scripts/test_bridge_verified_backlog_reconciler.py` and matching `ruff format --check` | Both commands exit 0. |
| Non-impairment | Verify all Git fixture operations use only pytest-owned temporary repositories and no test invokes the reconciler CLI against `E:\GT-KB\groundtruth.db` | Live database, work-item statuses, bridge files, index, dispatcher, TAFE, and harness state remain unchanged by tests. |
| Bridge/project authority | Validate the current PAUTH, independent GO, matching claim/start, WI-5383/WI-5426 linkage, and independent post-implementation verdict through governed CLI surfaces | Every transition is current and exact; no project authorization substitutes for bridge or start authority. |

## Risk / Rollback

The principal risk is false closure of unfinished work. Secondary risks are a
false skip of legitimately complete work, an over-broad waiver exception, and
serial Git inspection cost during full reconciliation. The implementation
fails closed and returns the exact closure reason plus commit evidence. LO must
verify both negative and positive paths, especially the literal negative
sentence above. WI-5397 separately owns full-audit Git fan-out/performance and
must not be treated as solved by this transaction.

The implementation must not run the live reconciliation mutation. A later
rollback requires separate exact mechanical authority and may restore only the
two final target images while preserving all bridge history, work-item history,
database rows, index entries, and unrelated worktree bytes.

## Bridge Filing

This proposal is filed as the next append-only numbered bridge file,
`bridge/gtkb-wi5383-terminal-commit-closure-evidence-001.md`; no prior version
is deleted or rewritten. Dispatcher/TAFE state plus the versioned bridge files
are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - the two-file transaction prevents false implementation closure and
false by-reference waiver activation while preserving governed positive paths.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
