NEW

# Implementation Proposal - Adopt frozen modernization release-candidate contract and checker

bridge_kind: prime_proposal
Document: gtkb-wi5316-frozen-modernization-rc-contract
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
Work Item: WI-5316

target_paths: ["config/governance/modernization-release-candidate.json", "scripts/check_modernization_release_candidate.py", "platform_tests/scripts/test_modernization_release_candidate.py"]

Implementation proposal for a bounded code or platform change.

## Claim

Adopt the exact frozen modernization release-candidate manifest, checker, and
focused test as one byte-preserving governed candidate. This scope establishes
the executable RC contract only; it does not issue or relabel clean-run,
attestation, audit, semantic, activation, Git, deployment, or release evidence.

## Requirement Sufficiency

Existing requirements are sufficient. The frozen acceptance contract,
release-readiness testing gate, cross-cutting enforcement requirement,
non-impairment rule, Git binding rule, and independent verification contract
fully determine this adoption; no new formal requirement is needed.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `config/governance/modernization-release-candidate.json`, `scripts/check_modernization_release_candidate.py`, `platform_tests/scripts/test_modernization_release_candidate.py`.

## Specification Links

- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - requires the release decision to depend on complete governed executable evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires role-correct append-only proposal, report, and independent verdict artifacts.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves the manifest, checker, tests, and reviews as durable artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires complete applicability and clause preflights.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires independent rerun of the exact checker suite before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds WI-5316 to the Assurance PAUTH.
- `SPEC-AUQ-POLICY-ENGINE-001` - preserves owner authority for release and other mechanical decisions.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps targets and scratch inside the GT-KB root without mutating adopters.
- `GOV-STANDING-BACKLOG-001` - WI-5316 is the single ownership record for this candidate trio.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - requires the governed Codex non-bypass proposal writer.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - links frozen scope, executable test, report, and verdict.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - makes candidate, in-flight, verified, and closure states explicit.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - requires all 94 handles to be mechanically represented rather than narratively asserted.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires fail-closed before/after and zero live-state impairment.
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` - binds evidence to exact Git state and rejects stale or mismatched runs.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires deterministic manifest, command, digest, and result evaluation.

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-GATE-0-RECONCILIATION` - GT-KB Platform Modernization Gate 0 reconciliation inventory
- `DELIB-202666274` - owner authorizes required modernization blocker work while retaining review and mechanical gates.
- `DELIB-202666288` - WI-5165 review proves historical/current evidence and exact-HEAD validity must remain distinct.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE` - active project-scope authority includes WI-5316; operation-time enforcement remains mandatory.
- `DELIB-202666274` - modernization implementation is authorized, but Git, release, deployment, credentials, and live evidence issuance remain separately gated.

## Proposed Scope

1. Verify all three files remain untracked and match SHA-256 values
   `203824F57C4FF8700E59B06864047C2F3CDD8436F70BB3730DCC0FDC788AF87D`,
   `E2D40360CD389FD3356F046A519C8324518A92061EB5AF530E8BA6C57E95ACFB`,
   and `1B07D2130E40E5B88EC8CCDDF828FCACC37E8ED4A1490D83BB0680B630D5CA48`.
2. After exact claim and implementation-start evidence, adopt the candidate
   bytes without editing them.
3. Run manifest validation, the exact 46-test checker suite, focused Ruff, and
   focused format verification.
4. File a hash-bound implementation report without running `run-clean`,
   `attest-run`, or `record-audit`, and without writing any RC runtime evidence.
5. Keep bridge history append-only by filing only the next numbered bridge
   files and never deleting or rewriting prior versions.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5316; TEST-11459; frozen modernization acceptance contract",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python scripts/check_modernization_release_candidate.py",
  "before_behavior": "The frozen eight-capability ninety-four-handle contract, checker, and focused test exist only as three untracked candidate files without a non-colliding adoption owner.",
  "after_behavior": "The exact same bytes are owned by WI-5316, independently reviewed, and reproducibly evaluable without claiming any current release evidence.",
  "self_descriptive_naming": "The manifest, check_modernization_release_candidate service, and test_modernization_release_candidate carrier name their contract and lifecycle directly.",
  "obsolete_guidance_disposition": "No existing route or guidance is replaced; this scope establishes the frozen executable contract only.",
  "history_preservation": "Frozen digest, original hashes, tests, append-only bridge history, and later run/attestation/audit evidence remain separately queryable.",
  "baseline": {
    "tracking_state": "three files untracked",
    "capabilities": 8,
    "handles": 94,
    "focused_tests": "46 passed in 5.95 seconds on 2026-07-15"
  },
  "expected_result": {
    "candidate_sha256_unchanged": true,
    "capabilities": 8,
    "handles": 94,
    "focused_tests_passed": 46,
    "runtime_evidence_writes": 0
  },
  "rollback": {
    "instructions": "Before separately authorized Git finalization, rollback is a no-op because adoption changes no candidate bytes. Any later finalized adoption is reversed only by a separately authorized exact commit operation.",
    "test": "Recompute all three hashes, run manifest validate, and rerun the focused 46-test suite."
  },
  "hard_invariants": [
    "The frozen scope digest and ninety-four-handle population do not change.",
    "Readiness requires two current complete clean runs with independent attestations plus one independent audit.",
    "Historical, stale, mismatched-HEAD, malformed, tampered, or same-session evidence cannot satisfy readiness.",
    "Adoption does not run collectors or issue run, attestation, audit, release, or deployment evidence.",
    "No live Git, bridge, TAFE, dispatcher, harness, database, credential, deployment, or release state is mutated."
  ],
  "fail_closed_conditions": [
    "Any candidate hash, tracking state, capability count, handle count, or frozen digest differs.",
    "Manifest validation, any focused test, Ruff, or format verification fails.",
    "Any undeclared path or runtime evidence artifact changes.",
    "Any review session is missing, same-session, or role-invalid."
  ],
  "essential_context_preservation": "The contract keeps frozen scope, Git binding, actor authority, run reports, independent attestations, audit, residual findings, and release decision as distinct current in-root evidence."
}
```

