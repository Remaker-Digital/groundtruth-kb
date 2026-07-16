NEW

# Implementation Proposal - Adopt recoverable modernization end-to-end workflow runner

bridge_kind: prime_proposal
Document: gtkb-wi5315-recoverable-modernization-end-to-end-workflow
Version: 001
Date: 2026-07-15 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder A; transcript role ::init gtkb pb


Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5315

target_paths: ["groundtruth-kb/src/groundtruth_kb/modernization/__init__.py", "groundtruth-kb/src/groundtruth_kb/modernization/__main__.py", "groundtruth-kb/src/groundtruth_kb/modernization/workflow.py", "platform_tests/scripts/test_modernization_end_to_end_workflow.py"]

Implementation proposal for a bounded code or platform change.

## Claim

Adopt one exact, already passing four-file candidate as the public recoverable
modernization rehearsal workflow. The implementation transaction is
byte-preserving: it claims the candidate under governance, reruns its objective
acceptance evidence, and files an implementation report without changing the
candidate or any live Git, bridge, dispatcher, harness, database, credential,
deployment, or release state.

## Requirement Sufficiency

Existing requirements are sufficient. The frozen modernization acceptance
contract, cross-cutting mechanical-enforcement requirement, non-impairment
gate, evaluability contract, and mandatory independent verification contract
already define this adoption completely; no new formal requirement is needed.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/modernization/__init__.py`, `groundtruth-kb/src/groundtruth_kb/modernization/__main__.py`, `groundtruth-kb/src/groundtruth_kb/modernization/workflow.py`, `platform_tests/scripts/test_modernization_end_to_end_workflow.py`.

## Specification Links

- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - requires objective end-to-end enforcement rather than narrative closure claims.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - keeps proposal, implementation report, and independent verdict roles distinct.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves the candidate, tests, proposal, report, and verdict as durable governed artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires complete applicability and clause preflights before filing.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires independent rerun of the declared spec-derived suite before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds WI-5315 to the Assurance project and active project PAUTH.
- `SPEC-AUQ-POLICY-ENGINE-001` - preserves owner-decision authority and forbids the rehearsal from minting owner approval.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - confines rehearsal mutation to a disposable in-root repository.
- `GOV-STANDING-BACKLOG-001` - WI-5315 is the single ownership record for this candidate.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - requires the Codex non-bypass bridge writer path used for this proposal.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - treats executable evidence and receipts as first-class lifecycle artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - moves the candidate from unresolved-new to governed in-flight only through this proposal.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires structured before/after, rollback, hard-invariant, and fail-closed evidence.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - binds each source carrier to exact reproducible verification commands.

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-GATE-0-RECONCILIATION` - GT-KB Platform Modernization Gate 0 reconciliation inventory
- `DELIB-20260710-GTKB-MODERNIZATION-GIT-LIFECYCLE-WORK-PACKET` - Approve GT-KB Modernization Governed Git Lifecycle work packet
- `DELIB-202666080` - Gate 1.25 readiness contract identifies the cross-cutting modernization acceptance carriers.
- `DELIB-202666274` - owner authorizes required modernization blocker repairs while preserving bridge, start, review, and mechanical gates.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE` - active project-scope authority covers WI-5315; operation-time enforcement remains mandatory.
- `DELIB-202666274` - full modernization implementation authorization, with mechanical Git/deployment/release operations still separately gated.

## Proposed Scope

1. Verify the four target files remain untracked and match these SHA-256 values:
   `F96BEA9091008B784770B144927195F8042F8BEC9023B37F5CFE44A0E79D728F`,
   `0D075333EBF67B036F6EF64547D7A450608955106B8F414A9FE7D68C545531EA`,
   `D06169E22AC308D403CC7BD8F148DF58946427C1587215CBEF713E7A9A022771`,
   and `86D18E9F628C644A80BBD969716E6BEF133C4667483ADCA5B1270CC7970088D5`.
2. Acquire a matching WI-5315 claim and successful implementation-start packet,
   then adopt the exact candidate bytes without editing them.
3. Run the focused 8-test subprocess acceptance, Ruff check, and Ruff format
   check against only the declared files.
4. File a hash-bound implementation report and release the claim. Do not stage,
   commit, push, deploy, release, or mutate live bridge, TAFE, dispatcher, or harness
   state or `groundtruth.db`.
5. Keep the bridge lifecycle append-only: proposal, report, and verdict are
   filed only as the next numbered bridge files, and no prior version is
   deleted or rewritten.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-202666274; WI-5315; TEST-11458",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python -m groundtruth_kb.modernization",
  "before_behavior": "The complete recoverable workflow and its acceptance carrier exist only as four untracked candidate files with no explicit backlog owner or independent adoption review.",
  "after_behavior": "The exact same bytes are owned by WI-5315, reviewed through the governed bridge, and objectively evaluable through one public CLI and one eight-test acceptance carrier.",
  "self_descriptive_naming": "The groundtruth_kb.modernization package, ModernizationWorkflow class, rehearse subcommand, review receipts, and result fields identify their authority and lifecycle purpose directly.",
  "obsolete_guidance_disposition": "No guidance is replaced or shadowed; this scope adds the canonical executable composition and does not alter existing routes.",
  "history_preservation": "Original candidate hashes, the versioned proposal/report/verdict chain, and isolated rehearsal Git history remain independently queryable.",
  "baseline": {
    "tracking_state": "four files untracked",
    "candidate_sha256_count": 4,
    "focused_tests": "8 passed in 24.30 seconds on 2026-07-15",
    "candidate_bytes_changed": false
  },
  "expected_result": {
    "candidate_sha256_unchanged": true,
    "focused_tests_passed": 8,
    "independent_verification_required": true,
    "live_repository_effects": 0
  },
  "rollback": {
    "instructions": "Before separately authorized Git finalization, rollback is a no-op because implementation changes no candidate bytes. Any later finalized adoption is reversed only by a separately authorized exact commit operation.",
    "test": "Recompute all four SHA-256 values and rerun platform_tests/scripts/test_modernization_end_to_end_workflow.py."
  },
  "hard_invariants": [
    "Proposal and verification authors have distinct session context ids.",
    "Protected rehearsal mutation requires active PAUTH, matching claim, and successful implementation-start evidence.",
    "Interrupted recovery produces exactly one target effect and completed replay produces none.",
    "All acceptance mutation stays inside a disposable in-root rehearsal repository.",
    "No live Git index, ref, history, bridge, TAFE, dispatcher, harness, groundtruth.db, credential, deployment, or release mutation occurs."
  ],
  "fail_closed_conditions": [
    "Any candidate SHA-256 mismatch or unexpected tracking-state change.",
    "Missing, forged, same-session, stale, or digest-mismatched authority/review receipt.",
    "Focused collection count differs from eight or any test, Ruff, or format check fails.",
    "Any undeclared target path or live-state mutation is observed."
  ],
  "essential_context_preservation": "The workflow resolves authority from canonical in-root session, identity, registry, PAUTH, proposal, report, verdict, recovery, and Git artifacts; adoption removes none of those contexts."
}
```

