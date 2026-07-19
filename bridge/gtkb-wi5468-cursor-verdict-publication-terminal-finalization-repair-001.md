NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: Codex
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; sandbox=none
author_metadata_source: trusted Codex turn metadata

# Implementation Proposal - Govern orphaned Cursor E read-only verdict-publication implementation

bridge_kind: prime_proposal
Document: gtkb-wi5468-cursor-verdict-publication-terminal-finalization-repair
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5468

target_paths: ["scripts/cursor_harness.py", "scripts/verify_cursor_dispatch.py", "platform_tests/scripts/test_cursor_harness.py", "platform_tests/scripts/test_verify_cursor_dispatch.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair the terminal-finalization gap for the already implemented and independently reviewed WI-5399 Cursor verdict-publication slice by adopting exactly four current files under a new bounded lifecycle, without semantic edits or unrelated worktree absorption.

Work item description: The authoritative worktree contains a coherent but unfinalized four-file Cursor E implementation in scripts/cursor_harness.py, scripts/verify_cursor_dispatch.py, platform_tests/scripts/test_cursor_harness.py, and platform_tests/scripts/test_verify_cursor_dispatch.py. It forces bridge review into read-only ask/text mode, parses one strict verdict envelope, derives trusted metadata and claims in the shim, publishes only through publish_lo_verdict, and makes readiness fail on contract drift. Exhaustive current/backlog comparison found no work item that owns this exact E projection: WI-4778 owns earlier readiness, WI-4881 daemon dispatch proof, WI-5211 only D/F publication, WI-5345 timeout recovery, and WI-5369 telemetry provenance. Preserve the current bytes as foreign pre-start evidence, identify their provenance, then independently review and exactly finalize or replace them without changing eligibility, routing, dispatcher state, TAFE, or unrelated dirt.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5468` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/cursor_harness.py`, `scripts/verify_cursor_dispatch.py`, `platform_tests/scripts/test_cursor_harness.py`, `platform_tests/scripts/test_verify_cursor_dispatch.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - auto-linked governing or work-item specification.
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - auto-linked governing or work-item specification.
- `ADR-DISPATCHER-ARCHITECTURE-001` - auto-linked governing or work-item specification.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
- `DCL-HARNESS-DISPATCH-ISOLATION-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666552` - Loyal Opposition Verification Verdict - WI-5345 Failed VERIFIED Finalization Repair
- `DELIB-202666647` - LO Review - WI-5370 No-Responds Repair Implementation Report (wi5383-verified-closure-evidence)
- `DELIB-202666508` - Loyal Opposition Verdict - WI-5318 Failed VERIFIED Finalization Repair
- `DELIB-20266182` - Spec-to-Test Mapping
- `DELIB-202666509` - Loyal Opposition Verdict - VERIFIED - Modified Terminal-Verdict Provenance (report review)

- `DELIB-202666734` - corrected WI-5399 GO: exact Cursor source/test scope, dispatchability preservation, governed verdict publication, and separate one-shot retirement conditions.
- `DELIB-202666735` - original WI-5399 GO provenance retained as append-only history; the corrected GO controls.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5468`.

## Proposed Scope

- Use WI-5468 only as the additive terminal-finalization repair carrier for the four existing Cursor E source/test files; canonical WI-5399 deliberations establish the functional implementation ownership.
- Treat the four current files as foreign pre-start bytes. After independent GO and matching claim/start, adopt only the exact hash-bound bytes; do not reauthor or broaden them.
- Preserve Cursor dispatchability while retaining read-only ask/text review mode, strict single-envelope parsing, trusted shim metadata/claim derivation, governed publish_lo_verdict publication, and readiness failure on publication-contract drift.
- Do not delete, edit, execute, stage, or commit either existing one-shot verdict helper in this repair thread; their retirement remains outside these target paths and requires separate worker-lifetime proof.
- Do not mutate dispatcher/TAFE configuration, harness eligibility, routing, roles, concurrency caps, process lifetimes, credentials, Agent Red, groundtruth.db, or unrelated worktree dirt.
- Require an independent post-implementation VERIFIED verdict before any finalization. A local Git commit is deferred to separate exact mechanical authority and must refuse an active index lock or any target hash drift.

## Cross-Harness Disposition

- **Cursor E**: In scope only for exact adoption and finalization of the four hash-bound current files; dispatchability and governed verdict publication are hard invariants.
- **Codex A**: No runtime behavior change; Prime Builder authors this repair lifecycle only.
- **Claude Code B**: No runtime behavior change and no target path in this scope.
- **Antigravity C**: No runtime behavior change and no target path in this scope.
- **Ollama D**: No runtime behavior change and no target path in this scope.
- **OpenRouter F**: No runtime behavior change and no target path in this scope.
- **Alibaba H**: No runtime behavior change and no target path in this scope.
- **TAFE and dispatcher**: No configuration, routing, eligibility, role, cap, or process-lifetime mutation.

## Terminal-Finalization Evidence

- Current Git baseline at filing: `434776baf8f3a53ef048fef1a22bc688ca0fad80`.
- `scripts/cursor_harness.py` SHA-256: `9637E601733B4DD954020EA3EC450CB81AA5B09B5744A18638AAA39E2AFE6FE6`.
- `scripts/verify_cursor_dispatch.py` SHA-256: `BD637DE504CB4B353DF67999792BD218A9BFD9F1E06EA5A5392474B66A5FE3F3`.
- `platform_tests/scripts/test_cursor_harness.py` SHA-256: `25AE9679EB8E6A6DFBCBB43203F243BE9A4461F5D85230C153D03476C682BEC5`.
- `platform_tests/scripts/test_verify_cursor_dispatch.py` SHA-256: `83FED8959B4DD065ADC61EC8FF1417501371B0426B9A6B0843C172E114D80FB9`.
- Observed patch shape: four files, 428 additions, 17 deletions.
- Focused verification already observed: 46 tests passed; ruff check and format checks passed; Git whitespace check passed. All evidence must be rerun after GO/start and again before VERIFIED.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "after_behavior": "The same four bytes are adopted under a bounded repair lifecycle and exactly finalized without semantic changes or absorption of unrelated dirt.",
  "applicability": "applicable",
  "baseline": {
    "diff_additions": 428,
    "diff_deletions": 17,
    "dirty_target_files": 4,
    "focused_tests_passed": 46
  },
  "before_behavior": "Four verified Cursor implementation files remain dirty because the original WI-5399 thread is terminal and cannot authorize another implementation report or finalizer.",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001, WI-5468, and PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE.",
  "essential_context_preservation": "The proposal carries the corrected WI-5399 ownership evidence, exact four-path boundary, byte hashes, no-impairment invariants, and deferred mechanical-finalizer gate.",
  "expected_result": {
    "dirty_target_files_after_exact_finalization": 0,
    "semantic_source_delta": 0,
    "unrelated_paths_absorbed": 0
  },
  "fail_closed_conditions": [
    "missing independent GO or matching claim/start",
    "any target hash drift",
    "any focused test, ruff, preflight, or whitespace-check failure",
    "missing independent VERIFIED",
    "active Git index lock or unavailable separate exact mechanical authority"
  ],
  "hard_invariants": [
    "preserve all four proposal hashes until exact finalization",
    "preserve Cursor dispatchability and governed publish_lo_verdict publication",
    "do not mutate dispatcher or TAFE configuration, eligibility, routing, roles, caps, or process lifetimes",
    "do not touch the two one-shot verdict helpers in this thread",
    "do not absorb unrelated worktree dirt"
  ],
  "history_preservation": "The WI-5399 version chain and both deliberation records remain append-only; WI-5468 adds a separate repair thread.",
  "obsolete_guidance_disposition": "WI-5468's earlier unowned classification is corrected by the cited deliberations; terminal WI-5399 history is preserved and not rewritten.",
  "primary_route": "governed NEW proposal, independent GO, exact claim/start, hash-bound implementation report, independent VERIFIED, then separate exact mechanical Git authority",
  "provenance": "DELIB-202666734 and DELIB-202666735 establish WI-5399 ownership and the corrected independently reviewed behavior contract.",
  "rollback": {
    "instructions": "Fail before finalization and leave the four current bytes untouched if authority, hash, test, lock, or scope checks differ.",
    "test": "Recompute the four SHA-256 values and rerun focused pytest, ruff, and exact-path Git checks."
  },
  "schema_version": 1,
  "self_descriptive_naming": "The slug names WI-5468, Cursor verdict publication, and terminal-finalization repair; target paths and hashes are explicit."
}
```

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Validate NEW, independent GO, exact claim/start, implementation report, and independent VERIFIED before finalization. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Confirm WI-5468, the canonical WI-5399 deliberations, and this additive bridge thread preserve ownership provenance. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the two focused pytest modules, ruff check, ruff format --check, git diff --check, and hash verification before VERIFIED. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Confirm the terminal-finalization repair remains an additive governed lifecycle rather than rewriting terminal WI-5399 history. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Confirm proposal, implementation report, review, and finalization evidence use their correct lifecycle artifacts. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Recompute all four hashes, rerun focused tests and ruff, and prove zero source-behavior delta plus preserved dispatchability. |
| `GOV-WORK-TREE-HYGIENE-001` | Use exact-path status and post-finalization diff checks to prove only the four owned paths are cleared. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Run author-metadata validation on every new status-bearing artifact in this thread. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Assert no dispatcher configuration diff and no direct provider-to-provider interaction. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Confirm verdict publication remains delegated to publish_lo_verdict and that Cursor does not write verdict artifacts directly. |
| `DCL-HARNESS-DISPATCH-ISOLATION-001` | Confirm no route, eligibility, role, cap, or process-lifetime mutation and that non-Cursor harness behavior is unchanged. |

## Acceptance Criteria

- All four target files still match the proposal SHA-256 manifest at implementation report and finalizer time.
- The focused Cursor test pair passes with 46 tests, ruff check passes, ruff format --check passes, and git diff --check passes for the four paths.
- Independent Loyal Opposition confirms that the current bytes satisfy the corrected WI-5399 GO behavior and that WI-5468 introduces no semantic source delta.
- No non-target source, test, dispatcher, TAFE, harness, database, credential, deployment, or release state is changed by this scope.
- After independent VERIFIED and separate exact mechanical authority, the four target paths are clean relative to the resulting commit and unrelated dirt remains byte-for-byte preserved.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/cursor_harness.py`
- `scripts/verify_cursor_dispatch.py`
- `platform_tests/scripts/test_cursor_harness.py`
- `platform_tests/scripts/test_verify_cursor_dispatch.py`

## Recommended Commit Type

`feat`