## Specification-Derived Verification Plan

| Specification | Verification |
|---|---|
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | Validate the manifest and prove readiness cannot pass without two attested current clean runs and an audit. |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Assert exactly eight capabilities and ninety-four uniquely bound handles. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Recompute hashes and attest zero runtime or live-state effects. |
| `DCL-GIT-BRANCH-BINDING-PROMOTION-001` | Exercise stale/mismatched HEAD and tree rejection tests. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Verify deterministic manifest, digest, commands, and machine outcomes. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independent LO reruns validation, all 46 tests, Ruff, and format. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm distinct PB/LO sessions and append-only numbered artifacts. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Resolve WI-5316 and active Assurance PAUTH before claim/start. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run applicability and clause preflights with zero blocking gaps. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm all targets and test scratch stay inside the project root. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Confirm only an owner action can authorize release or mechanical exceptions. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Preserve manifest, tests, report, and verdict as linked artifacts. |
| `GOV-STANDING-BACKLOG-001` | Confirm WI-5316 is the single owner for this adoption. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Confirm filing uses the Codex non-bypass writer. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Keep executable and review evidence linked and durable. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Confirm explicit candidate, in-flight, verified, and closure transitions. |

## Acceptance Criteria

1. Manifest validation exits zero with exactly 8 capabilities and 94 handles.
2. All three SHA-256 values remain unchanged.
3. The focused suite collects exactly 46 tests and all pass; Ruff and format
   checks pass for the Python targets.
4. Readiness continues to fail closed for absent, stale, tampered, malformed,
   same-session, mismatched-HEAD, incomplete, or unaudited evidence.
5. No clean-run, attestation, audit, semantic, activation, deployment, release,
   Git, bridge, TAFE, dispatcher, harness, database, or credential state changes.

## Risks / Rollback

The chief risk is mistaking adoption of the checker for current RC evidence or
silently changing the frozen digest. Hash, digest, count, and focused-test
checks fail closed. The implementation transaction changes no candidate bytes,
so rollback before a later exact commit is a no-op; any later commit reversal
requires separate mechanical authority.

## Files Expected To Change

- `config/governance/modernization-release-candidate.json`
- `scripts/check_modernization_release_candidate.py`
- `platform_tests/scripts/test_modernization_release_candidate.py`

## Recommended Commit Type

`feat`
