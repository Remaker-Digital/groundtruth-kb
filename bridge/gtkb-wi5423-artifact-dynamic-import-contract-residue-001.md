NEW

# WI-5423: Restore the artifact dynamic-import contract residue

bridge_kind: prime_proposal
Document: gtkb-wi5423-artifact-dynamic-import-contract-residue
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-17T03:41:23Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-desktop-019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: desktop interactive Prime Builder A

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5423

target_paths: ["groundtruth-kb/src/groundtruth_kb/gates.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Finalize only the existing four-line
`__gtkb_dynamic_import_contract__` declaration in
`groundtruth-kb/src/groundtruth_kb/gates.py`. Commit `42a252ab` adopted the
artifact-decontamination checker and frozen tests but omitted this production
declaration. The committed `gates.py` therefore produces an unresolved
non-literal import for `_import_gate`; the current worktree declaration records
the owner-configured plugin boundary and its runtime type-validation rationale.

This is a hunk-only residue repair. The current target file SHA-256 is
`DD86E9600570D7168614F231BB2A7DBBC8D8A319CB3AB4F6B0DDBCB676014864`;
the LF-rendered `git diff` SHA-256 is
`B8CD5CE6CEFB3202568D471413DFD7F080BB57D51A066EB36CB0A19E756C1C2E`.
Any drift or additional hunk invalidates this proposal.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO and VERIFIED around protected source work.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires complete applicable requirement linkage.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds the repair to WI-5423 and the Tree Stabilization PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires execution of the mapped scanner and frozen tests.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - prevents project scope from replacing GO, claim, or start authority.
- `GOV-STANDING-BACKLOG-001` - governs WI-5423 and linked TEST-11534.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires dynamic dependencies to be deterministically classifiable instead of unresolved or falsely passing.
- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` - governs active-path decontamination and explicit treatment of retained loading boundaries.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires the baseline, result, rollback, and hard-invariant disposition below.
- `GOV-WORK-TREE-HYGIENE-001` - requires exact hunk ownership and preservation of unrelated dirty state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the omitted residue and evidence to remain linked as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - links source, work item, test, review, and finalization evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - keeps the dirty candidate, reviewed repair, verification, and final committed state distinct.

## Prior Deliberations

- `INTAKE-eb0bbcad` - the tracked artifact list is canonical for cleanup
  essentiality. This repair converts a necessary live declaration from
  worktree-only residue into a reviewable tracked hunk.

## Owner Decisions / Input

The owner authorized the modernization program and directed that every
discovered flaw or omission become a hygiene work item, then that all worktree
dirt be cleared through exact independently verified ownership. No additional
owner decision is required to file or review this proposal. Protected
implementation and Git finalization remain separately gated.

## Requirement Sufficiency

Existing requirements sufficient - artifact evaluability, decontamination,
non-impairment, worktree hygiene, and bridge/project authority fully define the
one-hunk repair. No new requirement or runtime behavior is introduced.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5423 exact ownership audit at HEAD 42a252ab57b5a203e9406b626c741d897e8fb196",
  "canonical_authority": "The committed artifact-decontamination evaluator plus reviewed Git source bytes",
  "primary_route": "Independent bridge review of one exact gates.py hunk followed by governed implementation reporting, VERIFIED, and exact mechanical finalization",
  "before_behavior": "Committed gates.py exposes _import_gate as an unresolved non-literal dynamic import to the committed evaluator",
  "after_behavior": "The evaluator classifies _import_gate as one explicit reviewed owner-configured plugin boundary with runtime type validation",
  "self_descriptive_naming": "The declaration name __gtkb_dynamic_import_contract__ and _import_gate key identify the exact evaluator contract",
  "obsolete_guidance_disposition": "No guidance or historical artifact is changed",
  "history_preservation": "The existing file and all unrelated worktree, bridge, MemBase, and Git history are preserved",
  "baseline": "One tracked file with exactly four added lines and no deleted line",
  "expected_result": "No unresolved dynamic request for _import_gate and all 24 frozen artifact-lifecycle tests pass",
  "rollback": "A separately authorized hunk-exact rollback removes only the declaration and restores the prior evaluator result",
  "hard_invariants": "No other gates.py hunk, package file, checker, test, database, dispatcher, harness, bridge history, or Git history operation is included",
  "fail_closed_conditions": "Any target hash drift, extra hunk, unresolved import, malformed or empty contract, test failure, stale authority, or incomplete evidence blocks GO, VERIFIED, and finalization",
  "essential_context_preservation": "The review retains the evaluator, plugin-boundary rationale, frozen lifecycle suite, and exact prior/current AST result"
}
```

## Spec-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| Exact WI-5423 scope; `GOV-WORK-TREE-HYGIENE-001` | Recompute target and LF diff SHA-256 values; inspect `git diff --numstat` and `git diff --check` | Current hashes match; exactly four additions, zero deletions, no whitespace errors, and no second path or hunk. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Parse committed and worktree `gates.py` through `check_artifact_decontamination._import_requests` | Committed baseline has one unresolved dynamic request at `_import_gate`; candidate has zero unresolved dynamic requests and one declaration with the exact non-empty rationale. |
| Frozen artifact lifecycle and decontamination contract | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_artifact_decontamination.py -q --tb=short --timeout=600` | 24 tests pass. |
| Python quality | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/gates.py` and `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/gates.py` | Both exit 0. |
| Bridge/project and artifact lifecycle rules | Validate current PAUTH, independent GO, matching claim/start, linked WI-5423/TEST-11534, and independent post-implementation verdict through governed CLI surfaces | Every transition is current, linked, and exact; no project scope substitutes for bridge or start authority. |
| Exact finalization | After separate mechanical authority, inspect the resulting parent diff | Only the approved four-line hunk is present; no unrelated file or hunk is included. |

## Risk / Rollback

The risk is normalizing a dynamic import without proving it is an intentional,
bounded plugin seam. LO must inspect `_import_gate` and its runtime type check,
the declaration literal, and the evaluator's fail-closed handling. Any broader
dynamic-import exemption or empty rationale is NO-GO.

The repair is additive and hunk-exact. It executes no plugin, Git operation,
dispatcher action, or external access. A later rollback must be separately
authorized and remove only the four declaration lines.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered
bridge file for `gtkb-wi5423-artifact-dynamic-import-contract-residue`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - the hunk restores an evaluator declaration omitted from the committed
artifact-decontamination baseline.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