## Specification-Derived Verification Plan

| Specification | Verification |
|---|---|
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Run the exact 8-test subprocess acceptance and inspect the completed result invariants. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Recompute all hashes; confirm focused tests, Ruff, and format pass; attest zero live-state effects. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Verify all four exact paths and reproducible commands are present in report evidence. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independent LO reruns the eight-test suite and records collection count and outcomes. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm distinct PB/LO session ids and role-correct NEW, GO, report, and VERIFIED artifacts. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Resolve WI-5315 membership and active Assurance PAUTH before claim/start. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run applicability and clause preflights with zero blocking gaps. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm rehearsal mutation is confined to the disposable in-root workspace. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Confirm no workflow receipt or helper mints an owner decision. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Confirm candidate, tests, report, and verdict remain durable and linked. |
| `GOV-STANDING-BACKLOG-001` | Confirm WI-5315 is the single open owner for this candidate scope. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Confirm filing used `propose_bridge_codex_non_bypass`. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Confirm executable evidence and receipts are treated as lifecycle artifacts. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Confirm the candidate transitions only through NEW, implementation report, and independent VERIFIED evidence. |

## Acceptance Criteria

1. All four pre-adoption hashes match this proposal and remain identical after
   implementation; any mismatch aborts.
2. `platform_tests/scripts/test_modernization_end_to_end_workflow.py` collects
   exactly eight tests and all eight pass.
3. The suite proves distinct PB/LO runtime sessions, authority and tamper
   rejection, interruption recovery, one mutation effect, implementation and
   verification commit ancestry, and idempotent completed replay.
4. Focused Ruff and Ruff format checks pass for all four files.
5. No other source/test byte changes and no staging, commit, push, deploy,
   release, live bridge, TAFE, dispatcher, or harness mutation, `groundtruth.db`
   mutation, or credential operation occurs.

## Risks / Rollback

Primary risk is accidentally laundering foreign untracked bytes or allowing the
acceptance rehearsal to touch live authority. Fail closed on any hash, tracking,
path, receipt, test-count, lint, or live-state discrepancy. Because the
implementation transaction edits no candidate bytes and performs no Git
finalization, rollback before a later exact commit is a no-op. A future commit
may occur only under separate mechanical authority after independent VERIFIED.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/modernization/__init__.py`
- `groundtruth-kb/src/groundtruth_kb/modernization/__main__.py`
- `groundtruth-kb/src/groundtruth_kb/modernization/workflow.py`
- `platform_tests/scripts/test_modernization_end_to_end_workflow.py`

## Recommended Commit Type

`feat`
